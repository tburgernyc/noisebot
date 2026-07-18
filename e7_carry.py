"""E7 registered module: perp funding-rate carry, standalone (HYPOTHESES.md
2026-07-18). Pure logic + loaders. No execution code.

Sign convention: positive funding -> longs pay shorts. Position w > 0 is
long (pays funding), w < 0 is short (receives). Funding P&L per print =
-w * rate. Engine mirrors the E6 conventions: decide at day t close,
weight change costed on |dw| (0.10%/side all-in), price P&L = held *
next-day close-to-close return, funding P&L = held-weighted actual
prints of the next day. Episodes are per-asset flat-to-flat.
"""
from __future__ import annotations
import glob

import numpy as np
import pandas as pd

COST = 0.0010          # per side, all-in (registered fixture)
VOL_TARGET = 0.15      # E4-v2 convention
VOL_WIN = 30
LOOKBACK_D = 3         # trailing days for funding mean (FIXED)
HOURS_YEAR = 8760.0


def load_funding_daily(dirpath: str, sym: str) -> pd.DataFrame:
    """All monthly CSVs for one symbol -> daily DataFrame (UTC dates):
    ann_mean = mean annualized rate of the day's prints,
    day_sum  = plain sum of the day's rates (for P&L accrual)."""
    rows = []
    for f in sorted(glob.glob(f"{dirpath}/{sym}-fundingRate-*.csv")):
        df = pd.read_csv(f)
        rows.append(df)
    if not rows:
        raise FileNotFoundError(f"no funding CSVs for {sym} in {dirpath}")
    fr = pd.concat(rows, ignore_index=True)
    ts = pd.to_datetime(fr["calc_time"], unit="ms", utc=True)
    rate = fr["last_funding_rate"].astype(float)
    ann = rate * (HOURS_YEAR / fr["funding_interval_hours"].astype(float))
    d = pd.DataFrame({"rate": rate.values, "ann": ann.values},
                     index=ts).sort_index()
    day = d.index.normalize()
    out = pd.DataFrame({"ann_mean": d["ann"].groupby(day).mean(),
                        "day_sum": d["rate"].groupby(day).sum()})
    return out[~out.index.duplicated(keep="first")]


def run_e7(px: pd.DataFrame, fund: dict[str, pd.DataFrame],
           threshold: float = 0.15, vol_target: float = VOL_TARGET):
    """px: daily closes (UTC-normalized index), columns = asset names.
    fund: asset -> daily funding frame (ann_mean, day_sum).
    Returns (trades_df, daily_net, equity, attribution dict)."""
    names = list(px.columns)
    N, T = len(names), len(px)
    P = px.values
    idx = px.index
    valid = ~np.isnan(P)
    R = np.zeros((T, N))
    for i in range(N):
        c = P[:, i]
        with np.errstate(invalid="ignore"):
            R[1:, i] = np.where(valid[1:, i] & valid[:-1, i],
                                c[1:] / c[:-1] - 1.0, 0.0)
    Fmean = np.full((T, N), np.nan)   # trailing LOOKBACK_D mean ann funding
    Fsum = np.zeros((T, N))           # day's funding rate sum (accrual)
    for i, nm in enumerate(names):
        f = fund[nm].reindex(idx)
        Fmean[:, i] = f["ann_mean"].rolling(LOOKBACK_D, min_periods=LOOKBACK_D).mean().values
        Fsum[:, i] = f["day_sum"].fillna(0.0).values
    ret_df = pd.DataFrame(R, index=idx, columns=names)
    sig_ann = (ret_df.rolling(VOL_WIN).std() * np.sqrt(365)).values

    eq = np.ones(T)
    held = np.zeros(N)
    trades = []
    ep_ret = np.zeros(N)
    ep_open = np.zeros(N, dtype=bool)
    cum_fund, cum_px, cum_cost = 0.0, 0.0, 0.0
    for t in range(1, T - 1):
        w = np.zeros(N)
        for i in range(N):
            F, s = Fmean[t, i], sig_ann[t, i]
            if np.isnan(F) or np.isnan(s) or s < 0.01 or not valid[t, i]:
                continue
            if F > threshold:
                w[i] = -min(1.0, vol_target / s)   # short: collect funding
            elif F < -threshold:
                w[i] = +min(1.0, vol_target / s)   # long: collect funding
        tot = np.abs(w).sum()
        if tot > 1.0:
            w *= 1.0 / tot
        cost = 0.0
        for i in range(N):
            if w[i] != held[i]:
                ci = abs(w[i] - held[i]) * COST
                cost += ci
                ep_ret[i] -= ci
                held[i] = w[i]
        pnl_px = float(held @ R[t + 1])
        pnl_fund = float(-(held @ Fsum[t + 1]))
        cum_px += pnl_px
        cum_fund += pnl_fund
        cum_cost += cost
        eq[t + 1] = eq[t] * (1.0 + pnl_px + pnl_fund - cost)
        for i in range(N):
            if held[i] != 0.0:
                ep_open[i] = True
                ep_ret[i] += held[i] * R[t + 1, i] - held[i] * Fsum[t + 1, i]
            elif ep_open[i]:
                trades.append({"asset": names[i], "ret": ep_ret[i],
                               "exit": idx[t + 1]})
                ep_ret[i], ep_open[i] = 0.0, False
    for i in range(N):
        if ep_open[i]:
            trades.append({"asset": names[i], "ret": ep_ret[i],
                           "exit": idx[-1]})
    daily = pd.Series(eq, index=idx).pct_change().dropna()
    attribution = {"funding": cum_fund, "price": cum_px, "costs": cum_cost}
    return pd.DataFrame(trades), daily, pd.Series(eq, index=idx), attribution
