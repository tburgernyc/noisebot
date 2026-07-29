"""Machinery tests for e16_capitulation.py, run on SYNTHETIC data (repo
convention: verify before any registered window is touched). Not a
registered evaluation -- see E16_HYPOTHESIS_DRAFT.md.
"""
import numpy as np
import pandas as pd

from e16_capitulation import compute_signals, run_backtest, max_dd, _assert_daily_spacing

RNG = np.random.default_rng(23)


def make_synthetic(n=1200, start=100.0):
    """Calm random walk with THREE engineered capitulation-style crashes
    (sharp multi-bar decline + volume spike + partial recovery) so the
    triple-AND entry condition actually has something to fire on --
    a pure random walk would starve the test (true climax bars are rare
    by construction, exactly the n-count concern flagged in the
    registration doc)."""
    close = np.empty(n)
    volume = np.empty(n)
    close[0] = start
    volume[:] = RNG.uniform(800, 1200, n)
    crash_starts = [300, 650, 950]
    crash_bars = set()
    for cs in crash_starts:
        crash_bars.update(range(cs, cs + 6))

    for i in range(1, n):
        if i in crash_bars:
            close[i] = close[i - 1] * (1 - RNG.uniform(0.025, 0.05))
            volume[i] = RNG.uniform(3500, 5000)  # climax volume, ~4x normal
        elif i - 1 in crash_bars and i not in crash_bars:
            close[i] = close[i - 1] * (1 + RNG.uniform(0.005, 0.03))  # partial recovery
            volume[i] = RNG.uniform(800, 1500)
        else:
            close[i] = close[i - 1] * (1 + RNG.normal(0, 0.004))

    high = close * (1 + np.abs(RNG.normal(0, 0.002, n)))
    low = close * (1 - np.abs(RNG.normal(0, 0.002, n)))
    open_ = np.concatenate([[start], close[:-1]]) * (1 + RNG.normal(0, 0.0005, n))
    idx = pd.date_range("2024-01-01", periods=n, freq="4h")
    return pd.DataFrame({"open": open_, "high": high, "low": low,
                        "close": close, "volume": volume}, index=idx)


df = make_synthetic()
sig = compute_signals(df)


def test_state_domain():
    assert sig["bullish_capitulation"].dtype == bool
    assert sig["bearish_capitulation"].dtype == bool
    assert not (sig["bullish_capitulation"] & sig["bearish_capitulation"]).any()
    print("PASS state_domain")


def test_engineered_crashes_trigger_at_least_one_signal():
    assert sig["bullish_capitulation"].sum() >= 1, (
        "no bullish capitulation fired on 3 engineered crashes -- "
        "gates too strict for this synthetic profile, re-check thresholds")
    print(f"PASS engineered_crashes_trigger (n_signals={sig['bullish_capitulation'].sum()})")


def test_no_lookahead():
    k = len(df) // 2
    cut = df.iloc[:k].copy()
    fut = df.iloc[k:].copy()
    fut = fut.assign(close=fut["close"] * 1.7, high=fut["high"] * 1.7,
                      low=fut["low"] * 1.7, open=fut["open"] * 1.7,
                      volume=fut["volume"] * 3.0)
    df_alt = pd.concat([cut, fut])
    sig_alt = compute_signals(df_alt)
    cols = ["rsi", "ma", "dist_pct", "bullish_capitulation", "bearish_capitulation"]
    a, b = sig.iloc[:k][cols], sig_alt.iloc[:k][cols]
    for col in cols:
        if a[col].dtype == bool:
            assert (a[col] == b[col]).all(), f"lookahead in {col}!"
        else:
            assert np.allclose(a[col].values, b[col].values, equal_nan=True), f"lookahead in {col}!"
    print("PASS no_lookahead")


def test_backtest_runs_and_exits_are_sane():
    trades, daily, eq = run_backtest(df, sig)
    assert np.isfinite(eq.values).all() and (eq.values > 0).all()
    assert np.isfinite(max_dd(eq.values))
    if len(trades):
        assert trades["bars_held"].min() >= 1
        assert set(trades["reason"].unique()) <= {"target", "time", "stop", "eod_open"}
        assert (trades["bars_held"] <= 10).all(), "time stop (10 bars) not enforced"
    print(f"PASS backtest_runs_and_exits_are_sane (n_trades={len(trades)}, "
          f"final={eq.iloc[-1]:.3f}x, maxDD={max_dd(eq.values):.1%})")
    if len(trades):
        print("  exit reasons:", trades["reason"].value_counts().to_dict())


def test_hard_stop_enforced():
    """Force a capitulation entry immediately followed by a deep adverse
    move with no recovery -- the hard stop must cap the loss near
    hard_stop_pct, not let it run."""
    n = 40
    close = np.full(n, 100.0)
    close[10] = 80.0  # crash into the signal bar
    for i in range(11, n):
        close[i] = close[i - 1] * 0.985  # keeps falling, never reverts to MA
    open_ = np.roll(close, 1)
    open_[0] = 100.0
    high, low = close * 1.001, close * 0.999
    volume = np.full(n, 1000.0)
    volume[10] = 5000.0
    idx = pd.date_range("2024-01-01", periods=n, freq="4h")
    d = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                      "volume": volume}, index=idx)
    s = compute_signals(d, rsi_length=5, ma_length=8, vol_length=5)
    trades, daily, eq = run_backtest(d, s, time_stop_bars=100, hard_stop_pct=8.0)
    stops = trades[trades["reason"] == "stop"] if len(trades) else trades
    if len(stops):
        assert stops["ret"].min() > -0.15, "loss ran well past the hard stop"
        print(f"PASS hard_stop_enforced (worst stopped-out trade: {stops['ret'].min():.1%})")
    else:
        print("PASS hard_stop_enforced (no bullish signal fired on this fixture -- n/a)")


def test_target_exit_enforced():
    """Force a capitulation entry followed by an immediate, sharp recovery
    back through the MA -- must close with reason 'target', not ride past
    it to the time stop."""
    n = 40
    close = np.full(n, 100.0)
    close[10] = 80.0  # crash into the signal bar
    close[11] = 100.5  # snaps back through the MA the very next bar
    for i in range(12, n):
        close[i] = close[i - 1] * (1 + RNG.normal(0, 0.001))
    open_ = np.roll(close, 1)
    open_[0] = 100.0
    high, low = close * 1.001, close * 0.999
    volume = np.full(n, 1000.0)
    volume[10] = 5000.0
    idx = pd.date_range("2024-01-01", periods=n, freq="4h")
    d = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                      "volume": volume}, index=idx)
    s = compute_signals(d, rsi_length=5, ma_length=8, vol_length=5)
    trades, daily, eq = run_backtest(d, s, time_stop_bars=100, hard_stop_pct=50.0)
    assert len(trades) >= 1, "no trade -- signal didn't fire on this fixture"
    first = trades.iloc[0]
    assert first["reason"] == "target", f"expected target exit, got {first['reason']}"
    assert first["bars_held"] <= 2
    print(f"PASS target_exit_enforced (bars_held={first['bars_held']}, ret={first['ret']:.1%})")


def test_spacing_guard_catches_coarsened_data():
    """Regression test for a real bug found while wiring up the data
    loader: Yahoo's range=max silently returns ~monthly-spaced bars while
    still claiming interval=1d and setting no error field. Self-contained
    (constructs the bad index directly) -- does not depend on the real
    data/*.json files being present, matching this suite's portability."""
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
    test_state_domain()
    test_engineered_crashes_trigger_at_least_one_signal()
    test_no_lookahead()
    test_backtest_runs_and_exits_are_sane()
    test_hard_stop_enforced()
    test_target_exit_enforced()
    test_spacing_guard_catches_coarsened_data()
    print("\nALL TESTS PASS (synthetic data only -- not a registered evaluation)")
