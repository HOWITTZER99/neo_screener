import logging, sys
def setup_logger(name: str = "neo_screener") -> logging.Logger:
    lg = logging.getLogger(name)
    # This logger owns its output; do not duplicate records through root handlers.
    lg.propagate = False
    if not lg.handlers:
        lg.setLevel(logging.INFO)
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
        lg.addHandler(h)
    return lg
