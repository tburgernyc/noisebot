# HYPOTHESES — noise_bot (v2, re-created 2026-07-15)

Rule: nothing gets backtested unless it is registered here FIRST with an
economic rationale. One evaluation per hypothesis. Failures stay on the
record. Every metric ships with its n.

Window ledger (multiplicity budget):
- Databento MNQ 1m 2024-07-01→2026-07-14 (524 RTH days): evaluations used —
  noise-area baseline (1). E1 and E2 registered below get one each.
- Yahoo 60-day Tier A window: BURNED for selection. Data-QA use only.

---

## ARCHIVED — Noise-Area Intraday Momentum (Zarattini/Barbon/Aziz)

- BASELINE: **FALSIFIED** on MNQ 2024-07→2026-07 (2026-07-14 run, log:
  logs/phase2_baseline_2026-07-14.log). n=512 trades / 489 days: PF 0.98,
  WR 37.3%, total $-773/ct, maxDD $-7,466/ct, half1 $-867, plateau
  lb10/14/20 all negative, barrier-MC P(blow) 68.9%. Failed 4 of 6 gates.
- H1 (relative-range regime filter): **UNTESTABLE — registered definitions
  lost** in the Windows→Ubuntu machine wipe; never pushed to git. Do not
  reconstruct from memory (sweep-and-select in disguise).
- H2 (dual trail): **UNTESTABLE — registered definitions lost** (same).
- Process fix adopted: registered artifacts are committed and pushed to
  github.com/tburgernyc/noisebot the moment they are written.

---

## E1 — REGISTERED 2026-07-15 (pre-test): ORB-15 with range-compression filter

Economic rationale: after a compressed opening range, resting liquidity and
stops cluster tightly around the OR extremes; a breakout puts short-term
participants offside at once and their forced exits extend the move
(compression→expansion). Documented family: Zarattini & Aziz ORB studies
on QQQ/NQ. This is momentum *conditioned on an event*, not the always-on
momentum already falsified.

Rules (ALL fixed before any run):
- OR = high/low of 09:30–09:45 ET (first three 5m bars).
- Compression filter: trade the day ONLY if OR range ≤ 30% of the median
  full-RTH range of the prior 14 sessions.
- Entry: first 5m CLOSE > OR high → LONG; first 5m CLOSE < OR low → SHORT.
  Entry signals valid 09:45–14:00 ET. Fill next bar open +1 tick adverse.
  ONE trade per day. No re-entry, no reversal.
- Stop: 5m close beyond the opposite OR extreme → exit next open, adverse tick.
- Time exit: 15:55 ET flatten, no exceptions.
- Costs $2.50/ct RT; 1 contract; per-contract MNQ dollars.
- Registered plateau parameter: OR window 10 / 15 / 20 minutes — all three
  must be net positive. (Compression threshold 30% and 14-session median
  are FIXED, not swept.)
- Gates: standard Phase 2 set (n≥100, PF>1.3, both halves>0, plateau all>0,
  barrier-MC P(blow)<10%).
- Kill criterion: any gate fails → E1 is falsified on this window. No retune.

---

## E2 — REGISTERED 2026-07-15 (pre-test): VWAP mean-reversion, info-day filtered

Economic rationale: institutional execution is benchmarked to VWAP;
VWAP-pegged algos supply passive liquidity that pulls price back toward the
session anchor when aggressive flow stretches it without new information.
The falsified always-on momentum baseline (PF 0.98 ≈ zero edge) is
consistent with this window leaning mean-reverting intraday. Reversion
should fail precisely on information days — hence the gap filter.

Rules (ALL fixed before any run):
- VWAP: session-cumulative from 09:30, typical price (H+L+C)/3 × volume,
  RTH bars only.
- Stretch: z = (close − VWAP) / ATR20, ATR20 = 20-bar average true range on
  5m RTH bars (rolls across sessions).
- Info-day filter: skip the ENTIRE day if overnight |gap| > 75th percentile
  of the trailing 60 sessions' |gaps|.
- Entry window 10:00–15:00 ET: 5m close with z ≥ +2.0 → SHORT; z ≤ −2.0 →
  LONG. Fill next bar open +1 tick adverse. One position at a time,
  max 3 entries/day.
- Exit: 5m close crosses VWAP (target) OR |z| ≥ 3.5 at close (stop) →
  fill next open, adverse tick. 15:55 ET flatten, no exceptions.
- Costs $2.50/ct RT; 1 contract; per-contract MNQ dollars.
- Registered plateau parameter: entry threshold z = 1.75 / 2.00 / 2.25 —
  all three must be net positive. (Stop 3.5, ATR20, gap-p75 are FIXED.)
- Gates: standard Phase 2 set (n≥100, PF>1.3, both halves>0, plateau all>0,
  barrier-MC P(blow)<10%).
- Kill criterion: any gate fails → E2 is falsified on this window. No retune.

---

## RESULTS LOG (append-only; passes AND failures)
