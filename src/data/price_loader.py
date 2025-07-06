from typing import List
from pathlib import Path
import yfinance as yf, pandas as pd
from src.utils.logging import setup_logger

log = setup_logger(__name__)

class PriceFetcher:
    def __init__(self, out_path: Path = Path("data/raw_prices.parquet")):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        self.out_path = out_path

    def fetch(self, tickers: List[str], start: str = "2023-01-01") -> pd.DataFrame:
        log.info("Fetching %s", tickers)
        df = yf.download(tickers, start=start, group_by="ticker", progress=False)
        df.to_parquet(self.out_path)
        return df
