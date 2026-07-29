"""risk_gates.py — shared, family-agnostic ruin-probability bootstrap and
cap-binding diagnostic. Pure logic: no I/O, no broker imports.

WHY THIS EXISTS: crypto_trend.boot_p_dd, term_structure.bootstrap_p_maxdd,
and the boot_dd_dollars copy-pasted between phase2_e5_e4v2.py and
phase2_e14.py were three independent implementations of the same idea
(i.i.d. resample a return series, walk the resulting equity curve, check
whether it ever drew down past a threshold). That duplication is itself a
drift risk: a fix to one copy silently does not reach the others. It is
also how the E12 gate-audit finding (HYPOTHESES.md, E12 CAVEAT A — a
gross-exposure cap silently suppressed realized vol to 7.4% against a
registered 15% target, so the reported P(maxDD>40%)=0.038 did not hold at
the actually-registered target; re-scaled, 0.557) went unchecked for E9
and E11 until a dedicated one-off audit (audit_ruin_gate_e9_e11.py,
2026-07-29) confirmed those two were clean. This module productizes both:
one canonical bootstrap function, and one reusable version of the exact
diagnostic that audit performed by hand, so it can run automatically going
forward instead of waiting for someone to think to check.

INTEGRITY CONSTRAINT: bootstrap_p_ruin here is a byte-for-byte behavioral
match (same RNG draw sequence for the same seed, same comparison
semantics) for each of the three functions it replaces, GIVEN each call
site passes its own historically-used seed/threshold/mode. It changes NO
already-recorded gate number. See test_risk_gates.py for the synthetic
proof and the regression check against every already-evaluated
hypothesis's recorded figure.

Deliberately NOT unified: the underlying SIZING mechanisms (how a
per-date exposure multiplier or weight is computed) differ across
families for real, documented reasons — term_structure.py's EWMA
vol-target with a book-level gross_cap ceiling, e7_carry.py's simpler
post-hoc pro-rata rescale when Σ|w|>1, crypto_trend.py's single-asset
leverage ceiling at 1x. Forcing those into one function would risk
altering results neither pre-registered nor audited to change. Only the
REPORTING layer is shared here: hand cap_binding_report() a per-date
boolean "was some cap/ceiling binding today" series (computed however
that family's own code naturally produces it) plus the realized return
series and target, and it reports the same diagnostic
audit_ruin_gate_e9_e11.py already validated on E9/E11 — including the
artifact-risk flag, using the same thresholds (>50% of days binding AND
realized vol <85% of target) that distinguished E12 (artifact) from E9/E11
(clean).

WHAT IS AND ISN'T AUTOMATICALLY WIRED (2026-07-29 consolidation scope):
  Style A (EWMA vol-target + gross_cap ceiling on the multiplier) —
    term_structure.py/termstructure_backtest.py (E9/E11/E12): WIRED, see
    termstructure_backtest.cap_diagnostic().
  Style B (single-asset leverage ceiling at 1x, w_tgt=min(1,target/vol)) —
    crypto_trend.py (E4-v2) and e17_pivot_structure.py (E17-v2): WIRED,
    see single_asset_cap_diagnostic() below.
  Style C (post-hoc book-level pro-rata rescale when Σ|w|>1) —
    e7_carry.py (E7) and portfolio_trend.py (E6): NOT WIRED. Both compute
    per-date weights inside a Python for-loop and don't currently return
    the full per-date weight matrix; exposing it would mean changing
    run_e7()'s/run_e6()'s return signature, which every existing caller
    unpacks positionally — a real risk to a frozen, already-evaluated
    backtest for a diagnostic-only feature. Deliberately left as a manual
    check (mirroring what this whole module started as): if either ever
    comes under closer scrutiny again, compute `binding = tot > 1.0`
    where `tot = np.abs(w).sum()` at each date (already sitting right
    there in both functions' loops) and feed it to cap_binding_report()
    by hand, same as audit_ruin_gate_e9_e11.py did before this module
    existed. Lower priority in practice: E7 already fails decisively on
    PF/attribution (ruin was never its stated failure reason), and E6's
    own pass was noted as "the only pass where the ruin gate wasn't the
    central drama" (BOTTLENECK_DIAGNOSIS_2026-07-25.md) — i.e. already
    the least suspicious of the three passing/marginal hypotheses.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def bootstrap_p_ruin(returns, threshold: float, n_paths: int = 10_000,
                      seed: int = 0, mode: str = "compound") -> float:
    """P(the walked equity/PnL curve ever draws down past `threshold`),
    via i.i.d. resample of `returns`, full length, `n_paths` draws.

    mode="compound": returns are fractional per-period returns; equity
      compounds via cumprod (1+r); threshold is a FRACTION of peak equity
      (e.g. 0.40 = 40% drawdown). Replaces crypto_trend.boot_p_dd and
      term_structure.bootstrap_p_maxdd — algorithmically identical to both
      (they used the same eq/peak-1 vs (eq-peak)/peak arithmetic, which
      are the same quantity).
    mode="additive": returns are per-period dollar P&L; equity accumulates
      via cumsum; threshold is an ABSOLUTE dollar level. Replaces the
      boot_dd_dollars duplicated in phase2_e5_e4v2.py / phase2_e14.py.

    Each call creates its OWN rng from `seed` — no shared/module-level RNG
    state, unlike the two boot_dd_dollars copies this replaces (which used
    a module-level RNG object; harmless for their actual historical usage,
    since each was only ever called once per script run before any other
    draw, but a latent bug class for any future second call in the same
    process). Pass the ORIGINAL call site's seed explicitly to reproduce
    its recorded number exactly (crypto family: seed=7; term-structure
    family: seed=0; E5: seed=7; E14: seed=14 — see test_risk_gates.py).
    """
    if mode not in ("compound", "additive"):
        raise ValueError(f"mode must be 'compound' or 'additive', got {mode!r}")
    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) == 0:
        return 1.0
    rng = np.random.default_rng(seed)
    n = len(r)
    hits = 0
    for _ in range(n_paths):
        samp = rng.choice(r, size=n, replace=True)
        if mode == "compound":
            eq = np.cumprod(1.0 + samp)
            dd = (eq / np.maximum.accumulate(eq) - 1.0).min()
            if -dd > threshold:
                hits += 1
        else:
            eq = np.cumsum(samp)
            dd = (eq - np.maximum.accumulate(eq)).min()
            if dd < -threshold:
                hits += 1
    return hits / n_paths


def cap_binding_report(binding: pd.Series, realized_returns: pd.Series,
                        target_ann_vol: float, ann: float = 252.0,
                        binding_frac_threshold: float = 0.50,
                        vol_shortfall_threshold: float = 0.85) -> dict:
    """Generic version of the diagnostic audit_ruin_gate_e9_e11.py ran by
    hand for E9/E11 against the E12 cap-suppression pattern.

    `binding`: a bool-like per-date series/array, True on dates where
    whatever cap/ceiling this family's sizing uses actually bound (e.g.
    term_structure: the vol-target multiplier was clipped at gross_cap/2;
    e7_carry: Σ|w|>1 triggered the pro-rata rescale). Caller computes this
    locally from its own sizing step — this function does not know how
    any family's cap works, only how to report on the result.
    `realized_returns`: the AS-REGISTERED (post-cap) return series that
    already feeds this hypothesis's own bootstrap_p_ruin call.
    `target_ann_vol`: the registered vol target (e.g. 0.15).

    artifact_risk=True exactly reproduces the E12-vs-E9/E11 split found by
    hand: E12 had binding_frac=0.966, vol_ratio=7.4/15=0.49 (both flagged);
    E9 had 0.330, 0.967 (neither flagged); E11 had 0.259, 0.987 (neither
    flagged). Both conditions must hold — a cap that binds often but still
    lands near target isn't suppressing anything; a cap that rarely binds
    can't be the cause of a large vol shortfall either.
    """
    b = pd.Series(binding).astype(bool)
    binding_frac = float(b.mean()) if len(b) else 0.0
    realized_vol = float(pd.Series(realized_returns).dropna().std() * np.sqrt(ann))
    vol_ratio = realized_vol / target_ann_vol if target_ann_vol > 0 else float("nan")
    artifact_risk = (binding_frac > binding_frac_threshold
                      and vol_ratio < vol_shortfall_threshold)
    return dict(binding_frac=binding_frac, realized_vol=realized_vol,
                target_ann_vol=target_ann_vol, vol_ratio=vol_ratio,
                artifact_risk=artifact_risk)


def single_asset_cap_diagnostic(price_close, vol_win: int, vol_target: float,
                                 ann: float = 365.0, **report_kwargs) -> dict:
    """Style-B cap diagnostic: the single-asset leverage-ceiling pattern
    duplicated identically in crypto_trend.run_e4_voltarget (E4-v2) and
    e17_pivot_structure.run_backtest_voltarget (E17-v2) --
    w_tgt = min(1, vol_target/sigma_t), sigma_t a trailing rolling-std
    vol estimate. This is architecturally milder than a book-level
    gross_cap (it only ever LIMITS exposure, never permits leverage above
    1x), but still worth checking: a low-vol asset pinned at the 1x
    ceiling for most of the sample means the "vol-targeted" book is
    actually running near its raw, unscaled vol most of the time, same
    class of question as the term-structure gross_cap.

    Takes RAW CLOSE PRICES (not returns) so it can be called with exactly
    the same `df["close"]` input the sizing function itself uses, without
    needing that function to expose any internal series. Does not call or
    depend on run_e4_voltarget/run_backtest_voltarget -- this is an
    independent, cheap re-derivation (one rolling-std pass), not a
    modification of either frozen backtest function.

    SCOPE NOTE: `realized_vol` here measures the asset held CONTINUOUSLY
    at the vol-target sizing (w_tgt applied every day, one-day-shifted to
    stay no-lookahead), not the actual signal-gated traded book -- getting
    the latter exactly would require re-deriving the trend/pivot signal
    too, which this function deliberately does not do (see module
    docstring: no re-derivation of frozen backtest internals). This still
    answers the question that matters for cap-artifact risk -- "does the
    1x ceiling structurally bind for this asset at this vol target" --
    since gating to flat-when-no-signal can only pull realized exposure
    DOWN from the continuously-held case, never push the ceiling into
    binding more than this estimate shows.
    """
    c = np.asarray(price_close, dtype=float)
    r = np.zeros(len(c))
    r[1:] = c[1:] / c[:-1] - 1.0
    r_s = pd.Series(r)
    vol = r_s.rolling(vol_win).std() * np.sqrt(ann)
    w_tgt = np.minimum(1.0, vol_target / vol.replace(0, np.nan)).fillna(0.0)
    binding = w_tgt >= 1.0 - 1e-12
    scaled_ret = w_tgt.shift(1).fillna(0.0) * r_s  # no-lookahead: decide at t, apply to r[t+1]
    return cap_binding_report(binding, scaled_ret, vol_target, ann=ann, **report_kwargs)
