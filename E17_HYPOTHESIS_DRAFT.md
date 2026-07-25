# E17 — DRAFT REGISTRATION (not yet in HYPOTHESES.md — Tim's sign-off required before any run)

Per `.claude/skills/register-hypothesis`: written and echoed back per that
skill's required fields. Nothing here has been evaluated on real data.
`e17_pivot_structure.py` + `test_e17.py` machinery-verified on SYNTHETIC
data — **8/8 pass**, including a cross-check that matters more than usual
here (see below).

**Data loader now wired up** (`load_yahoo_daily_ohlcv`, identical copy to
E16's — see that draft for the loader-specific findings) and verified
against real BTC-USD daily history: 4330 bars, 2014-09-17 → 2026-07-25,
zero nulls, correct high≥low/high≥close/low≤close ordering. The same
`range=max` auto-coarsening bug documented in `E16_HYPOTHESIS_DRAFT.md`
applies here too — worth restating for E17 specifically since a
pivot_left/right=10 window silently fed monthly-spaced bars would have
been a much quieter, harder-to-notice failure than for E16's RSI/MA
(pivots would still "detect" something, just structurally meaningless
ones spanning 10 months instead of 10 days). Fixed the same way
(explicit `period1`/`period2`, spacing guard on every load).

## E17 — Livermore Pivot-Structure Breakout (BTC, candidate)

### Provenance / structural audit

Source: public indicator "Pivot Levels & Candle Color (Dark Theme)" (Tim
supplied the script) — the most sophisticated of the four uploaded, and
the audit found two real issues, one of them serious:

1. **Repaint / lookahead bug in the source (the important one).** A pivot
   at bar `i` requires seeing `pivot_right_bars` bars AFTER `i` to confirm
   (the right-side reversal check) — it is not actually known until bar
   `i + pivot_right_bars`. The source stores it AT index `i` and its
   trend-state loop reads it at that same index `i`, which silently uses
   future information. This is a common, easy-to-miss property of chart
   pivot/fractal tools (harmless for visual hindsight, fatal for a
   backtest) — **fixed** by shifting pivot availability forward by
   `pivot_right_bars` (`shift_for_availability` in
   `e17_pivot_structure.py`), verified by a dedicated test
   (`test_pivot_availability_shift_is_correct`) plus the standard
   perturb-the-future no-lookahead test.
2. **O(n²) performance issue, not a correctness bug.** The source
   recomputes the "reaction low/high" (lowest/highest point since the
   breakout, used as a failure-swing invalidation trigger) by rescanning
   the entire leg every time a new high/low-water-mark bar occurs.
   Replaced with an O(1)-amortized accumulator — **cross-checked against
   a literal port of the source's own rescan algorithm on synthetic data:
   0 mismatches across 2000 bars** (`test_fast_matches_bruteforce_
   reaction_tracking`). This isn't asserted, it's tested.

No other logic bugs found — the state machine itself (breakout → track
high-water-mark + reaction level → invalidate on failure-swing OR a
separate three-part stall/consolidation detector after enough bars have
passed) is a coherent, well-thought-through implementation of classical
Livermore/Wyckoff swing-structure trading.

### Economic rationale

Breakout above a confirmed swing high is treated as a genuine regime
shift (stops and momentum-chasing flow extend it); the reaction-low
invalidation is specifically a **failure-swing** check — if the
"breakout" immediately gives back to below the low made right after
breaking out, it was a stop-run, not a trend. The separate stall detector
catches a different, later failure mode: the trend going quiet (no new
highs, tightening range, price parked near the midpoint) well after the
breakout, independent of any hard invalidation level being touched.

**Registered prior against** (stated up front): mechanically related to
E1 (ORB breakout, falsified on MNQ) and H3-EXT (SMC/ICT, falsified on
EURUSD) — both are "price-structure breakout" mechanisms too. Not
obviously a fresh family; the specific failure-swing + stall-detector
combination is more developed than either falsified relative, but that's
a reason to test it honestly, not a reason to assume it's exempt from
their track record.

**Independent, directly relevant evidence on the failure-swing leg
specifically**: practitioner sources on the closely related "Swing
Failure Pattern" cite (not peer-reviewed, flagged as such) win rates
around 74% in consolidation vs. ~52% in strong trends for that pattern
family — i.e., a citable claim that this exact style of setup is
regime-dependent. That's the direct motivation for E18's regime gate,
and a reason to expect E17's OWN standalone numbers might look uneven
across the sample rather than uniformly strong or weak.

### Exact specification (fixed before any run)

- Universe: BTC-USD, daily bars. Swing-structure trading is
  mechanistically a slower, higher-timeframe practice — daily is the
  deliberate choice, same honesty-over-freshness call as E16 (this
  window is heavily mined for the TREND mechanism family — see below).
- Pivot detection: look-left/look-right confirmation + timeframe-adaptive
  confirmation factor + significance filter, exactly as audited above.
- **Registered plateau: pivot window (left=right, jointly) — 7 / 10 / 15
  bars**, all other parameters fixed at the indicator's shipped defaults
  (`neutral_lookback=5`).
- Position tracks `trend_state` directly (E4-style: no separate stop/
  target leg — the state machine's own invalidation IS the exit).
  Long/flat by default (`allow_short=False`, E4-v2/E6 spot convention);
  `allow_short=True` for a perp/futures variant, not registered here.
- Costs: 0.35% fee/side + 10bps slip (E4/E4-v2 daily convention).

### Prediction (what confirms / falsifies)

If real and distinct: PF > 1.3, all three pivot-window plateau cells net-
positive, both sample halves profitable, and daily-return correlation vs.
E4-v2/E6 that is positive but not so high it reads as "the same trend bet
with extra steps" (unlike E16, where LOW correlation is hoped for, here
SOME correlation with the trend sleeves is economically expected — a
correlation near 1.0 would mean the failure-swing/stall machinery isn't
adding anything beyond what a simple trailing-return signal already
captures). If the mechanism doesn't survive next-bar fills and real costs
the way E1/H3-EXT didn't, or if it's just a relabeled version of E4-v2:
falsified either way, for different reasons — both should be reported
explicitly, not collapsed into one "FAIL."

### Gates (standard set + correlation)

n ≥ 100 trades; PF > 1.3; both sample halves net-positive; plateau (7/10/15
pivot window, all three) net-positive; bootstrap (10k paths)
P(maxDD > 40%) < 10%; Sharpe ≥ BTC buy-hold Sharpe; correlation gate vs.
E4-v2 and E6 — reported and interpreted per the Prediction section above,
not just pass/fail.

### Data window / multiplicity

BTC daily: same reused-price-data situation as E16 — 4-5 prior
evaluations, all of the trend-family mechanism. A price-structure
breakout mechanism is a different kind of test, logged honestly, not
claimed as a fresh window.

### Kill criterion

Any gate fails → E17 falsified on this window, recorded, no retune, no
threshold search, no re-run with a different pivot-confirmation factor
after seeing results.

### Files (delivered, not yet run on real data)

- `e17_pivot_structure.py` — pure signal logic + backtest runner + data
  loader (`load_yahoo_daily_ohlcv`), including both the fast (production)
  and bruteforce (verification-only) reaction-tracking implementations.
- `test_e17.py` — **8/8 PASS** on synthetic data: pivot-availability shift
  correctness, fast-vs-bruteforce equivalence (0 mismatches), state-domain
  sanity, no-lookahead perturbation, long-flat/long-short backtest smoke
  tests, a performance comparison, and two spacing-guard regression tests.
- `data/btc_usd_1d.json` — real daily OHLCV, already fetched and
  loader-verified (shape/dtype/spacing only, not run through
  `compute_signals`/`run_backtest` — that's the registered evaluation
  itself, still gated on your sign-off).
- Real evaluation still requires: (1) this entry copied into
  `HYPOTHESES.md` and your sign-off, (2) the actual registered run —
  that's it, the loader is no longer a blocker.
