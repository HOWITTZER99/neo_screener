import streamlit as st
import requests
import pandas as pd
from fastapi.responses import Response

API = "http://localhost:8000"
st.title("Neo-Screener")

tickers = st.text_input("Tickers (comma-separated)", "AAPL,MSFT")

if st.button("Prices"):
    raw = requests.get(f"{API}/prices", params={"tickers": tickers}).text
    df  = pd.read_json(raw, orient="split")
    st.line_chart(df.xs("Close", level=1, axis=1))

if st.button("Sentiment"):
    scores = requests.get(
        f"{API}/sentiment", params={"tickers": tickers}
    ).json()
    st.bar_chart(scores)

if st.button("VaR"):
    var = requests.get(f"{API}/var").json()
    st.metric("95 % one-day VaR", f"{var['VaR']*100:.2f} %")

if st.button("Weights"):
    w = requests.get(f"{API}/weights").json()
    st.json(w)
