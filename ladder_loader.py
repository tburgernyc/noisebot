"""ladder_loader.py — I/O for the Databento daily expiry ladders pulled
for E9 (commodity) and E12 (FX). Reads one *_ladder_1d.csv, keeps only
OUTRIGHT contracts (drops calendar spreads / butterflies), decodes each
outright's expiry via the next-occurrence rule, and drops Databento
degraded-quality days. Returns a tidy long frame the pure logic in
term_structure.py consumes.

Data contract out: columns [date (tz-naive datetime64), symbol, close
(float), expiry_ym (int)], one row per (date, outright contract), sorted.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

import term_structure as ts

# Databento-flagged degraded days on GLBX.MDP3 (excluded from returns)
DEGRADED_DAYS = {"2014-06-11", "2014-06-12", "2014-06-13"}


def load_ladder(path: str | Path, root: str) -> pd.DataFrame:
    """Load and clean one root's daily ladder into the tidy contract."""
    df = pd.read_csv(path)
    # normalise the timestamp column to a tz-naive calendar date
    tcol = "ts_event" if "ts_event" in df.columns else df.columns[0]
    df["date"] = pd.to_datetime(df[tcol], utc=True).dt.tz_localize(None).dt.normalize()
    df = df[~df["date"].dt.strftime("%Y-%m-%d").isin(DEGRADED_DAYS)]

    # keep outrights only
    df = df[df["symbol"].map(lambda s: ts.is_outright(str(s), root))].copy()
    if df.empty:
        raise ValueError(f"{root}: no outright rows after filtering {path}")

    # decode each contract's expiry against its own observation month
    df["expiry_ym"] = [
        ts.decode_expiry_ym(sym, root, d.year, d.month)
        for sym, d in zip(df["symbol"], df["date"])
    ]
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["close"])
    out = df[["date", "symbol", "close", "expiry_ym"]].sort_values(
        ["date", "expiry_ym", "symbol"]).reset_index(drop=True)
    return out


def front_second_monthly(panel: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """From one root's tidy panel, return (front_monthly, second_monthly)
    no-splice compounded monthly return series."""
    fr = ts.monthly_returns(ts.nearby_return_series(panel, "front"))
    sr = ts.monthly_returns(ts.nearby_return_series(panel, "second"))
    return fr, sr


def month_end_curve(panel: pd.DataFrame) -> pd.DataFrame:
    """Month-end snapshot of front & second-nearby CLOSE and their expiry
    gap in years — the inputs to the FX carry signal (E12).

    Returns columns [front_close, second_close, dt_years] indexed by
    month-end date."""
    df = panel[["date", "symbol", "close", "expiry_ym"]].copy()
    df["obs_ym"] = df["date"].dt.year * 12 + df["date"].dt.month - 1
    cand = df[df["expiry_ym"] > df["obs_ym"]].sort_values(
        ["date", "expiry_ym", "symbol"])
    cand["rk"] = cand.groupby("date").cumcount()
    fr = cand[cand["rk"] == 0].set_index("date")
    sc = cand[cand["rk"] == 1].set_index("date")
    curve = pd.DataFrame({
        "front_close": fr["close"],
        "second_close": sc["close"],
        "dt_years": (sc["expiry_ym"] - fr["expiry_ym"]) / 12.0,
    }).dropna()
    curve = curve[(curve["front_close"] > 0) & (curve["second_close"] > 0)]
    curve.index = pd.to_datetime(curve.index)
    return curve.resample("ME").last().dropna()
