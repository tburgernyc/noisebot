"""E5 registered module: month-end rebalancing pressure on ES.
Daily ES.v.0 / ZN.v.0 continuous. Signal only in last N trading days of
month: S = MTD(ES) - MTD(ZN); S>0 -> SHORT ES 1 day, S<0 -> LONG 1 day.
Fills at close +/- 1 tick adverse (MOC-style). MES $5/pt, $2.50 RT."""
from __future__ import annotations
import numpy as np
import pandas as pd

MULT, TICK, COST_RT = 5.0, 0.25, 2.50


def load_es_zn(path: str):
    df = pd.read_csv(path, parse_dates=["ts_event"])
    df["sym"] = df["symbol"].str.slice(0, 2)
    piv = df.pivot_table(index="ts_event", columns="sym", values="close")
    piv = piv.rename(columns={"ES": "es", "ZN": "zn"}).dropna().sort_index()
    return piv


def run_e5(px: pd.DataFrame, window: int = 4) -> pd.DataFrame:
    """One-day trades in the last `window` trading days of each month."""
    px = px.copy()
    px["ym"] = px.index.to_period("M")
    trades = []
    months = list(px.groupby("ym"))
    for mi in range(1, len(months)):
        prev_close_es = months[mi - 1][1]["es"].iloc[-1]
        prev_close_zn = months[mi - 1][1]["zn"].iloc[-1]
        g = months[mi][1]
        n = len(g)
        for j in range(max(0, n - window), n):
            t_es, t_zn = g["es"].iloc[j], g["zn"].iloc[j]
            s = (t_es / prev_close_es - 1.0) - (t_zn / prev_close_zn - 1.0)
            if s == 0.0:
                continue
            pos = -1 if s > 0 else 1
            # exit next trading day close (may be first day of next month)
            if j + 1 < n:
                nxt = g["es"].iloc[j + 1]
            elif mi + 1 < len(months):
                nxt = months[mi + 1][1]["es"].iloc[0]
            else:
                continue
            entry = t_es + TICK * pos
            exit_ = nxt - TICK * pos
            pnl = (exit_ - entry) * pos * MULT - COST_RT
            trades.append({"date": g.index[j].date(), "dir": pos, "pnl": pnl})
    return pd.DataFrame(trades)
