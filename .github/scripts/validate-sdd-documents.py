#!/usr/bin/env python3
"""Validate canonical DESIGN.md and TASKS.md document contracts."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = {
    "005-aeg-open-horizons-azure-dev-pilot",
    "006-terraform-adoption-live-azure",
}
MERMAID = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
TASK = re.compile(
    r"^-\s+\[(?P<mark>[ xX])\]\s+\*\*(?P<id>T\d{3})"
    r"(?P<meta>.*?)\*\*(?P<body>.*?)(?=^-\s+\[[ xX]\]\s+\*\*T\d{3}|\Z)",
    re.MULTILINE | re.DOTALL,
)
TASK_ID = re.compile(r"\bT\d{3}\b")
REQ_ID = re.compile(r"\b(?:REQ|NFR)-\d{3}\b")
COMPLETION_LEDGER = re.compile(
    r"Marked complete by verification sweep:\s*(?P<ids>[^\n]+)",
    re.IGNORECASE,
)

GRAPHLIKE = ("flowchart", "graph", "classDiagram")
NON_STYLEABLE = ("sequenceDiagram", "erDiagram", "stateDiagram", "gantt")
PALETTE = (
    "classDef default fill:#FFFFFF,stroke:#777777,color:#222222",
    "classDef zone fill:#F2F2F2,stroke:#999999,color:#222222",
    "classDef external fill:#E8E8E8,stroke:#555555,color:#222222",
)
DESIGN_SECTIONS = (
    "Table of Contents",
    "Feature Metadata",
    "Architecture Overview",
    "System Context",
    "Architectural Invariants",
    "Deployment View",
    "State Model",
    "Critical Sequences",
    "Data Model",
    "Interfaces and Contracts",
    "Error Model",
    "Security Design",
    "Threat Model",
    "Observability Design",
    "Testing Strategy",
    "Implementation Surface",
    "Delivery and Traceability View",
    "Risks and Trade-Offs",
    "Phased Development",
    "Change Log",
    "References",
)
TASK_SECTIONS = (
    "Table of Contents",
    "Feature Metadata",
    "Pre-Implementation Gate",
    "Execution Rules",
    "Dependency Graph",
    "Test Case Mapping",
    "Completion Gate",
    "Change Log",
    "References",
)
DELIVERY_TERMS = (
    ("Requirements",),
    ("Design components",),
    ("Tasks",),
    ("Dependencies",),
    ("Tests or evidence", "Verification evidence"),
    ("Current versus target", "Current state", "Current / target"),
)


def is_gray(value: str) -> bool:
    if len(value) == 3:
        value = "".join(character * 2 for character in value)
    red, green, blue = (
        int(value[index:index + 2], 16) for index in (0, 2, 4)
    )
    return red == green == blue


def packages(spec_root: pathlib.Path, selected: str | None) -> list[pathlib.Path]:
    found = sorted(
        path
        for path in spec_root.glob("[0-9][0-9][0-9]-*")
        if path.is_dir()
        and path.name not in FROZEN
        and (path / "SPECIFICATION.md").is_file()
    )
    if selected is None:
        return found
    return [
        path
        for path in found
        if path.name == selected or path.name.startswith(f"{selected}-")
    ]


def section_errors(
    package: pathlib.Path,
    artifact: str,
    text: str,
    required: tuple[str, ...],
) -> list[str]:
    headings = set(HEADING.findall(text))
    return [
        f"{package.name}/{artifact}: missing `## {section}`"
        for section in required
        if section not in headings
    ]


def diagram_errors(path: pathlib.Path, text: str) -> tuple[list[str], int]:
    errors: list[str] = []
    blocks = list(MERMAID.finditer(text))
    for index, match in enumerate(blocks, 1):
        body = match.group(1)
        first = next(
            (
                line.strip()
                for line in body.splitlines()
                if line.strip() and not line.strip().startswith("%%{")
            ),
            "?",
        )
        kind = first.split()[0]
        label = f"{path} diagram {index} ({kind})"
        chromatic = next(
            (
                item.group(1)
                for item in HEX.finditer(body)
                if not is_gray(item.group(1))
            ),
            None,
        )
        if chromatic:
            errors.append(f"{label}: chromatic color #{chromatic}")
        if kind.startswith(GRAPHLIKE):
            for palette_line in PALETTE:
                count = body.count(palette_line)
                if count != 1:
                    errors.append(
                        f"{label}: expected one `{palette_line}`, found {count}"
                    )
        elif kind.startswith(NON_STYLEABLE) and "classDef" in body:
            errors.append(f"{label}: classDef is invalid for {kind}")
    return errors, len(blocks)


def validate_design(package: pathlib.Path) -> tuple[list[str], int]:
    path = package / "DESIGN.md"
    text = path.read_text(encoding="utf-8")
    errors, count = diagram_errors(path, text)
    errors.extend(section_errors(package, path.name, text, DESIGN_SECTIONS))
    headings = set(HEADING.findall(text))
    if not ({"Component Map", "Service Map"} & headings):
        errors.append(f"{package.name}/DESIGN.md: missing component or service map")
    if not any(
        heading.startswith("Data Flow") or heading.startswith("Data Lifecycle")
        for heading in headings
    ):
        errors.append(f"{package.name}/DESIGN.md: missing data-flow or lifecycle view")
    if count < 6:
        errors.append(
            f"{package.name}/DESIGN.md: {count} diagrams; expected at least six "
            "covering architecture, components, deployment, state, sequence, and data"
        )
    delivery = text.split("## Delivery and Traceability View", 1)
    if len(delivery) == 2:
        for alternatives in DELIVERY_TERMS:
            if not any(term in delivery[1] for term in alternatives):
                errors.append(
                    f"{package.name}/DESIGN.md: delivery view misses {alternatives}"
                )
    return errors, count


def validate_tasks(package: pathlib.Path) -> tuple[list[str], int]:
    path = package / "TASKS.md"
    text = path.read_text(encoding="utf-8")
    errors, count = diagram_errors(path, text)
    errors.extend(section_errors(package, path.name, text, TASK_SECTIONS))
    if "## Execution log" not in text:
        errors.append(f"{package.name}/TASKS.md: missing dated execution log")

    tasks = list(TASK.finditer(text))
    if not tasks:
        errors.append(
            f"{package.name}/TASKS.md: no checkbox tasks; use "
            "`- [ ] **T001 [S] [Plan:P1.1] ...**`"
        )
        return errors, count

    identifiers = [task.group("id") for task in tasks]
    mapping_section = text.split("## Test Case Mapping", 1)
    mapping_text = (
        mapping_section[1].split("\n## ", 1)[0]
        if len(mapping_section) == 2
        else ""
    )
    for identifier in sorted(set(identifiers)):
        if identifiers.count(identifier) > 1:
            errors.append(f"{package.name}/TASKS.md: duplicate {identifier}")

    for task in tasks:
        identifier = task.group("id")
        metadata = task.group("meta")
        body = task.group("body")
        full = metadata + body
        if not ({"[S]", "[P]"} & set(metadata.split())):
            errors.append(f"{package.name}/TASKS.md: {identifier} misses [S] or [P]")
        if "[Plan:" not in metadata:
            errors.append(f"{package.name}/TASKS.md: {identifier} misses plan mapping")
        mapped_rows = "\n".join(
            line
            for line in mapping_text.splitlines()
            if identifier in line
        )
        if (
            not REQ_ID.search(full)
            and "all requirements" not in full.lower()
            and not REQ_ID.search(mapped_rows)
        ):
            errors.append(f"{package.name}/TASKS.md: {identifier} maps no requirement")
        if not re.search(r"^\s+-\s+Files?:", body, re.MULTILINE):
            errors.append(f"{package.name}/TASKS.md: {identifier} has no change surface")
        if not re.search(r"^\s+-\s+Acceptance:", body, re.MULTILINE):
            errors.append(f"{package.name}/TASKS.md: {identifier} has no acceptance")

    dependency_section = text.split("## Dependency Graph", 1)
    graph = MERMAID.search(dependency_section[1]) if len(dependency_section) == 2 else None
    graph_ids = set(TASK_ID.findall(graph.group(1))) if graph else set()
    task_ids = set(identifiers)
    if graph_ids != task_ids:
        errors.append(
            f"{package.name}/TASKS.md: DAG mismatch "
            f"missing={sorted(task_ids - graph_ids)} "
            f"unknown={sorted(graph_ids - task_ids)}"
        )

    checked = {
        task.group("id")
        for task in tasks
        if task.group("mark").lower() == "x"
    }
    ledger = COMPLETION_LEDGER.search(text)
    logged = set(TASK_ID.findall(ledger.group("ids"))) if ledger else set()
    if checked and ledger is None:
        errors.append(f"{package.name}/TASKS.md: checked tasks lack verification ledger")
    if checked != logged:
        errors.append(
            f"{package.name}/TASKS.md: checkbox/ledger mismatch "
            f"checked_not_logged={sorted(checked - logged)} "
            f"logged_not_checked={sorted(logged - checked)}"
        )
    return errors, count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec-root",
        type=pathlib.Path,
        default=ROOT / ".specs",
    )
    parser.add_argument("--package")
    args = parser.parse_args(argv)

    selected = packages(args.spec_root.resolve(), args.package)
    if not selected:
        print("no canonical specification package matched", file=sys.stderr)
        return 2

    errors: list[str] = []
    diagram_count = 0
    for package in selected:
        design_errors, design_count = validate_design(package)
        task_errors, task_count = validate_tasks(package)
        errors.extend(design_errors)
        errors.extend(task_errors)
        diagram_count += design_count + task_count

    for error in errors:
        print(error, file=sys.stderr)
    print(
        f"SDD document standard: packages {len(selected)} "
        f"diagrams {diagram_count} errors {len(errors)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
