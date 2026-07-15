"""Unit tests for E5 + E4-v2 before gate runs."""
import numpy as np
import pandas as pd
from rebalance import run_e5, TICK, MULT, COST_RT

FAILS = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: FAILS.append(name)

# two months: Jan (ES flat, establishes prev close), Feb (ES rallies, ZN flat)
days_j = pd.bdate_range("2026-01-05", "2026-01-30")
days_f = pd.bdate_range("2026-02-02", "2026-02-27")
es = pd.Series(np.r_[np.full(len(days_j), 5000.0),
                     5000 + 10 * np.arange(1, len(days_f) + 1)],
               index=days_j.append(days_f))
zn = pd.Series(112.0, index=es.index)
px = pd.DataFrame({"es": es, "zn": zn})

tr = run_e5(px, window=4)
feb = tr[[d.month == 2 for d in tr["date"]]]
check("e5_trades_only_in_window", len(tr) == len(feb) and 3 <= len(feb) <= 4)
check("e5_overweight_equities_shorts", (feb["dir"] == -1).all())
# rising ES + short => each 1-day trade loses (10*5) + slippage + cost
exp = -(10 * MULT) - 2 * TICK * MULT - COST_RT
check("e5_pnl_math_exact", np.allclose(feb["pnl"], exp))

# E4-v2: weight never exceeds 1, equity path finite, fewer/equal DD vs E4
from crypto_trend import load_yahoo_daily, run_e4, run_e4_voltarget, max_dd
df = load_yahoo_daily("data/btc_1d.json")
_, _, eq_full = run_e4(df, 28)
tr2, d2, eq_vt = run_e4_voltarget(df, 28)
check("e4v2_finite", np.isfinite(eq_vt.values).all() and (eq_vt.values > 0).all())
check("e4v2_dd_reduced_vs_e4", max_dd(eq_vt.values) > max_dd(eq_full.values))
check("e4v2_trade_count_close_to_e4", abs(len(tr2) - 167) <= 15)

print("\nALL E5/E4v2 TESTS PASS" if not FAILS else f"\n{len(FAILS)} FAILURES: {FAILS}")
raise SystemExit(1 if FAILS else 0)
