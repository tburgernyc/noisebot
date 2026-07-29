# E18 — DRAFT REGISTRATION (not yet in HYPOTHESES.md — DO NOT EVALUATE before E16 and E17 have real standalone numbers)

Per `.claude/skills/register-hypothesis`: written and echoed back per
that skill's required fields. Nothing here has been evaluated on real
data. `e18_regime_switch.py` + `test_e18.py` machinery-verified on
SYNTHETIC data only — 5/5 pass, and **a third real bug was caught and
fixed during construction** (see below) — this is exactly the value of
verifying before registering, not after.

## E18 — Regime-Switched Combination: E17 (trend mode) / E16 (range mode)

### Sequencing — read this before anything else

This hypothesis is built FROM E16 and E17. Per the E4→E4-v2 precedent
(never compound before you understand the parts): **do not evaluate this
on real data until E16 and E17 each have real, standalone numbers.**
Beyond that, add one more pre-condition specific to a combination: if
E16 and E17's real backtests turn out highly correlated WITH EACH OTHER,
a regime switch between them adds complexity without diversification —
check that before spending an evaluation on this.

### A third structural bug, found and fixed while building this

The regime gate is a simplified version of MTF Compass Pro's multi-
horizon alignment logic. Building it surfaced a real unit bug in the
source: MTF Compass's `normSlope` divides a **raw price difference**
(`ema[t]-ema[t-1]`, in price units) by `atrPct` (a percentage NUMBER)
without first converting the numerator to a percentage. Confirmed on
synthetic data (price level ~100): the ratio came out in the tens against
a default threshold of 0.1, so the slope filter was satisfied on 99.6%
of bars — the regime classifier read "trend" almost constantly,
defeating the entire point of a regime gate. **Fixed** in
`compute_regime()` by converting the EMA's own bar-over-bar move to a
percentage before dividing by ATR% — both sides now dimensionless, and
`slope_atr_mult=0.1` means what its name implies. This is on top of the
two E17 fixes (repaint/lookahead shift, O(n²)→O(n) reaction tracking)
that carry through unchanged since E18 reuses `e17_pivot_structure.py`
directly.

### What's combined and why

- **Trend mode** (≥2 of 3 EMA horizons — 20/50/200 — aligned, by price-
  vs-EMA and a volatility-normalized slope): run **E17**'s pivot-
  structure `trend_state` directly.
- **Range mode** (horizons disagree): run **E16**'s capitulation entry/
  exit logic, adapted into a continuous per-bar position
  (`e16_position_series`) so it can be interrupted by a regime flip
  rather than assuming it always runs to its own target/time/stop exit
  uninterrupted.
- The regime classifier's RSI leg is deliberately dropped (would be
  collinear with E16's own RSI-based entry — the E8-R "delete a
  collinear filter" precedent, applied pre-data here). Ichimoku's TK-
  cross is not used anywhere in this system for the same reason: its
  content is already in the short-horizon EMA leg.

### Economic rationale

Trend-following and mean-reversion are regime-complementary — a
capitulation fade is exactly the wrong trade against a strong, real
markdown (buying a dip that's actually early-stage), and a channel/
structure breakout is exactly the trade most likely to be a fakeout
during chop. This is standard, well-established practice (not specific
literature, general regime-conditioning logic), and the Swing Failure
Pattern research already cited in `IDEAS_AUDIT_AND_SYNTHESIS.md` and
`E17_HYPOTHESIS_DRAFT.md` — ~74% win rate in consolidation vs. ~52% in
strong trends for the closely related failure-swing pattern family — is
a specific, citable (if not peer-reviewed) claim that exactly this kind
of regime-conditioning matters for this kind of setup.

**Important limitation, stated plainly**: the regime classifier itself
is NOT separately gated the way E16/E17 are — it has no standalone
`HYPOTHESES.md` entry, no plateau, no correlation gate of its own. Its
only validation so far is "the unit bug is fixed and it produces
variation in both directions on synthetic data." Treat E18's result as
conditional on the regime classifier being a reasonable proxy for
trend/range, not as independent confirmation that it is one.

### Exact specification (fixed before any run)

- Universe: BTC-USD, daily (same instrument/timeframe as E16 and E17,
  so the combination is a fair test of switching between them, not also
  a change of venue).
- Regime: EMA(20/50/200), slope-vs-ATR% threshold 0.1, ≥2-of-3 alignment
  — all fixed at the values used during construction, not tuned.
- Trend-mode leg: E17 unchanged. Range-mode leg: E16 unchanged (same
  RSI/MA/volume thresholds, same target/time-stop/hard-stop exits).
- **Registered plateau: none new** — E18 inherits E16's and E17's own
  plateau requirements; this registration adds no additional swept
  parameter of its own, by design (a combination hypothesis with its own
  plateau on top of two inherited ones would be very easy to quietly
  overfit).
- Costs: 0.35% fee/side + 10bps slip (consistent with E16/E17).

### Prediction (what confirms / falsifies)

Confirms: combined Sharpe/PF exceeds BOTH E16 alone and E17 alone (not
just beats one of them) — otherwise the switch isn't earning its
complexity, and you should simply run whichever component was better on
its own. Falsifies: combined performance is worse than the better of the
two standalone components, or E16/E17 turn out too correlated with each
other for a regime switch to add anything (see Sequencing above).

### Gates

Standard set (n≥100, PF>1.3, both halves, bootstrap P(maxDD>40%)<10%,
Sharpe ≥ BTC buy-hold) **plus** the two combination-specific bars in
Prediction above, which govern the actual go/no-go more than the generic
gates do here.

### Kill criterion

Any standard gate fails, OR combined Sharpe/PF does not exceed both
standalone components → E18 falsified/not worth deploying over running
the better single component. No retune of the regime thresholds after
seeing results — if the regime gate looks miscalibrated post-hoc, that's
a new, separately-registered hypothesis about the classifier, not a
silent edit here.

### Files (delivered, not yet run on real data)

- `e18_regime_switch.py` — regime classifier + both components' adapters
  + combined backtest runner with a rough P&L attribution split (
  diagnostic only, not a gate).
- `test_e18.py` — 5/5 PASS on synthetic data: regime produces both
  states, no-lookahead, range-mode routing (structurally verified across
  every bar of both regimes, plus a best-effort direct crash-routing
  check), and a backtest sanity/attribution check.
