from pathlib import Path
import pandas as pd
from pypfopt import EfficientFrontier
def _moments(path: Path):
    df = pd.read_parquet(path)
    closes = df.xs("Close", level=1, axis=1)
    rets = closes.pct_change().dropna()
    return rets.mean(), rets.cov()
def max_sharpe(price_file="data/raw_prices.parquet"):
    mu, cov = _moments(Path(price_file))
    ef = EfficientFrontier(mu, cov)
    return ef.clean_weights()
