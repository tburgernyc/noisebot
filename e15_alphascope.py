"""E15 candidate module: Alpha-Scope Channel Breakout. Pure logic: no I/O,
no broker imports (repo convention). Translated from a public indicator
("Mean Reversion & Momentum Hybrid | Alpha-Scope"); see the registration
draft (E15_HYPOTHESIS_DRAFT.md) for the full structural-audit notes.

Structural findings applied here (do not silently "fix" without
re-reading the draft's rationale):
  1. The original computes myScore and mySig from the IDENTICAL formula
     (for_every(myLongFil, myShortFil, ...) verbatim twice) and requires
     both in the buy/sell condition. That is one trend filter counted
     twice, not two independent confirmations -- collapsed here into a
     single `trend_state` series.
  2. The 75th/25th-percentile momentum block (momentum_length, mult_75,
     mult_25) is computed in the original but never referenced by
     myBuyCondition/mySellCondition -- it is DEAD CODE relative to the
     tradeable signal and is NOT ported. Wiring it in as an actual filter
     is a distinct hypothesis (see draft, "E15-alt").
  3. The original hardcodes the Bollinger basis/width calc to `close` but
     computes the %B position filter on an OHLC4 average, while only the
     RMA/ATR trend filter respects the user's `source` input. That mixed
     sourcing is preserved here for a faithful port, not because it's
     obviously the right design -- see draft for a "cleaned up" variant.

Data contract: DataFrame with columns open/high/low/close (any
DatetimeIndex; crypto trades 24/7 so no RTH/session structure is
assumed, unlike noise_area.py). No lookahead: every rolling/Wilder
computation at row t uses only rows <= t.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def wilder_rma(series: pd.Series, n: int) -> pd.Series:
    """Wilder's smoothing (same recursion TradingView's rma()/atr() use):
    seed = SMA(n), then rma[t] = rma[t-1] + (x[t] - rma[t-1]) / n."""
    x = series.astype(float).values
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return pd.Series(out, index=series.index)
    out[n - 1] = x[:n].mean()
    for t in range(n, len(x)):
        out[t] = out[t - 1] + (x[t] - out[t - 1]) / n
    return pd.Series(out, index=series.index)


def atr_wilder(high: pd.Series, low: pd.Series, close: pd.Series, n: int) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(),
                    (low - prev_close).abs()], axis=1).max(axis=1)
    return wilder_rma(tr, n)


def bollinger(series: pd.Series, length: int, mult: float):
    basis = series.rolling(length).mean()
    dev = series.rolling(length).std() * mult  # pandas default ddof=1
    return basis, basis + dev, basis - dev


def compute_signals(df: pd.DataFrame, *, source: str = "close",
                     bb_length: int = 20, bb_mult: float = 2.0,
                     min_bb_width_pct: float = 0.5,
                     long_threshold: float = 55.0, short_threshold: float = 45.0,
                     rma_length: int = 15, atr_length: int = 20) -> pd.DataFrame:
    """All defaults match the original indicator's shipped parameters."""
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    price = df[source] if source in df.columns else c

    # -- close-based BB: width/squeeze filter only --
    bb_basis_c = c.rolling(bb_length).mean()
    _, bb_upper, bb_lower = bollinger(c, bb_length, bb_mult)
    width_pct = (bb_upper - bb_lower) / bb_basis_c * 100.0
    width_ok = width_pct > min_bb_width_pct

    # -- OHLC4-based BB: %B position filter (loose 55/45 deadband) --
    ohlc4 = (o + h + l + c) / 4.0
    _, upper4, lower4 = bollinger(ohlc4, bb_length, bb_mult)
    pct_b = (ohlc4 - lower4) / (upper4 - lower4) * 100.0
    bb_raw = np.where(pct_b > long_threshold, 1,
                       np.where(pct_b < short_threshold, -1, np.nan))
    bb_state = pd.Series(bb_raw, index=df.index).ffill().fillna(0)

    # -- RMA +/- ATR trend/breakout filter (Keltner-channel-style) --
    rma = wilder_rma(price, rma_length)
    atr = atr_wilder(h, l, c, atr_length)
    long_fil = price > (rma + atr)
    short_fil = price < (rma - atr)
    trend_raw = np.where(long_fil & ~short_fil, 1, np.where(short_fil, -1, np.nan))
    trend_state = pd.Series(trend_raw, index=df.index).ffill().fillna(0)

    buy = (bb_state == 1) & (trend_state == 1) & width_ok
    sell = (bb_state == -1) & (trend_state == -1) & width_ok

    return pd.DataFrame({
        "width_pct": width_pct, "width_ok": width_ok,
        "bb_state": bb_state, "trend_state": trend_state,
        "buy": buy, "sell": sell,
    }, index=df.index)


def run_backtest(df: pd.DataFrame, sig: pd.DataFrame, *, fee: float = 0.0035,
                  slip: float = 0.0010, allow_short: bool = False):
    """Signal decided at bar t's close (no lookahead), exposure applied to
    the t->t+1 return -- equivalent to a next-bar-open fill in a 24/7
    market. Cost charged on turnover: |position change| * (fee + slip).
    Long/flat by default (allow_short=False), matching the E4-v2/E6 spot
    convention; set allow_short=True only for a perp/futures registration.
    """
    c = df["close"].values
    n = len(df)
    target = np.where(sig["buy"].values, 1.0,
                       np.where(sig["sell"].values, (-1.0 if allow_short else 0.0), 0.0))
    eq = np.ones(n)
    trades, entry_eq, pos_prev, in_pos = [], 1.0, 0.0, False
    for t in range(n - 1):
        pos = target[t]
        cost = abs(pos - pos_prev) * (fee + slip)
        ret = c[t + 1] / c[t] - 1.0
        eq[t + 1] = eq[t] * (1.0 + pos * ret - cost)
        if not in_pos and pos != 0:
            in_pos, entry_eq = True, eq[t]
        elif in_pos and pos == 0:
            trades.append({"exit_i": t, "ret": eq[t + 1] / entry_eq - 1.0})
            in_pos = False
        pos_prev = pos
    if in_pos:
        trades.append({"exit_i": n - 1, "ret": eq[-1] / entry_eq - 1.0})
    daily = pd.Series(eq, index=df.index).pct_change().dropna()
    return pd.DataFrame(trades), daily, pd.Series(eq, index=df.index)


def sharpe(daily: pd.Series, periods_per_year: float) -> float:
    return float(daily.mean() / max(1e-12, daily.std()) * np.sqrt(periods_per_year))


def max_dd(eq: np.ndarray) -> float:
    peak = np.maximum.accumulate(eq)
    return float(((eq - peak) / peak).min())
