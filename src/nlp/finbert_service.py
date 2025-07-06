from typing import List
import pandas as pd
from functools import lru_cache
from transformers import pipeline
from src.utils.logging import setup_logger

log = setup_logger(__name__)

@lru_cache(maxsize=1)
def _pipe():
    log.info("Loading FinBERT")
    return pipeline("sentiment-analysis",
                    model="ProsusAI/finbert",
                    tokenizer="ProsusAI/finbert",
                    device=-1, truncation=True)

class FinBERTService:
    def __init__(self):
        self.clf = _pipe()
    def score(self, sents: List[str]) -> pd.DataFrame:
        p = self.clf(sents, batch_size=16)
        return pd.DataFrame({"sentence": sents,
                             "label": [d["label"] for d in p],
                             "score": [d["score"] for d in p]})
