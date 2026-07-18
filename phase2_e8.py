"""E8-R gate evaluation: ETHUSDT 15m trend continuation (registered
2026-07-18). ONE registered run. Body = 2022-01-01..2025-12-31 (gates);
2026-01-01..2026-06-30 = once-only OOS, reported separately.
Data: Binance Vision USDT-perp 15m klines + actual funding prints.
Costs: 6 bps/side all-in (pinned). P&L: USDT per 1 unit."""
import glob

import numpy as np
import pandas as pd

from phase2_e5_e4v2 import pf_halves
from portfolio_trend import load_universe, run_e6
from e8_trend import load_klines_15m, run_e8

BODY_END, OOS_START, OOS_END = "2025-12-31", "2026-01-01", "2026-06-30"


def load_fund_prints(dirpath: str, sym: str = "ETHUSDT") -> pd.DataFrame:
    fr = pd.concat([pd.read_csv(f) for f in
                    sorted(glob.glob(f"{dirpath}/{sym}-fundingRate-*.csv"))],
                   ignore_index=True)
    idx = pd.to_datetime(fr["calc_time"], unit="ms", utc=True)
    out = pd.DataFrame({"rate": fr["last_funding_rate"].astype(float).values},
                       index=idx).sort_index()
    return out[~out.index.duplicated(keep="first")]


if __name__ == "__main__":
    k = load_klines_15m("data/klines")
    prints = load_fund_prints("data/funding")
    print(f"klines: {len(k):,} bars {k.index[0]} -> {k.index[-1]}")
    print(f"funding prints: {len(prints):,}")
    k_body = k.loc[:BODY_END]
    k_full = k.loc[:OOS_END]
    p_body = prints.loc[:BODY_END]

    # ---- 9-cell registered plateau on the body window ----
    cells = {}
    for ag in (30.0, 35.0, 40.0):
        for tm in (3.5, 4.0, 5.0):
            tr, daily, att = run_e8(k_body, adx_gate=ag, trail_mult=tm,
                                    fund_prints=p_body)
            cells[(ag, tm)] = (tr, daily, att)
            print(f"ADX>{ag:.0f} trail {tm}x: n={len(tr):4d}  "
                  f"net {tr['pnl'].sum():+10.1f} USDT")

    tr, daily, att = cells[(35.0, 4.0)]
    pf, h1, h2, wr = pf_halves(tr, "pnl")
    wins = tr["pnl"][tr["pnl"] > 0]
    losses = tr["pnl"][tr["pnl"] <= 0]
    awal = (wins.mean() / abs(losses.mean())) if len(losses) else np.inf
    net = tr["pnl"].sum()
    top5 = tr["pnl"].nlargest(5).sum()
    conc = top5 / net if net > 0 else np.nan
    print(f"\n== E8-R body (ADX>35, 4x) == n={len(tr)}  WR {wr:.1%}  "
          f"PF {pf:.2f}  net {net:+.1f} USDT/unit  "
          f"half1 {h1:+.1f} / half2 {h2:+.1f}")
    print(f"skew signature: avg win/avg loss {awal:.2f}  "
          f"(prediction: WR<50% with ratio>1.5)")
    print(f"attribution: price {att['price']:+.1f}  funding "
          f"{att['funding']:+.1f}  costs {att['costs']:.1f}")
    print(f"top-5 trades / net: {conc:.1%}" if net > 0 else
          "top-5 concentration: n/a (net <= 0)")

    # ---- correlation with E6 sleeve (registered gate) ----
    px = load_universe().loc[:BODY_END]
    _, d6, _ = run_e6(px)
    e8d = daily.copy()
    both = pd.concat([e8d.rename("e8"), d6.rename("e6")], axis=1).dropna()
    both = both[(both["e8"] != 0) | (both["e6"] != 0)]
    corr = float(both["e8"].corr(both["e6"]))
    print(f"corr(E8, E6) daily on body: {corr:+.3f} (n={len(both)} days)")

    gates = {
        "PF>=1.2": pf >= 1.2,
        "n>=150": len(tr) >= 150,
        "half1>0": h1 > 0,
        "half2>0": h2 > 0,
        "plateau 9 cells all>0":
            all(c[0]["pnl"].sum() > 0 for c in cells.values()),
        "corr(E6)<=0.5": corr <= 0.5,
        "top5<=60% of net": (net > 0 and conc <= 0.60),
    }
    for kk, v in gates.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {kk}")
    verdict = "PASS" if all(gates.values()) else "FAIL"
    print(f"E8-R BODY VERDICT: {verdict} (n={len(tr)})")

    # ---- once-only OOS: 2026-01-01..2026-06-30 ----
    tr_f, daily_f, att_f = run_e8(k_full, adx_gate=35.0, trail_mult=4.0,
                                  fund_prints=prints)
    oos_tr = tr_f[tr_f["exit"] >= pd.Timestamp(OOS_START, tz="UTC")]
    oos_d = daily_f.loc[OOS_START:]
    print(f"\n== E8-R OOS 2026H1 (once-only) == trades exiting in segment: "
          f"{len(oos_tr)}  net {oos_tr['pnl'].sum():+.1f} USDT/unit  "
          f"(n={len(oos_tr)} — reported as registered)")
