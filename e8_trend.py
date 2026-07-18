"""E8-R registered module: intraday crypto trend continuation, ETHUSDT 15m
(HYPOTHESES.md 2026-07-18). Pure logic + loaders. No execution code.

House fill convention throughout (non-negotiable #3): signals and exit
conditions evaluate on 15m bar CLOSE; fills at NEXT bar open at effective
price open*(1 +/- 0.0006) — 6 bps/side all-in, adverse (registered
fixture). 4h TEMA uses only COMPLETED 4h bars (value becomes available
at the 4h close). Funding accrues from actual 8h prints while held,
sign-aware, marked at the containing 15m bar close; prints in the exit
fill bar are not accrued (position leaves at the open). Opposite signal
while held = stop-and-reverse (both legs costed). P&L is USDT per 1 unit.
"""
from __future__ import annotations
import glob

import numpy as np
import pandas as pd

COST_SIDE = 0.0006          # 0.05% taker + 0.01% half-spread (registered)
ADX_N, ATR_N = 14, 14
TEMA_FAST_15, TEMA_SLOW_15 = 10, 80
TEMA_FAST_4H, TEMA_SLOW_4H = 20, 70


def load_klines_15m(dirpath: str, sym: str = "ETHUSDT") -> pd.DataFrame:
    frames = []
    for f in sorted(glob.glob(f"{dirpath}/{sym}-15m-*.csv")):
        df = pd.read_csv(f, usecols=["open_time", "open", "high", "low",
                                     "close", "volume"])
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f"no kline CSVs for {sym} in {dirpath}")
    k = pd.concat(frames, ignore_index=True)
    k.index = pd.to_datetime(k.pop("open_time"), unit="ms", utc=True)
    k = k.sort_index()
    return k[~k.index.duplicated(keep="first")].astype(float)


def ema(x: pd.Series, n: int) -> pd.Series:
    return x.ewm(span=n, adjust=False).mean()


def tema(x: pd.Series, n: int) -> pd.Series:
    e1 = ema(x, n); e2 = ema(e1, n); e3 = ema(e2, n)
    out = 3 * e1 - 3 * e2 + e3
    # 6n mask: the triple-EMA init transient decays in ~3 EMA stages;
    # 3n proved insufficient on synthetic data (init bias produced
    # wrong-side crossovers right after mask expiry).
    out.iloc[: 6 * n] = np.nan
    return out


def wilder(x: pd.Series, n: int) -> pd.Series:
    return x.ewm(alpha=1.0 / n, adjust=False).mean()


def atr(df: pd.DataFrame, n: int = ATR_N) -> pd.Series:
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(),
                    (df["low"] - pc).abs()], axis=1).max(axis=1)
    out = wilder(tr, n)
    out.iloc[: n] = np.nan
    return out


def adx(df: pd.DataFrame, n: int = ADX_N) -> pd.Series:
    up = df["high"].diff()
    dn = -df["low"].diff()
    plus_dm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), df.index)
    minus_dm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), df.index)
    pc = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - pc).abs(),
                    (df["low"] - pc).abs()], axis=1).max(axis=1)
    str_, spdm, smdm = wilder(tr, n), wilder(plus_dm, n), wilder(minus_dm, n)
    pdi = 100 * spdm / str_.replace(0, np.nan)
    mdi = 100 * smdm / str_.replace(0, np.nan)
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    out = wilder(dx.fillna(0.0), n)
    out.iloc[: 3 * n] = np.nan
    return out


def resample_4h(k15: pd.DataFrame) -> pd.DataFrame:
    return k15.resample("4h", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min",
         "close": "last", "volume": "sum"}).dropna(subset=["open"])


def trend_4h_on_15m(k15: pd.DataFrame) -> pd.Series:
    """+1/-1/NaN per 15m bar, using only COMPLETED 4h bars: the 4h TEMA
    value stamped at a 4h bar's CLOSE time, forward-filled onto 15m."""
    k4 = resample_4h(k15)
    t_fast = tema(k4["close"], TEMA_FAST_4H)
    t_slow = tema(k4["close"], TEMA_SLOW_4H)
    tr4 = pd.Series(np.where(t_fast > t_slow, 1.0, -1.0), k4.index)
    tr4[t_fast.isna() | t_slow.isna()] = np.nan
    avail = tr4.copy()
    avail.index = avail.index + pd.Timedelta(hours=4)   # known at 4h CLOSE
    return avail.reindex(k15.index.union(avail.index)).ffill() \
                .reindex(k15.index)


def run_e8(k15: pd.DataFrame, adx_gate: float = 35.0,
           trail_mult: float = 4.0, stop_mult: float = 3.0,
           fund_daysum: pd.Series | None = None,
           fund_prints: pd.DataFrame | None = None):
    """Returns (trades_df, daily_pnl_usdt, attribution dict).
    fund_prints: DataFrame with UTC timestamp index and column 'rate'
    (each actual print); accrued at the containing 15m bar."""
    c = k15["close"].values
    o = k15["open"].values
    idx = k15.index
    n = len(k15)
    t15f = tema(k15["close"], TEMA_FAST_15).values
    t15s = tema(k15["close"], TEMA_SLOW_15).values
    a = adx(k15).values
    at = atr(k15).values
    tr4 = trend_4h_on_15m(k15).values

    sig = np.zeros(n)
    ok = (~np.isnan(t15f)) & (~np.isnan(t15s)) & (~np.isnan(a)) \
        & (~np.isnan(tr4)) & (~np.isnan(at))
    up = ok & (t15f > t15s) & (tr4 > 0) & (a > adx_gate)
    dn = ok & (t15f < t15s) & (tr4 < 0) & (a > adx_gate)
    sig[up], sig[dn] = 1.0, -1.0

    fund_bar = np.zeros(n)              # sum of print rates inside each bar
    if fund_prints is not None:
        loc = idx.get_indexer(fund_prints.index.floor("15min"))
        for j, r in zip(loc, fund_prints["rate"].values):
            if j >= 0:
                fund_bar[j] += r

    trades = []
    daily_pnl: dict = {}
    pos = 0
    entry_px = stop_lvl = best = 0.0
    entry_i = -1
    fund_acc = 0.0                      # USDT funding while in this trade
    cum_price, cum_fund, cum_cost = 0.0, 0.0, 0.0

    def day(i):
        return idx[i].normalize()

    def close_trade(i_fill, side, reason):
        nonlocal cum_price, cum_fund, cum_cost, fund_acc
        exit_eff = o[i_fill] * (1 - side * COST_SIDE)
        gross = side * (exit_eff - entry_px)
        pnl = gross - fund_acc
        cost_usd = COST_SIDE * (o[i_fill] + o[entry_i])
        cum_price += gross + cost_usd   # price leg pre-cost
        cum_cost += cost_usd
        cum_fund -= fund_acc
        trades.append({"side": side, "entry": idx[entry_i],
                       "exit": idx[i_fill], "pnl": pnl, "reason": reason})
        # remainder from last accrued close to the exit fill price
        daily_pnl[day(i_fill)] = daily_pnl.get(day(i_fill), 0.0) + \
            (side * (exit_eff - c[i_fill - 1]))
        fund_acc = 0.0

    for t in range(1, n - 1):
        if pos != 0:
            # accrue this bar's P&L to daily series and funding
            d = day(t)
            bar_pnl = pos * (c[t] - c[t - 1]) if t > entry_i else \
                pos * (c[t] - entry_px)
            f_usd = pos * fund_bar[t] * c[t]
            fund_acc += f_usd
            daily_pnl[d] = daily_pnl.get(d, 0.0) + bar_pnl - f_usd
            best = max(best, pos * c[t])
            trail = best - trail_mult * at[t]         # in pos-signed space
            breach = (pos * c[t]) <= max(trail, pos * stop_lvl)
            opposite = sig[t] == -pos
            if breach or opposite:
                side = pos
                pos = 0
                close_trade(t + 1, side,
                            "reverse" if opposite else "stop/trail")
                if opposite:
                    pos = int(sig[t])
                    entry_i = t + 1
                    entry_px = o[t + 1] * (1 + pos * COST_SIDE)
                    stop_lvl = entry_px - pos * stop_mult * at[t]
                    best = pos * entry_px
                continue
        elif sig[t] != 0:
            pos = int(sig[t])
            entry_i = t + 1
            entry_px = o[t + 1] * (1 + pos * COST_SIDE)
            stop_lvl = entry_px - pos * stop_mult * at[t]
            best = pos * entry_px
    if pos != 0:                        # defensive close at final close
        entry_side = pos
        exit_eff = c[-1] * (1 - entry_side * COST_SIDE)
        pnl = entry_side * (exit_eff - entry_px) - fund_acc
        cost_usd = COST_SIDE * (c[-1] + o[entry_i])
        cum_price += entry_side * (exit_eff - entry_px) + cost_usd
        cum_cost += cost_usd
        cum_fund -= fund_acc
        trades.append({"side": entry_side, "entry": idx[entry_i],
                       "exit": idx[-1], "pnl": pnl, "reason": "final"})
    daily = pd.Series(daily_pnl).sort_index()
    att = {"price": cum_price, "funding": cum_fund, "costs": cum_cost}
    return pd.DataFrame(trades), daily, att
