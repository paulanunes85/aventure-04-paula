#!/usr/bin/env python3
"""Every test file a TESTING.md names must exist, or be counted.

Usage:
  ./scripts/validate-testing-evidence.py                 # gate against the baseline
  ./scripts/validate-testing-evidence.py --report        # per-package detail
  ./scripts/validate-testing-evidence.py --write-baseline

Exit codes:
  0 PASS   - no package names more missing test files than its baseline allows
  1 FAIL   - a package regressed, or the baseline is stale
  2 ERROR  - the spec tree or baseline could not be read

WHY THIS EXISTS
-------------------------------------------------------------------------------
`.specs/*/TESTING.md` is where a specification names the tests that verify its
requirements. It is the evidence half of the specification: a requirement whose
TESTING.md names `tests/test_x.py` is claiming that file proves it.

Measured 2026-08-30: those files name 339 test files and **232 of them do not
exist**. Sampled, they are not renames -- `CustomSignInPage.tsx` exists with no
test file for it anywhere in the tree, and `conditionalPolicy` exists nowhere at
all. They were never written.

`scripts/validate-specs.py --strict` passed the whole tree throughout, because
it contains no existence check of any kind: `grep -c 'exists()|is_file()'`
returns 0. So 27 packages reported OK while two thirds of the evidence they
named was fiction.

WHY A BASELINE RATHER THAN A HARD FAILURE
-------------------------------------------------------------------------------
Failing on all 232 would make this gate red on every commit, and a gate that is
always red is one everybody learns to scroll past -- the exact failure this
repository has already hit with Checkov, TFSec and the OPA policy tests.

So the count is ratcheted instead. The baseline records what each package is
currently missing; naming a new test file that does not exist fails the build,
and writing one of the missing tests makes the gate ask for the baseline to be
tightened. The number can only go down.

The baseline is a record of debt, not permission. `--report` prints exactly
which files are missing, per package.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
BASELINE = REPO_ROOT / ".specs" / "testing-evidence-baseline.json"

#: A path that looks like a test file under one of the trees this repository
#: actually holds code in. Deliberately anchored to those roots: TESTING.md
#: prose also mentions test *names* and upstream paths, and treating those as
#: promises would manufacture findings nobody can act on.
TEST_PATH = re.compile(
    r"`?((?:tests|backstage|mcp-servers|scripts)[\w./-]*?test[\w./-]*"
    r"\.(?:py|tsx|ts|go|sh))`?"
)

#: A path stated immediately after a backticked `owner/repo` belongs to that
#: repository, not this one. Two packages carry real evidence in
#: `Ohorizons/open-horizons-templates`; resolving those names against this
#: checkout reported them missing and made the gate demand a file that cannot
#: exist here. The qualifier must be adjacent, so a repository named elsewhere
#: in the same row still leaves a local claim falsifiable.
FOREIGN_REPOSITORY = re.compile(r"`[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+`\s*`?$")

#: A path stated inside `cd <dir> && ...`, or followed by the directory the
#: command ran in, is relative to that directory. Evidence rows are written
#: both ways, so a bare path only resolves once a stated root is applied.
WORKING_DIRECTORY = re.compile(r"\bcd\s+([A-Za-z0-9_./-]+?)/*\s*&&")

#: A backticked token that looks like a directory rather than a file. Any such
#: token on the row is tried as a root; one that names nothing on disk simply
#: fails to resolve, so this cannot turn a missing file into a passing claim.
STATED_DIRECTORY = re.compile(r"`([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+)`")


def named_tests(testing_md: pathlib.Path) -> set[str]:
    """Repository-relative test paths a TESTING.md claims as evidence.

    Paths owned by another repository are excluded rather than reported
    missing: this gate can only hold a claim about a file this checkout is
    able to contain. A path stated relative to a directory named on the same
    row resolves against it; a path that resolves against no stated root is
    returned unchanged, so it still fails the existence check.
    """

    claimed: set[str] = set()
    for line in testing_md.read_text(encoding="utf-8").splitlines():
        matches = list(TEST_PATH.finditer(line))
        if not matches:
            continue
        roots = ["", *WORKING_DIRECTORY.findall(line)]
        roots.extend(
            token.rstrip("/")
            for token in STATED_DIRECTORY.findall(line)
            if not pathlib.PurePosixPath(token).suffix
        )
        for match in matches:
            if FOREIGN_REPOSITORY.search(line[: match.start(1)]):
                continue
            path = match.group(1)
            resolved = next(
                (
                    f"{root}/{path}" if root else path
                    for root in roots
                    if (REPO_ROOT / root / path).exists()
                ),
                path,
            )
            claimed.add(resolved)
    return claimed


def measure(spec_root: pathlib.Path) -> dict[str, set[str]]:
    """Missing test files per specification package."""

    missing: dict[str, set[str]] = {}
    for testing_md in sorted(spec_root.glob("*/TESTING.md")):
        absent = {
            path
            for path in named_tests(testing_md)
            if not (REPO_ROOT / path).exists()
        }
        if absent:
            missing[testing_md.parent.name] = absent
    return missing


def load_baseline() -> dict[str, int]:
    if not BASELINE.exists():
        return {}
    try:
        data = json.loads(BASELINE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"{BASELINE} is not valid JSON: {error}", file=sys.stderr)
        raise SystemExit(2) from error
    return {str(k): int(v) for k, v in data.get("missing_by_package", {}).items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-root", default=".specs", type=pathlib.Path)
    parser.add_argument("--report", action="store_true", help="list every missing file")
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="record the current counts as the new ceiling",
    )
    args = parser.parse_args()

    spec_root = REPO_ROOT / args.spec_root
    if not spec_root.is_dir():
        print(f"not a directory: {spec_root}", file=sys.stderr)
        return 2

    packages = sorted(spec_root.glob("*/TESTING.md"))
    if not packages:
        print(
            f"FAIL: {spec_root} holds no TESTING.md. A run that measured nothing "
            f"is not a run that found nothing.",
            file=sys.stderr,
        )
        return 1

    missing = measure(spec_root)
    total = sum(len(v) for v in missing.values())

    if args.write_baseline:
        BASELINE.write_text(
            json.dumps(
                {
                    "_comment": (
                        "Test files named in .specs/*/TESTING.md that do not exist. "
                        "This is a record of debt, not permission: the numbers may "
                        "only go down. scripts/validate-testing-evidence.py enforces "
                        "it. Regenerate with --write-baseline only after writing "
                        "tests, never to admit new ones."
                    ),
                    "missing_by_package": {
                        name: len(paths) for name, paths in sorted(missing.items())
                    },
                    "total": total,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"baseline written: {len(missing)} package(s), {total} missing file(s)")
        return 0

    if args.report:
        for name, paths in sorted(missing.items()):
            print(f"{name}  ({len(paths)} missing)")
            for path in sorted(paths):
                print(f"    {path}")
        print()

    baseline = load_baseline()
    regressed: list[str] = []
    improved: list[str] = []

    for name in sorted(set(missing) | set(baseline)):
        actual = len(missing.get(name, ()))
        allowed = baseline.get(name, 0)
        if actual > allowed:
            regressed.append(
                f"{name}: names {actual} missing test file(s), baseline allows "
                f"{allowed}"
            )
        elif actual < allowed:
            improved.append(f"{name}: {allowed} -> {actual}")

    print(
        f"Testing evidence gate: {len(packages)} package(s), "
        f"{total} named test file(s) missing, baseline {sum(baseline.values())}"
    )

    if regressed:
        print("\nFAIL: a specification names test evidence that does not exist:", file=sys.stderr)
        for line in regressed:
            print(f"  - {line}", file=sys.stderr)
        print(
            "\nEither write the test, or stop naming it. TESTING.md is where a "
            "requirement claims it is verified; naming a file that was never "
            "written makes the claim unfalsifiable.",
            file=sys.stderr,
        )
        return 1

    if improved:
        print("\nFAIL: the baseline is stale -- tests were written:", file=sys.stderr)
        for line in improved:
            print(f"  - {line}", file=sys.stderr)
        print(
            "\nRun --write-baseline to lock in the improvement. The ratchet only "
            "holds if it tightens.",
            file=sys.stderr,
        )
        return 1

    print("PASS: no specification names more missing evidence than its baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
