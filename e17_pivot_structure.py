"""E17 candidate module: Livermore-style swing-pivot breakout with
failure-swing invalidation and a stall/consolidation detector. Pure
logic: no I/O, no broker imports. Translated from a public indicator
("Pivot Levels & Candle Color (Dark Theme)"); see E17_HYPOTHESIS_DRAFT.md
for the registration and the full structural-audit notes.

TWO structural fixes applied relative to the source, both explained in
the registration doc -- do not silently "revert" without re-reading why:

1. REPAINT / LOOKAHEAD FIX (the important one). The source stores a
   pivot at its OWN bar index i, but confirming a pivot at i requires
   seeing `pivot_right_bars` bars AFTER i (the right-side confirmation
   window) -- it is not actually knowable until bar i + pivot_right_bars.
   The source's trend-state loop reads `pivotHighs[i]` at that SAME index
   i, which silently uses information from the future. This is a common,
   easy-to-miss property of chart pivot/fractal indicators (fine for
   visual hindsight, fatal for a backtest) -- this module makes the pivot
   available to the trend-state machine only from bar i+right onward.
   Verified by test_e17.py's test_no_lookahead.
2. PERFORMANCE FIX, not a correctness change. The source recomputes the
   "reaction low/high" (lowest/highest point since the breakout) by
   rescanning the ENTIRE leg every time a new high/low-water-mark bar
   occurs -- worst case O(n^2) together with the pivot-significance
   filter's own pairwise comparison. This module tracks it with an O(1)
   amortized accumulator that is mathematically identical (a "min-since-
   last-checkpoint" accumulator folded into the running reaction level at
   each new-watermark bar) -- cross-checked against a literal brute-force
   port of the original's rescan in test_e17.py (must match bar-for-bar
   on synthetic data).

Data contract: DataFrame with columns open/high/low/close (any index).

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
    crypto_trend.py's load_yahoo_daily, extended to capture high/low
    (E17's pivot detection needs both -- the open/close-only original
    loader never fetched them). Identical to e16_capitulation.py's copy
    of this function -- duplicated deliberately, matching this repo's
    existing per-module convention (e.g. noise_area.py and crypto_trend.py
    each have their own, different, loader) rather than adding a shared
    utils module neither of them currently has.

    IMPORTANT -- fetch with explicit period1/period2 (Unix seconds), NOT
    range=max: confirmed empirically while wiring this up that range=max
    silently auto-coarsens to ~monthly spacing for long spans while still
    reporting interval=1d and no error field (BTC-USD range=max returned
    143 bars over 12 years, ~30 days apart). period1/period2 does not
    have this problem (verified: 4330 bars, exactly 1 day apart,
    2014-09-17 to 2026-07-25). Example fetch used for data/btc_usd_1d.json:
      curl "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD\
?interval=1d&period1=1388534400&period2=<now_unix>&includePrePost=false" \\
        -H "User-Agent: Mozilla/5.0" -o data/btc_usd_1d.json
    `_assert_daily_spacing` re-checks this on every load so a future
    accidental range=max re-fetch fails loudly here instead of silently
    feeding monthly bars into a pivot_left/right=10 window sized for
    daily data.
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


def find_pivots(high: np.ndarray, low: np.ndarray, left: int, right: int,
                 resolution_minutes: float = 1440.0, baseline_minutes: float = 240.0):
    """Swing pivot detection with timeframe-adaptive confirmation
    (matches the source: sqrt-scaled sensitivity vs. a 4h baseline) and a
    significance filter (drop a pivot if a more extreme one exists within
    min_spacing bars). Returns (pivot_high, pivot_low) float arrays, NaN
    where no confirmed/significant pivot exists, INDEXED AT THE PIVOT'S
    OWN BAR (not yet shifted for availability -- see
    `shift_for_availability`)."""
    n = len(high)
    sensitivity = np.sqrt(resolution_minutes / baseline_minutes)
    breakout_factor = 0.995 + (1 - sensitivity) * 0.003
    breakdown_factor = 1.005 - (1 - sensitivity) * 0.003

    cand_highs, cand_lows = [], []
    for i in range(left, n - right):
        cur_h = high[i]
        if np.all(high[i - left:i] <= cur_h):
            win = high[i + 1:i + right + 1]
            if win.max() < cur_h and np.any(win < cur_h * breakout_factor):
                cand_highs.append((i, cur_h))
        cur_l = low[i]
        if np.all(low[i - left:i] >= cur_l):
            win = low[i + 1:i + right + 1]
            if win.min() > cur_l and np.any(win > cur_l * breakdown_factor):
                cand_lows.append((i, cur_l))

    min_spacing = max(5, (left + right) // 3)

    def _significant(cands, beats):
        keep = {}
        for idx, (i, v) in enumerate(cands):
            if all(not (abs(i - i2) < min_spacing and beats(v2, v))
                   for j, (i2, v2) in enumerate(cands) if j != idx):
                keep[i] = v
        return keep

    sig_highs = _significant(cand_highs, lambda v2, v: v2 > v)
    sig_lows = _significant(cand_lows, lambda v2, v: v2 < v)

    pivot_high = np.full(n, np.nan)
    pivot_low = np.full(n, np.nan)
    for i, v in sig_highs.items():
        pivot_high[i] = v
    for i, v in sig_lows.items():
        pivot_low[i] = v
    return pivot_high, pivot_low


def shift_for_availability(pivot_series: np.ndarray, right: int) -> np.ndarray:
    """A pivot detected at bar i needs `right` future bars to confirm --
    it is available to a trader/backtest only from bar i+right onward.
    This is the repaint fix: shift, don't use the raw detection index."""
    n = len(pivot_series)
    out = np.full(n, np.nan)
    if right < n:
        out[right:] = pivot_series[: n - right]
    return out


def _trend_state_machine(close, high, low, pivot_high_avail, pivot_low_avail,
                          *, neutral_lookback: int, reaction_mode: str = "fast"):
    """reaction_mode='fast' uses the O(1)-amortized accumulator;
    'bruteforce' uses a literal full-range rescan every new-watermark bar
    (matches the source's own algorithm exactly, O(n^2)-ish) -- used only
    by test_e17.py to cross-check that 'fast' is not just efficient but
    IDENTICAL."""
    n = len(close)
    trend_state = np.zeros(n, dtype=int)
    breakout_marker = np.full(n, np.nan)
    breakdown_marker = np.full(n, np.nan)

    state = 0
    last_active_high, last_active_low = np.nan, np.nan
    last_breakout_level, last_breakdown_level = -np.inf, np.inf
    breakout_i, breakdown_i = -1, -1
    hwm, lwm = -np.inf, np.inf
    reaction_low, reaction_high = np.inf, -np.inf
    pending_low, pending_high = np.inf, -np.inf  # 'fast' mode accumulators

    for i in range(n):
        if not np.isnan(pivot_high_avail[i]):
            last_active_high = pivot_high_avail[i]
        if not np.isnan(pivot_low_avail[i]):
            last_active_low = pivot_low_avail[i]

        if not np.isnan(last_active_high) and close[i] > last_active_high:
            breakout_marker[i] = low[i]
            state, last_breakout_level, last_active_high = 1, last_active_high, np.nan
            breakout_i, hwm, reaction_low = i, high[i], low[i]
            pending_low = np.inf

        if not np.isnan(last_active_low) and close[i] < last_active_low:
            breakdown_marker[i] = high[i]
            state, last_breakdown_level, last_active_low = -1, last_active_low, np.nan
            breakdown_i, lwm, reaction_high = i, low[i], high[i]
            pending_high = -np.inf

        if state == 0 and last_breakout_level > -np.inf and close[i] > last_breakout_level and high[i] > hwm:
            state, breakout_i, hwm, reaction_low, pending_low = 1, i, high[i], low[i], np.inf
        if state == 0 and last_breakdown_level < np.inf and close[i] < last_breakdown_level and low[i] < lwm:
            state, breakdown_i, lwm, reaction_high, pending_high = -1, i, low[i], high[i], -np.inf

        if state == 1:
            prev_hwm = hwm
            if reaction_mode == "fast":
                pending_low = min(pending_low, low[i])
                hwm = max(hwm, high[i])
                if high[i] > prev_hwm:
                    reaction_low = min(reaction_low, pending_low)
                    pending_low = np.inf
            else:
                hwm = max(hwm, high[i])
                if high[i] > prev_hwm:
                    reaction_low = low[breakout_i:i + 1].min()
            bars_since = i - breakout_i
            if bars_since >= 2 and low[i] < reaction_low:
                state = 0
            elif bars_since >= neutral_lookback * 3:
                w0 = max(0, i - neutral_lookback + 1)
                rhh, rll = high[w0:i + 1].max(), low[w0:i + 1].min()
                rng = rhh - rll
                no_progress = rhh < hwm * 0.997
                tight = rng < (hwm - rll) * 0.4
                hover = abs(close[i] - (rhh + rll) / 2) < rng * 0.35
                if no_progress and tight and hover:
                    state = 0

        if state == -1:
            prev_lwm = lwm
            if reaction_mode == "fast":
                pending_high = max(pending_high, high[i])
                lwm = min(lwm, low[i])
                if low[i] < prev_lwm:
                    reaction_high = max(reaction_high, pending_high)
                    pending_high = -np.inf
            else:
                lwm = min(lwm, low[i])
                if low[i] < prev_lwm:
                    reaction_high = high[breakdown_i:i + 1].max()
            bars_since = i - breakdown_i
            if bars_since >= 2 and high[i] > reaction_high:
                state = 0
            elif bars_since >= neutral_lookback * 3:
                w0 = max(0, i - neutral_lookback + 1)
                rhh, rll = high[w0:i + 1].max(), low[w0:i + 1].min()
                rng = rhh - rll
                no_progress = rll > lwm * 1.003
                tight = rng < (rhh - lwm) * 0.4
                hover = abs(close[i] - (rhh + rll) / 2) < rng * 0.35
                if no_progress and tight and hover:
                    state = 0

        trend_state[i] = state

    return trend_state, breakout_marker, breakdown_marker


def compute_signals(df: pd.DataFrame, *, pivot_left: int = 10, pivot_right: int = 10,
                     neutral_lookback: int = 5, resolution_minutes: float = 1440.0,
                     reaction_mode: str = "fast") -> pd.DataFrame:
    """All defaults match the original indicator's shipped parameters."""
    high, low, close = df["high"].values, df["low"].values, df["close"].values
    pivot_high, pivot_low = find_pivots(high, low, pivot_left, pivot_right, resolution_minutes)
    pivot_high_avail = shift_for_availability(pivot_high, pivot_right)
    pivot_low_avail = shift_for_availability(pivot_low, pivot_right)
    trend_state, breakout_marker, breakdown_marker = _trend_state_machine(
        close, high, low, pivot_high_avail, pivot_low_avail,
        neutral_lookback=neutral_lookback, reaction_mode=reaction_mode)
    return pd.DataFrame({
        "pivot_high_avail": pivot_high_avail, "pivot_low_avail": pivot_low_avail,
        "trend_state": trend_state, "breakout": ~np.isnan(breakout_marker),
        "breakdown": ~np.isnan(breakdown_marker),
    }, index=df.index)


def run_backtest(df: pd.DataFrame, sig: pd.DataFrame, *, fee: float = 0.0035,
                  slip: float = 0.0010, allow_short: bool = False):
    """Position tracks trend_state directly (E4-style: no separate stop/
    target leg -- the state machine's own invalidation IS the exit).
    Signal decided at bar t close, exposure applied to the t->t+1 return
    (no lookahead); cost on turnover. Long/flat by default."""
    c = df["close"].values
    n = len(df)
    state = sig["trend_state"].values
    target = np.where(state == 1, 1.0, np.where((state == -1) & allow_short, -1.0, 0.0))
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


def max_dd(eq: np.ndarray) -> float:
    peak = np.maximum.accumulate(eq)
    return float(((eq - peak) / peak).min())
