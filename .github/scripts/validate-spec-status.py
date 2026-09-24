#!/usr/bin/env python3
"""Validate that every specification declares an honest implementation status.

This repository has drifted before: a specification declared itself
"Implemented" while its own verification record named unresolved blockers.
Nothing caught it, because implementation status was prose that no tool read.

Task status is written five different ways across the specifications here --
checkboxes, `**Status**:` lines, table cells, and combinations -- so counting
completed tasks cannot answer "is this specification implemented?". The
answerable question is whether the specification makes an explicit claim and
whether its own verification record supports that claim.

Six rules are enforced:

1. Every specification declares `implementation_status` from a controlled
   vocabulary. Silence is not a status.
2. A specification claiming completion has a verification record containing at
   least one passing check, and no unresolved blocker.
3. A specification claiming partial completion names what is still blocked,
   so the remaining work is discoverable rather than implied.
4. A completion claim has no unchecked canonical task.
5. A completion claim agrees with passing implementation and execution
   checkpoints.
6. A `Verified` claim has approved implementation and execution checkpoints.

Exit code 0 means every specification's claim is supported. Exit code 1 means
at least one claim is missing, unsupported, or contradicted.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is a repository prerequisite
    print("FATAL: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
STATUS_FIELD = re.compile(r"^implementation_status:\s*(.+?)\s*$", re.MULTILINE)
TASK_CHECKBOX = re.compile(
    r"^-\s+\[(?P<mark>[ xX])\]\s+\*\*(?P<id>T\d{3})\b",
    re.MULTILINE,
)

# Ordered from least to most complete.
VOCABULARY = (
    "Not started",
    "Planned",
    "Partial",
    "Implemented",
    "Verified",
)

COMPLETION_CLAIMS = frozenset({"Implemented", "Verified"})

# Completion claims need a structured PASS verdict -- a line that IS the
# verdict or a table cell that IS the verdict -- never the word inside prose
# ("all checks PASS." proves nothing was executed).
PASS_MARKER = re.compile(
    r"^(?:Result:\s*)?PASS\b"        # verdict line
    r"|\|\s*PASS\s*\|",             # table cell verdict
    re.MULTILINE,
)
# A structured blocker line, not a word in prose: the line must START with
# "Still blocked:" (or "BLOCKED:") and carry content other than "none".
# "BLOCKED is a possible verdict vocabulary" passed the old word-match --
# an adversarial fixture in the 2026-08-30 external audit proved it.
# Structured blocker forms only -- a colon-introduced statement, a table cell
# verdict, or a "Still blocked" heading with content. "BLOCKED is a possible
# verdict vocabulary" in prose matches none of them (adversarial fixture from
# the 2026-08-30 external audit), and "Still blocked: none" is excluded.
BLOCKER_MARKER = re.compile(
    r"^(?:Still blocked|BLOCKED):\s*(?!none\b)\S"      # statement line
    r"|\|\s*BLOCKED\s*\|"                              # table cell verdict
    r"|^#{1,6}\s*Still blocked\s*$\n+(?!\s*none\b)\S",  # heading + content
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class Finding:
    specification: str
    rule: str
    detail: str

    def render(self) -> str:
        return f"{self.specification}: [{self.rule}] {self.detail}"


def declared_status(specification: pathlib.Path) -> str | None:
    text = specification.read_text(encoding="utf-8", errors="replace")
    frontmatter = FRONTMATTER.match(text)
    if frontmatter is None:
        return None
    match = STATUS_FIELD.search(frontmatter.group(1))
    if match is None:
        return None
    return match.group(1).strip().strip('"').strip("'")


def normalize(status: str) -> str:
    """Accept a qualified claim such as 'Partial - blocked on X'."""
    head = re.split(r"\s+[-\u2014:]\s+", status, maxsplit=1)[0].strip()
    for allowed in VOCABULARY:
        if head.lower() == allowed.lower():
            return allowed
    return head


def load_checkpoint(path: pathlib.Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
    except yaml.YAMLError:
        return None
    return document if isinstance(document, dict) else None


def checkpoint_value(document: dict | None, key: str) -> str | None:
    if document is None:
        return None
    checkpoint = document.get("checkpoint")
    if not isinstance(checkpoint, dict):
        return None
    value = checkpoint.get(key)
    return str(value).strip().lower() if value is not None else None


def gate_result(document: dict | None) -> str | None:
    if document is None:
        return None
    gate = document.get("gate")
    if not isinstance(gate, dict):
        return None
    value = gate.get("result", gate.get("status"))
    return str(value).strip().lower() if value is not None else None


def checkpoint_task_ids(document: dict | None) -> list[str]:
    if document is None:
        return []
    plan_items = document.get("plan_items")
    if not isinstance(plan_items, dict):
        return []
    task_ids: list[str] = []
    for plan_item in plan_items.values():
        if not isinstance(plan_item, dict):
            continue
        tasks = plan_item.get("tasks")
        if isinstance(tasks, list):
            task_ids.extend(str(task) for task in tasks)
    return task_ids


def check_specification(directory: pathlib.Path) -> list[Finding]:
    name = directory.name
    # SPECIFICATION.md is the one canonical status document per package
    # (user decision 2026-08-31: the SDD tree lives in .specs/ and the main
    # document is named SPECIFICATION.md; REQUIREMENTS.md was the interim
    # name and is now the anomaly). The first version of this gate returned
    # [] when the document was absent, so a whole tree passed while NO
    # specification declared a status at all -- a vacuous pass, found
    # 2026-08-30. A directory that has a specification either declares a
    # status or fails this gate.
    legacy = directory / "REQUIREMENTS.md"
    canonical = directory / "SPECIFICATION.md"
    if legacy.exists() and canonical.exists():
        return [
            Finding(
                name,
                "conflicting-spec-documents",
                "both REQUIREMENTS.md and SPECIFICATION.md exist; one status "
                "document per specification, or the two can disagree silently",
            )
        ]
    specification = canonical if canonical.exists() else legacy
    if not specification.exists():
        return []

    raw = declared_status(specification)
    if raw is None:
        return [
            Finding(
                name,
                "status-undeclared",
                f"{specification.name} does not declare implementation_status; "
                "a reader cannot tell whether this specification is built",
            )
        ]

    status = normalize(raw)
    if status not in VOCABULARY:
        return [
            Finding(
                name,
                "status-not-in-vocabulary",
                f"{raw!r} is not one of {', '.join(VOCABULARY)}",
            )
        ]

    verification = directory / "VERIFICATION.md"
    if not verification.exists() and (directory / "TESTING.md").exists():
        verification = directory / "TESTING.md"
    verification_text = (
        verification.read_text(encoding="utf-8", errors="replace")
        if verification.exists()
        else ""
    )

    findings: list[Finding] = []

    if status in COMPLETION_CLAIMS:
        if not verification.exists():
            findings.append(
                Finding(
                    name,
                    "completion-without-verification",
                    f"claims {status!r} but has no VERIFICATION.md",
                )
            )
        else:
            if not PASS_MARKER.search(verification_text):
                findings.append(
                    Finding(
                        name,
                        "completion-without-passing-check",
                        f"claims {status!r} but its verification record contains "
                        "no passing check",
                    )
                )
            if BLOCKER_MARKER.search(verification_text):
                findings.append(
                    Finding(
                        name,
                        "completion-contradicted-by-blocker",
                        f"claims {status!r} while its own verification record "
                        "still names a blocker",
                    )
                )

        plan_checkpoint = load_checkpoint(
            directory / "checkpoints" / "plan-to-tasks.yaml"
        )
        tasks_path = directory / "TASKS.md"
        task_entries = (
            TASK_CHECKBOX.findall(
                tasks_path.read_text(encoding="utf-8", errors="replace")
            )
            if tasks_path.is_file()
            else []
        )
        if not task_entries:
            findings.append(
                Finding(
                    name,
                    "completion-without-task-ledger",
                    f"claims {status!r} but TASKS.md has no canonical task checkboxes",
                )
            )
        else:
            task_marks = [mark for mark, _ in task_entries]
            task_ids = [task_id for _, task_id in task_entries]
            planned_task_ids = checkpoint_task_ids(plan_checkpoint)
            if any(mark.lower() != "x" for mark in task_marks):
                findings.append(
                    Finding(
                        name,
                        "completion-with-open-tasks",
                        f"claims {status!r} while TASKS.md still contains unchecked tasks",
                    )
                )
            if len(task_ids) != len(set(task_ids)):
                findings.append(
                    Finding(
                        name,
                        "completion-with-duplicate-task-ids",
                        f"claims {status!r} while TASKS.md repeats canonical task IDs",
                    )
                )
            if not planned_task_ids:
                findings.append(
                    Finding(
                        name,
                        "completion-without-planned-task-map",
                        f"claims {status!r} but plan-to-tasks declares no task IDs",
                    )
                )
            elif set(task_ids) != set(planned_task_ids):
                missing = sorted(set(planned_task_ids) - set(task_ids))
                extra = sorted(set(task_ids) - set(planned_task_ids))
                findings.append(
                    Finding(
                        name,
                        "completion-task-ledger-mismatch",
                        f"claims {status!r} but TASKS.md and plan-to-tasks disagree; "
                        f"missing={missing or 'none'}, extra={extra or 'none'}",
                    )
                )

        implementation_status = checkpoint_value(
            plan_checkpoint, "implementation_status"
        )
        if implementation_status not in {"complete", "implemented"}:
            findings.append(
                Finding(
                    name,
                    "completion-without-implementation-checkpoint",
                    f"claims {status!r} but plan-to-tasks implementation_status is "
                    f"{implementation_status or 'missing/unreadable'}",
                )
            )
        if gate_result(plan_checkpoint) != "pass":
            findings.append(
                Finding(
                    name,
                    "completion-with-failing-task-gate",
                    f"claims {status!r} but the plan-to-tasks gate is not PASS",
                )
            )

        test_checkpoint = load_checkpoint(
            directory / "checkpoints" / "test-coverage.yaml"
        )
        execution_status = checkpoint_value(test_checkpoint, "execution_status")
        if execution_status != "complete":
            findings.append(
                Finding(
                    name,
                    "completion-without-execution-checkpoint",
                    f"claims {status!r} but test-coverage execution_status is "
                    f"{execution_status or 'missing/unreadable'}",
                )
            )
        if gate_result(test_checkpoint) != "pass":
            findings.append(
                Finding(
                    name,
                    "completion-with-failing-test-gate",
                    f"claims {status!r} but the test-coverage gate is not PASS",
                )
            )

        if status == "Verified":
            approvals = {
                checkpoint_value(plan_checkpoint, "approval_status"),
                checkpoint_value(test_checkpoint, "approval_status"),
            }
            if approvals != {"approved"}:
                findings.append(
                    Finding(
                        name,
                        "verification-without-approval",
                        "claims 'Verified' but implementation and test checkpoints "
                        "are not both approved",
                    )
                )

    if status == "Partial" and not BLOCKER_MARKER.search(verification_text):
        findings.append(
            Finding(
                name,
                "partial-without-named-blocker",
                "claims 'Partial' but does not name what is still blocked, so the "
                "remaining work is not discoverable",
            )
        )

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        default=".specs",
        type=pathlib.Path,
        help="directory holding specification folders",
    )
    arguments = parser.parse_args(argv)

    if not arguments.root.is_dir():
        print(f"not a directory: {arguments.root}", file=sys.stderr)
        return 2

    directories = sorted(
        item
        for item in arguments.root.iterdir()
        if item.is_dir()
        and (
            (item / "SPECIFICATION.md").exists()
            or (item / "REQUIREMENTS.md").exists()
        )
    )
    findings: list[Finding] = []
    for directory in directories:
        findings.extend(check_specification(directory))

    print(f"Specification status gate: specifications {len(directories)}, findings {len(findings)}")
    if findings:
        print("", file=sys.stderr)
        for finding in findings:
            print(f"  {finding.render()}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
