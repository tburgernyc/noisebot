"""Unit tests for load_databento_parquet(). Synthetic 1m data with
hand-computed expected 5m aggregates, both Databento parquet flavors.
Run: python3 test_loader.py
"""
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from noise_area import NY, load_databento_parquet

TMP = Path(tempfile.mkdtemp())


def _mk_1m() -> pd.DataFrame:
    """10 one-minute bars 09:30-09:39 NY on a known date, deterministic."""
    idx = pd.date_range("2026-07-06 09:30", periods=10, freq="1min",
                        tz=NY)
    opens = np.array([100., 101, 102, 103, 104, 105, 106, 107, 108, 109])
    return pd.DataFrame({
        "open": opens, "high": opens + 2.0, "low": opens - 1.0,
        "close": opens + 1.0, "volume": np.full(10, 10.0),
    }, index=idx)


def _expected_5m(df1: pd.DataFrame) -> pd.DataFrame:
    """Hand-rolled expectation: bar 09:30 aggregates 09:30..09:34."""
    rows = {}
    for start in ("09:30", "09:35"):
        g = df1.between_time(start, start[:3] + str(int(start[3:]) + 4))
        rows[g.index[0].replace(second=0)] = {
            "open": g["open"].iloc[0], "high": g["high"].max(),
            "low": g["low"].min(), "close": g["close"].iloc[-1],
            "volume": g["volume"].sum()}
    return pd.DataFrame(rows).T


def test_float_flavor_index():
    """to_df().to_parquet(): float prices, tz-aware UTC DatetimeIndex."""
    df1 = _mk_1m()
    flav = df1.copy()
    flav.index = flav.index.tz_convert("UTC")
    flav.index.name = "ts_event"
    flav["symbol"] = "MNQ.v.0"
    p = TMP / "float_idx.parquet"
    flav.to_parquet(p)
    out = load_databento_parquet(str(p))
    exp = _expected_5m(df1)
    assert str(out.index.tz) == "America/New_York", out.index.tz
    assert list(out.columns) == ["open", "high", "low", "close", "volume"]
    assert len(out) == 2, f"expected 2 five-min bars, got {len(out)}"
    assert (out.index.minute % 5 == 0).all(), "bars not on 5-min boundaries"
    for col in exp.columns:
        assert np.allclose(out[col].values, exp[col].values.astype(float)), \
            f"{col}: {out[col].values} != {exp[col].values}"
    print("PASS float_flavor_index")


def test_fixedpoint_flavor_column():
    """DBNStore.to_parquet(): int64 1e-9 prices, ts_event as int column."""
    df1 = _mk_1m()
    ns = df1.index.tz_convert("UTC").as_unit("ns").asi8  # true int64 ns epoch
    flav = pd.DataFrame({
        "ts_event": ns,
        "rtype": 32, "instrument_id": 12345,
        "open": (df1["open"] * 1e9).astype("int64"),
        "high": (df1["high"] * 1e9).astype("int64"),
        "low": (df1["low"] * 1e9).astype("int64"),
        "close": (df1["close"] * 1e9).astype("int64"),
        "volume": df1["volume"].astype("int64"),
        "symbol": "MNQ.v.0",
    })
    p = TMP / "fixed_col.parquet"
    flav.to_parquet(p, index=False)
    out = load_databento_parquet(str(p))
    exp = _expected_5m(df1)
    assert str(out.index.tz) == "America/New_York"
    assert len(out) == 2
    for col in exp.columns:
        assert np.allclose(out[col].values, exp[col].values.astype(float)), \
            f"{col}: {out[col].values} != {exp[col].values}"
    # first 5m bar must be labeled 09:30 NY exactly
    assert out.index[0] == pd.Timestamp("2026-07-06 09:30", tz=NY)
    print("PASS fixedpoint_flavor_column")


def test_us_epoch_detected():
    """Integer epochs in microseconds must be detected, not read as ns."""
    df1 = _mk_1m()
    us = df1.index.tz_convert("UTC").as_unit("us").asi8
    flav = pd.DataFrame({"ts_event": us,
                         "open": df1["open"].values,
                         "high": df1["high"].values,
                         "low": df1["low"].values,
                         "close": df1["close"].values,
                         "volume": df1["volume"].values})
    p = TMP / "us_epoch.parquet"
    flav.to_parquet(p, index=False)
    out = load_databento_parquet(str(p))
    assert out.index[0] == pd.Timestamp("2026-07-06 09:30", tz=NY), out.index[0]
    print("PASS us_epoch_detected")


def test_multi_symbol_refused():
    df1 = _mk_1m()
    flav = df1.copy()
    flav.index = flav.index.tz_convert("UTC")
    flav["symbol"] = ["MNQU6"] * 5 + ["MNQZ6"] * 5
    p = TMP / "multi.parquet"
    flav.to_parquet(p)
    try:
        load_databento_parquet(str(p))
    except ValueError as e:
        assert "multiple symbols" in str(e)
        print("PASS multi_symbol_refused")
        return
    raise AssertionError("multi-symbol file was not refused")


def test_gap_bars_dropped():
    """Empty 5-min buckets (e.g. maintenance halt) must not emit bars."""
    df1 = _mk_1m()
    df1 = df1.drop(df1.index[5:])  # keep only 09:30-09:34
    flav = df1.copy()
    flav.index = flav.index.tz_convert("UTC")
    p = TMP / "gap.parquet"
    flav.to_parquet(p)
    out = load_databento_parquet(str(p))
    assert len(out) == 1 and out.index[0].strftime("%H:%M") == "09:30"
    print("PASS gap_bars_dropped")


if __name__ == "__main__":
    test_float_flavor_index()
    test_fixedpoint_flavor_column()
    test_us_epoch_detected()
    test_multi_symbol_refused()
    test_gap_bars_dropped()
    print("\nALL LOADER TESTS PASS")
