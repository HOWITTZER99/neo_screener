from typing import List, Dict
from pathlib import Path
import requests, json
from src.utils.logging import setup_logger

log = setup_logger(__name__)
SEC_MAP = "https://www.sec.gov/files/company_tickers.json"

def _cik(ticker: str) -> str:
    m = requests.get(SEC_MAP, timeout=10).json()
    cik = [v["cik_str"] for v in m.values() if v["ticker"] == ticker.upper()][0]
    return f"{int(cik):010d}"

def fetch_risk_factors(tickers: List[str], out_dir: Path = Path("data/text")) -> Dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {}
    for t in tickers:
        url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{_cik(t)}/dei/EntityRiskFactors.json"
        j = requests.get(url, headers={"User-Agent":"neo-screener"}, timeout=20).json()
        txt = j["units"]["textBlock"][0]["val"]
        (out_dir / f"{t}.txt").write_text(txt, encoding="utf-8")
        out[t] = txt
    return out
