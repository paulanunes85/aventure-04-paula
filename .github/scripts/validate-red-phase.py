#!/usr/bin/env python3
"""Pass only when a targeted test run fails the way the RED phase expects.

Stack-agnostic: pass the project's test command after `--`, for example

    python3 -B .github/scripts/validate-red-phase.py \\
        --expect-output 'REQ-001' -- node --test test/eco.test.js

A non-zero exit alone is weak evidence, because syntax errors, missing
modules and crashes also fail. Use --expect-output with a regex that only
the intended failing assertion prints (the REQ-ID or AC-ID in the test
name is a good choice). Exit codes: 0 RED confirmed, 1 not RED, 2 usage.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--expect-exit",
        type=int,
        default=None,
        help="exact exit code of a test failure (default: any non-zero)",
    )
    parser.add_argument(
        "--expect-output",
        default=None,
        help="regex that must appear in stdout/stderr of the failing run",
    )
    parser.add_argument("--cwd", type=Path, default=ROOT)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command[:1] == ["--"]:
        args.command = args.command[1:]
    return args


def validate_red_phase(args: argparse.Namespace) -> int:
    if not args.command:
        print("RED validation requires a test command after --",
              file=sys.stderr)
        return 2
    try:
        result = subprocess.run(
            args.command,
            cwd=args.cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print(f"RED validation: command not found: {args.command[0]}",
              file=sys.stderr)
        return 2
    output = result.stdout + result.stderr
    sys.stdout.write(output)
    code = result.returncode
    if code == 0:
        print("RED validation failed: the tests passed; write a test "
              "that fails for the missing behavior first", file=sys.stderr)
        return 1
    if args.expect_exit is not None and code != args.expect_exit:
        print(f"RED validation failed: expected exit {args.expect_exit}, "
              f"received {code}", file=sys.stderr)
        return 1
    if args.expect_output and not re.search(args.expect_output, output):
        print("RED validation failed: the run failed, but not with the "
              f"expected output /{args.expect_output}/", file=sys.stderr)
        return 1
    print(f"RED validation passed: targeted tests failed (exit {code})")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    return validate_red_phase(
        parse_args(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    raise SystemExit(main())
