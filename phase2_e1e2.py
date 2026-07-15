"""Phase 2 gate evaluation for registered E1 and E2 (HYPOTHESES.md v2).
One evaluation each. Reuses baseline harness: metrics() and barrier_mc()
from backtest.py, loader from noise_area.py. No parameter changes here."""
from __future__ import annotations
import numpy as np

from noise_area import load_databento_parquet, rth
from backtest import metrics, barrier_mc
from edges import run_e1, run_e2

GATES = "PF>1.3 & n>=100 & both halves>0 & plateau all>0 & MC P(blow)<10%"


def verdict(label, m, plateau_totals, mc):
    checks = {
        "PF>1.3": m.get("pf", 0) > 1.3,
        "n>=100": m.get("trades", 0) >= 100,
        "half1>0": m.get("half1", 0) > 0,
        "half2>0": m.get("half2", 0) > 0,
        "plateau all>0": all(t > 0 for t in plateau_totals),
        "MC P(blow)<10%": mc.get("p_blow", 1.0) < 0.10,
    }
    print(f"\n== VERDICT {label} vs gates ({GATES}) ==")
    for k, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    ok = all(checks.values())
    print(f"{label} VERDICT: {'PASS' if ok else 'FAIL'} "
          f"(n={m.get('trades', 0)} trades)")
    return ok


if __name__ == "__main__":
    df5 = load_databento_parquet("data/databento_1m.parquet")
    n_days = len(set(rth(df5).index.date))
    print(f"data: {len(rth(df5))} RTH 5m bars, {n_days} days")

    # ---- E1: main = OR 15min; registered plateau = OR window 10/15/20 ----
    print("\n######## E1 — ORB + compression filter ########")
    e1_plateau = {}
    for om in (10, 15, 20):
        t = run_e1(df5, or_minutes=om)
        e1_plateau[om] = t
        tot = t["pnl"].sum() if not t.empty else 0.0
        pf = (t["pnl"][t.pnl > 0].sum() / max(1e-9, -t["pnl"][t.pnl <= 0].sum())
              if not t.empty else 0.0)
        print(f"OR {om:2d}min: trades {len(t):4d}  total ${tot:>9,.0f}/ct  PF {pf:.2f}")
    t1 = e1_plateau[15]
    m1 = metrics(t1, "E1 main — ORB-15 + compression (registered)")
    mc1 = barrier_mc(t1["pnl"].values) if len(t1) else {"p_blow": 1.0}
    v1 = verdict("E1", m1, [e1_plateau[o]["pnl"].sum() if len(e1_plateau[o])
                            else 0.0 for o in (10, 15, 20)], mc1)

    # ---- E2: main = z 2.0; registered plateau = z 1.75/2.00/2.25 ----
    print("\n######## E2 — VWAP reversion + info-day filter ########")
    e2_plateau = {}
    for z in (1.75, 2.00, 2.25):
        t = run_e2(df5, z_entry=z)
        e2_plateau[z] = t
        tot = t["pnl"].sum() if not t.empty else 0.0
        pf = (t["pnl"][t.pnl > 0].sum() / max(1e-9, -t["pnl"][t.pnl <= 0].sum())
              if not t.empty else 0.0)
        print(f"z {z:.2f}: trades {len(t):4d}  total ${tot:>9,.0f}/ct  PF {pf:.2f}")
    t2 = e2_plateau[2.00]
    m2 = metrics(t2, "E2 main — VWAP reversion z2.0 (registered)")
    mc2 = barrier_mc(t2["pnl"].values) if len(t2) else {"p_blow": 1.0}
    v2 = verdict("E2", m2, [e2_plateau[z]["pnl"].sum() if len(e2_plateau[z])
                            else 0.0 for z in (1.75, 2.00, 2.25)], mc2)

    print(f"\nSESSION: E1 {'PASS' if v1 else 'FAIL'}  E2 {'PASS' if v2 else 'FAIL'}")
