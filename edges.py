"""E1/E2 registered edge modules (HYPOTHESES.md v2, registered 2026-07-15).
E1: ORB-15 with range-compression filter. E2: VWAP mean-reversion with
info-day (gap) filter. Pure logic, same data contract as noise_area.
No broker code. Rules are locked to the registration — do not add knobs.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from noise_area import rth

PT, TICK, COST_RT = 2.0, 0.25, 2.50
FLATTEN = "15:55"


def _day_groups(df5: pd.DataFrame, min_bars: int = 60):
    r = rth(df5)
    return {d: g for d, g in r.groupby(r.index.date) if len(g) >= min_bars}


def _fill(nxt_open: float, direction: int) -> float:
    """Pessimistic entry: next bar open, 1 tick adverse."""
    return nxt_open + TICK * direction


def _exit_fill(nxt_open: float, position: int) -> float:
    return nxt_open - TICK * position


def _trade(date, position, entry, exit_) -> dict:
    return {"date": date, "dir": position, "entry": entry, "exit": exit_,
            "pnl": (exit_ - entry) * position * PT - COST_RT}


def run_e1(df5: pd.DataFrame, or_minutes: int = 15,
           compression: float = 0.30, range_lookback: int = 14) -> pd.DataFrame:
    """E1 as registered: OR = first or_minutes of RTH. Trade day only if
    OR range <= compression * median(prior range_lookback full-RTH ranges).
    First 5m close beyond OR high/low (window 09:45-14:00) enters LONG/SHORT,
    fill next open +1 tick adverse. Stop: close beyond opposite OR extreme.
    Flatten 15:55. ONE trade/day, no reversal."""
    groups = _day_groups(df5)
    dates = sorted(groups)
    day_range = {d: float(groups[d]["high"].max() - groups[d]["low"].min())
                 for d in dates}
    n_or = max(1, or_minutes // 5)
    trades = []
    for i, d in enumerate(dates):
        if i < range_lookback:
            continue
        med = float(np.median([day_range[dates[j]]
                               for j in range(i - range_lookback, i)]))
        g = groups[d]
        or_hi = float(g["high"].iloc[:n_or].max())
        or_lo = float(g["low"].iloc[:n_or].min())
        if (or_hi - or_lo) > compression * med:
            continue
        pos, entry_px, done = 0, 0.0, False
        for k in range(n_or, len(g) - 1):
            hhmm = g.index[k].strftime("%H:%M")
            close = float(g["close"].iloc[k])
            nxt = float(g["open"].iloc[k + 1])
            if pos == 0 and not done and "09:45" <= hhmm <= "14:00":
                if close > or_hi:
                    pos, entry_px, done = 1, _fill(nxt, 1), True
                elif close < or_lo:
                    pos, entry_px, done = -1, _fill(nxt, -1), True
                continue
            if pos:
                stop = (pos == 1 and close < or_lo) or (pos == -1 and close > or_hi)
                if hhmm >= FLATTEN or stop:
                    trades.append(_trade(d, pos, entry_px, _exit_fill(nxt, pos)))
                    pos = 0
        if pos:  # defensive flatten at last bar close, adverse tick
            last = float(g["close"].iloc[-1])
            trades.append(_trade(d, pos, entry_px, last - TICK * pos))
    return pd.DataFrame(trades)


def run_e2(df5: pd.DataFrame, z_entry: float = 2.0, z_stop: float = 3.5,
           atr_len: int = 20, gap_lookback: int = 60, gap_pctile: float = 75.0,
           max_entries: int = 3) -> pd.DataFrame:
    """E2 as registered: fade 5m closes stretched >= z_entry ATR20 from
    session VWAP, window 10:00-15:00. Exit on VWAP cross (target) or
    |z| >= z_stop (stop), fill next open adverse tick. Skip whole day if
    overnight |gap| > p75 of trailing 60 sessions. Max 3 entries/day,
    one position at a time. Flatten 15:55."""
    groups = _day_groups(df5)
    dates = sorted(groups)
    r = pd.concat([groups[d] for d in dates])
    prev_c = r["close"].shift(1)
    tr = pd.concat([r["high"] - r["low"], (r["high"] - prev_c).abs(),
                    (r["low"] - prev_c).abs()], axis=1).max(axis=1)
    atr = tr.rolling(atr_len).mean()
    opens = {d: float(groups[d]["open"].iloc[0]) for d in dates}
    closes = {d: float(groups[d]["close"].iloc[-1]) for d in dates}
    gaps = {dates[i]: abs(opens[dates[i]] / closes[dates[i - 1]] - 1.0)
            for i in range(1, len(dates))}
    trades = []
    for i, d in enumerate(dates):
        if i < gap_lookback + 1:
            continue
        hist = [gaps[dates[j]] for j in range(i - gap_lookback, i)]
        if gaps[d] > float(np.percentile(hist, gap_pctile)):
            continue
        g = groups[d]
        tp = (g["high"] + g["low"] + g["close"]) / 3
        vol = g["volume"].replace(0, np.nan).ffill().fillna(1.0)
        vwap = (tp * vol).cumsum() / vol.cumsum()
        a = atr.reindex(g.index)
        pos, entry_px, entries = 0, 0.0, 0
        for k in range(len(g) - 1):
            hhmm = g.index[k].strftime("%H:%M")
            close = float(g["close"].iloc[k])
            nxt = float(g["open"].iloc[k + 1])
            ak = float(a.iloc[k])
            if not (np.isfinite(ak) and ak > 0):
                continue
            z = (close - float(vwap.iloc[k])) / ak
            if pos:
                target = (pos == 1 and close >= float(vwap.iloc[k])) or \
                         (pos == -1 and close <= float(vwap.iloc[k]))
                stop = (pos == 1 and z <= -z_stop) or (pos == -1 and z >= z_stop)
                if hhmm >= FLATTEN or target or stop:
                    trades.append(_trade(d, pos, entry_px, _exit_fill(nxt, pos)))
                    pos = 0
                continue
            if entries < max_entries and "10:00" <= hhmm <= "15:00":
                if z >= z_entry:
                    pos, entry_px, entries = -1, _fill(nxt, -1), entries + 1
                elif z <= -z_entry:
                    pos, entry_px, entries = 1, _fill(nxt, 1), entries + 1
        if pos:
            last = float(g["close"].iloc[-1])
            trades.append(_trade(d, pos, entry_px, last - TICK * pos))
    return pd.DataFrame(trades)
