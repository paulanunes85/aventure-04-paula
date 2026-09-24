#!/usr/bin/env python3
"""Ponto de entrada portável dos hooks do GitHub Copilot.

Funciona com Copilot CLI, Copilot cloud agent e o harness Local do VS Code.
Lê o evento em JSON pela entrada padrão e responde no formato de cada harness.

Uso:
    python3 .github/hooks/scripts/hook.py <evento>

Eventos:
    pre-tool-use            Bloqueia ou pede confirmação para operações arriscadas.
    post-tool-use           Registra auditoria e conta escritas da sessão.
    post-tool-use-failure   Registra falhas de ferramenta.
    session-start           Injeta contexto curto do projeto.
    session-end             Registra o encerramento e limpa o estado da sessão.
    agent-stop              Quality gate opcional antes de o agente encerrar o turno.

Configuração opcional: .github/hooks/config/policy.json (substitui seções padrão).
Somente biblioteca padrão; requer Python 3.9+.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

POLICY_FILE = Path(".github/hooks/config/policy.json")
LOG_DIR = Path(".github/hooks/.logs")

DEFAULT_POLICY: dict[str, Any] = {
    "protected_paths": {
        "deny": ["**/.git/**"],
        "ask": [".github/hooks/**", ".github/workflows/**"],
    },
    "secret_paths": {
        "patterns": [
            ".env", ".env.*", "*.pem", "*.key", "*.pfx", "*.p12", "id_rsa*",
            "id_ecdsa*", "id_ed25519*", ".npmrc", ".pypirc", ".netrc",
            "*.tfstate", "*.tfstate.*", "**/secrets/**",
        ],
        "exceptions": [".env.example", ".env.sample", ".env.template", "*.pub"],
    },
    "outside_workspace_write": "ask",
    "shell": {
        "deny": [
            r"\brm\s+(?:-\S+\s+)*(?:--\s+)?(?:/|~|\$HOME|\$\{HOME\})(?:/\*?)?(?=\s|$|[;&|])",
            r"\bmkfs(?:\.\w+)?\b",
            r"\bdd\b[^\n;|&]*\bof=/dev/(?!null\b)",
            r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",
            r"\b(?:curl|wget)\b[^\n;]*\|\s*(?:sudo\s+)?(?:ba|z|da|k)?sh\b",
            r">\s*/dev/(?:sd|nvme|disk)\w*",
        ],
        "ask": [
            r"\brm\s+-\w*(?:r\w*f|f\w*r)",
            r"\bgit\s+push\b",
            r"\bgit\s+reset\s+--hard\b",
            r"\bgit\s+clean\s+-\w*f",
            r"\bgit\s+branch\s+-D\b",
            r"\bgit\s+(?:checkout|restore)\s+(?:--\s+)?\.(?=\s|$)",
            r"--no-verify\b",
            r"\bsudo\b",
            r"\b(?:npm|pnpm|yarn)\s+publish\b",
            r"\b(?:terraform|tofu)\s+(?:apply|destroy)\b",
            r"\bkubectl\s+delete\b",
            r"\baz\s+group\s+delete\b",
            r"(?i)\bdrop\s+(?:table|database|schema)\b",
        ],
    },
    "audit": {"enabled": True, "max_bytes": 5_000_000},
    "session_context": {
        "enabled": True,
        "extra": [
            "Siga .github/copilot-instructions.md e as instruções de .github/instructions/.",
            "Nenhum código sem requisito aprovado em specs/<NNN>-<funcionalidade>/spec.md.",
            "Testes que verificam requisitos citam o REQ-ID em comentário.",
            "Nunca registre segredos, credenciais ou dados pessoais.",
        ],
    },
    "quality_gate": {"enabled": False, "commands": [], "timeout_sec": 240, "max_blocks": 2},
}

SHELL_TOOLS = {
    "bash", "powershell", "pwsh", "sh", "zsh", "shell", "execute",
    "run_in_terminal", "runinterminal", "send_to_terminal", "run_command", "runcommand",
}
WRITE_HINT = re.compile(
    r"create|edit|write|replace|patch|insert|delete|remove|move|rename|mkdir|directory|notebook"
)
READ_HINT = re.compile(r"read|view|get_|list|search|find|query")
PATH_KEYS = {
    "path", "filepath", "file_path", "target_file", "targetfile", "new_path", "newpath",
    "old_path", "oldpath", "destination", "dirpath", "dir_path", "notebook_path", "uri",
}
PATCH_HEADER = re.compile(r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to):\s*(.+?)\s*$", re.M)
SEVERITY = {"ask": 1, "deny": 2}


# ---------------------------------------------------------------- policy and io

def load_policy(root: Path) -> tuple[dict[str, Any], str | None]:
    policy = json.loads(json.dumps(DEFAULT_POLICY))
    path = root / POLICY_FILE
    if not path.is_file():
        return policy, None
    try:
        custom = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return policy, f"policy_invalid:{type(exc).__name__}"
    if not isinstance(custom, dict):
        return policy, "policy_invalid:not_object"
    for key, value in custom.items():
        if key in policy and isinstance(policy[key], dict) and isinstance(value, dict):
            policy[key].update(value)
        elif key in policy:
            policy[key] = value
    return policy, None


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()


def session_id(event: dict[str, Any]) -> str:
    raw = str(event.get("sessionId") or event.get("session_id") or "unknown")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", raw)[:80]


def audit(root: Path, policy: dict[str, Any], record: dict[str, Any]) -> None:
    settings = policy.get("audit") or {}
    if not settings.get("enabled", True):
        return
    try:
        log_dir = root / LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "audit.jsonl"
        max_bytes = int(settings.get("max_bytes", 5_000_000))
        if log_file.exists() and log_file.stat().st_size > max_bytes:
            log_file.replace(log_dir / "audit.jsonl.1")
        entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **record}
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def state_file(root: Path, sid: str) -> Path:
    return root / LOG_DIR / "state" / f"{sid}.json"


def load_state(root: Path, sid: str) -> dict[str, Any]:
    try:
        return json.loads(state_file(root, sid).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(root: Path, sid: str, state: dict[str, Any]) -> None:
    path = state_file(root, sid)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state), encoding="utf-8")


# ---------------------------------------------------------------- payload parsing

def tool_name(event: dict[str, Any]) -> str:
    return str(event.get("toolName") or event.get("tool_name") or "").strip()


def tool_args(event: dict[str, Any]) -> Any:
    args = event.get("toolArgs", event.get("tool_input"))
    if isinstance(args, str):
        try:
            return json.loads(args)
        except json.JSONDecodeError:
            return args
    return args if args is not None else {}


def is_shell(name: str) -> bool:
    lowered = name.lower()
    return lowered in SHELL_TOOLS or "terminal" in lowered or "shell" in lowered


def is_write(name: str) -> bool:
    lowered = name.lower()
    return bool(WRITE_HINT.search(lowered)) and not READ_HINT.search(lowered)


def shell_command(args: Any) -> str:
    if isinstance(args, str):
        return args
    if isinstance(args, dict):
        for key in ("command", "cmd", "script"):
            if isinstance(args.get(key), str):
                return args[key]
    return ""


def collect_paths(value: Any, found: list[str]) -> list[str]:
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, str) and key.lower() in PATH_KEYS:
                found.append(item)
            else:
                collect_paths(item, found)
    elif isinstance(value, list):
        for item in value:
            collect_paths(item, found)
    elif isinstance(value, str):
        found.extend(match.group(1) for match in PATCH_HEADER.finditer(value))
    return found


def locate(raw: str, root: Path) -> tuple[str, bool] | None:
    """Return (posix path used for matching, is_outside_workspace)."""
    text = raw.strip()
    if not text:
        return None
    if text.startswith("file://"):
        text = unquote(urlparse(text).path)
    elif "://" in text:
        return None
    candidate = Path(os.path.expanduser(text))
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = Path(os.path.realpath(candidate))
    try:
        return resolved.relative_to(root).as_posix(), False
    except ValueError:
        return resolved.as_posix(), True


def match(path: str, patterns: list[str]) -> str | None:
    name = path.rsplit("/", 1)[-1]
    for pattern in patterns:
        if "/" not in pattern:
            if fnmatch.fnmatchcase(name, pattern):
                return pattern
            continue
        options = [pattern, pattern[3:]] if pattern.startswith("**/") else [pattern]
        for option in options:
            if fnmatch.fnmatchcase(path, option):
                return pattern
            if option.endswith("/**") and path == option[:-3]:
                return pattern
    return None


def is_secret(path: str, policy: dict[str, Any]) -> bool:
    rules = policy.get("secret_paths") or {}
    if match(path, rules.get("exceptions", [])):
        return False
    return match(path, rules.get("patterns", [])) is not None


# ---------------------------------------------------------------- pre-tool-use policy

def evaluate(event: dict[str, Any], policy: dict[str, Any], root: Path) -> tuple[str, str, str] | None:
    """Return (decision, rule, reason) for the most restrictive finding, or None."""
    name = tool_name(event)
    args = tool_args(event)
    findings: list[tuple[str, str, str]] = []

    if is_shell(name):
        command = shell_command(args)
        rules = policy.get("shell") or {}
        for level in ("deny", "ask"):
            for pattern in rules.get(level, []):
                try:
                    if re.search(pattern, command):
                        findings.append((level, f"shell_{level}",
                                         f"comando corresponde à regra de shell `{pattern}`"))
                        break
                except re.error:
                    continue
        for token in split_command(command):
            located = locate(token.lstrip("<>"), root) if not token.startswith("-") else None
            if located and is_secret(located[0], policy):
                findings.append(("ask", "shell_secret",
                                 f"comando referencia arquivo sensível `{token}`"))
                break

    write = is_write(name)
    protected = policy.get("protected_paths") or {}
    for raw in collect_paths(args, []):
        located = locate(raw, root)
        if located is None:
            continue
        path, outside = located
        if outside and write:
            level = str(policy.get("outside_workspace_write", "ask"))
            if level in SEVERITY:
                findings.append((level, "outside_workspace",
                                 f"escrita fora do workspace em `{path}`"))
        if write and not outside:
            for level in ("deny", "ask"):
                rule = match(path, protected.get(level, []))
                if rule:
                    findings.append((level, "protected_path",
                                     f"escrita em caminho protegido `{path}` (regra `{rule}`)"))
                    break
        if is_secret(path, policy):
            level = "ask" if write else "deny"
            findings.append((level, "secret_path", f"acesso a arquivo sensível `{path}`"))

    if not findings:
        return None
    return max(findings, key=lambda finding: SEVERITY[finding[0]])


def split_command(command: str) -> list[str]:
    if not command:
        return []
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return command.split()


def respond_permission(decision: str, reason: str) -> int:
    message = f"Hook de política: {reason}. Ajuste .github/hooks/config/policy.json se for legítimo."
    emit({
        "permissionDecision": decision,
        "permissionDecisionReason": message,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": message,
        },
    })
    if decision == "deny":
        print(message, file=sys.stderr)
        return 2
    return 0


# ---------------------------------------------------------------- handlers

def on_pre_tool_use(event: dict[str, Any], policy: dict[str, Any], root: Path) -> int:
    result = evaluate(event, policy, root)
    if result is None:
        return 0
    decision, rule, reason = result
    audit(root, policy, {"event": "preToolUse", "session": session_id(event),
                         "tool": tool_name(event), "outcome": decision, "rule": rule})
    return respond_permission(decision, reason)


def on_post_tool_use(event: dict[str, Any], policy: dict[str, Any], root: Path) -> int:
    name = tool_name(event)
    sid = session_id(event)
    audit(root, policy, {"event": "postToolUse", "session": sid, "tool": name,
                         "outcome": "success"})
    if is_write(name) and collect_paths(tool_args(event), []):
        state = load_state(root, sid)
        state["writes"] = int(state.get("writes", 0)) + 1
        save_state(root, sid, state)
    return 0


def on_post_tool_use_failure(event: dict[str, Any], policy: dict[str, Any], root: Path) -> int:
    audit(root, policy, {"event": "postToolUseFailure", "session": session_id(event),
                         "tool": tool_name(event), "outcome": "failure"})
    return 0


def on_session_start(event: dict[str, Any], policy: dict[str, Any], root: Path) -> int:
    settings = policy.get("session_context") or {}
    audit(root, policy, {"event": "sessionStart", "session": session_id(event),
                         "outcome": str(event.get("source", ""))})
    if not settings.get("enabled", True):
        return 0
    lines = ["Contexto do projeto (hook sessionStart):"]
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if branch:
        changed = git(root, "status", "--porcelain")
        count = len(changed.splitlines()) if changed else 0
        lines.append(f"- Branch: {branch}; arquivos alterados: {count}.")
    specs = root / "specs"
    if specs.is_dir():
        names = sorted(item.name for item in specs.iterdir() if item.is_dir())[:10]
        if names:
            lines.append(f"- Especificações: {', '.join(names)}.")
    lines.extend(f"- {line}" for line in settings.get("extra", []) if isinstance(line, str))
    lines.append("- Hooks ativos: operações destrutivas, segredos e caminhos protegidos "
                 "são bloqueados ou exigem confirmação.")
    context = "\n".join(lines)[:2000]
    emit({"additionalContext": context,
          "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}})
    return 0


def on_session_end(event: dict[str, Any], policy: dict[str, Any], root: Path) -> int:
    sid = session_id(event)
    audit(root, policy, {"event": "sessionEnd", "session": sid,
                         "outcome": str(event.get("reason", ""))})
    try:
        state_file(root, sid).unlink()
    except OSError:
        pass
    return 0


def on_agent_stop(event: dict[str, Any], policy: dict[str, Any], root: Path) -> int:
    gate = policy.get("quality_gate") or {}
    commands = gate.get("commands") or []
    if not gate.get("enabled") or not commands:
        return 0
    sid = session_id(event)
    state = load_state(root, sid)
    if int(state.get("writes", 0)) == 0:
        return 0
    blocks = int(state.get("blocks", 0))
    if blocks >= int(gate.get("max_blocks", 2)):
        audit(root, policy, {"event": "agentStop", "session": sid, "outcome": "gate_gave_up"})
        save_state(root, sid, {"writes": 0, "blocks": 0})
        emit({"systemMessage": "Quality gate ainda falha após as tentativas permitidas; "
                               "revise manualmente antes de integrar."})
        return 0

    failures = run_gate(commands, float(gate.get("timeout_sec", 240)), root)
    if not failures:
        audit(root, policy, {"event": "agentStop", "session": sid, "outcome": "gate_pass"})
        save_state(root, sid, {"writes": 0, "blocks": 0})
        return 0

    state["blocks"] = blocks + 1
    save_state(root, sid, state)
    audit(root, policy, {"event": "agentStop", "session": sid, "outcome": "gate_block"})
    reason = ("O quality gate do projeto falhou. Corrija e rode novamente antes de encerrar.\n"
              + "\n\n".join(failures))[:4000]
    emit({"decision": "block", "reason": reason,
          "hookSpecificOutput": {"hookEventName": "Stop", "decision": "block", "reason": reason}})
    return 0


def run_gate(commands: list[Any], budget: float, root: Path) -> list[str]:
    deadline = time.monotonic() + budget
    failures: list[str] = []
    for command in commands:
        if not (isinstance(command, list) and command and all(isinstance(p, str) for p in command)):
            failures.append(f"Comando inválido em quality_gate.commands: {command!r}")
            continue
        label = " ".join(command)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            failures.append(f"`{label}`: orçamento de tempo do quality gate esgotado.")
            break
        try:
            result = subprocess.run(command, cwd=root, capture_output=True, text=True,
                                    timeout=remaining, stdin=subprocess.DEVNULL, check=False)
        except FileNotFoundError:
            failures.append(f"`{label}`: executável não encontrado.")
            continue
        except subprocess.TimeoutExpired:
            failures.append(f"`{label}`: excedeu o orçamento de tempo.")
            break
        if result.returncode != 0:
            tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-30:])
            failures.append(f"`{label}` saiu com código {result.returncode}:\n{tail[-2500:]}")
    return failures


def git(root: Path, *args: str) -> str:
    if not (root / ".git").exists():
        return ""
    try:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                                timeout=2, stdin=subprocess.DEVNULL, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


HANDLERS = {
    "pre-tool-use": on_pre_tool_use,
    "post-tool-use": on_post_tool_use,
    "post-tool-use-failure": on_post_tool_use_failure,
    "session-start": on_session_start,
    "session-end": on_session_end,
    "agent-stop": on_agent_stop,
}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] in {"-h", "--help"}:
        print(__doc__)
        return 0 if len(argv) == 2 else 1
    event_name = argv[1]
    handler = HANDLERS.get(event_name)
    if handler is None:
        print(f"Evento desconhecido: {event_name}", file=sys.stderr)
        return 1
    root = Path(os.path.realpath(os.getcwd()))
    guarded = event_name == "pre-tool-use"
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
        if not isinstance(event, dict):
            raise ValueError("payload is not an object")
    except (json.JSONDecodeError, ValueError):
        if guarded:
            return respond_permission("deny", "evento com JSON inválido; chamada bloqueada")
        print("Evento com JSON inválido; ignorado.", file=sys.stderr)
        return 1
    policy, warning = load_policy(root)
    if warning:
        audit(root, policy, {"event": event_name, "outcome": warning})
    try:
        return handler(event, policy, root)
    except Exception as exc:  # noqa: BLE001 - pre-tool-use must fail closed on any error
        if guarded:
            return respond_permission("deny", f"falha interna do hook ({type(exc).__name__})")
        print(f"Falha interna do hook ({type(exc).__name__}).", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
