#!/usr/bin/env python3
"""Export versioned, explicitly unapproved English authoring templates.

This exports the canonical skill references, not generated project requirements.
It never publishes, authenticates, approves, or overwrites an existing version.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / ".github/skills/sdd-requirements-engineer/references"
ARTIFACTS = (
    "SPECIFICATION.md", "ANALYSIS.md", "DESIGN.md", "TASKS.md", "TESTING.md",
    "DECISIONS.md", "CHECKLIST.md", "CROSS_ANALYSIS.md", "VERIFICATION.md",
    "SOURCE_TRACEABILITY.md",
)


def extract_template(text: str, heading: str | None = None) -> str:
    if heading:
        marker = f"## {heading}\n"
        if marker not in text:
            raise ValueError(f"missing canonical template {heading}")
        text = text.split(marker, 1)[1]
    match = re.search(r"^(`{3,})markdown\n", text, re.MULTILINE)
    if match is None:
        raise ValueError(f"missing Markdown template fence: {heading}")
    end = re.search(r"^" + re.escape(match[1]) + r"$", text[match.end():], re.MULTILINE)
    if end is None:
        raise ValueError(f"unterminated Markdown template: {heading}")
    return text[match.end():match.end() + end.start()].rstrip() + "\n"


def template_files() -> dict[str, str]:
    source = (REFERENCES / "spec-templates.md").read_text(encoding="utf-8")
    warning = (
        "> UNAPPROVED AUTHORING TEMPLATE. Replace every authoring slot with "
        "project-specific evidence; this is not an approved or implemented specification.\n\n"
    )
    files = {
        name: warning + extract_template(source, name)
        for name in ARTIFACTS
    }
    for name, reference in (
        ("FRD.md", "frd-template.md"),
        ("NFRD.md", "nfrd-template.md"),
        ("TDD.md", "tdd-and-library-lifecycle.md"),
    ):
        files[name] = warning + extract_template(
            (REFERENCES / reference).read_text(encoding="utf-8")
        )
    for path in sorted(REFERENCES.glob("*.md")):
        files[f"references/{path.name}"] = path.read_text(encoding="utf-8")
    files["CONSTITUTION.md"] = warning + extract_template(source, "CONSTITUTION.md")
    for checkpoint in ("spec-to-plan", "plan-to-tasks", "test-coverage"):
        files[f"checkpoints/{checkpoint}.yaml"] = (
            "# UNAPPROVED AUTHORING TEMPLATE: replace with project-specific mappings.\n"
            'schema_version: "1.0"\n'
            'feature:\n  id: "<feature-id>"\n  slug: "<feature-slug>"\n'
            '  specification_version: "<version>"\n'
            f"checkpoint:\n  type: {checkpoint}\n"
            "  mapping_status: incomplete\n  approval_status: pending\n"
            '  generated_on: "<date>"\n'
            "requirements: {}\n"
        )
    files["contracts/manifest.yaml"] = (
        "# UNAPPROVED AUTHORING TEMPLATE: declare actual provided contracts or\n"
        "# scoped, reviewed non-applicability. Empty mappings never pass handoff.\n"
        'schema_version: "1.0"\n'
        'feature:\n  id: "<feature-id>"\n  slug: "<feature-slug>"\n'
        "contracts: {}\n"
    )
    return files


def export(destination: Path) -> None:
    if destination.exists():
        raise ValueError("destination already exists; choose a new immutable template version")
    files = template_files()
    files["template-manifest.json"] = json.dumps({
        "schema_version": "1.0",
        "status": "unapproved_authoring_template",
        "language": "en",
        "source": "Ohorizons/ohorizons-demo:.github/skills/sdd-requirements-engineer",
        "required_artifacts": [*ARTIFACTS, "FRD.md", "NFRD.md", "TDD.md"],
        "files": {
            path: hashlib.sha256(content.encode("utf-8")).hexdigest()
            for path, content in sorted(files.items())
        },
    }, indent=2, sort_keys=True) + "\n"
    for name, content in files.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new version directory in a library checkout")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        export(args.destination)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Exported unapproved English templates to {args.destination}")


if __name__ == "__main__":
    main()
