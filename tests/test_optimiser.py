"""Regression tests for the portfolio optimizer's execution order."""

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class TestMaxSharpe(unittest.TestCase):
    def test_optimizes_before_returning_weights(self):
        """The optimizer must solve the Sharpe problem before reading weights."""
        source = Path(__file__).resolve().parents[1] / "src" / "risk" / "optimiser.py"
        fake_pandas = types.ModuleType("pandas")
        fake_pypfopt = types.ModuleType("pypfopt")
        frontier = Mock()
        expected_weights = {"AAA": 0.6, "BBB": 0.4}
        frontier.clean_weights.return_value = expected_weights
        fake_pypfopt.EfficientFrontier = Mock(return_value=frontier)

        with patch.dict(sys.modules, {"pandas": fake_pandas, "pypfopt": fake_pypfopt}):
            spec = importlib.util.spec_from_file_location("_test_optimiser_isolated", source)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        with patch.object(module, "_moments", return_value=("mu", "cov")) as moments:
            weights = module.max_sharpe("sample.parquet")

        moments.assert_called_once_with(Path("sample.parquet"))
        fake_pypfopt.EfficientFrontier.assert_called_once_with("mu", "cov")
        self.assertEqual(weights, expected_weights)
        self.assertEqual(
            frontier.mock_calls,
            [unittest.mock.call.max_sharpe(), unittest.mock.call.clean_weights()],
        )


if __name__ == "__main__":
    unittest.main()
