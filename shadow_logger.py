"""SHADOW LOGGER — signal-only, zero execution.

Purpose: accumulate TRUE forward out-of-sample evidence while Phase 2 is
re-run on tick-grade data. Polls Yahoo 5m bars (delayed ~15 min — fine for
shadow expectancy tracking, NOT for live fills), rebuilds noise bands from
the prior 14 sessions, and appends signal transitions to signals.jsonl.

This file intentionally contains no broker code and never will; execution
lives in a separate module that only gets written after Phase 2 passes.
Run:  python3 shadow_logger.py            (one poll cycle; cron it)
      python3 shadow_logger.py --replay   (emit today's signals from history)
"""
from __future__ import annotations
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from noise_area import NY, build_days, load_yahoo_json, signal_for_bar

DATA = Path(__file__).parent / "data" / "nq_5m.json"
OUT = Path(__file__).parent / "signals.jsonl"
URL = ("https://query1.finance.yahoo.com/v8/finance/chart/NQ%3DF"
       "?interval=5m&range=60d&includePrePost=false")


def refresh_data() -> bool:
    try:
        r = subprocess.run(
            ["curl", "-sk", URL, "-H", "User-Agent: Mozilla/5.0",
             "-o", str(DATA)], timeout=30, check=True)
        return r.returncode == 0
    except Exception as e:  # noqa: BLE001
        print(f"data refresh failed: {e}", file=sys.stderr)
        return False


def emit(rec: dict) -> None:
    rec["logged_at"] = datetime.now(timezone.utc).isoformat()
    with OUT.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))


def run_once() -> None:
    if not refresh_data() and not DATA.exists():
        return
    days = build_days(load_yahoo_json(DATA), lookback=14)
    if not days:
        print("insufficient history", file=sys.stderr)
        return
    day = days[-1]
    pos = 0
    for i in range(len(day.bars)):
        sig = signal_for_bar(day, i, pos)
        if sig == "HOLD":
            continue
        ts = day.bars.index[i]
        px = float(day.bars["close"].iloc[i])
        emit({"ts": ts.isoformat(), "symbol": "MNQ", "strategy": "noise_area_5m",
              "signal": sig, "ref_close": px,
              "upper": round(float(day.upper.iloc[i]), 2),
              "lower": round(float(day.lower.iloc[i]), 2),
              "vwap": round(float(day.vwap.iloc[i]), 2),
              "mode": "SHADOW", "note": "delayed data; no order placed"})
        pos = {"LONG": 1, "SHORT": -1, "EXIT": 0}[sig]


if __name__ == "__main__":
    run_once()
