"""Machinery tests for e7_carry (synthetic data only — no evaluation of
the registered hypothesis happens here). Run: python3 test_e7.py"""
import numpy as np
import pandas as pd

from e7_carry import run_e7, load_funding_daily, LOOKBACK_D, VOL_WIN

IDX = pd.date_range("2024-01-01", periods=120, freq="D", tz="UTC")


def _flat_px(vol_seed: int = 0) -> pd.DataFrame:
    """Prices with tiny alternating moves: realized vol > 0, ~zero drift."""
    steps = np.where(np.arange(len(IDX)) % 2 == 0, 1.001, 1 / 1.001)
    return pd.DataFrame({"BTC": 100 * np.cumprod(steps)}, index=IDX)


def _fund(ann: float) -> dict:
    """Constant funding at `ann` annualized: 3 prints/day of ann/(3*365)."""
    rate = ann / (3 * 365)
    return {"BTC": pd.DataFrame({"ann_mean": ann, "day_sum": 3 * rate},
                                index=IDX)}


def test_short_collects_positive_funding():
    px = _flat_px()
    tr, daily, eq, att = run_e7(px, _fund(0.50), threshold=0.15)
    assert att["funding"] > 0, "short must collect positive funding"
    assert abs(att["price"]) < 0.02, "flat prices: price leg ~0"
    assert eq.iloc[-1] > 1.0, "carry should net positive here"
    print(f"PASS short_collects (funding {att['funding']:+.4f}, "
          f"price {att['price']:+.4f})")


def test_long_collects_negative_funding():
    px = _flat_px()
    tr, daily, eq, att = run_e7(px, _fund(-0.50), threshold=0.15)
    assert att["funding"] > 0, "long must collect negative funding"
    print(f"PASS long_collects (funding {att['funding']:+.4f})")


def test_below_threshold_stays_flat():
    px = _flat_px()
    tr, daily, eq, att = run_e7(px, _fund(0.05), threshold=0.15)
    assert (eq == 1.0).all(), "sub-threshold funding: never in the market"
    assert len(tr) == 0
    print("PASS flat_below_threshold")


def test_funding_magnitude():
    """Held short at w with constant funding f_ann: funding P&L per day
    ~= |w| * f_ann/365. Check within 25% (warmup periods excluded)."""
    px = _flat_px()
    tr, daily, eq, att = run_e7(px, _fund(0.50), threshold=0.15)
    sig = 0.001 * np.sqrt(365)  # ~alternating step vol
    days_held = len(IDX) - max(VOL_WIN, LOOKBACK_D) - 2
    w = min(1.0, 0.15 / (0.0316))  # cap at 1 given tiny vol -> w = 1
    expect = w * 0.50 / 365 * days_held
    assert abs(att["funding"] - expect) / expect < 0.25, \
        f"funding {att['funding']:.4f} vs expected ~{expect:.4f}"
    print(f"PASS funding_magnitude ({att['funding']:.4f} ~ {expect:.4f})")


def test_no_lookahead():
    """Truncating the last 30 days must not change earlier equity."""
    px = _flat_px()
    fund = _fund(0.50)
    _, _, eq_full, _ = run_e7(px, fund, threshold=0.15)
    cut = IDX[:-30]
    _, _, eq_cut, _ = run_e7(px.loc[cut], {"BTC": fund["BTC"].loc[cut]},
                             threshold=0.15)
    a, b = eq_full.loc[cut[:-1]], eq_cut.iloc[:-1]
    assert np.allclose(a.values, b.values), "lookahead detected"
    print("PASS no_lookahead")


def test_loader_annualization():
    """8h print of 0.0001 -> annualized 0.0001*3*365 = 10.95%."""
    import tempfile, os
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "XUSDT-fundingRate-2024-01.csv"), "w") as f:
        f.write("calc_time,funding_interval_hours,last_funding_rate\n")
        f.write("1704067200000,8,0.00010000\n")
        f.write("1704096000000,8,0.00010000\n")
        f.write("1704124800000,8,0.00010000\n")
    day = load_funding_daily(d, "XUSDT")
    assert abs(day["ann_mean"].iloc[0] - 0.0001 * 3 * 365) < 1e-9
    assert abs(day["day_sum"].iloc[0] - 0.0003) < 1e-12
    print("PASS loader_annualization")


if __name__ == "__main__":
    test_loader_annualization()
    test_short_collects_positive_funding()
    test_long_collects_negative_funding()
    test_below_threshold_stays_flat()
    test_funding_magnitude()
    test_no_lookahead()
    print("\nALL E7 MACHINERY TESTS PASS")
