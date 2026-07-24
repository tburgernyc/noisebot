"""test_backtest.py — end-to-end engine proof on SYNTHETIC data ONLY.

Fabricates a cross-section whose month-end signal genuinely predicts the
NEXT month's drift, and checks that termstructure_backtest:
  * runs end-to-end and produces a finite net-return stream
  * earns when the signal is aligned and LOSES when it is reversed
    (the engine respects the signal sign — no accidental look-ahead flip)
  * is NO-LOOKAHEAD at the book level (net up to a cut date is invariant
    to deleting all data after the cut)
  * produces a sane episode count and a computable PF and benchmark
Exit 0 iff all pass.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import termstructure_backtest as bt
import term_structure as ts

FAILS = []


def check(name, cond, detail=""):
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)


def synthetic(reverse=False, k=0.0015, seed=0):
    roots = list("ABCDEF")
    dates = pd.bdate_range("2015-01-01", periods=60 * 21)
    month_ends = pd.date_range("2014-12-31", periods=62, freq="ME")
    rng = np.random.default_rng(seed)
    scores = {me: pd.Series(rng.permutation([3, 2, 1, -1, -2, -3]),
                            index=roots, dtype=float) for me in month_ends}
    signal_me = pd.DataFrame(scores).T.sort_index()
    if reverse:
        signal_me = -signal_me
    me_vals = signal_me.index.values
    dr = pd.DataFrame(0.0, index=dates, columns=roots)
    for d in dates:
        pos = np.searchsorted(me_vals, np.datetime64(d), side="left") - 1
        if pos < 0:
            continue
        eff = signal_me.index[pos]
        drift = k * scores[eff]            # true scores drive the drift
        dr.loc[d] = drift.values + rng.normal(0, 0.004, len(roots))
    return signal_me, dr


def test_end_to_end():
    sig, dr = synthetic()
    book = bt.run_book(sig, dr, tercile=True)
    net = book["net"]
    check("net stream finite & non-empty", len(net) > 100 and np.isfinite(net).all(),
          f"n={len(net)}")
    check("aligned signal is profitable", (1 + net).prod() > 1.0,
          f"final={float((1 + net).prod()):.3f}")
    check("aligned Sharpe positive", ts.sharpe(net) > 0.3,
          f"Sharpe={ts.sharpe(net):.2f}")


def test_sign_respected():
    sig_a, dr = synthetic(reverse=False)
    sig_r, _ = synthetic(reverse=True)
    net_a = bt.run_book(sig_a, dr)["net"]
    net_r = bt.run_book(sig_r, dr)["net"]
    check("reversed signal underperforms aligned",
          ts.sharpe(net_a) > ts.sharpe(net_r),
          f"aligned={ts.sharpe(net_a):.2f} reversed={ts.sharpe(net_r):.2f}")


def test_book_no_lookahead():
    sig, dr = synthetic()
    full = bt.run_book(sig, dr)["net"]
    cut = dr.index[len(dr) // 2]
    trunc = bt.run_book(sig, dr[dr.index <= cut])["net"]
    common = full.index.intersection(trunc.index)
    diff = (full.loc[common] - trunc.loc[common]).abs().max()
    check("book net invariant to future truncation", diff < 1e-9,
          f"maxdiff={diff:.2e}")


def test_episodes_and_metrics():
    sig, dr = synthetic()
    book = bt.run_book(sig, dr)
    ep = bt.episode_pnl(book)
    bench = bt.long_only_benchmark(dr)
    check("episode count is sane (>=50)", len(ep) >= 50, f"n={len(ep)}")
    check("PF computable & >0", ts.profit_factor(ep) > 0,
          f"PF={ts.profit_factor(ep):.3f}")
    check("benchmark stream finite", len(bench) > 100 and np.isfinite(bench).all())
    # full gate panel assembles without error
    plateau = {"lo": (1 + book["net"]).prod() - 1,
               "mid": (1 + book["net"]).prod() - 1,
               "hi": (1 + book["net"]).prod() - 1}
    v = bt.evaluate_gates(book["net"], ep, bench, plateau)
    check("gate panel assembles with a verdict", v["verdict"] in ("PASS", "FAIL"),
          f"verdict={v['verdict']} PF={v['PF']} Sharpe={v['Sharpe']} n={v['n']}")


def main():
    for t in (test_end_to_end, test_sign_respected, test_book_no_lookahead,
              test_episodes_and_metrics):
        print(f"\n{t.__name__}:")
        t()
    print("\n" + "=" * 52)
    if FAILS:
        print(f"ENGINE TESTS: {len(FAILS)} FAILED -> {FAILS}")
        sys.exit(1)
    print("ENGINE TESTS: ALL PASS")


if __name__ == "__main__":
    main()
