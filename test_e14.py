"""Machinery tests for E14 (threshold band-breach rebalancing) on SYNTHETIC
data, run BEFORE the registered es_zn window is touched. Covers: roll-safe
returns, trigger direction, sub-band silence, exact P&L, roll exclusion,
book reset, and no-lookahead (truncation invariance)."""
import numpy as np
import pandas as pd
from rebalance_threshold import (run_e14, roll_safe_ret, MULT, TICK,
                                 COST_RT, REF)

FAILS = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def frame(es, zn, es_iid=None, zn_iid=None):
    idx = pd.bdate_range("2020-01-01", periods=len(es))
    n = len(es)
    return pd.DataFrame(
        {"es": np.asarray(es, float), "zn": np.asarray(zn, float),
         "es_iid": np.ones(n) if es_iid is None else np.asarray(es_iid),
         "zn_iid": np.ones(n) if zn_iid is None else np.asarray(zn_iid)},
        index=idx)


# ---- roll_safe_ret ----------------------------------------------------
c = pd.Series([100.0, 101.0, 102.0, 103.0])
i = pd.Series([1, 1, 2, 2])       # roll between bar 1 and bar 2
r = roll_safe_ret(c, i)
check("rollret_first_bar_nan", np.isnan(r[0]))
check("rollret_roll_bar_nan", np.isnan(r[2]))
check("rollret_clean_bar_value", np.isclose(r[1], 101/100 - 1) and
      np.isclose(r[3], 103/102 - 1))

# ---- rising ES: equity always overweight -> every trade is a SHORT -----
rise = frame(5000 * (1.02 ** np.arange(40)), np.full(40, 112.0))
tr = run_e14(rise, 0.05)
check("rising_triggers_at_least_two", len(tr) >= 2)
check("rising_all_shorts", len(tr) and (tr["dir"] == -1).all())

# ---- book RESETS: sustained rise does NOT trigger every day ------------
# without a reset a 40-day breach would fire ~30x; with reset it is few
check("reset_limits_trigger_count", len(tr) < 10)

# ---- exact P&L: recompute each trade from its own dates ----------------
pos_by_date = {d.date(): k for k, d in enumerate(rise.index)}
ok = True
for _, row in tr.iterrows():
    t = pos_by_date[row["date"]]
    e = rise["es"].iloc[t]
    nx = rise["es"].iloc[t + 1]
    pos = row["dir"]
    exp = ((nx - TICK * pos) - (e + TICK * pos)) * pos * MULT - COST_RT
    ok = ok and np.isclose(row["pnl"], exp)
check("pnl_math_exact", ok)

# ---- sub-band silence: tiny drift never breaches -----------------------
flat = frame(5000 * (1.0005 ** np.arange(30)), np.full(30, 112.0))
check("subband_no_trades", len(run_e14(flat, 0.05)) == 0)

# ---- roll exclusion in isolation: one breach, exit spans a roll --------
# day1 ES jumps +50% -> w_eq = 0.9/1.3 = 0.692, breaches 0.05 -> trade d1->d2
base = frame([5000.0, 7500.0, 7600.0], np.full(3, 112.0))
noroll = run_e14(base, 0.05)
check("isolated_breach_tradeable", len(noroll) == 1 and noroll["dir"].iloc[0] == -1)
rolled = frame([5000.0, 7500.0, 7600.0], np.full(3, 112.0),
               es_iid=[1, 1, 2])          # equity roll between d1 and d2
check("roll_drops_the_trade", len(run_e14(rolled, 0.05)) == 0)

# ---- no-lookahead: truncation invariance -------------------------------
# trades fully contained in a prefix must be identical when the tail is cut
full = run_e14(rise, 0.05)
k = 25
trunc = run_e14(rise.iloc[:k], 0.05)
cutoff = rise.index[k - 2].date()          # last trade fully inside prefix
full_in = full[full["date"] <= cutoff]["date"].tolist()
trunc_in = trunc[trunc["date"] <= cutoff]["date"].tolist()
check("no_lookahead_truncation_invariant", full_in == trunc_in and len(full_in) > 0)

print("\nALL E14 TESTS PASS" if not FAILS else f"\n{len(FAILS)} FAILURES: {FAILS}")
raise SystemExit(1 if FAILS else 0)
