"""Dependency-free regression tests for the historical VaR function.

The risk module imports pandas and NumPy at module load time. Extracting the
real function's AST allows the lightweight CI suite to exercise its input
checks and percentile call without installing the entire analytics stack.
These tests do not replace integration tests using real market data.
"""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


SOURCE = Path(__file__).resolve().parents[1] / "src" / "risk" / "var_calc.py"


def load_hist_var(returns):
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "hist_var"
    )
    percentile = Mock(return_value=-0.03654)
    get_returns = Mock(return_value=returns)
    namespace = {
        "Path": Path,
        "_returns": get_returns,
        "np": SimpleNamespace(percentile=percentile),
    }
    isolated = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    exec(compile(isolated, str(SOURCE), "exec"), namespace)
    return namespace["hist_var"], get_returns, percentile


class TestHistoricalVar(unittest.TestCase):
    def test_valid_confidence_uses_lower_tail_and_rounds(self):
        hist_var, get_returns, percentile = load_hist_var([-0.04, -0.02, 0.01])
        self.assertEqual(hist_var("prices.parquet", alpha=0.95), 0.0365)
        get_returns.assert_called_once_with(Path("prices.parquet"))
        percentile.assert_called_once()
        args, _ = percentile.call_args
        self.assertEqual(args[0], [-0.04, -0.02, 0.01])
        self.assertAlmostEqual(args[1], 5.0)

    def test_rejects_invalid_confidence_before_loading_prices(self):
        for alpha in (0, 1, -0.1, 1.1, float("nan")):
            with self.subTest(alpha=alpha):
                hist_var, get_returns, percentile = load_hist_var([-0.01])
                with self.assertRaisesRegex(ValueError, "alpha"):
                    hist_var("prices.parquet", alpha=alpha)
                get_returns.assert_not_called()
                percentile.assert_not_called()

    def test_rejects_empty_returns_before_percentile(self):
        hist_var, get_returns, percentile = load_hist_var([])
        with self.assertRaisesRegex(ValueError, "without returns"):
            hist_var("prices.parquet")
        get_returns.assert_called_once()
        percentile.assert_not_called()


if __name__ == "__main__":
    unittest.main()
