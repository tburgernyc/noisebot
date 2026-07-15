"""E4-v2 Phase 4 shadow logger. Runs daily via cron (00:10 UTC).
Fetches BTC-USD daily bars, recomputes the registered signal from FULL
history, appends one line to logs/signals_e4v2.jsonl. Idempotent per
date. Any exception is logged as an error line — errors are data.
Phase 4 gate (registered): 90 calendar days, zero critical errors,
signal/w must match backtest recomputation exactly."""
from __future__ import annotations
import json, os, sys, time, urllib.request, datetime as dt

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crypto_trend import SLIP, FEE  # noqa (documented constants)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "logs", "signals_e4v2.jsonl")
URL = ("https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD"
       "?interval=1d&range=15y")
LOOKBACK, VOL_TARGET, VOL_WIN = 28, 0.15, 30


def fetch() -> pd.DataFrame:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    raw = json.loads(urllib.request.urlopen(req, timeout=30).read())
    r = raw["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    df = pd.DataFrame({"open": q["open"], "close": q["close"]},
                      index=pd.to_datetime(r["timestamp"], unit="s", utc=True))
    return df.dropna().sort_index()


def compute(df: pd.DataFrame) -> dict:
    c = df["close"]
    # signal uses the LAST COMPLETED daily bar (drop today's partial bar)
    today = pd.Timestamp.now(tz="UTC").normalize()
    c = c[c.index.normalize() < today]
    r28 = float(c.iloc[-1] / c.iloc[-1 - LOOKBACK] - 1.0)
    sig = 1 if r28 > 0 else 0
    vol = float(c.pct_change().rolling(VOL_WIN).std().iloc[-1] * np.sqrt(365))
    w = min(1.0, VOL_TARGET / vol) if (sig and vol > 0) else 0.0
    return {"bar_date": str(c.index[-1].date()), "close": float(c.iloc[-1]),
            "r28": round(r28, 6), "signal": sig, "vol30_ann": round(vol, 4),
            "w": round(w, 4)}


def already_logged(bar_date: str) -> bool:
    if not os.path.exists(OUT):
        return False
    for line in open(OUT):
        try:
            if json.loads(line).get("bar_date") == bar_date:
                return True
        except json.JSONDecodeError:
            continue
    return False


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rec = {"computed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "strategy": "e4v2", "source": "yahoo"}
    try:
        d = compute(fetch())
        if already_logged(d["bar_date"]):
            return 0
        rec.update(d)
    except Exception as e:  # errors are logged, never hidden
        rec["error"] = f"{type(e).__name__}: {e}"
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return 0 if "error" not in rec else 1


if __name__ == "__main__":
    raise SystemExit(main())
