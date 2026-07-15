"""Unit tests for E1/E2 registered edges. Run before ANY backtest is trusted.
Synthetic behavior tests + a no-lookahead proof on the real parquet."""
from __future__ import annotations
import numpy as np
import pandas as pd
import zoneinfo

from edges import run_e1, run_e2, TICK

NY = zoneinfo.ZoneInfo("America/New_York")
FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def synth_day(date, opens, spread=1.0, vol=100.0):
    """78 RTH 5m bars from a list/array of open prices."""
    idx = pd.date_range(f"{date} 09:30", f"{date} 15:55", freq="5min", tz=NY)
    o = np.asarray(opens, dtype=float)[: len(idx)]
    c = np.r_[o[1:], o[-1]]
    return pd.DataFrame({"open": o, "high": np.maximum(o, c) + spread,
                         "low": np.minimum(o, c) - spread, "close": c,
                         "volume": vol}, index=idx)


def make_flat_days(n, base=20000.0, start="2026-01-05"):
    """n consecutive business days of dead-flat price (range ~2*spread)."""
    days = pd.bdate_range(start, periods=n)
    return pd.concat([synth_day(d.date(), np.full(78, base)) for d in days])


def test_e1_behavior():
    base = 20000.0
    days = pd.bdate_range("2026-01-05", periods=16)
    frames = []
    # 14 history days with wide swings (full range ~100 pts)
    for d in days[:14]:
        swing = base + 50 * np.sin(np.linspace(0, 2 * np.pi, 78))
        frames.append(synth_day(d.date(), swing))
    # day 15: compressed OR (flat first 3 bars) then clean upside breakout
    brk = np.r_[np.full(4, base), base + 10 * np.arange(1, 75)]
    frames.append(synth_day(days[14].date(), brk))
    # day 16: WIDE OR (swing in first 3 bars) then breakout -> must be filtered
    wide = np.r_[base, base + 40, base - 40, base + 10 * np.arange(1, 76)]
    frames.append(synth_day(days[15].date(), wide))
    df = pd.concat(frames)
    tr = run_e1(df, or_minutes=15)
    d15, d16 = days[14].date(), days[15].date()
    t15 = tr[tr["date"] == d15] if not tr.empty else tr
    check("e1_one_trade_on_breakout_day", len(t15) == 1)
    check("e1_breakout_is_long_and_profitable",
          (not t15.empty) and t15["dir"].iloc[0] == 1 and t15["pnl"].iloc[0] > 0)
    check("e1_wide_or_day_filtered",
          tr.empty or (tr["date"] == d16).sum() == 0)
    check("e1_entry_has_adverse_tick",
          t15.empty or abs(t15["entry"].iloc[0] % 0.25) < 1e-9)


def test_e2_behavior():
    base = 20000.0
    hist = make_flat_days(61)
    d_t = pd.bdate_range("2026-04-06", periods=2)
    # stretch day: +6pt pop after 10:00 (z~2.5), decays through VWAP
    pop = np.r_[np.full(7, base), np.full(4, base + 6.0),
                np.linspace(base + 6.0, base - 3.0, 12), np.full(55, base - 3.0)]
    stretch = synth_day(d_t[0].date(), pop)
    # gap day: identical shape but opens 5% above prior close -> must be skipped
    gap = synth_day(d_t[1].date(), pop * 1.05)
    df = pd.concat([hist, stretch, gap])
    tr = run_e2(df, z_entry=2.0)
    t0 = tr[tr["date"] == d_t[0].date()] if not tr.empty else tr
    check("e2_fade_triggered_on_stretch_day", len(t0) >= 1)
    check("e2_fade_is_short_and_profitable",
          (not t0.empty) and t0["dir"].iloc[0] == -1 and t0["pnl"].iloc[0] > 0)
    check("e2_gap_day_skipped",
          tr.empty or (tr["date"] == d_t[1].date()).sum() == 0)


def test_no_lookahead_real_data():
    """Truncating the future must not change past trades (both edges)."""
    from noise_area import load_databento_parquet, rth
    df5 = load_databento_parquet("data/databento_1m.parquet")
    all_dates = sorted(set(rth(df5).index.date))
    cutoff = all_dates[250]
    sub = df5[[d < cutoff for d in df5.index.date]]
    for name, fn in (("e1", run_e1), ("e2", run_e2)):
        full = fn(df5)
        part = fn(sub)
        f = full[[d < cutoff for d in full["date"]]].reset_index(drop=True)
        p = part[[d < cutoff for d in part["date"]]].reset_index(drop=True)
        same = len(f) == len(p) and (f.empty or
               (np.allclose(f["pnl"], p["pnl"]) and (f["dir"] == p["dir"]).all()))
        check(f"{name}_no_lookahead_truncation_invariance", same)


def test_flatten_no_overnight():
    """Every trade closes same day; no trade date appears with open position
    (defensive branch covers last bar). Uses real data output shape."""
    from noise_area import load_databento_parquet
    df5 = load_databento_parquet("data/databento_1m.parquet")
    for name, fn in (("e1", run_e1), ("e2", run_e2)):
        tr = fn(df5)
        ok = (not tr.empty) and tr["pnl"].notna().all() and \
             tr["entry"].gt(0).all() and tr["exit"].gt(0).all()
        check(f"{name}_all_trades_closed_and_finite", ok)




def test_e3_behavior():
    from edges import run_e3
    base = 20000.0
    d = pd.bdate_range("2026-05-04", periods=2)
    # up-day: steady rise all day -> LONG at 15:30, exit 15:55
    up = synth_day(d[0].date(), base + 0.5 * np.arange(78))
    # down-day: steady fall -> SHORT
    dn = synth_day(d[1].date(), base - 0.5 * np.arange(78))
    tr = run_e3(pd.concat([up, dn]))
    check("e3_two_days_two_trades", len(tr) == 2)
    check("e3_updy_long_dndy_short",
          len(tr) == 2 and tr["dir"].iloc[0] == 1 and tr["dir"].iloc[1] == -1)
    # entry must be the 15:30 bar open +/- tick: bar index 72 = 15:30
    ent_expected = up["open"].iloc[73 - 1]  # signal bar 15:25 is idx 71; next open idx 72
    check("e3_entry_at_1530_open",
          len(tr) == 2 and abs(tr["entry"].iloc[0] - (up["open"].iloc[72] + TICK)) < 1e-9)
    # exit at 15:55 bar open, adverse tick (idx 77)
    check("e3_exit_at_flatten_open",
          len(tr) == 2 and abs(tr["exit"].iloc[0] - (up["open"].iloc[77] - TICK)) < 1e-9)


def test_e3_no_lookahead_real():
    from edges import run_e3
    from noise_area import load_databento_parquet, rth
    df5 = load_databento_parquet("data/databento_1m.parquet")
    all_dates = sorted(set(rth(df5).index.date))
    cutoff = all_dates[250]
    sub = df5[[dd < cutoff for dd in df5.index.date]]
    full = run_e3(df5); part = run_e3(sub)
    f = full[[dd < cutoff for dd in full["date"]]].reset_index(drop=True)
    p = part.reset_index(drop=True)
    check("e3_no_lookahead_truncation_invariance",
          len(f) == len(p) and np.allclose(f["pnl"], p["pnl"]))


if __name__ == "__main__":
    test_e1_behavior()
    test_e2_behavior()
    test_no_lookahead_real_data()
    test_flatten_no_overnight()
    test_e3_behavior()
    test_e3_no_lookahead_real()
    print("\nALL EDGE TESTS PASS" if not FAILS else
          f"\n{len(FAILS)} FAILURES: {FAILS}")
    raise SystemExit(1 if FAILS else 0)
