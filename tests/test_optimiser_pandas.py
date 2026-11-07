"""Numerical regression test for portfolio moments with missing prices."""

import ast
from pathlib import Path
import unittest
from unittest.mock import patch

try:
    import pandas as pd
except ImportError:
    pd = None


SOURCE = Path(__file__).resolve().parents[1] / "src" / "risk" / "optimiser.py"


@unittest.skipUnless(pd is not None, "pandas is required for numeric tests")
class TestPortfolioMoments(unittest.TestCase):
    def test_missing_price_is_not_forward_filled(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
        function = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_moments"
        )
        namespace = {"pd": pd, "Path": Path}
        isolated = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
        exec(compile(isolated, str(SOURCE), "exec"), namespace)

        columns = pd.MultiIndex.from_tuples([("ACME", "Close")])
        frame = pd.DataFrame(
            [[100.0], [float("nan")], [120.0], [132.0], [145.2]],
            columns=columns,
        )
        with patch.object(pd, "read_parquet", return_value=frame):
            mean, covariance = namespace["_moments"](Path("unused.parquet"))

        # Only the last two adjacent, nonmissing price pairs are valid.
        self.assertAlmostEqual(float(mean["ACME"]), 0.10)
        self.assertAlmostEqual(float(covariance.loc["ACME", "ACME"]), 0.0, places=12)


if __name__ == "__main__":
    unittest.main()
