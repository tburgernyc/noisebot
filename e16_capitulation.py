"""E16 candidate module: volume-confirmed capitulation mean-reversion.
Pure logic: no I/O, no broker imports. Translated from a public indicator
("Capitulation Finder"); see E16_HYPOTHESIS_DRAFT.md for the registration.

The source indicator is a signal/marker only -- it defines the ENTRY
trigger (RSI extreme + price extension from MA + volume climax, all on
one bar) but no exit. The exit rule below (reversion-to-MA target, time
stop, hard stop) is this registration's own design, not part of the
original script -- flagged explicitly since "no exit was specified" is
not the same as "any exit is fine": the hard stop exists specifically
because oversold conditions do not reliably resolve into a reversal
(see registration doc, Research section).

Data contract: DataFrame with columns open/high/low/close/volume (any
index). No lookahead: rolling/rsi computations at row t use only rows
<= t; entries fill at t+1 open.

Pure logic + loader (matches crypto_trend.py's own convention -- the
"no I/O" rule in CLAUDE.md is scoped to noise_area.py specifically, not
every module). No broker imports.
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd


def load_yahoo_daily_ohlcv(path: str) -> pd.DataFrame:
    """Load a Yahoo chart-API daily OHLCV JSON. Same source/schema as
    crypto_trend.py's load_yahoo_daily, extended to capture high/low/
    volume -- E16 needs volume (climax filter), which the open/close-only
    original loader never fetched.

    IMPORTANT -- fetch with explicit period1/period2 (Unix seconds), NOT
    range=max: confirmed empirically while wiring this up that range=max
    silently auto-coarsens to ~monthly spacing for long spans while still
    reporting interval=1d and no error field (BTC-USD range=max returned
    143 bars over 12 years, ~30 days apart). period1/period2 does not
    have this problem (verified: 4330 bars, exactly 1 day apart,
    2014-09-17 to 2026-07-25). Example fetch used for data/btc_usd_1d.json
    and data/eth_usd_1d.json:
      curl "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD\
?interval=1d&period1=1388534400&period2=<now_unix>&includePrePost=false" \\
        -H "User-Agent: Mozilla/5.0" -o data/btc_usd_1d.json
    `_assert_daily_spacing` below re-checks this on every load so a
    future accidental range=max re-fetch fails loudly here instead of
    silently feeding monthly bars into RSI(14)/SMA(50)/volume(20)
    windows sized for daily data.
    """
    raw = json.load(open(path))["chart"]["result"][0]
    q = raw["indicators"]["quote"][0]
    df = pd.DataFrame(
        {k: q[k] for k in ("open", "high", "low", "close", "volume")},
        index=pd.to_datetime(raw["timestamp"], unit="s", utc=True),
    ).dropna()
    df = df[~df.index.duplicated(keep="first")].sort_index()
    _assert_daily_spacing(df.index, path)
    return df


def _assert_daily_spacing(index: pd.DatetimeIndex, path: str, max_gap_days: int = 4) -> None:
    if len(index) < 2:
        return
    median_gap = index.to_series().diff().dropna().dt.days.median()
    if median_gap > max_gap_days:
        raise ValueError(
            f"{path}: median bar spacing is {median_gap:.0f} days, expected ~1 "
            "(daily). This is the range=max auto-coarsening failure mode found "
            "while wiring this loader up -- re-fetch with explicit period1/"
            "period2 Unix timestamps instead of range=max.")


def wilder_rma(series: pd.Series, n: int) -> pd.Series:
    x = series.astype(float).values
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return pd.Series(out, index=series.index)
    out[n - 1] = x[:n].mean()
    for t in range(n, len(x)):
        out[t] = out[t - 1] + (x[t] - out[t - 1]) / n
    return pd.Series(out, index=series.index)


def rsi_wilder(close: pd.Series, n: int) -> pd.Series:
    # .diff() leaves row 0 as NaN; wilder_rma's seed is a plain .mean() over
    # its first window, and one NaN there poisons the entire recursive
    # chain forever (out[t] depends on out[t-1] all the way down). Row 0
    # has no prior price to compare against anyway, so 0 change is correct,
    # not a hack.
    delta = close.diff().fillna(0.0)
    gain = wilder_rma(delta.clip(lower=0), n)
    loss = wilder_rma((-delta.clip(upper=0)), n)
    rs = gain / loss.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.where(loss != 0, 100.0)


def compute_signals(df: pd.DataFrame, *, rsi_length: int = 14,
                     rsi_oversold: float = 30.0, rsi_overbought: float = 70.0,
                     ma_length: int = 50, pct_threshold: float = 5.0,
                     vol_mult: float = 1.2, vol_length: int = 20) -> pd.DataFrame:
    """All defaults match the original indicator's shipped parameters."""
    close, volume = df["close"], df["volume"]
    rsi_val = rsi_wilder(close, rsi_length)
    ma = close.rolling(ma_length).mean()
    vol_avg = volume.rolling(vol_length).mean()
    vol_ok = volume >= vol_avg * vol_mult
    dist_pct = (close / ma - 1.0) * 100.0

    bullish_capitulation = ((rsi_val <= rsi_oversold)
                            & (close < ma * (1 - pct_threshold / 100.0))
                            & vol_ok)
    bearish_capitulation = ((rsi_val >= rsi_overbought)
                            & (close > ma * (1 + pct_threshold / 100.0))
                            & vol_ok)
    return pd.DataFrame({
        "rsi": rsi_val, "ma": ma, "dist_pct": dist_pct, "vol_ok": vol_ok,
        "bullish_capitulation": bullish_capitulation,
        "bearish_capitulation": bearish_capitulation,
    }, index=df.index)


def run_backtest(df: pd.DataFrame, sig: pd.DataFrame, *, fee: float = 0.0035,
                  slip: float = 0.0010, time_stop_bars: int = 10,
                  hard_stop_pct: float = 8.0, allow_short: bool = False):
    """Decide at bar t's close, fill at t+1's open -- applied uniformly to
    BOTH entries and exits (matches noise_area.py's convention). Enter on
    a capitulation bar (skipped while already in a position). Exit at the
    FIRST of: close reverts to the MA (target, the mechanism's own
    definition of "reversion"), time_stop_bars elapsed (registered
    plateau parameter), or hard_stop_pct adverse move (fixed risk
    backstop -- not swept). Long/flat by default, matching the E4-v2/E6
    spot convention. Cost (fee+slip) charged on each fill."""
    o, c = df["open"].values, df["close"].values
    ma = sig["ma"].values
    bull = sig["bullish_capitulation"].values
    bear = sig["bearish_capitulation"].values
    n = len(df)
    cost = fee + slip

    eq = np.ones(n)
    pos, entry_eq, entry_px, entry_i, bars_held = 0, 1.0, 0.0, -1, 0
    trades = []

    for t in range(n - 1):
        ret_bar = pos * (c[t + 1] / c[t] - 1.0) if pos != 0 else 0.0
        eq[t + 1] = eq[t] * (1.0 + ret_bar)
        if pos != 0:
            bars_held += 1

        if pos != 0:
            unrealized_pct = (c[t] / entry_px - 1.0) * pos * 100.0
            target_hit = (pos == 1 and c[t] >= ma[t]) or (pos == -1 and c[t] <= ma[t])
            time_hit = bars_held >= time_stop_bars
            stop_hit = unrealized_pct <= -abs(hard_stop_pct)
            if target_hit or time_hit or stop_hit:
                eq[t + 1] *= (1.0 - cost)
                trades.append({
                    "entry_i": entry_i, "exit_i": t + 1,
                    "ret": eq[t + 1] / entry_eq - 1.0, "bars_held": bars_held,
                    "reason": "target" if target_hit else ("time" if time_hit else "stop"),
                })
                pos, bars_held = 0, 0

        if pos == 0:
            if bull[t]:
                pos = 1
            elif allow_short and bear[t]:
                pos = -1
            if pos != 0:
                eq[t + 1] *= (1.0 - cost)
                entry_px, entry_eq, entry_i, bars_held = o[t + 1], eq[t + 1], t + 1, 0

    if pos != 0:
        trades.append({"entry_i": entry_i, "exit_i": n - 1,
                        "ret": eq[-1] / entry_eq - 1.0, "bars_held": bars_held,
                        "reason": "eod_open"})

    daily = pd.Series(eq, index=df.index).pct_change().dropna()
    return pd.DataFrame(trades), daily, pd.Series(eq, index=df.index)


def max_dd(eq: np.ndarray) -> float:
    peak = np.maximum.accumulate(eq)
    return float(((eq - peak) / peak).min())
