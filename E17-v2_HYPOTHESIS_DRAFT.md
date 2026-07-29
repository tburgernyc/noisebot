# E17-v2 — DRAFT REGISTRATION (not yet in HYPOTHESES.md — Tim's sign-off required before any run)

Per `.claude/skills/register-hypothesis`. This is the highest-confidence
item in `BOTTLENECK_DIAGNOSIS_2026-07-25.md` — not a new signal search,
a direct application of the one risk-engineering fix this repo has
already proven works (E4→E4-v2), to the one other hypothesis whose
failure shape matches E4's original failure shape most closely.
`run_backtest_voltarget` is written, in `e17_pivot_structure.py`, and
machinery-verified on synthetic data — `test_e17.py` is now **9/9**,
including a dedicated high-volatility fixture (~67% annualized, BTC-
like) showing the mechanism actually working: full-size maxDD −61.4%
vs. vol-targeted −18.9%, with nearly identical final returns (1.03x vs.
1.04x). Nothing has been run on real data.

## E17-v2 — Livermore pivot-structure breakout, vol-targeted sizing (BTC)

### Rationale (same shape as E4→E4-v2, restated for E17)

E17 passed 4 of 6 gates decisively — PF 7.618, both halves positive,
plateau strongly positive across all three registered pivot windows,
Sharpe 1.410 vs. buy-hold 0.962 — and failed specifically and only on
tail risk (bootstrap P(maxDD>40%) = 74.1%) plus trade count (n=47). This
is the exact shape of E4's original failure (PF 2.86, ruin-gate FAIL,
fixed by E4-v2's vol-targeting without touching the signal). **This is a
GATE FIX, not a signal search** — `compute_signals()` is completely
unchanged; only the exposure-sizing layer changes, exactly as E4-v2 only
changed E4's sizing.

**What this registration does NOT claim to fix**: n=47 is a property of
the signal's own firing frequency (a 10-day pivot breakout on daily BTC
bars), not of position sizing — vol-targeting does not and cannot
increase trade count. If the vol-targeted version clears every other
gate but n stays at 47, **it still fails the n≥100 gate** and this
registration is falsified on that basis alone, honestly, not quietly
waived because "the important part passed." Said differently in advance
(per the register-hypothesis discipline of stating the falsification
condition before running): passing the ruin gate but not the n gate is
STILL a fail here, and should be read as "the sizing fix works, the
frequency problem is separate and unsolved" rather than as a win.

Also worth stating plainly: E17's own correlation with E4-v2/E6 was
0.72/0.59 (reported, not gated, in the original registration). Vol-
targeting does not change the underlying signal, so this will not
improve — if E17-v2 clears every gate including n, it is very likely
still substantially correlated with the trend book already in shadow
trading, and the case for deploying it would rest on modest
incremental diversification, not a fresh return stream.

### Exact specification (fixed before any run)

- Universe/timeframe: BTC-USD, daily — unchanged from E17.
- Signal: `e17_pivot_structure.compute_signals()`, pivot_left=pivot_
  right=10, neutral_lookback=5 — byte-for-byte unchanged from E17's
  registered primary cell.
- Sizing (the only change): `run_backtest_voltarget()` — exposure
  w_t = min(1, vol_target / sigma_t) applied to trend_state's direction;
  sigma_t = 30-day realized volatility of daily returns, annualized
  (sqrt(365)), computed using only returns through bar t (no lookahead
  — identical construction to `crypto_trend.run_e4_voltarget`).
  vol_target = 0.15 (E4-v2's registered value, reused for direct
  comparability, not re-derived).
- Costs: 0.35% fee/side + 10bps slip (unchanged, E4/E4-v2 convention).
- Long/flat by default (`allow_short=False`); short variant not
  registered here, same as E17.
- **Registered plateau parameter: vol_target — 0.10 / 0.15 / 0.20 — all
  three must be net positive.** (Pivot window stays fixed at 10/10 —
  that plateau was already cleared by E17 itself; sweeping it again here
  would be re-litigating an already-passed gate. vol_win=30 is E4-v2's
  shipped default, fixed, not swept.)

### Gates (IDENTICAL to E17's original bar — not weakened)

n ≥ 100 trades; PF > 1.3; both sample halves net-positive; plateau (all
three vol_target cells) net-positive; bootstrap (10k paths) P(maxDD >
40%) < 10%; Sharpe ≥ BTC buy-hold Sharpe on the identical window;
correlation vs. E4-v2 and E6 reported and interpreted (not a hard gate,
matching E17's own convention).

### Prediction

If the diagnosis in `BOTTLENECK_DIAGNOSIS_2026-07-25.md` is right (E17's
problem is tail risk, not edge quality): PF stays strong (will fall
somewhat from 7.6 as de-risking trims the best trades too, but should
stay well above 1.3, mirroring E4→E4-v2's PF 2.86→2.84), bootstrap ruin
drops sharply (E4's 97.8%→0.1% is the reference magnitude), Sharpe likely
*improves* (E4's went 1.11→1.38 — de-risking a fat-tailed series often
raises risk-adjusted return even as raw CAGR falls). n stays at 47 and
this alone falls short of the registered gate — **the expected outcome
of this specific registration, stated in advance, is "passes every gate
except n."** If PF collapses or ruin risk barely improves, the diagnosis
itself would be wrong for E17 specifically (i.e., its problem was
Population-2-shaped — weak underlying edge — not Population-1-shaped —
strong edge, bad tail risk — contrary to what the raw numbers suggest),
which would itself be useful to know.

### Kill criterion

Any gate fails → E17-v2 falsified on this window, recorded, no retune.
Given the n≥100 gate is very unlikely to pass on daily BTC alone (see
Prediction), a likely honest outcome here is "falsified on n, but the
ruin-gate mechanism confirmed working" — record that distinction
explicitly rather than collapsing it into an undifferentiated FAIL, the
same way E4's original write-up distinguished "signal real, sizing
wrong" from a sign failure.

### Window ledger

BTC daily: this would be evaluation #6 (E4/E4-v2/E4-v3/E6/E17/E17-v2) —
a sizing-only variant of an already-registered signal, same treatment
E4-v2 got relative to E4. Not claimed as fresh.

### Files

- `e17_pivot_structure.py` — `run_backtest_voltarget()` added, `compute_
  signals()` untouched.
- `test_e17.py` — 9/9 PASS on synthetic data (8 prior + 1 new: a
  dedicated ~67%-annualized-vol fixture confirming the sizing fix
  actually reduces drawdown, since the shared low-vol fixture used by
  the rest of the suite never makes vol_target bind).
- Real evaluation still requires: (1) this entry copied into
  `HYPOTHESES.md` and your sign-off, (2) the actual registered run —
  the BTC daily data and loader are already in place from E17.
