"""Phase 2 gate evaluation for registered E4. One evaluation.
Gates (spot-adapted, as registered): n>=100, PF>1.3, halves both>0,
plateau 21/28/35 all>0, bootstrap P(maxDD>40%)<10%, Sharpe >= buy-hold."""
import numpy as np
from crypto_trend import load_yahoo_daily, run_e4, sharpe, max_dd, boot_p_dd

if __name__ == "__main__":
    df = load_yahoo_daily("data/btc_1d.json")
    print(f"data: {len(df)} daily bars  {df.index[0].date()} -> {df.index[-1].date()}")
    plateau = {}
    for lb in (21, 28, 35):
        tr, daily, eq = run_e4(df, lookback=lb)
        plateau[lb] = (tr, daily, eq)
        print(f"lb {lb}: trades {len(tr):4d}  sum(ret) {tr['ret'].sum():+.2f}  "
              f"final eq {eq.iloc[-1]:.2f}x")
    tr, daily, eq = plateau[28]
    w, l = tr["ret"][tr["ret"] > 0], tr["ret"][tr["ret"] <= 0]
    pf = w.sum() / max(1e-9, -l.sum())
    half = len(tr) // 2
    h1, h2 = tr["ret"].iloc[:half].sum(), tr["ret"].iloc[half:].sum()
    p_dd = boot_p_dd(daily)
    s_strat = sharpe(daily)
    bh = df["close"].pct_change().dropna()
    s_bh = sharpe(bh)
    print(f"\n== E4 main (lb 28) ==")
    print(f"trades {len(tr)}  WR {len(w)/len(tr):.1%}  PF {pf:.2f}  "
          f"final {eq.iloc[-1]:.2f}x  maxDD {max_dd(eq.values):.1%}")
    print(f"half1 {h1:+.2f}  half2 {h2:+.2f}  Sharpe {s_strat:.2f} vs buy-hold "
          f"{s_bh:.2f} (bh maxDD {max_dd((1+bh).cumprod().values):.1%})")
    print(f"bootstrap P(maxDD>40%) {p_dd:.1%}")
    checks = {
        "n>=100": len(tr) >= 100, "PF>1.3": pf > 1.3,
        "half1>0": h1 > 0, "half2>0": h2 > 0,
        "plateau all>0": all(plateau[lb][0]["ret"].sum() > 0 for lb in (21, 28, 35)),
        "P(maxDD>40%)<10%": p_dd < 0.10,
        "Sharpe>=buy-hold": s_strat >= s_bh,
    }
    print("\n== VERDICT E4 vs registered gates ==")
    for k, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print(f"E4 VERDICT: {'PASS' if all(checks.values()) else 'FAIL'} (n={len(tr)})")
