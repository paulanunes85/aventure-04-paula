"""Tests for the SDD/TDD helper scripts in .github/scripts/.

Run: python3 -B -m unittest discover -s .github/scripts -p 'test_*.py'
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock

HERE = Path(__file__).resolve().parent


def load(name: str) -> ModuleType:
    module_name = name.replace("-", "_")
    spec = importlib.util.spec_from_file_location(
        module_name, HERE / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


red = load("validate-red-phase")
docs = load("validate-doc-references")
hooks = load("verify-hooks-loaded")
diagrams = load("validate-design-diagrams")
formatter = load("format-sdd-mermaid")

PY = sys.executable
PALETTE = "\n".join(diagrams.PALETTE)


def run(main, argv: list[str]) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = main(argv)
    return code, out.getvalue()


def write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TempRoot(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()


class RedPhaseTests(unittest.TestCase):
    def test_passes_when_tests_fail_with_expected_output(self) -> None:
        code, _ = run(red.main, [
            "--expect-output", "AC-REQ-001-01", "--", PY, "-c",
            "import sys; print('AC-REQ-001-01 failed'); sys.exit(1)"])
        self.assertEqual(code, 0)

    def test_rejects_green_run(self) -> None:
        code, out = run(red.main, ["--", PY, "-c", "pass"])
        self.assertEqual(code, 1)
        self.assertIn("tests passed", out)

    def test_rejects_failure_without_expected_output(self) -> None:
        code, _ = run(red.main, [
            "--expect-output", "REQ-002", "--", PY, "-c",
            "raise SystemExit(1)"])
        self.assertEqual(code, 1)

    def test_rejects_unexpected_exit_code(self) -> None:
        code, _ = run(red.main, [
            "--expect-exit", "1", "--", PY, "-c", "raise SystemExit(2)"])
        self.assertEqual(code, 1)

    def test_usage_errors(self) -> None:
        self.assertEqual(run(red.main, [])[0], 2)
        self.assertEqual(
            run(red.main, ["--", "no-such-command-xyz"])[0], 2)


class DocReferenceTests(TempRoot):
    def check(self, text: str) -> tuple[int, str]:
        write(self.root, "docs/guide.md", text)
        return run(docs.main, ["--root", str(self.root)])

    def test_reports_missing_path(self) -> None:
        code, out = self.check("Run `scripts/missing.sh`.\n")
        self.assertEqual(code, 1)
        self.assertIn("target-not-found: scripts/missing.sh", out)

    def test_accepts_existing_path_and_bare_file(self) -> None:
        write(self.root, "scripts/ok.py", "")
        write(self.root, "README.md", "")
        code, _ = self.check("Use `scripts/ok.py` and `README.md`.\n")
        self.assertEqual(code, 0)

    def test_requires_executable_for_dot_slash(self) -> None:
        write(self.root, "scripts/run.sh", "")
        code, out = self.check("Run `./scripts/run.sh`.\n")
        self.assertEqual(code, 1)
        self.assertIn("not-executable", out)

    def test_skips_non_current_claims(self) -> None:
        text = (
            "- [ ] Create `src/later.js`\n\n"
            "Planned: `docs/adr/` [planned]\n\n"
            "```text\nsrc/fenced.js\n```\n\n"
            "<!-- doc-references: off -->\n`src/ignored.js`\n"
            "<!-- doc-references: on -->\n"
        )
        self.assertEqual(self.check(text)[0], 0)

    def test_skips_draft_documents_and_spec_tree(self) -> None:
        write(self.root, ".spec/001-x/SPECIFICATION.md", "`src/nope.js`\n")
        code, _ = self.check("---\nstatus: draft\n---\n`src/nope.js`\n")
        self.assertEqual(code, 0)
        code, _ = run(docs.main, ["--root", str(self.root),
                                  "--include-specs"])
        self.assertEqual(code, 1)


class HookVerifierTests(TempRoot):
    def descriptor(self, name: str, data: object) -> None:
        write(self.root, f".github/hooks/{name}", json.dumps(data))

    def valid(self) -> None:
        write(self.root, ".github/hooks/scripts/hook.py", "")
        self.descriptor("10-guard.json", {"version": 1, "hooks": {
            "preToolUse": [{
                "bash": "python3 .github/hooks/scripts/hook.py pre",
                "powershell": "python .github/hooks/scripts/hook.py pre",
                "cwd": ".", "timeoutSec": 10}]}})

    def verify(self, *extra: str) -> tuple[int, str]:
        home = self.root / "home"
        home.mkdir(exist_ok=True)
        return run(hooks.main, ["--root", str(self.root),
                                "--copilot-home", str(home), *extra])

    def test_valid_descriptor_passes_without_runtime(self) -> None:
        self.valid()
        code, out = self.verify()
        self.assertEqual(code, 0, out)
        self.assertIn("WARNING no runtime evidence", out)

    def test_missing_script_and_config_json_fail(self) -> None:
        self.valid()
        self.descriptor("20-ctx.json", {"version": 1, "hooks": {
            "sessionStart": [{"bash": "python3 scripts/nope.py"}]}})
        self.descriptor("policy.json", {"shell": {}})
        code, out = self.verify()
        self.assertEqual(code, 1)
        self.assertIn("script not found: scripts/nope.py", out)
        self.assertIn("policy.json: must be an object with `version: 1`",
                      out)

    def test_disable_all_hooks_in_settings_fails(self) -> None:
        self.valid()
        write(self.root, ".github/copilot/settings.json",
              '{\n  // c\n  "disableAllHooks": true,\n}\n')
        code, out = self.verify()
        self.assertEqual(code, 1)
        self.assertIn("disableAllHooks", out)

    def test_runtime_evidence_is_bound_to_session(self) -> None:
        self.valid()
        write(self.root, ".github/hooks/.logs/audit.jsonl",
              '{"event": "sessionStart", "session": "a"}\n')
        self.assertEqual(self.verify("--require-runtime")[0], 0)
        self.assertEqual(self.verify("--session", "a")[0], 0)
        self.assertEqual(self.verify("--session", "b")[0], 1)

    def test_strip_jsonc_keeps_escaped_quotes_and_urls(self) -> None:
        text = '{"a": "x\\"//y", "u": "http://h", // c\n "b": [1,],}'
        self.assertEqual(json.loads(hooks.strip_jsonc(text)),
                         {"a": 'x"//y', "u": "http://h", "b": [1]})


class MermaidTests(TempRoot):
    def diagram(self, body: str) -> str:
        return f"# Doc\n\n```mermaid\n{body}```\n"

    def test_validator_flags_missing_theme_and_color(self) -> None:
        path = write(self.root, "doc.md",
                     self.diagram("flowchart TD\n  A:::x\n"
                                  "  classDef x fill:#FF0000\n"))
        errors, count = diagrams.validate_file(path)
        self.assertEqual(count, 1)
        self.assertTrue(any("theme directive" in e for e in errors))
        self.assertTrue(any("chromatic color" in e for e in errors))

    def test_validator_requires_palette_in_spec_package(self) -> None:
        body = f"{diagrams.THEME_DIRECTIVE}\nflowchart TD\n  A-->B\n"
        path = write(self.root, ".spec/001-x/DESIGN.md", self.diagram(body))
        with mock.patch.object(diagrams, "ROOT", self.root.resolve()):
            errors, _ = diagrams.validate_file(path)
            self.assertTrue(any("expected one" in e for e in errors))
            path.write_text(self.diagram(f"{body}{PALETTE}\n"),
                            encoding="utf-8")
            self.assertEqual(diagrams.validate_file(path)[0], [])

    def test_formatter_adds_theme_and_check_mode(self) -> None:
        path = write(self.root, "doc.md",
                     self.diagram("sequenceDiagram\n  A->>B: x\n"))
        argv = ["--spec-root", str(self.root)]
        self.assertEqual(run(formatter.main, [*argv, "--check"])[0], 1)
        self.assertEqual(run(formatter.main, argv)[0], 0)
        self.assertIn(formatter.THEME_DIRECTIVE, path.read_text())
        self.assertEqual(run(formatter.main, [*argv, "--check"])[0], 0)


if __name__ == "__main__":
    unittest.main()
