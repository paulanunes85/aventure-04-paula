#!/usr/bin/env python3
"""Ponto de entrada portável dos hooks do GitHub Copilot.

Funciona com Copilot CLI, Copilot cloud agent e o harness Local do
VS Code. Lê o evento em JSON pela entrada padrão e responde no formato
aceito por cada harness.

Uso:
    python3 .github/hooks/scripts/hook.py <evento>

Eventos:
    pre-tool-use           Bloqueia ou pede confirmação para riscos.
    post-tool-use          Registra auditoria e conta escritas.
    post-tool-use-failure  Registra falhas de ferramenta.
    session-start          Injeta contexto curto do projeto.
    session-end            Registra o encerramento da sessão.
    agent-stop             Quality gate opcional antes de encerrar.

Configuração opcional: .github/hooks/config/policy.json
Somente biblioteca padrão; requer Python 3.9 ou superior.
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
from typing import Any, Optional, Tuple
from urllib.parse import unquote, urlparse

POLICY_FILE = Path(".github/hooks/config/policy.json")
LOG_DIR = Path(".github/hooks/.logs")

DEFAULT_POLICY: dict = {
    "protected_paths": {
        "deny": ["**/.git/**"],
        "ask": [".github/hooks/**", ".github/workflows/**"],
    },
    "secret_paths": {
        "patterns": [
            ".env", ".env.*", "*.pem", "*.key", "*.pfx", "*.p12",
            "id_rsa*", "id_ecdsa*", "id_ed25519*", ".npmrc", ".pypirc",
            ".netrc", "*.tfstate", "*.tfstate.*", "**/secrets/**",
        ],
        "exceptions": [
            ".env.example", ".env.sample", ".env.template", "*.pub",
        ],
    },
    "outside_workspace_write": "ask",
    "shell": {
        "deny": [
            r"\brm\s+(?:-\S+\s+)*(?:--\s+)?"
            r"(?:/|~|\$HOME|\$\{HOME\})(?:/\*?)?(?=\s|$|[;&|])",
            r"\bmkfs(?:\.\w+)?\b",
            r"\bdd\b[^\n;|&]*\bof=/dev/(?!null\b)",
            r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",
            r"\b(?:curl|wget)\b[^\n;|]*\|\s*(?:sudo\s+)?(?:ba|z|da|k)?sh\b",
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
            "Siga .github/copilot-instructions.md e .github/instructions/.",
            "Nenhum código sem requisito aprovado em specs/<NNN>-*/spec.md.",
            "Testes que verificam requisitos citam o REQ-ID em comentário.",
            "Nunca registre segredos, credenciais ou dados pessoais.",
        ],
    },
    "quality_gate": {
        "enabled": False,
        "commands": [],
        "timeout_sec": 240,
        "max_blocks": 2,
    },
}

SHELL_TOOLS = {
    "bash", "powershell", "pwsh", "sh", "zsh", "shell", "execute",
    "run_in_terminal", "runinterminal", "send_to_terminal",
    "run_command", "runcommand",
}
WRITE_HINT = re.compile(
    r"create|edit|write|replace|patch|insert|delete|remove|move|rename"
    r"|mkdir|directory|notebook"
)
READ_HINT = re.compile(r"read|view|get_|list|search|find|query")
PATH_KEYS = {
    "path", "filepath", "file_path", "target_file", "targetfile",
    "new_path", "newpath", "old_path", "oldpath", "destination",
    "dirpath", "dir_path", "notebook_path", "uri",
}
PATCH_HEADER = re.compile(
    r"^\*\*\* (?:(?:Add|Update|Delete) File|Move to): *(\S[^\n]*)$",
    re.M,
)
SEVERITY = {"ask": 1, "deny": 2}

Finding = Tuple[str, str, str]
Event = dict
Policy = dict


# ------------------------------------------------------------ policy / io

def load_policy(root: Path) -> Tuple[Policy, Optional[str]]:
    policy = json.loads(json.dumps(DEFAULT_POLICY))
    path = root / POLICY_FILE
    if not path.is_file():
        return policy, None
    try:
        custom = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return policy, f"policy_invalid:{type(exc).__name__}"
    if not isinstance(custom, dict):
        return policy, "policy_invalid:not_object"
    for key, value in custom.items():
        if key not in policy:
            continue
        if isinstance(policy[key], dict) and isinstance(value, dict):
            policy[key].update(value)
        else:
            policy[key] = value
    return policy, None


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()


def session_id(event: Event) -> str:
    raw = event.get("sessionId") or event.get("session_id") or "unknown"
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(raw))[:80]


def audit(root: Path, policy: Policy, record: dict) -> None:
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
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        line = json.dumps({"ts": now, **record}, ensure_ascii=False)
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        pass


def state_file(root: Path, sid: str) -> Path:
    return root / LOG_DIR / "state" / f"{sid}.json"


def load_state(root: Path, sid: str) -> dict:
    try:
        return json.loads(state_file(root, sid).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(root: Path, sid: str, state: dict) -> None:
    path = state_file(root, sid)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state), encoding="utf-8")


# ------------------------------------------------------- payload parsing

def tool_name(event: Event) -> str:
    return str(event.get("toolName") or event.get("tool_name") or "")


def tool_args(event: Event) -> Any:
    args = event.get("toolArgs", event.get("tool_input"))
    if isinstance(args, str):
        try:
            return json.loads(args)
        except ValueError:
            return args
    return {} if args is None else args


def is_shell(name: str) -> bool:
    lowered = name.lower()
    return (lowered in SHELL_TOOLS or "terminal" in lowered
            or "shell" in lowered)


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


def split_command(command: str) -> list:
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return command.split()


def collect_paths(value: Any, found: list) -> list:
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
        headers = PATCH_HEADER.finditer(value)
        found.extend(header.group(1).strip() for header in headers)
    return found


def locate(raw: str, root: Path) -> Optional[Tuple[str, bool]]:
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


def match(path: str, patterns: list) -> Optional[str]:
    name = path.rsplit("/", 1)[-1]
    for pattern in patterns:
        if matches_pattern(path, name, pattern):
            return pattern
    return None


def matches_pattern(path: str, name: str, pattern: str) -> bool:
    if "/" not in pattern:
        return fnmatch.fnmatchcase(name, pattern)
    options = [pattern]
    if pattern.startswith("**/"):
        options.append(pattern[3:])
    for option in options:
        if fnmatch.fnmatchcase(path, option):
            return True
        if option.endswith("/**") and path == option[:-3]:
            return True
    return False


def is_secret(path: str, policy: Policy) -> bool:
    rules = policy.get("secret_paths") or {}
    if match(path, rules.get("exceptions", [])):
        return False
    return match(path, rules.get("patterns", [])) is not None


# ---------------------------------------------------- pre-tool-use rules

def evaluate(event: Event, policy: Policy, root: Path) -> Optional[Finding]:
    """Return the most restrictive (decision, rule, reason), or None."""
    name = tool_name(event)
    args = tool_args(event)
    findings = []
    if is_shell(name):
        findings.extend(shell_findings(shell_command(args), policy, root))
    write = is_write(name)
    for raw in collect_paths(args, []):
        located = locate(raw, root)
        if located is not None:
            path, outside = located
            findings.extend(path_findings(path, outside, write, policy))
    if not findings:
        return None
    return max(findings, key=lambda finding: SEVERITY[finding[0]])


def shell_findings(command: str, policy: Policy, root: Path) -> list:
    findings = []
    rules = policy.get("shell") or {}
    for level in ("deny", "ask"):
        pattern = first_regex_match(rules.get(level, []), command)
        if pattern:
            reason = f"comando corresponde à regra de shell `{pattern}`"
            findings.append((level, f"shell_{level}", reason))
    for token in split_command(command):
        if token.startswith("-"):
            continue
        located = locate(token.lstrip("<>"), root)
        if located and is_secret(located[0], policy):
            reason = f"comando referencia arquivo sensível `{token}`"
            findings.append(("ask", "shell_secret", reason))
            break
    return findings


def first_regex_match(patterns: list, text: str) -> Optional[str]:
    for pattern in patterns:
        try:
            if re.search(pattern, text):
                return pattern
        except re.error:
            continue
    return None


def path_findings(path: str, outside: bool, write: bool,
                  policy: Policy) -> list:
    findings = []
    if write and outside:
        level = str(policy.get("outside_workspace_write", "ask"))
        if level in SEVERITY:
            reason = f"escrita fora do workspace em `{path}`"
            findings.append((level, "outside_workspace", reason))
    elif write:
        findings.extend(protected_findings(path, policy))
    if is_secret(path, policy):
        reason = f"acesso a arquivo sensível `{path}`"
        findings.append(("ask" if write else "deny", "secret_path", reason))
    return findings


def protected_findings(path: str, policy: Policy) -> list:
    protected = policy.get("protected_paths") or {}
    for level in ("deny", "ask"):
        rule = match(path, protected.get(level, []))
        if rule:
            reason = f"escrita em caminho protegido `{path}` (regra `{rule}`)"
            return [(level, "protected_path", reason)]
    return []


def respond_permission(decision: str, reason: str) -> int:
    message = (f"Hook de política: {reason}. Se for legítimo, ajuste "
               ".github/hooks/config/policy.json.")
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


# -------------------------------------------------------------- handlers

def on_pre_tool_use(event: Event, policy: Policy, root: Path) -> int:
    result = evaluate(event, policy, root)
    if result is None:
        return 0
    decision, rule, reason = result
    audit(root, policy, {
        "event": "preToolUse", "session": session_id(event),
        "tool": tool_name(event), "outcome": decision, "rule": rule,
    })
    return respond_permission(decision, reason)


def on_post_tool_use(event: Event, policy: Policy, root: Path) -> int:
    name = tool_name(event)
    sid = session_id(event)
    audit(root, policy, {
        "event": "postToolUse", "session": sid, "tool": name,
        "outcome": "success",
    })
    if is_write(name) and collect_paths(tool_args(event), []):
        state = load_state(root, sid)
        state["writes"] = int(state.get("writes", 0)) + 1
        save_state(root, sid, state)
    return 0


def on_post_tool_use_failure(event: Event, policy: Policy,
                             root: Path) -> int:
    audit(root, policy, {
        "event": "postToolUseFailure", "session": session_id(event),
        "tool": tool_name(event), "outcome": "failure",
    })
    return 0


def on_session_start(event: Event, policy: Policy, root: Path) -> int:
    audit(root, policy, {
        "event": "sessionStart", "session": session_id(event),
        "outcome": str(event.get("source", "")),
    })
    settings = policy.get("session_context") or {}
    if settings.get("enabled", True):
        context = build_context(root, settings)
        emit({
            "additionalContext": context,
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            },
        })
    return 0


def build_context(root: Path, settings: dict) -> str:
    lines = ["Contexto do projeto (hook sessionStart):"]
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if branch:
        changed = git(root, "status", "--porcelain")
        count = len(changed.splitlines()) if changed else 0
        lines.append(f"- Branch: {branch}; arquivos alterados: {count}.")
    specs = root / "specs"
    if specs.is_dir():
        names = sorted(d.name for d in specs.iterdir() if d.is_dir())[:10]
        if names:
            lines.append(f"- Especificações: {', '.join(names)}.")
    extra = settings.get("extra", [])
    lines.extend(f"- {line}" for line in extra if isinstance(line, str))
    lines.append("- Hooks ativos: operações destrutivas, segredos e caminhos "
                 "protegidos são bloqueados ou exigem confirmação.")
    return "\n".join(lines)[:2000]


def on_session_end(event: Event, policy: Policy, root: Path) -> int:
    sid = session_id(event)
    audit(root, policy, {
        "event": "sessionEnd", "session": sid,
        "outcome": str(event.get("reason", "")),
    })
    try:
        state_file(root, sid).unlink()
    except OSError:
        pass
    return 0


def on_agent_stop(event: Event, policy: Policy, root: Path) -> int:
    gate = policy.get("quality_gate") or {}
    sid = session_id(event)
    state = load_state(root, sid)
    if not gate_applies(gate, state):
        return 0
    blocks = int(state.get("blocks", 0))
    if blocks >= int(gate.get("max_blocks", 2)):
        record_gate(root, policy, sid, "gate_gave_up")
        emit({"systemMessage": "O quality gate ainda falha após as "
                               "tentativas permitidas; revise manualmente."})
        return 0
    budget = float(gate.get("timeout_sec", 240))
    failures = run_gate(gate["commands"], budget, root)
    if not failures:
        record_gate(root, policy, sid, "gate_pass")
        return 0
    save_state(root, sid, {**state, "blocks": blocks + 1})
    audit(root, policy, {
        "event": "agentStop", "session": sid, "outcome": "gate_block",
    })
    reason = ("O quality gate do projeto falhou. Corrija e execute "
              "novamente antes de encerrar.\n\n" + "\n\n".join(failures))
    emit({
        "decision": "block",
        "reason": reason[:4000],
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "decision": "block",
            "reason": reason[:4000],
        },
    })
    return 0


def gate_applies(gate: dict, state: dict) -> bool:
    enabled = bool(gate.get("enabled")) and bool(gate.get("commands"))
    return enabled and int(state.get("writes", 0)) > 0


def record_gate(root: Path, policy: Policy, sid: str, outcome: str) -> None:
    save_state(root, sid, {"writes": 0, "blocks": 0})
    audit(root, policy, {
        "event": "agentStop", "session": sid, "outcome": outcome,
    })


def run_gate(commands: list, budget: float, root: Path) -> list:
    deadline = time.monotonic() + budget
    failures = []
    for command in commands:
        if not valid_argv(command):
            failures.append(f"Comando inválido no quality gate: {command!r}")
            continue
        remaining = deadline - time.monotonic()
        failure = run_one(command, remaining, root)
        if failure:
            failures.append(failure)
            if "tempo" in failure:
                break
    return failures


def valid_argv(command: Any) -> bool:
    return (isinstance(command, list) and bool(command)
            and all(isinstance(part, str) for part in command))


def run_one(command: list, remaining: float, root: Path) -> Optional[str]:
    label = " ".join(command)
    if remaining <= 0:
        return f"`{label}`: orçamento de tempo esgotado."
    try:
        result = subprocess.run(
            command, cwd=root, capture_output=True, text=True,
            timeout=remaining, stdin=subprocess.DEVNULL, check=False,
        )
    except FileNotFoundError:
        return f"`{label}`: executável não encontrado."
    except subprocess.TimeoutExpired:
        return f"`{label}`: excedeu o orçamento de tempo."
    if result.returncode == 0:
        return None
    output = (result.stdout + result.stderr).strip().splitlines()
    tail = "\n".join(output[-30:])[-2500:]
    return f"`{label}` saiu com código {result.returncode}:\n{tail}"


def git(root: Path, *args: str) -> str:
    if not (root / ".git").exists():
        return ""
    try:
        result = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True,
            timeout=2, stdin=subprocess.DEVNULL, check=False,
        )
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


def read_event() -> Event:
    raw = sys.stdin.read()
    event = json.loads(raw) if raw.strip() else {}
    if not isinstance(event, dict):
        raise ValueError("payload is not a JSON object")
    return event


def main(argv: list) -> int:
    if len(argv) != 2 or argv[1] in {"-h", "--help"}:
        print(__doc__)
        return 0 if len(argv) == 2 else 1
    handler = HANDLERS.get(argv[1])
    if handler is None:
        print(f"Evento desconhecido: {argv[1]}", file=sys.stderr)
        return 1
    guarded = argv[1] == "pre-tool-use"
    root = Path(os.path.realpath(os.getcwd()))
    try:
        event = read_event()
    except ValueError:
        if guarded:
            return respond_permission("deny", "evento com JSON inválido")
        print("Evento com JSON inválido; ignorado.", file=sys.stderr)
        return 1
    policy, warning = load_policy(root)
    if warning:
        audit(root, policy, {"event": argv[1], "outcome": warning})
    try:
        return handler(event, policy, root)
    except Exception as exc:  # pylint: disable=broad-except
        # pre-tool-use must fail closed on any unexpected error.
        reason = f"falha interna do hook ({type(exc).__name__})"
        if guarded:
            return respond_permission("deny", reason)
        print(reason, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
