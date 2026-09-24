#!/usr/bin/env python3
"""Audit SDD reference integrity, not test execution or live acceptance."""

from __future__ import annotations

import argparse
import collections
import dataclasses
import datetime
import fnmatch
import glob
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
from typing import Iterable
from urllib.parse import unquote, urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCAL_REPOSITORY = "Ohorizons/ohorizons-demo"
FROZEN = {
    "005-aeg-open-horizons-azure-dev-pilot",
    "006-terraform-adoption-live-azure",
}
TASK = re.compile(
    r"^-\s+\[(?P<mark>[ xX])\]\s+\*\*(?P<id>T\d{3})"
    r"(?P<meta>.*?)\*\*(?P<body>.*?)"
    r"(?=^-\s+\[[ xX]\]\s+\*\*T\d{3}|^#{1,6}\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
BACKTICK = re.compile(r"`([^`\n]+)`")
TEST_ID = re.compile(r"\bTST-[A-Z]*\d{3}\b")
# Ranges are written three ways in the corpus: ".." (282), an en dash (96)
# and a hyphen (19), and the tail is often abbreviated -- "TST-R015-R019".
TEST_RANGE = re.compile(
    r"\b(TST-[A-Z]*)(\d{3})\s*(?:\.\.|[\u2013\u2014-])\s*"
    r"(TST-[A-Z]*|[A-Z]*)(\d{3})\b"
)
TEST_ROW = re.compile(
    r"^\|\s*(?P<id>TST-[A-Z]*\d{3})\s*\|(?P<body>.+)$",
    re.MULTILINE,
)
PACKAGE_LOCAL = re.compile(
    r"^(?:checkpoints|contracts|evidence)/|^(?:ANALYSIS|CHECKLIST|"
    r"CROSS_ANALYSIS|DECISIONS|DESIGN|SOURCE_TRACEABILITY|SPECIFICATION|"
    r"TASKS|TESTING|VERIFICATION|REHEARSAL_RUNBOOK)\.md$"
)
REPOSITORY = re.compile(r"^(Ohorizons/[\w.-]+)(?:@([\w.-]+))?$")
EXTERNAL_PATH = re.compile(r"^(Ohorizons/[\w.-]+)(?:@([\w.-]+))?/(.+)$")
SHA = re.compile(r"^[a-fA-F0-9]{40}$")
FILE_NAME = re.compile(
    r"(?:\.(?:pyi?|md|ya?ml|json|[cm]?js|jsx|tsx?|sh|bash|go|tf|tfvars|txt|"
    r"rego|hcl|bicep|sql|toml|lock|example)|(?:^|/)Dockerfile)$"
)
SCOPED_PATH = re.compile(
    r"(?<![\w./-])(?:\.\./)*(?:tests|scripts|backstage|harness|terraform|"
    r"\.github|\.specs)/[^\s`'\"()|,;:]+"
)
PROTOCOL_METHODS = frozenset({
    "tools/list", "tools/call", "resources/list", "resources/read",
    "resources/templates/list", "prompts/list", "prompts/get",
})


@dataclasses.dataclass(frozen=True)
class Finding:
    package: str
    task: str
    rule: str
    detail: str

    def render(self) -> str:
        return f"{self.package}/{self.task}: [{self.rule}] {self.detail}"


@dataclasses.dataclass(frozen=True)
class Reference:
    path: str
    repository: str = LOCAL_REPOSITORY
    revision: str | None = None
    candidates: tuple[str, ...] = ()

    @property
    def local(self) -> bool:
        return self.repository == LOCAL_REPOSITORY and self.revision is None

    def render(self) -> str:
        if not self.local:
            return f"{self.repository}@{self.revision or 'UNPINNED'}:{self.path}"
        path = pathlib.Path(self.path)
        return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def normalize_reference(
    package: pathlib.Path,
    value: str,
    owner: tuple[str, str | None] | None = None,
    *,
    file_context: bool = False,
) -> Reference | None:
    candidate = value.strip().rstrip(".,;:")
    if candidate.startswith(("https://", "http://")):
        url = urlparse(candidate)
        parts = url.path.strip("/").split("/", 4)
        if url.hostname != "github.com" or len(parts) != 5 or parts[2] not in {"blob", "tree"}:
            return None
        return Reference(unquote(parts[4]), "/".join(parts[:2]), parts[3])
    candidate = candidate.split(":", 1)[0]
    candidate = candidate.split("#", 1)[0]
    if re.fullmatch(r"[A-Z]\w*(?:\.\w+)+(?:/\.\w+)+", candidate):
        return None
    external = EXTERNAL_PATH.fullmatch(candidate)
    if external:
        candidate, owner = external[3], (external[1], external[2])
    if candidate in PROTOCOL_METHODS and not file_context:
        return None
    if not file_context and owner is None and re.fullmatch(r"\d+/\d+", value.strip()):
        return None
    if candidate.startswith("/") and not candidate.startswith(str(ROOT)) and not FILE_NAME.search(candidate):
        return None
    if " " in candidate or not (
        "/" in candidate or FILE_NAME.search(candidate)
        or candidate in {".dockerignore", ".gitignore", ".env.example"}
    ):
        return None
    if owner and owner != (LOCAL_REPOSITORY, None):
        return Reference(candidate.removeprefix("./"), *owner)
    if owner == (LOCAL_REPOSITORY, None):
        path = ROOT / candidate.removeprefix("./")
    elif PACKAGE_LOCAL.match(candidate):
        path = package / candidate
    elif candidate.startswith("../"):
        path = package / candidate
    else:
        path = ROOT / candidate.removeprefix("./")
    # Never inspect absolute host examples or parent escapes from documentation.
    if path.is_absolute() and not path.is_relative_to(ROOT):
        return Reference(str(path))
    return Reference(os.path.abspath(path))


def file_fields(body: str) -> str:
    """Keep wrapped Files fields, but never consume Acceptance or Evidence."""
    lines: list[str] = []
    in_files = False
    for line in body.splitlines():
        if re.match(r"^\s*-\s+Files?:", line, re.IGNORECASE):
            in_files = True
        elif re.match(r"^\s*[-#]", line):
            in_files = False
        if in_files:
            lines.append(line)
    return "\n".join(lines)


def references(
    package: pathlib.Path, text: str, *, file_context: bool = False
) -> list[Reference]:
    result: list[Reference] = []
    owner: tuple[str, str | None] | None = None
    pins = re.findall(r"\b(?:commit|pin|revision|ref)\s*[:=]?\s*`([a-fA-F0-9]{40})`", text, re.IGNORECASE)
    pin = pins[0] if len(set(pins)) == 1 else None
    for token in BACKTICK.finditer(text):
        value = token[1]
        repository = REPOSITORY.fullmatch(value.strip())
        if repository:
            owner = (repository[1], repository[2] or pin)
            continue
        # A comma inside a brace glob is not a Markdown list separator.
        for candidate in re.split(r",\s*(?![^{}]*\})|;\s*", value):
            numeric_source = re.fullmatch(r"\d+/\d+", candidate.strip()) and re.search(
                r"\b(?:Evidence|Sources?|Files?)\s*:\s*(?:`[^`]+`[\s,;]*)*$",
                text[:token.start()],
                re.IGNORECASE,
            )
            reference = normalize_reference(
                package, candidate, owner,
                file_context=file_context or bool(numeric_source),
            )
            if reference is not None:
                result.append(reference)
            elif re.match(r"^(?:python[\d.]*|bash|sh|node|\./scripts/|scripts/)", candidate):
                try:
                    arguments = shlex.split(candidate)
                except ValueError:
                    continue
                for argument in arguments:
                    if argument.startswith("-") or "=" in argument:
                        continue
                    reference = normalize_reference(
                        package, argument, owner, file_context=file_context
                    )
                    if reference is not None:
                        result.append(reference)
    return list(dict.fromkeys(result))


def task_file_references(package: pathlib.Path, body: str) -> list[Reference]:
    return references(package, file_fields(body), file_context=True)


def declared_sources(package: pathlib.Path, text: str) -> tuple[dict, dict]:
    """Resolve short test names only within the document's declared file scope."""
    files: set[pathlib.Path] = set()
    for token in SCOPED_PATH.findall(text):
        reference = normalize_reference(package, token)
        if reference is None:
            continue
        path = pathlib.Path(reference.path)
        if not path.is_relative_to(ROOT):
            continue
        if path.is_dir() and "tests" in path.parts:
            files.update(path.rglob("*.py"))
        else:
            files.add(path)
    by_name: dict[str, list[Reference]] = {}
    by_symbol: dict[str, list[Reference]] = {}
    for path in sorted(files):
        reference = Reference(str(path))
        by_name.setdefault(path.name, []).append(reference)
        if path.suffix == ".py" and path.is_file() and path.resolve().is_relative_to(ROOT):
            source = path.read_text(encoding="utf-8", errors="replace")
            for symbol in re.findall(r"^\s*(?:async\s+)?(?:def|class)\s+(\w+)", source, re.MULTILINE):
                by_symbol.setdefault(symbol, []).append(reference)
    return by_name, by_symbol


def resolve_short_names(refs: list[Reference], names: dict) -> list[Reference]:
    result = []
    for reference in refs:
        path = pathlib.Path(reference.path)
        if reference.local and path.is_relative_to(ROOT) and not path.exists():
            suffix = path.relative_to(ROOT).as_posix()
            aliases = [
                alias for alias in names.get(path.name, [])
                if alias.path != reference.path and alias.path.endswith("/" + suffix)
            ]
            if len(aliases) == 1:
                reference = aliases[0]
            elif len(aliases) > 1:
                reference = dataclasses.replace(
                    reference, candidates=tuple(alias.render() for alias in aliases)
                )
        result.append(reference)
    return list(dict.fromkeys(result))


def before_oracle(text: str) -> str:
    quoted = False
    for index, character in enumerate(text):
        if character == "`":
            quoted = not quoted
        elif (
            character == ":" and not quoted
            and re.search(r"`[^`]+`\s*$", text[:index])
        ):
            evidence = re.search(
                r"\b(?:Evidence|Sources?|Files?)\s*:\s*(.+)",
                text[index + 1:],
                re.IGNORECASE,
            )
            return text[:index] + (" " + evidence[0] if evidence else "")
    return text


def catalog_blocks(testing: str) -> list[str]:
    """Keep contiguous tables and exclude fenced authoring examples."""
    blocks: list[str] = []
    lines: list[str] = []
    fence = ""
    for line in testing.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if (
                marker and marker[1][0] == fence[0]
                and len(marker[1]) >= len(fence) and not marker[2].strip()
            ):
                fence = ""
            continue
        if marker and (marker[1][0] != "`" or "`" not in marker[2]):
            fence = marker[1]
        elif re.match(r"^ {0,3}\|", line):
            lines.append(line.lstrip())
            continue
        if lines:
            blocks.append("\n".join(lines))
            lines = []
    if lines:
        blocks.append("\n".join(lines))
    return blocks


def catalog_rows(testing: str) -> list[re.Match]:
    return [
        match for block in catalog_blocks(testing)
        for match in TEST_ROW.finditer(block)
        if re.search(
            r"\b(?:REQ|NFR)-\d{3}\b|^\s*(?:Unit|Contract|Integration|"
            r"Security|Runtime|Property)\s*\|",
            match.group("body"),
        )
    ]


HEADER_SEPARATOR = re.compile(r"^\|?(?:\s*:?-{2,}:?\s*\|)*\s*:?-{2,}:?\s*\|?$")


def split_row_cells(line: str) -> list[str]:
    """Split a complete row without shifting empty or code-span cells."""
    cells: list[str] = []
    current: list[str] = []
    fence = 0
    index = 0
    while index < len(line):
        character = line[index]
        if character == "\\" and not fence:
            current.append(line[index:index + 2])
            index += 2
            continue
        if character == "`":
            end = index + 1
            while end < len(line) and line[end] == "`":
                end += 1
            width = end - index
            if not fence:
                fence = width
            elif fence == width:
                fence = 0
            current.append(line[index:end])
            index = end
            continue
        if character == "|" and not fence:
            cells.append("".join(current))
            current = []
        else:
            current.append(character)
        index += 1
    cells.append("".join(current))
    if line.lstrip().startswith("|") and cells[0].strip() == "":
        cells.pop(0)
    if cells and line.rstrip().endswith("|") and cells[-1].strip() == "":
        cells.pop()
    return cells


def table_header(block: str) -> list[str] | None:
    """Read column names, retaining a conservative fallback for headerless tables."""
    lines = block.splitlines()
    for index in range(len(lines) - 1):
        header, separator = lines[index], lines[index + 1]
        if not header.strip().startswith("|"):
            continue
        if TEST_ID.search(header):
            return None
        if HEADER_SEPARATOR.match(separator.strip()):
            return [cell.strip().strip("`*_").strip() for cell in split_row_cells(header)]
        return None
    return None


def file_column_offsets(header: list[str] | None) -> set[int] | None:
    """Select source columns after the ID; retain all cells without a header."""
    if header is None:
        return None
    return {
        offset for offset, name in enumerate(header[1:])
        if re.search(
            r"file|source|evidence|owner|repository|revision|commit|"
            r"\b(?:pin|ref|command|executable|implementation)\b|^tests?$",
            name,
            re.IGNORECASE,
        )
    }


SOURCE_LABEL = re.compile(r"\b(?:Evidence|Sources?|Files?)\s*:", re.IGNORECASE)


def source_labels(text: str) -> list[re.Match]:
    """Labels inside a quoted oracle literal do not declare source evidence."""
    quoted = list(BACKTICK.finditer(text))
    return [
        match for match in SOURCE_LABEL.finditer(text)
        if not any(token.start() <= match.start() < token.end() for token in quoted)
    ]


def primary_source_text(text: str, *, include_unlabeled: bool) -> str:
    labels = source_labels(text)
    parts = []
    if include_unlabeled:
        parts.append(text[:labels[0].start()] if labels else text)
    for index, label in enumerate(labels):
        if label[0].lower().startswith("evidence"):
            continue
        end = labels[index + 1].start() if index + 1 < len(labels) else len(text)
        parts.append(text[label.start():end])
    return " | ".join(before_oracle(part) for part in parts)


def test_catalog(
    testing: str, package: pathlib.Path, tasks: str = ""
) -> dict[str, tuple[Reference, ...]]:
    catalog: dict[str, tuple[Reference, ...]] = {}
    names, symbols = declared_sources(package, testing + "\n" + tasks)
    def resolve_cells(text: str, previous: list[Reference]) -> list[Reference]:
        refs = resolve_short_names(references(package, text), names)
        for value in BACKTICK.findall(text):
            if value.startswith("..::"):
                refs.extend(previous)
            elif value.strip() in symbols:
                refs.extend(symbols[value.strip()])
            elif re.search(r"\bmodule\s+`" + re.escape(value) + r"`", text):
                refs.extend(names.get(value + ".py", []))
        return list(dict.fromkeys(refs))

    for block in catalog_blocks(testing):
        header = table_header(block)
        file_offsets = file_column_offsets(header)
        previous: list[Reference] = []
        for match in catalog_rows(block):
            # Execution-result tables reuse IDs; they must not overwrite the catalog.
            cells = split_row_cells(match.group(0))[1:]
            metadata: list[str] = []
            selected: list[str] = []
            primary: list[str] = []
            for offset, cell in enumerate(cells):
                name = header[offset + 1] if header and offset + 1 < len(header) else ""
                if re.search(
                    r"owner|repository|revision|commit|\b(?:pin|ref)\b",
                    name, re.IGNORECASE,
                ) and not re.search(r"file|evidence|oracle", name, re.IGNORECASE):
                    if re.search(r"revision|commit|\b(?:pin|ref)\b", name, re.IGNORECASE):
                        cell = f"revision: {cell}"
                    metadata.append(cell)
                    continue
                is_source_column = file_offsets is None or offset in file_offsets
                if is_source_column:
                    selected.append(before_oracle(cell))
                else:
                    labels = source_labels(cell)
                    if labels:
                        selected.append(before_oracle(cell[labels[0].start():]))
                primary.append(primary_source_text(
                    cell,
                    include_unlabeled=is_source_column and (
                        not re.search(r"evidence", name, re.IGNORECASE)
                        or bool(re.search(r"file|source|oracle", name, re.IGNORECASE))
                    ),
                ))
            context = " | ".join(metadata)
            refs = resolve_cells(context + " | " + " | ".join(selected), previous)
            primary_refs = resolve_cells(context + " | " + " | ".join(primary), previous)
            catalog[match.group("id")] = tuple(
                dict.fromkeys((*catalog.get(match.group("id"), ()), *refs))
            )
            if primary_refs:
                previous = primary_refs
    return catalog


def test_ids(text: str) -> set[str]:
    result = set(TEST_ID.findall(text))
    for prefix, start, end_prefix, end in TEST_RANGE.findall(text):
        # An abbreviated tail ("TST-R015-R019") carries no "TST-" and may carry
        # no letters at all; normalise it to the head prefix before comparing,
        # or every en-dash range in the corpus is silently dropped.
        tail = end_prefix or prefix
        if not tail.startswith("TST-"):
            tail = "TST-" + tail
        if prefix == tail and int(start) <= int(end):
            result.update(
                f"{prefix}{number:03}"
                for number in range(int(start), int(end) + 1)
            )
    return result


def mapped_tests(
    text: str, task: str, metadata: str, include_plan: bool = True
) -> set[str]:
    plan = re.search(r"\[Plan:(P[\d.]+)\]", metadata)
    result: set[str] = set()
    for line in text.splitlines():
        cells = line.strip().split("|")
        if len(cells) < 4:
            continue
        key = cells[1]
        if re.search(rf"\b{task}\b", key) or (
            include_plan and plan and key.strip() == plan[1]
        ):
            result.update(test_ids("|".join(cells[2:])))
    return result


def expand_braces(pattern: str) -> list[str]:
    match = re.search(r"\{([^{}]+)\}", pattern)
    if not match:
        return [pattern]
    return [
        expanded
        for option in match[1].split(",")
        for expanded in expand_braces(
            pattern[:match.start()] + option + pattern[match.end():]
        )
    ]


class Resolver:
    """Local existence or pinned Git tree evidence; neither executes a test."""

    def __init__(self, online: bool = False) -> None:
        self.online = online
        self.trees: dict[tuple[str, str], dict] = {}

    def check(self, reference: Reference) -> dict:
        result = dataclasses.asdict(reference)
        result["reference"] = reference.render()
        result["matches"] = []
        if any(token in reference.path for token in ("<", ">")):
            return {**result, "status": "unresolved", "detail": "placeholder path"}
        patterns = expand_braces(reference.path)
        if reference.local:
            path = pathlib.Path(reference.path)
            if not path.is_relative_to(ROOT) or ".." in path.parts:
                return {
                    **result, "status": "unresolved",
                    "detail": "host path outside repository; not inspected",
                }
            if reference.candidates:
                return {
                    **result, "status": "unresolved",
                    "detail": "multiple declared source candidates; qualify the reference",
                }
            if (
                path.parent == ROOT
                and not glob.has_magic(reference.path)
                and not path.exists()
            ):
                return {
                    **result, "status": "unresolved",
                    "detail": "short filename has no unique declared source",
                }
            paths = sorted({
                path for pattern in patterns
                for path in glob.glob(pattern, recursive=True)
                if pathlib.Path(path).resolve().is_relative_to(ROOT)
                and pathlib.Path(path).exists()
            })
            result["matches"] = [
                str(pathlib.Path(path).relative_to(ROOT))
                if pathlib.Path(path).is_relative_to(ROOT) else path
                for path in paths
            ]
            return {**result, "status": "present" if paths else "missing"}
        if not reference.revision or not SHA.fullmatch(reference.revision):
            return {
                **result, "status": "unverified",
                "detail": "external reference is not pinned to a full commit SHA",
            }
        if not self.online:
            return {
                **result, "status": "unverified",
                "detail": "pinned external source requires --online verification",
            }
        key = (reference.repository, reference.revision)
        if key not in self.trees:
            endpoint = (
                f"repos/{reference.repository}/git/trees/"
                f"{reference.revision}?recursive=1"
            )
            try:
                response = subprocess.run(
                    ["gh", "api", endpoint], check=True, capture_output=True,
                    text=True, timeout=60,
                )
                tree = json.loads(response.stdout)
                if (
                    tree.get("truncated")
                    or tree.get("sha") != reference.revision
                    or not isinstance(tree.get("tree"), list)
                ):
                    raise ValueError("incomplete or mismatched Git tree")
                self.trees[key] = {
                    "tree": tree["tree"],
                    "source": f"https://api.github.com/{endpoint}",
                }
            except (OSError, subprocess.SubprocessError, ValueError):
                self.trees[key] = {"error": "pinned Git tree could not be verified"}
        tree = self.trees[key]
        if "error" in tree:
            return {**result, "status": "unverified", "detail": tree["error"]}
        result["source"] = tree["source"]
        result["matches"] = sorted({
            item["path"] for item in tree["tree"]
            if item.get("type") in {"blob", "tree"}
            and any(
                fnmatch.fnmatchcase(item["path"], pattern.rstrip("/"))
                for pattern in patterns
            )
        })
        return {**result, "status": "present" if result["matches"] else "missing"}


def package_report(package: pathlib.Path, resolver: Resolver) -> dict:
    tasks_path = package / "TASKS.md"
    testing_path = package / "TESTING.md"
    tasks_text = tasks_path.read_text(encoding="utf-8")
    testing_text = (
        testing_path.read_text(encoding="utf-8")
        if testing_path.is_file() else ""
    )
    tests = test_catalog(testing_text, package, tasks_text)
    catalog_counts = collections.Counter(
        match.group("id") for match in catalog_rows(testing_text)
    )
    names, _ = declared_sources(package, tasks_text)
    findings: list[Finding] = []
    records = []
    for match in TASK.finditer(tasks_text):
        task_id = match.group("id")
        checked = match.group("mark").lower() == "x"
        block = match.group(0)
        task_findings: list[Finding] = []
        file_lines = file_fields(block)
        if checked and re.search(
            r"\[(?:planejado|planned)(?:[^\]]*)\]",
            file_lines,
            re.IGNORECASE,
        ):
            task_findings.append(
                Finding(
                    package.name,
                    task_id,
                    "completed-planned-surface",
                    "checked task still labels an implementation or test surface as planned",
                )
            )
        file_references = resolve_short_names(
            task_file_references(package, match.group("body")), names
        )
        if checked and not file_references:
            task_findings.append(
                Finding(
                    package.name,
                    task_id,
                    "completed-without-files",
                    "checked task names no resolvable change surface",
                )
            )
        checks = [
            {"kind": "task", **resolver.check(reference)}
            for reference in file_references
        ]
        direct_tests = test_ids(block) | mapped_tests(
            tasks_text, task_id, match.group("meta"), include_plan=False
        )
        named_tests = test_ids(block) | mapped_tests(
            tasks_text, task_id, match.group("meta")
        )
        for test_id in sorted(named_tests):
            if test_id not in tests:
                if checked:
                    task_findings.append(
                        Finding(
                            package.name,
                            task_id,
                            "missing-test-catalog-row",
                            test_id,
                        )
                    )
                continue
            if checked and catalog_counts[test_id] > 1:
                task_findings.append(Finding(
                    package.name, task_id, "ambiguous-test-catalog-id",
                    f"{test_id}: {catalog_counts[test_id]} active catalog rows; all references retained",
                ))
            if checked and not tests[test_id]:
                task_findings.append(Finding(
                    package.name, task_id, "test-without-files", test_id
                ))
            for reference in tests[test_id]:
                declared = [
                    candidate for candidate in file_references
                    if candidate.render() in reference.candidates
                ]
                if len(declared) == 1:
                    reference = declared[0]
                checks.append({
                    "kind": "test", "test": test_id,
                    "test_scope": "task" if test_id in direct_tests else "plan_context",
                    **resolver.check(reference),
                })
        if checked:
            for check in checks:
                if check["status"] != "present":
                    rule = (
                        f"missing-{check['kind']}-file" if check["status"] == "missing"
                        else f"{check['status']}-{check['kind']}-reference"
                    )
                    detail = (
                        f"{check.get('test', '')}: {check['reference']}"
                    ).lstrip(": ")
                    if check.get("detail"):
                        detail += f" ({check['detail']})"
                    task_findings.append(Finding(package.name, task_id, rule, detail))
        state = "open"
        if checked:
            state = (
                "checked_with_reference_findings"
                if task_findings else "checked_reference_only"
            )
        records.append({
            "id": task_id,
            "checked": checked,
            "state": state,
            "description": " ".join(match.group("body").split("\n  -", 1)[0].split()),
            "acceptance": [
                line.strip() for line in block.splitlines()
                if re.match(
                    r"^\s+-\s+(Acceptance|Audit status|Audit evidence|"
                    r"Remaining acceptance):", line
                )
            ],
            "owner_repositories": sorted({
                check["repository"] for check in checks
            }) or [LOCAL_REPOSITORY],
            "tests": sorted(named_tests),
            "test_origins": {
                test_id: "task" if test_id in direct_tests else "plan_context"
                for test_id in sorted(named_tests)
            },
            "reference_checks": checks,
            "findings": [dataclasses.asdict(finding) for finding in task_findings],
            "execution_verified_by_audit": False,
        })
        findings.extend(task_findings)
    return {
        "package": package.name,
        "tasks": records,
        "findings": [dataclasses.asdict(finding) for finding in findings],
    }


def audit_package(
    package: pathlib.Path, resolver: Resolver | None = None
) -> list[Finding]:
    report = package_report(package, resolver or Resolver())
    return [Finding(**finding) for finding in report["findings"]]


def packages(spec_root: pathlib.Path, selected: Iterable[str]) -> list[pathlib.Path]:
    wanted = set(selected)
    found = [
        path
        for path in sorted(spec_root.glob("[0-9][0-9][0-9]-*"))
        if path.is_dir() and path.name not in FROZEN and (path / "TASKS.md").is_file()
    ]
    if not wanted:
        return found
    return [
        path
        for path in found
        if path.name in wanted or path.name.split("-", 1)[0] in wanted
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-root", type=pathlib.Path, default=ROOT / ".specs")
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument(
        "--online", action="store_true",
        help="Verify pinned external paths using read-only gh Git tree requests.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    arguments = parser.parse_args(argv)
    selected = packages(arguments.spec_root.resolve(), arguments.package)
    if not selected:
        parser.error("no canonical task packages matched; refusing an empty audit")
    resolver = Resolver(online=arguments.online)
    reports = [package_report(package, resolver) for package in selected]
    findings = [
        Finding(**finding)
        for report in reports for finding in report["findings"]
    ]
    tasks = [task for report in reports for task in report["tasks"]]
    summary = {
        "canonical_packages": len(selected), "canonical_tasks": len(tasks),
        "checked_tasks": sum(task["checked"] for task in tasks),
        "open_tasks": sum(not task["checked"] for task in tasks),
        "checked_tasks_with_findings": sum(bool(task["findings"]) for task in tasks),
        "findings": len(findings),
    }
    if arguments.format == "json":
        print(json.dumps({
            "schema_version": 1,
            "audited_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "scope": "Canonical task reference integrity; presence is not execution, approval, or live acceptance.",
            "summary": summary,
            "historical_pilot_graphs_excluded": [
                name for name in sorted(FROZEN) if (arguments.spec_root / name).is_dir()
            ],
            "packages": reports,
        }, indent=2))
    else:
        for finding in findings:
            print(f"ERROR: {finding.render()}", file=sys.stderr)
        print(
            f"Task evidence audit: canonical packages {len(selected)}, tasks {len(tasks)}, "
            f"checked {summary['checked_tasks']}, open {summary['open_tasks']}, "
            f"findings {len(findings)} (reference integrity only; no execution verified)"
        )
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
