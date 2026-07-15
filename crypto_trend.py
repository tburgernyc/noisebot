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
