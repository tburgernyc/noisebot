"""E6: multi-asset crypto trend sleeve (registered). BTC/ETH/SOL daily,
blended 14/28/56 trend scores, EWMA(0.94) vol+cov, 15% book vol target,
no leverage, 5% band rebalancing, per-asset episodes for PF/n."""
from __future__ import annotations
import numpy as np
import pandas as pd

from crypto_trend import load_yahoo_daily, SLIP, FEE

LAM, MIN_OBS, ENTER_OBS, BAND, TARGET = 0.94, 60, 120, 0.05, 0.15


def load_universe(paths=None):
    paths = paths or {"BTC": "data/btc_1d.json", "ETH": "data/eth_1d.json",
                      "SOL": "data/sol_1d.json"}
    dfs = {k: load_yahoo_daily(v) for k, v in paths.items()}
    px = pd.DataFrame({k: v["close"] for k, v in dfs.items()})
    px.index = px.index.normalize()
    return px[~px.index.duplicated(keep="first")].sort_index()


def run_e6(px: pd.DataFrame, lookbacks=(14, 28, 56), vol_target=TARGET):
    names = list(px.columns)
    N, T = len(names), len(px)
    P = px.values
    R = np.zeros((T, N))
    valid = ~np.isnan(P)
    obs_count = valid.cumsum(axis=0)
    for i in range(N):
        col = P[:, i]
        with np.errstate(invalid="ignore"):
            R[1:, i] = np.where(valid[1:, i] & valid[:-1, i],
                                col[1:] / col[:-1] - 1.0, 0.0)
    # EWMA covariance (daily), scores, weights
    cov = np.zeros((N, N))
    eq = np.ones(T)
    held = np.zeros(N)
    trades = {n: [] for n in names}
    ep_ret = np.zeros(N); ep_open = np.zeros(N, dtype=bool)
    daily_idx = []
    for t in range(1, T - 1):
        rt = R[t][:, None]
        cov = LAM * cov + (1 - LAM) * (rt @ rt.T)
        # scores
        s = np.zeros(N)
        for i in range(N):
            if obs_count[t, i] < ENTER_OBS or np.isnan(P[t, i]):
                continue
            sc = 0.0
            for L in lookbacks:
                if t - L >= 0 and not np.isnan(P[t - L, i]):
                    sc += 1.0 if P[t, i] > P[t - L, i] else 0.0
            s[i] = sc / len(lookbacks)
        sig_i = np.sqrt(np.maximum(np.diag(cov), 1e-12) * 365)
        active = (s > 0) & (obs_count[t] >= ENTER_OBS) & (sig_i > 0.01)
        w = np.zeros(N)
        if active.any():
            wt = np.where(active, s / sig_i, 0.0)
            var_p = float(wt @ cov @ wt) * 365
            if var_p > 0:
                w = wt * (vol_target / np.sqrt(var_p))
            tot = w.sum()
            if tot > 1.0:
                w /= tot
        # band rebalance + costs
        cost = 0.0
        for i in range(N):
            if abs(w[i] - held[i]) > BAND or (w[i] == 0 and held[i] > 0):
                cost_i = abs(w[i] - held[i]) * (FEE + SLIP)
                cost += cost_i
                ep_ret[i] -= cost_i
                held[i] = w[i]
        # equity step + episode tracking
        pnl = float(held @ R[t + 1])
        eq[t + 1] = eq[t] * (1.0 + pnl - cost)
        for i in range(N):
            if held[i] > 0:
                if not ep_open[i]:
                    ep_open[i] = True
                ep_ret[i] += held[i] * R[t + 1, i]
            elif ep_open[i]:
                trades[names[i]].append(ep_ret[i])
                ep_ret[i], ep_open[i] = 0.0, False
    for i in range(N):
        if ep_open[i]:
            trades[names[i]].append(ep_ret[i])
    globals()["LAST_HELD"] = {names[i]: round(float(held[i]), 4) for i in range(N)}
    rows = [{"asset": k, "ret": r} for k, v in trades.items() for r in v]
    daily = pd.Series(eq, index=px.index).pct_change().dropna()
    return pd.DataFrame(rows), daily, pd.Series(eq, index=px.index)
