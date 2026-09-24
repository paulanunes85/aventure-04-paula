#!/usr/bin/env python3
"""Sealed control plane and command policy shared by the fleet gate and runner.

This module is imported by `.github/hooks/scripts/fleet_gate.py` (trusted hook
context) and by `scripts/run_fleet.py` (trusted launcher context). It owns the
primitives that must behave identically on both sides:

* contract/state sealing with a launcher-generated HMAC key,
* a hash-chained evidence ledger with an independently sealed head record,
* content digests of owned trees plus repository binding,
* the argv policy for trusted validation vectors,
* the child-environment allowlist,
* the `CONFINED_LITE` capability removal sets.

Security notes
--------------
The HMAC key never touches disk and is never written into evidence, injected
context, or process output. POSIX modes are not a trust boundary against a
same-uid process; the boundary is that the control directory lives outside the
repository, structured tool calls to it are denied by the gate, and every
control record is sealed so tampering is detected rather than merely
discouraged.
"""

from __future__ import annotations

import contextlib
import errno
import hashlib
import hmac
import json
import os
import re
import shlex
import stat
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

try:  # POSIX advisory locking is the primary inter-process lock.
    import fcntl
except ImportError:  # pragma: no cover - exercised only on non-POSIX hosts
    fcntl = None  # type: ignore[assignment]


CONTRACT_ENV = "OPEN_HORIZONS_FLEET_HOOK_CONTRACT"
KEY_ENV = "OPEN_HORIZONS_FLEET_HOOK_KEY"
CONTRACT_SCHEMA_VERSION = 2
STATE_SCHEMA_VERSION = 2
LEDGER_NAME = "hook-evidence.jsonl"
LEDGER_HEAD_NAME = "hook-ledger-head.json"
STATE_NAME = "hook-state.json"
CONTRACT_NAME = "hook-contract.json"
BASELINE_NAME = "hook-baseline-tree.json"
ABORT_NAME = "abort"
LOCK_NAME = "hook-control.lock"
SCRATCH_NAME = "scratch"
CONTROL_DIRECTORY_MODE = 0o700
CONTROL_FILE_MODE = 0o600
KEY_BYTES = 32
MAC_PREFIX = "hmac-sha256:"
# Every control-plane mutation is serialised behind one lock. A hook process
# only ever holds it for a short transaction, never across validation.
LOCK_TIMEOUT_SECONDS = 120.0
LOCK_POLL_SECONDS = 0.02
LOCK_STALE_SECONDS = 300.0


# Copilot CLI ends the turn itself after 8 consecutive `block` continuations
# (hooks reference, "Runaway guard"). One global counter is capped strictly
# below that ceiling so the gate always reaches its own terminal decision.
COPILOT_RUNAWAY_BLOCK_GUARD = 8
MAX_CONSECUTIVE_BLOCKS = 4
# A hook timeout is fail-open, so the handler budget must expire before the
# descriptor `timeoutSec`.
VALIDATION_BUDGET_MARGIN_SECONDS = 60
VALIDATION_BUDGET_FLOOR_SECONDS = 60
# Model-visible failure excerpts are repair feedback, not logs. Keeping them
# small bounds both prompt cost and the blast radius of an imperfect redactor.
VALIDATION_OUTPUT_CAP_BYTES = 8192

MODE_CONFINED_LITE = "CONFINED_LITE"
PURPOSE_CANARY = "canary"
PURPOSE_FLEET = "fleet"
# Per-run hook liveness proof. A `liveness` contract declares no task at all,
# so it can neither dispatch nor write: its only job is to make a real
# launcher-spawned session fire `sessionStart` and seal the launcher nonce.
# The gate treats it exactly like any non-canary contract — it is deliberately
# *not* `canary_verified`, so a write or dispatch attempted during a liveness
# session is denied `canary-not-verified` rather than evaluated.
PURPOSE_LIVENESS = "liveness"
# Durable, launcher-owned platform containment attestation. It lives in the
# control root beside the per-run control directories, never in a repository,
# and is sealed with a key that is never exported into any child environment.
ATTESTATION_NAME = "containment-attestation.json"
ATTESTATION_KEY_NAME = "attestation.key"
ATTESTATION_SCHEMA_VERSION = 1

# Structured write tools understood by the gate.
WRITE_TOOLS = frozenset(
    {
        "apply_patch",
        "create",
        "edit",
        "multi_edit",
        "notebook_edit",
        "str_replace",
        "str_replace_editor",
        "write",
        "write_file",
    }
)
# Every shell-family tool name, including the async session variants. In
# `CONFINED_LITE` these are removed from the model's tool set *and* denied by
# the gate, because a backgrounded command outlives the stop-hook digest.
SHELL_TOOLS = frozenset(
    {
        "bash",
        "execute",
        "exec",
        "list_bash",
        "list_powershell",
        "powershell",
        "read_bash",
        "read_powershell",
        "run_in_terminal",
        "shell",
        "stop_bash",
        "stop_powershell",
        "write_bash",
        "write_powershell",
    }
)
AGENT_MESSAGING_TOOLS = frozenset({"list_agents", "read_agent", "write_agent"})
DISPATCH_TOOLS = frozenset({"task"})
# Tool names accepted by `--excluded-tools`, limited to values documented in
# the CLI command reference so the flag cannot be rejected at launch.
CONFINED_LITE_EXCLUDED_TOOLS = (
    "bash",
    "list_agents",
    "list_bash",
    "list_powershell",
    "powershell",
    "read_agent",
    "read_bash",
    "read_powershell",
    "stop_bash",
    "stop_powershell",
    "web_fetch",
    "write_agent",
    "write_bash",
    "write_powershell",
)
# `--deny-tool` beats every allow rule, including `--allow-all-tools`.
DENY_TOOL_STEMS = (
    "shell(git commit)",
    "shell(git push)",
    "shell(git merge)",
    "shell(git rebase)",
    "shell(git reset)",
    "shell(git checkout)",
    "shell(git switch)",
    "shell(git clean)",
    "shell(git stash)",
    "shell(git tag)",
    "shell(git revert)",
    "shell(git worktree)",
    "shell(git config)",
    "shell(git add)",
    "shell(git apply)",
    "shell(git update-index)",
    "shell(gh)",
    "shell(az)",
    "shell(terraform)",
    "shell(kubectl)",
    "shell(helm)",
    "shell(docker)",
    "shell(npm)",
    "shell(yarn)",
    "shell(pnpm)",
    "shell(curl)",
    "shell(wget)",
    "shell(ssh)",
    "shell(scp)",
    "shell(rsync)",
    "shell(sudo)",
    "shell(chmod)",
    "shell(chown)",
    "shell(rm)",
    "shell(mv)",
    "shell(dd)",
    "shell(env)",
    "shell(xargs)",
    "shell(eval)",
    "shell(sh)",
    "shell(bash)",
    "shell(zsh)",
    "shell(nc)",
    "shell(socat)",
    "shell(base64)",
    "shell(open)",
    "shell(osascript)",
)
# High-impact operations that must be denied at two independent layers: the CLI
# permission layer (`--deny-tool`) and the trusted-vector argv policy.
HIGH_IMPACT_OPERATIONS = (
    ("git", "commit"),
    ("git", "push"),
    ("terraform", "apply"),
    ("az", "deployment"),
    ("kubectl", "apply"),
    ("helm", "install"),
    ("npm", "publish"),
    ("docker", "push"),
)

# Repository paths that are never a structured-write destination for a fleet
# subagent, regardless of task ownership.
DENIED_REPOSITORY_SUBTREES = (
    ".git",
    ".github/hooks",
    ".test-results",
)
# Directory names skipped by content digests; they are build scratch, not
# reviewable task content.
DIGEST_EXCLUDED_NAMES = frozenset(
    {
        ".DS_Store",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".terraform",
        "__pycache__",
        "node_modules",
    }
)

# Child-environment allowlist for the *Copilot* session. Everything else is
# dropped before Copilot runs, so Azure, AWS, Kubernetes, and generic secret
# variables never reach the model or any tool it invokes.
#
# `OPEN_HORIZONS_FLEET_*` is deliberately **not** a prefix here. The launcher
# sets the contract path and the run key explicitly on the one child that needs
# them; inheriting the prefix would leak the sealing key into every git and
# validation subprocess as well (finding N1).
ENVIRONMENT_ALLOWED_NAMES = frozenset(
    {
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "LOGNAME",
        "PATH",
        "SHELL",
        "TERM",
        "TMPDIR",
        "TZ",
        "USER",
    }
)
ENVIRONMENT_ALLOWED_PREFIXES = ("COPILOT_",)
ENVIRONMENT_SENSITIVE = re.compile(
    r"(?:^(?:AZURE|ARM|AWS|GOOGLE|GCP|TF_VAR|DOCKER|NPM|KUBE)_)"
    r"|(?:^KUBECONFIG$)"
    r"|(?:_(?:TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIALS|APIKEY|PRIVATE_KEY)$)"
    r"|(?:^(?:SECRET|PASSWORD|APIKEY|API_KEY)$)",
    re.IGNORECASE,
)
ENVIRONMENT_AUTH_EXEMPT = frozenset({"GH_TOKEN", "GITHUB_TOKEN"})

# Trusted-vector argv policy.
DANGEROUS_ARGUMENT_CHARACTERS = frozenset(";|&><$`()[]{}*?~!#\\'\"\n\r\t")
INLINE_CODE_FLAGS = frozenset(
    {
        "-c",
        "-e",
        "-o",
        "-O",
        "-i",
        "--eval",
        "--command",
        "-command",
        "-Command",
        "-exec",
        "-execdir",
        "--inplace",
        "--in-place",
        "--upload-file",
    }
)
DANGEROUS_EXECUTABLES = frozenset(
    {
        "awk",
        "az",
        "base64",
        "bash",
        "chmod",
        "chown",
        "cp",
        "csh",
        "curl",
        "dash",
        "dd",
        "doas",
        "env",
        "eval",
        "exec",
        "find",
        "fish",
        "gh",
        "git",
        "helm",
        "kubectl",
        "ksh",
        "ln",
        "make",
        "mv",
        "nc",
        "nohup",
        "npm",
        "npx",
        "open",
        "osascript",
        "perl",
        "pnpm",
        "rm",
        "rsync",
        "ruby",
        "scp",
        "script",
        "sed",
        "setsid",
        "sh",
        "socat",
        "ssh",
        "sudo",
        "tee",
        "time",
        "timeout",
        "wget",
        "xargs",
        "yarn",
        "zsh",
    }
)
# The single measured exception: `bash -n <script>` is parse-only and executes
# nothing. It is accepted with exact arity so no other bash form can reuse it.
BASH_PARSE_ONLY = ("bash", "-n")
PYTHON_EXECUTABLES = frozenset({"python", "python3"})
PYTHON_MODULE_ALLOWLIST = frozenset({"py_compile", "pytest", "unittest"})

# Retained as a tripwire only. Regex over free-form command strings is
# not a security boundary: `g""it push`, `$(...)`, and interpreter flags all
# evade it. Real containment is capability removal plus the sealed control
# plane; a tripwire match records a reason code and denies, but it never
# grants and is never the only control.
FORBIDDEN_COMMAND = re.compile(
    r"(?:\bgit(?:\s+-C\s+\S+)?\s+"
    r"(?:add|apply|checkout|clean|commit|merge|push|rebase|reset|restore|"
    r"revert|stash|switch|tag|update-index|worktree)\b|"
    r"\bgh\s+(?:pr|release|repo)\b|"
    r"\bgh\s+workflow\s+(?:run|enable|disable)\b|"
    r"\bgh\s+api\b[^\n]*?(?:-X|--method)\s*=?\s*"
    r"(?:POST|PUT|PATCH|DELETE)\b|"
    r"\bterraform\s+(?:apply|destroy|import|taint|state)\b|"
    r"\bkubectl\s+(?:apply|create|delete|patch|replace|scale|edit)\b|"
    r"\bhelm\s+(?:install|upgrade|uninstall|rollback)\b|"
    r"\baz\s+\S+\s+(?:create|delete|update|purge|restore|start|stop)\b|"
    r"\baz\s+deployment\b|"
    r"\b(?:npm|yarn|pnpm)\s+publish\b|"
    r"\bdocker\s+push\b|"
    # `rm` against a root-ish target: `rm -rf /`, `rm -rf /*`,
    # `rm --no-preserve-root -rf /`, and `rm -rf -- /`.
    r"\brm\b[^\n]*?(?:--no-preserve-root\b|"
    r"(?<=\s)/(?:\*|\s|$))|"
    r"\brm\s+(?:-[A-Za-z-]+\s+)*/(?:\*)?(?:\s|$))",
    re.IGNORECASE,
)
PROTECTED_BRANCH_PUSH = re.compile(
    r"\bgit(?:\s+-C\s+\S+)?\s+push\b", re.IGNORECASE
)
MCP_TOOL_PATTERN = re.compile(r"(?:^|[._-])mcp(?:[._-]|$)|__")


class SealError(RuntimeError):
    """A sealed control-plane record is missing, unreadable, or tampered."""


class PolicyError(RuntimeError):
    """A command vector violates the trusted-validation argv policy."""


class LockError(RuntimeError):
    """The control-plane lock could not be acquired inside its budget."""


# ---------------------------------------------------------------------------
# Inter-process control-plane lock
# ---------------------------------------------------------------------------

# Depth counter per lock path. The lock is reentrant *within* one process so a
# transaction may append evidence while holding the state lock, and exclusive
# *between* processes so two overlapping hook invocations cannot interleave a
# read-head / append / reseal-head sequence or a load / mutate / save sequence.
_LOCK_DEPTH: dict[str, int] = {}


def lock_path(control_directory: Path) -> Path:
    return control_directory / LOCK_NAME


def _acquire_flock(handle: int, deadline: float, path: str) -> None:
    while True:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except OSError as exc:
            if exc.errno not in (errno.EACCES, errno.EAGAIN, errno.EWOULDBLOCK):
                raise LockError(f"cannot lock the control plane: {exc}") from exc
            if time.monotonic() >= deadline:
                raise LockError(
                    f"timed out waiting for the control-plane lock: {path}"
                ) from exc
            time.sleep(LOCK_POLL_SECONDS)


def _acquire_exclusive_file(path: Path, deadline: float) -> int:
    """Portable fallback for hosts without `fcntl`: an `O_EXCL` sentinel."""
    sentinel = path.with_suffix(path.suffix + ".excl")
    while True:
        try:
            return os.open(
                sentinel, os.O_CREAT | os.O_EXCL | os.O_RDWR, CONTROL_FILE_MODE
            )
        except FileExistsError:
            try:
                age = time.time() - sentinel.stat().st_mtime
            except OSError:
                age = 0.0
            if age > LOCK_STALE_SECONDS:
                with contextlib.suppress(OSError):
                    sentinel.unlink()
                continue
            if time.monotonic() >= deadline:
                raise LockError(
                    f"timed out waiting for the control-plane lock: {sentinel}"
                )
            time.sleep(LOCK_POLL_SECONDS)


@contextlib.contextmanager
def control_lock(
    control_directory: Path, timeout: float = LOCK_TIMEOUT_SECONDS
) -> Iterator[None]:
    """Hold the exclusive control-plane lock across one transaction.

    Every ledger append (read head → append line → reseal head) and every state
    load → mutate → save must run inside this, otherwise concurrent hook
    processes corrupt the hash chain or silently discard each other's writes
    (finding N4). The lock is never held across validation; long handlers
    release it, run the vectors, then reacquire and merge.
    """
    path = lock_path(control_directory)
    key = str(path)
    depth = _LOCK_DEPTH.get(key, 0)
    if depth:
        _LOCK_DEPTH[key] = depth + 1
        try:
            yield
        finally:
            _LOCK_DEPTH[key] = depth
        return
    control_directory.mkdir(parents=True, exist_ok=True, mode=CONTROL_DIRECTORY_MODE)
    deadline = time.monotonic() + timeout
    sentinel: Path | None = None
    if fcntl is not None:
        handle = os.open(path, os.O_CREAT | os.O_RDWR, CONTROL_FILE_MODE)
        _acquire_flock(handle, deadline, key)
    else:  # pragma: no cover - exercised only on non-POSIX hosts
        handle = _acquire_exclusive_file(path, deadline)
        sentinel = path.with_suffix(path.suffix + ".excl")
    _LOCK_DEPTH[key] = 1
    try:
        yield
    finally:
        _LOCK_DEPTH.pop(key, None)
        try:
            if fcntl is not None:
                with contextlib.suppress(OSError):
                    fcntl.flock(handle, fcntl.LOCK_UN)
        finally:
            with contextlib.suppress(OSError):
                os.close(handle)
            if sentinel is not None:  # pragma: no cover - non-POSIX only
                with contextlib.suppress(OSError):
                    sentinel.unlink()



def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def generate_key() -> str:
    """Return a fresh 256-bit launcher key as hex."""
    return os.urandom(KEY_BYTES).hex()


def hook_key(environ: Mapping[str, str] | None = None) -> bytes:
    source = os.environ if environ is None else environ
    raw = source.get(KEY_ENV, "").strip()
    if not raw:
        raise SealError("fleet hook key is not present in the environment")
    try:
        key = bytes.fromhex(raw)
    except ValueError as exc:
        raise SealError("fleet hook key is not valid hex") from exc
    if len(key) < KEY_BYTES:
        raise SealError("fleet hook key is too short")
    return key


def compute_mac(key: bytes, body: Any) -> str:
    return MAC_PREFIX + hmac.new(
        key, canonical_bytes(body), hashlib.sha256
    ).hexdigest()


def seal(payload: Mapping[str, Any], key: bytes) -> dict[str, Any]:
    body = {name: value for name, value in payload.items() if name != "mac"}
    return {**body, "mac": compute_mac(key, body)}


def verify_seal(payload: Any, key: bytes) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SealError("sealed record must be an object")
    declared = payload.get("mac")
    if not isinstance(declared, str) or not declared.startswith(MAC_PREFIX):
        raise SealError("sealed record has no signature")
    body = {name: value for name, value in payload.items() if name != "mac"}
    if not hmac.compare_digest(declared, compute_mac(key, body)):
        raise SealError("sealed record signature does not verify")
    return body


def atomic_write(path: Path, text: str, mode: int = CONTROL_FILE_MODE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=CONTROL_DIRECTORY_MODE)
    handle = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    )
    try:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    finally:
        handle.close()
    temporary = Path(handle.name)
    os.chmod(temporary, mode)
    temporary.replace(path)


def write_sealed_json(
    path: Path,
    payload: Mapping[str, Any],
    key: bytes,
    mode: int = CONTROL_FILE_MODE,
) -> dict[str, Any]:
    sealed = seal(payload, key)
    atomic_write(path, json.dumps(sealed, sort_keys=True) + "\n", mode)
    return sealed


def read_sealed_json(path: Path, key: bytes) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SealError(f"cannot read sealed record: {path.name}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SealError(f"sealed record is not valid JSON: {path.name}") from exc
    return verify_seal(payload, key)


def line_digest(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def ledger_head_path(control_directory: Path) -> Path:
    return control_directory / LEDGER_HEAD_NAME


def ledger_path(control_directory: Path) -> Path:
    return control_directory / LEDGER_NAME


def read_ledger_head(control_directory: Path, key: bytes) -> dict[str, Any]:
    path = ledger_head_path(control_directory)
    if not path.is_file():
        return {"count": 0, "head": "genesis"}
    head = read_sealed_json(path, key)
    if not isinstance(head.get("count"), int) or not isinstance(
        head.get("head"), str
    ):
        raise SealError("ledger head record is malformed")
    return head


def append_ledger(
    control_directory: Path, key: bytes, record: Mapping[str, Any]
) -> dict[str, Any]:
    """Append one hash-chained, signed ledger record and reseal the head.

    `prev` binds each record to the exact bytes of its predecessor, so a forged
    or reordered line breaks the chain. The separately sealed head record
    carries the authoritative count and terminal digest, so removing trailing
    lines is detected as truncation rather than read as a shorter history.

    The whole read-head → append → reseal-head sequence runs under the
    control-plane lock; without it two concurrent hooks produce duplicate
    sequence numbers and the chain no longer verifies (finding N4).
    """
    with control_lock(control_directory):
        head = read_ledger_head(control_directory, key)
        body = {**record, "seq": head["count"], "prev": head["head"]}
        sealed = seal(body, key)
        line = json.dumps(sealed, sort_keys=True)
        path = ledger_path(control_directory)
        path.parent.mkdir(
            parents=True, exist_ok=True, mode=CONTROL_DIRECTORY_MODE
        )
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(path, CONTROL_FILE_MODE)
        write_sealed_json(
            ledger_head_path(control_directory),
            {"count": head["count"] + 1, "head": line_digest(line)},
            key,
        )
        return sealed


def read_ledger(control_directory: Path, key: bytes) -> list[dict[str, Any]]:
    """Verify and return every ledger record, or raise `SealError`.

    Verifies each signature, that sequence numbers are dense and ordered, that
    `prev` matches the previous line bytes, and that the sealed head agrees
    with the file, which is what makes truncation and forgery both detectable.
    """
    with control_lock(control_directory):
        path = ledger_path(control_directory)
        head = read_ledger_head(control_directory, key)
        if not path.is_file():
            if head["count"]:
                raise SealError(
                    "sealed ledger is missing but the head records entries"
                )
            return []
        records: list[dict[str, Any]] = []
        previous = "genesis"
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines()
        ):
            if not line.strip():
                raise SealError(f"ledger line {number} is empty")
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SealError(f"ledger line {number} is not valid JSON") from exc
            body = verify_seal(payload, key)
            if body.get("seq") != number:
                raise SealError(
                    f"ledger line {number} has an out-of-order sequence"
                )
            if body.get("prev") != previous:
                raise SealError(f"ledger line {number} breaks the hash chain")
            previous = line_digest(line)
            records.append(body)
        if len(records) != head["count"] or previous != head["head"]:
            raise SealError("sealed ledger does not match its sealed head")
        return records


def control_root(environ: Mapping[str, str] | None = None) -> Path:
    """Return the launcher-owned control root, always outside any repository."""
    source = os.environ if environ is None else environ
    state_home = source.get("XDG_STATE_HOME", "").strip()
    base = (
        Path(state_home)
        if state_home
        else Path(source.get("HOME", str(Path.home()))) / ".local" / "state"
    )
    return base.expanduser() / "open-horizons" / "fleet"


def create_control_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=False, mode=CONTROL_DIRECTORY_MODE)
    os.chmod(path, CONTROL_DIRECTORY_MODE)
    (path / SCRATCH_NAME).mkdir(mode=CONTROL_DIRECTORY_MODE)
    return path


def abort_path(control_directory: Path) -> Path:
    return control_directory / ABORT_NAME


def raise_abort(control_directory: Path, reason_code: str) -> None:
    try:
        atomic_write(abort_path(control_directory), reason_code + "\n")
    except OSError:
        pass


def is_aborted(control_directory: Path) -> bool:
    return abort_path(control_directory).is_file()


def scrub_environment(
    source: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Return the child environment allowlist with sensitive names removed."""
    origin = os.environ if source is None else source
    scrubbed: dict[str, str] = {}
    for name, value in origin.items():
        allowed = name in ENVIRONMENT_ALLOWED_NAMES or name.startswith(
            ENVIRONMENT_ALLOWED_PREFIXES
        )
        if not allowed:
            continue
        if name not in ENVIRONMENT_AUTH_EXEMPT and ENVIRONMENT_SENSITIVE.search(
            name
        ):
            continue
        scrubbed[name] = value
    return scrubbed


SECRET_TEXT = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{16,})"
    r"|(?:eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})"
    r"|(?:\b[A-Fa-f0-9]{40,}\b)"
    # Long opaque base64/base64url runs: the shape a leaked key or an encoded
    # credential takes once it has been through `base64`.
    r"|(?:\b[A-Za-z0-9+/]{48,}={0,2}\b)"
    r"|(?:\b[A-Za-z0-9_-]{48,}\b)"
    r"|(?:(?i:(?:secret|token|password|api[_-]?key)\s*[:=]\s*)\S+)"
)


def redact_text(text: str) -> str:
    """Remove obvious credential shapes from model-visible failure excerpts."""
    return SECRET_TEXT.sub("[REDACTED]", text)


def bounded_excerpt(raw: bytes, cap: int = VALIDATION_OUTPUT_CAP_BYTES) -> str:
    """Return a bounded, redacted tail of command output for repair feedback.

    The cap is applied twice: once to the raw tail and once to the redacted
    text, so redaction can never expand the excerpt past the model-visible
    ceiling.
    """
    tail = raw[-cap:] if len(raw) > cap else raw
    text = tail.decode("utf-8", errors="replace").strip()
    redacted = redact_text(text)
    if len(redacted.encode("utf-8")) > cap:
        redacted = redacted.encode("utf-8")[-cap:].decode("utf-8", errors="replace")
    return redacted


def is_mcp_tool(tool_name: str) -> bool:
    """Detect namespaced MCP tool names such as `server__tool` or `mcp_x`."""
    return bool(MCP_TOOL_PATTERN.search(tool_name.strip().lower()))


def path_is_within(path: Path, parent: Path) -> bool:
    return path == parent or path.is_relative_to(parent)


def resolve_path(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return (path if path.is_absolute() else root / path).resolve()


def normalize_relative(raw_path: str) -> str:
    """Normalize a repository-relative path without stripping leading dots.

    `str.lstrip("./")` removes *characters*, which silently turns
    `.github/hooks` into `github/hooks`.
    """
    normalized = Path(raw_path).as_posix()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/")


def path_matches_owned(path: str, owned_paths: Sequence[str]) -> bool:
    normalized = normalize_relative(path)
    for owned_path in owned_paths:
        owned = normalize_relative(str(owned_path))
        if not owned:
            continue
        if normalized == owned or normalized.startswith(f"{owned}/"):
            return True
    return False


def _entry_digest(digest: "hashlib._Hash", root: Path, path: Path) -> None:
    relative = path.relative_to(root).as_posix()
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode):
        target = os.readlink(path)
        digest.update(
            f"{relative}\0symlink\0{len(target)}\0".encode("utf-8")
        )
        digest.update(target.encode("utf-8", errors="surrogateescape"))
        return
    mode = "755" if info.st_mode & stat.S_IXUSR else "644"
    digest.update(f"{relative}\0{mode}\0{info.st_size}\0".encode("utf-8"))
    digest.update(hashlib.sha256(path.read_bytes()).digest())


def _walk(root: Path, target: Path) -> list[Path]:
    if not target.exists() and not target.is_symlink():
        return []
    if target.is_symlink() or target.is_file():
        return [target]
    entries: list[Path] = []
    for child in sorted(target.iterdir(), key=lambda item: item.name):
        if child.name in DIGEST_EXCLUDED_NAMES:
            continue
        entries.extend(_walk(root, child))
    return entries


def tree_digest(root: Path, owned_paths: Sequence[str]) -> str:
    """Digest the actual content of owned trees.

    Path, mode bit, size, and file bytes are hashed; a symlink contributes its
    target string and is never followed. This is independent of the git index,
    so `git add`, `git stash`, and `git restore` cannot hide a change.
    """
    root = root.resolve()
    digest = hashlib.sha256(b"ohfleet-tree-v2\0")
    seen: set[str] = set()
    for owned_path in sorted(str(path) for path in owned_paths):
        target = resolve_path(root, owned_path)
        if not path_is_within(target, root):
            raise PolicyError(f"owned path escapes the repository: {owned_path}")
        for entry in _walk(root, target):
            relative = entry.relative_to(root).as_posix()
            if relative in seen:
                continue
            seen.add(relative)
            _entry_digest(digest, root, entry)
    return digest.hexdigest()


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
        env={**scrub_environment(), "GIT_OPTIONAL_LOCKS": "0"},
    )


def repository_binding(root: Path) -> dict[str, str]:
    """Bind to HEAD, the index, and the stash so staging cannot hide work."""
    head = _git(root, "rev-parse", "HEAD")
    if head.returncode != 0 or not re.fullmatch(
        r"[a-f0-9]{40}", head.stdout.strip()
    ):
        raise PolicyError("cannot resolve repository HEAD")
    index = root / ".git" / "index"
    index_digest = (
        hashlib.sha256(index.read_bytes()).hexdigest()
        if index.is_file()
        else "absent"
    )
    stash = _git(root, "rev-parse", "--verify", "--quiet", "refs/stash")
    return {
        "head": head.stdout.strip(),
        "index_sha256": index_digest,
        "stash_ref": stash.stdout.strip() or "none",
    }


def binding_drift(baseline: Mapping[str, Any], current: Mapping[str, Any]) -> str:
    for field, label in (
        ("head", "repository HEAD changed"),
        ("index_sha256", "the git index changed (staged work is not reviewable)"),
        ("stash_ref", "the git stash changed (stashed work is not reviewable)"),
    ):
        if str(baseline.get(field, "")) != str(current.get(field, "")):
            return label
    return ""


def denied_write_targets(
    repository_root: Path, control_directory: Path
) -> list[Path]:
    root = repository_root.resolve()
    denied = [control_directory.resolve()]
    denied.extend(root / subtree for subtree in DENIED_REPOSITORY_SUBTREES)
    return denied


def _reject_argument(argument: str, index: int) -> None:
    for character in argument:
        if character in DANGEROUS_ARGUMENT_CHARACTERS:
            raise PolicyError(
                f"argument {index} contains a shell metacharacter"
            )
    if argument in INLINE_CODE_FLAGS:
        raise PolicyError(f"argument {index} is an inline-code flag")
    if ".." in Path(argument).parts:
        raise PolicyError(f"argument {index} traverses out of the repository")


def validate_vector(vector: Any, repository_root: Path | None = None) -> None:
    """Validate a trusted validation argv vector, or raise `PolicyError`.

    Trusted vectors execute in the hook and runner, never through a shell, so
    the policy rejects everything that could reintroduce shell semantics:
    metacharacters, inline-code flags, wrapper executables, interpreter
    invocations without a repository script, and absolute paths outside the
    repository.
    """
    if not isinstance(vector, list) or not vector:
        raise PolicyError("validation command must be a non-empty argv list")
    if not all(isinstance(item, str) and item for item in vector):
        raise PolicyError("validation command must contain non-empty strings")
    executable = vector[0]
    arguments = vector[1:]
    for index, argument in enumerate(vector):
        _reject_argument(argument, index)
    parse_only_bash = (
        tuple(vector[:2]) == BASH_PARSE_ONLY and len(vector) == 3
    )
    if executable in DANGEROUS_EXECUTABLES and not parse_only_bash:
        raise PolicyError(f"`{executable}` may not start a validation vector")
    if Path(executable).is_absolute():
        raise PolicyError("validation executable must be repository-relative")
    if executable in PYTHON_EXECUTABLES:
        if not arguments:
            raise PolicyError("python validation vector needs a target")
        if arguments[0] == "-m":
            if len(arguments) < 2 or arguments[1] not in PYTHON_MODULE_ALLOWLIST:
                raise PolicyError(
                    "python -m module is outside the validation allowlist"
                )
        elif not arguments[0].endswith(".py"):
            raise PolicyError(
                "python validation vector must run a repository .py script"
            )
        elif Path(arguments[0]).is_absolute():
            raise PolicyError("python validation script must be repository-relative")
    if repository_root is not None:
        root = repository_root.resolve()
        for index, argument in enumerate(vector):
            if not argument.startswith("/"):
                continue
            if not path_is_within(Path(argument).resolve(), root):
                raise PolicyError(
                    f"argument {index} references a path outside the repository"
                )
    joined = shlex.join(vector)
    for stem, verb in HIGH_IMPACT_OPERATIONS:
        if vector[0] == stem and verb in arguments:
            raise PolicyError(f"`{stem} {verb}` is a high-impact operation")
    if FORBIDDEN_COMMAND.search(joined):
        raise PolicyError("validation vector matches the high-impact tripwire")


def paths_intersect(left: str, right: str) -> bool:
    """True when two repository-relative paths overlap in either direction.

    Ownership questions are symmetric: a vector naming `backstage/tests` reaches
    an owned file *inside* it, and a vector naming `backstage/tests/test_x.py`
    is reached *by* ownership of the directory. Checking only one direction is
    what let directory-shaped vectors escape the self-validating rule (N1).
    """
    first = normalize_relative(left)
    second = normalize_relative(right)
    if not first or not second:
        return False
    if first == "." or second == ".":
        return True
    return (
        first == second
        or first.startswith(f"{second}/")
        or second.startswith(f"{first}/")
    )


# Modules whose invocation collects and executes repository code rather than a
# single named script. When such a vector carries no explicit path argument the
# collection root is the whole repository.
COLLECTING_MODULES = frozenset({"pytest", "unittest"})


def vector_collection_paths(vector: Sequence[str]) -> list[str]:
    """Return every repository path a vector can execute or import.

    Covers the executable itself, positional path arguments, and the implicit
    whole-repository collection root of a bare `pytest`/`unittest` invocation.
    """
    if not vector:
        return []
    paths: list[str] = []
    executable = vector[0]
    arguments = list(vector[1:])
    if executable not in PYTHON_EXECUTABLES:
        paths.append(executable)
    module = ""
    if arguments and arguments[0] == "-m" and len(arguments) > 1:
        module = arguments[1]
        arguments = arguments[2:]
    positional = [
        argument
        for argument in arguments
        if not argument.startswith("-")
    ]
    paths.extend(positional)
    if module in COLLECTING_MODULES and not positional:
        # `pytest` with no target collects from the rootdir downwards.
        paths.append(".")
    normalized = []
    for candidate in paths:
        value = normalize_relative(candidate)
        if value:
            normalized.append(value)
    return normalized


def vector_owned_targets(
    vector: Sequence[str], owned_paths: Sequence[str]
) -> list[str]:
    """Return the collection paths of `vector` that overlap `owned_paths`.

    `owned_paths` must be the **union** across every selected task. A vector
    that executes another task's owned tree is exactly as untrusted as one that
    executes its own (N1, cross-task hole).
    """
    matches: list[str] = []
    for candidate in vector_collection_paths(vector):
        for owned_path in owned_paths:
            if paths_intersect(candidate, str(owned_path)):
                matches.append(candidate)
                break
    return matches


def vector_owned_script(
    vector: Sequence[str], owned_paths: Sequence[str]
) -> str:
    """Return the first collection path of `vector` inside `owned_paths`.

    Retained as the contract's `self_validating` predicate. It is a *labelling*
    helper only: it no longer selects a mitigation, because every vector now
    runs from a disposable base-revision worktree inside a probed sandbox.
    """
    matches = vector_owned_targets(vector, owned_paths)
    return matches[0] if matches else ""


def owned_path_union(tasks: Iterable[Mapping[str, Any]]) -> list[str]:
    """Return every owned path across the selected tasks, de-duplicated."""
    union: set[str] = set()
    for task in tasks:
        for owned_path in task.get("owned_paths", []) or []:
            value = normalize_relative(str(owned_path))
            if value:
                union.add(value)
    return sorted(union)


# ---------------------------------------------------------------------------
# Whole-repository baseline
# ---------------------------------------------------------------------------

# Directory names that are never part of the reviewable repository baseline.
SNAPSHOT_EXCLUDED_NAMES = frozenset(
    DIGEST_EXCLUDED_NAMES
    | {
        ".git",
        ".test-results",
        ".tox",
        ".venv",
        ".yarn",
        "bower_components",
        "dist-newstyle",
        "target",
        "venv",
        "vendor",
    }
)
SNAPSHOT_MAX_ENTRIES = 60000
SNAPSHOT_MAX_FILE_BYTES = 8 * 1024 * 1024


def _snapshot_entry(path: Path) -> str:
    try:
        info = path.lstat()
    except OSError:
        return "absent"
    if stat.S_ISLNK(info.st_mode):
        target = os.readlink(path)
        return "symlink:" + hashlib.sha256(
            target.encode("utf-8", errors="surrogateescape")
        ).hexdigest()
    if info.st_size > SNAPSHOT_MAX_FILE_BYTES:
        return f"size:{info.st_size}"
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "unreadable"


def repository_snapshot(
    root: Path, *, excluded_prefixes: Sequence[str] = ()
) -> dict[str, str]:
    """Digest every tracked and non-ignored untracked file in the repository.

    This is the whole-repository baseline the runner needs to detect a change to
    a path *no task owns* (finding N3). It is bounded: dependency, cache, and
    vendor directories are skipped, oversized blobs contribute their size rather
    than their bytes, and an entry-count ceiling turns an unexpectedly huge tree
    into a fail-closed error instead of an unbounded contract.
    """
    root = root.resolve()
    result = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if result.returncode != 0:
        raise PolicyError("cannot enumerate repository files for the baseline")
    prefixes = [normalize_relative(str(item)) for item in excluded_prefixes]
    entries: dict[str, str] = {}
    for raw in result.stdout.split("\0"):
        if not raw:
            continue
        relative = normalize_relative(raw)
        if not relative:
            continue
        parts = Path(relative).parts
        if any(part in SNAPSHOT_EXCLUDED_NAMES for part in parts):
            continue
        if any(prefix and paths_intersect(relative, prefix) for prefix in prefixes):
            continue
        if len(entries) >= SNAPSHOT_MAX_ENTRIES:
            raise PolicyError(
                "repository baseline exceeds the bounded entry ceiling"
            )
        entries[relative] = _snapshot_entry(root / relative)
    return entries


def snapshot_drift(
    baseline: Mapping[str, str],
    current: Mapping[str, str],
    tolerated: Sequence[str] = (),
) -> list[str]:
    """Return every path whose content differs and is not under `tolerated`."""
    allowed = [normalize_relative(str(item)) for item in tolerated]
    drifted: list[str] = []
    for relative in sorted(set(baseline) | set(current)):
        if baseline.get(relative) == current.get(relative):
            continue
        if any(
            prefix and path_matches_owned(relative, [prefix]) for prefix in allowed
        ):
            continue
        drifted.append(relative)
    return drifted


def high_impact_denials_present(deny_rules: Iterable[str]) -> list[str]:
    """Return high-impact operations missing from the CLI deny layer."""
    rules = {rule.lower() for rule in deny_rules}
    missing: list[str] = []
    for stem, verb in HIGH_IMPACT_OPERATIONS:
        if f"shell({stem} {verb})" in rules or f"shell({stem})" in rules:
            continue
        missing.append(f"{stem} {verb}")
    return missing
