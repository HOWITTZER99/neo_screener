"""Integration coverage for price gaps using real pandas return calculations.

These tests skip when pandas is not installed in the lightweight CI environment.
Unlike the AST/mock tests, they check the numerical result of pct_change.
"""

import ast
from pathlib import Path
import unittest
from unittest.mock import patch

try:
    import pandas as pd
except ImportError:
    pd = None


SOURCE = Path(__file__).resolve().parents[1] / "src" / "risk" / "var_calc.py"


@unittest.skipUnless(pd is not None, "pandas is required for numeric integration tests")
class TestReturnsWithPandas(unittest.TestCase):
    def test_missing_middle_price_does_not_create_synthetic_returns(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
        function = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_returns"
        )
        namespace = {"pd": pd, "Path": Path}
        isolated = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
        exec(compile(isolated, str(SOURCE), "exec"), namespace)

        columns = pd.MultiIndex.from_tuples([("ACME", "Close")])
        frame = pd.DataFrame(
            [[100.0], [float("nan")], [120.0], [132.0]],
            columns=columns,
        )
        with patch.object(pd, "read_parquet", return_value=frame):
            result = namespace["_returns"](Path("unused.parquet"))

        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(float(result.iloc[0]), 0.10)


if __name__ == "__main__":
    unittest.main()
