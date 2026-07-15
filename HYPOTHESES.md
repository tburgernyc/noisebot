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

### 2026-07-15 — E4 evaluation (single registered run; log: logs/phase2_e4_2026-07-15.log)
E4 VERDICT: **FAIL (6/7 gates passed)** — n=167 round trips, WR 34.7%,
PF 2.86, final equity 136.9x, half1 +8.35 / half2 +0.86 (both PASS),
plateau lb21/28/35 all positive (49.7x/136.9x/160.9x), Sharpe 1.11 vs
buy-hold 0.96 (PASS). FAILED gate: realized maxDD -78.5%; bootstrap
P(maxDD>40%) = 97.8% vs gate <10%.
Read: the trend signal is real on this window (PF 2.86 across 167 trades
is the strongest metric this pipeline has produced) but at full spot
sizing the strategy carries near-buy-hold ruin risk — it avoided only
~5pts of buy-hold's -83.4% maxDD. Half2 (+0.86 vs half1 +8.35) also
confirms the documented post-ETF decay direction. For a small account
where the capital is needed, the DD gate is the correct bar and it
failed decisively. Kill criterion applies to THIS registration (full
sizing). A fractionally-sized variant would be a NEW registration — and
honesty first: sizing down to pass the DD gate shrinks absolute returns
proportionally, which at $2-5k capital means the passing version earns
too little to matter. The binding constraint remains capital, not signal.

---

## E5 — REGISTERED 2026-07-15 (pre-test): Month-end rebalancing pressure (ES)

Economic rationale: pensions/target-date funds rebalance to fixed
stock/bond weights near month-end by MANDATE, not choice. When stocks
outperformed bonds month-to-date, they must sell equities into month-end
(and vice versa), depressing next-day returns ~17 bps, strongest in the
last 4 trading days (Harvey/Mazzoleni/Melone NBER WP 33554, 2025; ES +
10Y futures 1997–2023; est. $16B/yr transfer). Registered priors: effect
freshly published (decay risk); zero post-2023 OOS exists — our 2024–2026
tail is genuine OOS the paper never saw.

Rules (ALL fixed before any run):
- Data: ES.v.0 and ZN.v.0 daily (GLBX continuous, 2010-06-06→2026-07-15).
- Signal at close of day t, only when t is among the LAST 4 trading days
  of the calendar month: S = MTD(ES close-to-close) − MTD(ZN
  close-to-close), month-to-date from prior month-end close.
- S > 0 → SHORT ES for one day (overweight equities → rebalancers sell);
  S < 0 → LONG ES one day. Enter close(t) with 1 tick (0.25) adverse;
  exit close(t+1) with 1 tick adverse (MOC-style fills). Consecutive
  same-direction days chain as separate 1-day trades.
- Dollars: MES multiplier $5/pt; costs $2.50/ct RT per 1-day trade.
- Registered plateau parameter: window = last 3 / 4 / 5 trading days of
  month — all three must be net positive.
- Gates: n≥100, PF>1.3, both halves>0, plateau all>0, bootstrap
  P(maxDD > $2,500/ct) < 10% (spot-adapted ruin gate; overnight holds →
  NOT prop-compatible, IBKR-account edge).
- Kill criterion: any gate fails → E5 falsified. No retune.
Window ledger: ES daily 2010–2026 is a FRESH window; evaluation #1.

---

## E4-v2 — REGISTERED 2026-07-15 (pre-test): E4 signal at vol-targeted sizing

Rationale: E4 (28d BTC trend) passed 6/7 gates; sole failure was ruin
risk at full sizing (P(maxDD>40%) 97.8%). Registered fix is SIZING, not
signal: target 15% annualized vol — weight w_t = min(1, 0.15/σ_t), σ_t =
30-day realized vol (annualized √365), applied to the long leg only.
Signal, costs, and all E4 parameters unchanged. This is the standard CTA
construction (vol targeting), not a parameter search.
- Gates: identical to E4 (incl. P(maxDD>40%)<10% and Sharpe ≥ buy-hold).
- Kill criterion: any gate fails → E4-v2 falsified; no further sizing
  variants on this window.
Window ledger: BTC daily window evaluation #2 (E4 was #1). Sizing-only
variant of a 6/7 near-pass; logged as such.

### 2026-07-15 — E5 evaluation (single registered run; log: logs/phase2_e5_e4v2_2026-07-15.log)
E5 VERDICT: **FAIL** — n=771, WR 47.9%, PF 1.06 (gate >1.3), total
$2,200/ct over 16 yrs, half1 $258 / half2 $1,942 (both PASS), plateau
3/4/5-day all positive (PASS), P(maxDD>$2.5k) 86.8% (gate FAIL).
Read: the mechanism is likely REAL — direction consistent across both
halves and all three windows, and the effect strengthened post-2018
(consistent with NBER paper) — but ~$2.85/trade net edge is too small to
survive drawdown risk at micro scale. An institutional edge, not a
retail one. Falsified for OUR deployment; no retune.

### 2026-07-15 — E4-v2 evaluation (single registered run; same log)
E4-v2 VERDICT: **PASS — first hypothesis to clear all gates** — n=167,
WR 32.9%, PF 2.84, final 7.98x (~19% CAGR at 15% vol target), maxDD
-26.0%, half1 +2.17 / half2 +0.26, plateau lb21/28/35 all positive
(5.48x/7.98x/7.64x), bootstrap P(maxDD>40%) 0.1%, Sharpe 1.38 vs
buy-hold 0.96. 
Registered caveats carried forward: (1) half2 much weaker than half1 —
assume forward Sharpe materially below 1.38 (decay documented); (2) one
asset, long-only, ~14 trades/yr; (3) PASS means proceed to Phase 4
shadow validation, NOT capital. Phase 4 gate must be adapted (30 trades
would take ~2 yrs at this frequency): registered adaptation = 90
calendar days of daily shadow signals, zero critical errors, live w_t
and signal states matching backtest recomputation exactly; expectancy
comparison at whatever n accrues, reported with its (small) n.

---

## E4-v3 — REGISTERED 2026-07-15 (pre-test): E4-v2 with GARCH(1,1) sizing

Rationale: GARCH adds an "aftershock" term to vol estimation — reacts
faster after shock days than 30d realized vol. Literature prior: vol
clustering is robust; improvement over realized vol for TARGETING is
usually marginal. Sizing-estimator A/B, signal untouched.
Rules: identical to E4-v2 except σ_t = GARCH(1,1) 1-day-ahead forecast
on daily log returns, params refit every 21 trading days on expanding
window (min 500 obs warmup; realized-vol fallback before warmup),
variance recursion updated daily between refits. No lookahead: forecast
for day t+1 uses data through day t only.
Bar (pre-stated): must pass ALL E4 gates AND Sharpe ≥ E4-v2's AND maxDD
no worse than E4-v2's, else E4-v2 stands. BTC window evaluation #3.

---

## E6 — REGISTERED 2026-07-15 (pre-test): Multi-asset crypto trend sleeve

Rationale: institutional TSMOM blueprint (Moskowitz/Ooi/Pedersen; AQR
century-of-evidence) — same trend premium as E4, harvested with breadth,
blended horizons, and portfolio-level vol targeting. Honest prior:
BTC/ETH/SOL correlate ~0.7-0.8 → effective bets ~1.3-1.5, expect modest
improvement over E4-v2, not transformation.
Rules (ALL fixed):
- Universe: BTC-USD (2014-), ETH-USD (2017-), SOL-USD (2020-), daily,
  Yahoo. Assets enter the book when they have 120 obs of history.
- Score per asset: s_i = mean of 1[r_L > 0] for L ∈ {14,28,56} days.
- Vol/cov: EWMA λ=0.94 on daily returns (min 60 obs), annualized √365.
- Weights: w̃_i = s_i/σ_i; scale whole book so EWMA portfolio vol = 15%
  ann; cap Σw ≤ 1 (no leverage, long-only, no shorts).
- Band rebalancing: trade asset i only when |w_target − w_held| > 0.05;
  cost 0.35% fee + 10 bps slip on traded notional |Δw|.
- Trade (for PF/n): per-asset episode from w_i > 0 to w_i = 0.
- Gates: n≥100 episodes, PF>1.3, both halves>0, plateau = lookback sets
  {7,14,28}/{14,28,56}/{28,56,112} all net positive, bootstrap
  P(maxDD>40%)<10%, Sharpe ≥ BTC buy-hold Sharpe (hardest benchmark).
- Kill criterion: any gate fails → E6 falsified. No retune. ETH/SOL
  windows: evaluation #1 each; BTC window evaluation #4 (sizing/
  portfolio construction only — signal family unchanged since E4).
