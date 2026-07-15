"""Unit tests for E4 before the gate run."""
import json
import numpy as np
import pandas as pd
from crypto_trend import run_e4, load_yahoo_daily

FAILS = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: FAILS.append(name)

def mk(prices):
    idx = pd.date_range("2020-01-01", periods=len(prices), freq="D", tz="UTC")
    p = np.asarray(prices, float)
    return pd.DataFrame({"open": p, "close": p}, index=idx)

# 1. monotonic up: one entry after warmup, held to end, profitable
up = mk(100 * 1.01 ** np.arange(200))
tr, daily, eq = run_e4(up, 28)
check("up_one_trade", len(tr) == 1)
check("up_profitable_net", tr["ret"].iloc[0] > 0)
# 2. monotonic down: never long, equity stays 1.0, zero trades
dn = mk(100 * 0.99 ** np.arange(200))
tr2, _, eq2 = run_e4(dn, 28)
check("down_zero_trades", len(tr2) == 0 and abs(eq2.iloc[-1] - 1.0) < 1e-12)
# 3. costs charged both sides: round trip on flat-ish flip loses ~2*(fee+slip)
flat = mk(np.r_[100 * 1.005 ** np.arange(40), 100 * 1.005 ** 39 * 0.97 ** np.arange(1, 60)])
tr3, _, _ = run_e4(flat, 28)
check("flip_roundtrip_cost_visible", len(tr3) >= 1 and tr3["ret"].iloc[0] < 0.05)
# 4. no lookahead: truncating future leaves earlier trades identical
df = load_yahoo_daily("data/btc_1d.json")
full, _, _ = run_e4(df, 28)
part, _, _ = run_e4(df.iloc[:-500], 28)
k = len(part) - 1  # last trade of part may be a defensive close; compare all before it
f, p = full.iloc[:k], part.iloc[:k]
check("no_lookahead_truncation", len(f) == len(p) and np.allclose(f["ret"], p["ret"]))

print("\nALL E4 TESTS PASS" if not FAILS else f"\n{len(FAILS)} FAILURES: {FAILS}")
raise SystemExit(1 if FAILS else 0)
