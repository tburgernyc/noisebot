"""E19-v2 gate evaluation: E19's delta-neutral perp funding-rate harvest
with the perp leg priced off REAL Binance mark-price history
(data/perp_mark/) instead of the spot proxy (registered 2026-07-26).
Single registered run per HYPOTHESES.md -- do not re-run after seeing
output. Structure mirrors phase2_e19.py exactly; only the data/engine
differ (run_e19_v2/load_mark_price_daily instead of run_e19).

Windowing: same METRIC_START convention as phase2_e19.py/phase2_e7.py --
gates/Sharpe/bootstrap/correlation computed only from 2020-01-01 onward.

Primary/default cell: entry=8%/exit=3% (unchanged from E19). Plateau
cells (6/2, 8/3, 12/5) get a net-positive-only check.
"""
from __future__ import annotations
import pandas as pd

from crypto_trend import sharpe, max_dd, boot_p_dd, run_e4_voltarget, load_yahoo_daily
from portfolio_trend import load_universe, run_e6
from e7_carry import load_funding_daily
from e19_funding_basis import run_e19_v2, load_mark_price_daily

SYMS = {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT"}
PATHS = {"BTC": "data/btc_usd_1d.json", "ETH": "data/eth_usd_1d.json",
         "SOL": "data/sol_usd_1d.json"}
METRIC_START = "2020-01-01"
PLATEAU = [(0.06, 0.02), (0.08, 0.03), (0.12, 0.05)]
PRIMARY = (0.08, 0.03)


def half_split_by_exit(trades: pd.DataFrame):
    if not len(trades):
        return 0.0, 0.0
    t = trades.sort_values("exit").reset_index(drop=True)
    half = len(t) // 2
    return float(t["ret"].iloc[:half].sum()), float(t["ret"].iloc[half:].sum())


def pf_of(trades: pd.DataFrame):
    if not len(trades):
        return float("nan"), float("nan")
    wins = trades["ret"][trades["ret"] > 0]
    losses = trades["ret"][trades["ret"] <= 0]
    pf = wins.sum() / max(1e-9, -losses.sum()) if len(losses) else float("inf")
    wr = len(wins) / len(trades)
    return pf, wr


if __name__ == "__main__":
    fund = {k: load_funding_daily("data/funding", v) for k, v in SYMS.items()}
    for k, f in fund.items():
        print(f"funding {k}: {f.index[0].date()} -> {f.index[-1].date()} ({len(f)} days)")
    px_spot = load_universe(paths=PATHS)
    px_perp = {k: load_mark_price_daily("data/perp_mark", v) for k, v in SYMS.items()}
    for k, s in px_perp.items():
        print(f"perp mark {k}: {s.index[0].date()} -> {s.index[-1].date()} ({len(s)} days)")
    print(f"price universe (spot): {px_spot.index[0].date()} -> {px_spot.index[-1].date()} "
          f"({len(px_spot)} rows, cols={list(px_spot.columns)})")

    print("\n== PLATEAU (net total return by entry/exit threshold pair) ==")
    plateau_results = {}
    for entry, exit_thr in PLATEAU:
        trades, daily, eq, per_asset, att = run_e19_v2(px_spot, px_perp, fund,
                                                        entry=entry, exit_thr=exit_thr)
        total = float(trades["ret"].sum()) if len(trades) else 0.0
        plateau_results[(entry, exit_thr)] = total
        print(f"entry={entry:.0%}/exit={exit_thr:.0%}: n={len(trades):3d} "
              f"total_ret={total:+.4f} final={eq.iloc[-1]:.3f}x")

    print(f"\n== PRIMARY (entry={PRIMARY[0]:.0%}/exit={PRIMARY[1]:.0%}, full gate battery) ==")
    trades, daily, eq, per_asset, att = run_e19_v2(px_spot, px_perp, fund,
                                                    entry=PRIMARY[0], exit_thr=PRIMARY[1])
    n = len(trades)
    pf, wr = pf_of(trades)
    h1, h2 = half_split_by_exit(trades)
    print(f"n={n}  PF={pf:.3f}  WR={wr:.1%}  total_ret={trades['ret'].sum() if n else 0:+.4f}")
    print(f"half1={h1:+.4f}  half2={h2:+.4f}")
    for nm in SYMS:
        t_a, d_a, e_a, att_a = per_asset[nm]
        print(f"  {nm}: n={len(t_a)}  final={e_a.iloc[-1]:.3f}x  "
              f"funding={att_a['funding']:+.4f}  price={att_a['price']:+.4f}  "
              f"costs={att_a['costs']:.4f}")

    daily_m = daily.loc[METRIC_START:]
    eq_m = eq.loc[METRIC_START:]
    print(f"\nmetric window: {daily_m.index[0].date()} -> {daily_m.index[-1].date()} "
          f"({len(daily_m)} days)")
    print(f"final={eq.iloc[-1]:.4f}x  maxDD(metric window)={max_dd(eq_m.values):.1%}")
    strat_sharpe = sharpe(daily_m)
    print(f"Sharpe (metric window, descriptive -- not gated for a market-neutral book)"
          f"={strat_sharpe:.3f}")

    p_dd = boot_p_dd(daily_m, thresh=0.40, n_paths=10_000, seed=7)
    print(f"Bootstrap (10k paths, metric window): P(maxDD>40%) = {p_dd:.1%}")

    print(f"\nattribution total (sum of per-asset attribution / n_assets): {att}")
    attr_gate = abs(att["price"]) < 0.20 * abs(att["funding"]) if att["funding"] != 0 else False

    print("\n== Correlation gate (vs E4-v2 and E6, reconstructed from the same data) ==")
    btc_oc = load_yahoo_daily(PATHS["BTC"])
    _, daily_e4v2, _ = run_e4_voltarget(btc_oc, lookback=28, vol_target=0.15, vol_win=30)
    _, daily_e6, _ = run_e6(px_spot)

    def corr(a, b):
        idx = a.index.intersection(b.index)
        return float(a.reindex(idx).corr(b.reindex(idx))), len(idx)

    corr_e4v2, n_e4v2 = corr(daily_m, daily_e4v2)
    corr_e6, n_e6 = corr(daily_m, daily_e6)
    print(f"corr(E19-v2, E4-v2) = {corr_e4v2:.4f}  (n={n_e4v2} overlapping days, metric window)")
    print(f"corr(E19-v2, E6)    = {corr_e6:.4f}  (n={n_e6} overlapping days, metric window)")

    print("\n== Gate summary ==")
    print(f"n>=100: {n} -> {'PASS' if n >= 100 else 'FAIL'}")
    print(f"PF>1.3: {pf:.3f} -> {'PASS' if pf > 1.3 else 'FAIL'}")
    print(f"both-halves: half1={h1:+.4f} half2={h2:+.4f} -> "
          f"{'PASS' if (h1 > 0 and h2 > 0) else 'FAIL'}")
    plateau_pass = all(v > 0 for v in plateau_results.values())
    print(f"plateau all>0: { {f'{e:.0%}/{x:.0%}': round(v, 4) for (e, x), v in plateau_results.items()} } "
          f"-> {'PASS' if plateau_pass else 'FAIL'}")
    print(f"bootstrap P(maxDD>40%)<10%: {p_dd:.1%} -> {'PASS' if p_dd < 0.10 else 'FAIL'}")
    print(f"attribution |price|<20%|funding|: price={att['price']:+.4f} "
          f"funding={att['funding']:+.4f} ratio={abs(att['price'])/max(1e-9,abs(att['funding'])):.1%} "
          f"-> {'PASS' if attr_gate else 'FAIL'}")
    corr_gate = (abs(corr_e4v2) <= 0.5) and (abs(corr_e6) <= 0.5)
    print(f"correlation<=0.5 (both E4-v2 and E6): {corr_e4v2:.3f}/{corr_e6:.3f} -> "
          f"{'PASS' if corr_gate else 'FAIL'}")

    all_gates = {
        "n>=100": n >= 100,
        "PF>1.3": pf > 1.3,
        "both_halves": h1 > 0 and h2 > 0,
        "plateau": plateau_pass,
        "bootstrap": p_dd < 0.10,
        "attribution": attr_gate,
        "correlation": corr_gate,
    }
    verdict = "PASS" if all(all_gates.values()) else "FAIL"
    n_pass = sum(all_gates.values())
    print(f"\nE19-v2 VERDICT: {verdict} ({n_pass}/{len(all_gates)} gates)")

    # Specific check flagged in the registration: was any asset hedged
    # through the 2022-11 FTX-collapse window, and what did that episode
    # realize? Descriptive only, not a gate.
    print("\n== FTX-collapse window check (descriptive, not gated) ==")
    for nm in SYMS:
        t_a = per_asset[nm][0]
        if not len(t_a):
            continue
        around = t_a[(t_a["entry"] <= "2022-11-09") & (t_a["exit"] >= "2022-11-09")]
        if len(around):
            print(f"  {nm}: hedged through 2022-11-09 -- {around.to_dict('records')}")
        else:
            print(f"  {nm}: not hedged on 2022-11-09")
