#!/usr/bin/env python3
"""Apply the canonical light theme to SDD and primitive Mermaid blocks."""

from __future__ import annotations

import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
GITHUB_ROOT = ROOT / ".github"
BLOCK_PATTERNS = (
    re.compile(
        r"(?P<opening>```mermaid\n)(?P<body>.*?)(?P<closing>```)",
        re.DOTALL,
    ),
    re.compile(
        r"(?P<opening>~~~mermaid\n)(?P<body>.*?)(?P<closing>~~~)",
        re.DOTALL,
    ),
)
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
PALETTE = frozenset(
    {
        "classDef default fill:#FFFFFF,stroke:#777777,color:#222222",
        "classDef zone fill:#F2F2F2,stroke:#999999,color:#222222",
        "classDef external fill:#E8E8E8,stroke:#555555,color:#222222",
    }
)
DEFAULT_ROOTS = (
    ROOT / ".specs",
    GITHUB_ROOT / "skills",
    GITHUB_ROOT / "agents",
    GITHUB_ROOT / "prompts",
    GITHUB_ROOT / "instructions",
)


def diagram_kind(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("%%{"):
            return stripped.split()[0]
    return "?"


def format_block(match: re.Match[str]) -> tuple[str, bool]:
    body = match.group("body")
    if not body.startswith(f"{THEME_DIRECTIVE}\n"):
        body = f"{THEME_DIRECTIVE}\n{body}"
    if diagram_kind(body).startswith("stateDiagram"):
        body = "\n".join(
            line
            for line in body.splitlines()
            if line.strip() not in PALETTE
        )
        if match.group("body").endswith("\n"):
            body += "\n"
    formatted = (
        f"{match.group('opening')}{body}{match.group('closing')}"
    )
    return formatted, formatted != match.group(0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec-root",
        type=pathlib.Path,
        default=None,
        help=(
            "format only this root; by default formats .specs and canonical "
            ".github skills, agents, prompts, and instructions"
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report files that need formatting without changing them",
    )
    args = parser.parse_args(argv)

    changed: list[pathlib.Path] = []
    diagram_count = 0
    roots = list(
        [args.spec_root.resolve()]
        if args.spec_root is not None
        else DEFAULT_ROOTS
    )
    markdown_files = sorted(
        {
            path
            for root in roots
            if root.is_dir()
            for path in root.rglob("*.md")
        }
    )
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        formatted = text
        count = 0
        for pattern in BLOCK_PATTERNS:
            def replace(match: re.Match[str]) -> str:
                nonlocal count
                block, changed = format_block(match)
                count += int(changed)
                return block

            formatted = pattern.sub(replace, formatted)
        if not count:
            continue
        changed.append(path)
        diagram_count += count
        if not args.check:
            path.write_text(formatted, encoding="utf-8")

    mode = "need formatting" if args.check else "formatted"
    print(
        f"Mermaid theme formatter: files {len(changed)} "
        f"diagrams {diagram_count} {mode}"
    )
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
