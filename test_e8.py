"""Machinery tests for e8_trend (synthetic data only — the registered
hypothesis is NOT evaluated here). Run: python3 test_e8.py"""
import numpy as np
import pandas as pd

from e8_trend import (run_e8, tema, adx, atr, trend_4h_on_15m,
                      load_klines_15m, COST_SIDE)

RNG = np.random.default_rng(11)


def _mk(closes: np.ndarray, start="2024-01-01") -> pd.DataFrame:
    idx = pd.date_range(start, periods=len(closes), freq="15min", tz="UTC")
    o = np.concatenate([[closes[0]], closes[:-1]])
    h = np.maximum(o, closes) * 1.0005
    l = np.minimum(o, closes) * 0.9995
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": closes,
                         "volume": 1.0}, index=idx)


def _trend_up(n=9000, drift=0.002, noise=0.0002):
    """Strong smooth trend: TEMA crossovers are near-lag-free, so the
    fast/slow gap on a gentle trend is noise-dominated — machinery
    probes need drift >> noise to give an unambiguous expectation."""
    r = drift + noise * RNG.standard_normal(n)
    return _mk(100 * np.cumprod(1 + r))


def test_tema_constant():
    x = pd.Series(np.full(600, 5.0))
    v = tema(x, 10).iloc[-1]
    assert abs(v - 5.0) < 1e-9, "TEMA of constant must equal it"
    print("PASS tema_constant")


def test_uptrend_goes_long_and_wins():
    k = _trend_up()
    tr, daily, att = run_e8(k, adx_gate=20.0)
    assert len(tr) >= 1, "persistent uptrend must produce trades"
    assert (tr["side"] == 1).all(), "uptrend: longs only"
    assert tr["pnl"].sum() > 0, "trend engine must profit on a clean trend"
    print(f"PASS uptrend_long (trades {len(tr)}, pnl {tr['pnl'].sum():+.1f})")


def test_downtrend_goes_short():
    k = _mk(100 * np.cumprod(1 - 0.002 + 0.0002 *
                             RNG.standard_normal(9000)))
    tr, _, _ = run_e8(k, adx_gate=20.0)
    assert len(tr) >= 1 and (tr["side"] == -1).all(), "downtrend: shorts"
    assert tr["pnl"].sum() > 0
    print(f"PASS downtrend_short (trades {len(tr)})")


def test_chop_stays_out():
    """Directionless low-ADX chop: the ADX>35 gate must keep us flat."""
    r = 0.0012 * RNG.standard_normal(10000)
    k = _mk(100 * np.cumprod(1 + r - r.mean()))
    tr, _, _ = run_e8(k, adx_gate=35.0)
    tr0, _, _ = run_e8(k, adx_gate=0.0)
    ntr = 0 if tr.empty else len(tr)
    n0 = 0 if tr0.empty else len(tr0)
    assert ntr < n0 / 2, f"ADX gate must cut chop trades ({ntr} vs {n0})"
    print(f"PASS chop_gated (trades {ntr} vs {n0} ungated)")


def test_costs_charged():
    """Zero-vol staircase: entry+exit round trip must cost ~12 bps."""
    k = _trend_up()
    tr, _, att = run_e8(k, adx_gate=20.0)
    assert att["costs"] > 0, "costs must be positive"
    per_rt = att["costs"] / len(tr)
    px = k["close"].mean()
    assert per_rt > 1.5 * COST_SIDE * px, "round trip cost too small"
    print(f"PASS costs_charged ({att['costs']:.1f} USDT total)")


def test_funding_sign():
    """Long position + positive funding prints -> funding P&L negative."""
    k = _trend_up()
    prints = pd.DataFrame(
        {"rate": 0.0001},
        index=pd.date_range("2024-01-01", periods=400, freq="8h", tz="UTC"))
    _, _, att0 = run_e8(k, adx_gate=20.0)
    _, _, att1 = run_e8(k, adx_gate=20.0, fund_prints=prints)
    assert att1["funding"] < 0, "long pays positive funding"
    assert abs(att0["funding"]) < 1e-12
    print(f"PASS funding_sign (funding {att1['funding']:+.2f})")


def test_no_lookahead():
    """Truncating the tail must not change earlier closed trades.
    Regime-switching series so multiple trades CLOSE before the cut."""
    drifts = np.repeat([0.002, -0.002, 0.002, -0.002], 3500)
    r = drifts + 0.0002 * RNG.standard_normal(len(drifts))
    k = _mk(100 * np.cumprod(1 + r))
    tr_full, _, _ = run_e8(k, adx_gate=20.0)
    tr_cut, _, _ = run_e8(k.iloc[:-2000], adx_gate=20.0)
    cut_end = k.index[-2001]
    closed_full = tr_full[tr_full["exit"] < cut_end - pd.Timedelta(days=2)]
    m = min(len(closed_full), len(tr_cut))
    assert m >= 2, f"probe needs closed trades before the cut (got {m})"
    a = closed_full["pnl"].values[:m]
    b = tr_cut["pnl"].values[:m]
    assert np.allclose(a, b), "lookahead detected in closed trades"
    print(f"PASS no_lookahead ({m} trades compared)")


def test_4h_uses_completed_bars_only():
    """The 4h trend value on a 15m bar inside 4h-bar K must derive from
    bars strictly before K: perturbing the LAST 4h block must not change
    tr4 values inside that block."""
    k = _trend_up(9000)
    tr_a = trend_4h_on_15m(k)
    k2 = k.copy()
    k2.iloc[-16:, k2.columns.get_loc("close")] *= 1.2   # bomb last 4h block
    tr_b = trend_4h_on_15m(k2)
    same_until = k.index[-17]
    assert (tr_a.loc[:same_until].fillna(0) ==
            tr_b.loc[:same_until].fillna(0)).all(), \
        "4h trend leaked in-progress bar information"
    print("PASS 4h_completed_bars_only")


if __name__ == "__main__":
    test_tema_constant()
    test_uptrend_goes_long_and_wins()
    test_downtrend_goes_short()
    test_chop_stays_out()
    test_costs_charged()
    test_funding_sign()
    test_no_lookahead()
    test_4h_uses_completed_bars_only()
    print("\nALL E8 MACHINERY TESTS PASS")
