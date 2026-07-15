"""Noise-Area signal module. Pure logic: no broker code, no I/O side effects.

Data contract: DataFrame indexed by tz-aware NY timestamps with columns
open, high, low, close, volume. Loader for Yahoo chart JSON included;
swap load_yahoo_json() for a Databento loader later — same contract.
"""
from __future__ import annotations
import json
import zoneinfo
from dataclasses import dataclass

import numpy as np
import pandas as pd

NY = zoneinfo.ZoneInfo("America/New_York")
RTH_OPEN, SIG_START, SIG_END, FLATTEN = "09:30", "09:45", "15:30", "15:55"


def load_yahoo_json(path: str) -> pd.DataFrame:
    raw = json.load(open(path))["chart"]["result"][0]
    q = raw["indicators"]["quote"][0]
    df = pd.DataFrame(
        {k: q[k] for k in ("open", "high", "low", "close", "volume")},
        index=pd.to_datetime(raw["timestamp"], unit="s", utc=True).tz_convert(NY),
    ).dropna()
    return df[~df.index.duplicated(keep="first")].sort_index()


def load_databento_parquet(path: str) -> pd.DataFrame:
    """Load a Databento GLBX.MDP3 ohlcv-1m parquet and return 5-minute bars
    matching the module data contract (tz-aware America/New_York index,
    columns open/high/low/close/volume).

    Handles both common Databento parquet flavors:
    - DBNStore.to_parquet(): int64 fixed-point prices (1e-9), ts_event column
    - to_df().to_parquet():  float prices, ts_event as the index
    Databento OHLCV ts_event is the bar OPEN time (UTC). Bars are resampled
    1m -> 5m on NY wall-clock boundaries (label=left, closed=left): the
    09:30 bar aggregates 09:30:00-09:34:59, matching Yahoo's convention.
    Refuses multi-symbol files rather than silently mixing contracts.
    """
    def _epoch_unit(col: pd.Series) -> str:
        """Infer epoch unit of integer timestamps by magnitude (2020s era:
        ns ~1.7e18, us ~1.7e15, ms ~1.7e12, s ~1.7e9)."""
        m = float(col.abs().median())
        if m > 1e17:
            return "ns"
        if m > 1e14:
            return "us"
        if m > 1e11:
            return "ms"
        return "s"

    df = pd.read_parquet(path)
    if isinstance(df.index, pd.DatetimeIndex):
        pass
    else:
        for cand in ("ts_event", "ts_recv", "timestamp"):
            if cand in df.columns:
                col = df[cand]
                ts = (pd.to_datetime(col, utc=True) if col.dtype.kind == "M"
                      else pd.to_datetime(col.astype("int64"),
                                          unit=_epoch_unit(col), utc=True))
                df = df.drop(columns=[cand])
                df.index = ts
                break
        else:
            raise ValueError(f"{path}: no DatetimeIndex and no "
                             "ts_event/ts_recv/timestamp column")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    df.index = df.index.tz_convert(NY)
    if "symbol" in df.columns:
        syms = df["symbol"].unique()
        if len(syms) > 1:
            raise ValueError(f"{path}: multiple symbols {sorted(map(str, syms))}; "
                             "expected a single continuous stream (MNQ.v.0)")
    need = ["open", "high", "low", "close", "volume"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")
    df = df[need].dropna().sort_index()
    df = df[~df.index.duplicated(keep="first")]
    px = df[["open", "high", "low", "close"]]
    if (px.dtypes.apply(lambda t: t.kind in "iu").all()
            or float(px["close"].median()) > 1e7):  # raw 1e-9 fixed point
        df[["open", "high", "low", "close"]] = px.astype("float64") / 1e9
    df = df.astype({c: "float64" for c in need})
    out = df.resample("5min", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min",
         "close": "last", "volume": "sum"}).dropna(subset=["open"])
    return out


def rth(df: pd.DataFrame) -> pd.DataFrame:
    return df.between_time(RTH_OPEN, "15:59")


@dataclass
class Day:
    date: object
    bars: pd.DataFrame        # RTH 5m bars
    day_open: float
    prev_close: float | None
    upper: pd.Series          # per-bar noise bands (built from PRIOR days only)
    lower: pd.Series
    vwap: pd.Series


def build_days(df5: pd.DataFrame, lookback: int = 14) -> list[Day]:
    """Construct per-day structures. Bands for day D use only days < D
    (no lookahead). Days with too few bars or insufficient history skipped."""
    out: list[Day] = []
    r = rth(df5)
    grouped = {d: g for d, g in r.groupby(r.index.date) if len(g) >= 60}
    dates = sorted(grouped)
    # per-day map: minute-offset -> |close/open - 1|
    dev_by_day: dict[object, pd.Series] = {}
    for d in dates:
        g = grouped[d]
        o = g["open"].iloc[0]
        offs = ((g.index - g.index.normalize()).total_seconds() // 60).astype(int)
        dev_by_day[d] = pd.Series(np.abs(g["close"].values / o - 1.0), index=offs)

    for i, d in enumerate(dates):
        if i < lookback:
            continue
        g = grouped[d]
        offs = ((g.index - g.index.normalize()).total_seconds() // 60).astype(int)
        hist = pd.concat([dev_by_day[dates[j]] for j in range(i - lookback, i)], axis=1)
        mu = hist.mean(axis=1).reindex(offs).ffill().bfill().values
        o = g["open"].iloc[0]
        pc = grouped[dates[i - 1]]["close"].iloc[-1]
        upper = pd.Series(max(o, pc) * (1 + mu), index=g.index)
        lower = pd.Series(min(o, pc) * (1 - mu), index=g.index)
        tp = (g["high"] + g["low"] + g["close"]) / 3
        vol = g["volume"].replace(0, np.nan).ffill().fillna(1.0)
        vwap = (tp * vol).cumsum() / vol.cumsum()
        out.append(Day(d, g, o, pc, upper, lower, vwap))
    return out


def signal_for_bar(day: Day, i: int, position: int) -> str:
    """Evaluate on bar i CLOSE. Returns LONG / SHORT / EXIT / HOLD.
    Never None. Flat->entry only inside signal window; VWAP stop and
    flatten handled here so the executor stays dumb."""
    ts = day.bars.index[i]
    close = day.bars["close"].iloc[i]
    hhmm = ts.strftime("%H:%M")
    if hhmm >= FLATTEN:
        return "EXIT" if position else "HOLD"
    if position == 1 and close < day.vwap.iloc[i]:
        return "EXIT"
    if position == -1 and close > day.vwap.iloc[i]:
        return "EXIT"
    if not (SIG_START <= hhmm <= SIG_END):
        return "HOLD"
    if close > day.upper.iloc[i] and position <= 0:
        return "LONG"
    if close < day.lower.iloc[i] and position >= 0:
        return "SHORT"
    return "HOLD"
