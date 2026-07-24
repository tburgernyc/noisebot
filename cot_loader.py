"""cot_loader.py — I/O for the CFTC Commitments-of-Traders hedger signal
used by E11. Reads the consolidated data/cot/cot_hedgers.csv (built from
the CFTC disaggregated annual files, matched by stable contract-market
code), computes hedging pressure per root, and exposes it with a RELEASE
LAG so no future report can leak into a month-end signal.

Hedging pressure (FFM-2018 convention):
    HP = (ProdMerc_long - ProdMerc_short) / (ProdMerc_long + ProdMerc_short)
in [-1, +1]. HP very negative = commercial hedgers heavily net-short =
long speculators most compensated (the E11 long leg).

Release lag: the CoT snapshot is the Tuesday ("As_of") position; it is
published the following Friday. We mark each report AVAILABLE only from
As_of + `release_lag_days` (default 4 calendar days => the Saturday after
release), and a month-end signal uses only reports available on/before
that date.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def load_cot(path: str | Path) -> pd.DataFrame:
    """Long frame [root, date (Tuesday As_of), hp, oi], sorted."""
    df = pd.read_csv(path, parse_dates=["date"])
    tot = df["prodmerc_long"] + df["prodmerc_short"]
    df["hp"] = np.where(tot > 0,
                        (df["prodmerc_long"] - df["prodmerc_short"]) / tot,
                        np.nan)
    df = df.rename(columns={"open_interest": "oi"})
    return df[["root", "date", "hp", "oi"]].dropna(subset=["hp"]).sort_values(
        ["root", "date"]).reset_index(drop=True)


def hp_signal_at_month_ends(cot: pd.DataFrame, month_ends: pd.DatetimeIndex,
                            avg_weeks: int = 13, release_lag_days: int = 4
                            ) -> pd.DataFrame:
    """Wide (month_end x root) trailing-`avg_weeks` mean hedging pressure,
    using ONLY reports available (As_of + lag) on/before each month-end.

    No lookahead: for each root we forward-asof-join the lagged weekly HP
    onto the month-end dates; the trailing mean is over the weekly series
    up to and including the last available report.
    """
    roots = sorted(cot["root"].unique())
    out = pd.DataFrame(index=month_ends, columns=roots, dtype="float64")
    for root in roots:
        s = cot[cot["root"] == root].copy().sort_values("date")
        s["avail"] = s["date"] + pd.Timedelta(days=release_lag_days)
        s["hp_avg"] = s["hp"].rolling(avg_weeks, min_periods=avg_weeks).mean()
        s = s.dropna(subset=["hp_avg"])
        if s.empty:
            continue
        merged = pd.merge_asof(
            pd.DataFrame({"me": month_ends}).sort_values("me"),
            s[["avail", "hp_avg"]].sort_values("avail"),
            left_on="me", right_on="avail", direction="backward")
        out[root] = merged.set_index("me")["hp_avg"].reindex(month_ends).values
    return out
