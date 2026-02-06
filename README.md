# Neo Screener

Sentiment enhanced risk screener that combines live market data, SEC risk factor text, and FinBERT sentiment to produce quick risk signals and a simple portfolio tilt.

This is a portfolio project built to show end to end thinking
data ingestion, NLP, risk metrics, optimization, and a lightweight UI.

## What it does

- Downloads recent price history for a ticker list and stores it as a parquet file
- Pulls SEC EntityRiskFactors text for each company and saves it locally
- Runs FinBERT sentiment scoring on the risk factor text
- Computes a simple historical VaR signal from stored prices
- Produces a max Sharpe weight suggestion using mean and covariance from returns
- Exposes everything through a FastAPI service and a Streamlit dashboard

Not financial advice. For learning and demo purposes only.

## Architecture

- Streamlit dashboard calls the API
- FastAPI API orchestrates the pipeline
- Price loader pulls data via yfinance and writes parquet
- Risk factor loader pulls text from SEC data APIs and caches text files
- NLP service uses ProsusAI FinBERT via transformers pipeline
- Risk module computes VaR and portfolio weights via PyPortfolioOpt

Suggested diagram to add under docs
docs architecture.png and docs dataflow.png

## Project structure

- src api
  - main.py FastAPI endpoints
  - dashboard.py Streamlit UI
- src data
  - price_loader.py market data ingestion and cache
  - text_loader.py SEC risk factor ingestion and cache
- src nlp
  - finbert_service.py sentiment scoring
- src risk
  - var_calc.py historical VaR
  - optimiser.py max Sharpe weights
- src utils
  - logging.py logger setup

## Quickstart

Prereqs
- Python 3.10 plus recommended
- Internet access on first run for model download and data fetch

Create a virtual environment and install dependencies

Mac and Linux
```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
