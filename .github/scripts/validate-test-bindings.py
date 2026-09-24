#!/usr/bin/env python3
"""A checkpoint's bound file must contain the test its TESTING.md row names.

Usage:
  ./scripts/validate-test-bindings.py            # gate
  ./scripts/validate-test-bindings.py --report   # list every resolved binding

Exit codes:
  0 PASS  - every resolvable binding names a file that defines its selector
  1 FAIL  - at least one binding points at a file that does not define it
  2 ERROR - the spec tree could not be read

WHY THIS EXISTS
-------------------------------------------------------------------------------
`checkpoints/test-coverage.yaml` binds a TST id to the file that proves it, and
a task's closure rests on that binding. Nothing checked that the file actually
contained the test.

Measured 2026-09-20, before this gate existed: 40 rows across four packages
bound a TST id to a file that defines none of the tests its TESTING.md row
names. 031 had 16 -- a documented three-way phase split was recorded in
TASKS.md prose and never propagated to the checkpoint, so fourteen rows still
named the pre-split file. 029 had 19 pointing at a contract suite whose tests
had moved to `_infrastructure` and `_catalog` siblings. 027 bound five live
estate rows to the spec-manifest validator's suite. 034 had TST-R019 and
TST-R021 bound to each other's files.

None of this was visible to the nine gates or to the 6,809-test suite:
`validate-testing-evidence.py` checks that a named file *exists*, which every
one of these did, and no gate had ever compared a binding to its contents.

WHAT IT DOES NOT CHECK
-------------------------------------------------------------------------------
Only rows whose TESTING.md entry names a selector this script can resolve --
`..::test_name`, a backticked `test_name`, or a JS `it(...)`/`test(...)` title
that some file declares. A row naming no resolvable selector is skipped rather
than guessed at, and the report says how many were skipped. A binding that
names extra files beyond the one defining the selector is not an error; the
check is that the bound `file:` is among the files that define it.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SPEC_ROOT = REPO_ROOT / ".specs"
SKIPPED_DIRECTORIES = {"node_modules", "__pycache__", ".git", ".open-horizons"}

PY_TEST = re.compile(r"^\s*def (test_\w+)", re.MULTILINE)
JS_TEST = re.compile(r"^\s*(?:it|test)\(\s*['\"](.+?)['\"]", re.MULTILINE)
TESTING_ROW = re.compile(r"^\| (TST-[A-Z]*\d{3}) \|(.*)$", re.MULTILINE)
SELECTOR = re.compile(r"\.\.::(\w+)")
BACKTICKED = re.compile(r"`(test_\w+)`")


def declaring_files(root: pathlib.Path) -> dict[str, set[str]]:
    """Map every test name declared anywhere in the tree to the files declaring it."""
    index: dict[str, set[str]] = {}
    patterns = ("tests/**/*.py", "backstage/**/test_*.py",
                "backstage/**/*.test.ts", "backstage/**/*.test.tsx")
    for pattern in patterns:
        for path in root.glob(pattern):
            if SKIPPED_DIRECTORIES & set(path.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            relative = str(path.relative_to(root))
            for matcher in (PY_TEST, JS_TEST):
                for match in matcher.finditer(text):
                    index.setdefault(match.group(1), set()).add(relative)
    return index


def bound_file(checkpoint_text: str, test_id: str) -> str | None:
    block = re.search(
        rf"^  {re.escape(test_id)}:\n(?:(?:    .*|)\n)*", checkpoint_text, re.MULTILINE
    )
    if not block:
        return None
    declared = re.search(r"^    file: (.*)$", block.group(0), re.MULTILINE)
    return declared.group(1).strip() if declared else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-root", type=pathlib.Path, default=DEFAULT_SPEC_ROOT)
    parser.add_argument("--report", action="store_true")
    arguments = parser.parse_args()

    if not arguments.spec_root.is_dir():
        print(f"ERROR: no spec root at {arguments.spec_root}", file=sys.stderr)
        return 2

    index = declaring_files(REPO_ROOT)
    findings: list[str] = []
    checked = skipped = 0

    for checkpoint in sorted(arguments.spec_root.glob("*/checkpoints/test-coverage.yaml")):
        testing_md = checkpoint.parent.parent / "TESTING.md"
        if not testing_md.exists():
            continue
        package = checkpoint.parent.parent.name
        checkpoint_text = checkpoint.read_text(encoding="utf-8")
        for test_id, row in TESTING_ROW.findall(testing_md.read_text(encoding="utf-8")):
            names = set(SELECTOR.findall(row)) | set(BACKTICKED.findall(row))
            declaring: set[str] = set()
            for name in names:
                declaring |= index.get(name, set())
            if not declaring:
                skipped += 1
                continue
            declared = bound_file(checkpoint_text, test_id)
            if declared is None:
                skipped += 1
                continue
            checked += 1
            if declared not in declaring:
                findings.append(
                    f"{package}/{test_id}: bound to {declared}, which declares none of "
                    f"its named tests; they are in {', '.join(sorted(declaring))}"
                )
            elif arguments.report:
                print(f"OK   {package}/{test_id} -> {declared}")

    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    print(
        f"Test bindings: {checked} resolved, {len(findings)} misbound, "
        f"{skipped} unresolvable and skipped"
    )
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
