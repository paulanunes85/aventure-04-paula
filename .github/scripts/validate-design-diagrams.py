#!/usr/bin/env python3
"""Validate the universal light Mermaid theme across SDD and primitives."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
GITHUB_ROOT = ROOT / ".github"
BLOCK_PATTERNS = (
    re.compile(r"```mermaid\n(?P<body>.*?)```", re.DOTALL),
    re.compile(r"~~~mermaid\n(?P<body>.*?)~~~", re.DOTALL),
)
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
GRAPHLIKE = ("flowchart", "graph", "classDiagram")
NON_STYLEABLE = ("sequenceDiagram", "erDiagram", "stateDiagram", "gantt")
THEME_DIRECTIVE = (
    '%%{init: {"theme":"base","themeVariables":{'
    '"background":"#FFFFFF",'
    '"primaryColor":"#FFFFFF",'
    '"primaryTextColor":"#222222",'
    '"primaryBorderColor":"#777777",'
    '"lineColor":"#555555",'
    '"secondaryColor":"#F2F2F2",'
    '"tertiaryColor":"#E8E8E8"}}}%%'
)
PALETTE = (
    "classDef default fill:#FFFFFF,stroke:#777777,color:#222222",
    "classDef zone fill:#F2F2F2,stroke:#999999,color:#222222",
    "classDef external fill:#E8E8E8,stroke:#555555,color:#222222",
)
FROZEN = {
    "005-aeg-open-horizons-azure-dev-pilot",
    "006-terraform-adoption-live-azure",
}
DEFAULT_ROOTS = (
    ROOT / ".spec",
    GITHUB_ROOT / "skills",
    GITHUB_ROOT / "agents",
    GITHUB_ROOT / "prompts",
    GITHUB_ROOT / "instructions",
)


def is_gray(value: str) -> bool:
    if len(value) == 3:
        value = "".join(character * 2 for character in value)
    red, green, blue = (
        int(value[index:index + 2], 16) for index in (0, 2, 4)
    )
    return red == green == blue


def diagram_kind(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("%%{"):
            return stripped.split()[0]
    return "?"


def canonical_graph_artifact(path: pathlib.Path) -> bool:
    if (
        path.name in {"plan.md", "tasks.md", "frd.md", "nfrd.md"}
        and path.parent.name not in FROZEN
        and (path.parent / "spec.md").is_file()
    ):
        return True
    try:
        relative = path.resolve().relative_to(GITHUB_ROOT)
    except ValueError:
        return False
    return relative.parts[0] in {"skills", "agents", "prompts", "instructions"}


def block_matches(text: str) -> list[re.Match[str]]:
    return sorted(
        (
            match
            for pattern in BLOCK_PATTERNS
            for match in pattern.finditer(text)
        ),
        key=lambda match: match.start(),
    )


def markdown_files(roots: list[pathlib.Path]) -> list[pathlib.Path]:
    return sorted(
        {
            path
            for root in roots
            if root.is_dir()
            for path in root.rglob("*.md")
        }
    )


def validate_block(
    path: pathlib.Path,
    index: int,
    body: str,
) -> list[str]:
    errors: list[str] = []
    kind = diagram_kind(body)
    label = f"{path} diagram {index} ({kind})"
    theme_prefix = f"{THEME_DIRECTIVE}\n"
    if not body.startswith(theme_prefix):
        errors.append(
            f"{label}: missing the universal light theme directive"
        )
    chromatic = next(
        (
            item.group(1)
            for item in HEX.finditer(body)
            if not is_gray(item.group(1))
        ),
        None,
    )
    if chromatic:
        errors.append(
            f"{label}: chromatic color #{chromatic}"
        )
    if kind.startswith(GRAPHLIKE) and canonical_graph_artifact(path):
        for palette_line in PALETTE:
            count = body.count(palette_line)
            if count != 1:
                errors.append(
                    f"{label}: expected one `{palette_line}`, "
                    f"found {count}"
                )
    elif kind.startswith(NON_STYLEABLE) and "classDef" in body:
        errors.append(f"{label}: classDef is invalid for {kind}")
    return errors


def validate_file(path: pathlib.Path) -> tuple[list[str], int]:
    matches = block_matches(path.read_text(encoding="utf-8"))
    errors = [
        error
        for index, match in enumerate(matches, 1)
        for error in validate_block(
            path,
            index,
            match.group("body"),
        )
    ]
    return errors, len(matches)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec-root",
        type=pathlib.Path,
        default=None,
        help=(
            "scan only this root; by default scans .spec and canonical "
            ".github skills, agents, prompts, and instructions"
        ),
    )
    args = parser.parse_args(argv)

    roots = list(
        [args.spec_root.resolve()]
        if args.spec_root is not None
        else DEFAULT_ROOTS
    )
    with_diagrams = [
        path
        for path in markdown_files(roots)
        if block_matches(path.read_text(encoding="utf-8"))
    ]
    if not with_diagrams:
        print(
            "no Mermaid diagrams found; refusing a vacuous pass",
            file=sys.stderr,
        )
        return 2

    reports = [validate_file(path) for path in with_diagrams]
    errors = [error for report, _ in reports for error in report]
    total = sum(count for _, count in reports)

    for error in errors:
        print(error, file=sys.stderr)
    print(
        f"Mermaid theme standard: files {len(with_diagrams)} "
        f"diagrams {total} errors {len(errors)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
