#!/usr/bin/env python3
"""Validate repository paths and commands named in Markdown inline code.

Relative Markdown links are covered by validate-sdd.py; this gate covers
path-shaped inline code such as `.github/hooks/config/policy.json` or
`python3 -B .github/scripts/validate-sdd.py`. A token is checked when it
starts with `./`, `../`, a known root prefix or an existing top-level
entry, or when it is a bare root file (README.md, CONSTITUTION.md...).

Not current-state claims, therefore skipped: fenced code, regions between
`<!-- doc-references: off -->` and `<!-- doc-references: on -->`,
unchecked task items, paragraphs marked planned/optional/absent or
written as tutorial steps and examples, documents whose YAML
front matter status is draft/planned/proposed/superseded/archived, the
`.spec/` tree (it declares future surfaces; use --include-specs for an
advisory audit) and the agent customizations, whose templates describe
artifacts a project creates later. Exit codes: 0 clean, 1 findings.
"""

from __future__ import annotations

import argparse
import re
import shlex
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INLINE_CODE = re.compile(r"`([^`\n]+)`")
TASK = re.compile(r"^\s*-\s+\[(?P<state>[ xX])\]\s+")
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^\s*#{1,6}\s+")

DEFAULT_PREFIXES = (
    ".github/", ".spec/", ".vscode/", "docs/", "scripts/", "src/",
    "test/", "tests/",
)
BARE_FILES = {
    "AGENTS.md", "CHANGELOG.md", "CODEMAP.md", "CONSTITUTION.md",
    "CONTRIBUTING.md", "README.md", "SECURITY.md",
}
NON_CURRENT_MARKERS = (
    "[absent]", "[ausente]", "[optional]", "[opcional]", "[planned]",
    "[planejado]", "does not exist", "is absent", "is missing",
    "não existe", "não existem", "ainda não existe", "será criado",
    "quando existir", "create ", "crie ", "example", "exemplo",
    "scenario", "cena ", "step ", "passo ",
)
IGNORE_START = "<!-- doc-references: off -->"
IGNORE_END = "<!-- doc-references: on -->"
NON_CURRENT_STATUSES = {
    "archived", "arquivado", "draft", "rascunho", "planned", "planejado",
    "proposed", "proposto", "superseded", "substituído",
}
EXCLUDED_DIRS = {
    ".cache", ".git", ".mypy_cache", ".pytest_cache", ".tox", ".venv",
    "__pycache__", "build", "coverage", "dist", "node_modules", "vendor",
    "venv",
}
EXCLUDED_PREFIXES = (
    Path(".github/copilot-instructions.md"),
    Path(".github/agents"),
    Path(".github/instructions"),
    Path(".github/prompts"),
    Path(".github/skills"),
    Path(".github/hooks/.logs"),
)
SPEC_DIR = Path(".spec")
SKIP_MARKERS = ("*", "?", "{", "}", "<", ">", "$", "|", "...", "…")


@dataclass(frozen=True)
class Finding:
    source: Path
    line: int
    reference: str
    reason: str


def root_prefixes(root: Path) -> tuple[str, ...]:
    entries = {
        f"{path.name}/" for path in root.iterdir()
        if path.is_dir() and path.name not in EXCLUDED_DIRS
    }
    return tuple(sorted(entries | set(DEFAULT_PREFIXES)))


def is_excluded(path: Path, root: Path, include_specs: bool) -> bool:
    relative = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return True
    if not include_specs and relative.is_relative_to(SPEC_DIR):
        return True
    return any(relative.is_relative_to(p) for p in EXCLUDED_PREFIXES)


def markdown_files(root: Path, paths: list[Path],
                   include_specs: bool) -> list[Path]:
    files: set[Path] = set()
    for path in paths:
        resolved = (path if path.is_absolute() else root / path).resolve()
        if resolved.is_dir():
            candidates = list(resolved.rglob("*.md"))
        else:
            candidates = [resolved] if resolved.is_file() else []
        for candidate in candidates:
            if candidate.suffix.lower() == ".md" and not is_excluded(
                    candidate, root, include_specs):
                files.add(candidate)
    return sorted(files)


def document_is_non_current(text: str) -> bool:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, separator, value = line.partition(":")
        if separator and key.strip().casefold() == "status":
            status = value.strip().strip("\"'").casefold()
            return status in NON_CURRENT_STATUSES
    return False


def normalize_token(token: str) -> str:
    normalized = token.strip().strip("([{").rstrip(".,;:)]}")
    normalized = normalized.split("::", 1)[0]
    normalized = re.sub(r":\d+(?:-\d+)?$", "", normalized)
    return normalized.split("#", 1)[0]


def candidate_tokens(code_span: str) -> list[str]:
    try:
        tokens = shlex.split(code_span)
    except ValueError:
        tokens = code_span.split()
    found: list[str] = []
    for token in tokens:
        for fragment in token.split(","):
            normalized = normalize_token(fragment)
            if normalized and normalized not in found:
                found.append(normalized)
    return found


def is_path_like(token: str) -> bool:
    return bool(token) and not (
        token.startswith(("http://", "https://", "mailto:", "-"))
        or token in {".", "..", "/"}
        or any(marker in token for marker in SKIP_MARKERS))


def resolve_prefixed(token: str, source: Path, root: Path) -> Path | None:
    local = (source.parent / token).resolve()
    if local.exists():
        return local
    package = re.fullmatch(r"\.spec/(\d{3})/?", token)
    if package:
        matches = list((root / SPEC_DIR).glob(f"{package.group(1)}-*"))
        if len(matches) == 1:
            return matches[0].resolve()
    if token.endswith("/") or Path(token).suffix:
        return (root / token).resolve()
    return None


def resolve_reference(token: str, source: Path, root: Path,
                      prefixes: tuple[str, ...]) -> tuple[Path, bool] | None:
    """Return (target, must_be_executable) or None when not a path."""
    if not is_path_like(token):
        return None
    if token.startswith("./"):
        relative = token[2:]
        if not relative.startswith(prefixes):
            return None
        return (root / relative).resolve(), True
    if token.startswith("../"):
        return (source.parent / token).resolve(), False
    if token.startswith(prefixes):
        target = resolve_prefixed(token, source, root)
        return (target, False) if target else None
    if token in BARE_FILES:
        local = (source.parent / token).resolve()
        return (local if local.exists() else (root / token).resolve(),
                False)
    return None


@dataclass(frozen=True)
class LineReference:
    line: int
    token: str
    target: Path
    requires_executable: bool


def prose_lines(text: str) -> Iterator[tuple[int, str]]:
    """Yield lines outside fenced code and ignore regions."""
    in_fence = ignored = False
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped in (IGNORE_START, IGNORE_END):
            ignored = stripped == IGNORE_START
        elif FENCE.match(line):
            in_fence = not in_fence
        elif not (in_fence or ignored):
            yield number, line


def current_lines(text: str) -> Iterator[tuple[int, str]]:
    """Yield lines that state current facts (see module docstring)."""
    pending_task = non_current = False
    for number, line in prose_lines(text):
        if not line.strip():
            non_current = False
            continue
        task = TASK.match(line)
        if task:
            pending_task = task.group("state") == " "
        elif HEADING.match(line):
            pending_task = non_current = False
        folded = line.casefold()
        non_current = non_current or any(
            marker in folded for marker in NON_CURRENT_MARKERS)
        if not (pending_task or non_current):
            yield number, line


def iter_references(source: Path, root: Path, prefixes: tuple[str, ...],
                    text: str) -> Iterator[LineReference]:
    for number, line in current_lines(text):
        tokens = (token for span in INLINE_CODE.findall(line)
                  for token in candidate_tokens(span))
        for token in tokens:
            resolved = resolve_reference(token, source, root, prefixes)
            if resolved is not None:
                yield LineReference(number, token, *resolved)


def validate_file(source: Path, root: Path,
                  prefixes: tuple[str, ...]) -> list[Finding]:
    text = source.read_text(encoding="utf-8")
    if document_is_non_current(text):
        return []
    findings: list[Finding] = []
    for ref in iter_references(source, root, prefixes, text):
        if not ref.target.exists():
            findings.append(
                Finding(source, ref.line, ref.token, "target-not-found"))
        elif (ref.requires_executable and ref.target.is_file()
              and not ref.target.stat().st_mode & 0o111):
            findings.append(
                Finding(source, ref.line, ref.token, "not-executable"))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path,
                        help="Markdown files or directories (default: root)")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--include-specs", action="store_true",
                        help="also audit .spec/ (advisory)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    prefixes = root_prefixes(root)
    files = markdown_files(root, args.paths or [root], args.include_specs)
    findings = [f for source in files
                for f in validate_file(source, root, prefixes)]
    for finding in findings:
        print(f"{finding.source.relative_to(root)}:{finding.line}: "
              f"{finding.reason}: {finding.reference}", file=sys.stderr)
    print(f"Documentation references: files {len(files)} "
          f"errors {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
