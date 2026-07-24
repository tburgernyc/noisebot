"""phase2_termstructure.py — the registered ONE-SHOT evaluation driver for
E9 / E11 / E12. Loads the real windows, builds each signal exactly as
registered in HYPOTHESES.md, and prints the E6-adapted gate verdicts.

RUNNING THIS ON THE REAL WINDOWS IS THE SINGLE REGISTERED EVALUATION per
hypothesis. Do NOT run it except on Tim's explicit "go". The machinery it
calls is proven on synthetic data by test_term_structure.py (28/28) and
test_backtest.py (engine). No parameter here may be changed after a run.

Registered fixtures (locked):
  E9  commodity basis-momentum : lookback 12m; plateau {6,12,18}; tercile;
      5 bps/side; 15% vol; benchmark = long-only commodity basket.
  E11 commodity hedger-pressure: HP avg 13w; plateau {4,13,26}; tercile;
      release-lag 4d; same costs/benchmark; extra gate corr(E9) <= 0.5.
  E12 FX carry                 : smoothing 3m; plateau {1,3,6}; long3/short3;
      3 bps/side; 15% vol; benchmark = long-only FX basket.
"""
from __future__ import annotations

import sys

import pandas as pd

import cot_loader
import ladder_loader as L
import term_structure as ts
import termstructure_backtest as bt

DATA = "/home/tburger/noisebot/data"
COMMO = ["CL", "NG", "HO", "RB", "GC", "SI", "HG",
         "ZC", "ZW", "ZS", "ZL", "ZM", "LE", "HE"]
FX = ["6E", "6J", "6B", "6A", "6C", "6S", "6N", "6M"]


def _print(name, res, plateau):
    print(f"\n{'=' * 60}\n{name} VERDICT: {res['verdict']}\n{'=' * 60}")
    print(f"  final_equity={res['final_equity']}  maxDD={res['maxDD']}  "
          f"Sharpe={res['Sharpe']}  PF={res['PF']}  n={res['n']}")
    for gate, (ok, val) in res["gates"].items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {gate:<20} {val}")
    print(f"  plateau totals: {plateau}")


def load_panels(roots, subdir):
    return {r: L.load_ladder(f"{DATA}/{subdir}/{r}_ladder_1d.csv", r)
            for r in roots}


def run_e9(cpanels, cdaily, cbench):
    sig = bt.e9_signal(cpanels, 12)
    book = bt.run_book(sig, cdaily, tercile=True, bps_per_side=5.0)
    plateau = {lb: (1 + bt.run_book(bt.e9_signal(cpanels, lb), cdaily,
                                    tercile=True, bps_per_side=5.0)["net"]
                    ).prod() - 1 for lb in (6, 12, 18)}
    res = bt.evaluate_gates(book["net"], bt.episode_pnl(book), cbench, plateau)
    _print("E9 commodity basis-momentum", res, plateau)
    return book["net"]


def run_e11(cpanels, cdaily, cbench, e9_net, month_ends):
    cot = cot_loader.load_cot(f"{DATA}/cot/cot_hedgers.csv")

    def build(avg_w):
        sig = -cot_loader.hp_signal_at_month_ends(cot, month_ends, avg_w)
        # long where hedgers most net-short => most NEGATIVE HP => negate so
        # cross_sectional_ls longs the top (least-hedged short-pressure) — see note
        return bt.run_book(sig, cdaily, tercile=True, bps_per_side=5.0)

    book = build(13)
    plateau = {w: (1 + build(w)["net"]).prod() - 1 for w in (4, 13, 26)}
    e11_net = book["net"]
    common = e11_net.index.intersection(e9_net.index)
    corr = float(e11_net.loc[common].corr(e9_net.loc[common]))
    extra = {"corr(E9)<=0.5": (abs(corr) <= 0.5, round(corr, 3))}
    res = bt.evaluate_gates(e11_net, bt.episode_pnl(book), cbench, plateau, extra)
    _print("E11 commodity hedger-positioning", res, plateau)


def run_e12(fxpanels, fxdaily, fxbench):
    curves = {r: L.month_end_curve(p) for r, p in fxpanels.items()}
    sig = bt.e12_signal(curves, 3)
    book = bt.run_book(sig, fxdaily, tercile=False, n_long=3, n_short=3,
                       bps_per_side=3.0)
    plateau = {sm: (1 + bt.run_book(bt.e12_signal(curves, sm), fxdaily,
                                    tercile=False, n_long=3, n_short=3,
                                    bps_per_side=3.0)["net"]).prod() - 1
               for sm in (1, 3, 6)}
    res = bt.evaluate_gates(book["net"], bt.episode_pnl(book), fxbench, plateau)
    _print("E12 FX carry", res, plateau)


def main(which="all"):
    print("Loading commodity panels ...", flush=True)
    cpanels = load_panels(COMMO, "ladders_commodity")
    cdaily = bt.daily_front_returns(cpanels)
    cbench = bt.long_only_benchmark(cdaily)
    e9_sig = bt.e9_signal(cpanels, 12)
    month_ends = e9_sig.index

    e9_net = None
    if which in ("all", "e9", "e11"):
        e9_net = run_e9(cpanels, cdaily, cbench)
    if which in ("all", "e11"):
        run_e11(cpanels, cdaily, cbench, e9_net, month_ends)
    if which in ("all", "e12"):
        print("\nLoading FX panels ...", flush=True)
        fxpanels = load_panels(FX, "ladders_fx")
        fxdaily = bt.daily_front_returns(fxpanels)
        fxbench = bt.long_only_benchmark(fxdaily)
        run_e12(fxpanels, fxdaily, fxbench)


if __name__ == "__main__":
    print("!! This driver RUNS the registered one-shot evaluation. Proceed "
          "only on explicit go.\n")
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    main(arg)
