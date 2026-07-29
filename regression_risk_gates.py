"""regression_risk_gates.py — ONE-TIME integrity check, not a permanent
test: proves risk_gates.bootstrap_p_ruin reproduces the OLD (still-present
at time of writing) implementations EXACTLY on REAL data, for every
distinct (mode, seed) combination that exists anywhere in this repo's
history, before any call site is switched over.

Four combinations cover everything (verified by grep across every
phase2_*.py / crypto_trend.py / term_structure.py call site,
2026-07-29):
  compound, seed=7  -- crypto family (E4/E4-v2/E6/E7/E16/E17/E17-v2/E19/E19-v2)
  compound, seed=0  -- term-structure family (E9/E11/E12)
  additive, seed=7  -- E5
  additive, seed=14 -- E14

Not every hypothesis needs its own check: once the shared function is
proven byte-identical to the old one on real data for ONE representative
case per (mode, seed) pair, every OTHER hypothesis using that exact same
(mode, seed) pair runs through the identical code path with a different
input series -- there is nothing left that could differ. This is checked,
not asserted: exact equality is required to PASS, not "close enough".
"""
from __future__ import annotations

import sys

import numpy as np

import risk_gates as rg

FAILS = []


def check(name, cond, detail=""):
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)


def check_e4v2():
    import crypto_trend as ct
    df = ct.load_yahoo_daily("data/btc_1d.json")
    _, daily, _ = ct.run_e4_voltarget(df, lookback=28)
    old = ct.boot_p_dd(daily)  # defaults: thresh=0.40, n_paths=10_000, seed=7
    new = rg.bootstrap_p_ruin(daily, threshold=0.40, n_paths=10_000, seed=7, mode="compound")
    check("E4-v2 real data: new==old (compound, seed=7)", old == new, detail=f"old={old} new={new}")


def check_e5():
    import rebalance as reb
    import phase2_e5_e4v2 as p5  # importing only defs/module-level RNG init; no __main__ side effects
    px = reb.load_es_zn("data/es_zn_1d.csv")
    t5 = reb.run_e5(px, window=4)
    pnl = t5["pnl"].values
    old = p5.boot_dd_dollars(pnl)  # uses p5's own module-level RNG(7), first draw
    new = rg.bootstrap_p_ruin(pnl, threshold=2500.0, n_paths=10_000, seed=7, mode="additive")
    check("E5 real data: new==old (additive, seed=7)", old == new, detail=f"old={old} new={new}")


def check_e14():
    import rebalance_threshold as rebt
    import phase2_e14 as p14
    px = rebt.load_es_zn("data/es_zn_1d.csv")
    tr = rebt.run_e14(px, delta=0.04)
    pnl = tr["pnl"].values
    old = p14.boot_dd_dollars(pnl)  # uses p14's own module-level RNG(14), first draw
    new = rg.bootstrap_p_ruin(pnl, threshold=2500.0, n_paths=10_000, seed=14, mode="additive")
    check("E14 real data: new==old (additive, seed=14)", old == new, detail=f"old={old} new={new}")


def check_e9():
    import cot_loader  # noqa: F401  (not needed for E9 itself, kept for parity/clarity)
    import ladder_loader as L
    import term_structure as ts
    import termstructure_backtest as bt

    DATA = "data"
    COMMO = ["CL", "NG", "HO", "RB", "GC", "SI", "HG",
             "ZC", "ZW", "ZS", "ZL", "ZM", "LE", "HE"]
    print("  (loading full commodity ladders -- this is the slow step, ~90-120s)")
    cpanels = {r: L.load_ladder(f"{DATA}/ladders_commodity/{r}_ladder_1d.csv", r)
               for r in COMMO}
    cdaily = bt.daily_front_returns(cpanels)
    e9_sig = bt.e9_signal(cpanels, 12)
    e9_book = bt.run_book(e9_sig, cdaily, tercile=True, bps_per_side=5.0)
    net = e9_book["net"]
    old = ts.bootstrap_p_maxdd(net, 0.40)  # default seed=0
    new = rg.bootstrap_p_ruin(net, threshold=0.40, n_paths=10_000, seed=0, mode="compound")
    check("E9 real data: new==old (compound, seed=0)", old == new, detail=f"old={old} new={new}")


def main():
    print("check_e4v2 (compound, seed=7):")
    check_e4v2()
    print("\ncheck_e5 (additive, seed=7):")
    check_e5()
    print("\ncheck_e14 (additive, seed=14):")
    check_e14()
    print("\ncheck_e9 (compound, seed=0):")
    check_e9()

    print("\n" + "=" * 52)
    if FAILS:
        print(f"REGRESSION: {len(FAILS)} FAILED -> {FAILS}")
        print("DO NOT swap any call site over until this is green.")
        sys.exit(1)
    print("REGRESSION: ALL 4 (mode, seed) COMBINATIONS REPRODUCE EXACTLY")
    print("Safe to swap crypto_trend/term_structure/phase2_e5_e4v2/phase2_e14")
    print("over to risk_gates.bootstrap_p_ruin.")


if __name__ == "__main__":
    main()
