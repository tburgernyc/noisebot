"""Phase 2: E16 (Capitulation Finder) registered evaluation. Single
registered run per HYPOTHESES.md -- do not re-run after seeing output.

Methodology note not fully pinned by the registration text (disclosed
here rather than silently decided): "per-asset independent episodes"
means BTC and ETH are each backtested as their own independent 100%-
capital book (using e16_capitulation.run_backtest per-asset). Trades
from both books are POOLED for the n/PF/half1-half2 statistics. For the
bootstrap-ruin and correlation gates, which need ONE daily-return series,
an equal-weighted (50/50) daily blend of the two books is used -- a
transparent, standard way to combine independent single-asset books,
chosen at evaluation time because the registration did not specify a
joint sizing rule (E16 has no covariance-based book construction the way
E6 does).

Primary/default cell for the full gate battery: time_stop_bars=10 (the
module's own coded default). Plateau cells (5/10/15) get a lighter
net-positive-only check, matching the E1 precedent (full gates on the
named/default parameter, plateau checks total-return sign only).
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from e16_capitulation import compute_signals, run_backtest, max_dd
from crypto_trend import boot_p_dd, sharpe, load_yahoo_daily, run_e4_voltarget
from portfolio_trend import load_universe, run_e6

BTC_PATH = "data/btc_usd_1d.json"
ETH_PATH = "data/eth_usd_1d.json"


def load(path):
    from e16_capitulation import load_yahoo_daily_ohlcv
    return load_yahoo_daily_ohlcv(path)


def run_asset(df, time_stop_bars):
    sig = compute_signals(df)
    trades, daily, eq = run_backtest(df, sig, time_stop_bars=time_stop_bars)
    return trades, daily, eq


def combined_metrics(trades_btc, trades_eth):
    all_ret = pd.concat([trades_btc["ret"], trades_eth["ret"]], ignore_index=True) \
        if len(trades_btc) and len(trades_eth) else \
        (trades_btc["ret"] if len(trades_btc) else trades_eth["ret"])
    n = len(all_ret)
    wins = all_ret[all_ret > 0]
    losses = all_ret[all_ret <= 0]
    pf = wins.sum() / max(1e-9, -losses.sum()) if len(losses) else float("inf")
    wr = len(wins) / n if n else float("nan")
    half = n // 2
    # order trades by combining on exit index proxy: BTC then ETH won't be
    # chronologically interleaved this way -- report each asset's own
    # half-split too, since a naive concat half-split is not meaningful
    # across two independent assets with different date ranges.
    return {"n": n, "pf": pf, "wr": wr, "total_ret": all_ret.sum(),
            "avg_ret": all_ret.mean() if n else float("nan")}


def half_split(trades):
    if not len(trades):
        return 0.0, 0.0
    half = len(trades) // 2
    return trades["ret"].iloc[:half].sum(), trades["ret"].iloc[half:].sum()


def combined_half_split(trades_btc, df_btc, trades_eth, df_eth):
    """Merge trades from both books by ACTUAL exit date (not naive
    BTC-then-ETH concatenation) for a chronologically honest combined
    half-split."""
    rows = []
    for t in trades_btc.itertuples():
        rows.append((df_btc.index[t.exit_i], t.ret))
    for t in trades_eth.itertuples():
        rows.append((df_eth.index[t.exit_i], t.ret))
    rows.sort(key=lambda r: r[0])
    rets = [r[1] for r in rows]
    half = len(rets) // 2
    return sum(rets[:half]), sum(rets[half:]), rows


if __name__ == "__main__":
    btc = load(BTC_PATH)
    eth = load(ETH_PATH)
    print(f"BTC: {len(btc)} bars {btc.index[0].date()}->{btc.index[-1].date()}")
    print(f"ETH: {len(eth)} bars {eth.index[0].date()}->{eth.index[-1].date()}")

    print("\n== PLATEAU (net total return by time_stop_bars, BTC+ETH pooled) ==")
    plateau_results = {}
    for ts in (5, 10, 15):
        tb, db, eb = run_asset(btc, ts)
        te, de, ee = run_asset(eth, ts)
        m = combined_metrics(tb, te)
        plateau_results[ts] = m
        print(f"time_stop={ts:2d}: n={m['n']:3d} total_ret={m['total_ret']:+.4f} "
              f"PF={m['pf']:.2f} WR={m['wr']:.1%}")

    print("\n== PRIMARY (time_stop_bars=10, full gate battery) ==")
    trades_btc, daily_btc, eq_btc = run_asset(btc, 10)
    trades_eth, daily_eth, eq_eth = run_asset(eth, 10)
    m = combined_metrics(trades_btc, trades_eth)
    h1_btc, h2_btc = half_split(trades_btc)
    h1_eth, h2_eth = half_split(trades_eth)
    print(f"n={m['n']} (BTC={len(trades_btc)}, ETH={len(trades_eth)})")
    print(f"PF={m['pf']:.3f}  WR={m['wr']:.1%}  total_ret={m['total_ret']:+.4f}")
    print(f"BTC-only half1={h1_btc:+.4f} half2={h2_btc:+.4f}")
    print(f"ETH-only half1={h1_eth:+.4f} half2={h2_eth:+.4f}")
    print(f"BTC book: final={eq_btc.iloc[-1]:.4f}x maxDD={max_dd(eq_btc.values):.1%}")
    print(f"ETH book: final={eq_eth.iloc[-1]:.4f}x maxDD={max_dd(eq_eth.values):.1%}")
    ch1, ch2, merged_rows = combined_half_split(trades_btc, btc, trades_eth, eth)
    print(f"COMBINED (chronologically merged by actual exit date, n={len(merged_rows)}): "
          f"half1={ch1:+.4f} half2={ch2:+.4f}")

    # Equal-weighted blended daily series (union of dates, missing->0 on
    # days the OTHER asset's series doesn't cover -- both start well
    # before either asset's data ends, and ETH data postdates BTC's
    # earliest bars, so align on the intersection where both books exist
    # simultaneously to avoid overweighting the BTC-only early period).
    joint_idx = daily_btc.index.intersection(daily_eth.index)
    blended = 0.5 * daily_btc.reindex(joint_idx).fillna(0.0) + \
              0.5 * daily_eth.reindex(joint_idx).fillna(0.0)
    blended_eq = (1 + blended).cumprod()
    print(f"\nBlended (50/50, overlapping window {joint_idx[0].date()}->{joint_idx[-1].date()}, "
          f"n={len(joint_idx)} days): final={blended_eq.iloc[-1]:.4f}x "
          f"maxDD={max_dd(blended_eq.values):.1%} Sharpe={sharpe(blended):.2f}")

    p_dd = boot_p_dd(blended, thresh=0.40, n_paths=10_000, seed=7)
    print(f"Bootstrap (10k paths, blended daily): P(maxDD>40%) = {p_dd:.1%}")

    print("\n== Correlation gate (vs E4-v2 and E6, reconstructed from the same data) ==")
    btc_oc = load_yahoo_daily(BTC_PATH)
    _, daily_e4v2, _ = run_e4_voltarget(btc_oc, lookback=28, vol_target=0.15, vol_win=30)
    px = load_universe(paths={"BTC": BTC_PATH, "ETH": ETH_PATH, "SOL": "data/sol_usd_1d.json"})
    _, daily_e6, _ = run_e6(px)

    def corr(a, b):
        idx = a.index.intersection(b.index)
        return float(a.reindex(idx).corr(b.reindex(idx))), len(idx)

    corr_e4v2, n_e4v2 = corr(blended, daily_e4v2)
    corr_e6, n_e6 = corr(blended, daily_e6)
    print(f"corr(E16 blended, E4-v2) = {corr_e4v2:.4f}  (n={n_e4v2} overlapping days)")
    print(f"corr(E16 blended, E6)    = {corr_e6:.4f}  (n={n_e6} overlapping days)")

    print("\n== Gate summary ==")
    print(f"n>=100: {m['n']} -> {'PASS' if m['n'] >= 100 else 'FAIL'}")
    print(f"PF>1.3: {m['pf']:.3f} -> {'PASS' if m['pf'] > 1.3 else 'FAIL'}")
    both_halves = ch1 > 0 and ch2 > 0
    print(f"both-halves (combined, chronologically merged): "
          f"half1={ch1:+.4f} half2={ch2:+.4f} -> {'PASS' if both_halves else 'FAIL'}")
    plateau_pass = all(plateau_results[ts]["total_ret"] > 0 for ts in (5, 10, 15))
    print(f"plateau all>0: {[round(plateau_results[ts]['total_ret'],4) for ts in (5,10,15)]} "
          f"-> {'PASS' if plateau_pass else 'FAIL'}")
    print(f"bootstrap P(maxDD>40%)<10%: {p_dd:.1%} -> {'PASS' if p_dd < 0.10 else 'FAIL'}")
    corr_pass = abs(corr_e4v2) <= 0.5 and abs(corr_e6) <= 0.5
    print(f"correlation <=0.5 vs E4-v2/E6 (low correlation hoped for): "
          f"{corr_e4v2:.3f} / {corr_e6:.3f} -> {'PASS' if corr_pass else 'FAIL'}")
