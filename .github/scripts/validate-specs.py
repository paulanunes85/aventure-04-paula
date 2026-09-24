#!/usr/bin/env python3
"""Validate reference specification packages under .specs/.

Canonical gate for the 27-package reference program (.specs/001-*..specs/027-*).
Referenced by every package's TESTING.md as:

    python3 scripts/validate-specs.py --spec-root <root> --strict

Checks, per package directory (three-digit prefix + kebab slug):
  1. Artifact presence: the six authoritative markdown artifacts, three checkpoint YAMLs,
     and every contract the package is required to provide (see below).
     The ten-file portfolio is enforced separately by validate-spec-artifacts.py.
  2. Parse: every checkpoint/contract YAML and JSON parses and is non-empty.
  3. Identifier closure: REQ-/NFR- IDs defined in SPECIFICATION.md match the
     requirement maps in checkpoints/spec-to-plan.yaml and test-coverage.yaml
     bidirectionally; task IDs in TASKS.md match plan-to-tasks.yaml; test IDs
     in TESTING.md cover every test referenced by test-coverage.yaml.
  4. Checkpoint identity: feature.id equals the directory prefix and
     feature.slug equals the directory slug.
  5. Contract shape: run-api.openapi.yaml declares openapi/info/paths;
     run-state.schema.json is an object schema (properties/$defs/oneOf).
  6. Link sanity: Constitution links must resolve to the repository-root
     CONSTITUTION.md (../CONSTITUTION.md from inside a package; the
     constitution lives at .specs/CONSTITUTION.md since 2026-08-31).

Which contracts a package must provide
--------------------------------------
By default: both canonical contracts. That is what every package written
before this mechanism existed relies on, and it stays the default precisely
so nothing is relaxed by accident.

A package whose surface is not an HTTP service may say so, in
contracts/manifest.yaml, rather than commit a document describing an API it
has decided never to build. The manifest must account for every canonical
contract by name, and a 'not_applicable' declaration costs more than the file
it replaces: a reason in prose, the repository path of the artifact whose
shape justifies the claim, a DR-NNN decision that the package's own
DECISIONS.md records, and the absence of the waived file. A package may not
waive every contract; that would leave the gate asserting nothing about its
interface. An unreadable manifest is a hard failure, never a fallback to the
default -- a declaration nobody can read must not quietly relax a gate.

Warnings (fatal with --strict):
  - plan-to-tasks.yaml missing the 'gate' block (schema uniformity).
  - contracts/manifest.yaml missing 'schema_version' (schema uniformity).
  - mapping_status values other than 'complete'.

Exit codes: 0 ok, 1 validation errors (or warnings with --strict), 2 usage.
"""

import argparse
import json
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is a repo prerequisite
    print("FATAL: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

MARKDOWN_ARTIFACTS = (
    "ANALYSIS.md",
    "DECISIONS.md",
    "DESIGN.md",
    "SPECIFICATION.md",
    "TASKS.md",
    "TESTING.md",
)
CHECKPOINTS = ("spec-to-plan.yaml", "plan-to-tasks.yaml", "test-coverage.yaml")
CONTRACTS = ("run-api.openapi.yaml", "run-state.schema.json")
CONTRACT_MANIFEST = "manifest.yaml"
CONTRACT_STATUSES = ("provided", "not_applicable")
MANIFEST_ENTRY_KEYS = frozenset({"status", "reason", "evidence", "decision", "note"})
# A waiver has to argue. Anything shorter than this is a label, not a reason.
WAIVER_REASON_MIN = 80

REQ_ID = re.compile(r"\b(?:REQ|NFR)-\d{3}\b")
TASK_ID = re.compile(r"\bT\d{3}\b")
# A task is declared by its own heading, either as a checkbox row or as a
# section title. Prose that merely mentions an identifier -- a launcher stage
# such as `T034-004`, or an audit note naming the very finding this validator
# reports -- declares nothing, and reading it as a declaration invented tasks
# no plan could ever map.
TASK_DECLARATION = re.compile(
    r"^\s*(?:- \[[ x]\] \*\*|#{2,6} )(T\d{3})\b",
    re.MULTILINE,
)


def declared_task_ids(tasks_md: str) -> set[str]:
    """Task identifiers this TASKS.md actually declares."""
    declared = set(TASK_DECLARATION.findall(tasks_md))
    # Packages predating the heading conventions declare tasks in prose only.
    return declared or set(TASK_ID.findall(tasks_md))
TEST_ID = re.compile(r"\bTST-[A-Z]*\d{3}\b")
TEST_DECLARATION = re.compile(r"^\|\s*(TST-[A-Z]*\d{3})\s*\|", re.MULTILINE)


def declared_test_ids(testing_md: str) -> set[str]:
    """The tests a TESTING.md *declares*, not every id it mentions.

    A free-text scan admits any id a cross-reference names. 004 writes
    "registered as TST-S015 in spec 003" and 009 cites TST-C011 the same way,
    so both were accepted as locally defined and the closure check silently
    widened. A declaration is a catalog table row, the same shape
    `declared_task_ids` relies on for tasks; the prose scan stays as a
    fallback for packages that predate the convention.
    """
    declared = set(TEST_DECLARATION.findall(testing_md))
    return declared or set(TEST_ID.findall(testing_md))
PKG_DIR = re.compile(r"^(\d{3})-([a-z0-9-]+)$")
DECISION_ID = re.compile(r"DR-\d{3}")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load_yaml(path, errors):
    try:
        data = yaml.safe_load(read(path))
    except Exception as exc:  # noqa: BLE001 - report every parse failure
        errors.append(f"{path}: YAML parse error: {exc}")
        return None
    if not data:
        errors.append(f"{path}: empty YAML document")
        return None
    return data


def resolve_contract_set(pkg_path, name, pkg_id, pkg_slug, errors, warnings):
    """Return the set of canonical contracts this package must provide.

    Absent contracts/manifest.yaml the answer is both of them, unchanged.
    Returns None when the manifest exists but cannot be trusted, which stops
    validation of the package: a declaration nobody can read must not be
    treated as permission, and must not fall back to the default either,
    because then a typo would silently choose which rule applies.
    """
    manifest_path = os.path.join(pkg_path, "contracts", CONTRACT_MANIFEST)
    if not os.path.isfile(manifest_path):
        return set(CONTRACTS)

    label = f"{name}/contracts/{CONTRACT_MANIFEST}"
    doc = load_yaml(manifest_path, errors)
    if doc is None:
        return None
    if not isinstance(doc, dict):
        errors.append(f"{label}: top level is not a mapping")
        return None
    if "schema_version" not in doc:
        warnings.append(f"{label}: no 'schema_version' (schema uniformity)")

    feature = doc.get("feature") or {}
    if str(feature.get("id")) != pkg_id:
        errors.append(f"{label}: feature.id {feature.get('id')!r} != {pkg_id}")
    if feature.get("slug") != pkg_slug:
        errors.append(f"{label}: feature.slug {feature.get('slug')!r} != {pkg_slug}")

    declared = doc.get("contracts")
    if not isinstance(declared, dict):
        errors.append(f"{label}: 'contracts' must map each canonical contract file name to a declaration")
        return None
    unknown = sorted(set(declared) - set(CONTRACTS))
    if unknown:
        errors.append(f"{label}: declares unknown contract(s) {unknown}; the canonical set is {list(CONTRACTS)}")
    undeclared = sorted(set(CONTRACTS) - set(declared))
    if undeclared:
        errors.append(f"{label}: does not declare {undeclared}; a manifest must account for every canonical contract by name")
        return None

    decisions_path = os.path.join(pkg_path, "DECISIONS.md")
    decisions = read(decisions_path) if os.path.isfile(decisions_path) else ""
    # A package lives at <repo>/<spec-root>/<package>, in both the multi-package
    # and single-package invocations, so evidence paths are repository-relative.
    repo_root = os.path.abspath(os.path.join(pkg_path, os.pardir, os.pardir))

    required, waived = set(), set()
    for contract in CONTRACTS:
        entry = declared.get(contract)
        if not isinstance(entry, dict):
            errors.append(f"{label}: the {contract} declaration is not a mapping")
            continue
        stray = sorted(set(entry) - MANIFEST_ENTRY_KEYS)
        if stray:
            errors.append(f"{label}: the {contract} declaration has unknown key(s) {stray}; permitted: {sorted(MANIFEST_ENTRY_KEYS)}")
        status = entry.get("status")
        if status == "provided":
            required.add(contract)
            continue
        if status != "not_applicable":
            errors.append(f"{label}: {contract} status {status!r} is not one of {list(CONTRACT_STATUSES)}")
            continue

        waived.add(contract)
        if os.path.isfile(os.path.join(pkg_path, "contracts", contract)):
            errors.append(
                f"{label}: {contract} is declared not_applicable but the file is present; "
                "a package must not both disown a contract and ship it"
            )
        reason = entry.get("reason")
        if not isinstance(reason, str) or len(reason.strip()) < WAIVER_REASON_MIN:
            errors.append(
                f"{label}: {contract} needs a 'reason' of at least {WAIVER_REASON_MIN} characters "
                "saying why the surface it describes does not exist"
            )
        evidence = entry.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            errors.append(
                f"{label}: {contract} needs 'evidence': the repository path of the artifact "
                "whose shape makes the claim checkable"
            )
        elif os.path.isabs(evidence) or os.pardir in evidence.split("/"):
            errors.append(f"{label}: {contract} evidence {evidence!r} must be a repository-relative path that does not escape the repository")
        elif not os.path.exists(os.path.join(repo_root, evidence)):
            errors.append(f"{label}: {contract} evidence {evidence!r} does not exist")
        decision = entry.get("decision")
        if not isinstance(decision, str) or not DECISION_ID.fullmatch(decision.strip()):
            errors.append(f"{label}: {contract} needs 'decision': a DR-NNN identifier recorded in this package's DECISIONS.md")
        elif decision.strip() not in decisions:
            errors.append(f"{label}: {contract} cites decision {decision.strip()!r}, which {name}/DECISIONS.md does not record")

    if waived == set(CONTRACTS):
        errors.append(f"{label}: every canonical contract is waived, which leaves no interface contract for the gate to assert")
    return required


def validate_package(pkg_path, errors, warnings):
    name = os.path.basename(pkg_path.rstrip("/"))
    match = PKG_DIR.match(name)
    if not match:
        errors.append(f"{pkg_path}: directory name is not NNN-kebab-slug")
        return
    pkg_id, pkg_slug = match.groups()

    # 1. Presence. Which contracts count as required is the package's own
    #    declaration when it makes one, and both of them when it does not.
    required_contracts = resolve_contract_set(pkg_path, name, pkg_id, pkg_slug, errors, warnings)
    if required_contracts is None:
        return

    missing = [f for f in MARKDOWN_ARTIFACTS if not os.path.isfile(os.path.join(pkg_path, f))]
    missing += [
        os.path.join("checkpoints", f)
        for f in CHECKPOINTS
        if not os.path.isfile(os.path.join(pkg_path, "checkpoints", f))
    ]
    missing += [
        os.path.join("contracts", f)
        for f in CONTRACTS
        if f in required_contracts and not os.path.isfile(os.path.join(pkg_path, "contracts", f))
    ]
    if missing:
        errors.append(f"{name}: missing artifacts: {missing}")
        return

    reqs_md = read(os.path.join(pkg_path, "SPECIFICATION.md"))
    tasks_md = read(os.path.join(pkg_path, "TASKS.md"))
    testing_md = read(os.path.join(pkg_path, "TESTING.md"))

    req_ids = set(REQ_ID.findall(reqs_md))
    task_ids = declared_task_ids(tasks_md)
    test_ids = declared_test_ids(testing_md)
    if not req_ids:
        errors.append(f"{name}: SPECIFICATION.md defines no REQ-/NFR- identifiers")
    if not task_ids:
        errors.append(f"{name}: TASKS.md defines no T-number identifiers")
    if not test_ids:
        errors.append(f"{name}: TESTING.md defines no TST- identifiers")

    # 2. Parse checkpoints and contracts.
    sp = load_yaml(os.path.join(pkg_path, "checkpoints", "spec-to-plan.yaml"), errors)
    pt = load_yaml(os.path.join(pkg_path, "checkpoints", "plan-to-tasks.yaml"), errors)
    tc = load_yaml(os.path.join(pkg_path, "checkpoints", "test-coverage.yaml"), errors)
    api = schema = None
    if "run-api.openapi.yaml" in required_contracts:
        api = load_yaml(os.path.join(pkg_path, "contracts", "run-api.openapi.yaml"), errors)
        if api is None:
            return
    if "run-state.schema.json" in required_contracts:
        schema_path = os.path.join(pkg_path, "contracts", "run-state.schema.json")
        try:
            schema = json.loads(read(schema_path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{schema_path}: JSON parse error: {exc}")
            return
    if None in (sp, pt, tc):
        return

    # 4. Checkpoint identity.
    for label, doc in (("spec-to-plan", sp), ("plan-to-tasks", pt), ("test-coverage", tc)):
        feature = doc.get("feature") or {}
        if str(feature.get("id")) != pkg_id:
            errors.append(f"{name}/checkpoints/{label}.yaml: feature.id {feature.get('id')!r} != {pkg_id}")
        if feature.get("slug") != pkg_slug:
            errors.append(f"{name}/checkpoints/{label}.yaml: feature.slug {feature.get('slug')!r} != {pkg_slug}")
        status = (doc.get("checkpoint") or {}).get("mapping_status")
        if status != "complete":
            warnings.append(f"{name}/checkpoints/{label}.yaml: mapping_status is {status!r}, not 'complete'")

    # 5. Contract shape, for each contract the package actually provides.
    if api is not None:
        for key in ("openapi", "info", "paths"):
            if key not in api:
                errors.append(f"{name}/contracts/run-api.openapi.yaml: missing top-level '{key}'")
    if schema is not None and (
        not isinstance(schema, dict) or not any(k in schema for k in ("properties", "$defs", "oneOf"))
    ):
        errors.append(f"{name}/contracts/run-state.schema.json: not an object schema (properties/$defs/oneOf)")

    # 3. Identifier closure.
    sp_reqs = set((sp.get("requirements") or {}).keys())
    tc_reqs = set((tc.get("requirements") or {}).keys())
    pt_items = pt.get("plan_items") or {}
    pt_reqs, pt_tasks = set(), set()
    for item in pt_items.values():
        pt_reqs.update(item.get("requirements") or [])
        pt_tasks.update(item.get("tasks") or [])
    tc_tests = set()
    for entry in (tc.get("requirements") or {}).values():
        tc_tests.update(entry.get("tests") or [])

    closure = (
        ("spec-to-plan requirement not defined in SPECIFICATION.md", sp_reqs - req_ids),
        ("requirement missing from spec-to-plan checkpoint", req_ids - sp_reqs),
        ("requirement missing from test-coverage checkpoint", req_ids - tc_reqs),
        ("test-coverage requirement not defined in SPECIFICATION.md", tc_reqs - req_ids),
        ("plan-to-tasks requirement not defined in SPECIFICATION.md", pt_reqs - req_ids),
        ("plan-to-tasks task not defined in TASKS.md", pt_tasks - task_ids),
        ("task never mapped by plan-to-tasks", task_ids - pt_tasks),
        ("test-coverage test not defined in TESTING.md", tc_tests - test_ids),
    )
    for label, diff in closure:
        if diff:
            sample = sorted(diff)[:10]
            errors.append(f"{name}: {label}: {sample}{' ...' if len(diff) > 10 else ''} ({len(diff)})")

    # 6. Constitution links must escape .specs/ to the repository root.
    for artifact in MARKDOWN_ARTIFACTS:
        text = read(os.path.join(pkg_path, artifact))
        if "](../../CONSTITUTION.md)" in text:
            errors.append(f"{name}/{artifact}: Constitution link '../../CONSTITUTION.md' escapes .specs/; the constitution lives at .specs/CONSTITUTION.md -- use ../CONSTITUTION.md")

    # Warning: schema uniformity for the gate block.
    if "gate" not in pt:
        warnings.append(f"{name}/checkpoints/plan-to-tasks.yaml: no 'gate' block (schema uniformity)")


def main(argv):
    parser = argparse.ArgumentParser(description="Validate reference spec packages.")
    parser.add_argument("--spec-root", default=".specs", help="Directory containing NNN-slug packages (default: specs)")
    parser.add_argument("--package", help="Validate only the package whose ID or full name matches")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args(argv[1:])

    root = args.spec_root
    if not os.path.isdir(root):
        print(f"FATAL: spec root not found: {root}", file=sys.stderr)
        return 2

    # Ledger-only directories: historical evidence that never was a full
    # package. 013-multi-repository-catalog-topology holds CATALOG_UPGRADES.md
    # (the templates-ref upgrade ledger two spec-006 oracles depend on); the
    # legacy package around it was retired in the 2026-08-31 cleanup.
    ledger_only = {
        "013-multi-repository-catalog-topology",
        # Historical evidence packages from the AEG-era tree, restored
        # 2026-08-31 because CI gates and eleven oracles read them (task
        # graph, import map, cross-analysis). They are records, not
        # canonical packages.
        "005-aeg-open-horizons-azure-dev-pilot",
        "006-terraform-adoption-live-azure",
    }
    packages = sorted(
        os.path.join(root, entry)
        for entry in os.listdir(root)
        if PKG_DIR.match(entry)
        and entry not in ledger_only
        and os.path.isdir(os.path.join(root, entry))
    )
    # A root that is itself one package (contains SPECIFICATION.md directly).
    if not packages and os.path.isfile(os.path.join(root, "SPECIFICATION.md")):
        packages = [root]
    if args.package:
        packages = [p for p in packages if args.package in os.path.basename(p)]
    if not packages:
        print(f"FATAL: no spec packages found under {root}", file=sys.stderr)
        return 2

    errors, warnings = [], []
    for pkg in packages:
        validate_package(pkg, errors, warnings)

    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"ERROR {error}")

    failed = bool(errors) or (args.strict and bool(warnings))
    print(
        f"{'FAIL' if failed else 'OK'}  packages={len(packages)} "
        f"errors={len(errors)} warnings={len(warnings)} strict={args.strict}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
