"""Regression test for complete-case returns across assets with staggered gaps."""

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
class TestMultiAssetMoments(unittest.TestCase):
    def test_staggered_missing_prices_use_only_shared_valid_returns(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
        function = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_moments"
        )
        namespace = {"pd": pd, "Path": Path}
        isolated = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
        exec(compile(isolated, str(SOURCE), "exec"), namespace)

        columns = pd.MultiIndex.from_tuples([("AAA", "Close"), ("BBB", "Close")])
        frame = pd.DataFrame(
            [
                [100.0, 200.0],
                [110.0, 210.0],
                [float("nan"), 220.5],
                [121.0, 231.525],
                [133.1, float("nan")],
                [146.41, 243.10125],
                [161.051, 255.2563125],
                [177.1561, 268.019128125],
            ],
            columns=columns,
        )
        with patch.object(pd, "read_parquet", return_value=frame):
            mean, covariance = namespace["_moments"](Path("unused.parquet"))

        # Only rows 1, 6 and 7 have adjacent valid prices for BOTH assets.
        self.assertEqual(list(mean.index), ["AAA", "BBB"])
        self.assertAlmostEqual(float(mean["AAA"]), 0.10)
        self.assertAlmostEqual(float(mean["BBB"]), 0.05)
        self.assertEqual(covariance.shape, (2, 2))
        for value in covariance.to_numpy().flat:
            self.assertAlmostEqual(float(value), 0.0, places=12)


if __name__ == "__main__":
    unittest.main()
