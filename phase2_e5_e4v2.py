"""Gate evaluations for E5 (month-end rebalancing, ES) and E4-v2
(vol-targeted BTC trend). One evaluation each, as registered."""
import numpy as np
import pandas as pd
from rebalance import load_es_zn, run_e5
from crypto_trend import (load_yahoo_daily, run_e4_voltarget, sharpe,
                          max_dd, boot_p_dd)

RNG = np.random.default_rng(7)


def pf_halves(tr, col="pnl"):
    w, l = tr[col][tr[col] > 0], tr[col][tr[col] <= 0]
    pf = w.sum() / max(1e-9, -l.sum())
    h = len(tr) // 2
    return pf, tr[col].iloc[:h].sum(), tr[col].iloc[h:].sum(), len(w) / len(tr)


def boot_dd_dollars(pnl, thresh=2500.0, n_paths=10_000):
    hits = 0
    for _ in range(n_paths):
        eq = np.cumsum(RNG.choice(pnl, size=len(pnl), replace=True))
        peak = np.maximum.accumulate(eq)
        if (eq - peak).min() < -thresh:
            hits += 1
    return hits / n_paths


if __name__ == "__main__":
    # ---------------- E5 ----------------
    px = load_es_zn("data/es_zn_1d.csv")
    print(f"E5 data: {len(px)} days  {px.index[0].date()} -> {px.index[-1].date()}")
    plateau = {}
    for w in (3, 4, 5):
        t = run_e5(px, window=w)
        plateau[w] = t
        print(f"window {w}: trades {len(t):4d}  total ${t['pnl'].sum():>9,.0f}/ct  "
              f"PF {t['pnl'][t.pnl>0].sum()/max(1e-9,-t['pnl'][t.pnl<=0].sum()):.2f}")
    t5 = plateau[4]
    pf, h1, h2, wr = pf_halves(t5)
    pdd = boot_dd_dollars(t5["pnl"].values)
    print(f"\n== E5 main (window 4) == trades {len(t5)}  WR {wr:.1%}  PF {pf:.2f}  "
          f"total ${t5['pnl'].sum():,.0f}/ct  half1 ${h1:,.0f} half2 ${h2:,.0f}  "
          f"P(maxDD>$2.5k) {pdd:.1%}")
    c5 = {"n>=100": len(t5) >= 100, "PF>1.3": pf > 1.3, "half1>0": h1 > 0,
          "half2>0": h2 > 0,
          "plateau all>0": all(plateau[w]["pnl"].sum() > 0 for w in (3, 4, 5)),
          "P(maxDD>$2.5k)<10%": pdd < 0.10}
    for k, v in c5.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print(f"E5 VERDICT: {'PASS' if all(c5.values()) else 'FAIL'} (n={len(t5)})")

    # ---------------- E4-v2 ----------------
    df = load_yahoo_daily("data/btc_1d.json")
    plat2 = {}
    for lb in (21, 28, 35):
        tr, daily, eq = run_e4_voltarget(df, lookback=lb)
        plat2[lb] = (tr, daily, eq)
        print(f"\nE4v2 lb {lb}: trades {len(tr)}  sum(ret) {tr['ret'].sum():+.2f}  "
              f"final {eq.iloc[-1]:.2f}x", end="")
    tr, daily, eq = plat2[28]
    pf, h1, h2, wr = pf_halves(tr, "ret")
    pdd = boot_p_dd(daily)
    s_strat = sharpe(daily)
    bh = df["close"].pct_change().dropna()
    s_bh = sharpe(bh)
    print(f"\n\n== E4-v2 main (lb 28) == trades {len(tr)}  WR {wr:.1%}  PF {pf:.2f}  "
          f"final {eq.iloc[-1]:.2f}x  maxDD {max_dd(eq.values):.1%}")
    print(f"half1 {h1:+.2f} half2 {h2:+.2f}  Sharpe {s_strat:.2f} vs bh {s_bh:.2f}  "
          f"P(maxDD>40%) {pdd:.1%}")
    c4 = {"n>=100": len(tr) >= 100, "PF>1.3": pf > 1.3, "half1>0": h1 > 0,
          "half2>0": h2 > 0,
          "plateau all>0": all(plat2[lb][0]["ret"].sum() > 0 for lb in (21, 28, 35)),
          "P(maxDD>40%)<10%": pdd < 0.10, "Sharpe>=buy-hold": s_strat >= s_bh}
    for k, v in c4.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print(f"E4-v2 VERDICT: {'PASS' if all(c4.values()) else 'FAIL'} (n={len(tr)})")
