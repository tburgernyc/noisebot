"""E14 registered module: THRESHOLD (band-breach) 60/40 rebalancing
pressure, equity leg on MES. Daily ES.v.0 / ZN.v.0 continuous.

A synthetic 60/40 book drifts by realized ES/ZN daily returns; when the
equity weight breaches +/- delta from 0.60 the mandate rebalances, and we
take the SAME side as that forced flow for one day (short the overweight
leg, long the underweight leg). Fills at close +/- 1 tick adverse
(MOC-style). MES $5/pt, $2.50 RT.

Roll-no-splice (constitution): a day's return is used only WITHIN a single
contract (instrument_id constant); a 1-day trade whose exit spans an
equity-leg roll is dropped. Pure logic; the only I/O is the CSV reader.
No execution paths of any kind.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

MULT, TICK, COST_RT, REF = 5.0, 0.25, 2.50, 0.60


def load_es_zn(path: str) -> pd.DataFrame:
    """Wide daily frame: es, zn closes plus es_iid, zn_iid contract ids."""
    df = pd.read_csv(path, parse_dates=["ts_event"])
    df["sym"] = df["symbol"].str.slice(0, 2)
    close = df.pivot_table(index="ts_event", columns="sym", values="close")
    iid = df.pivot_table(index="ts_event", columns="sym",
                         values="instrument_id")
    out = pd.DataFrame({"es": close["ES"], "zn": close["ZN"],
                        "es_iid": iid["ES"], "zn_iid": iid["ZN"]})
    return out.dropna().sort_index()


def roll_safe_ret(px_close: pd.Series, iid: pd.Series) -> np.ndarray:
    """close-to-close return, NaN where the contract id changed (a roll)
    or at the first bar — never splices two contracts into one return."""
    c = px_close.values.astype(float)
    i = iid.values
    r = np.full(len(c), np.nan)
    r[1:] = c[1:] / c[:-1] - 1.0
    roll = np.zeros(len(c), bool)
    roll[0] = True
    roll[1:] = i[1:] != i[:-1]
    r[roll] = np.nan
    return r


def run_e14(px: pd.DataFrame, delta: float) -> pd.DataFrame:
    """One-day trades triggered when |w_eq - 0.60| >= delta at close t.
    The book drifts by realized returns and RESETS to 60/40 at each breach
    (the mandate rebalances). Only roll-clean trades are returned; the
    reset happens whether or not the trade was tradeable."""
    es = px["es"].values.astype(float)
    es_iid = px["es_iid"].values
    r_es = roll_safe_ret(px["es"], px["es_iid"])
    r_zn = roll_safe_ret(px["zn"], px["zn_iid"])
    dates = px.index

    v_eq, v_bd = REF, 1.0 - REF
    trades = []
    n = len(px)
    for t in range(1, n):
        # drift the book by today's realized returns (roll day -> no update)
        re = r_es[t] if np.isfinite(r_es[t]) else 0.0
        rb = r_zn[t] if np.isfinite(r_zn[t]) else 0.0
        v_eq *= (1.0 + re)
        v_bd *= (1.0 + rb)
        w_eq = v_eq / (v_eq + v_bd)

        if abs(w_eq - REF) >= delta:
            pos = -1 if (w_eq - REF) > 0 else 1     # short the overweight leg
            # 1-day trade close t -> close t+1; drop if the equity leg rolls
            if t + 1 < n and es_iid[t + 1] == es_iid[t]:
                entry = es[t] + TICK * pos
                exit_ = es[t + 1] - TICK * pos
                pnl = (exit_ - entry) * pos * MULT - COST_RT
                trades.append({"date": dates[t].date(), "w_eq": w_eq,
                               "dir": pos, "pnl": pnl})
            v_eq, v_bd = REF, 1.0 - REF             # mandate rebalances

    return pd.DataFrame(trades)
