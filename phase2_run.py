"""Phase 2 runner — Databento ohlcv-1m parquet -> Tier A baseline + parameter
plateau + eval-barrier MC, reported against the pre-registered Phase 2 gates.

Usage:
  python3 phase2_run.py data/databento_1m.parquet [--yahoo data/nq_5m.json]

Fills/costs per spec (immutable): signals on bar close, filled next bar open
+/- 1 tick adverse, $2.50/ct RT, 15:55 ET flatten, per-contract MNQ dollars.
Every metric ships with its sample size. Backtests are hypotheses, never
forward expectancy.
"""
from __future__ import annotations
import argparse

import numpy as np
import pandas as pd

from backtest import TICK, barrier_mc, metrics, run_tier_a
from noise_area import (build_days, load_databento_parquet, load_yahoo_json,
                        rth)

GATES = ("PF>1.3 & n>=100 & both halves>0 & plateau(10/14/20 all>0) "
         "& MC P(blow)<10%")


def audit(df5: pd.DataFrame) -> None:
    r = rth(df5)
    by_day = r.groupby(r.index.date).size()
    print("== DATA AUDIT ==")
    print(f"5m bars total {len(df5):,}  RTH bars {len(r):,}  "
          f"days with RTH data {len(by_day)}")
    print(f"span {df5.index[0]} -> {df5.index[-1]}")
    print(f"RTH bars/day: median {by_day.median():.0f}  min {by_day.min()}  "
          f"max {by_day.max()}  days<60 bars (skipped): {(by_day < 60).sum()}")
    days = sorted(by_day.index)
    grouped = {d: g for d, g in r.groupby(r.index.date)}
    gaps = {b: abs(grouped[b]["open"].iloc[0] / grouped[a]["close"].iloc[-1] - 1.0)
            for a, b in zip(days, days[1:])}
    g = pd.Series(gaps)
    if len(g):
        print(f"overnight |gap| (n={len(g)}): median {g.median():.3%}  "
              f"p95 {g.quantile(.95):.3%}")
        print("top 6 gap days (roll caveat: MNQ.v.0 is volume-rolled; check "
              "vs quarterly roll windows Mar/Jun/Sep/Dec):")
        for d, v in g.sort_values(ascending=False).head(6).items():
            print(f"  {d}  {v:.2%}")


def cross_check(df5: pd.DataFrame, yahoo_path: str) -> None:
    print("\n== YAHOO OVERLAP CROSS-CHECK (data QA only — no tuning) ==")
    y = rth(load_yahoo_json(yahoo_path))
    d = rth(df5)
    j = d[["close"]].join(y[["close"]], how="inner",
                          lsuffix="_db", rsuffix="_y").dropna()
    if j.empty:
        print("no overlapping timestamps — SKIPPED")
        return
    diff = (j["close_db"] - j["close_y"]).abs() / TICK
    print(f"overlap bars n={len(j):,}  |close diff| in ticks: "
          f"median {diff.median():.1f}  p95 {diff.quantile(.95):.1f}  "
          f"max {diff.max():.1f}")
    sh = d[["close"]].shift(-1).join(y[["close"]], how="inner",
                                     lsuffix="_db", rsuffix="_y").dropna()
    shd = (sh["close_db"] - sh["close_y"]).abs() / TICK
    print(f"timestamp-convention diagnostic: -1 bar shift median "
          f"{shd.median():.1f} ticks (n={len(sh):,}) — must be far worse "
          "than aligned, else ts convention is off")
    bad = diff[diff > 4]
    if len(bad):
        print(f"FLAG: {len(bad)} of {len(j)} bars differ by >4 ticks; worst:")
        for ts, v in bad.sort_values(ascending=False).head(5).items():
            print(f"  {ts}  {v:.0f} ticks")
    else:
        print("no overlapping bar diverges by more than 4 ticks — agree")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("parquet")
    ap.add_argument("--yahoo", default=None)
    args = ap.parse_args()

    df5 = load_databento_parquet(args.parquet)
    audit(df5)
    if args.yahoo:
        cross_check(df5, args.yahoo)

    lbs = (10, 14, 20)
    trades = {}
    ndays = {}
    for lb in lbs:
        days = build_days(df5, lookback=lb)
        ndays[lb] = len(days)
        trades[lb] = run_tier_a(days)

    m = metrics(trades[14], f"BASELINE — Noise-Area 5m Databento, lookback 14, "
                            f"{ndays[14]} tradeable days")

    print("\n== Parameter plateau (Tier A lookback, same window) ==")
    plateau_ok = True
    for lb in lbs:
        t = trades[lb]
        tot = t["pnl"].sum() if len(t) else 0.0
        pf = (t["pnl"][t.pnl > 0].sum() / max(1e-9, -t["pnl"][t.pnl <= 0].sum())
              if len(t) else 0.0)
        plateau_ok &= tot > 0
        print(f"lookback {lb:2d}: trades {len(t):4d} ({ndays[lb]} days)  "
              f"total ${tot:>10,.0f}/ct  PF {pf:.2f}")

    mc = barrier_mc(trades[14]["pnl"].values) if len(trades[14]) else {}

    print(f"\n== VERDICT vs Phase 2 gates ({GATES}) ==")
    checks = {
        "PF>1.3": m.get("pf", 0) > 1.3,
        "n>=100": m.get("trades", 0) >= 100,
        "half1>0": m.get("half1", 0) > 0,
        "half2>0": m.get("half2", 0) > 0,
        "plateau 10/14/20 all>0": plateau_ok,
        "MC P(blow)<10%": mc.get("p_blow", 1.0) < 0.10,
    }
    for k, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print("BASELINE VERDICT:", "PASS" if all(checks.values()) else "FAIL",
          f"(n={m.get('trades', 0)} trades, {ndays[14]} days)")


if __name__ == "__main__":
    main()
