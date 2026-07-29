"""test_risk_gates.py — machinery proof on SYNTHETIC data ONLY, matching
the test_term_structure.py/test_backtest.py convention: prove the shared
bootstrap/cap-diagnostic module is correct BEFORE anything real depends on
it. Real-data reproduction of every already-recorded hypothesis's exact
ruin-gate figure is a SEPARATE step (regression_risk_gates.py) — this file
only proves the function's own behavior on constructed cases.

No network, no real data. Exit code 0 iff all pass.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import risk_gates as rg

FAILS = []


def check(name, cond, detail=""):
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


# ---- bootstrap_p_ruin: compound (fractional-return) mode ----------------

def test_compound_zero_vol_never_ruins():
    r = np.zeros(500)
    p = rg.bootstrap_p_ruin(r, threshold=0.10, n_paths=200, seed=0, mode="compound")
    check("zero-vol series never breaches any positive threshold", p == 0.0, detail=f"p={p}")


def test_compound_guaranteed_ruin():
    # every resampled path is built from a series that is ALWAYS -50% —
    # cumprod hits threshold on step 1 of every single path.
    r = np.full(50, -0.50)
    p = rg.bootstrap_p_ruin(r, threshold=0.10, n_paths=200, seed=0, mode="compound")
    check("guaranteed-drawdown series ruins on every path", p == 1.0, detail=f"p={p}")


def test_compound_deterministic_same_seed():
    rng = np.random.default_rng(1)
    r = rng.normal(0.0005, 0.02, size=1000)
    p1 = rg.bootstrap_p_ruin(r, threshold=0.40, n_paths=500, seed=42, mode="compound")
    p2 = rg.bootstrap_p_ruin(r, threshold=0.40, n_paths=500, seed=42, mode="compound")
    check("same seed -> bit-identical result", p1 == p2, detail=f"{p1} vs {p2}")


def test_compound_different_seed_can_differ():
    rng = np.random.default_rng(2)
    r = rng.normal(0.0002, 0.03, size=300)
    p1 = rg.bootstrap_p_ruin(r, threshold=0.30, n_paths=1000, seed=7, mode="compound")
    p2 = rg.bootstrap_p_ruin(r, threshold=0.30, n_paths=1000, seed=0, mode="compound")
    # not a strict requirement that they MUST differ, but for a series with
    # real dispersion at moderate n_paths, bit-identical would indicate the
    # seed argument is silently ignored — that IS a bug worth catching.
    check("different seeds are not silently ignored", p1 != p2, detail=f"{p1} vs {p2}")


def test_compound_matches_manual_reference():
    # Hand-computable case: two possible returns, -0.5 and +1.0, equal
    # weight in the source array so resampling draws each ~50% of the
    # time. A single -0.5 draw alone is already a 50% drawdown, so ANY
    # path containing at least one -0.5 draw breaches a 0.40 threshold.
    # With n=20 draws per path, P(zero -0.5 draws) = 0.5**20 ≈ 9.5e-07 —
    # p_ruin should be effectively 1.0 at any reasonable n_paths.
    r = np.array([-0.5, 1.0])
    r = np.tile(r, 10)  # 20 values, balanced
    p = rg.bootstrap_p_ruin(r, threshold=0.40, n_paths=2000, seed=3, mode="compound")
    check("near-certain ruin case lands at 1.0", p == 1.0, detail=f"p={p}")


# ---- bootstrap_p_ruin: additive (dollar-PnL) mode ------------------------

def test_additive_zero_pnl_never_ruins():
    r = np.zeros(300)
    p = rg.bootstrap_p_ruin(r, threshold=100.0, n_paths=200, seed=0, mode="additive")
    check("zero-PnL series never breaches any positive dollar threshold", p == 0.0, detail=f"p={p}")


def test_additive_guaranteed_ruin():
    r = np.full(30, -500.0)
    p = rg.bootstrap_p_ruin(r, threshold=100.0, n_paths=200, seed=0, mode="additive")
    check("guaranteed-loss dollar series ruins on every path", p == 1.0, detail=f"p={p}")


def test_additive_vs_compound_are_different_mechanics():
    # Same numeric array interpreted two ways must NOT coincidentally
    # agree — sanity that the two code paths are actually distinct.
    rng = np.random.default_rng(5)
    r = rng.normal(10.0, 50.0, size=200)  # dollar-scale values
    p_add = rg.bootstrap_p_ruin(r, threshold=200.0, n_paths=500, seed=1, mode="additive")
    p_comp = rg.bootstrap_p_ruin(r, threshold=0.40, n_paths=500, seed=1, mode="compound")
    check("additive and compound modes are mechanically distinct",
          p_add != p_comp, detail=f"{p_add} vs {p_comp}")


# ---- shared behavior --------------------------------------------------

def test_empty_series_returns_one():
    p = rg.bootstrap_p_ruin(np.array([]), threshold=0.40, n_paths=100, seed=0, mode="compound")
    check("empty series -> p=1.0 (matches term_structure.bootstrap_p_maxdd guard)", p == 1.0)


def test_nan_values_dropped_not_fabricated():
    r_clean = np.array([0.01, -0.02, 0.015, -0.01] * 20)
    r_with_nan = np.concatenate([r_clean, [np.nan, np.nan]])
    p_clean = rg.bootstrap_p_ruin(r_clean, threshold=0.40, n_paths=300, seed=9, mode="compound")
    p_nan = rg.bootstrap_p_ruin(r_with_nan, threshold=0.40, n_paths=300, seed=9, mode="compound")
    check("NaNs are dropped, not treated as 0 or fabricated",
          p_clean == p_nan, detail=f"{p_clean} vs {p_nan}")


def test_invalid_mode_raises():
    raised = False
    try:
        rg.bootstrap_p_ruin(np.array([0.01, -0.01]), threshold=0.1, mode="bogus")
    except ValueError:
        raised = True
    check("unknown mode raises ValueError, does not silently default", raised)


def test_no_shared_rng_state_across_calls():
    # the bug class this replaces: a MODULE-LEVEL RNG object whose state
    # advances across calls, so a second call in the same process would
    # NOT reproduce the first call's result even with the "same" seed
    # semantics implied by reusing the object. Two independent calls with
    # the same explicit seed must agree regardless of call order/count.
    r = np.random.default_rng(11).normal(0, 0.02, 400)
    rg.bootstrap_p_ruin(r, threshold=0.3, n_paths=100, seed=4, mode="compound")  # burn one
    rg.bootstrap_p_ruin(r, threshold=0.3, n_paths=100, seed=4, mode="compound")  # burn another
    p_after_two_calls = rg.bootstrap_p_ruin(r, threshold=0.3, n_paths=100, seed=4, mode="compound")
    p_fresh = rg.bootstrap_p_ruin(r, threshold=0.3, n_paths=100, seed=4, mode="compound")
    check("no cross-call RNG drift (unlike the module-level-RNG bug class it replaces)",
          p_after_two_calls == p_fresh, detail=f"{p_after_two_calls} vs {p_fresh}")


# ---- cap_binding_report -------------------------------------------------

def test_cap_report_flags_e12_shaped_case():
    # Constructed to mirror E12's actual audit numbers: cap binds ~97% of
    # days, realized vol is far below (~49% of) the 15% target.
    n = 1000
    binding = pd.Series([True] * 966 + [False] * 34)
    rng = np.random.default_rng(20)
    # std needed for ~7.4% annualized vol at ann=252: sigma = 0.074/sqrt(252)
    sigma = 0.074 / np.sqrt(252.0)
    returns = pd.Series(rng.normal(0.0, sigma, n))
    res = rg.cap_binding_report(binding, returns, target_ann_vol=0.15)
    check("E12-shaped case: binding_frac > 0.50", res["binding_frac"] > 0.50,
          detail=str(res))
    check("E12-shaped case: vol_ratio < 0.85", res["vol_ratio"] < 0.85, detail=str(res))
    check("E12-shaped case: artifact_risk flagged True", res["artifact_risk"] is True,
          detail=str(res))


def test_cap_report_clean_e9_shaped_case():
    # Mirrors E9's actual audit: cap binds ~33% of days, realized vol
    # lands essentially AT the 15% target -- neither condition alone
    # should be enough to flag it.
    n = 1000
    binding = pd.Series([True] * 330 + [False] * 670)
    rng = np.random.default_rng(21)
    sigma = 0.145 / np.sqrt(252.0)  # ~14.5% annualized, matches E9's audit
    returns = pd.Series(rng.normal(0.0, sigma, n))
    res = rg.cap_binding_report(binding, returns, target_ann_vol=0.15)
    check("E9-shaped case: binding_frac NOT flagged (below 0.50 threshold... "
          "actually 0.33, so this checks the LOW-binding non-trigger path)",
          res["binding_frac"] < 0.50, detail=str(res))
    check("E9-shaped case: artifact_risk correctly False", res["artifact_risk"] is False,
          detail=str(res))


def test_cap_report_requires_both_conditions_high_binding_ok_vol():
    # High binding fraction ALONE (e.g. 90%) must NOT trigger the flag if
    # realized vol still lands near target -- a cap can bind constantly
    # and still be harmless if it's binding at a level that matches the
    # registered target, not suppressing it.
    n = 1000
    binding = pd.Series([True] * 900 + [False] * 100)
    rng = np.random.default_rng(22)
    sigma = 0.15 / np.sqrt(252.0)  # exactly at target
    returns = pd.Series(rng.normal(0.0, sigma, n))
    res = rg.cap_binding_report(binding, returns, target_ann_vol=0.15)
    check("high binding_frac with on-target vol does NOT flag artifact_risk",
          res["artifact_risk"] is False, detail=str(res))


def test_cap_report_requires_both_conditions_low_binding_low_vol():
    # Low binding fraction with low vol ratio (e.g. vol shortfall caused
    # by something OTHER than the cap) must also NOT trigger the flag --
    # the flag specifically means "the cap looks like the cause".
    n = 1000
    binding = pd.Series([True] * 100 + [False] * 900)
    rng = np.random.default_rng(23)
    sigma = 0.05 / np.sqrt(252.0)  # well under target, but cap rarely binds
    returns = pd.Series(rng.normal(0.0, sigma, n))
    res = rg.cap_binding_report(binding, returns, target_ann_vol=0.15)
    check("low binding_frac with low vol does NOT flag artifact_risk "
          "(cap isn't the cause if it rarely binds)",
          res["artifact_risk"] is False, detail=str(res))


def test_cap_report_realized_vol_matches_known_construction():
    n = 5000
    sigma_daily = 0.10 / np.sqrt(252.0)
    rng = np.random.default_rng(24)
    returns = pd.Series(rng.normal(0.0, sigma_daily, n))
    binding = pd.Series([False] * n)
    res = rg.cap_binding_report(binding, returns, target_ann_vol=0.15)
    check("realized_vol recovers the constructed ~10% annualized vol",
          abs(res["realized_vol"] - 0.10) < 0.01,
          detail=f"realized_vol={res['realized_vol']:.4f}")
    check("binding_frac is exactly 0.0 for an all-False series",
          res["binding_frac"] == 0.0)


# ---- single_asset_cap_diagnostic (Style B: E4-v2/E17-v2 leverage ceiling) --

def test_single_asset_high_vol_ceiling_rarely_binds():
    # A BTC-shaped asset (vol >> 15% target) should almost NEVER hit the
    # 1x ceiling -- the vol-target formula scales DOWN, not up, so the
    # ceiling isn't the active constraint. Mirrors the real E4-v2 finding.
    rng = np.random.default_rng(30)
    sigma_daily = 0.65 / np.sqrt(365.0)  # ~65% annualized, BTC-shaped
    r = rng.normal(0.0002, sigma_daily, 800)
    price = 100.0 * np.cumprod(1.0 + r)
    res = rg.single_asset_cap_diagnostic(price, vol_win=30, vol_target=0.15, ann=365.0)
    check("high-vol asset: ceiling binds on a small minority of days",
          res["binding_frac"] < 0.10, detail=str(res))
    check("high-vol asset: not flagged as artifact risk",
          res["artifact_risk"] is False, detail=str(res))


def test_single_asset_low_vol_ceiling_binds_often():
    # A calm asset (vol << 15% target) should hit the ceiling MOST days --
    # the vol-target formula wants to lever UP past 1x and can't.
    rng = np.random.default_rng(31)
    sigma_daily = 0.03 / np.sqrt(365.0)  # ~3% annualized, very calm
    r = rng.normal(0.0, sigma_daily, 800)
    price = 100.0 * np.cumprod(1.0 + r)
    res = rg.single_asset_cap_diagnostic(price, vol_win=30, vol_target=0.15, ann=365.0)
    check("low-vol asset: ceiling binds on most days",
          res["binding_frac"] > 0.70, detail=str(res))


def test_single_asset_no_lookahead_truncation():
    # w_tgt at day t must only ever depend on prices through day t. Proven
    # the way test_term_structure.py proves the same property for its own
    # vol target: a spike appended AFTER a cutoff must not change the
    # per-date multiplier computed AT OR BEFORE that cutoff. Reconstructs
    # the same 3-line w_tgt computation single_asset_cap_diagnostic uses
    # internally (acceptable duplication in a test, unlike in production
    # code) so the per-date series -- not just the aggregate report -- can
    # be compared directly.
    def w_tgt_series(price, vol_win=30, vol_target=0.15, ann=365.0):
        c = np.asarray(price, dtype=float)
        r = np.zeros(len(c))
        r[1:] = c[1:] / c[:-1] - 1.0
        r_s = pd.Series(r)
        vol = r_s.rolling(vol_win).std() * np.sqrt(ann)
        return np.minimum(1.0, vol_target / vol.replace(0, np.nan)).fillna(0.0)

    rng = np.random.default_rng(32)
    sigma_daily = 0.20 / np.sqrt(365.0)
    r_calm = rng.normal(0.0, sigma_daily, 400)
    price_prefix = 100.0 * np.cumprod(1.0 + r_calm)
    # Append a violent spike AFTER the prefix -- if the rolling window
    # were somehow centered or forward-looking, this would change w_tgt
    # values near the end of the prefix.
    spike = price_prefix[-1] * np.array([1.0, 2.5, 0.4, 1.0, 1.0])
    price_extended = np.concatenate([price_prefix, spike])

    w_prefix = w_tgt_series(price_prefix)
    w_extended = w_tgt_series(price_extended)
    overlap_matches = np.allclose(w_prefix.values, w_extended.values[:len(w_prefix)])
    check("late spike does not alter earlier w_tgt values (no lookahead)",
          overlap_matches)


def main():
    for t in (test_compound_zero_vol_never_ruins, test_compound_guaranteed_ruin,
              test_compound_deterministic_same_seed,
              test_compound_different_seed_can_differ,
              test_compound_matches_manual_reference,
              test_additive_zero_pnl_never_ruins, test_additive_guaranteed_ruin,
              test_additive_vs_compound_are_different_mechanics,
              test_empty_series_returns_one, test_nan_values_dropped_not_fabricated,
              test_invalid_mode_raises, test_no_shared_rng_state_across_calls,
              test_cap_report_flags_e12_shaped_case,
              test_cap_report_clean_e9_shaped_case,
              test_cap_report_requires_both_conditions_high_binding_ok_vol,
              test_cap_report_requires_both_conditions_low_binding_low_vol,
              test_cap_report_realized_vol_matches_known_construction,
              test_single_asset_high_vol_ceiling_rarely_binds,
              test_single_asset_low_vol_ceiling_binds_often,
              test_single_asset_no_lookahead_truncation):
        print(f"\n{t.__name__}:")
        t()
    print("\n" + "=" * 52)
    if FAILS:
        print(f"MACHINERY TESTS: {len(FAILS)} FAILED -> {FAILS}")
        sys.exit(1)
    print("MACHINERY TESTS: ALL PASS")


if __name__ == "__main__":
    main()
