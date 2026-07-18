"""E7 gate evaluation: perp funding-rate carry (registered 2026-07-18).
ONE registered run. Body = 2020-01-01..2025-12-31 (gates evaluated here);
final six months 2026-01-01..2026-06-30 = once-only OOS segment, reported
separately. Funding: Binance monthly archives (data/funding/), ends
2026-06-30. Prices: same Yahoo dailies as E4/E6 (partial window reuse —
recorded in HYPOTHESES.md with mitigations)."""
import numpy as np
import pandas as pd

from crypto_trend import sharpe, max_dd, boot_p_dd
from phase2_e5_e4v2 import pf_halves
from portfolio_trend import load_universe, run_e6
from e7_carry import load_funding_daily, run_e7

SYMS = {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT"}
BODY_END, OOS_END = "2025-12-31", "2026-06-30"
METRIC_START = "2020-01-01"

if __name__ == "__main__":
    fund = {k: load_funding_daily("data/funding", v) for k, v in SYMS.items()}
    for k, f in fund.items():
        print(f"funding {k}: {f.index[0].date()} -> {f.index[-1].date()} "
              f"({len(f)} days)")
    px_all = load_universe()
    px_body = px_all.loc[:BODY_END]
    px_full = px_all.loc[:OOS_END]

    # ---- plateau over registered thresholds (body window) ----
    plat = {}
    for th in (0.10, 0.15, 0.20):
        tr, daily, eq, att = run_e7(px_body, fund, threshold=th)
        plat[th] = (tr, daily.loc[METRIC_START:], eq, att)
        print(f"th ±{th:.0%}: episodes {len(tr)}  sum(ret) "
              f"{tr['ret'].sum():+.4f}  final {eq.iloc[-1]:.3f}x")

    tr, daily, eq, att = plat[0.15]
    pf, h1, h2, wr = pf_halves(tr, "ret")
    body_dd = max_dd(eq.loc[METRIC_START:].values)
    print(f"\n== E7 body (±15%) == episodes {len(tr)}  WR {wr:.1%}  "
          f"PF {pf:.2f}  final {eq.iloc[-1]:.3f}x  maxDD {body_dd:.1%}  "
          f"Sharpe {sharpe(daily):.2f}")
    print(f"attribution: funding {att['funding']:+.4f}  "
          f"price {att['price']:+.4f}  costs {att['costs']:.4f}")

    # ---- correlation with E6 book (registered gate) ----
    _, d6, _ = run_e6(px_body)
    both = pd.concat([daily.rename("e7"), d6.rename("e6")], axis=1).dropna()
    both = both[(both["e7"] != 0) | (both["e6"] != 0)]
    corr = float(both["e7"].corr(both["e6"]))
    print(f"corr(E7, E6) daily on body: {corr:+.3f} (n={len(both)} days)")

    gates = {
        "n>=100": len(tr) >= 100,
        "PF>=1.2 (registered adaptation)": pf >= 1.2,
        "half1>0": h1 > 0,
        "half2>0": h2 > 0,
        "plateau 10/15/20 all>0":
            all(plat[t][0]["ret"].sum() > 0 for t in plat),
        "P(maxDD>40%)<10%": boot_p_dd(daily) < 0.10,
        "attribution funding>0 & > |price|":
            att["funding"] > 0 and att["funding"] > abs(att["price"]),
        "corr(E6)<=0.5": corr <= 0.5,
    }
    for k, v in gates.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    verdict = "PASS" if all(gates.values()) else "FAIL"
    print(f"E7 BODY VERDICT: {verdict} (n={len(tr)})")

    # ---- once-only OOS segment: 2026-01-01..2026-06-30 ----
    tr_f, daily_f, eq_f, att_f = run_e7(px_full, fund, threshold=0.15)
    oos_d = daily_f.loc["2026-01-01":OOS_END]
    oos_tr = tr_f[tr_f["exit"] >= pd.Timestamp("2026-01-01", tz="UTC")]
    oos_eq = (1 + oos_d).cumprod()
    print(f"\n== E7 OOS 2026H1 (once-only) == episodes exiting in segment: "
          f"{len(oos_tr)}  sum(ret) {oos_tr['ret'].sum():+.4f}  "
          f"segment return {oos_eq.iloc[-1] - 1:+.2%}  "
          f"Sharpe {sharpe(oos_d):.2f}  (n={len(oos_d)} days — small, "
          f"reported as registered)")
