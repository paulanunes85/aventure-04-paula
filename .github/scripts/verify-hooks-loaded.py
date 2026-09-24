#!/usr/bin/env python3
"""Verify that the repository's Copilot hooks can load and have executed.

Static checks (errors block): every `*.json` at the root of
`.github/hooks/` is a valid descriptor (`version: 1`, non-empty `hooks`,
each entry with a `bash` or `powershell` command), every script a
command names exists (shell scripts must be executable), no stray
`.github/hook/` directory, and no layer sets `disableAllHooks`.

Runtime evidence is the audit log written by the kit handler
(`.github/hooks/.logs/audit.jsonl`). Only a `sessionStart` record proves
that hooks actually ran; pass --require-runtime to make it mandatory and
--session to bind it to one session. Folder trust is resolved by the
harness at session start and is not inferred here.

Exit codes: 0 pass, 1 errors (or warnings with --strict).
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GITHUB_DIR = Path(".github")
HOOKS_DIR = GITHUB_DIR / "hooks"
AUDIT_LOG = HOOKS_DIR / ".logs" / "audit.jsonl"
COMMAND_FIELDS = ("bash", "powershell")
SCRIPT_SUFFIXES = (".py", ".sh", ".ps1", ".js", ".mjs", ".cjs")
KNOWN_EVENTS = {
    "sessionStart", "sessionEnd", "userPromptSubmitted", "preToolUse",
    "postToolUse", "postToolUseFailure", "agentStop", "subagentStart",
    "subagentStop", "errorOccurred", "permissionRequest", "preCompact",
    "notification",
}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    events: set[str] = field(default_factory=set)


def string_end(text: str, start: int) -> int:
    """Index just past the JSON string literal opening at `start`."""
    i = start + 1
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == '"':
            return i + 1
        i += 1
    return len(text)


def strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments and trailing commas outside strings."""
    out: list[str] = []
    i = 0
    while i < len(text):
        char, pair = text[i], text[i:i + 2]
        if char == '"':
            end = string_end(text, i)
            out.append(text[i:end])
            i = end
        elif pair == "//":
            end = text.find("\n", i)
            i = len(text) if end < 0 else end
        elif pair == "/*":
            end = text.find("*/", i + 2)
            i = len(text) if end < 0 else end + 2
        else:
            if not (char == ","
                    and text[i + 1:].lstrip()[:1] in ("}", "]")):
                out.append(char)
            i += 1
    return "".join(out)


def read_json(path: Path, rep: Report, jsonc: bool = False) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(strip_jsonc(text) if jsonc else text)
    except (OSError, json.JSONDecodeError) as exc:
        rep.errors.append(f"{path}: cannot parse JSON ({exc})")
        return None


def script_paths(command: str) -> list[str]:
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        tokens = command.split()
    return [t for t in tokens if "/" in t and t.endswith(SCRIPT_SUFFIXES)]


def check_entry(rep: Report, root: Path, label: str, entry: Any) -> None:
    if not isinstance(entry, dict):
        rep.errors.append(f"{label}: entry must be an object")
        return
    commands: list[str] = [
        value for value in (entry.get(k) for k in COMMAND_FIELDS)
        if isinstance(value, str) and value.strip()]
    if not commands:
        rep.errors.append(f"{label}: needs a `bash` or `powershell` command")
        return
    if len(commands) < len(COMMAND_FIELDS):
        rep.warnings.append(f"{label}: declare both `bash` and "
                            "`powershell` for portability")
    timeout = entry.get("timeoutSec")
    if timeout is not None and (not isinstance(timeout, int) or timeout < 1):
        rep.errors.append(f"{label}: `timeoutSec` must be a positive integer")
    cwd = root / str(entry.get("cwd", "."))
    for command in commands:
        for token in script_paths(command):
            script = (cwd / token).resolve()
            if not script.is_file():
                rep.errors.append(f"{label}: script not found: {token}")
            elif token.endswith(".sh") and not os.access(script, os.X_OK):
                rep.errors.append(f"{label}: script not executable: {token}")


def check_descriptor(rep: Report, root: Path, path: Path) -> None:
    data = read_json(path, rep)
    if data is None:
        return
    name = path.name
    if not isinstance(data, dict) or data.get("version") != 1:
        rep.errors.append(f"{name}: must be an object with `version: 1`; "
                          "keep configuration JSON under a subfolder")
        return
    if data.get("disableAllHooks") is True:
        rep.errors.append(f"{name}: sets `disableAllHooks: true`")
    hooks = data.get("hooks")
    if not isinstance(hooks, dict) or not hooks:
        rep.errors.append(f"{name}: `hooks` must be a non-empty object")
        return
    for event, entries in hooks.items():
        if event not in KNOWN_EVENTS:
            rep.warnings.append(f"{name}: unknown event `{event}`")
        if not isinstance(entries, list) or not entries:
            rep.errors.append(f"{name}: event `{event}` has no entries")
            continue
        rep.events.add(event)
        for index, entry in enumerate(entries, 1):
            check_entry(rep, root, f"{name} {event}[{index}]", entry)


def check_settings(rep: Report, root: Path, copilot_home: Path) -> None:
    layers = (
        copilot_home / "config.json",
        copilot_home / "settings.json",
        root / GITHUB_DIR / "copilot" / "settings.json",
        root / GITHUB_DIR / "copilot" / "settings.local.json",
    )
    for path in layers:
        if not path.is_file():
            continue
        data = read_json(path, rep, jsonc=True)
        if isinstance(data, dict) and data.get("disableAllHooks") is True:
            rep.errors.append(f"{path}: `disableAllHooks` disables hooks")


def check_static(rep: Report, root: Path, copilot_home: Path) -> None:
    hooks_dir = root / HOOKS_DIR
    if (root / GITHUB_DIR / "hook").exists():
        rep.errors.append("stray `.github/hook/`; the canonical directory "
                          "is `.github/hooks/`")
    descriptors = sorted(hooks_dir.glob("*.json"))
    if not descriptors:
        rep.errors.append(f"no hook descriptor in {HOOKS_DIR}/")
    for path in descriptors:
        check_descriptor(rep, root, path)
    check_settings(rep, root, copilot_home)


def audit_events(path: Path, session: str | None) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        if session and record.get("session") != session:
            continue
        if isinstance(record.get("event"), str):
            counts[record["event"]] += 1
    return counts


def check_runtime(rep: Report, audit: Path, session: str | None,
                  required: bool) -> Counter[str]:
    add = rep.errors.append if required else rep.warnings.append
    if not audit.is_file():
        add(f"no runtime evidence: {audit} does not exist")
        return Counter()
    counts = audit_events(audit, session)
    if not counts.get("sessionStart"):
        scope = f" for session {session}" if session else ""
        add(f"no `sessionStart` record{scope} in {audit}")
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--copilot-home", type=Path,
                        default=Path(os.environ.get(
                            "COPILOT_HOME", "~/.copilot")).expanduser())
    parser.add_argument("--audit", type=Path, default=None,
                        help=f"audit log (default: {AUDIT_LOG})")
    parser.add_argument("--session", help="require evidence for this id")
    parser.add_argument("--require-runtime", action="store_true",
                        help="fail without a sessionStart audit record")
    parser.add_argument("--strict", action="store_true",
                        help="treat warnings as errors")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    rep = Report()
    check_static(rep, root, args.copilot_home)
    counts = check_runtime(rep, args.audit or root / AUDIT_LOG,
                           args.session,
                           args.require_runtime or bool(args.session))
    for message in rep.errors:
        print(f"ERROR {message}", file=sys.stderr)
    for message in rep.warnings:
        print(f"WARNING {message}", file=sys.stderr)
    observed = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    print(f"Hooks: events declared {len(rep.events)} "
          f"({', '.join(sorted(rep.events))}); "
          f"observed {observed or 'none'}; "
          f"errors {len(rep.errors)} warnings {len(rep.warnings)}")
    failed = rep.errors or (args.strict and rep.warnings)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
