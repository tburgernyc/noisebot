"""Machinery tests for e15_alphascope.py, run on SYNTHETIC data (repo
convention: verify on synthetic data before any registered window is
touched). Not a registered evaluation -- see E15_HYPOTHESIS_DRAFT.md for
the actual registration and real-data plan.
"""
import numpy as np
import pandas as pd

from e15_alphascope import compute_signals, run_backtest, max_dd

RNG = np.random.default_rng(11)


def make_synthetic(n=1500, start=100.0):
    """Trending-with-noise synthetic OHLCV so the trend filter actually
    has something to catch (pure random walk would starve every gate)."""
    drift = np.concatenate([np.full(n // 3, 0.0006), np.full(n // 3, -0.0004),
                            np.full(n - 2 * (n // 3), 0.0003)])
    shocks = RNG.normal(0, 0.006, n)
    close = start * np.cumprod(1 + drift + shocks)
    high = close * (1 + np.abs(RNG.normal(0, 0.003, n)))
    low = close * (1 - np.abs(RNG.normal(0, 0.003, n)))
    open_ = np.concatenate([[start], close[:-1]]) * (1 + RNG.normal(0, 0.001, n))
    idx = pd.date_range("2024-01-01", periods=n, freq="4h")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close}, index=idx)


df = make_synthetic()
sig = compute_signals(df)


def test_state_domain():
    assert set(sig["bb_state"].unique()) <= {-1.0, 0.0, 1.0}
    assert set(sig["trend_state"].unique()) <= {-1.0, 0.0, 1.0}
    assert sig["width_ok"].dtype == bool
    assert not (sig["buy"] & sig["sell"]).any()
    print("PASS state_domain")


def test_no_lookahead():
    """Perturb FUTURE bars; signals at and before the cut bar must not
    change (mirrors test_signals.py's test_no_lookahead)."""
    k = len(df) // 2
    cut = df.iloc[:k].copy()
    fut = df.iloc[k:].copy() * 1.8  # corrupt the future hard
    df_alt = pd.concat([cut, fut])
    sig_alt = compute_signals(df_alt)
    cols = ["width_pct", "bb_state", "trend_state", "buy", "sell"]
    a, b = sig.iloc[:k][cols], sig_alt.iloc[:k][cols]
    for col in cols:
        if a[col].dtype == bool:
            assert (a[col] == b[col]).all(), f"lookahead in {col}!"
        else:
            assert np.allclose(a[col].values, b[col].values, equal_nan=True), f"lookahead in {col}!"
    print("PASS no_lookahead")


def test_backtest_runs_long_flat():
    trades, daily, eq = run_backtest(df, sig, allow_short=False)
    assert np.isfinite(eq.values).all(), "non-finite equity"
    assert (eq.values > 0).all(), "equity went non-positive (bug, not a real result)"
    assert np.isfinite(max_dd(eq.values))
    print(f"PASS backtest_runs_long_flat (n_trades={len(trades)}, "
          f"final={eq.iloc[-1]:.3f}x, maxDD={max_dd(eq.values):.1%})")


def test_backtest_runs_long_short():
    trades, daily, eq = run_backtest(df, sig, allow_short=True)
    assert np.isfinite(eq.values).all() and (eq.values > 0).all()
    print(f"PASS backtest_runs_long_short (n_trades={len(trades)}, final={eq.iloc[-1]:.3f}x)")


def test_flat_when_neither_condition_holds():
    both_false = ~sig["buy"] & ~sig["sell"]
    assert both_false.any(), "synthetic data never produced a flat bar -- filters too loose to test"
    print("PASS flat_when_neither_condition_holds")


if __name__ == "__main__":
    test_state_domain()
    test_no_lookahead()
    test_backtest_runs_long_flat()
    test_backtest_runs_long_short()
    test_flat_when_neither_condition_holds()
    print("\nALL TESTS PASS (synthetic data only -- not a registered evaluation)")
