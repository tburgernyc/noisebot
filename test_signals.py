"""Phase 3 unit tests. Run before any execution scaffold is trusted.

Default data source: data/nq_5m.json (Yahoo). Set NOISE_DATA_PARQUET to a
Databento ohlcv-1m parquet path to run the identical suite on the new loader.
"""
import os

import numpy as np
import pandas as pd

from noise_area import (NY, build_days, load_databento_parquet,
                        load_yahoo_json, rth, signal_for_bar)

_PARQ = os.environ.get("NOISE_DATA_PARQUET")
if _PARQ:
    print(f"data source: databento parquet ({_PARQ})")
    df5 = load_databento_parquet(_PARQ)
else:
    print("data source: yahoo json (data/nq_5m.json)")
    df5 = load_yahoo_json("data/nq_5m.json")
days = build_days(df5, lookback=14)
assert days, "no days built"


def test_signal_domain():
    seen = set()
    for day in days[:10]:
        pos = 0
        for i in range(len(day.bars)):
            s = signal_for_bar(day, i, pos)
            assert s in ("LONG", "SHORT", "EXIT", "HOLD"), f"bad signal {s}"
            seen.add(s)
            if s == "LONG":
                pos = 1
            elif s == "SHORT":
                pos = -1
            elif s == "EXIT":
                pos = 0
    assert "HOLD" in seen
    print("PASS signal_domain (values seen:", sorted(seen), ")")


def test_no_lookahead():
    """Perturb FUTURE days' prices; bands for an earlier day must not change."""
    k = len(days) // 2
    target_date = days[k].date
    cut = df5[df5.index.date <= target_date]
    fut = df5[df5.index.date > target_date] * 1.5   # corrupt the future
    days_alt = build_days(pd.concat([cut, fut]), lookback=14)
    a = next(d for d in days if d.date == target_date)
    b = next(d for d in days_alt if d.date == target_date)
    assert np.allclose(a.upper.values, b.upper.values), "lookahead in bands!"
    assert np.allclose(a.lower.values, b.lower.values), "lookahead in bands!"
    print("PASS no_lookahead")


def test_flatten_enforced():
    day = days[0]
    late = [i for i, ts in enumerate(day.bars.index)
            if ts.strftime("%H:%M") >= "15:55"]
    if late:
        assert signal_for_bar(day, late[0], 1) == "EXIT"
        assert signal_for_bar(day, late[0], -1) == "EXIT"
        assert signal_for_bar(day, late[0], 0) == "HOLD"
    print("PASS flatten_enforced")


def test_bands_sane():
    for day in days:
        assert (day.upper.values >= day.lower.values).all()
        assert day.upper.isna().sum() == 0 and day.lower.isna().sum() == 0
    print("PASS bands_sane")


def test_empty_data():
    try:
        build_days(df5.iloc[:0], lookback=14)
        print("PASS empty_data (returned without crash)")
    except Exception as e:  # noqa: BLE001
        raise AssertionError(f"empty data crashed: {e}") from e


if __name__ == "__main__":
    test_signal_domain()
    test_no_lookahead()
    test_flatten_enforced()
    test_bands_sane()
    test_empty_data()
    print("\nALL TESTS PASS")
