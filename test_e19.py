"""Machinery tests for e19_funding_basis (synthetic data only -- no
evaluation of the registered hypothesis happens here). Run:
python3 test_e19.py"""
import numpy as np
import pandas as pd

from e19_funding_basis import run_e19_single, run_e19, LOOKBACK_D, SPOT_COST, PERP_COST

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


if __name__ == "__main__":
    test_enters_and_collects_positive_funding()
    test_below_entry_stays_flat()
    test_hedge_neutrality_despite_large_price_move()
    test_hysteresis_band_avoids_whipsaw()
    test_costs_charged_both_legs_on_entry_and_exit()
    test_no_lookahead()
    test_funding_magnitude()
    test_multi_asset_combination()
    print("\nALL E19 MACHINERY TESTS PASS")
