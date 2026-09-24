#!/usr/bin/env python3
"""Validate the RED/GREEN task dependency graph of an SDD package.

Specification `005-aeg-open-horizons-azure-dev-pilot` orders its work as a
dependency-ordered RED/GREEN/REFACTOR sequence. That ordering is only a real
control if something checks it: a task that depends on a task that does not
exist, a cycle, or a GREEN implementation task that does not follow its RED
test task are all defects a reader will not reliably catch.

The gate parses `TASKS.md` and enforces:

* every task declares a mode, a dependency line, and at least one traced
  requirement,
* every declared dependency names a task that exists,
* the dependency graph is acyclic,
* every dependency is declared before its dependant, so the file can be
  executed top to bottom, and
* every GREEN task depends, directly or transitively, on a RED task, so an
  implementation can never be written before a failing test.

Usage:
    validate-task-graph.py [--spec DIR] [--json]

Exit code 0 means the task graph is internally consistent.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / ".specs" / "005-aeg-open-horizons-azure-dev-pilot"

# A task heading, optionally carrying the `[P]` parallel-execution marker.
# Packages use either a bare sequence (`T001`) or a package-scoped one
# (`T011-001`); both are stable identifiers and both are accepted.
TASK_HEADING = re.compile(
    r"^###\s+(?P<id>T-?[A-Z0-9]+(?:-[A-Z0-9]+)*)(?P<parallel>\s+\[P\])?:"
    r"\s*(?P<title>.+?)\s*$",
    re.MULTILINE,
)

# Any line that looks like a task heading, used to detect a package whose
# headings exist but do not parse. Discovering packages with the strict pattern
# alone would drop such a package from the report without a word, which is the
# same silent-subset defect at file granularity.
TASK_HEADING_HINT = re.compile(r"^###\s+T[-A-Z0-9]", re.MULTILINE)
FIELD = re.compile(r"^-\s+\*\*(?P<key>[^*]+):\*\*\s*(?P<value>.*)$")
TASK_REF = re.compile(r"\bT-?[A-Z0-9]+(?:-[A-Z0-9]+)*\b")

# Implementation modes that must be preceded by a failing test.
GREEN_MODES = {"GREEN", "REFACTOR"}
RED_MODES = {"RED"}


@dataclass
class Task:
    identifier: str
    title: str
    order: int
    parallel: bool = False
    mode: str = ""
    depends_on: list[str] = field(default_factory=list)
    conditional_on: list[str] = field(default_factory=list)
    traces: list[str] = field(default_factory=list)
    has_dependency_field: bool = False


def parse_tasks(text: str) -> list[Task]:
    """Return every task block in document order."""
    tasks: list[Task] = []
    matches = list(TASK_HEADING.finditer(text))
    for order, match in enumerate(matches):
        start = match.end()
        end = matches[order + 1].start() if order + 1 < len(matches) else len(text)
        task = Task(
            identifier=match.group("id"),
            title=match.group("title"),
            order=order,
            parallel=bool(match.group("parallel")),
        )
        for line in text[start:end].split("\n"):
            field_match = FIELD.match(line.strip())
            if not field_match:
                continue
            key = field_match.group("key").strip().lower()
            value = field_match.group("value").strip()
            if key == "mode":
                task.mode = value.upper()
            elif key == "depends on":
                task.has_dependency_field = True
                if value.lower() not in {"none", "none.", "-"}:
                    # A dependency line may carry conditional clauses after a
                    # semicolon, for example "T041, T025; T049 PASS before any
                    # v0.3.0". Only the first clause is a hard ordering
                    # constraint; a conditional clause is a gate for a later
                    # phase and must not be treated as file ordering.
                    hard, _, conditional = value.partition(";")
                    task.depends_on = TASK_REF.findall(hard)
                    task.conditional_on = TASK_REF.findall(conditional)
            elif key == "traces":
                task.traces = [
                    item.strip().rstrip(".")
                    for item in value.split(",")
                    if item.strip()
                ]
        tasks.append(task)
    return tasks


def reachable_modes(
    identifier: str,
    by_id: dict[str, Task],
    seen: set[str] | None = None,
) -> set[str]:
    """Return every mode reachable through the dependency chain."""
    seen = seen if seen is not None else set()
    if identifier in seen:
        return set()
    seen.add(identifier)
    task = by_id.get(identifier)
    if task is None:
        return set()
    modes = set()
    for dependency in task.depends_on:
        parent = by_id.get(dependency)
        if parent is None:
            continue
        modes.add(parent.mode)
        modes |= reachable_modes(dependency, by_id, seen)
    return modes


def find_cycle(by_id: dict[str, Task]) -> list[str] | None:
    """Return one dependency cycle, if any exists."""
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {identifier: WHITE for identifier in by_id}
    stack: list[str] = []

    def visit(identifier: str) -> list[str] | None:
        colour[identifier] = GREY
        stack.append(identifier)
        for dependency in by_id[identifier].depends_on:
            if dependency not in colour:
                continue
            if colour[dependency] == GREY:
                return stack[stack.index(dependency):] + [dependency]
            if colour[dependency] == WHITE:
                found = visit(dependency)
                if found:
                    return found
        colour[identifier] = BLACK
        stack.pop()
        return None

    for identifier in by_id:
        if colour[identifier] == WHITE:
            found = visit(identifier)
            if found:
                return found
    return None


def validate(tasks: list[Task]) -> list[str]:
    errors: list[str] = []
    by_id: dict[str, Task] = {}

    for task in tasks:
        if task.identifier in by_id:
            errors.append(f"{task.identifier}: duplicate task identifier")
            continue
        by_id[task.identifier] = task

    if not by_id:
        errors.append("no task block was found; the gate would pass vacuously")
        return errors

    # A package uses either a RED/GREEN plan form, which declares a Mode per
    # task, or an execution-ledger form, which declares Status and Evidence.
    # Requiring Mode in a ledger is a category error; requiring consistency is
    # not, because a package that mixes both forms cannot be read reliably.
    declares_mode = sum(1 for task in tasks if task.mode)
    plan_form = declares_mode > 0

    # A package either declares dependencies for its tasks or does not. Some
    # execution ledgers record Status, Owner, Scope, and Validation without an
    # ordering claim; there is no graph to check there, and demanding one is
    # the same category error as demanding a Mode. A package that declares
    # dependencies for some tasks and not others is still rejected, because a
    # reader cannot tell which omissions are deliberate.
    declares_dependencies = sum(1 for task in tasks if task.has_dependency_field)
    ordered_form = declares_dependencies > 0

    for task in tasks:
        if plan_form and not task.mode:
            errors.append(
                f"{task.identifier}: declares no Mode, but this package uses "
                f"the RED/GREEN plan form ({declares_mode} of {len(tasks)} "
                "tasks declare one)"
            )
        if ordered_form and not task.has_dependency_field:
            errors.append(
                f"{task.identifier}: declares no 'Depends on' field, but this "
                f"package declares one for {declares_dependencies} of "
                f"{len(tasks)} tasks"
            )
        if plan_form and not task.traces:
            errors.append(f"{task.identifier}: traces no requirement")
        for dependency in task.conditional_on:
            if dependency not in by_id:
                errors.append(
                    f"{task.identifier}: conditionally depends on {dependency}, "
                    "which does not exist"
                )
        for dependency in task.depends_on:
            if dependency not in by_id:
                errors.append(
                    f"{task.identifier}: depends on {dependency}, which does "
                    "not exist"
                )
                continue
            if by_id[dependency].order > task.order:
                errors.append(
                    f"{task.identifier}: depends on {dependency}, which is "
                    "declared later; the file cannot be executed in order"
                )

    cycle = find_cycle(by_id)
    if cycle:
        errors.append("dependency cycle: " + " -> ".join(cycle))
    elif plan_form:
        for task in tasks:
            if task.mode in GREEN_MODES:
                if not RED_MODES & reachable_modes(task.identifier, by_id):
                    errors.append(
                        f"{task.identifier}: mode {task.mode} does not depend "
                        "on a RED task, so an implementation could precede its "
                        "failing test"
                    )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=None)
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate every package that uses machine-readable task blocks.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.all and args.spec:
        parser.error("--all and --spec are mutually exclusive")

    if args.all:
        targets = sorted(
            path.parent
            for path in (ROOT / ".specs").glob("*/TASKS.md")
            if TASK_HEADING_HINT.search(path.read_text(encoding="utf-8"))
        )
        if not targets:
            print(
                "no package uses machine-readable task blocks; the gate would "
                "pass vacuously",
                file=sys.stderr,
            )
            return 1
    else:
        targets = [args.spec or DEFAULT_SPEC]

    reports = []
    total_errors = 0
    for target in targets:
        tasks_file = target / "TASKS.md"
        if not tasks_file.is_file():
            print(f"missing {tasks_file}", file=sys.stderr)
            return 2
        text = tasks_file.read_text(encoding="utf-8")
        tasks = parse_tasks(text)
        errors = validate(tasks)
        hints = len(TASK_HEADING_HINT.findall(text))
        if hints and not tasks:
            errors.append(
                f"{hints} task headings are present but none parsed; the gate "
                "would report nothing for this package"
            )
        elif hints != len(tasks):
            errors.append(
                f"parsed {len(tasks)} tasks from {hints} task headings; a "
                "silently skipped task is an unchecked dependency"
            )
        total_errors += len(errors)
        modes: dict[str, int] = {}
        for task in tasks:
            modes[task.mode or "(none)"] = modes.get(task.mode or "(none)", 0) + 1
        reports.append(
            {
                "spec": target.name,
                "tasks": len(tasks),
                "modes": modes,
                "errors": errors,
            }
        )

    if args.json:
        print(json.dumps(reports, indent=2, sort_keys=True))
    else:
        for report in reports:
            print(f"{report['spec']}: tasks parsed {report['tasks']}")
            if not args.all:
                for mode, count in sorted(report["modes"].items()):
                    print(f"  {mode}: {count}")
            for error in report["errors"]:
                print(f"{report['spec']}: {error}", file=sys.stderr)
        print(f"Summary: task-graph findings {total_errors}")

    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
