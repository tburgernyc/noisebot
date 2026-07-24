"""termstructure_backtest.py — portfolio assembly + Phase-2 gate evaluation
for E9 (commodity basis-momentum), E11 (commodity hedger-positioning),
E12 (FX carry). Imports the pure logic in term_structure.py and the
loaders; contains NO signal tuning. Running it on the registered windows
IS the one-shot evaluation, so it is exercised end-to-end on SYNTHETIC
data first (test_backtest.py).

No-lookahead contract enforced here: a month-end signal on date t drives
positions only STRICTLY AFTER t (searchsorted side='left' - 1), and the
vol-target multiplier is shifted one day inside term_structure.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import term_structure as ts


# ---- wide daily front returns ----------------------------------------

def daily_front_returns(panels: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """{root: tidy panel} -> wide (date x root) NO-SPLICE front daily
    returns, aligned on the union of trading days (missing = 0 P&L)."""
    series = {r: ts.nearby_return_series(p, "front") for r, p in panels.items()}
    wide = pd.DataFrame(series).sort_index()
    return wide


# ---- signal builders (month-end wide) --------------------------------

def e9_signal(panels: dict[str, pd.DataFrame], lookback_m: int) -> pd.DataFrame:
    """Basis-momentum per root at each month-end."""
    cols = {}
    for r, p in panels.items():
        fr = ts.monthly_returns(ts.nearby_return_series(p, "front"))
        sr = ts.monthly_returns(ts.nearby_return_series(p, "second"))
        cols[r] = ts.basis_momentum(fr, sr, lookback_m)
    return pd.DataFrame(cols).sort_index()


def e12_signal(curves: dict[str, pd.DataFrame], smoothing_m: int) -> pd.DataFrame:
    """FX carry per currency at each month-end, trailing `smoothing_m`-month
    mean of the annualized term-structure carry."""
    cols = {}
    for r, c in curves.items():
        raw = ts.fx_carry(c["front_close"], c["second_close"], c["dt_years"])
        cols[r] = raw.rolling(smoothing_m, min_periods=1).mean()
    return pd.DataFrame(cols).sort_index()


# ---- book construction ------------------------------------------------

def _daily_weights(legw: pd.DataFrame, daily_index: pd.DatetimeIndex
                   ) -> pd.DataFrame:
    """Broadcast month-end leg weights to daily, EFFECTIVE STRICTLY AFTER
    the signal date (no same-day lookahead)."""
    me = legw.index.sort_values()
    pos = np.searchsorted(me.values, daily_index.values, side="left") - 1
    w = pd.DataFrame(0.0, index=daily_index, columns=legw.columns)
    valid = pos >= 0
    w.loc[valid, :] = legw.reindex(me).iloc[pos[valid]].values
    return w


def run_book(signal_me: pd.DataFrame, daily_ret: pd.DataFrame,
             tercile: bool = True, n_long: int = 3, n_short: int = 3,
             bps_per_side: float = 5.0, target_vol: float = 0.15,
             gross_cap: float = 2.0) -> dict:
    """Assemble the long/short, vol-targeted, cost-charged book."""
    legw = ts.cross_sectional_ls(signal_me, n_long, n_short, tercile)
    roots = daily_ret.columns
    legw = legw.reindex(columns=roots).fillna(0.0)
    w_daily = _daily_weights(legw, daily_ret.index)                # unscaled
    dr = daily_ret.reindex(w_daily.index).fillna(0.0)

    gross_unscaled = (w_daily * dr).sum(axis=1)
    mult = ts.vol_target_scale(gross_unscaled, target_vol, gross_cap=gross_cap)
    w_scaled = w_daily.mul(mult, axis=0).fillna(0.0)
    gross = (w_scaled * dr).sum(axis=1)
    costs = ts.apply_costs(w_scaled, bps_per_side)
    net = (gross - costs).dropna()

    return dict(net=net, legw=legw, w_daily=w_daily, w_scaled=w_scaled,
                daily_ret=dr, bps=bps_per_side)


def episode_pnl(book: dict) -> pd.Series:
    """Per-root episode P&L stream (unscaled leg contribution over each
    constant-sign run, minus a round-trip cost). Feeds PF and n."""
    w = book["w_daily"]
    dr = book["daily_ret"]
    contrib = w * dr
    pnls = []
    for ep in ts.extract_episodes(w):
        root = ep["root"]
        mask = (contrib.index > ep["start"]) & (contrib.index <= ep["end"])
        seg = contrib.loc[mask, root].sum()
        avg_w = w.loc[(w.index >= ep["start"]) & (w.index <= ep["end"]),
                      root].abs().mean()
        # use the book's registered per-side cost (was hard-coded 5.0 bps —
        # gate-audit fix 2026-07-24; E12's LOGGED run predated this and used
        # 5.0 bps, which is CONSERVATIVE vs its registered 3.0 bps and was
        # NOT re-run, per the one-shot kill criterion).
        bps = book.get("bps", 5.0)
        rt_cost = 2.0 * (bps / 1e4) * (avg_w if np.isfinite(avg_w) else 0.0)
        pnls.append(seg - rt_cost)
    return pd.Series(pnls, dtype="float64")


# ---- benchmark --------------------------------------------------------

def long_only_benchmark(daily_ret: pd.DataFrame, target_vol: float = 0.15,
                        gross_cap: float = 2.0) -> pd.Series:
    """Equal-weight long-only basket of the same universe, vol-targeted —
    the hardest honest Sharpe benchmark (must beat passive long beta)."""
    n = daily_ret.shape[1]
    w = pd.DataFrame(1.0 / n, index=daily_ret.index, columns=daily_ret.columns)
    dr = daily_ret.fillna(0.0)
    gross_unscaled = (w * dr).sum(axis=1)
    mult = ts.vol_target_scale(gross_unscaled, target_vol, gross_cap=gross_cap)
    return ((w.mul(mult, axis=0)) * dr).sum(axis=1).dropna()


# ---- gate evaluation --------------------------------------------------

def evaluate_gates(net: pd.Series, ep_pnl: pd.Series, benchmark: pd.Series,
                   plateau_totals: dict, extra_gates: dict | None = None,
                   pf_min: float = 1.3) -> dict:
    """Return the E6-adapted gate panel with pass/fail and every metric's n."""
    net = net.dropna()
    half = len(net) // 2
    h1, h2 = net.iloc[:half].sum(), net.iloc[half:].sum()
    eq = (1.0 + net).cumprod()
    p_blow = ts.bootstrap_p_maxdd(net, 0.40)
    s_strat = ts.sharpe(net)
    s_bench = ts.sharpe(benchmark.reindex(net.index).dropna())
    pf = ts.profit_factor(ep_pnl)
    n = len(ep_pnl)

    gates = {
        "n>=100": (n >= 100, n),
        "PF>1.3": (pf > pf_min, round(pf, 3)),
        "both_halves>0": (h1 > 0 and h2 > 0, (round(h1, 4), round(h2, 4))),
        "plateau_all>0": (all(v > 0 for v in plateau_totals.values()),
                          {k: round(v, 4) for k, v in plateau_totals.items()}),
        "P(maxDD>40%)<10%": (p_blow < 0.10, round(p_blow, 4)),
        "Sharpe>=benchmark": (s_strat >= s_bench,
                              (round(s_strat, 3), round(s_bench, 3))),
    }
    if extra_gates:
        gates.update(extra_gates)
    verdict = "PASS" if all(g[0] for g in gates.values()) else "FAIL"
    return dict(verdict=verdict, gates=gates, n=n, PF=round(pf, 3),
                Sharpe=round(s_strat, 3), maxDD=round(ts.max_drawdown(eq), 4),
                final_equity=round(float(eq.iloc[-1]), 3))
