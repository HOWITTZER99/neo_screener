import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2] / "src"))
from fastapi import FastAPI, Query, Response
from statistics import mean
from src.data.price_loader import PriceFetcher
from src.data.text_loader import fetch_risk_factors
from src.nlp.finbert_service import FinBERTService
from src.risk.var_calc import hist_var
from src.risk.optimiser import max_sharpe

app = FastAPI(title="Neo-Screener API")
pf = PriceFetcher(); fb = FinBERTService()

@app.get("/prices")
def prices(tickers: str = "AAPL,MSFT"):
    df = pf.fetch(tickers.split(","), start="2023-01-01").tail()
    payload = df.to_json(orient="split")
    return Response(content=payload, media_type="application/json")

@app.get("/var")
def var(alpha: float = 0.95):
    return {"VaR": hist_var(alpha=alpha), "conf": alpha}

@app.get("/weights")
def weights():
    return max_sharpe()

@app.get("/sentiment")
def sentiment(tickers: str = Query("AAPL,MSFT")):
    tl = [t.strip().upper() for t in tickers.split(",")]
    para = fetch_risk_factors(tl)
    m = {"POSITIVE":1,"NEUTRAL":0,"NEGATIVE":-1}
    res={}
    for t in tl:
        df = fb.score(para[t].split(". "))
        res[t]=round(mean(m[l]*s for l,s in zip(df.label,df.score)),3)
    return res


