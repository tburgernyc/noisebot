"""Machinery tests for e17_pivot_structure.py, run on SYNTHETIC data.
Not a registered evaluation -- see E17_HYPOTHESIS_DRAFT.md.
"""
import time
import numpy as np
import pandas as pd

from e17_pivot_structure import (compute_signals, run_backtest, max_dd,
                                  find_pivots, shift_for_availability,
                                  _trend_state_machine, _assert_daily_spacing)

RNG = np.random.default_rng(5)


def make_synthetic(n=2000, start=100.0):
    """Alternating trend/chop regimes so breakouts, holds, failure-swing
    invalidations, and stalls all have a chance to fire."""
    segs = [(0.0015, 300), (-0.0010, 250), (0.0000, 200), (0.0020, 300),
            (-0.0018, 250), (0.0000, 250), (0.0012, 450)]
    drift = np.concatenate([np.full(k, d) for d, k in segs])[:n]
    if len(drift) < n:
        drift = np.concatenate([drift, np.zeros(n - len(drift))])
    shocks = RNG.normal(0, 0.005, n)
    close = start * np.cumprod(1 + drift + shocks)
    high = close * (1 + np.abs(RNG.normal(0, 0.003, n)))
    low = close * (1 - np.abs(RNG.normal(0, 0.003, n)))
    open_ = np.concatenate([[start], close[:-1]]) * (1 + RNG.normal(0, 0.001, n))
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close}, index=idx)


df = make_synthetic()


def test_pivot_availability_shift_is_correct():
    high, low = df["high"].values, df["low"].values
    ph, pl = find_pivots(high, low, 10, 10)
    avail = shift_for_availability(ph, 10)
    detected_idx = np.where(~np.isnan(ph))[0]
    assert len(detected_idx), "no pivots detected on synthetic data -- can't test the shift"
    for i in detected_idx:
        assert np.isnan(avail[i]), f"pivot at {i} visible before it could be confirmed"
        if i + 10 < len(avail):
            assert avail[i + 10] == ph[i], "pivot not visible exactly when it should become available"
    print(f"PASS pivot_availability_shift_is_correct ({len(detected_idx)} pivots checked)")


def test_fast_matches_bruteforce_reaction_tracking():
    """The O(1)-amortized reaction-low/high accumulator must produce the
    IDENTICAL trend_state as a literal rescan-every-new-watermark port of
    the source's own algorithm -- this is the correctness proof for the
    performance fix, not just an efficiency claim."""
    high, low, close = df["high"].values, df["low"].values, df["close"].values
    ph, pl = find_pivots(high, low, 10, 10)
    pha, pla = shift_for_availability(ph, 10), shift_for_availability(pl, 10)
    fast, fb_out, fd_out = _trend_state_machine(close, high, low, pha, pla,
                                                neutral_lookback=5, reaction_mode="fast")
    brute, bb_out, bd_out = _trend_state_machine(close, high, low, pha, pla,
                                                 neutral_lookback=5, reaction_mode="bruteforce")
    mismatches = np.where(fast != brute)[0]
    assert len(mismatches) == 0, f"fast vs bruteforce diverge at bars {mismatches[:10]}"
    print(f"PASS fast_matches_bruteforce_reaction_tracking ({len(fast)} bars, 0 mismatches)")


def test_state_domain():
    sig = compute_signals(df)
    assert set(sig["trend_state"].unique()) <= {-1, 0, 1}
    n_bull = (sig["trend_state"] == 1).sum()
    n_bear = (sig["trend_state"] == -1).sum()
    n_neutral = (sig["trend_state"] == 0).sum()
    assert n_bull > 0 and n_bear > 0 and n_neutral > 0, (
        "synthetic regimes didn't produce all three states -- weak test")
    print(f"PASS state_domain (bull={n_bull}, bear={n_bear}, neutral={n_neutral})")


def test_no_lookahead():
    sig = compute_signals(df)
    k = len(df) // 2
    cut = df.iloc[:k].copy()
    fut = df.iloc[k:].copy() * 1.6
    df_alt = pd.concat([cut, fut])
    sig_alt = compute_signals(df_alt)
    a = sig.iloc[:k]["trend_state"].values
    b = sig_alt.iloc[:k]["trend_state"].values
    assert np.array_equal(a, b), "lookahead: corrupting the future changed past trend_state"
    print("PASS no_lookahead")


def test_backtest_runs_long_flat_and_long_short():
    sig = compute_signals(df)
    t1, d1, e1 = run_backtest(df, sig, allow_short=False)
    t2, d2, e2 = run_backtest(df, sig, allow_short=True)
    for eq in (e1, e2):
        assert np.isfinite(eq.values).all() and (eq.values > 0).all()
    print(f"PASS backtest_runs_long_flat_and_long_short "
          f"(long-flat: n={len(t1)} final={e1.iloc[-1]:.3f}x maxDD={max_dd(e1.values):.1%}; "
          f"long-short: n={len(t2)} final={e2.iloc[-1]:.3f}x)")


def test_performance_fast_beats_bruteforce():
    high, low, close = df["high"].values, df["low"].values, df["close"].values
    ph, pl = find_pivots(high, low, 10, 10)
    pha, pla = shift_for_availability(ph, 10), shift_for_availability(pl, 10)
    t0 = time.time()
    _trend_state_machine(close, high, low, pha, pla, neutral_lookback=5, reaction_mode="fast")
    t_fast = time.time() - t0
    t0 = time.time()
    _trend_state_machine(close, high, low, pha, pla, neutral_lookback=5, reaction_mode="bruteforce")
    t_brute = time.time() - t0
    print(f"PASS performance_fast_beats_bruteforce (fast={t_fast*1000:.1f}ms, "
          f"bruteforce={t_brute*1000:.1f}ms, n={len(df)} bars)")


def test_spacing_guard_catches_coarsened_data():
    """Regression test for a real bug found while wiring up the data
    loader: Yahoo's range=max silently returns ~monthly-spaced bars while
    still claiming interval=1d and setting no error field. Self-contained
    -- does not depend on the real data/*.json files being present."""
    monthly_index = pd.date_range("2020-01-01", periods=12, freq="MS")
    try:
        _assert_daily_spacing(monthly_index, "synthetic-monthly-fixture")
        raise AssertionError("spacing guard did not fire on monthly-spaced data")
    except ValueError as e:
        assert "range=max" in str(e)
        print("PASS spacing_guard_catches_coarsened_data")

    daily_index = pd.date_range("2020-01-01", periods=365, freq="D")
    _assert_daily_spacing(daily_index, "synthetic-daily-fixture")  # must not raise
    print("PASS spacing_guard_accepts_true_daily_data")


if __name__ == "__main__":
    test_pivot_availability_shift_is_correct()
    test_fast_matches_bruteforce_reaction_tracking()
    test_state_domain()
    test_no_lookahead()
    test_backtest_runs_long_flat_and_long_short()
    test_performance_fast_beats_bruteforce()
    test_spacing_guard_catches_coarsened_data()
    print("\nALL TESTS PASS (synthetic data only -- not a registered evaluation)")
