import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from mcp_tooldelta.cli import main
from mcp_tooldelta.diff import compare
from mcp_tooldelta.render import render


class CliTests(unittest.TestCase):
    def call(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_demo_gate_and_json(self):
        code, output, _ = self.call(["demo", "--format", "json"])
        self.assertEqual(code, 1)
        report = json.loads(output)
        self.assertEqual(report["summary"], {"breaking": 4, "review": 3, "info": 3})
        self.assertEqual(self.call(["demo", "--fail-on", "none"])[0], 0)

    def test_write_refuse_overwrite_and_force(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "report.html"
            code, _, _ = self.call(["demo", "--format", "html", "-o", str(path)])
            self.assertEqual(code, 1)
            self.assertIn("<!doctype html>", path.read_text(encoding="utf-8"))
            self.assertEqual(self.call(["demo", "-o", str(path)])[0], 2)
            self.assertEqual(self.call(["demo", "-o", str(path), "--force"])[0], 1)

    def test_normalize_and_protect_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory) / "input.json", Path(directory) / "baseline.json"
            source.write_text('{"tools": []}', encoding="utf-8")
            self.assertEqual(self.call(["snapshot", str(source), "-o", str(target)])[0], 0)
            self.assertEqual(json.loads(target.read_text()), {"tools": []})
            self.assertEqual(self.call(["diff", str(source), str(target)])[0], 0)
            self.assertEqual(self.call(["diff", str(source), str(target), "-o", str(source), "--force"])[0], 2)
            self.assertEqual(json.loads(source.read_text()), {"tools": []})

    def test_errors_stderr_not_json_stdout(self):
        code, output, error = self.call(["diff", "not-present.json", "also-missing.json", "--format", "json"])
        self.assertEqual(code, 2)
        self.assertEqual(output, "")
        self.assertIn("tooldelta:", error)

    def test_real_module_process(self):
        result = subprocess.run([sys.executable, "-m", "mcp_tooldelta", "demo", "--format", "json"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["schema_version"], 1)
        with tempfile.TemporaryDirectory() as directory:
            before, after = Path(directory) / "before.json", Path(directory) / "after.json"
            before.write_text('{"tools": []}', encoding="utf-8")
            after.write_text(json.dumps({"tools": [{"name": "поиск🔎", "inputSchema": {"type": "object"}}]}, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run([sys.executable, "-m", "mcp_tooldelta", "diff", str(before), str(after), "--format", "json"], capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "cp1251"})
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["changes"][0]["tool"], "поиск🔎")


class RenderingTests(unittest.TestCase):
    def test_untrusted_strings_cannot_break_script_block(self):
        attack = '</script><script>alert("x")</script> | **bad**\nnext'
        tool = {"name": attack, "description": attack, "inputSchema": {"type": "object"}}
        report = compare([], [tool])
        document = render(report, "html", attack, "after")
        self.assertNotIn(attack, document)
        self.assertIn("\\u003c/script\\u003e", document)
        self.assertNotIn("innerHTML", document)
        self.assertNotIn("__TOOLDELTA_PAYLOAD__", document)
        markdown = render(report, "markdown")
        self.assertNotIn("<script>", markdown)
        self.assertIn("\\|", markdown)

    def test_empty_reports_and_format_validation(self):
        report = compare([], [])
        for format in ("text", "markdown"):
            self.assertIn("No contract changes", render(report, format))
        with self.assertRaises(ValueError):
            render(report, "invalid")

    def test_terminal_control_characters_removed(self):
        report = compare([], [{"name": "\x1b[31mtool", "inputSchema": {"type": "object"}}])
        self.assertNotIn("\x1b", render(report))


if __name__ == "__main__":
    unittest.main()
