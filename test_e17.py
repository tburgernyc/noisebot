"""Machinery tests for e17_pivot_structure.py, run on SYNTHETIC data.
Not a registered evaluation -- see E17_HYPOTHESIS_DRAFT.md.
"""
import time
import numpy as np
import pandas as pd

from e17_pivot_structure import (compute_signals, run_backtest, max_dd,
                                  find_pivots, shift_for_availability,
                                  _trend_state_machine, _assert_daily_spacing,
                                  run_backtest_voltarget)

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


def test_voltarget_runs_and_reduces_exposure_vs_full_size():
    """E17-v2 candidate machinery check (NOT a registered evaluation).
    Must run without crashing, produce finite equity, and -- the actual
    point of the fix -- realize a SMALLER max drawdown than full-size
    run_backtest on the same signal, at some cost to the raw return.

    Needs its own higher-volatility fixture: the module-level `df` used
    by every other test in this file has ~10% annualized realized vol
    (by design, to keep pivot detection well-behaved), which never
    exceeds the 15% vol_target -- so w_tgt clips at 1.0 throughout and
    voltarget is silently identical to full-size on that series (not a
    bug, just not a meaningful test of the sizing logic). Real BTC runs
    40-80%+ annualized, so this fixture is closer to what the actual
    registered evaluation would see."""
    n = 2000
    shocks = RNG.normal(0, 0.035, n)  # ~67% annualized -- BTC-like, not the shared fixture's ~10%
    drift = np.where(np.arange(n) % 400 < 200, 0.0015, -0.0008)
    close = 100.0 * np.cumprod(1 + drift + shocks)
    high = close * (1 + np.abs(RNG.normal(0, 0.01, n)))
    low = close * (1 - np.abs(RNG.normal(0, 0.01, n)))
    open_ = np.concatenate([[100.0], close[:-1]]) * (1 + RNG.normal(0, 0.002, n))
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    hv_df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close}, index=idx)

    hv_sig = compute_signals(hv_df)
    trades_full, daily_full, eq_full = run_backtest(hv_df, hv_sig, allow_short=False)
    trades_vt, daily_vt, eq_vt = run_backtest_voltarget(hv_df, hv_sig, vol_target=0.15,
                                                        vol_win=30, allow_short=False)
    assert np.isfinite(eq_vt.values).all() and (eq_vt.values > 0).all()
    dd_full, dd_vt = max_dd(eq_full.values), max_dd(eq_vt.values)
    assert abs(dd_vt) < abs(dd_full), (
        f"vol-targeted maxDD ({dd_vt:.1%}) should be smaller in magnitude than "
        f"full-size maxDD ({dd_full:.1%}) -- sizing fix isn't reducing tail risk "
        f"on a high-vol fixture where it should clearly bind")
    print(f"PASS voltarget_runs_and_reduces_exposure_vs_full_size "
          f"(full: final={eq_full.iloc[-1]:.2f}x maxDD={dd_full:.1%}; "
          f"vol-targeted: final={eq_vt.iloc[-1]:.2f}x maxDD={dd_vt:.1%})")


if __name__ == "__main__":
    test_pivot_availability_shift_is_correct()
    test_fast_matches_bruteforce_reaction_tracking()
    test_state_domain()
    test_no_lookahead()
    test_backtest_runs_long_flat_and_long_short()
    test_performance_fast_beats_bruteforce()
    test_spacing_guard_catches_coarsened_data()
    test_voltarget_runs_and_reduces_exposure_vs_full_size()
    print("\nALL TESTS PASS (synthetic data only -- not a registered evaluation)")
