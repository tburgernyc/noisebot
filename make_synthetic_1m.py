"""Build a synthetic Databento-flavor ohlcv-1m parquet from Yahoo 5m bars,
constructed so 1m -> 5m re-aggregation is EXACT (open/high/low/close/volume).
Used only to prove loader+runner equivalence in the container dry run.
Run: python3 make_synthetic_1m.py data/nq_5m.json data/synth_1m.parquet
"""
import sys

import numpy as np
import pandas as pd

from noise_area import load_yahoo_json


def main(src: str, dst: str) -> None:
    df5 = load_yahoo_json(src)
    rows = []
    for ts, r in df5.iterrows():
        o, h, l, c = r["open"], r["high"], r["low"], r["close"]
        v = int(r["volume"])
        q, rem = divmod(v, 5)
        vols = [q + rem, q, q, q, q]
        for k in range(5):
            rows.append({
                "ts_event": (ts + pd.Timedelta(minutes=k))
                .tz_convert("UTC").as_unit("ns").value,
                "rtype": 32, "instrument_id": 1,
                "open": int(round((o if k == 0 else c) * 1e9)),
                "high": int(round(h * 1e9)),
                "low": int(round(l * 1e9)),
                "close": int(round(c * 1e9)),
                "volume": vols[k], "symbol": "MNQ.v.0",
            })
    out = pd.DataFrame(rows)
    out.to_parquet(dst, index=False)
    print(f"wrote {len(out):,} synthetic 1m rows -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
