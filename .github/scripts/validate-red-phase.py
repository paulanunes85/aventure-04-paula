#!/usr/bin/env python3
"""Pass only when a targeted pytest RED-phase run has test failures."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path


PYTEST_TEST_FAILURE = 1
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def validate_red_phase(command: Sequence[str]) -> int:
    if not command:
        print("RED validation requires a command", file=sys.stderr)
        return 2

    result = subprocess.run(
        list(command),
        cwd=REPOSITORY_ROOT,
        check=False,
    )
    if result.returncode == PYTEST_TEST_FAILURE:
        print("RED validation passed: targeted tests failed as expected")
        return 0

    print(
        "RED validation failed: expected pytest exit 1, "
        f"received {result.returncode}",
        file=sys.stderr,
    )
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments[:1] == ["--go-suite"]:
        if len(arguments) != 2:
            print("--go-suite requires exactly one suite", file=sys.stderr)
            return 2
        command = [
            sys.executable,
            "scripts/validate-go-tests.py",
            "--suite",
            arguments[1],
        ]
    else:
        command = [sys.executable, "-m", "pytest", "-q", *arguments]
    return validate_red_phase(command)


if __name__ == "__main__":
    raise SystemExit(main())
