"""E6 Phase 4 shadow logger. Daily cron. Fetches BTC/ETH/SOL, recomputes
the registered E6 book from full history (completed bars only), logs
target weights to logs/signals_e6.jsonl. Errors are logged, never hidden."""
from __future__ import annotations
import json, os, sys, urllib.request, datetime as dt

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portfolio_trend as ptf

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "logs", "signals_e6.jsonl")
URLS = {"BTC": ("btc", "15y"), "ETH": ("eth", "10y"), "SOL": ("sol", "7y")}


def fetch_all() -> dict:
    paths = {}
    for name, (tag, rng) in URLS.items():
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/"
               f"{name}-USD?interval=1d&range={rng}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        p = os.path.join(ROOT, "data", f"shadow_{tag}_1d.json")
        open(p, "wb").write(urllib.request.urlopen(req, timeout=30).read())
        paths[name] = p
    return paths


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rec = {"computed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "strategy": "e6", "source": "yahoo"}
    try:
        px = ptf.load_universe(fetch_all())
        today = pd.Timestamp.now(tz="UTC").normalize()
        px = px[px.index < today]                    # completed bars only
        bar_date = str(px.index[-1].date())
        if os.path.exists(OUT) and any(
                json.loads(l).get("bar_date") == bar_date
                for l in open(OUT) if l.strip()):
            return 0
        _, daily, eq = ptf.run_e6(px)
        rec.update({"bar_date": bar_date, "weights": ptf.LAST_HELD,
                    "book_ret_last": round(float(daily.iloc[-1]), 6),
                    "eq_index": round(float(eq.iloc[-1]), 4)})
    except Exception as e:
        rec["error"] = f"{type(e).__name__}: {e}"
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return 0 if "error" not in rec else 1


if __name__ == "__main__":
    raise SystemExit(main())
