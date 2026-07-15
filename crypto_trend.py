"""E4 registered module: slow BTC trend, long-only spot (HYPOTHESES.md).
Daily bars. Signal: trailing L-day return > 0 -> long, else flat.
Fill next open, 10 bps adverse slippage + 0.35% fee per side.
Pure logic + loader. No broker code."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd

SLIP, FEE = 0.0010, 0.0035


def load_yahoo_daily(path: str) -> pd.DataFrame:
    r = json.load(open(path))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    df = pd.DataFrame({"open": q["open"], "close": q["close"]},
                      index=pd.to_datetime(r["timestamp"], unit="s", utc=True))
    df = df.dropna().sort_index()
    return df[~df.index.duplicated(keep="first")]


def run_e4(df: pd.DataFrame, lookback: int = 28):
    """Returns (trades_df, daily_net_returns, equity_series)."""
    o, c = df["open"].values, df["close"].values
    n = len(df)
    sig = np.zeros(n, dtype=int)
    for t in range(lookback, n):
        sig[t] = 1 if c[t] > c[t - lookback] else 0
    cash, btc, pos = 1.0, 0.0, 0
    equity = np.ones(n)
    trades, entry_eq = [], 1.0
    for t in range(n - 1):
        if sig[t] != pos:                      # act on t close, fill t+1 open
            if sig[t] == 1:                    # buy
                p = o[t + 1] * (1 + SLIP)
                entry_eq = cash
                btc, cash, pos = cash * (1 - FEE) / p, 0.0, 1
            else:                              # sell
                p = o[t + 1] * (1 - SLIP)
                cash, btc, pos = btc * p * (1 - FEE), 0.0, 0
                trades.append({"exit_i": t + 1, "ret": cash / entry_eq - 1.0})
        equity[t + 1] = cash if pos == 0 else btc * c[t + 1]
    if pos == 1:                               # defensive close at last close
        cash = btc * c[-1] * (1 - SLIP) * (1 - FEE)
        trades.append({"exit_i": n - 1, "ret": cash / entry_eq - 1.0})
        equity[-1] = cash
    daily = pd.Series(equity, index=df.index).pct_change().dropna()
    return pd.DataFrame(trades), daily, pd.Series(equity, index=df.index)


def sharpe(daily: pd.Series) -> float:
    return float(daily.mean() / max(1e-12, daily.std()) * np.sqrt(365))


def max_dd(eq: np.ndarray) -> float:
    peak = np.maximum.accumulate(eq)
    return float(((eq - peak) / peak).min())


def boot_p_dd(daily: pd.Series, thresh=0.40, n_paths=10_000, seed=7) -> float:
    rng = np.random.default_rng(seed)
    r = daily.values
    hits = 0
    for _ in range(n_paths):
        eq = np.cumprod(1 + rng.choice(r, size=len(r), replace=True))
        if max_dd(eq) < -thresh:
            hits += 1
    return hits / n_paths


def run_e4_voltarget(df: pd.DataFrame, lookback: int = 28,
                     vol_target: float = 0.15, vol_win: int = 30):
    """E4-v2 as registered: same signal; exposure w_t = min(1, target/sigma_t)
    when long, else 0. Costs charged on turnover: |dw| * (FEE + SLIP).
    Returns (trades_df, daily_net_returns, equity_series)."""
    c = df["close"].values
    n = len(df)
    r = np.zeros(n)
    r[1:] = c[1:] / c[:-1] - 1.0
    sig = np.zeros(n)
    for t in range(lookback, n):
        sig[t] = 1.0 if c[t] > c[t - lookback] else 0.0
    vol = pd.Series(r, index=df.index).rolling(vol_win).std() * np.sqrt(365)
    w_tgt = np.minimum(1.0, vol_target / vol.replace(0, np.nan)).fillna(0.0).values
    eq = np.ones(n)
    w_prev = 0.0
    trades, entry_eq, in_pos = [], 1.0, False
    for t in range(n - 1):
        w = sig[t] * w_tgt[t]
        cost = abs(w - w_prev) * (FEE + SLIP)
        eq[t + 1] = eq[t] * (1.0 + w * r[t + 1] - cost)
        if not in_pos and w > 0:
            in_pos, entry_eq = True, eq[t]
        elif in_pos and w == 0:
            trades.append({"exit_i": t, "ret": eq[t + 1] / entry_eq - 1.0})
            in_pos = False
        w_prev = w
    if in_pos:
        trades.append({"exit_i": n - 1, "ret": eq[-1] / entry_eq - 1.0})
    daily = pd.Series(eq, index=df.index).pct_change().dropna()
    return pd.DataFrame(trades), daily, pd.Series(eq, index=df.index)
