"""Phase 2 gate evaluation for registered E3 (HYPOTHESES.md v2).
One evaluation. Plateau: signal bar 15:15/15:25/15:35."""
from noise_area import load_databento_parquet, rth
from backtest import metrics, barrier_mc
from edges import run_e3
from phase2_e1e2 import verdict

if __name__ == "__main__":
    df5 = load_databento_parquet("data/databento_1m.parquet")
    print(f"data: {len(rth(df5))} RTH 5m bars")
    plateau = {}
    for hhmm in ("15:15", "15:25", "15:35"):
        t = run_e3(df5, signal_hhmm=hhmm)
        plateau[hhmm] = t
        tot = t["pnl"].sum() if not t.empty else 0.0
        pf = (t["pnl"][t.pnl > 0].sum() / max(1e-9, -t["pnl"][t.pnl <= 0].sum())
              if not t.empty else 0.0)
        print(f"signal {hhmm}: trades {len(t):4d}  total ${tot:>9,.0f}/ct  PF {pf:.2f}")
    t3 = plateau["15:25"]
    m3 = metrics(t3, "E3 main — last-hour flow momentum, signal 15:25 (registered)")
    mc3 = barrier_mc(t3["pnl"].values) if len(t3) else {"p_blow": 1.0}
    v3 = verdict("E3", m3, [plateau[h]["pnl"].sum() if len(plateau[h]) else 0.0
                            for h in ("15:15", "15:25", "15:35")], mc3)
    print(f"\nSESSION: E3 {'PASS' if v3 else 'FAIL'}")
