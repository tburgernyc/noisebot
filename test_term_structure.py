"""test_term_structure.py — machinery proof on SYNTHETIC data ONLY.

Runs BEFORE any registered window is evaluated (E7/E8 precedent). Proves
the invariants that make the E9/E11/E12 backtest honest:
  1  outright vs spread discrimination
  2  single-digit-year decode by next-occurrence
  3  front/second selection excludes the delivery month
  4  NO-SPLICE: a roll-day return never uses a cross-contract price jump
  5  NO-LOOKAHEAD: basis-momentum at t is invariant to truncation at >= t
  6  basis-momentum sign
  7  FX carry sign
  8  cross-sectional weights are dollar-neutral, gross 1.0/side
  9  vol targeting is no-lookahead (spike at end cannot change earlier mult)
 10  episode extraction counts constant-sign runs

No network, no real data. Exit code 0 iff all pass.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import term_structure as ts

FAILS = []


def check(name, cond, detail=""):
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def bdays(start, periods):
    return pd.bdate_range(start=start, periods=periods)


# ---- 1. outright vs spread ------------------------------------------
def test_outright():
    check("outright CLN0", ts.is_outright("CLN0", "CL"))
    check("outright 6EF5", ts.is_outright("6EF5", "6E"))
    check("reject butterfly", not ts.is_outright("CL:BF F0-G0-H0", "CL"))
    check("reject calendar", not ts.is_outright("6EU0-6EM0", "6E"))
    check("reject foreign root", not ts.is_outright("NGF0", "CL"))
    check("reject 2-digit tail", not ts.is_outright("CLN00", "CL"))


# ---- 2. decode next-occurrence --------------------------------------
def test_decode():
    # CLN0 observed 2010-06 -> July 2010 (nearest N with digit 0 >= obs)
    check("CLN0@2010-06 -> 2010-07",
          ts.decode_expiry_ym("CLN0", "CL", 2010, 6) == ts.ym_key(2010, 7))
    # CLZ1 observed 2010-06 -> Dec 2011
    check("CLZ1@2010-06 -> 2011-12",
          ts.decode_expiry_ym("CLZ1", "CL", 2010, 6) == ts.ym_key(2011, 12))
    # CLF0 observed 2010-06 -> Jan 2020 (Jan 2010 already passed)
    check("CLF0@2010-06 -> 2020-01",
          ts.decode_expiry_ym("CLF0", "CL", 2010, 6) == ts.ym_key(2020, 1))
    # a 2026 contract: CLN6 observed 2026-03 -> July 2026
    check("CLN6@2026-03 -> 2026-07",
          ts.decode_expiry_ym("CLN6", "CL", 2026, 3) == ts.ym_key(2026, 7))


# ---- 3. front/second excludes delivery month ------------------------
def test_select():
    exp = {"A": ts.ym_key(2020, 2), "B": ts.ym_key(2020, 3),
           "C": ts.ym_key(2020, 4)}
    # observed January -> front Feb(A), second Mar(B)
    f, s = ts.select_front_second(exp, ts.ym_key(2020, 1))
    check("Jan -> front A/second B", f == "A" and s == "B")
    # observed February -> Feb is delivery, excluded -> front Mar(B)
    f, s = ts.select_front_second(exp, ts.ym_key(2020, 2))
    check("Feb -> delivery excluded, front B/second C", f == "B" and s == "C")


# ---- 4. no-splice roll ----------------------------------------------
def _panel_two_contracts():
    """A ~100 (front in Jan), B ~50 (second in Jan, front in Feb). A splice
    at the Feb roll would fabricate a ~-50% return; no-splice must not."""
    jan = bdays("2020-01-01", 22)
    feb = bdays("2020-02-03", 20)
    rows = []
    rng = np.random.default_rng(1)
    for d in list(jan) + list(feb):
        # A trades Jan and into early Feb, ~100
        rows.append((d, "A", 100 + rng.normal(0, 0.2), ts.ym_key(2020, 2)))
        # B trades throughout, ~50
        rows.append((d, "B", 50 + rng.normal(0, 0.1), ts.ym_key(2020, 3)))
    return pd.DataFrame(rows, columns=["date", "symbol", "close", "expiry_ym"])


def test_no_splice():
    panel = _panel_two_contracts()
    r = ts.nearby_return_series(panel, "front")
    check("no fabricated roll jump (all |ret|<0.10)", (r.abs() < 0.10).all(),
          detail=f"max|ret|={r.abs().max():.3f}")
    # explicitly: the first Feb business day return is B/B, ~0, not ~-0.5
    feb1 = pd.Timestamp("2020-02-03")
    if feb1 in r.index:
        check("roll-day return is within-contract small", abs(r.loc[feb1]) < 0.05,
              detail=f"roll ret={r.loc[feb1]:.3f}")
    else:
        check("roll-day priced", False, "feb1 missing")


# ---- 5. no-lookahead (truncation invariance) ------------------------
def _panel_trend(front_slope, second_slope, n_months=15):
    """One root, monthly contracts, front rises at front_slope/day, second
    at second_slope/day, so basis-momentum sign is controllable."""
    dates = bdays("2020-01-01", n_months * 21)
    rows = []
    base_f, base_s = 100.0, 100.0
    for i, d in enumerate(dates):
        obs = ts.ym_key(d.year, d.month)
        # front = obs+1 month, second = obs+2 (monthly contracts present)
        rows.append((d, f"F{obs+1}", base_f + front_slope * i, obs + 1))
        rows.append((d, f"S{obs+2}", base_s + second_slope * i, obs + 2))
    return pd.DataFrame(rows, columns=["date", "symbol", "close", "expiry_ym"])


def _bm_from_panel(panel, lb=6):
    fr = ts.monthly_returns(ts.nearby_return_series(panel, "front"))
    sr = ts.monthly_returns(ts.nearby_return_series(panel, "second"))
    return ts.basis_momentum(fr, sr, lb)


def test_no_lookahead():
    panel = _panel_trend(0.15, 0.02)
    full = _bm_from_panel(panel)
    if len(full) < 3:
        check("enough BM points", False, f"n={len(full)}")
        return
    cut = full.index[-2]                      # truncate at a past month-end
    trunc_panel = panel[panel["date"] <= cut]
    trunc = _bm_from_panel(trunc_panel)
    common = full.index.intersection(trunc.index)
    diff = (full.loc[common] - trunc.loc[common]).abs().max()
    check("BM at t invariant to future truncation", diff < 1e-9,
          detail=f"maxdiff={diff:.2e}")


# ---- 6. basis-momentum sign -----------------------------------------
def test_bm_sign():
    up = _bm_from_panel(_panel_trend(0.20, 0.01))     # front >> second mom
    dn = _bm_from_panel(_panel_trend(0.01, 0.20))     # second >> front mom
    check("BM positive when front out-trends second", up.dropna().iloc[-1] > 0,
          detail=f"{up.dropna().iloc[-1]:.4f}")
    check("BM negative when second out-trends front", dn.dropna().iloc[-1] < 0,
          detail=f"{dn.dropna().iloc[-1]:.4f}")


# ---- 7. FX carry sign -----------------------------------------------
def test_carry_sign():
    idx = pd.bdate_range("2020-01-31", periods=3, freq="ME")
    front = pd.Series([1.10, 1.10, 1.10], index=idx)     # front > second
    second = pd.Series([1.09, 1.09, 1.09], index=idx)    # forward discount
    dt = pd.Series([0.25, 0.25, 0.25], index=idx)
    c = ts.fx_carry(front, second, dt)
    check("forward discount -> positive carry", (c > 0).all(),
          detail=f"{c.iloc[-1]:.4f}")
    c2 = ts.fx_carry(second, front, dt)                  # forward premium
    check("forward premium -> negative carry", (c2 < 0).all())


# ---- 8. cross-sectional neutrality ----------------------------------
def test_xsection():
    idx = pd.bdate_range("2020-01-31", periods=2, freq="ME")
    roots = list("ABCDEF")
    sig = pd.DataFrame([[6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6]],
                       index=idx, columns=roots, dtype=float)
    w = ts.cross_sectional_ls(sig, 2, 2, tercile=True)
    row = w.iloc[0]
    check("dollar-neutral (sum~0)", abs(row.sum()) < 1e-9)
    check("gross long = 1.0", abs(row[row > 0].sum() - 1.0) < 1e-9)
    check("gross short = 1.0", abs(row[row < 0].sum() + 1.0) < 1e-9)
    check("top root A is long", row["A"] > 0 and w.iloc[1]["F"] > 0)


# ---- 9. vol targeting no-lookahead ----------------------------------
def test_vol_target_nolook():
    rng = np.random.default_rng(2)
    idx = pd.bdate_range("2020-01-01", periods=200)
    base = pd.Series(rng.normal(0, 0.01, 200), index=idx)
    spiked = base.copy()
    spiked.iloc[-1] = 0.5                         # huge return on the LAST day
    m_base = ts.vol_target_scale(base)
    m_spk = ts.vol_target_scale(spiked)
    # multipliers on all dates EXCEPT the last must be identical
    d = (m_base.iloc[:-1] - m_spk.iloc[:-1]).abs().max()
    check("end-spike cannot change earlier leverage", d < 1e-12,
          detail=f"maxdiff={d:.2e}")


# ---- 10. episodes ----------------------------------------------------
def test_episodes():
    idx = pd.bdate_range("2020-01-01", periods=6)
    w = pd.DataFrame({"X": [0.5, 0.5, 0.5, 0.0, -0.5, -0.5]}, index=idx)
    eps = ts.extract_episodes(w)
    check("two episodes from +run then -run", len(eps) == 2,
          detail=f"n={len(eps)}")
    check("sides are +1 then -1",
          len(eps) == 2 and eps[0]["side"] == 1 and eps[1]["side"] == -1)


# ---- 11. non-positive-price guard (Apr-2020 negative-WTI analog) -----
def test_neg_price_guard():
    dates = bdays("2020-01-01", 15)
    rows = []
    for i, d in enumerate(dates):
        px = -5.0 if i == 7 else 100.0 + i * 0.1
        rows.append((d, "A", px, ts.ym_key(2020, 2)))   # A is front all Jan
    panel = pd.DataFrame(rows, columns=["date", "symbol", "close", "expiry_ym"])
    r = ts.nearby_return_series(panel, "front")
    d7, d8 = dates[7], dates[8]
    check("return INTO negative-price day excluded", d7 not in r.index)
    check("return OUT OF negative-price day excluded", d8 not in r.index)
    check("all surviving returns finite & sane", (r.abs() < 0.10).all(),
          detail=f"max|ret|={r.abs().max():.3f}")


def main():
    for t in (test_outright, test_decode, test_select, test_no_splice,
              test_no_lookahead, test_bm_sign, test_carry_sign,
              test_xsection, test_vol_target_nolook, test_episodes,
              test_neg_price_guard):
        print(f"\n{t.__name__}:")
        t()
    print("\n" + "=" * 52)
    if FAILS:
        print(f"MACHINERY TESTS: {len(FAILS)} FAILED -> {FAILS}")
        sys.exit(1)
    print("MACHINERY TESTS: ALL PASS")


if __name__ == "__main__":
    main()
