"""E4-v3: E4-v2 signal with GARCH(1,1) vol-targeted sizing (registered).
Params refit every 21 obs on expanding window (min 500 warmup); variance
recursion daily between refits; realized-vol fallback pre-warmup.
No lookahead: sigma for day t+1 uses data through day t."""
from __future__ import annotations
import numpy as np
import pandas as pd
from arch import arch_model

from crypto_trend import SLIP, FEE

WARMUP, REFIT = 500, 21


def sigma_garch_ann(df: pd.DataFrame) -> np.ndarray:
    """sigma_ann[t] = annualized 1-day-ahead vol forecast usable AT day t
    close (i.e., for sizing exposure over day t+1)."""
    r = df["close"].pct_change().fillna(0.0).values * 100.0  # in %
    n = len(r)
    sig = np.full(n, np.nan)
    # realized-vol fallback before warmup
    s = pd.Series(r / 100.0).rolling(30).std() * np.sqrt(365)
    sig[:WARMUP] = s.values[:WARMUP]
    om = al = be = None
    h = None
    for t in range(WARMUP, n):
        if (t - WARMUP) % REFIT == 0:  # refit on data through t-1... use r[:t]
            res = arch_model(r[:t], vol="GARCH", p=1, q=1, mean="Zero",
                             rescale=False).fit(disp="off", show_warning=False)
            om, al, be = (res.params["omega"], res.params["alpha[1]"],
                          res.params["beta[1]"])
            h = float(res.conditional_volatility[-1] ** 2)
        # h currently = var estimate for day t; forecast for t+1:
        h = om + al * r[t] ** 2 + be * h
        sig[t] = np.sqrt(h * 365) / 100.0
    return sig


def run_sized(df: pd.DataFrame, sigma_ann: np.ndarray, lookback: int = 28,
              vol_target: float = 0.15):
    """Same construction as run_e4_voltarget but with supplied sigma."""
    c = df["close"].values
    n = len(df)
    r = np.zeros(n); r[1:] = c[1:] / c[:-1] - 1.0
    sig = np.zeros(n)
    for t in range(lookback, n):
        sig[t] = 1.0 if c[t] > c[t - lookback] else 0.0
    w_tgt = np.where(np.isfinite(sigma_ann) & (sigma_ann > 0),
                     np.minimum(1.0, vol_target / sigma_ann), 0.0)
    eq = np.ones(n); w_prev = 0.0
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
