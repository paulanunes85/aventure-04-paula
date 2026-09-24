#!/usr/bin/env python3
"""Validate the durable shape of SDD artifacts under `.specs/`.

Specification-authoring tasks previously declared `git diff --check -- <path>`
as their only validation vector. That command inspects whitespace in a diff, so
on a clean tree it compares nothing and exits 0 even for a path that does not
exist. It would pass identically against an empty specification.

This validator is discriminating: it fails when a specification is missing,
incomplete, internally inconsistent, or still carries placeholder text. It
enforces the conventions in `.github/instructions/sdd-artifacts.instructions.md`
and nothing beyond them. Every canonical feature package uses the same ten-file
portfolio. The repository-level `.specs/CONSTITUTION.md` is reused and must not
be duplicated merely to satisfy a feature-local gate.

Usage:
    validate-spec-artifacts.py [SPEC_DIR ...]

With no arguments every directory under `.specs/` that contains
`SPECIFICATION.md` is validated; auxiliary reference directories are ignored.
Exit code 0 means every checked specification satisfies the conventions.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS_DIR = ROOT / ".specs"

REQUIRED_ARTIFACTS = (
    "ANALYSIS.md",
    "CHECKLIST.md",
    "CROSS_ANALYSIS.md",
    "DECISIONS.md",
    "DESIGN.md",
    "SOURCE_TRACEABILITY.md",
    "SPECIFICATION.md",
    "TASKS.md",
    "TESTING.md",
    "VERIFICATION.md",
)

OPTIONAL_ARTIFACTS = (
    "IMPLEMENTATION_PLAN.md",
    "TEST_MANIFEST.yaml",
    "TEST_PLAN.md",
)

KNOWN_ARTIFACTS = REQUIRED_ARTIFACTS + OPTIONAL_ARTIFACTS

DIRECTORY_PATTERN = re.compile(r"^[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
# Requirements are authored three ways in this repository, all legitimate:
# a level-three heading, a level-four heading, and a table row. A gate that
# recognized only one of them reported "declares no SHALL requirement" against
# specifications holding as many as 99, which trains readers to ignore it.
REQUIREMENT_HEADING_PATTERN = re.compile(
    r"^#{3,4} ((?!AC-)[A-Z]{2,}-(?:[A-Z0-9]+-)?[0-9]{3}):",
    re.MULTILINE,
)
REQUIREMENT_ID_PATTERN = re.compile(
    r"^(?!AC-)[A-Z]{2,}-(?:[A-Z0-9]+-)?[0-9]{3}$"
)
REQUIREMENT_BULLET_PATTERN = re.compile(
    r"^\s*-\s+\*\*((?!AC-)[A-Z]{2,}-(?:[A-Z0-9]+-)?[0-9]{3}):\*\*"
    r"\s*(.*)$"
)
SHALL_PATTERN = re.compile(r"\bSHALL\b", re.IGNORECASE)
# Two exact acceptance-criterion forms are in use. They are written as
# separate alternatives rather than one pattern of optional fragments, because
# a permissive combined pattern matched unrelated lines and reported four
# times as many findings as it should have.
ACCEPTANCE_PATTERN = re.compile(
    r"^\s*-\s+`?(AC-((?:FR|NFR)-[A-Z0-9]+-[0-9]{3})-[0-9]{2})`?"
    r"(?:\s+\([^)]+\))?\s*:\s*(.+)$",
    re.MULTILINE,
)
ACCEPTANCE_BOLD_PATTERN = re.compile(
    r"^\s*-\s+\*\*(AC-((?:FR|NFR)-[A-Z0-9]+-[0-9]{3})-[0-9]{2})"
    r"(?:\s+\([^)]+\))?:\*\*\s*(.+)$",
    re.MULTILINE,
)


def acceptance_criteria(text: str) -> list[re.Match[str]]:
    """Return acceptance criteria written in either supported form."""
    return list(ACCEPTANCE_PATTERN.finditer(text)) + list(
        ACCEPTANCE_BOLD_PATTERN.finditer(text)
    )
PLACEHOLDER_PATTERN = re.compile(r"\b(TODO|TBD|FIXME|XXX|LOREM IPSUM)\b")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, spec: str, message: str) -> None:
        self.errors.append(f"{spec}: ERROR: {message}")


def requirement_sections(text: str) -> list[tuple[str, str]]:
    """Return `(requirement ID, section body)` pairs from requirement headings."""
    headings = list(REQUIREMENT_HEADING_PATTERN.finditer(text))
    sections: list[tuple[str, str]] = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections.append((heading.group(1), text[heading.end():end]))
    return sections


def requirement_table_rows(text: str) -> list[tuple[str, str, str | None]]:
    """Read declaration tables, never traceability tables.

    A declaration table has `ID` in its first header cell and `Requirement` or
    `EARS requirement` in its second. Rows whose first cell is not a requirement
    ID (for example `AC-*` rows in an acceptance table) are ignored.
    """
    lines = text.splitlines()
    rows: list[tuple[str, str, str | None]] = []
    index = 0
    while index < len(lines):
        header = lines[index]
        if not header.lstrip().startswith("|"):
            index += 1
            continue
        cells = [cell.strip() for cell in header.strip().strip("|").split("|")]
        if (
            len(cells) < 2
            or cells[0].lower() != "id"
            or cells[1].lower() not in {"requirement", "ears requirement"}
            or index + 1 >= len(lines)
            or not re.fullmatch(r"\s*\|(?:\s*:?-{3,}:?\s*\|)+\s*", lines[index + 1])
        ):
            index += 1
            continue

        index += 2
        while index < len(lines) and lines[index].lstrip().startswith("|"):
            values = [
                cell.strip() for cell in lines[index].strip().strip("|").split("|")
            ]
            if len(values) >= 2 and REQUIREMENT_ID_PATTERN.fullmatch(values[0]):
                acceptance = values[2] if len(values) >= 3 and values[2] else None
                rows.append((values[0], values[1], acceptance))
            index += 1
    return rows


def requirement_bullet_rows(text: str) -> list[tuple[str, str, str | None]]:
    """Read the historical bold-bullet requirement form.

    The reference program uses this form for most packages. Requirement
    metadata and acceptance mappings follow on indented lines, so only the
    first line is the normative EARS statement.
    """
    lines = text.splitlines()
    rows: list[tuple[str, str, str | None]] = []
    index = 0
    while index < len(lines):
        match = REQUIREMENT_BULLET_PATTERN.match(lines[index])
        if not match:
            index += 1
            continue

        statement = [match.group(2).strip()]
        index += 1
        while index < len(lines):
            continuation = lines[index]
            if (
                not continuation.strip()
                or continuation.lstrip().startswith(("- ", "#"))
                or not continuation.startswith(("  ", "\t"))
            ):
                break
            statement.append(continuation.strip())
            index += 1
        rows.append((match.group(1), " ".join(statement).strip(), None))
    return rows


def legacy_ears_statement(section: str) -> str | None:
    """Extract one legacy requirement statement from a heading section."""
    quoted = [
        line.removeprefix(">").strip()
        for line in section.splitlines()
        if line.lstrip().startswith(">") and line.removeprefix(">").strip()
    ]
    if quoted:
        return " ".join(quoted)

    stop_markers = ("**Acceptance Criteria:**", "---", "\n## ")
    end = len(section)
    for marker in stop_markers:
        position = section.find(marker)
        if position >= 0:
            end = min(end, position)
    lines = [
        line.strip()
        for line in section[:end].splitlines()
        if line.strip() and not line.strip().startswith("**")
    ]
    return " ".join(lines) if lines else None



def ears_statement(section: str) -> str | None:
    """Extract the normative EARS statement, excluding acceptance criteria.

    Some specifications place acceptance criteria immediately below the
    requirement; others collect them in a later document section. Requiring
    both markers in one section reported "no EARS statement" against
    requirements that state one perfectly well, so the end of the statement
    falls back to the next bold label or the end of the section.
    """
    marker = "**EARS requirement:**"
    acceptance_marker = "**Acceptance criteria (EARS):**"
    start = section.find(marker)
    if start < 0:
        return None
    end = section.find(acceptance_marker, start)
    if end < 0:
        # The last requirement in a document has no following requirement
        # heading, so its section runs to end of file. Without an explicit
        # stop the statement absorbed every later constraint and appendix,
        # and the SHALL count reported 42 instead of 1.
        remainder = section[start + len(marker):]
        following = re.search(
            r"^(?:#{1,6}\s|\s*-?\s*\*\*[^*]+:\*\*)", remainder, re.MULTILINE
        )
        end = (
            start + len(marker) + following.start()
            if following
            else len(section)
        )
    lines = [
        line.removeprefix(">").strip()
        for line in section[start + len(marker):end].splitlines()
        if line.removeprefix(">").strip()
    ]
    return " ".join(lines) if lines else None


def accepted_ears_deviations(spec_dir: Path) -> set[str]:
    """Return IDs explicitly accepted as EARS-form deviations in decisions."""
    decisions = spec_dir / "DECISIONS.md"
    if not decisions.is_file():
        return set()
    accepted: set[str] = set()
    for block in decisions.read_text(encoding="utf-8").split("\n- "):
        if "**EARS form deviation (accepted):**" not in block:
            continue
        accepted.update(match.group(1) for match in ACCEPTANCE_PATTERN.finditer(block))
        accepted.update(
            re.findall(r"\bAC-(?:FR|NFR)-[A-Z0-9]+-[0-9]{3}-[0-9]{2}\b", block)
        )
    return accepted


def validate_spec(spec_dir: Path, report: Report) -> None:
    name = spec_dir.name

    if not DIRECTORY_PATTERN.fullmatch(name):
        report.error(name, "directory must be a zero-padded number plus a kebab-case slug")

    for artifact in REQUIRED_ARTIFACTS:
        path = spec_dir / artifact
        if not path.is_file():
            report.error(name, f"required artifact is missing: {artifact}")
        elif not path.read_text(encoding="utf-8").strip():
            report.error(name, f"required artifact is empty: {artifact}")

    specification = spec_dir / "SPECIFICATION.md"
    if not specification.is_file():
        return

    spec_text = specification.read_text(encoding="utf-8")
    sections = requirement_sections(spec_text)
    table_rows = (
        []
        if sections
        else requirement_bullet_rows(spec_text) or requirement_table_rows(spec_text)
    )
    requirement_order = [rid for rid, _ in sections] + [
        rid for rid, _, _ in table_rows
    ]
    declared = set(requirement_order)
    accepted_deviations = accepted_ears_deviations(spec_dir)


    if not sections and not table_rows:
        if SHALL_PATTERN.search(spec_text):
            # Saying "no SHALL requirement" here would be false and would
            # send an author looking for the wrong problem.
            report.error(
                name,
                "SPECIFICATION.md declares SHALL requirements without a recognizable "
                "requirement heading; use a level-three or level-four heading "
                "keyed by the requirement identifier",
            )
        else:
            report.error(name, "SPECIFICATION.md declares no `SHALL` requirement")

    duplicates = sorted({rid for rid in requirement_order if requirement_order.count(rid) > 1})
    for rid in duplicates:
        report.error(name, f"requirement heading is duplicated: {rid}")

    for rid, statement, acceptance in table_rows:
        if len(SHALL_PATTERN.findall(statement)) < 1:
            report.error(
                name,
                f"legacy table requirement {rid} contains no SHALL response",
            )
        if acceptance is not None and not acceptance.strip():
            report.error(
                name,
                f"legacy table requirement {rid} has an empty acceptance criterion",
            )

    # Strict exact-one-SHALL and criterion-ID checks apply to the canonical
    # marker convention. Legacy headings remain machine checked for a
    # requirement response and source traceability without pretending their
    # historical acceptance bullets have canonical IDs.
    canonical = any("**EARS requirement:**" in section for _, section in sections)
    if sections and not canonical:
        for rid, section in sections:
            statement = legacy_ears_statement(section)
            if statement is None:
                report.error(name, f"legacy requirement {rid} has no statement")
            elif len(SHALL_PATTERN.findall(statement)) < 1:
                report.error(
                    name,
                    f"legacy requirement {rid} contains no SHALL response",
                )

    if canonical:
        # Acceptance criteria are collected once, document-wide, and grouped by
        # the requirement each one names. Searching per section and then
        # falling back to the whole document counted the same criterion twice
        # whenever the last requirement's section ran to the end of the file.
        acceptance_ids: list[str] = []
        by_parent: dict[str, list[str]] = {}
        for criterion in acceptance_criteria(spec_text):
            acceptance_id, parent, response = criterion.groups()
            acceptance_ids.append(acceptance_id)
            by_parent.setdefault(parent, []).append(acceptance_id)
            if parent not in declared:
                report.error(
                    name,
                    f"acceptance criterion {acceptance_id} names {parent}, "
                    "which is not a declared requirement",
                )
            if (
                len(SHALL_PATTERN.findall(response)) != 1
                and acceptance_id not in accepted_deviations
            ):
                report.error(
                    name,
                    f"acceptance criterion {acceptance_id} must contain exactly one SHALL "
                    "or have an accepted EARS-form deviation",
                )

        for rid, section in sections:
            statement = ears_statement(section)
            if statement is None:
                report.error(name, f"requirement {rid} has no EARS statement")
            elif len(SHALL_PATTERN.findall(statement)) != 1:
                report.error(
                    name,
                    f"requirement {rid} EARS statement must contain exactly one SHALL",
                )
            if not by_parent.get(rid):
                report.error(name, f"requirement {rid} has no acceptance criterion")

            # Placement only carries meaning when the requirement co-locates
            # its own criteria. When a specification collects criteria in a
            # later section, that section falls inside whichever requirement
            # heading precedes it, and every criterion there would be reported
            # as misfiled -- 38 false findings in specification 006.
            if "**Acceptance criteria (EARS):**" not in section:
                continue
            for criterion in acceptance_criteria(section):
                acceptance_id, parent, _ = criterion.groups()
                if parent != rid and parent in declared:
                    report.error(
                        name,
                        f"acceptance criterion {acceptance_id} is under {rid}, "
                        f"not {parent}",
                    )

        for acceptance_id in sorted(
            {aid for aid in acceptance_ids if acceptance_ids.count(aid) > 1}
        ):
            report.error(name, f"acceptance criterion is duplicated: {acceptance_id}")

    traceability = spec_dir / "SOURCE_TRACEABILITY.md"
    if traceability.is_file():
        trace_text = traceability.read_text(encoding="utf-8")
        for rid in sorted(declared):
            if not re.search(rf"\b{re.escape(rid)}\b", trace_text):
                report.error(name, f"requirement {rid} has no source traceability entry")

    for artifact in KNOWN_ARTIFACTS:
        path = spec_dir / artifact
        if not path.is_file():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if PLACEHOLDER_PATTERN.search(line) and "placeholder" not in line.lower():
                report.error(name, f"{artifact}:{number} contains placeholder text")


def resolve_targets(arguments: list[str]) -> list[Path]:
    if arguments:
        return [Path(a) if Path(a).is_absolute() else ROOT / a for a in arguments]
    if not SPECS_DIR.is_dir():
        return []
    return sorted(
        path
        for path in SPECS_DIR.iterdir()
        if path.is_dir() and (path / "SPECIFICATION.md").is_file()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec_dirs", nargs="*", help="specification directories to validate")
    args = parser.parse_args(argv)

    targets = resolve_targets(args.spec_dirs)
    if not targets:
        print("No specification directories found", file=sys.stderr)
        return 1

    report = Report()
    for target in targets:
        if not target.is_dir():
            report.error(target.name, f"specification directory does not exist: {target}")
            continue
        validate_spec(target, report)

    for error in report.errors:
        print(error, file=sys.stderr)

    print(f"Summary: specifications {len(targets)}, errors {len(report.errors)}")
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
