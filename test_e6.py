"""Sanity tests for E4-v3 and E6 before gate runs."""
import numpy as np
import pandas as pd
from crypto_trend import load_yahoo_daily
from garch_sizing import sigma_garch_ann, run_sized
from portfolio_trend import load_universe, run_e6

FAILS = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: FAILS.append(name)

df = load_yahoo_daily("data/btc_1d.json")
sg = sigma_garch_ann(df)
check("garch_sigma_finite_after_warmup", np.isfinite(sg[520:]).all())
check("garch_sigma_plausible_range",
      (sg[520:] > 0.05).all() and (sg[520:] < 5.0).all())
# no-lookahead: truncating the future must not change earlier sigmas
sg_part = sigma_garch_ann(df.iloc[:-400])
check("garch_no_lookahead",
      np.allclose(sg[:len(df) - 400 - 1], sg_part[:-1], rtol=1e-6, equal_nan=True))

tr, d, eq = run_sized(df, sg, 28)
check("e4v3_equity_finite", np.isfinite(eq.values).all() and (eq.values > 0).all())

px = load_universe()
check("universe_aligned", list(px.columns) == ["BTC", "ETH", "SOL"] and len(px) > 4000)
t6, d6, e6 = run_e6(px)
check("e6_equity_finite", np.isfinite(e6.values).all() and (e6.values > 0).all())
check("e6_episodes_reasonable", 100 <= len(t6) <= 2000)
# no leverage: worst daily book loss cannot exceed worst asset daily loss
worst_asset = np.nanmin(px.pct_change().values)
check("e6_no_leverage_daily_loss", d6.min() >= worst_asset - 0.001)

print("\nALL E4v3/E6 TESTS PASS" if not FAILS else f"\n{len(FAILS)} FAILURES: {FAILS}")
raise SystemExit(1 if FAILS else 0)
