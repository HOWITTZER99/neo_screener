"""Regression tests for the dependency-free daily repository report."""

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "record_daily_health.py"
spec = importlib.util.spec_from_file_location("record_daily_health", SCRIPT)
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)


class TestDailyHealthReport(unittest.TestCase):
    def run_report(self, root, day="2026-10-31"):
        fake_script = root / ".github" / "scripts" / "record_daily_health.py"
        with patch.object(health, "__file__", str(fake_script)), patch.object(
            sys, "argv", ["record_daily_health.py", "--date", day]
        ), redirect_stdout(io.StringIO()):
            health.main()
        return root / "docs" / "daily_checks" / f"{day}.md"

    def test_syntax_error_is_recorded_as_failure(self):
        """Broken source must never appear as a passing syntax check."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src" / "broken.py"
            source.parent.mkdir(parents=True)
            source.write_text("def broken(:\n    pass\n", encoding="utf-8")

            report = self.run_report(root).read_text(encoding="utf-8")

            self.assertIn("| Parse all `src/**/*.py` with Python AST | **FAIL** |", report)
            self.assertIn("| `python -m compileall -q src` | **FAIL** |", report)
            self.assertIn("broken.py", report)

    def test_existing_daily_report_is_not_overwritten(self):
        """A second run on the same day must preserve the first report."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "docs" / "daily_checks" / "2026-10-31.md"
            report.parent.mkdir(parents=True)
            report.write_text("original daily report\n", encoding="utf-8")

            self.run_report(root)

            self.assertEqual(report.read_text(encoding="utf-8"), "original daily report\n")


    def test_failing_unittest_is_recorded_as_failure(self):
        """A failed regression test must mark the daily report as failed."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src" / "healthy.py"
            source.parent.mkdir(parents=True)
            source.write_text("VALUE = 1\n", encoding="utf-8")
            test_file = root / "tests" / "test_failure.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(
                "import unittest\n"
                "class TestFailure(unittest.TestCase):\n"
                "    def test_fails(self):\n"
                "        self.assertEqual(1, 2)\n",
                encoding="utf-8",
            )

            report = self.run_report(root).read_text(encoding="utf-8")

            self.assertIn("| Parse all `src/**/*.py` with Python AST | **PASS** |", report)
            self.assertIn("| `python -m compileall -q src` | **PASS** |", report)
            self.assertIn("| `python -m unittest discover -s tests -p 'test_*.py' -v` | **FAIL** |", report)
            self.assertIn("FAILED (failures=1)", report)


if __name__ == "__main__":
    unittest.main()
