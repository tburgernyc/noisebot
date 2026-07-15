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

### 2026-07-15 — E1 evaluation (single registered run; log: logs/phase2_e1e2_2026-07-15.log)
E1 VERDICT: **FAIL** — n=183, WR 43.2%, PF 1.12 (gate >1.3), total $2,286/ct,
maxDD $-3,355/ct, half1 $3,226 / half2 $-940 (half2 gate FAIL), plateau
OR10 $-204 / OR15 $2,286 / OR20 $1,146 (OR10 negative, gate FAIL),
barrier-MC P(blow) 50.9% (gate FAIL). Failed 4/6 gates.
Note for the record: the only hypothesis so far with positive total and a
strongly positive first half — but the edge decays in the recent half,
which is precisely the half live capital would trade. Kill criterion
applies: E1 is falsified on this window. No retune.

### 2026-07-15 — E2 evaluation (single registered run; same log)
E2 VERDICT: **FAIL** — n=818, WR 38.4%, PF 0.79 (gate >1.3), total
$-8,656/ct, maxDD $-9,852/ct, half1 $-2,209 / half2 $-6,446 (both FAIL),
plateau z1.75 $-7,650 / z2.00 $-8,656 / z2.25 $-8,429 (all negative, FAIL),
barrier-MC P(blow) 87.5% (gate FAIL). Failed 5/6 gates. Decisively dead:
VWAP stretches on this window continued rather than reverted.

Window ledger update: Databento 2024-07→2026-07 evaluations used = 3
(baseline, E1, E2). Any further hypothesis on this window must be
registered with a mechanism materially different from always-on momentum,
event-conditioned momentum (ORB), and VWAP reversion.

---

## E3 — REGISTERED 2026-07-15 (pre-test): Last-hour flow momentum

Economic rationale: options market-makers and leveraged-ETF issuers must
rebalance hedges into the close in the direction of the day's move; this
mandated end-of-day flow makes the rest-of-day return predict the final
30 minutes (Baltussen/Da/Lammers/Martens JFE 2021, 60+ futures, asset-class
Sharpe 0.87–1.73; Dim/Eraker/Vilkov 2024 confirm the dealer-gamma channel
in the 0DTE era). Registered prior AGAINST: this is the nearest surviving
relative of our falsified momentum family — proximity noted deliberately.

Rules (ALL fixed before any run):
- Signal: at the 15:25 ET bar close, ROD = close(15:25)/RTH open(09:30) − 1.
- ROD > 0 → LONG; ROD < 0 → SHORT (sign only, no magnitude knob).
  Fill next bar open (15:30) +1 tick adverse. ONE trade/day, every
  qualifying day (skip only ROD exactly 0 or short sessions <60 bars).
- Exit: 15:55 ET flatten only (signal on 15:50 close, fill 15:55 open,
  adverse tick; defensive last-close exit as in baseline harness).
  No stop — the hold is 25 minutes by construction.
- Costs $2.50/ct RT; 1 contract; per-contract MNQ dollars.
- Registered plateau parameter: signal bar 15:15 / 15:25 / 15:35 (exit
  fixed at flatten) — all three must be net positive.
- Gates: standard Phase 2 set (n≥100, PF>1.3, both halves>0, plateau
  all>0, barrier-MC P(blow)<10%).
- Kill criterion: any gate fails → E3 falsified on this window. No retune,
  no added filters (vol/magnitude conditioning is NOT registered).

Window ledger: this consumes evaluation #4 on Databento 2024-07→2026-07.

### 2026-07-15 — E3 evaluation (single registered run; log: logs/phase2_e3_2026-07-15.log)
E3 VERDICT: **FAIL** — n=503, WR 44.5%, PF 0.81 (gate >1.3), total
$-3,846/ct, maxDD $-4,310/ct, half1 $-1,570 / half2 $-2,276 (both FAIL),
plateau 15:15 $-4,194 / 15:25 $-3,846 / 15:35 $-3,190 (all negative, FAIL),
barrier-MC P(blow) 87.0% (gate FAIL). Failed 5/6 gates.
Read: the JFE-2021 last-30-min effect does not survive on MNQ 2024-07→
2026-07 at honest costs — consistent with per-trade edge of a few bps
being below friction, and/or the effect being dealer-gamma-conditional
(conditioning was deliberately NOT registered) and/or decayed. The
registered prior-against was correct. No retune.

Window ledger update: Databento 2024-07→2026-07 evaluations used = 4
(baseline, E1, E2, E3). This window is heavily mined by our own process
now — treat any further hypothesis on it with elevated skepticism; prefer
NEW data (longer history, different instrument, or different asset class)
for the next registration.

---

## E4 — REGISTERED 2026-07-15 (pre-test): Slow BTC trend, long-only spot

Economic rationale: slow-moving capital and retail underreaction make
multi-week crypto trends persist; the documented value is DOWNSIDE
AVOIDANCE at similar return, not excess return (Han/Kang/Ryu SSRN 4675565:
net Sharpe 1.51 vs 0.85 buy-hold at 15 bps costs, 2014–2023; Kang/Ryu
Risk Mgmt 2026: slow signals beat fast). Decay documented post-ETF
(Rosen/Wang 2025) — registered prior: effect weakened in recent years,
halves gate is the live test of that.

Rules (ALL fixed before any run):
- Asset: BTC-USD only. Daily bars, 2014-01-01 → present. Source: Yahoo
  chart API daily closes, spot-checked vs a second source on overlap.
- Signal at each daily close: LONG 100% if trailing 28-day close-to-close
  return > 0, else FLAT (cash, 0% yield assumed). Position changes fill at
  NEXT daily open with 10 bps adverse slippage + 0.35% fee per side.
- Trade = one round trip (entry flip → exit flip). No leverage, no shorts.
- Registered plateau parameter: lookback 21 / 28 / 35 days — all three
  must be net positive at trade level.
- Gates (registered adaptation for spot asset — barrier-MC replaced):
  n ≥ 100 round trips; PF > 1.3; both sample halves positive; plateau
  all > 0; bootstrap (10k paths, daily-return resample, full sample
  length) P(maxDD > 40%) < 10%; AND annualized Sharpe (net) ≥ buy-hold
  Sharpe on the identical window.
- Kill criterion: any gate fails → E4 falsified on this window. No
  retune, no ETH fallback (ETH would be a separate registration).

Window ledger: BTC daily 2014→2026 is a FRESH window; evaluation #1.
