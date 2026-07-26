"""Machinery tests for e19_funding_basis (synthetic data only -- no
evaluation of the registered hypothesis happens here). Run:
python3 test_e19.py"""
import numpy as np
import pandas as pd

from e19_funding_basis import (run_e19_single, run_e19, LOOKBACK_D, SPOT_COST, PERP_COST,
                                run_e19_single_v2, run_e19_v2, load_mark_price_daily)

IDX = pd.date_range("2024-01-01", periods=150, freq="D", tz="UTC")


def _trend_px(total_drift: float = 0.50, vol: float = 0.02, seed: int = 7) -> pd.Series:
    """Strong trending + volatile price path -- deliberately NOT flat,
    so the hedge-neutrality test is a real check, not a trivial one."""
    rng = np.random.default_rng(seed)
    n = len(IDX)
    steps = total_drift / n + rng.normal(0, vol, n)
    return pd.Series(100.0 * np.cumprod(1 + steps), index=IDX)


def _const_fund(ann: float) -> pd.DataFrame:
    """Constant funding at `ann` annualized: 3 prints/day of ann/(3*365)."""
    rate = ann / (3 * 365)
    return pd.DataFrame({"ann_mean": ann, "day_sum": 3 * rate}, index=IDX)


def _step_fund(values: list, seg_len: int) -> pd.DataFrame:
    """Piecewise-constant annualized funding, `seg_len` days/segment
    (clamped to the last value past the end), for exercising
    entry/exit/hysteresis transitions."""
    n = len(IDX)
    ann = np.array([values[min(i // seg_len, len(values) - 1)] for i in range(n)])
    rate = ann / (3 * 365)
    return pd.DataFrame({"ann_mean": ann, "day_sum": 3 * rate}, index=IDX)


def test_enters_and_collects_positive_funding():
    px = _trend_px()
    fund = _const_fund(0.50)
    trades, daily, eq, att = run_e19_single(px, fund, entry=0.08, exit_thr=0.03)
    assert len(trades) == 1, "constant above-entry funding: one continuous episode"
    assert att["funding"] > 0, "hedged and funding positive -> must collect"
    assert eq.iloc[-1] > 1.0
    print(f"PASS enters_and_collects (funding {att['funding']:+.4f}, "
          f"price {att['price']:+.4f}, trades {len(trades)})")


def test_below_entry_stays_flat():
    px = _trend_px()
    fund = _const_fund(0.05)  # below entry=0.08
    trades, daily, eq, att = run_e19_single(px, fund, entry=0.08, exit_thr=0.03)
    assert len(trades) == 0
    assert (eq == 1.0).all()
    print("PASS below_entry_stays_flat")


def test_hedge_neutrality_despite_large_price_move():
    """Core E19 claim: even with a strongly trending/volatile price
    path, price-leg P&L is ~0 because spot and perp legs are always
    sized equal-and-opposite off the same price series (the disclosed
    proxy simplification -- see module docstring)."""
    px = _trend_px(total_drift=1.20, vol=0.03)  # big, noisy uptrend
    fund = _const_fund(0.50)
    trades, daily, eq, att = run_e19_single(px, fund, entry=0.08, exit_thr=0.03)
    assert abs(att["price"]) < 1e-8, f"price leg should net to ~0, got {att['price']}"
    print(f"PASS hedge_neutrality (price leg {att['price']:.2e} despite "
          f"{(px.iloc[-1] / px.iloc[0] - 1):+.1%} spot move)")


def test_hysteresis_band_avoids_whipsaw():
    """Funding walks 0.01 -> 0.05 -> 0.10 -> 0.05 -> 0.01 (30d/segment).
    Must not enter during the first 0.05 leg (below entry=0.08), must
    enter once in the 0.10 leg, and must NOT exit during the second
    0.05 leg (mid-band, above exit=0.03) -- only once back at 0.01."""
    seg_len = 30
    fund = _step_fund([0.01, 0.05, 0.10, 0.05, 0.01], seg_len)
    px = _trend_px()
    trades, daily, eq, att = run_e19_single(px, fund, entry=0.08, exit_thr=0.03)
    assert len(trades) == 1, f"expected exactly one episode, got {len(trades)}"
    first_entry, exit_time = trades.iloc[0]["entry"], trades.iloc[0]["exit"]
    assert first_entry >= IDX[2 * seg_len], (
        f"entered before crossing the entry threshold: {first_entry}")
    assert exit_time >= IDX[4 * seg_len], (
        f"exited while funding was still above the exit threshold: {exit_time}")
    print(f"PASS hysteresis_band (entered {first_entry.date()}, "
          f"exited {exit_time.date()})")


def test_costs_charged_both_legs_on_entry_and_exit():
    fund = _step_fund([0.01, 0.50, 0.01], 40)  # flat -> hedge -> flat
    px = pd.Series(100.0, index=IDX)  # zero price move: isolate cost+funding
    trades, daily, eq, att = run_e19_single(px, fund, entry=0.08, exit_thr=0.03)
    assert len(trades) == 1
    expect_cost = 2 * (SPOT_COST + PERP_COST)  # one entry + one exit, both legs
    assert abs(att["costs"] - expect_cost) < 1e-9, \
        f"costs {att['costs']} vs expected {expect_cost}"
    print(f"PASS costs_both_legs (costs={att['costs']:.4f}, "
          f"expected {expect_cost:.4f})")


def test_no_lookahead():
    px = _trend_px()
    fund = _const_fund(0.50)
    _, _, eq_full, _ = run_e19_single(px, fund, entry=0.08, exit_thr=0.03)
    cut = IDX[:-30]
    _, _, eq_cut, _ = run_e19_single(px.loc[cut], fund.loc[cut], entry=0.08, exit_thr=0.03)
    a, b = eq_full.loc[cut[:-1]], eq_cut.iloc[:-1]
    assert np.allclose(a.values, b.values), "lookahead detected"
    print("PASS no_lookahead")


def test_funding_magnitude():
    """Fixed 1-unit sizing (no vol-targeting in E19, unlike E7's
    min(1, vol_target/sigma)): funding P&L while held should track
    ann/365 * days_held tightly, with no vol-scaling factor to muddy it."""
    px = _trend_px(seed=11)
    fund = _const_fund(0.50)
    trades, daily, eq, att = run_e19_single(px, fund, entry=0.08, exit_thr=0.03)
    assert len(trades) == 1
    days_held = (trades.iloc[0]["exit"] - trades.iloc[0]["entry"]).days
    expect = 0.50 / 365 * days_held
    assert abs(att["funding"] - expect) / expect < 0.05, \
        f"funding {att['funding']:.4f} vs expected ~{expect:.4f} ({days_held}d)"
    print(f"PASS funding_magnitude ({att['funding']:.4f} ~ {expect:.4f}, {days_held}d)")


def test_multi_asset_combination():
    """run_e19: 2-asset book, only one hedged -> portfolio daily return
    on any day should be exactly half that asset's own return (equal-
    weight average of {active_return, 0})."""
    px = pd.DataFrame({"A": _trend_px(seed=1), "B": _trend_px(seed=2)})
    fund = {"A": _const_fund(0.50), "B": _const_fund(0.01)}  # A hedges, B stays flat
    trades, daily, eq, per_asset, att = run_e19(px, fund, entry=0.08, exit_thr=0.03)
    assert set(trades["asset"].unique()) == {"A"}
    a_daily = per_asset["A"][1]
    common = daily.index.intersection(a_daily.index)
    assert len(common) > 100
    assert np.allclose(daily.loc[common].values, 0.5 * a_daily.loc[common].values), \
        "2-asset equal-weight average mismatch"
    print(f"PASS multi_asset_combination (A trades={len(per_asset['A'][0])}, "
          f"B trades={len(per_asset['B'][0])}, combined={len(trades)})")


# ---------------------------------------------------------------------------
# E19-v2: real perp mark price instead of the spot proxy
# ---------------------------------------------------------------------------

def test_v2_matches_v1_when_perp_equals_spot():
    """Regression/consistency check: if px_perp == px_spot (i.e. no real
    basis at all), v2 must reduce to identical results as v1's spot-proxy
    construction -- the only thing that's supposed to differ is what
    prices the perp leg."""
    px = _trend_px()
    fund = _const_fund(0.50)
    t1, d1, e1, a1 = run_e19_single(px, fund, entry=0.08, exit_thr=0.03)
    t2, d2, e2, a2 = run_e19_single_v2(px, px, fund, entry=0.08, exit_thr=0.03)
    assert t1.equals(t2), "trades should be identical when perp==spot"
    assert np.allclose(d1.values, d2.values)
    assert np.allclose(e1.values, e2.values)
    assert abs(a1["price"] - a2["price"]) < 1e-9
    assert abs(a1["funding"] - a2["funding"]) < 1e-9
    print("PASS v2_matches_v1_when_perp_equals_spot")


def test_v2_captures_real_basis_divergence():
    """Core E19-v2 claim: when the perp genuinely diverges from spot
    while hedged, the price leg is no longer zero -- it captures the
    actual basis move. Verified by an INDEPENDENT replay of the exact
    accumulation logic (not a hand-derived formula), so this doesn't
    just check the code agrees with itself."""
    spot = pd.Series(100.0, index=IDX)  # perfectly flat: isolate the basis effect
    fund = _const_fund(0.50)  # hedge stays on almost the entire series
    perp = spot.copy()
    shock_i = 100
    perp.iloc[shock_i:] = perp.iloc[shock_i:] * 0.90  # perp permanently 10% below spot from here on
    trades, daily, eq, att = run_e19_single_v2(spot, perp, fund, entry=0.08, exit_thr=0.03)
    assert len(trades) == 1

    T = len(IDX)
    c_spot, c_perp = spot.values, perp.values
    spot_ret = np.zeros(T)
    perp_ret = np.zeros(T)
    spot_ret[1:] = c_spot[1:] / c_spot[:-1] - 1.0
    perp_ret[1:] = c_perp[1:] / c_perp[:-1] - 1.0
    fmean = fund["ann_mean"].rolling(LOOKBACK_D, min_periods=LOOKBACK_D).mean().values
    have_f = ~np.isnan(fmean)
    held = False
    replay_price = 0.0
    for t in range(1, T - 1):
        if have_f[t]:
            if not held and fmean[t] > 0.08:
                held = True
            elif held and fmean[t] < 0.03:
                held = False
        w_spot = 1.0 if held else 0.0
        w_perp = -1.0 if held else 0.0
        replay_price += w_spot * spot_ret[t + 1] + w_perp * perp_ret[t + 1]

    assert abs(att["price"] - replay_price) < 1e-9, f"{att['price']} vs {replay_price}"
    assert abs(att["price"]) > 0.05, \
        "a 10% one-time perp/spot divergence while hedged should show up clearly, not wash out"
    print(f"PASS v2_captures_real_basis_divergence (price leg = {att['price']:+.4f}, "
          f"independent replay = {replay_price:+.4f})")


def test_v2_no_lookahead():
    """Same truncation-invariance check as v1, now with a perp series
    that genuinely differs from spot (independent noise), not just a
    trivial equal-series case."""
    spot = _trend_px(seed=3)
    rng = np.random.default_rng(99)
    perp = spot * (1.0 + rng.normal(0, 0.01, len(IDX)).cumsum() * 0.01)
    fund = _const_fund(0.50)
    _, _, eq_full, _ = run_e19_single_v2(spot, perp, fund, entry=0.08, exit_thr=0.03)
    cut = IDX[:-30]
    _, _, eq_cut, _ = run_e19_single_v2(spot.loc[cut], perp.loc[cut], fund.loc[cut],
                                         entry=0.08, exit_thr=0.03)
    a, b = eq_full.loc[cut[:-1]], eq_cut.iloc[:-1]
    assert np.allclose(a.values, b.values), "lookahead detected"
    print("PASS v2_no_lookahead")


def test_v2_multi_asset_combination():
    """run_e19_v2: 2-asset book, only one hedged -> portfolio daily
    return should be exactly half that asset's own return (same
    equal-weight-average check as v1, now through the v2 engine)."""
    px_spot = pd.DataFrame({"A": _trend_px(seed=1), "B": _trend_px(seed=2)})
    px_perp = {"A": px_spot["A"] * 0.999, "B": px_spot["B"] * 1.001}  # small, real basis on each
    fund = {"A": _const_fund(0.50), "B": _const_fund(0.01)}  # A hedges, B stays flat
    trades, daily, eq, per_asset, att = run_e19_v2(px_spot, px_perp, fund, entry=0.08, exit_thr=0.03)
    assert set(trades["asset"].unique()) == {"A"}
    a_daily = per_asset["A"][1]
    common = daily.index.intersection(a_daily.index)
    assert len(common) > 100
    assert np.allclose(daily.loc[common].values, 0.5 * a_daily.loc[common].values), \
        "2-asset equal-weight average mismatch"
    print(f"PASS v2_multi_asset_combination (A trades={len(per_asset['A'][0])}, "
          f"B trades={len(per_asset['B'][0])}, combined={len(trades)})")


def test_load_mark_price_daily_handles_missing_header():
    """The real Binance-archive quirk found while sourcing this data:
    monthly files before ~2022-02 have NO header row, later ones do.
    Build one synthetic file of each kind and confirm they parse to
    identical, correctly-typed results either way."""
    import tempfile, os
    d = tempfile.mkdtemp()
    # 2020-01: no header (pre-2022-02 style)
    with open(os.path.join(d, "XUSDT-1d-2020-01.csv"), "w") as f:
        f.write("1577836800000,100.0,105.0,99.0,102.0,0,1577923199999,0,10,0,0,0\n")
        f.write("1577923200000,102.0,103.0,98.0,99.0,0,1578009599999,0,10,0,0,0\n")
    # 2020-02: WITH header (post-2022-02 style) -- exercises the other branch
    with open(os.path.join(d, "XUSDT-1d-2020-02.csv"), "w") as f:
        f.write("open_time,open,high,low,close,volume,close_time,quote_volume,"
                "count,taker_buy_volume,taker_buy_quote_volume,ignore\n")
        f.write("1580515200000,99.0,101.0,97.0,100.5,0,1580601599999,0,10,0,0,0\n")
    s = load_mark_price_daily(d, "XUSDT")
    assert len(s) == 3
    assert abs(s.iloc[0] - 102.0) < 1e-9
    assert abs(s.iloc[1] - 99.0) < 1e-9
    assert abs(s.iloc[2] - 100.5) < 1e-9
    assert str(s.index.tz) == "UTC"
    print("PASS load_mark_price_daily_handles_missing_header")


if __name__ == "__main__":
    test_enters_and_collects_positive_funding()
    test_below_entry_stays_flat()
    test_hedge_neutrality_despite_large_price_move()
    test_hysteresis_band_avoids_whipsaw()
    test_costs_charged_both_legs_on_entry_and_exit()
    test_no_lookahead()
    test_funding_magnitude()
    test_multi_asset_combination()
    test_v2_matches_v1_when_perp_equals_spot()
    test_v2_captures_real_basis_divergence()
    test_v2_no_lookahead()
    test_v2_multi_asset_combination()
    test_load_mark_price_daily_handles_missing_header()
    print("\nALL E19 MACHINERY TESTS PASS (v1 + v2)")
