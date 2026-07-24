"""E14 gate evaluation: threshold (band-breach) 60/40 rebalancing pressure,
equity leg on MES. ONE registered run on data/es_zn_1d.csv (2010-06 ->
2026-07). Plateau band delta in {0.03, 0.04, 0.05}, ALL must be net
positive. Gates: n>=100, PF>1.3, both halves>0, plateau all>0,
bootstrap P(maxDD > $2,500/ct) < 10% (E5-identical ruin gate).

!! Running this IS the one-shot evaluation. Machinery is proven first by
test_e14.py on synthetic data.
"""
import numpy as np
import pandas as pd
from rebalance_threshold import load_es_zn, run_e14

RNG = np.random.default_rng(14)
PLATEAU = (0.03, 0.04, 0.05)
MAIN = 0.04


def pf_halves(tr, col="pnl"):
    w, l = tr[col][tr[col] > 0], tr[col][tr[col] <= 0]
    pf = w.sum() / max(1e-9, -l.sum())
    h = len(tr) // 2
    return pf, tr[col].iloc[:h].sum(), tr[col].iloc[h:].sum(), len(w) / max(1, len(tr))


def boot_dd_dollars(pnl, thresh=2500.0, n_paths=10_000):
    hits = 0
    for _ in range(n_paths):
        eq = np.cumsum(RNG.choice(pnl, size=len(pnl), replace=True))
        peak = np.maximum.accumulate(eq)
        if (eq - peak).min() < -thresh:
            hits += 1
    return hits / n_paths


if __name__ == "__main__":
    print("!! This driver RUNS the registered one-shot E14 evaluation.\n")
    px = load_es_zn("data/es_zn_1d.csv")
    print(f"E14 data: {len(px)} days  {px.index[0].date()} -> {px.index[-1].date()}")

    plateau = {}
    for d in PLATEAU:
        t = run_e14(px, delta=d)
        plateau[d] = t
        tot = t["pnl"].sum() if len(t) else 0.0
        pf = (t["pnl"][t.pnl > 0].sum() / max(1e-9, -t["pnl"][t.pnl <= 0].sum())
              if len(t) else 0.0)
        print(f"  delta {d:.2f}: trades {len(t):4d}  total ${tot:>9,.0f}/ct  PF {pf:.3f}")

    tr = plateau[MAIN]
    if len(tr) == 0:
        print("\nE14 VERDICT: FAIL — zero trades at the main band.")
        raise SystemExit(0)

    pf, h1, h2, wr = pf_halves(tr)
    pdd = boot_dd_dollars(tr["pnl"].values)
    eq = tr["pnl"].cumsum()
    peak = eq.cummax()
    maxdd = (eq - peak).min()

    print(f"\n== E14 main (delta {MAIN}) == trades {len(tr)}  WR {wr:.1%}  "
          f"PF {pf:.3f}  total ${tr['pnl'].sum():,.0f}/ct  "
          f"half1 ${h1:,.0f} half2 ${h2:,.0f}  maxDD ${maxdd:,.0f}/ct  "
          f"P(maxDD>$2.5k) {pdd:.1%}")

    gates = {
        "n>=100": len(tr) >= 100,
        "PF>1.3": pf > 1.3,
        "half1>0": h1 > 0,
        "half2>0": h2 > 0,
        "plateau all>0": all(plateau[d]["pnl"].sum() > 0 if len(plateau[d]) else False
                             for d in PLATEAU),
        "P(maxDD>$2.5k)<10%": pdd < 0.10,
    }
    print()
    for k, v in gates.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    verdict = "PASS" if all(gates.values()) else "FAIL"
    npass = sum(gates.values())
    print(f"\nE14 VERDICT: {verdict} — {npass}/{len(gates)} gates "
          f"(n={len(tr)}, plateau "
          f"{ {d: round(float(plateau[d]['pnl'].sum()),0) for d in PLATEAU} })")
