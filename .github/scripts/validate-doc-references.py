#!/usr/bin/env python3
"""Validate repository paths and commands named in Markdown inline code.

`validate-docs.sh` owns Markdown link resolution. This companion gate covers
path-shaped inline-code references in operational documentation, such as
`.github/mcp.json`, and commands such as
`python3 scripts/validate-spec-artifacts.py`. The `.specs/` tree is excluded by
default because it declares future implementation surfaces and has dedicated
SDD gates; pass `--include-specs` for a non-gating audit. Unchecked task blocks
and references explicitly described as planned, optional, or absent are not
current-state claims and are also excluded.
"""

from __future__ import annotations

import argparse
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path

INLINE_CODE_PATTERN = re.compile(r"`([^`\n]+)`")
TASK_PATTERN = re.compile(r"^\s*-\s+\[(?P<state>[ xX])\]\s+")
FENCE_PATTERN = re.compile(r"^\s*(```|~~~)")
HEADING_PATTERN = re.compile(r"^\s*#{1,6}\s+")

ROOT_PATH_PREFIXES = (
    ".claude/",
    ".github/",
    ".specs/",
    ".vscode/",
    "argocd/",
    "backstage/",
    "deploy/",
    "docker/",
    "docs/",
    "grafana/",
    "mcp-servers/",
    "policies/",
    "prometheus/",
    "registry/",
    "scripts/",
    "stack-profiles/",
    "terraform/",
    "tests/",
)

BARE_REFERENCE_FILES = {
    "AGENTS.md",
    "ANALYSIS.md",
    "CODEMAP.md",
    "CONSTITUTION.md",
    "DECISIONS.md",
    "DESIGN.md",
    "README.md",
    "SPECIFICATION.md",
    "TASKS.md",
    "TESTING.md",
    "VERIFICATION.md",
}

NON_CURRENT_MARKERS = (
    "[absent]",
    "[ausente]",
    "[optional]",
    "[opcional]",
    "[planned]",
    "[planejado]",
    "does not exist",
    "do not exist",
    "is not present",
    "is absent",
    "is missing",
    "are absent",
    "missing path",
    "no tracked",
    "not recognized",
    "não existe",
    "não existem",
)

EXCLUDED_DIRECTORY_NAMES = {
    ".cache",
    ".git",
    # Sealed run receipts, not repository documentation. They are gitignored,
    # so a clone has none and only a machine that has executed the fleet sees
    # them; scanning them made this gate's verdict depend on local history,
    # and policy forbids writing there to correct whatever it reported.
    ".test-results",
    ".terraform",
    ".tox",
    ".venv",
    "node_modules",
    "vendor",
    "venv",
}

EXCLUDED_PREFIXES = (
    Path(".claude"),
    Path(".github/agents"),
    Path(".github/instructions"),
    Path(".github/prompts"),
    Path(".github/skills"),
    Path(".open-horizons/catalog"),
    Path("docs/aeg-feature-scaffold"),
    Path("docs/foundry-templates-references"),
    Path("docs/md"),
    Path("docs/microsoft-agent-framwork-example"),
)

TRAILING_PUNCTUATION = ".,;:)]}"
LEADING_PUNCTUATION = "([{"
NON_CURRENT_DOCUMENT_STATUSES = {
    "archived",
    "draft",
    "planned",
    "proposed",
    "superseded",
}


@dataclass(frozen=True)
class Finding:
    source: Path
    line: int
    reference: str
    reason: str


def is_excluded(path: Path, root: Path, include_specs: bool) -> bool:
    relative = path.relative_to(root)
    if any(part in EXCLUDED_DIRECTORY_NAMES for part in relative.parts):
        return True
    if not include_specs and relative.is_relative_to(Path(".specs")):
        return True
    return any(relative.is_relative_to(prefix) for prefix in EXCLUDED_PREFIXES)


def markdown_files(
    root: Path, paths: list[Path], include_specs: bool
) -> list[Path]:
    files: set[Path] = set()
    for path in paths:
        resolved = path if path.is_absolute() else root / path
        if resolved.is_file():
            if resolved.suffix.lower() == ".md" and not is_excluded(
                resolved, root, include_specs
            ):
                files.add(resolved)
            continue
        if not resolved.is_dir():
            continue
        for candidate in resolved.rglob("*.md"):
            if not is_excluded(candidate, root, include_specs):
                files.add(candidate)
    return sorted(files)


def document_is_non_current(source: Path) -> bool:
    lines = source.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, separator, value = line.partition(":")
        if separator and key.strip().casefold() == "status":
            status = value.strip().strip("\"'").casefold()
            return status in NON_CURRENT_DOCUMENT_STATUSES
    return False


def normalize_token(token: str) -> str:
    normalized = token.strip().strip(LEADING_PUNCTUATION)
    normalized = normalized.rstrip(TRAILING_PUNCTUATION)
    normalized = normalized.split("::", 1)[0]
    normalized = re.sub(r":\d+(?:-\d+)?$", "", normalized)
    if "#" in normalized:
        normalized = normalized.split("#", 1)[0]
    return normalized


def candidate_tokens(code_span: str) -> list[str]:
    try:
        tokens = shlex.split(code_span)
    except ValueError:
        tokens = code_span.split()

    candidates: list[str] = []
    for token in tokens:
        for fragment in token.split(","):
            normalized = normalize_token(fragment)
            if normalized and normalized not in candidates:
                candidates.append(normalized)
    return candidates


def resolve_reference(token: str, source: Path, root: Path) -> tuple[Path, bool] | None:
    if not token or token.startswith(("http://", "https://", "mailto:", "#")):
        return None
    if any(
        marker in token
        for marker in ("*", "?", "{", "}", "<", ">", "$", "|", "...", "…")
    ):
        return None
    if token.startswith("-") or token in {".", "..", "/"}:
        return None

    requires_executable = token.startswith("./")
    if token.startswith("./"):
        root_relative = token[2:]
        if not root_relative.startswith(ROOT_PATH_PREFIXES):
            return None
        return (root / root_relative).resolve(), requires_executable

    if token.startswith("../"):
        return (source.parent / token).resolve(), requires_executable

    if token.startswith(ROOT_PATH_PREFIXES):
        local_candidate = (source.parent / token).resolve()
        if local_candidate.exists():
            return local_candidate, requires_executable
        root_candidate = (root / token).resolve()
        if root_candidate.exists():
            return root_candidate, requires_executable
        if re.fullmatch(r"\.specs/\d{3}", token):
            matches = list(root.glob(f"{token}-*"))
            if len(matches) == 1:
                return matches[0].resolve(), requires_executable
        if token.startswith(".") or token.endswith("/") or Path(token).suffix:
            return root_candidate, requires_executable
        return None

    if token in BARE_REFERENCE_FILES:
        local_candidate = (source.parent / token).resolve()
        if local_candidate.exists():
            return local_candidate, requires_executable
        if token == "CONSTITUTION.md":
            specification_constitution = root / ".specs" / token
            if specification_constitution.exists():
                return specification_constitution.resolve(), requires_executable
        root_candidate = (root / token).resolve()
        if root_candidate.exists():
            return root_candidate, requires_executable
        return None

    return None


def line_is_non_current(
    line: str, pending_task: bool, paragraph_non_current: bool
) -> bool:
    if pending_task or paragraph_non_current:
        return True
    lowered = line.casefold()
    return any(marker in lowered for marker in NON_CURRENT_MARKERS)


@dataclass(frozen=True)
class LineReference:
    line: int
    token: str
    target: Path
    requires_executable: bool


def iter_line_references(source: Path, root: Path):
    """Yield every resolvable command/path token named in ``source``.

    Shared by ``validate_file`` (which additionally checks each resolved
    target against disk) and ``extract_references`` (which only needs the
    set of named tokens). Applies the same fence, task, and non-current
    marker filtering so both callers see an identical reference surface.
    """
    in_fence = False
    pending_task = False
    paragraph_non_current = False

    for line_number, line in enumerate(
        source.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            paragraph_non_current = False
            continue
        if FENCE_PATTERN.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        task_match = TASK_PATTERN.match(line)
        if task_match:
            pending_task = task_match.group("state") == " "
        elif HEADING_PATTERN.match(line):
            pending_task = False
            paragraph_non_current = False

        line_has_non_current_marker = any(
            marker in line.casefold() for marker in NON_CURRENT_MARKERS
        )
        if line_has_non_current_marker:
            paragraph_non_current = True

        if line_is_non_current(line, pending_task, paragraph_non_current):
            continue

        for code_span in INLINE_CODE_PATTERN.findall(line):
            for token in candidate_tokens(code_span):
                resolved = resolve_reference(token, source, root)
                if resolved is None:
                    continue
                target, requires_executable = resolved
                yield LineReference(line_number, token, target, requires_executable)


def extract_references(source: Path, root: Path | None = None) -> set[str]:
    """Return every resolvable command/path token named in ``source``.

    Reuses the fence/non-current-marker/candidate-token scan shared with
    ``validate_file`` via ``iter_line_references``, but reports the named
    tokens themselves rather than unresolved-target findings.
    """
    if document_is_non_current(source):
        return set()
    effective_root = root if root is not None else source.parent
    return {
        reference.token
        for reference in iter_line_references(source, effective_root)
    }


def validate_file(source: Path, root: Path) -> list[Finding]:
    if document_is_non_current(source):
        return []

    findings: list[Finding] = []

    for reference in iter_line_references(source, root):
        target = reference.target
        if not target.exists():
            findings.append(
                Finding(source, reference.line, reference.token, "target-not-found")
            )
        elif reference.requires_executable and target.is_file():
            if target.stat().st_mode & 0o111 == 0:
                findings.append(
                    Finding(source, reference.line, reference.token, "not-executable")
                )

    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate repository paths and commands named in Markdown."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Markdown files or directories to scan; defaults to the repository root.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root used to resolve root-relative references.",
    )
    parser.add_argument(
        "--include-specs",
        action="store_true",
        help="Include `.specs/` in an advisory audit of future path declarations.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    paths = args.paths or [root]
    files = markdown_files(root, paths, args.include_specs)
    findings = [
        finding
        for source in files
        for finding in validate_file(source, root)
    ]

    for finding in findings:
        relative_source = finding.source.relative_to(root)
        print(
            f"{relative_source}:{finding.line}: {finding.reason}: "
            f"{finding.reference}",
            file=sys.stderr,
        )

    print(
        f"Documentation references: files {len(files)} "
        f"errors {len(findings)}"
    )
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
