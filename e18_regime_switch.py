"""E18 candidate module: regime-switched combination of E17 (trend mode)
and E16 (range mode), gated by a simplified MTF-Compass-style multi-
horizon EMA alignment classifier. Pure logic: no I/O, no broker imports.

Built FROM e16_capitulation.py and e17_pivot_structure.py -- per the
E4->E4-v2 sequencing precedent, THIS SHOULD NOT BE EVALUATED before E16
and E17 have real standalone numbers (see E18_HYPOTHESIS_DRAFT.md). You
cannot attribute a combined result to either half without knowing what
each half does alone first.

The regime classifier deliberately DROPS the RSI leg that the source
MTF Compass indicator's own bias definition uses: keeping it would make
the regime gate collinear with E16's own RSI-based entry trigger (the
E8-R "delete a collinear filter" precedent, applied here pre-data).
Ichimoku's TK-cross is not used anywhere in this system: its economic
content is already covered by the short-horizon EMA leg below, and
stacking both would repeat the same mistake.

ATR here uses a plain EMA(14) smoothing, matching the MTF Compass
source's OWN `ema(tr, 14)` -- deliberately NOT Wilder's RMA (which E15
and E17 use for their own, different source indicators' ATR legs). Do
not "fix" this into consistency with the other modules; it would stop
matching what MTF Compass actually specified.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from e16_capitulation import compute_signals as e16_compute_signals
from e17_pivot_structure import compute_signals as e17_compute_signals


def _atr_ema(high: pd.Series, low: pd.Series, close: pd.Series, n: int) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(),
                    (low - prev_close).abs()], axis=1).max(axis=1)
    return tr.ewm(span=n, adjust=False).mean()


def compute_regime(df: pd.DataFrame, *, ema_lengths=(20, 50, 200),
                    slope_atr_mult: float = 0.1, atr_length: int = 14,
                    min_horizons_agree: int = 2) -> pd.Series:
    """Simplified MTF-Compass alignment (RSI leg dropped, see module
    docstring): for each EMA horizon, bull if price > EMA AND EMA slope
    (normalized by ATR%) >= slope_atr_mult; bear mirror; else neutral.
    regime = 1 (trend mode) if >= min_horizons_agree horizons agree on
    the same side; else 0 (range mode).

    THIRD structural fix relative to the MTF Compass source (see
    E18_HYPOTHESIS_DRAFT.md): the source's normSlope divides a RAW price
    difference (ema[t]-ema[t-1], in price units) by atrPct (a percentage
    NUMBER), without first converting the numerator to a percentage. That
    makes the ratio scale with the absolute price level rather than being
    a clean multiple of ATR% -- confirmed on synthetic data: with price
    ~100 the "raw" ratio ranged into the tens against a default 0.1
    threshold, so the slope filter was satisfied on 99.6% of bars
    (regime read as "trend" almost always, defeating the whole point of
    a regime gate). Fixed here by converting the EMA's own bar-over-bar
    move to a percentage BEFORE dividing by ATR% -- both sides of the
    ratio are now dimensionless, and slope_atr_mult=0.1 means what its
    name says: "the EMA must be moving at least 10% as fast as ATR%."""
    close, high, low = df["close"], df["high"], df["low"]
    atr = _atr_ema(high, low, close, atr_length)
    atr_pct = (atr / close) * 100.0

    biases = []
    for length in ema_lengths:
        ema = close.ewm(span=length, adjust=False).mean()
        ema_pct_change = ema.pct_change() * 100.0
        norm_slope = ema_pct_change / atr_pct.replace(0, np.nan)
        bull = (close > ema) & (norm_slope >= slope_atr_mult)
        bear = (close < ema) & (norm_slope <= -slope_atr_mult)
        biases.append(pd.Series(np.where(bull, 1, np.where(bear, -1, 0)), index=df.index))

    stacked = pd.concat(biases, axis=1)
    n_bull = (stacked == 1).sum(axis=1)
    n_bear = (stacked == -1).sum(axis=1)
    aligned = (n_bull >= min_horizons_agree) | (n_bear >= min_horizons_agree)
    return aligned.astype(int)


def e16_position_series(df: pd.DataFrame, *, time_stop_bars: int = 10,
                         hard_stop_pct: float = 8.0, **entry_kwargs) -> np.ndarray:
    """Adapts e16_capitulation's discrete entry/exit rule into a
    continuous per-bar long/flat position array (1 while inside a
    capitulation trade), so E18 can gate it bar-by-bar against the
    regime classifier -- rather than reusing E16's own trade-list-based
    run_backtest, which assumes a trade runs uninterrupted to its own
    exit. Entry/exit conditions are otherwise IDENTICAL to E16 standalone.

    KNOWN TIMING MISMATCH, flagged 2026-07-25, NOT fixed (E18 is not
    registered or evaluated -- this does not affect any committed
    result): this array sets pos[t+1]=1 when a position is entered AT
    bar t's open (matching E16's own discrete-trade fill semantics), but
    run_backtest() below consumes it the same way E9/E17 consume their
    position arrays -- pos[t] weights the c[t]->c[t+1] return, the
    house-standard continuous-exposure convention. Those are two
    different conventions: this adapter's pos[k]=1 means "exposed from
    bar k's open," while the consumer wants "decided at bar k's close,
    exposed for bar k->k+1." Reconcile before E18 is ever registered --
    either reindex this array by one, or change what run_backtest reads."""
    sig = e16_compute_signals(df, **entry_kwargs)
    ma, bull = sig["ma"].values, sig["bullish_capitulation"].values
    c, o = df["close"].values, df["open"].values
    n = len(df)
    pos = np.zeros(n)
    in_pos, entry_px, bars_held = False, 0.0, 0
    for t in range(n - 1):
        if in_pos:
            bars_held += 1
            unrealized_pct = (c[t] / entry_px - 1.0) * 100.0
            if c[t] >= ma[t] or bars_held >= time_stop_bars or unrealized_pct <= -abs(hard_stop_pct):
                in_pos, bars_held = False, 0
        if not in_pos and bull[t]:
            in_pos, entry_px, bars_held = True, o[t + 1], 0
        pos[t + 1] = 1.0 if in_pos else 0.0
    return pos


def compute_signals(df: pd.DataFrame) -> pd.DataFrame:
    regime = compute_regime(df)
    trend_state = e17_compute_signals(df)["trend_state"].values
    range_pos = e16_position_series(df)
    combined_pos = np.where(regime.values == 1, trend_state,
                             np.where(regime.values == 0, range_pos, 0.0))
    return pd.DataFrame({"regime": regime, "trend_state": trend_state,
                        "range_pos": range_pos, "combined_pos": combined_pos},
                       index=df.index)


def run_backtest(df: pd.DataFrame, sig: pd.DataFrame, *, fee: float = 0.0035,
                  slip: float = 0.0010):
    """Continuous exposure backtest (E15/E17 style): cost on turnover of
    combined_pos. Trades = contiguous non-flat episodes (E6 convention).
    Returns (trades, daily, equity, attribution) -- note the 4-tuple,
    one more element than the other modules: `attribution` is a rough
    P&L split by which component was active (diagnostic only, not a
    gate; transition-cost bars fall on neither side of the split, so the
    two figures will not sum to the total to the last cent)."""
    c = df["close"].values
    n = len(df)
    pos, regime = sig["combined_pos"].values, sig["regime"].values
    eq = np.ones(n)
    pnl_trend, pnl_range = 0.0, 0.0
    trades, pos_prev, entry_eq, in_pos = [], 0.0, 1.0, False

    for t in range(n - 1):
        p = pos[t]
        cost = abs(p - pos_prev) * (fee + slip)
        bar_pnl = eq[t] * (p * (c[t + 1] / c[t] - 1.0) - cost)
        eq[t + 1] = eq[t] + bar_pnl
        if p != 0:
            if regime[t] == 1:
                pnl_trend += bar_pnl
            else:
                pnl_range += bar_pnl
        if not in_pos and p != 0:
            in_pos, entry_eq = True, eq[t]
        elif in_pos and p == 0:
            trades.append({"exit_i": t, "ret": eq[t + 1] / entry_eq - 1.0})
            in_pos = False
        pos_prev = p

    if in_pos:
        trades.append({"exit_i": n - 1, "ret": eq[-1] / entry_eq - 1.0})

    daily = pd.Series(eq, index=df.index).pct_change().dropna()
    return (pd.DataFrame(trades), daily, pd.Series(eq, index=df.index),
            {"pnl_trend": pnl_trend, "pnl_range": pnl_range})


def max_dd(eq: np.ndarray) -> float:
    peak = np.maximum.accumulate(eq)
    return float(((eq - peak) / peak).min())
