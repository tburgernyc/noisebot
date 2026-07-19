"""
pull_databento.py — RUN THIS LOCALLY on your machine (where
DATABENTO_API_KEY lives in your env). It never prints or stores the key.

What it does:
1. Quotes the exact cost of the pull and shows it BEFORE downloading.
   Aborts if the quote exceeds $25 (override with --yes-over-cap).
2. Downloads CME Globex (GLBX.MDP3) ohlcv-1m, continuous front month
   by volume: NQ.v.0 (analysis series) and MNQ.v.0 (reference/volume
   sanity), 2023-07-01 -> 2026-07-18.
3. Writes one CSV per symbol into ./databento_out/ and prints row
   counts, date ranges, and sha256 hashes.

Then attach the two CSVs to the Claude session (or open the Claude
desktop app so the session can stage them itself).

Usage:
    pip install databento
    python3 pull_databento.py

CANONICAL-REPO CAVEAT (added on import, 2026-07-18): this script was
staged by a parallel cloud session working from a stale project
snapshot. The canonical repo ALREADY OWNS Databento 1-min data
(data/databento_1m.parquet) and its window overlaps the burned
Databento MNQ 2024-07->2026-07 window (4 evaluations). Do not run this
for hypothesis selection; any new spend must clear the window ledger
in HYPOTHESES.md first.
"""

import hashlib
import os
import sys
from pathlib import Path

try:
    import databento as db
except ImportError:
    sys.exit("pip install databento  (then re-run)")

DATASET = "GLBX.MDP3"
SCHEMA = "ohlcv-1m"
SYMBOLS = ["NQ.v.0", "MNQ.v.0"]
START, END = "2023-07-01", "2026-07-18"
COST_CAP_USD = 25.0
OUT = Path("databento_out")


def main() -> None:
    if not os.environ.get("DATABENTO_API_KEY"):
        sys.exit("DATABENTO_API_KEY not set in this shell. "
                 "Set it (export DATABENTO_API_KEY=...) and re-run.")
    client = db.Historical()  # reads key from env; never printed

    cost = client.metadata.get_cost(
        dataset=DATASET, symbols=SYMBOLS, stype_in="continuous",
        schema=SCHEMA, start=START, end=END,
    )
    print(f"Quoted cost for {SYMBOLS} {SCHEMA} {START}->{END}: ${cost:.2f}")
    if cost > COST_CAP_USD and "--yes-over-cap" not in sys.argv:
        sys.exit(f"Quote exceeds ${COST_CAP_USD:.0f} cap — aborting. "
                 f"Re-run with --yes-over-cap to proceed anyway.")

    OUT.mkdir(exist_ok=True)
    for sym in SYMBOLS:
        print(f"Downloading {sym} ...", flush=True)
        data = client.timeseries.get_range(
            dataset=DATASET, symbols=[sym], stype_in="continuous",
            schema=SCHEMA, start=START, end=END,
        )
        df = data.to_df()  # ts_event UTC index, OHLCV scaled floats
        keep = [c for c in ("open", "high", "low", "close", "volume")
                if c in df.columns]
        df = df[keep]
        name = sym.replace(".", "_").lower()
        path = OUT / f"{name}_1m.csv"
        df.to_csv(path)
        sha = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        print(f"  {path}  rows={len(df)}  "
              f"{df.index[0]} -> {df.index[-1]}  sha256[:16]={sha}")

    print("\nDone. Attach the CSVs in ./databento_out/ to the Claude "
          "session (or open the Claude desktop app and tell Claude "
          "where they are).")


if __name__ == "__main__":
    main()
