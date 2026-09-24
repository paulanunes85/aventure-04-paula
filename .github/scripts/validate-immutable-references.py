#!/usr/bin/env python3
"""Enforce immutable cross-repository references.

Specification 013 `FR-TOPO-003` requires that a reference from one repository
into another resolve to an immutable tag or commit. A reference to a mutable
branch such as `main` makes template execution non-reproducible: an unrelated
merge in the referenced repository silently changes what this repository
resolves, and a rollback here cannot restore the previous behaviour.

The gate inspects Backstage catalog locations and Terraform module sources. A
reference that stays inside this repository is exempt, because it is versioned
by the same commit that declares it; a reference that crosses a repository
boundary is not.

Usage:
    validate-immutable-references.py [PATH ...]

Exit code 0 means every cross-repository reference is immutable.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF_REPOSITORY = "Ohorizons/ohorizons-demo"

EXCLUDED_PARTS = {
    ".git",
    ".terraform",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "__pycache__",
    ".test-results",
}

# A GitHub blob or tree URL carrying the ref it resolves.
GITHUB_REF_URL = re.compile(
    r"https://github\.com/(?P<repo>[\w.-]+/[\w.-]+)/(?:blob|tree|raw)/(?P<ref>[^/\s\"']+)"
)

# A Terraform module sourced from Git, optionally pinned with ?ref=.
TERRAFORM_GIT_SOURCE = re.compile(
    r'source\s*=\s*"(?:git::)?(?P<url>[^"]*github\.com[^"]*)"'
)

# A 40- or 7-plus-character hexadecimal commit, or a version-like tag.
COMMIT_REF = re.compile(r"^[0-9a-f]{7,40}$")
TAG_REF = re.compile(r"^v?\d+\.\d+")

MUTABLE_REFS = {"main", "master", "develop", "HEAD", "trunk"}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    repository: str
    ref: str

    def render(self, root: Path) -> str:
        try:
            location = self.path.relative_to(root)
        except ValueError:
            location = self.path
        return (
            f"{location}:{self.line}: mutable-cross-repository-reference: "
            f"{self.repository} is referenced at {self.ref!r}. Use an immutable "
            "tag or commit so the resolved content cannot change without a "
            "recorded upgrade."
        )


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def is_immutable(ref: str) -> bool:
    if ref in MUTABLE_REFS:
        return False
    return bool(COMMIT_REF.fullmatch(ref) or TAG_REF.match(ref))


def scan_line(path: Path, number: int, line: str) -> list[Finding]:
    findings: list[Finding] = []

    for match in GITHUB_REF_URL.finditer(line):
        repository = match.group("repo")
        ref = match.group("ref")
        if repository == SELF_REPOSITORY:
            continue
        if not is_immutable(ref):
            findings.append(Finding(path, number, repository, ref))

    for match in TERRAFORM_GIT_SOURCE.finditer(line):
        url = match.group("url")
        if SELF_REPOSITORY in url:
            continue
        if "?ref=" not in url:
            findings.append(Finding(path, number, url, "<unpinned>"))
            continue
        ref = url.split("?ref=", 1)[1].split("&", 1)[0]
        if not is_immutable(ref):
            findings.append(Finding(path, number, url, ref))

    return findings


def scan(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    suffixes = {".yaml", ".yml", ".tf"}
    for target in paths:
        candidates = [target] if target.is_file() else list(target.rglob("*"))
        for path in candidates:
            if not path.is_file() or is_excluded(path) or path.suffix not in suffixes:
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            for number, line in enumerate(lines, 1):
                findings.extend(scan_line(path, number, line))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)

    targets = args.paths or [ROOT / "backstage", ROOT / "terraform"]
    resolved = [p if p.is_absolute() else ROOT / p for p in targets]
    existing = [p for p in resolved if p.exists()]
    if not existing:
        print("No inspectable path was provided", file=sys.stderr)
        return 1

    findings = scan(existing)
    for finding in findings:
        print(finding.render(ROOT), file=sys.stderr)

    print(f"Summary: mutable cross-repository references {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
