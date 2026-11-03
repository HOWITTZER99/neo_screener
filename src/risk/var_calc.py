from pathlib import Path
import pandas as pd, numpy as np
from src.utils.logging import setup_logger
log = setup_logger(__name__)

def _returns(path: Path) -> pd.Series:
    df = pd.read_parquet(path)
    closes = df.xs("Close", level=1, axis=1)
    return closes.pct_change(fill_method=None).dropna().mean(axis=1)

def hist_var(price_file="data/raw_prices.parquet", alpha=0.95) -> float:
    if not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between 0 and 1")
    r = _returns(Path(price_file))
    if len(r) == 0:
        raise ValueError("Cannot compute historical VaR without returns")
    var = -np.percentile(r, 100*(1-alpha))
    return round(var, 4)
