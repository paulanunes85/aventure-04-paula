#!/usr/bin/env python3
"""Verify that Open Horizons Copilot hooks can load and have executed.

Readiness has two tiers, and only the second is authoritative.

Static preconditions — descriptor inventory, handler presence, and
`disableAllHooks` — genuinely stop hooks from loading, so they are hard
failures. Folder trust is *not* one of them. Copilot defers repository hooks
while trust is unknown and loads them once trust is granted, and the
documented "currently running session only" grant never writes to
`trustedFolders`. Treating an absent entry as proof that hooks are ignored
produced a false negative that blocked launch in a workspace whose hooks were
demonstrably enforcing, so absence is now reported as unresolved trust rather
than as a blocked gate. Only the unattended launch mode, which runs with
`--no-ask-user` and cannot answer a trust prompt, still requires the
persistent form.

The authoritative signal remains sealed live evidence: a hash-chained ledger
whose `session-start` record carries the launcher's per-run nonce. That is the
only thing here that proves hooks actually executed, and it is what the
launcher blocks on.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any


REQUIRED_HOOKS = {
    "10-guardrails.json": {"preToolUse", "postToolUse", "postToolUseFailure"},
    "20-task-contract.json": {"sessionStart", "subagentStart"},
    "30-validation-gate.json": {"subagentStop", "agentStop", "sessionEnd"},
    "40-mcp-gate.json": {"permissionRequest", "preMcpToolCall"},
}
REQUIRED_RUNTIME_EVENTS = {"session-start"}
GITHUB_DIRECTORY = ".github"
HANDLER_REFERENCE = "fleet_gate.py"
HANDLER_SCRIPTS = ("fleet_gate.py", "fleet_policy.py", "fleet_sandbox.py")
COMMAND_FIELDS = ("bash", "powershell", "command")
# Documented `disableAllHooks` layers only. The official semantics are
# per-descriptor-file and repository/user settings; there is no documented
# last-wins layering, so any layer asserting `true` disables hooks here.
DISABLE_LAYER_NAMES = (
    "config.json",
    "settings.json",
)


def _load_fleet_policy(root: Path) -> Any:
    sys.dont_write_bytecode = True
    directory = root / GITHUB_DIRECTORY / "hooks" / "scripts"
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
    import fleet_policy as module

    return module


class HookReadinessError(RuntimeError):
    pass


def copy_json_string(text: str, start: int, output: list[str]) -> int:
    index = start
    escaped = False
    while index < len(text):
        character = text[index]
        output.append(character)
        index += 1
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == '"' and index > start + 1:
            break
    return index


def skip_line_comment(text: str, start: int) -> int:
    index = start + 2
    while index < len(text) and text[index] not in "\r\n":
        index += 1
    return index


def skip_block_comment(text: str, start: int, output: list[str]) -> int:
    index = start + 2
    while index + 1 < len(text) and text[index:index + 2] != "*/":
        if text[index] in "\r\n":
            output.append(text[index])
        index += 1
    return min(index + 2, len(text))


def next_non_whitespace(text: str, start: int) -> str:
    index = start
    while index < len(text) and text[index].isspace():
        index += 1
    return text[index] if index < len(text) else ""


def sanitize_jsonc(text: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(text):
        token = text[index:index + 2]
        if text[index] == '"':
            index = copy_json_string(text, index, output)
        elif token == "//":
            index = skip_line_comment(text, index)
        elif token == "/*":
            index = skip_block_comment(text, index, output)
        elif text[index] == "," and next_non_whitespace(text, index + 1) in "}]":
            index += 1
        else:
            output.append(text[index])
            index += 1
    return "".join(output)


def read_jsonc(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    cleaned = sanitize_jsonc(path.read_text(encoding="utf-8"))
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise HookReadinessError(f"cannot parse {path}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise HookReadinessError(f"{path} must contain an object")
    return value


def effective_hooks_disabled(root: Path, copilot_home: Path) -> bool:
    """Report whether any documented layer disables hooks.

    The official semantics are per-descriptor-file plus repository and user
    settings. There is no documented last-wins layering across files, so a
    later `false` never masks an earlier `true`; treating it as masking is how
    a `settings.local.json` could hide a genuine global disable.
    """
    layers = (
        copilot_home / "config.json",
        copilot_home / "settings.json",
        root / GITHUB_DIRECTORY / "copilot" / "settings.json",
        root / GITHUB_DIRECTORY / "copilot" / "settings.local.json",
    )
    return any(
        bool(read_jsonc(path).get("disableAllHooks", False)) for path in layers
    )


def trusted_folders(copilot_home: Path) -> set[Path]:
    config = read_jsonc(copilot_home / "config.json")
    raw_folders = config.get("trustedFolders", [])
    if not isinstance(raw_folders, list):
        raise HookReadinessError("trustedFolders must be a list")
    return {
        Path(folder).expanduser().resolve()
        for folder in raw_folders
        if isinstance(folder, str) and folder.strip()
    }


def trust_is_persistent(root: Path, copilot_home: Path) -> bool:
    """Report whether folder trust is *already durable* in `config.json`.

    Absence is not a denial. Copilot defers repository hooks while folder
    trust is unknown and loads them once trust is granted, including the
    documented "currently running session only" grant, which never writes to
    `trustedFolders`. Observed directly in the CLI log for this workspace:

        deferred repo hooks: folder trust unknown; waiting (cwd=<repo>)
        deferred repo hooks: loading for session <id>
        loadDeferredRepoHooks(<id>): loaded repo hooks (hookCount=8)

    So this predicate answers "is trust pre-established?", which only an
    unattended launch needs, and never "will hooks run?", which only sealed
    live evidence can answer.
    """
    return root.resolve() in trusted_folders(copilot_home)


def verify_canonical_layout(root: Path) -> None:
    """Prove `.github/hooks/` is the only repository hook surface.

    Generated bytecode is git-ignored rather than tracked, so it is repository
    hygiene owned by the primitive validator, not a runtime readiness signal.
    Checking it here would make the launch gate fail on a transient artifact.
    """
    if (root / GITHUB_DIRECTORY / "hook").exists():
        raise HookReadinessError(
            "stray `.github/hook` exists; the canonical directory is "
            "`.github/hooks`"
        )


def verify_descriptor_inventory(hooks_directory: Path) -> None:
    """Require the exact descriptor inventory, with no undocumented siblings.

    Copilot loads every `*.json` in the directory. An unreviewed sibling could
    register additional handlers or a `disableAllHooks` flag the launch gate
    never inspected, so the inventory must match exactly.
    """
    present = {path.name for path in sorted(hooks_directory.glob("*.json"))}
    missing = sorted(set(REQUIRED_HOOKS) - present)
    if missing:
        raise HookReadinessError(
            f"required hook descriptors are missing: {missing}")
    unexpected = sorted(present - set(REQUIRED_HOOKS))
    if unexpected:
        raise HookReadinessError(
            f"unreviewed hook descriptors are present: {unexpected}")


def verify_descriptors(root: Path) -> None:
    hooks_directory = root / GITHUB_DIRECTORY / "hooks"
    for name in HANDLER_SCRIPTS:
        script = hooks_directory / "scripts" / name
        if not script.is_file():
            raise HookReadinessError(f"fleet hook handler is missing: {name}")
        if not script.stat().st_mode & stat.S_IXUSR:
            raise HookReadinessError(
                f"fleet hook handler is not executable: {name}")
    verify_canonical_layout(root)
    verify_descriptor_inventory(hooks_directory)
    for filename, expected_events in REQUIRED_HOOKS.items():
        path = hooks_directory / filename
        payload = read_jsonc(path)
        if payload.get("version") != 1:
            raise HookReadinessError(
                f"{filename} must use hook schema version 1")
        if payload.get("disableAllHooks") is True:
            raise HookReadinessError(f"{filename} disables its own hooks")
        hooks = payload.get("hooks")
        if not isinstance(hooks, dict):
            raise HookReadinessError(f"{filename} has no hooks object")
        if set(hooks) != expected_events:
            raise HookReadinessError(
                f"{filename} must declare exactly {sorted(expected_events)}, "
                f"found {sorted(hooks)}"
            )
        verify_handler_references(filename, hooks)


def verify_handler_references(filename: str, hooks: dict[str, Any]) -> None:
    """Every declared event must actually invoke the repository handler."""
    for event, items in hooks.items():
        if not isinstance(items, list) or not items:
            raise HookReadinessError(
                f"{filename} event `{event}` has no hook entries")
        for item in items:
            commands = [
                item.get(field)
                for field in COMMAND_FIELDS
                if isinstance(item, dict)
            ]
            if not any(
                isinstance(command, str) and HANDLER_REFERENCE in command
                for command in commands
            ):
                raise HookReadinessError(
                    f"{filename} event `{event}` does not invoke "
                    f"{HANDLER_REFERENCE}"
                )


def verify_prerequisites(
    root: Path,
    copilot_home: Path | None = None,
    *,
    require_persistent_trust: bool = False,
) -> bool:
    """Verify the static preconditions and report the folder-trust state.

    Returns True when folder trust is already persistent. Descriptor layout
    and `disableAllHooks` are hard failures because they genuinely stop hooks
    from loading. Folder trust is different: it is resolved at session start,
    so its absence is only fatal for the unattended launch mode, which runs
    with `--no-ask-user` and therefore has nobody to answer the trust prompt.
    """
    repository_root = root.resolve()
    home = (
        copilot_home
        or Path(os.environ.get("COPILOT_HOME", "~/.copilot")).expanduser()
    ).resolve()
    verify_descriptors(repository_root)
    if effective_hooks_disabled(repository_root, home):
        raise HookReadinessError(
            "Copilot hooks are disabled by effective settings")
    persistent_trust = trust_is_persistent(repository_root, home)
    if not persistent_trust and require_persistent_trust:
        raise HookReadinessError(
            f"unattended launch requires persistent folder trust: "
            f"{repository_root} is absent from trustedFolders in "
            f"{home / 'config.json'}. An unattended run uses `--no-ask-user`, "
            "so nobody can answer the session trust prompt and repository "
            "hooks would stay deferred. Interactive sessions are unaffected."
        )
    return persistent_trust


def runtime_events(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    events: set[str] = set()
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise HookReadinessError(
                f"invalid runtime evidence at line {line_number}"
            ) from exc
        if isinstance(record, dict) and isinstance(record.get("event"), str):
            events.add(record["event"])
    return events


def verify_runtime_evidence(path: Path) -> None:
    missing = REQUIRED_RUNTIME_EVENTS - runtime_events(path)
    if missing:
        raise HookReadinessError(
            "runtime hook proof is missing events: " +
            ", ".join(sorted(missing))
        )


def verify_sealed_evidence(
    root: Path, control_directory: Path, expected_nonce: str
) -> None:
    """Require a sealed, hash-chained ledger carrying the launcher nonce.

    A hand-written evidence file cannot satisfy this: every record is signed
    with the launcher key, each line is chained to the previous line's bytes,
    and the separately sealed head detects truncation. The nonce proves a real
    hook execution inside a real Copilot session rather than a replayed file.
    """
    fleet_policy = _load_fleet_policy(root)
    try:
        key = fleet_policy.hook_key()
    except fleet_policy.SealError as exc:
        raise HookReadinessError(f"sealed evidence key unavailable: {exc}") from exc
    try:
        records = fleet_policy.read_ledger(control_directory, key)
    except fleet_policy.SealError as exc:
        raise HookReadinessError(f"sealed hook ledger did not verify: {exc}") from exc
    if not records:
        raise HookReadinessError("sealed hook ledger is empty")
    if records[0].get("event") != "ledger-genesis":
        raise HookReadinessError(
            "sealed hook ledger does not start at the launcher genesis")
    if not any(
        record.get("event") == "session-start"
        and record.get("nonce") == expected_nonce
        for record in records
    ):
        raise HookReadinessError(
            "sealed hook ledger has no sessionStart record carrying the "
            "launcher nonce"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify Copilot repository hook prerequisites and runtime proof."
    )
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--copilot-home", type=Path)
    parser.add_argument("--runtime-evidence", type=Path)
    parser.add_argument("--control-directory", type=Path)
    parser.add_argument("--expect-nonce")
    parser.add_argument(
        "--unattended",
        action="store_true",
        help=(
            "Assert the non-interactive launch mode, which cannot answer a "
            "session trust prompt and therefore requires persistent folder "
            "trust unless sealed live evidence is supplied."
        ),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    sealed_requested = (
        args.control_directory is not None or args.expect_nonce is not None
    )
    try:
        # Sealed live evidence outranks every static signal, so when it is
        # offered the static trust requirement is not applied pre-emptively;
        # it is only reconsidered if that evidence fails to verify.
        persistent_trust = verify_prerequisites(
            args.repository,
            args.copilot_home,
            require_persistent_trust=args.unattended and not sealed_requested,
        )
        if args.runtime_evidence is not None:
            verify_runtime_evidence(args.runtime_evidence)
        if sealed_requested:
            if args.control_directory is None or not args.expect_nonce:
                raise HookReadinessError(
                    "sealed evidence needs both --control-directory and "
                    "--expect-nonce"
                )
            verify_sealed_evidence(
                args.repository.resolve(),
                args.control_directory,
                args.expect_nonce,
            )
    except HookReadinessError as exc:
        print(f"HOOK_GATE=BLOCKED: {exc}", file=sys.stderr)
        return 2
    if sealed_requested:
        # Hooks provably executed and sealed a record carrying this run's
        # nonce. That is the authoritative readiness signal; whether the
        # folder was trusted persistently or only for the session is moot.
        print("HOOK_GATE=PASS (sealed live hook evidence verified)")
        return 0
    if not persistent_trust:
        # Not a failure: trust is unresolved, not denied. Say so precisely
        # instead of claiming hooks "would be silently ignored", and name the
        # only mode that actually needs the persistent form.
        print(
            "HOOK_GATE=PASS TRUST=UNRESOLVED: static preconditions hold; the "
            "repository is not in trustedFolders, so repository hooks are "
            "deferred until folder trust is granted at session start (a "
            "session-only grant is sufficient and is never written to "
            "trustedFolders). Only an unattended launch requires the "
            "persistent form; re-run with --unattended to assert it. "
            "Authoritative readiness is the sealed live hook canary "
            "(--control-directory with --expect-nonce)."
        )
        return 0
    print("HOOK_GATE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
