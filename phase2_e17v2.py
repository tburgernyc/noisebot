"""Phase 2: E17-v2 (E17 signal, vol-targeted sizing) registered
evaluation. Single registered run per HYPOTHESES.md -- do not re-run
after seeing output.

Primary/default cell: vol_target=0.15 (E4-v2's registered value, reused
for direct comparability). Plateau cells (0.10/0.15/0.20) get a lighter
net-positive-only check, matching the E1/E17 precedent.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from e17_pivot_structure import compute_signals, run_backtest_voltarget, max_dd
from crypto_trend import boot_p_dd, sharpe, load_yahoo_daily, run_e4_voltarget
from portfolio_trend import load_universe, run_e6

BTC_PATH = "data/btc_usd_1d.json"
ETH_PATH = "data/eth_usd_1d.json"
SOL_PATH = "data/sol_usd_1d.json"


def load(path):
    from e17_pivot_structure import load_yahoo_daily_ohlcv
    return load_yahoo_daily_ohlcv(path)


def half_split(trades):
    if not len(trades):
        return 0.0, 0.0
    half = len(trades) // 2
    return trades["ret"].iloc[:half].sum(), trades["ret"].iloc[half:].sum()


if __name__ == "__main__":
    btc = load(BTC_PATH)
    print(f"BTC: {len(btc)} bars {btc.index[0].date()}->{btc.index[-1].date()}")
    sig = compute_signals(btc, pivot_left=10, pivot_right=10)

    print("\n== PLATEAU (net total return by vol_target, pivot_window=10 fixed) ==")
    plateau_results = {}
    for vt in (0.10, 0.15, 0.20):
        trades, daily, eq = run_backtest_voltarget(btc, sig, vol_target=vt, vol_win=30)
        total = trades["ret"].sum() if len(trades) else 0.0
        plateau_results[vt] = total
        print(f"vol_target={vt:.2f}: n={len(trades):3d} total_ret={total:+.4f} "
              f"final={eq.iloc[-1]:.3f}x maxDD={max_dd(eq.values):.1%}")

    print("\n== PRIMARY (vol_target=0.15, full gate battery, long/flat) ==")
    trades, daily, eq = run_backtest_voltarget(btc, sig, vol_target=0.15, vol_win=30)
    n = len(trades)
    wins = trades["ret"][trades["ret"] > 0] if n else pd.Series(dtype=float)
    losses = trades["ret"][trades["ret"] <= 0] if n else pd.Series(dtype=float)
    pf = wins.sum() / max(1e-9, -losses.sum()) if len(losses) else float("inf")
    wr = len(wins) / n if n else float("nan")
    h1, h2 = half_split(trades)
    print(f"n={n}  PF={pf:.3f}  WR={wr:.1%}  total_ret={trades['ret'].sum() if n else 0:+.4f}")
    print(f"half1={h1:+.4f}  half2={h2:+.4f}")
    print(f"final={eq.iloc[-1]:.4f}x  maxDD={max_dd(eq.values):.1%}")

    strat_sharpe = sharpe(daily)
    bh_daily = btc["close"].pct_change().dropna()
    bh_sharpe = sharpe(bh_daily)
    print(f"Strategy Sharpe={strat_sharpe:.3f}  Buy-hold Sharpe={bh_sharpe:.3f}")

    p_dd = boot_p_dd(daily, thresh=0.40, n_paths=10_000, seed=7)
    print(f"Bootstrap (10k paths): P(maxDD>40%) = {p_dd:.1%}")

    print("\n== Correlation gate (vs E4-v2 and E6, reconstructed from the same data) ==")
    btc_oc = load_yahoo_daily(BTC_PATH)
    _, daily_e4v2, _ = run_e4_voltarget(btc_oc, lookback=28, vol_target=0.15, vol_win=30)
    px = load_universe(paths={"BTC": BTC_PATH, "ETH": ETH_PATH, "SOL": SOL_PATH})
    _, daily_e6, _ = run_e6(px)

    def corr(a, b):
        idx = a.index.intersection(b.index)
        return float(a.reindex(idx).corr(b.reindex(idx))), len(idx)

    corr_e4v2, n_e4v2 = corr(daily, daily_e4v2)
    corr_e6, n_e6 = corr(daily, daily_e6)
    print(f"corr(E17-v2, E4-v2) = {corr_e4v2:.4f}  (n={n_e4v2} overlapping days)")
    print(f"corr(E17-v2, E6)    = {corr_e6:.4f}  (n={n_e6} overlapping days)")

    print("\n== Gate summary (long/flat) ==")
    print(f"n>=100: {n} -> {'PASS' if n >= 100 else 'FAIL'}")
    print(f"PF>1.3: {pf:.3f} -> {'PASS' if pf > 1.3 else 'FAIL'}")
    print(f"both-halves: half1={h1:+.4f} half2={h2:+.4f} -> "
          f"{'PASS' if (h1 > 0 and h2 > 0) else 'FAIL'}")
    plateau_pass = all(v > 0 for v in plateau_results.values())
    print(f"plateau all>0: {plateau_results} -> {'PASS' if plateau_pass else 'FAIL'}")
    print(f"bootstrap P(maxDD>40%)<10%: {p_dd:.1%} -> {'PASS' if p_dd < 0.10 else 'FAIL'}")
    print(f"Sharpe>=buy-hold: {strat_sharpe:.3f} vs {bh_sharpe:.3f} -> "
          f"{'PASS' if strat_sharpe >= bh_sharpe else 'FAIL'}")
    print(f"correlation (reported/interpreted, not a hard pass/fail here): "
          f"{corr_e4v2:.3f} vs E4-v2, {corr_e6:.3f} vs E6")
