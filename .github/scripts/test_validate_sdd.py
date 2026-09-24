"""Testes do validador SDD nativo (.github/scripts/validate-sdd.py)."""

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "validate-sdd.py"
SPEC = importlib.util.spec_from_file_location("validate_sdd", SCRIPT)
sdd = importlib.util.module_from_spec(SPEC)
sys.modules["validate_sdd"] = sdd
SPEC.loader.exec_module(sdd)

THEME = sdd.THEME
PALETTE = "\n".join(sdd.PALETTE)
SOURCE = "# Requisitos\n\n- RF-01: ecoar.\n- RNF-01: Node.js.\n"
BODIES = {
    "registro de fontes": (
        "| ID | Classe | Local |\n| --- | --- | --- |\n"
        "| SRC-001 | repositório | `requisitos/req.md` |\n"
    ),
    "requisitos": (
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
        "- Envelope de medição: nfrd.md NFR-001\n\n"
        "**Verificação**\n\n- inspeção: i1\n"
    ),
    "requisitos funcionais por domínio": "| REQ-001 | Ecoar |\n",
    "requisitos de qualidade": "### NFR-001: Node\n\nEnvelope.\n",
    "visão de entrega e rastreabilidade": "| REQ-001, NFR-001 | cli |\n",
    "grafo de dependências": (
        f"```mermaid\n{THEME}\nflowchart TD\n{PALETTE}\n"
        "  T001 --> T002\n```\n"
    ),
    "registro de execução": (
        "Tarefas concluídas: **0 de 2**.\n"
        "Marcadas como concluídas pela verificação: nenhuma\n"
    ),
}
TASKS = (
    "## Fase 1\n\n"
    "- [ ] **T001 [S] [Plano:P1.1] RED** Teste. Rastreia REQ-001.\n"
    "  - Aceite: falha.\n\n"
    "- [ ] **T002 [S] [Plano:P1.1] GREEN** Código. Rastreia NFR-001.\n"
    "  - Depende de: T001.\n"
)
HEADER = {
    "spec.md": "# Especificação\n\n- Status: Rascunho\n"
               "- Constituição: CONSTITUTION.md\n\n",
}


def document(name: str) -> str:
    parts = [HEADER.get(name, f"# {name}\n\n")]
    for names in sdd.SECTIONS[name]:
        title = names[0]
        body = BODIES.get(title, "NÃO APLICÁVEL: fixture.\n")
        parts.append(f"## {title}\n\n{body}\n")
    if name == "tasks.md":
        parts.append(TASKS)
    return "".join(parts)


class ValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pkg = self.root / ".spec" / "001-demo"
        self.pkg.mkdir(parents=True)
        (self.root / "requisitos").mkdir()
        (self.root / "requisitos" / "req.md").write_text(
            SOURCE, encoding="utf-8")
        (self.root / "CONSTITUTION.md").write_text(
            "# Constituição\n", encoding="utf-8")
        for name in sdd.SECTIONS:
            self.write(name, document(name))

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

    def assert_code(self, code: str) -> None:
        exit_code, output = self.run_validator()
        self.assertEqual(exit_code, 1, output)
        self.assertIn(f"[{code}]", output)


class CompletePackageTests(ValidatorTestCase):
    def test_should_pass_complete_package(self):
        code, output = self.run_validator("--strict", "--require-full")
        self.assertEqual(code, 0, output)

    def test_should_refuse_vacuous_pass_without_packages(self):
        for path in self.pkg.iterdir():
            path.unlink()
        self.pkg.rmdir()
        code, _ = self.run_validator()
        self.assertEqual(code, 2)


class LayoutTests(ValidatorTestCase):
    def test_should_reject_specs_outside_dot_spec(self):
        (self.root / "specs").mkdir()
        self.assert_code("PKG-001")

    def test_should_require_constitution(self):
        (self.root / "CONSTITUTION.md").unlink()
        self.assert_code("CON-001")

    def test_should_require_frd(self):
        (self.pkg / "frd.md").unlink()
        self.assert_code("PKG-002")

    def test_should_report_missing_template_section(self):
        self.edit("frd.md", "## interações externas", "## Outra coisa")
        self.assert_code("SEC-001")

    def test_should_report_empty_section(self):
        self.edit("nfrd.md", "NÃO APLICÁVEL: fixture.", "")
        self.assert_code("SEC-002")


class RequirementTests(ValidatorTestCase):
    def test_should_require_origem_line(self):
        self.edit("spec.md", "origem: SRC-001 (requisitos/req.md#L3)",
                  "fonte: SRC-001")
        self.assert_code("REQ-001")

    def test_should_require_registered_source(self):
        self.edit("spec.md", "origem: SRC-001 (requisitos/req.md#L3)",
                  "origem: SRC-009 (requisitos/req.md#L3)")
        self.assert_code("SRC-001")

    def test_should_reject_anchor_beyond_source_end(self):
        self.edit("spec.md", "req.md#L3)", "req.md#L3-L90)")
        self.assert_code("ANC-004")

    def test_should_require_disposition_for_every_source_id(self):
        (self.root / "requisitos" / "req.md").write_text(
            SOURCE + "- RF-02: novo.\n", encoding="utf-8")
        self.assert_code("FON-002")

    def test_should_require_acceptance_id(self):
        self.edit("spec.md", "- AC-REQ-001-01:", "- Critério:")
        self.assert_code("REQ-007")


class CrossFileTests(ValidatorTestCase):
    def test_should_reject_ears_statement_copied_into_frd(self):
        self.edit("frd.md", "| REQ-001 | Ecoar |",
                  "| REQ-001 | Ecoar |\n\n> A Sala deve ecoar.")
        self.assert_code("XRF-003")

    def test_should_require_every_nfr_in_nfrd(self):
        self.edit("nfrd.md", "### NFR-001: Node", "### Qualidade")
        self.assert_code("XRF-001")

    def test_should_require_every_requirement_in_plan(self):
        self.edit("plan.md", "| REQ-001, NFR-001 | cli |",
                  "| NFR-001 | cli |")
        self.assert_code("XRF-004")

    def test_should_require_task_for_every_requirement(self):
        self.edit("tasks.md", "Rastreia NFR-001.", "Rastreia REQ-001.")
        self.assert_code("TSK-006")

    def test_should_reject_checked_task_without_ledger(self):
        self.edit("tasks.md", "- [ ] **T001", "- [x] **T001")
        self.assert_code("TSK-008")

    def test_should_reject_dependency_cycle(self):
        self.edit("tasks.md", "Teste. Rastreia REQ-001.\n",
                  "Teste. Rastreia REQ-001.\n  - Depende de: T002.\n")
        self.assert_code("TSK-007")

    def test_should_require_mermaid_theme(self):
        self.edit("tasks.md", f"{THEME}\n", "")
        self.assert_code("MMD-001")

    def test_should_reject_broken_relative_link(self):
        self.edit("plan.md", "| cli |", "| [cli](ausente.md) |")
        self.assert_code("LNK-001")


if __name__ == "__main__":
    unittest.main()
