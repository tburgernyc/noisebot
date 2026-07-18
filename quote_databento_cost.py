"""Quote the EXACT Databento cost of the H3 cross-instrument pull BEFORE
spending credit. Zero data is downloaded; get_cost is a free metadata call.

Run locally:  DATABENTO_API_KEY=<key> python3 quote_databento_cost.py
(key stays in your env var — never in files or chat, per repo rules)

Symbology: .v.0 = continuous front month, volume-based roll. NOTE for the
actual backtest: bands use intraday ratios (close_t / day_open) which are
roll-safe, but prev_close on a roll date comes from a DIFFERENT contract.
Handle by taking prev_close from the same contract's prior session or by
skipping band construction inputs across roll days. Flagged so it doesn't
become a silent lookalike of the spec.
"""
import os
import sys

try:
    import databento as db
except ImportError:
    sys.exit("pip install databento")

KEY = os.environ.get("DATABENTO_API_KEY")
if not KEY:
    sys.exit("set DATABENTO_API_KEY env var first")

DATASET = "GLBX.MDP3"
SCHEMA = "ohlcv-1m"
START, END = "2024-07-01", "2026-07-17"          # ~2 years
SYMBOLS = {
    "NQ.v.0":  "Nasdaq-100 e-mini  (PRIMARY — documented edge market)",
    "ES.v.0":  "S&P 500 e-mini     (in-family confirm)",
    "YM.v.0":  "Dow e-mini         (in-family confirm)",
    "RTY.v.0": "Russell 2000 e-mini(in-family confirm)",
    "GC.v.0":  "Gold               (out-of-family control)",
    "CL.v.0":  "Crude oil          (out-of-family control)",
}

client = db.Historical(key=KEY)
total = 0.0
print(f"{'symbol':<10} {'USD':>10}   role")
for sym, role in SYMBOLS.items():
    try:
        cost = client.metadata.get_cost(
            dataset=DATASET, symbols=[sym], stype_in="continuous",
            schema=SCHEMA, start=START, end=END,
        )
        total += cost
        print(f"{sym:<10} {cost:>10.2f}   {role}")
    except Exception as e:  # noqa: BLE001
        print(f"{sym:<10} {'ERROR':>10}   {e}")
print(f"{'TOTAL':<10} {total:>10.2f}   (credit available: ~$100)")
print("\nIf total <= ~$15, proceed: the remainder stays reserved for a"
      "\ntick/1-s pull on the finalist instrument before live capital.")
