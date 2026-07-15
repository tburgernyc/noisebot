"""Gate evaluations: E4-v3 (GARCH sizing A/B vs E4-v2) and E6 (portfolio).
One evaluation each, as registered."""
import numpy as np
import pandas as pd
from crypto_trend import (load_yahoo_daily, run_e4_voltarget, sharpe,
                          max_dd, boot_p_dd)
from garch_sizing import sigma_garch_ann, run_sized
from portfolio_trend import load_universe, run_e6
from phase2_e5_e4v2 import pf_halves

if __name__ == "__main__":
    df = load_yahoo_daily("data/btc_1d.json")
    bh = df["close"].pct_change().dropna()

    # -------- E4-v3 --------
    print("Fitting GARCH (expanding, monthly refits)...")
    sg = sigma_garch_ann(df)
    tr3, d3, eq3 = run_sized(df, sg, 28)
    tr2, d2, eq2 = run_e4_voltarget(df, 28)
    pf3, h13, h23, wr3 = pf_halves(tr3, "ret")
    print(f"\n== E4-v3 (GARCH) == trades {len(tr3)}  PF {pf3:.2f}  "
          f"final {eq3.iloc[-1]:.2f}x  maxDD {max_dd(eq3.values):.1%}  "
          f"Sharpe {sharpe(d3):.2f}")
    print(f"== E4-v2 (ref)  == final {eq2.iloc[-1]:.2f}x  "
          f"maxDD {max_dd(eq2.values):.1%}  Sharpe {sharpe(d2):.2f}")
    c3 = {"n>=100": len(tr3) >= 100, "PF>1.3": pf3 > 1.3,
          "half1>0": h13 > 0, "half2>0": h23 > 0,
          "P(maxDD>40%)<10%": boot_p_dd(d3) < 0.10,
          "Sharpe>=buy-hold": sharpe(d3) >= sharpe(bh),
          "BAR Sharpe>=E4v2": sharpe(d3) >= sharpe(d2),
          "BAR maxDD<=E4v2": max_dd(eq3.values) >= max_dd(eq2.values)}
    for k, v in c3.items(): print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print(f"E4-v3 VERDICT: {'PASS — replaces E4-v2' if all(c3.values()) else 'FAIL — E4-v2 stands'}")

    # -------- E6 --------
    px = load_universe()
    print(f"\nE6 universe: {len(px)} days, cols {list(px.columns)}")
    plat = {}
    for ls in ((7, 14, 28), (14, 28, 56), (28, 56, 112)):
        t6, d6, e6 = run_e6(px, lookbacks=ls)
        plat[ls] = (t6, d6, e6)
        print(f"lbs {ls}: episodes {len(t6)}  sum(ret) {t6['ret'].sum():+.2f}  "
              f"final {e6.iloc[-1]:.2f}x  Sharpe {sharpe(d6):.2f}")
    t6, d6, e6 = plat[(14, 28, 56)]
    pf6, h16, h26, wr6 = pf_halves(t6, "ret")
    # benchmark over identical span
    span = d6.index
    bh6 = bh.reindex(span).dropna()
    print(f"\n== E6 main == episodes {len(t6)}  WR {wr6:.1%}  PF {pf6:.2f}  "
          f"final {e6.iloc[-1]:.2f}x  maxDD {max_dd(e6.values):.1%}  "
          f"Sharpe {sharpe(d6):.2f} vs BTC-bh {sharpe(bh6):.2f}")
    c6 = {"n>=100": len(t6) >= 100, "PF>1.3": pf6 > 1.3,
          "half1>0": h16 > 0, "half2>0": h26 > 0,
          "plateau all>0": all(plat[k][0]["ret"].sum() > 0 for k in plat),
          "P(maxDD>40%)<10%": boot_p_dd(d6) < 0.10,
          "Sharpe>=BTC-bh": sharpe(d6) >= sharpe(bh6)}
    for k, v in c6.items(): print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print(f"E6 VERDICT: {'PASS' if all(c6.values()) else 'FAIL'} (n={len(t6)})")
