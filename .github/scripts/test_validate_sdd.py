"""Testes do validador SDD nativo (.github/scripts/validate-sdd.py)."""

import importlib.util
import io
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "validate-sdd.py"
SPEC = importlib.util.spec_from_file_location("validate_sdd", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
sdd = importlib.util.module_from_spec(SPEC)
sys.modules["validate_sdd"] = sdd
SPEC.loader.exec_module(sdd)

THEME = sdd.THEME
PALETTE = "\n".join(sdd.PALETTE)
SOURCE = "# Requisitos\n\n- RF-01: ecoar.\n- RNF-01: Node.js.\n"
IDS = "REQ-001, NFR-001"
REQUIREMENTS = (
    "### REQ-001: Ecoar\norigem: SRC-001 (requisitos/req.md#L3)\n\n"
    "- IDs da fonte: RF-01\n- Padrão: orientado a evento\n"
    "- Prioridade: P0\n- Status: Proposto\n\n"
    "> Quando o aluno informar, a Sala deve ecoar.\n\n"
    "- AC-REQ-001-01: Dado x, Quando y, Então z.\n\n"
    "**Verificação**\n\n- teste: t1\n\n"
    "### NFR-001: Node\norigem: SRC-001 (requisitos/req.md#L4)\n\n"
    "- IDs da fonte: RNF-01\n- Padrão: ubíquo\n"
    "- Prioridade: P0\n- Status: Proposto\n\n"
    "> A Sala deve executar em Node.js.\n\n"
    "- AC-NFR-001-01: Dado x, Quando y, Então z.\n"
    "- Envelope de medição: NFRD.md NFR-001\n\n"
    "**Verificação**\n\n- inspeção: i1\n"
)
BODIES = {
    ("SPECIFICATION.md", "requisitos"): REQUIREMENTS,
    ("SOURCE_TRACEABILITY.md", "registro de fontes"): (
        "| ID | Classe | Local |\n| --- | --- | --- |\n"
        "| SRC-001 | repositório | `requisitos/req.md` |\n"
    ),
    ("SOURCE_TRACEABILITY.md", "matriz de rastreabilidade"): IDS,
    ("FRD.md", "requisitos funcionais por domínio"): "| REQ-001 |\n",
    ("NFRD.md", "requisitos de qualidade"): "### NFR-001: Node\n",
    ("DESIGN.md", "visão de entrega e rastreabilidade"): IDS,
    ("TESTING.md", "mapa de testes"): IDS,
    ("CROSS_ANALYSIS.md", "análise cruzada"): IDS,
    ("VERIFICATION.md", "verificações planejadas"): IDS,
    ("TDD.md", "ciclos por critério de aceite"):
        "AC-REQ-001-01 e AC-NFR-001-01",
    ("TASKS.md", "grafo de dependências"): (
        f"```mermaid\n{THEME}\nflowchart TD\n{PALETTE}\n"
        "  T001 --> T002\n```\n"
    ),
    ("TASKS.md", "registro de execução"): (
        "Tarefas concluídas: **0 de 2**.\n"
        "Marcadas como concluídas pela verificação: nenhuma\n"
    ),
}
TASK_LIST = (
    "## Fase 1\n\n"
    "- [ ] **T001 [S] [Plano:P1.1] RED** Teste. Rastreia REQ-001.\n"
    "  - Aceite: falha.\n\n"
    "- [ ] **T002 [S] [Plano:P1.1] GREEN** Código. Rastreia NFR-001.\n"
    "  - Depende de: T001.\n"
)
CHECKPOINTS = {
    "spec-to-plan.yaml": f"feature: {{id: \"001\"}}\n# {IDS}\n",
    "plan-to-tasks.yaml": "feature: {id: \"001\"}\n# T001 T002\n",
    "test-coverage.yaml": f"feature: {{id: \"001\"}}\n# {IDS}\n",
}


def document(name: str, status: str = "Rascunho") -> str:
    parts = [f"# {name}\n\n- Funcionalidade: 001-demo\n"
             f"- Status: {status}\n- Constituição: CONSTITUTION.md\n\n"]
    if status == "Não iniciado":
        return parts[0]
    for names in sdd.SECTIONS[name]:
        body = BODIES.get((name, names[0]), "NÃO APLICÁVEL: fixture.")
        parts.append(f"## {names[0]}\n\n{body}\n\n")
    if name == "TASKS.md":
        parts.append(TASK_LIST)
    return "".join(parts)


def build_package(pkg: Path) -> None:
    for folder in sdd.FOLDERS:
        (pkg / folder).mkdir(parents=True)
        (pkg / folder / "README.md").write_text(
            "# Índice\n\nNÃO APLICÁVEL: fixture.\n", encoding="utf-8")
    for name, text in CHECKPOINTS.items():
        (pkg / "checkpoints" / name).write_text(text, encoding="utf-8")
    (pkg / "contracts" / "manifest.yaml").write_text(
        "feature: {id: \"001\"}\ncontracts: {}\n", encoding="utf-8")
    for name in sdd.FILES:
        (pkg / name).write_text(document(name), encoding="utf-8")


class ValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pkg = self.root / ".spec" / "001-demo"
        build_package(self.pkg)
        (self.root / ".spec" / "README.md").write_text(
            "| Pacote |\n| --- |\n| 001-demo |\n", encoding="utf-8")
        (self.root / "requisitos").mkdir()
        self.source = self.root / "requisitos" / "req.md"
        self.source.write_text(SOURCE, encoding="utf-8")
        for name in ("CONSTITUTION.md", "CODEMAP.md"):
            (self.root / name).write_text("# x\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name: str, text: str) -> None:
        (self.pkg / name).write_text(text, encoding="utf-8")

    def edit(self, name: str, old: str, new: str) -> None:
        text = (self.pkg / name).read_text(encoding="utf-8")
        self.assertIn(old, text)
        self.write(name, text.replace(old, new, 1))

    def run_validator(self, *args: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = sdd.main(["--root", str(self.root), *args])
        return code, out.getvalue() + err.getvalue()

    def assert_code(self, code: str, *args: str) -> None:
        exit_code, output = self.run_validator(*args)
        self.assertEqual(exit_code, 1, output)
        self.assertIn(f"[{code}]", output)


class LayoutTests(ValidatorTestCase):
    def test_should_pass_complete_package(self):
        code, output = self.run_validator("--strict", "--require-full")
        self.assertEqual(code, 0, output)

    def test_should_refuse_vacuous_pass_without_packages(self):
        shutil.rmtree(self.pkg)
        code, _ = self.run_validator()
        self.assertEqual(code, 2)

    def test_should_reject_specs_outside_dot_spec(self):
        (self.root / "specs").mkdir()
        self.assert_code("PKG-001")

    def test_should_reject_lowercase_legacy_files(self):
        self.write("spec.md", "# legado\n")
        self.assert_code("PKG-007")

    def test_should_require_every_structure_file(self):
        (self.pkg / "TDD.md").unlink()
        self.assert_code("PKG-002")

    def test_should_require_folder_index(self):
        (self.pkg / "evidence" / "README.md").unlink()
        self.assert_code("PKG-006")

    def test_should_require_constitution(self):
        (self.root / "CONSTITUTION.md").unlink()
        self.assert_code("CON-001")

    def test_should_require_codemap_after_design(self):
        (self.root / "CODEMAP.md").unlink()
        self.assert_code("CMP-001")

    def test_should_require_feature_index(self):
        (self.root / ".spec" / "README.md").unlink()
        self.assert_code("IDX-001")

    def test_should_require_every_package_in_index(self):
        build_package(self.root / ".spec" / "002-outra")
        self.assert_code("IDX-002")


class StageTests(ValidatorTestCase):
    def test_should_reject_unstarted_requirements_file(self):
        self.write("FRD.md", document("FRD.md", "Não iniciado"))
        self.assert_code("STG-001")

    def test_should_reject_unstarted_design_after_tasks(self):
        self.write("DESIGN.md", document("DESIGN.md", "Não iniciado"))
        self.assert_code("STG-003")

    def test_should_only_warn_for_pending_stage_by_default(self):
        for name in sdd.STAGES[2]:
            self.write(name, document(name, "Não iniciado"))
        for name in ("plan-to-tasks.yaml", "test-coverage.yaml"):
            (self.pkg / "checkpoints" / name).unlink()
        code, output = self.run_validator()
        self.assertEqual(code, 0, output)
        self.assert_code("PKG-003", "--require-full")

    def test_should_require_checkpoint_for_produced_stage(self):
        (self.pkg / "checkpoints" / "spec-to-plan.yaml").unlink()
        self.assert_code("CKP-001")

    def test_should_require_every_id_in_checkpoint(self):
        (self.pkg / "checkpoints" / "plan-to-tasks.yaml").write_text(
            "feature: {id: \"001\"}\n# T001\n", encoding="utf-8")
        self.assert_code("CKP-003")

    def test_should_require_contract_manifest_after_design(self):
        (self.pkg / "contracts" / "manifest.yaml").unlink()
        self.assert_code("CTR-001")


class SectionTests(ValidatorTestCase):
    def test_should_report_missing_template_section(self):
        self.edit("FRD.md", "## interações externas", "## Outra coisa")
        self.assert_code("SEC-001")

    def test_should_report_empty_section(self):
        self.edit("NFRD.md", "NÃO APLICÁVEL: fixture.", "")
        self.assert_code("SEC-002")

    def test_should_require_valid_file_status(self):
        self.edit("CHECKLIST.md", "- Status: Rascunho", "- Status: ok")
        self.assert_code("SPC-001")


class RequirementTests(ValidatorTestCase):
    def test_should_require_origem_line(self):
        self.edit("SPECIFICATION.md",
                  "origem: SRC-001 (requisitos/req.md#L3)", "fonte: x")
        self.assert_code("REQ-001")

    def test_should_require_registered_source(self):
        self.edit("SPECIFICATION.md", "origem: SRC-001 (requisitos",
                  "origem: SRC-009 (requisitos")
        self.assert_code("SRC-001")

    def test_should_reject_anchor_beyond_source_end(self):
        self.edit("SPECIFICATION.md", "req.md#L3)", "req.md#L3-L90)")
        self.assert_code("ANC-004")

    def test_should_require_disposition_for_every_source_id(self):
        self.source.write_text(SOURCE + "- RF-02: novo.\n",
                               encoding="utf-8")
        self.assert_code("FON-002")

    def test_should_accept_source_id_covered_by_another_package(self):
        self.source.write_text(SOURCE + "- RF-02: novo.\n",
                               encoding="utf-8")
        other = self.root / ".spec" / "002-outra"
        build_package(other)
        text = (other / "SOURCE_TRACEABILITY.md").read_text(
            encoding="utf-8")
        (other / "SOURCE_TRACEABILITY.md").write_text(
            text + "\nRF-02 derivado.\n", encoding="utf-8")
        for name in ("spec-to-plan.yaml", "plan-to-tasks.yaml",
                     "test-coverage.yaml"):
            path = other / "checkpoints" / name
            path.write_text(path.read_text(encoding="utf-8").replace(
                'id: "001"', 'id: "002"'), encoding="utf-8")
        (self.root / ".spec" / "README.md").write_text(
            "001-demo\n002-outra\n", encoding="utf-8")
        code, output = self.run_validator()
        self.assertEqual(code, 0, output)

    def test_should_require_acceptance_id(self):
        self.edit("SPECIFICATION.md", "- AC-REQ-001-01:", "- Critério:")
        self.assert_code("REQ-007")


class CrossFileTests(ValidatorTestCase):
    def test_should_reject_ears_statement_copied_into_frd(self):
        self.edit("FRD.md", "| REQ-001 |",
                  "| REQ-001 |\n\n> A Sala deve ecoar.")
        self.assert_code("XRF-003")

    def test_should_require_every_nfr_in_nfrd(self):
        self.edit("NFRD.md", "### NFR-001: Node", "### Qualidade")
        self.assert_code("XRF-001")

    def test_should_require_every_requirement_in_design(self):
        self.edit("DESIGN.md", IDS, "NFR-001")
        self.assert_code("XRF-001")

    def test_should_require_tdd_cycle_for_every_acceptance(self):
        self.edit("TDD.md", "AC-REQ-001-01 e ", "")
        self.assert_code("XRF-005")

    def test_should_require_task_for_every_requirement(self):
        self.edit("TASKS.md", "Rastreia NFR-001.", "Rastreia REQ-001.")
        self.assert_code("TSK-006")

    def test_should_reject_checked_task_without_ledger(self):
        self.edit("TASKS.md", "- [ ] **T001", "- [x] **T001")
        self.assert_code("TSK-008")

    def test_should_reject_dependency_cycle(self):
        self.edit("TASKS.md", "Teste. Rastreia REQ-001.\n",
                  "Teste. Rastreia REQ-001.\n  - Depende de: T002.\n")
        self.assert_code("TSK-007")

    def test_should_require_mermaid_theme(self):
        self.edit("TASKS.md", f"{THEME}\n", "")
        self.assert_code("MMD-001")

    def test_should_reject_broken_relative_link(self):
        self.edit("DESIGN.md", IDS, f"[{IDS}](ausente.md)")
        self.assert_code("LNK-001")

    def test_should_reject_missing_evidence_file(self):
        self.edit("VERIFICATION.md", IDS,
                  f"{IDS} `evidence/2026-09-24-testes.md`")
        self.assert_code("EVD-001")


if __name__ == "__main__":
    unittest.main()
