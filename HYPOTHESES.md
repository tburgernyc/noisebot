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

### 2026-07-15 — E4-v3 evaluation (single registered run; log: logs/phase2_e4v3_e6_2026-07-15.log)
E4-v3 VERDICT: **FAIL on the pre-stated bar — E4-v2 stands.** GARCH(1,1)
sizing passed all absolute gates (n=167, PF 2.42, P(maxDD>40%)<10%,
Sharpe 1.22 ≥ bh) but was strictly WORSE than E4-v2's realized-vol
sizing: Sharpe 1.22 vs 1.38, final 4.56x vs 7.98x, maxDD equal at -26%.
The registered prior held: GARCH's complexity did not earn its keep for
vol TARGETING on this window. The YouTube video's one technical
contribution is hereby tested and declined. No retune.

### 2026-07-15 — E6 evaluation (single registered run; same log)
E6 VERDICT: **PASS — 7/7 gates** — n=327 episodes, WR 28.7%, PF 1.94,
final 4.72x, maxDD -31.2%, plateau {7,14,28}/{14,28,56}/{28,56,112} all
positive (4.59x/4.72x/6.00x), P(maxDD>40%)<10%, Sharpe 0.97 vs BTC
buy-hold 0.96 (cleared by a hair — logged as such).
Honest comparison ON THE RECORD: E6 (portfolio) underperforms E4-v2
(single-asset BTC) in-sample — Sharpe 0.97 vs 1.38 — because ETH/SOL
trends were weaker than BTC's and the assets are highly correlated.
E6's case is robustness (no single-asset selection risk), not in-sample
metrics. DECISION REGISTERED: both E4-v2 and E6 run Phase 4 shadow for
90 days in parallel; deployment choice (if any) is made on shadow
integrity + whichever construction's live behavior matches its backtest
recomputation — NOT on which had the prettier backtest.

---

## QC-AUDIT — REGISTERED 2026-07-16 (pre-data): QuantCrawler signal audit

Protocol locked BEFORE any signal is logged. Vendor backtests are
exhibits, not evidence; only forward signals count. Every QC signal is
logged at appearance via shadow_qc.py (append-only, hash-chained,
backfills excluded), adjudicated pessimistically against market data
(market entry at next bar open +5bps/side; stop-before-target in
ambiguous bars). DECISION RULE: n>=60 closed signals AND PF>=1.2 on
R-multiples -> registerable as a pipeline hypothesis; otherwise REJECT
and cancel subscription. No mid-audit rule changes.

## E7 — REGISTERED 2026-07-18 (pre-test): Perp funding-rate carry (standalone)

Economic rationale: perpetual-swap funding is paid by the crowded side —
persistently leveraged longs in crypto — to whoever takes the other side.
Harvesting it is compensation for warehousing inventory risk against
retail leverage demand: a structural payment stream, not a price
forecast. Mechanism family: CARRY — distinct from every falsified family
(always-on momentum, event-conditioned momentum, VWAP reversion) and
from the passing trend family (E4-v2/E6), whose signal is price-derived;
E7's signal is the funding print itself.

Rules (ALL fixed before any run):
- Universe: BTC, ETH, SOL USDT-margined perps. Funding source: Binance
  funding-rate history, 2020-01→2026-07 (8h prints; annualized =
  mean(8h rate) × 3 × 365).
- Signal at each daily close: trailing 3-day mean annualized funding F.
  F > +15% → SHORT 1 unit (collect funding); F < −15% → LONG 1 unit;
  else FLAT. Per asset, independently.
- Sizing: E4-v2 convention per asset — w_i = min(1, 0.15/σ_i), σ_i =
  30-day realized vol annualized √365, applied to |position|; book cap
  Σ|w_i| ≤ 1 with pro-rata scale-down (E6 convention). No leverage,
  no martingale.
- Fills: position changes at next daily open on traded notional |Δw|.
- Costs: 0.10% per side ALL-IN (taker + spread + slippage), flat across
  assets — registered pessimistic fixture. Funding P&L accrues from the
  actual historical 8h prints while the position is held.
- Trade for PF/n: per-asset episode from |w_i| > 0 to w_i = 0 (E6
  convention).
- Registered plateau parameter: funding threshold ±10% / ±15% / ±20% —
  all three must be net positive. (Lookback 3d, vol target 15%, and all
  cost numbers are FIXED, not swept.)
- Gates (all required): n ≥ 100 episodes; PF ≥ 1.2 — REGISTERED
  ADAPTATION below the standard 1.3, rationale: carry P&L is a
  high-frequency small-increment stream (structurally lower PF variance
  than trend's fat right tail), logged as such; both sample halves
  positive; plateau all > 0; bootstrap (10k paths, daily resample)
  P(maxDD > 40%) < 10%; ATTRIBUTION gate: cumulative funding-leg P&L > 0
  AND > |cumulative price-leg P&L| (else it is accidental trend, not
  carry → FAIL); CORRELATION gate: daily-return correlation with the E6
  backtest book ≤ 0.5.
- Data window: Binance funding 2020→2026 is FRESH — evaluation #1.
  Price marks partially REUSE the BTC/ETH/SOL daily window (BTC has 4
  prior evaluations, all trend-family). Recorded mitigations: (a) the
  signal is funding, not price — orthogonal mechanism; (b) the final 6
  months (2026-01→2026-07) are a ONCE-ONLY OOS segment: evaluated once,
  after the 2020→2025 body, results reported separately with their n.
  Yahoo 60-day window: not used (burned, QA-only).
- Kill criterion: ANY gate fails → E7 falsified on this window.
  Recorded and abandoned — no retune, no threshold search, no venue
  shopping.
- On pass: candidate SECOND sleeve alongside E4-v2/E6 — enters its own
  Phase 4 shadow (funding-sim verified against live prints; adaptation
  to be registered before shadow starts). NOT capital. Deployment-venue
  fees (US-regulated perps) must be re-verified in writing before any
  live sizing; Binance fixture is for evaluation only.

### 2026-07-18 — E7 evaluation (single registered run; log: logs/phase2_e7_2026-07-18.log)
Data: Binance monthly funding archives (226 files; BTC/ETH 2020-01→
2026-06-30, SOL 2020-09→2026-06-30; annualization interval-aware — 101
of 20,662 prints were 2h/4h emergency intervals). Machinery verified on
synthetic data before the run (test_e7.py, 6/6 incl. no-lookahead).
E7 VERDICT: **FAIL — 2/8 gates.** Body 2020-01→2025-12 at ±15%: n=129
episodes, WR 48.8%, PF 0.58, final 0.424x, maxDD -63.7%, Sharpe -0.69,
both halves negative. Plateau ±10/15/20 sum(ret) -1.12/-0.76/-0.58 —
all negative (n=205/129/123). Ruin gate FAIL. ATTRIBUTION gate FAIL and
decisive: funding leg +0.333 (real, positive) vs price leg -1.033 —
harvesting the payment cost 3x the payment. Passing gates: n>=100 and
corr(E6) = -0.486 (n=2,022 days). Once-only OOS 2026H1: 3 episodes,
-5.31% segment return, Sharpe -1.66 (n=181 days — small, as registered).
Read: the structural payment EXISTS (+33% cumulative funding capture
over 6 years) but it is fair-or-cheap compensation, not free money —
being short the crowded side in a market that mostly went up cost far
more in adverse price moves than funding paid. The carry is priced.
Kill criterion applies: E7 falsified. Recorded and abandoned — no
retune, no threshold search, no venue shopping. The negative E6
correlation is noted for the record but purchases nothing at PF 0.58.
Window ledger: Binance funding 2020→2026 evaluation #1 (burned);
BTC/ETH/SOL daily price marks reused (recorded above).

---

## E8-R — REGISTERED 2026-07-18 (pre-test): Intraday crypto trend continuation, coherent expression (ETHUSDT 15m)

Provenance: redesign of a public Jesse TEMA strategy after structural
audit. Original DISCARDED for: entry adverse to mechanism (fade-limit on
a momentum signal), tail-amputating fixed TP, collinear double filter
(ADX+CMO), 3× sizing error. All redesign choices fixed here, PRE-DATA;
any post-data change voids the entry.

Economic rationale: leveraged-positioning cascades — strong aligned
directional moves on 15m/4h force liquidations and momentum-chasing on
the same side, extending moves. Faster-clocked relative of the E4-v2/E6
underreaction family; the correlation gate adjudicates distinctness.
RECORDED RISKS (pre-stated): (a) TEMA periods 10/80 and 20/70 are
inherited from the public original and MAY have been tuned by its author
on overlapping ETH history — the plateau does not cover them; if E8-R
passes, this provenance caveat travels with the pass. (b) The ETHUSDT
15m 2022→2026 price path overlaps E6's ETH daily window (eval #1
burned there); granularity and mechanism are new, the overlap is not.

Rules (ALL fixed before any run):
- Signal on 15m bar close: LONG when TEMA(10) > TEMA(80) on 15m AND
  TEMA(20) > TEMA(70) on 4h AND ADX(14) > 35. SHORT mirror. CMO gate
  deleted (collinear with ADX by design audit, pre-data).
- Entry: next-bar open, adverse half-spread — with the flow. No fade
  limits.
- Initial stop: 3×ATR(14) from fill.
- Exit: Chandelier trail 4×ATR(14) from highest close since entry
  (mirror short); also exit on opposite signal. No fixed TP. 24/7 hold
  permitted; funding accrued while held.
- Size: fixed 1 unit — edge measurement only. Sizing is a SEPARATE
  future registration (E4-v2 precedent).
- Costs (pinned 2026-07-18, Tim's selection): 0.05% taker + 0.01%
  half-spread per side (6 bps/side all-in); funding from ACTUAL Binance
  ETHUSDT 8h prints over each holding period, sign-aware.
- Registered plateau (ALL cells must be net positive, never best-of):
  ADX gate ∈ {30, 35, 40} × trail ∈ {3.5, 4, 5}×ATR — 9 cells.
- Data: Binance ETHUSDT USDT-perp 15m klines (data.binance.vision,
  free — no Databento spend), 2022-01-01 → 2026-06-30. FRESH window at
  this granularity, evaluation #1 (overlap caveat above). Final 6
  months (2026-01-01 → 2026-06-30) once-only OOS segment, reported
  separately. Yahoo 60-day window untouched; daily crypto windows
  untouched.
- Prediction if TRUE: PF ≥ 1.2 net on n ≥ 150 fills; both halves
  profitable; WR < 50% with avg-win/avg-loss > 1.5 (skew signature — a
  trend system with high WR and small wins is doing something other
  than claimed); daily-return correlation with E6 sleeve ≤ 0.5.
- FALSIFIED if ANY: PF < 1.2; n < 150; either half negative; any
  plateau cell negative; corr(E6) > 0.5 (verdict: redundant expression,
  recorded as such); top 5 trades > 60% of net P&L (lottery, not edge).
- Decision rule: PASS → candidate sleeve; separate sizing registration
  before any deployment math; FundedNext funding-sim verification
  required in writing before that sleeve touches their MC. FAIL →
  recorded, abandoned, no re-tuning against this window ever.

### 2026-07-18 — E8-R evaluation (single registered run; log: logs/phase2_e8_2026-07-18.log)
Data: Binance Vision ETHUSDT perp 15m klines, 54 monthly archives,
157,632 bars 2022-01-01→2026-06-30; 7,119 actual funding prints.
Machinery verified pre-run on synthetic data (test_e8.py, 8/8 incl.
no-lookahead over 137 closed trades and completed-4h-bar isolation; a
TEMA init-transient bug was found and fixed on SYNTHETIC data before
the registered window was touched — warmup mask 3n→6n).
E8-R VERDICT: **FAIL — 3/7 gates.** Body 2022→2025 at (ADX>35, 4×):
n=951, WR 33.1%, PF 1.05 (gate ≥1.2 FAIL), net +1,061 USDT/unit,
half1 +267 / half2 +794 (both PASS). Plateau FAIL: 5 of 9 cells
negative (ADX30: -2042/-1263/+223; ADX35: -823/+1061/+2555; ADX40:
-335/-82/+707 — monotone improvement toward fewer, longer trades).
Top-5 concentration FAIL: 217% of net (the pre-declared lottery
signature — the entire net edge and more sits in 5 of 951 trades).
corr(E6) -0.008 (n=1,161 days) PASS. Once-only OOS 2026H1: n=126,
net -909 USDT/unit. FAIL.
Attribution: price leg +3,883 gross; costs -2,759 (71% of gross);
funding -64. The skew signature MATCHED prediction (WR<50%, W/L 2.13)
— the system is genuinely trend-shaped, but at 15m the per-trade edge
(~$4 gross/trade) is the same order as the $2.90 round-trip cost.
Read: same failure mode as E3 and the falsified MNQ family — the
15m-frequency effect, if any, is below friction; profitability drifts
toward the slowest cells (ADX40/5×, +707), pointing back at the daily
horizon where E4-v2/E6 already live. The cascade mechanism did not pay
at this clock. Kill criterion applies: E8-R falsified. Recorded and
abandoned — no re-tuning against this window ever (as registered).
Window ledger: ETHUSDT 15m 2022→2026 evaluation #1 (burned).

---

## E4-v2 → FundedNext DEPLOYMENT PLAN — REGISTERED 2026-07-16

MC on E4-v2's return stream vs Stellar 2-step rules (static 10% max
loss, 5% daily, +8%/+5% targets, no time limit): at 10% vol target,
P(pass both) ~90%, median ~9 months (in-sample-flattered; log:
logs/fundednext_mc_2026-07-15.log). BUY TRIGGER — all three required:
(1) 90-day shadow gate passes (signals_e4v2.jsonl, zero critical
errors, live matches recomputation); (2) signal is ON (r28>0) at
purchase; (3) firm rules verified in writing: BTC CFD weekend quoting
on MT5, EA add-on cost, inactivity-breach rule, Stellar consistency
rules, profit split. Registered sizing: vol target 10%. One account.

---

## H3-EXT — EXTERNAL RECORD, imported 2026-07-18: AMD/IFVG EURUSD intraday (SMC/ICT family)

PROVENANCE (read first): registered AND evaluated in a PARALLEL cloud
session that worked from a stale snapshot of this project — NOT in
this repo. Its numbers cannot be independently re-derived here (the
artifacts — AMD_IFVG_SPEC.md, amd_ifvg_signals.py, amd_ifvg_backtest.py,
test_amd_ifvg.py 10/10, run_phase2.py, phase2_report.json,
trades_full.csv — live in that session's workspace, delivered to Tim
directly). Imported because failed tests stay on the record regardless
of where they ran. The "H3" ID is that session's own numbering (it had
migrated the lost H1/H2 as registered-untestable); namespaced here as
H3-EXT to avoid collision with the canonical E-series. Source document
archived verbatim at imports/STATE_cloud-session_2026-07-19.md.

- Mechanism claimed: SMC/ICT "AMD cycle" (accumulation–manipulation–
  distribution session structure) with inverse fair-value-gap (IFVG)
  entries on EURUSD, prop-firm risk shell; MQL5 was the eventual
  target. Distinct family from everything in the E-series: discretionary-
  style intraday FX structure, mechanized.
- Evaluation (per that session's Phase 2 gate, single run): Dukascopy
  EURUSD M5, 2023-07-01 → 2026-06-30.
- VERDICT: **FAIL.** PF 0.657, n=297. Both halves negative. All 5
  plateau variants negative. Loses GROSS of costs (−0.59 pips/trade
  before commissions) — not a friction failure, a sign failure. WR 3.2
  standard errors below breakeven. Non-negotiable #1 held: no MT5/MQL5
  code was built.
- Standing: SEVENTH falsified family — SMC/ICT intraday FX structure —
  alongside always-on momentum, ORB, VWAP reversion, last-hour flow,
  funding carry, fast crypto trend. Recorded and abandoned; any future
  SMC/ICT-flavored registration must cite this record and explain why
  its mechanism escapes a gross-of-costs sign failure.
- Window ledger: Dukascopy EURUSD M5 2023-07→2026-06 — evaluation #1,
  burned (externally). If EURUSD M5 data ever enters this repo, that
  window counts as mined.
- Trust caveat: unverified externally-run numbers. If any decision were
  ever to hinge on H3-EXT being *wrong* (it is a FAIL, so none should),
  re-derivation from the delivered artifacts is required first.

---

## WINDOW-LEDGER NOTE — 2026-07-19: PB4 dataset pulled, window consumed EXTERNALLY

Databento GLBX.MDP3 ohlcv-1d, parent symbology, expiry ladders for 9
CME roots (ES NQ 6E 6B 6A 6J GC SI CL), 2019-01-01 → 2026-07-01.
Pulled 2026-07-19 by Tim locally ($6.66, quoted before spend; cap $25);
files in ~/pb4_pull/pb4_out/, verified here (9 CSVs, all spans
2019-01→2026-06-30, multi-contract ladders; note: parent symbology
includes calendar-spread instruments — outrights must be filtered
downstream). Feeds a hypothesis called "PB4" being evaluated in a
SEPARATE Claude session — NOT registered in this file. Ledger status:
**this window's evaluation #1 is consumed externally by PB4.** Any
future registration here against daily futures ladders 2019→2026 must
count that mining and cite whatever PB4 record Tim imports (as was
done for H3-EXT). Overlap caveat: ES daily also appears in
data/es_zn_1d.csv (E5, 1 evaluation) — partial reuse for ES.

---

## COMMODITY / FX TERM-STRUCTURE FAMILY — REGISTERED 2026-07-23 (E9, E11, E12)

Provenance: deep-research sweep (2026-07-23; 108 agents, 25 claims
adversarially verified, 19 confirmed / 6 killed; report archived at
tasks/wt914flw4.output). The sweep converged on ONE surviving family
distinct from our seven falsified families — commodity/FX futures
term-structure risk premia. Rejected on verification or on our own
cost bar: Goldman-roll front-run (arbitraged away), leveraged-VIX-ETP
flow (unprofitable after costs), naive long-only roll yield (now a
"tax"), social-sentiment (behavioral, refuted 0-3), crypto term-basis
(refuted 0-3). A specific "commodity carry nets Sharpe 1.12 after
costs" claim was REFUTED 0-3 — carried as a prior-against below.

E10 INTENTIONALLY RESERVED / UNUSED: it was to be cross-sectional
commodity term-structure carry; DROPPED pre-registration in favour of
E12 (FX carry) — better small-account implementability and it breaks
the commodity-family concentration. Recorded so the gap in numbering
is explicit, not an error.

SHARED-WINDOW MULTIPLICITY (disclosed up front): E9 and E11 share the
SAME commodity daily-futures price window for P&L (E11's signal is free
CoT positioning, but its returns are computed on E9's prices) — that
window is therefore mined TWICE; both are registered, both evaluated
once, neither may be reshuffled after seeing data. E12 uses a separate
FX futures window.

IMPLEMENTABILITY (registered, applies to all three): the full
cross-section is backtested at 1 unit for EDGE MEASUREMENT ONLY.
Whether the edge survives reduction to the tradable CME-micro subset
(MGC/MCL/MHG… for commodities; M6E/M6A/M6B for FX) is a SEPARATE
future registration — E4-v2 precedent. A pass here is a measured edge,
never a deployment claim.

MACHINERY-FIRST (registered): for each, no-lookahead + roll-no-splice +
tercile-construction unit tests are written and must pass on SYNTHETIC
data BEFORE the registered window is touched (E7/E8 precedent).

---

## E9 — REGISTERED 2026-07-23 (pre-test): Commodity basis-momentum (cross-sectional, monthly)

Economic rationale: compensated risk premium for LIQUIDITY PROVISION.
Boons & Prado (Journal of Finance 74(1):239-279, 2019) build a signal
from the difference between momentum in the first-nearby vs
second-nearby futures; it earns 18.38% p.a. (t=6.73), Sharpe ~0.9 over
21 commodities since 1959, and is shown INCONSISTENT with storage,
inventory, and hedging-pressure — it captures returns to speculators
who absorb supply/demand imbalances when intermediaries' market-
clearing ability is impaired. Mechanistically distinct from all seven
falsified families: a curve curvature/slope-change signal, not price
trend (always-on/ORB/fast-crypto momentum), not carry (E7 perp
funding), not VWAP reversion, not last-hour gamma, not SMC/ICT, not
month-end rebalancing.
Priors-against (registered): (a) headline figures are gross, in-sample,
60+ years; (b) 2024-2025 work (Uhl 2025; QuantPedia commodity-factor
crowding; Fan 2025) documents attenuation/crowding → expect live <<
in-sample; (c) implementability gap (above).

Universe (FIXED, 14 GLBX roots, chosen for a liquid second-nearby;
ICE softs deliberately excluded to stay one-dataset): CL, NG, HO, RB,
GC, SI, HG, ZC, ZW, ZS, ZL, ZM, LE, HE.

Rules (ALL fixed before any run):
- Continuous series, NO SPLICE (per constitution): first-nearby = the
  nearest contract NOT in its delivery month; second-nearby = the next
  expiry after that. Roll on the last trading day of the month before
  the nearby enters its delivery month. Each day's return is taken
  WITHIN a single contract; roll days use the held contract's return
  only — never a cross-contract splice.
- Signal at each month-end: BM_i = mom_nearby_i − mom_2ndnearby_i,
  where mom = trailing 12-month cumulative within-contract total
  return of the (resp.) nearby / second-nearby series (no skip month).
- Cross-sectional rank of BM_i across the 14 roots each month-end:
  LONG the top tercile, SHORT the bottom tercile, equal-weight within
  tercile. Middle tercile flat.
- Sizing: scale the whole long/short book to 15% annualized portfolio
  vol (EWMA λ=0.94 on daily book returns, min 60 obs, √252); gross
  exposure capped Σ|w_i| ≤ 2.0 with pro-rata scale-down. No leverage
  beyond that.
- Rebalance monthly (last trading day); fill at NEXT session open,
  1-tick adverse. Full rebalance, no bands.
- Costs: pessimistic flat fixture 5 bps/side ALL-IN on traded notional
  |Δw_i| (dominates true 1-tick + $2.50/ct RT for these liquid roots;
  registered as the pessimistic fixture, logged as such).
- Trade/episode for PF and n: per-commodity episode from position open
  (enters a tercile) to close (exits/flips) — E6 convention.
- Registered plateau (ALL must be net positive, never best-of):
  momentum lookback 6 / 12 / 18 months. Tercile breakpoint, vol
  target, gross cap, and cost fixture are FIXED, not swept.

Gates (E6-adapted portfolio set, ALL required): n ≥ 100 episodes;
PF > 1.3; both sample halves (by calendar time) net positive; plateau
all > 0; bootstrap (10k paths, daily book-return resample) P(maxDD >
40%) < 10%; Sharpe(net) ≥ Sharpe of the equal-weight LONG-ONLY basket
of the same 14 nearby series vol-targeted to 15% on the identical
window (hardest honest benchmark — must beat passive long commodity
beta).

Prediction if TRUE: PF > 1.3 net on n ≥ 100 episodes; both halves
positive; plateau all positive; beats passive long-only commodity
Sharpe. FALSIFIED if ANY gate fails.

Data window: Databento GLBX.MDP3 ohlcv-1d, parent symbology, 14 roots,
2010-06-06 → 2026-06-30 — FRESH, evaluation #1 on commodity daily
ladders in this repo. (Window AMENDED 2026-07-23 from a mistaken
2005-01-01 start to the dataset's real availability start 2010-06-06,
confirmed by metadata.get_cost; amended PRE-DATA, zero results seen —
not a post-hoc window choice. ~16 yrs, ample for n≥100.) Cost quoted before pull; key stays in env.
Overlap disclosure: GC/SI/CL 2019→2026 sub-span overlaps the PB4
window (mechanism unknown). Mitigations recorded: (a) E9's signal is
basis-momentum (curvature), almost certainly orthogonal to whatever
PB4 is; (b) 2010-2019 is clean for those three (over half the sample); (c) the other 11 roots are fully fresh; (d) PB4's own CSVs are
NOT reused — a clean pull is taken. When Tim imports the PB4 record,
reconcile.

Kill criterion: any gate fails → E9 falsified on this window. No
retune, no universe reshuffle, no threshold/lookback search.

### 2026-07-24 — E9 evaluation (single registered run; log: logs/phase2_e9_2026-07-24.log)
E9 VERDICT: **FAIL — 1/6 gates.** Commodity basis-momentum, 14 GLBX
roots 2010-06→2026-06, tercile L/S, 15% vol target, 5 bps/side.
- n = 294 episodes (PASS, gate ≥100).
- PF 1.081 (gate >1.3, FAIL).
- Both halves: half1 −0.254 / half2 +0.327 (half1 negative, FAIL).
- Plateau lookback {6 / 12 / 18} = +2.404 / −0.126 / −0.351 — only the
  6-month cell positive (gate "all > 0", FAIL).
- Bootstrap P(maxDD>40%) 0.845 (gate <0.10, FAIL).
- Sharpe(net) 0.026 vs long-only commodity benchmark 0.312 (FAIL —
  worse than passive commodity beta).
- final equity 0.874 (net loss over the window), realized maxDD −52.0%.
Read: the liquidity-provision premium of Boons & Prado (18.38% p.a.
in-sample, 21 commodities since 1959) does NOT survive on the liquid
14-root CME universe 2010-2026 at honest costs — consistent with the
registered priors-against (gross / in-sample / 60-yr inflation +
documented 2024-25 crowding/attenuation). The plateau's single positive
cell (lookback 6) is NOT a rescue: the registered plateau demands ALL
cells positive precisely to catch a horizon-fragile fit; adopting the
6-month cell post-hoc would be textbook sweep-and-select and is
forbidden. Kill criterion applies: E9 falsified on this window.
Recorded and abandoned — no retune, no universe reshuffle, no lookback
search. EIGHTH falsified family (commodity basis-momentum).
Window ledger: commodity daily ladders (14 GLBX roots) 2010-06→2026-06
evaluation #1 CONSUMED (burned). E11 shares this price window — a
disclosed second registered use (positioning signal, not price).

---

## E11 — REGISTERED 2026-07-23 (pre-test): Commodity hedger-positioning pressure (CFTC CoT, cross-sectional)

Economic rationale: the cleanest MANDATED flow in the sweep. Commercial
hedgers (producers/consumers) are structurally FORCED to hedge; long
speculators must be compensated to absorb the net short-hedging
imbalance (Keynes/Cootner/Hirshleifer normal-backwardation; De Roon-
Nijman-Veld; Basu & Miffre 2013; Fernandez-Perez/Fuertes/Miffre 2018,
"Hedging Pressure Everywhere"). The signal is POSITIONING, not price —
maximally orthogonal to every price-based family we have falsified.
Prior-against (registered): single-sort hedging pressure is construction-
dependent and can be WEAK (Fan & Zhang 2024, J. Futures Markets:
average 1.5%, Sharpe 0.24 standalone). The bet is that the FFM-2018
broad-universe, normalized, vol-targeted construction clears the bar on
2006→2026; if it does not, E11 is falsified — no rescue by adding
filters or switching to a double-sort after the fact.

Universe (FIXED): the same 14 roots as E9 (CoT reported for all).

Rules (ALL fixed before any run):
- Signal from CFTC Disaggregated CoT (weekly): hedging pressure
  HP_i = (ProducerMerchantProcessorUser long − short) /
  (Producer... long + short), i.e. commercial net position normalized
  to [−1, +1], averaged over the trailing 13 weekly reports. Hedgers
  most NET SHORT (most negative HP) → speculators most compensated.
- Cross-sectional rank of HP_i each month-end (using the latest CoT as
  of that date, release-lag respected — Tuesday snapshot, Friday
  release, no lookahead): LONG the bottom tercile of HP (hedgers most
  net short), SHORT the top tercile (hedgers most net long). Middle
  flat.
- Sizing, rebalance, fills, costs, trade/episode: IDENTICAL to E9
  (15% vol, Σ|w|≤2, monthly, next-open 1-tick adverse, 5 bps/side,
  per-commodity episode). Returns computed on E9's commodity price
  series.
- Registered plateau (ALL must be net positive): HP averaging window
  4 / 13 / 26 weeks. Normalization, tercile breakpoint, vol target,
  cost fixture FIXED.

Gates (E6-adapted set, ALL required): n ≥ 100 episodes; PF > 1.3; both
halves positive; plateau all > 0; bootstrap P(maxDD>40%) < 10%;
Sharpe(net) ≥ same long-only-commodity benchmark as E9; PLUS a
DISTINCTNESS gate: daily-return correlation with the E9 book ≤ 0.5
(if E11 is just E9 in disguise it earns nothing new → recorded as
redundant).

Prediction if TRUE: PF > 1.3 net, n ≥ 100, both halves positive,
plateau all positive, corr(E9) ≤ 0.5. FALSIFIED if ANY gate fails
(explicitly including corr(E9) > 0.5 → verdict "redundant with E9").

Data window: CFTC CoT (Disaggregated, available from 2006) aligned to
the price-bounded evaluation window 2010-06-06 → 2026-06-30 — FRESH
positioning window, never used here (evaluation #1). The backtest runs
only where BOTH CoT and price exist → 2010-06 → 2026-06. Prices REUSE
E9's commodity window
(disclosed shared-window multiplicity above — that window is mined
twice by design; both single-evaluation). Free data for the signal;
no incremental Databento spend beyond E9's pull.

Kill criterion: any gate fails → E11 falsified. No retune, no filter
additions, no post-hoc double-sort.

### 2026-07-24 — E11 evaluation (single registered run; log: logs/phase2_e11_2026-07-24.log)
E11 VERDICT: **FAIL — 2/7 gates.** Commodity hedger-positioning (CFTC
CoT, FFM-2018 hedging pressure), 14 GLBX roots 2010-06→2026-06, tercile
L/S, 15% vol, 5 bps/side, release-lag 4d.
- n = 146 episodes (PASS, ≥100).
- corr(E9) −0.008 (PASS — genuinely orthogonal to price basis-momentum;
  the positioning mechanism IS distinct, as registered).
- PF 1.097 (gate >1.3, FAIL).
- Both halves: half1 −0.018 / half2 +0.381 (half1 negative, FAIL).
- Plateau HP window {4 / 13 / 26 wk} = −0.210 / +0.158 / +0.373
  (4-week cell negative, gate "all > 0" FAIL).
- Bootstrap P(maxDD>40%) 0.766 (gate <0.10, FAIL).
- Sharpe(net) 0.124 vs long-only commodity benchmark 0.312 (FAIL).
- final equity 1.158, realized maxDD −56.3%.
Read: the mechanism is REAL and DISTINCT — hedgers net-short across all
14 roots as normal-backwardation predicts, and the book is essentially
uncorrelated with E9 (−0.008) — but the compensation is too small and
too crash-prone to clear the bar at honest costs. The registered
prior-against held (Fan & Zhang 2024: single-sort HP Sharpe 0.24; our
broad vol-targeted construction reached only 0.12 net). Same signature
as E5 (month-end) and E7 (funding carry): a genuine structural premium
that is an institutional edge, not a retail one. The long-window plateau
cells (13/26 wk) being positive is NOT a rescue — the 4-wk cell fails
and even the positive cells sit at PF ~1.1, below benchmark. Kill
criterion applies: E11 falsified. Recorded and abandoned — no retune, no
filter additions, no post-hoc double-sort. NINTH falsified family. The
corr(E9) pass means E11 is INDEPENDENTLY dead, not redundant with E9.
Window ledger: commodity price window 2010-06→2026-06 second (final)
registered use consumed (disclosed at registration); CoT positioning
2010-2026 evaluation #1 burned.

---

## E12 — REGISTERED 2026-07-23 (pre-test): FX carry via futures term structure (cross-sectional, monthly)

Economic rationale: the FX carry risk premium — compensation for
currency crash risk and funding-liquidity risk (Lustig-Roussanov-
Verdelhan 2011; Brunnermeier-Nagel-Pedersen 2009). High-interest-rate
currencies trade at a forward discount; by covered interest parity the
interest differential is embedded in the FX futures curve (near vs
deferred quarterly), so carry is read straight off the term structure —
the SAME machinery as E9, applied to a different asset class. Distinct
from the record: NOT E7 (crypto perpetual-funding carry — different
driver and asset), NOT H3-EXT/SMC-ICT (intraday FX price STRUCTURE —
unrelated mechanism and horizon; cited per the standing rule that any
FX registration references that falsified record). Forex added at Tim's
request; it also breaks E9/E11's commodity-family concentration and is
the most small-account-implementable of the three (deep, cheap CME FX
micros).
Prior-against (registered): FX carry is famously crash-prone (negative
skew — "picking up pennies in front of a steamroller"); the
P(maxDD>40%) ruin gate is the live test, exactly the gate E4 failed.
"Carry" broadly is a concept the program has touched (E7) — flagged,
though the driver here is distinct.

Universe (FIXED, 8 USD-quoted CME FX futures): 6E (EUR), 6J (JPY),
6B (GBP), 6A (AUD), 6C (CAD), 6S (CHF), 6N (NZD), 6M (MXN).

Rules (ALL fixed before any run):
- Carry_i at each month-end = annualized log(front / second-deferred
  quarterly)/Δt for currency i, sign-normalized so that a currency at
  a forward DISCOUNT (higher local short rate) has POSITIVE carry.
  Roll/no-splice handled as in E9 (within-contract returns; the
  quarterly-cycle roll uses the held contract only).
- Cross-sectional rank each month-end: LONG the top 3 carry currencies,
  SHORT the bottom 3; middle 2 flat. (Fixed 3/3 given only 8 names —
  the FX analog of a tercile.)
- Sizing: book scaled to 15% annualized vol (EWMA λ=0.94, min 60 obs,
  √252); gross Σ|w_i| ≤ 2.0, pro-rata scale-down.
- Rebalance monthly (last trading day); fill next-session open, 1-tick
  adverse. Costs: pessimistic flat 3 bps/side ALL-IN on |Δw_i| (liquid
  FX futures; registered fixture).
- Trade/episode for PF and n: per-currency episode from open to
  close/flip.
- Registered plateau (ALL must be net positive): carry smoothing
  1 / 3 / 6-month trailing average. Long/short count (3/3), vol target,
  gross cap, cost fixture FIXED.

Gates (E6-adapted set, ALL required): n ≥ 100 currency-episodes;
PF > 1.3; both halves positive; plateau all > 0; bootstrap
P(maxDD>40%) < 10%; Sharpe(net) ≥ Sharpe of an equal-weight passive
long-all-8-vs-USD basket (the "FX beta") vol-targeted to 15% on the
identical window.

Prediction if TRUE: PF > 1.3 net, n ≥ 100 episodes, both halves
positive, plateau all positive, clears the ruin gate despite carry's
negative skew, beats passive FX beta. FALSIFIED if ANY gate fails —
the ruin gate is the pre-declared most-likely failure.

Data window: Databento GLBX.MDP3 ohlcv-1d, parent symbology, 8 FX
roots, 2010-06-06 → 2026-06-30 — FRESH FX window, evaluation #1.
(Window AMENDED 2026-07-23 from 2005 to the dataset start 2010-06-06,
pre-data, same as E9.) Cost quoted before pull. Overlap disclosure: 6E/6B/6A/6J 2019→2026 sub-span
overlaps the PB4 window (mechanism unknown); mitigations mirror E9 —
signal is FX carry (orthogonal to plausible PB4 mechanisms), 2010-2019
clean, 6C/6S/6N/6M fully fresh, PB4 CSVs not reused. Reconcile on PB4
import.

Kill criterion: any gate fails → E12 falsified on this window. No
retune, no universe change, no threshold search.

### 2026-07-24 — E12 evaluation (single registered run; log: logs/phase2_e12_2026-07-24.log)
E12 VERDICT: **PASS — 6/6 gates.** FX carry via futures term structure,
8 CME FX roots 2010-06→2026-06, long 3 / short 3, 15% vol, 3 bps/side,
carry smoothing 3m.
- n = 115 currency-episodes (PASS, ≥100 — just clears).
- PF 1.724 (PASS >1.3).
- Both halves: half1 +0.093 / half2 +0.398 (both PASS).
- Plateau smoothing {1 / 3 / 6 mo} = +0.507 / +0.546 / +0.654 — ALL
  positive AND monotone increasing (a robust plateau, unlike E9/E11's
  single fragile cell).
- Bootstrap P(maxDD>40%) 0.038 (PASS <0.10 — this was the PRE-DECLARED
  likely-failure gate; vol-targeting + 3/3 diversification tamed carry's
  negative skew).
- Sharpe(net) 0.334 vs passive long-FX benchmark −0.092 (PASS).
- final equity 1.546 (~+54.6% over ~16 yr), realized maxDD −23.7%.
HONEST CAVEATS ON THE PASS (do not let a green verdict hide these):
(1) Sharpe 0.334 is MODEST (E4-v2 1.38, E6 0.97); and the benchmark it
beat is NEGATIVE (passive long-FX lost as USD strengthened 2010-2026),
so that gate was a low bar — the ABSOLUTE edge is small. (2) n=115 just
clears 100. (3) PB4 OVERLAP: 6E/6B/6A/6J 2019→2026 overlaps the unknown
PB4 window; 2010-2019 is clean and 6C/6S/6N/6M fully fresh, but if PB4
is FX carry this is partially contaminated — reconcile on PB4 import.
(4) early FX years had a sparse second-nearby → thin cross-section
pre-2012.
DECISION (E4-v2/E6 precedent): a PASS means PROCEED TO INDEPENDENT AUDIT
then Phase-4 shadow validation — NOT capital, and NO gate marker yet.
Next: gate-auditor re-derivation from scratch in a clean context BEFORE
any shadow registration. If the audit confirms, register a 90-day daily
shadow (FX carry signal + weights logged, live matching recomputation)
adapted as E4-v2's was; deployment math and US-regulated-venue fees are
SEPARATE future registrations. Kill criterion note: no retune is
permitted regardless of audit outcome — audit either confirms the pass
or finds a defect that voids it.
Window ledger: FX daily ladders (8 GLBX roots) 2010-06→2026-06
evaluation #1 CONSUMED (burned).

#### 2026-07-24 — E12 INDEPENDENT GATE AUDIT (gate-auditor, clean re-derivation)
VERDICT: **CONFIRMED PASS — stands WITH TWO SERIOUS CAVEATS; no defect
voids it.** The auditor re-derived every gate from the raw CSVs in its
own script; all 6 reproduce EXACTLY. Failure-mode hunt: sign CLEAN
(AUD/NZD/MXN long, JPY/CHF/EUR short — textbook carry; book is
USD-neutral so the edge is cross-sectional carry, not USD drift/trend);
lookahead CLEAN (real-data truncation invariance = 0.000e+00; weights
effective strictly after t; vol estimate shifted); costs CHARGED and
if anything over-charged; no fabricated returns.
- **CAVEAT A — the ruin-gate pass is LITERAL-ONLY (corrects this
  session's wrong narrative).** P(maxDD>40%)=0.038 passed NOT because
  "vol-targeting tamed the skew" (that claim above is WRONG) but because
  the gross cap Σ|w|≤2.0 binds on 96.6% of days, holding the book at
  ~7.4% realized vol — the 15% target is INACTIVE. Re-scaled to the
  registered 15% target the SAME book gives P(maxDD>40%)=0.557,
  maxDD −45.5% — a catastrophic FAIL. Faithful to the (cap-inclusive)
  registered rule, so not a coding defect, BUT the 0.038 does NOT
  license deployment at 15% vol. At cap-limited sizing the book earns
  ~2.5%/yr (Sharpe 0.334 × 7.4% vol) — crash-safe but low-return.
- **CAVEAT B — edge concentrated in the PB4-overlap window.** ~84% of
  P&L is 2019–2026 (Sharpe 0.710); clean 2010–2018 is FLAT (sum +0.078,
  Sharpe 0.089). The recent window overlaps unresolved PB4 on 4/8 names
  (incl. AUD, the largest carry name). Combined with absolute Sharpe
  0.334 and n just clearing 100, the margin is thin.
- Minor: episode_pnl used a hard-coded 5.0 bps (E12 registered 3.0) —
  CONSERVATIVE, made PF 1.724 vs 1.756; fixed post-audit, E12 NOT
  re-run (kill criterion). Signal uses second-NEAREST (next serial
  month, Δt≈1mo) not the literally-written "second-deferred quarterly";
  sign correct and annualized, but a deviation from the spec text.
  Author's "sparse early cross-section" caveat was OVERSTATED (8
  currencies present almost every month).
NET: a CONFIRMED but MARGINAL pass — real cross-sectional FX carry,
correctly built, but (A) not crash-safe at deployment sizing and (B)
edge is a recent-window, PB4-overlapping phenomenon. NO gate marker.
Same binding constraint as E4/E5: the signal is real; at safe sizing
the return is too small to matter for a small account. Next step is
PB4 reconciliation, NOT shadow registration, unless Tim decides the
low-return crash-safe version is worth shadowing anyway.
- Window AMENDED pre-data to 2010-06-06 start (GLBX.MDP3 availability;
  get_cost confirmed 2010-06-06). Applies to E9, E11, E12.
- Commodity daily ladders (14 GLBX roots) 2010-06→2026: reserved for
  E9 (eval #1) and E11 (shares the price window — mined twice,
  disclosed). Quoted $41.43.
- FX daily ladders (8 GLBX roots) 2010-06→2026: reserved for E12
  (eval #1). Quoted $2.20.
- Both pulls FRESH; GC/SI/CL and 6E/6B/6A/6J carry a 2019→2026
  PB4-overlap caveat (recorded per-entry). Quote total $43.63 of ~$100
  credit; Tim authorized discretionary spend 2026-07-23.

---

## E14 — REGISTERED 2026-07-24 (pre-test): Threshold (band-breach) 60/40 rebalancing pressure, equity leg (MES)

Provenance: 2026-07-24 focused deep-research sweep (106 agents, 25
claims adversarially verified; report tasks/wt2kwaacd.output). All four
seed candidates were KILLED on their own evidence — (A) overnight equity
drift documented DEAD post-2021 by its NY-Fed discoverers; (B) VIX/VX
carry ruinous + no micro contract; (C) crypto cross-sectional collapses
to 5-min reversal; (D) month-end FX fix flow sub-friction + 72% reverts
by next noon. The ONE distinct, micro-expressible lead that survived:
institutional 60/40 THRESHOLD rebalancing (Harvey-Mazzoleni-Melone 2025,
"The Unintended Consequences of Rebalancing"), separately measured from
the calendar signal we already falsified as E5.

Economic rationale (who is FORCED): balanced / target-date / 60-40
mandates rebalance not only on the calendar (E5) but on THRESHOLD
breaches — when the equity weight drifts past a tolerance band, the
mandate FORCES a rebalancing trade regardless of date: sell the
outperformer, buy the underperformer. HMM-2025 measure the threshold
signal separately: 1-SD → ~16 bps next-day equity reversal (opposite
~4 bps in bonds), reverting within two weeks; explicitly "a by-product
of mandates that likely conveys little information about fundamentals."
Distinct from all nine falsified families (a calendar/threshold-forced
allocation flow, not price trend/reversion/carry/gamma/positioning).

EXPLICIT E5 RELATIONSHIP (constitution-required — E5 is falsified; any
rebalancing-flavored registration must cite it and explain escape):
E5 = CALENDAR month-end rebalancing (ES), FALSIFIED — real but
sub-friction (PF 1.06, n=771, ~$2.85/trade, ruin gate 86.8%). E14 is
NOT an E5 retune: it is the paper's OTHER, separately-measured signal
with a DIFFERENT TRIGGER (band-breach, not date) that E5 did not
register or test. E5 fired on every month-end regardless of drift —
mostly on tiny divergences, which is precisely why its per-trade edge
was microscopic. E14 fires ONLY after a large drift breaches a band —
conditioning the forced flow on HIGH-MAGNITUDE events, so the per-trade
edge should be materially larger. That magnitude-conditioning is the
registered bet. IF E14 ALSO FAILS, the mandated-rebalancing family is
CLOSED (calendar + threshold both dead) — no third variant.

Rules (ALL fixed before any run):
- Data: ES.v.0 + ZN.v.0 daily, data/es_zn_1d.csv, 2010-06-07 →
  2026-07-14. Equity leg = ES; bond leg = ZN. DISCLOSED SECOND
  registered use of E5's window (signal differs entirely; window mined
  twice, both single-eval; E9/E11 shared-window precedent).
- Returns: close-to-close on the continuous series. Roll days handled
  per constitution — a 1-day trade (enter close t, exit close t+1) is
  EXCLUDED if a roll falls between t and t+1 (no cross-contract splice
  in a trade's P&L); roll dates from the .v.0 instrument_id change.
- Synthetic 60/40 book: start w_eq=0.60, w_bd=0.40 at sample start;
  each day the weights drift by realized ES/ZN close-to-close returns
  (no contributions/withdrawals); RESET to 60/40 at each rebalance.
- Trigger at close t: rebalance FIRES when |w_eq,t − 0.60| ≥ δ. On
  fire: equity-leg signal d = −sign(w_eq,t − 0.60) (short the overweight
  leg, with the forced flow; long if equity underweight). Reset book to
  60/40 after firing.
- Trade (deployable expression): EQUITY LEG on MES ($5/pt) — where ~16
  of the 20 bps sits, and the flagship micro. Enter close t, exit close
  t+1 (MOC-style), 1-tick (0.25 = $1.25 on MES) adverse each side +
  $2.50/ct RT. Consecutive triggers chain as separate 1-day trades.
  The ES/ZN PAIR is measured and reported as corroboration only; the
  tradeable claim is MES-only (no liquid micro bond leg exists).
- Registered plateau (ALL must be net positive, never best-of): band
  δ ∈ {0.03, 0.04, 0.05}. Hold (t+1), reference weight 0.60, and the
  cost fixture are FIXED, not swept.

Gates (E5-adapted set, ALL required): n ≥ 100 trigger trades;
PF > 1.3; both sample halves (by calendar time) net positive; plateau
all > 0; bootstrap (10k paths, daily 1-day-trade resample)
P(maxDD > $2,500/ct) < 10% (overnight holds → NOT prop-compatible,
IBKR-account edge — identical ruin gate to E5 for comparability).

Prediction if TRUE: PF > 1.3 net on n ≥ 100 trigger trades; both halves
positive; plateau all positive; ruin gate < 10%. FALSIFIED if ANY gate
fails.

Registered priors-against: (a) same ~16 bps magnitude as falsified E5 —
sub-friction death is a live risk; (b) threshold triggers are
infrequent, so n ≥ 100 MAY NOT be reached over 16 years — a legitimate
falsification if so, NOT a reason to loosen the band post-hoc;
(c) HMM-2025 coefficients are in-sample predictive regressions
1997–2023, not net tradable returns.

Machinery-first (registered, E7/E8/E9 precedent): no-lookahead +
trigger-construction + book-drift + roll-exclusion unit tests written
and passing on SYNTHETIC data BEFORE the registered window is touched.

Decision rule: PASS → candidate sleeve → Phase 4 shadow (adapted as
E4-v2's was), NEVER straight to capital; deployment math and
US-regulated-venue specifics are separate future registrations. FAIL →
recorded and abandoned; mandated-rebalancing family CLOSED; no retune,
no band search, no hold search, no third variant ever.

Window ledger: es_zn_1d.csv 2010-06→2026-07 — second registered use
(first was E5, calendar signal). No new data, no Databento spend.

### 2026-07-24 — E14 evaluation (single registered run; log: logs/phase2_e14_2026-07-24.log)
Machinery verified first on SYNTHETIC data (test_e14.py, 11/11: roll-safe
returns, trigger direction, sub-band silence, exact P&L, roll exclusion in
isolation, book reset, no-lookahead truncation invariance) BEFORE the
window was touched.
E14 VERDICT: **FAIL — 4/6 gates.** Threshold band-breach 60/40
rebalancing, ES/ZN 2010-06→2026-07, equity leg on MES, $2.50 RT + 1 tick.
- n = **17** trigger trades at the main band δ=0.04 (gate ≥100, **FAIL**) —
  28 at δ=0.03, 17 at δ=0.04, 14 at δ=0.05 over 16 YEARS (≈1 trade/yr).
- PF 1.350 (PASS, >1.3).
- half1 +$1,408 / half2 −$891 (half2 negative, **FAIL**).
- Plateau δ{0.03/0.04/0.05} = +$1,322 / +$516 / +$134 — all positive
  (PASS "all>0"), monotone-decreasing (wider band → fewer trades, friction
  eats the smaller sample).
- P(maxDD>$2,500/ct) 4.3% (PASS, <10%); realized maxDD −$1,338/ct.
READ — this is an **UNDERPOWERED fail, a DIFFERENT death from E5, not the
sub-friction wall.** The threshold rule simply does not FIRE often enough
to be a standalone retail strategy: ~1 trade/year is not a strategy for a
$2–5k account regardless of edge sign (~$30/trade × ~1/yr ≈ nothing). At
n=17 the positive PF and all-positive plateau are NOISE, not evidence. The
registered prior-against (b) — "threshold triggers are infrequent, n≥100
MAY NOT be reached … NOT a reason to loosen the band post-hoc" — is exactly
what happened; loosening δ further or holding longer or widening the
universe to manufacture triggers is FORBIDDEN (sweep/retune). Kill
criterion applies: E14 falsified. **TENTH falsified family, and per the
registration the MANDATED-REBALANCING FAMILY IS NOW CLOSED** — calendar
(E5: real but sub-friction) + threshold (E14: too rare to power a test or
matter at retail) are both dead. No third variant, no band search, no hold
search, ever.
Window ledger: es_zn_1d.csv 2010-06→2026-07 second registered use consumed
(disclosed at registration). No Databento spend.

## E20 — REGISTERED 2026-07-29 (pre-test, BLOCKED — no data source): Tokenized-equity vs cash-equity oracle basis mean-reversion (single-name)

Provenance: brought by Tim from an external Claude Code session (separate
project, ~/tokenized-oracle-divergence/) that built a complete Pine Script
v6 TradingView strategy against a "Coding LLM Build Package" spec
(DOC 0-10). NOT sourced from noisebot's own research pipeline — no
adversarial deep-research sweep has vetted this mechanism the way
E9/E11/E12 or E14's seed candidates were. The .pine file has NEVER been
compiled or backtested (no offline Pine compiler exists); it is a
reasoned draft, not a verified one, per its own header disclaimer.

EXPLICIT FREEZE OVERRIDE (constitution-required note — flagged before
registering, not silently bypassed): STATE.md's 2026-07-24b close
explicitly declared "no new discovery registrations (edge well is dry —
manufacturing more would be padding/p-hacking)," with the stated next
action being Tim's PB4 decision, not new discovery. Tim explicitly asked
to register THIS hypothesis in this session (2026-07-29) despite that
freeze, after being shown both the freeze note and the infra gap below.
Recorded here so the freeze is not silently contradicted: this is a
DIRECT, ONE-OFF OVERRIDE for this entry, not a resumption of general
discovery activity. The freeze otherwise stands.

Economic rationale (why the edge should exist in microstructure terms):
tokenized-equity products (an on-chain proxy tracking a real-exchange
stock, e.g. a tokenized-AAPL token) trade on 24/5 or 24/7 crypto-style
venues with fragmented liquidity and market-maker inventory/latency risk,
while the underlying cash equity trades on a continuous-NBBO exchange
only during RTH. The wrapper has no real-time arbitrage mechanism forcing
price equality outside the cash market's hours or during thin
tokenized-venue liquidity — the basis (token price vs a same/prior-bar
cash-equity oracle) should drift on token-side order flow alone and
mean-revert once real price discovery resumes (RTH open) or once
tokenized-venue liquidity normalizes. This is a wrapper/ADR/closed-end-
fund-premium-style convergence trade, not price momentum,
calendar/threshold rebalancing flow, funding-rate carry, term-structure
roll, or CoT positioning — mechanistically DISTINCT from all ten
falsified families and from marginal E12 (FX carry via futures term
structure). No correlation-vs-prior-family check is possible here (no
overlapping price series exists with anything already tested in this
repo).

Rules (ALL fixed before any run — defaults exactly as shipped in the
referenced .pine file, never tuned or backtested):
- Chart symbol: tokenized-equity proxy, single name (spec default pairs
  it with NASDAQ:AAPL as the oracle). Oracle: input.symbol, default
  NASDAQ:AAPL, request.security same-timeframe with lookahead_off +
  confirmed-prior-bar close[1] default; daily HTF oracle+token via
  close[1] paired with lookahead_on (documented non-repaint HTF idiom).
- Spread: spread_pct = (token_close − oracle_close) / oracle_close * 100.
- Signal: rolling PERCENTILE RANK of spread over a 100-PRINT window
  (oracle-print-gated, not bar-gated — closed-market bars excluded from
  the reference distribution). Long when rank <= 10; short when
  rank >= 90 (signalMode = "Percentile", the registered primary; ZScore
  and "Both" modes exist in the file but are NOT part of this
  registration — a separate registration would be required to test them).
- Exit: directional reversion (long exits once rank climbs back >= 40;
  short once rank falls back <= 60), OR max 240 bars in trade, OR ATR
  stop = entry-snapshot ATR(14) x 2.5, fixed (not trailing).
- Filters (all ON by default, all required to fire): RTH session gate
  09:30–16:00 America/New_York; ADX(14,14) < 25 regime filter; daily HTF
  token-vs-oracle spread must agree in sign with the trade direction;
  oracle must have moved on the current bar (not mid-multi-bar-stale
  tolerance) AND be within 5 consecutive stale bars; equity-curve filter
  (equity >= EMA20 of equity); daily loss circuit −5%.
- Sizing: PATH B only — strategy.fixed qty in shares =
  floor(equity * effectivePct / 100 / close), base 10% of equity per
  trade, cut to 5% after 3 consecutive losses (sizeCutPct=50%, floored at
  95% max cut). Kelly cap OFF for v1 (useKelly=false).
- Costs: commission 0.05% (explicitly a RESEARCH FLOOR per the file's own
  header — noisebot's usual $2.50/ct RT / per-contract-multiplier
  convention DOES NOT APPLY here; this is share-based, not futures-based.
  A 0.30%+ re-run is required before any pass is trusted, per the file's
  own cost note), slippage 1 tick, margin 100% (cash-like).
- Registered plateau (ALL must be net positive, never best-of):
  entryPercentile in {5, 10, 15}. lookback (print-count window) NOT swept
  in this registration — fixed at 100 prints.

Gates (Phase-2-standard set, adapted to shares/percent instead of
contracts/dollars): n >= 100 trades; PF > 1.3; both sample halves
(calendar time) net positive; entryPercentile plateau {5,10,15} all
positive; barrier-MC P(maxDD > 40% of equity) < 10% at the registered
sizing (buffer-aware, WR assumed 5pts below backtest per constitution
non-negotiable #5).

Prediction if TRUE: PF > 1.3 on n >= 100 trades net of 0.05% costs (AND
the strategy must still show a positive-PF signature, even if smaller, at
the 0.30% stress commission per the file's own cost note); both halves
positive; entryPercentile plateau all positive; ruin gate < 10%.
FALSIFIED if ANY gate fails, OR if the edge only survives at the
unrealistic 0.05% commission floor and dies at 0.30% (sub-friction death,
same signature as E5/E7/E11).

Registered priors-against (real risks specific to this entry):
(a) NEVER COMPILED OR RUN — the .pine file has zero verified backtest
history; a Python port could inherit the same untested mechanical risk,
or could diverge from Pine's actual (still-unverified) runtime behavior,
making any Python-side "pass" partially uninformative about the Pine
strategy as shipped;
(b) tokenized-equity products are a NEW, thin market — real historical
price history may be short (months, not years) and illiquid outside a
handful of names, so n >= 100 may be structurally unreachable within any
honest window, same failure mode as E14's ~1 trade/yr;
(c) STRUCTURAL RISK NOT MODELED BY ANY PRICE BACKTEST: token
redemption/oracle-desync/custody risk is real and can produce a
"profitable" backtest on a feed that periodically decouples from reality
without warning — the .pine file's own risk disclaimer says the same
thing. A statistical PASS here would NOT by itself justify capital;
(d) commission/slippage realism for tokenized venues is genuinely unknown
(no fee schedule verified) — the 0.30% stress figure in the .pine file is
a guess, not a sourced venue fee.

Machinery-first (constitution/skill precedent, NOT yet done): before ANY
run, a pure-logic Python port of the signal (percentile-rank engine,
oracle-print gating, HTF agreement, ATR-snapshot stop, directional revert
exit) matching noise_area.py's "no I/O, no broker code" convention would
need to be written and unit-tested on SYNTHETIC data (no-lookahead,
no-repaint, correct rank/z, correct oracle-print exclusion) BEFORE any
real window is touched. NOT STARTED.

DATA WINDOW: **UNRESOLVED / BLOCKED.** No tokenized-equity data source
exists anywhere in this repo. Databento (this repo's paid vendor) is a
CME/futures/commodities vendor and does not carry tokenized-equity data.
noise_area.py's loader contract (single-instrument tz-aware NY OHLCV) also
does not fit — this strategy needs TWO synchronized feeds (tokenized
token + real equity oracle). No window is claimed, proposed, or burned by
this registration. This hypothesis CANNOT be evaluated until (1) a
tokenized-equity price source is identified and licensed/pulled, (2) a
loader is built and tested, and (3) the machinery-first port above is
done. Each of those is a separate, explicit future task.

Decision rule: this entry is registered for the RECORD ONLY, per Tim's
explicit instruction this session, overriding the discovery freeze for
this one case. NO CODE RUNS as a result of this registration — running
the test remains a separate, explicit future instruction
(register-hypothesis skill convention), and is additionally gated on
resolving the DATA WINDOW and MACHINERY-FIRST blockers above, neither of
which this session attempted. On eventual PASS: candidate sleeve -> Phase
4 shadow (adapted, as E4-v2/E14 were), never straight to capital. On
eventual FAIL: recorded and abandoned, no retune, no threshold search.

Window ledger: N/A — no data pulled, no Databento spend, nothing burned.

---

## E16 — REGISTERED 2026-07-25 (pre-test): Capitulation Finder — volume-confirmed mean reversion (BTC + ETH)

Provenance: public indicator "Capitulation Finder" (Tim-supplied script).
Structural audit found no bugs or dead code (unlike the Alpha-Scope
channel-breakout indicator audited the same session — drafted as a
candidate "E15" but NOT registered here; see
IDEAS_AUDIT_AND_SYNTHESIS.md/E15_HYPOTHESIS_DRAFT.md if that ID is ever
actually registered) — this indicator's entry logic is internally
coherent. Signal/marker only in the source; no exit was defined there,
so the exit rule below is this registration's own design, not inherited
from the indicator.

Economic rationale: forced-liquidation exhaustion — leveraged-long
liquidation cascades during a crypto selloff can push price through a
volume-climax blow-off low that overshoots any reasonable fair value;
once forced sellers are exhausted, price reverts toward its recent mean.
Distinct from E2 (VWAP-stretch mean reversion, decisively falsified:
PF 0.79, n=818) — E2's trigger was pure price/VWAP distance with no
volume condition at all; this requires an actual climax event, not just
a price stretch. Registered prior against: oversold readings do not
reliably resolve into a reversal — Bitcoin stayed pinned at
extreme-oversold through additional decline in the Nov 2018 crash. The
hard stop below exists specifically because of this, not as an
afterthought bolted onto a signal that "should" work.

Rules (ALL fixed before any run):
- Universe: BTC-USD AND ETH-USD, per-asset independent episodes (E6
  convention) — registered together because true triple-AND capitulation
  bars are rare by construction; a single asset risks starving n≥100.
- Timeframe: daily. Capitulation/exhaustion is mechanistically a slower,
  higher-timeframe phenomenon (multi-day panic, not an intrabar flicker).
- Entry: RSI(14) ≤ 30 AND close < SMA(50)×0.95 AND volume ≥ 1.2× its
  20-period average, all on the same bar → LONG next bar open. Long/flat
  only — the mirrored bearish-capitulation trigger is computed but not
  traded in this registration.
- Exit — first of: (1) close reverts to the SMA(50) (target, the
  mechanism's own definition of "reversion"); (2) time stop — registered
  plateau, 5 / 10 / 15 bars; (3) fixed 8% adverse move (hard stop, risk
  backstop, not swept).
- Costs: 0.35% fee/side + 10bps slip (E4/E4-v2 daily convention).
- Registered plateau parameter: time-stop bars (5 / 10 / 15) — all three
  must be net positive. (RSI/pct-threshold/volume-multiplier are the
  indicator's shipped defaults — FIXED, not swept.)
- Gates: n ≥ 100 closed trades (BTC+ETH combined); PF > 1.3; both sample
  halves net-positive; plateau (all three time-stop cells) net-positive;
  bootstrap (10k paths) P(maxDD > 40%) < 10%; correlation gate:
  daily-return correlation vs. E4-v2 and vs. E6 ≤ 0.5 — here a LOW
  correlation is the hoped-for result (a mean-reversion entry should look
  nothing like the trend book if it's real), unlike E7/E8-R where low
  correlation couldn't save a failing PF.
- Kill criterion: any gate fails → E16 falsified on this window. No
  retune, no threshold search, no swap to a different MA type/length
  after seeing results.

Window ledger: BTC/ETH daily price history has 4-5 prior evaluations
(E4, E4-v2, E4-v3, E6), all of the trend-family mechanism. A
mean-reversion trigger run on the same raw prices is a different kind of
test — logged honestly as "reused price data, fresh mechanism," not
claimed as a fresh window outright.

Data: `data/btc_usd_1d.json` and `data/eth_usd_1d.json` (Yahoo chart API,
explicit period1/period2 bounds — NOT range=max, which was found during
loader construction to silently return ~monthly-spaced bars while still
claiming interval=1d). 4330 BTC bars (2014-09-17→2026-07-25), 3181 ETH
bars (2017-11-09→2026-07-25), zero nulls, loader-verified. Code:
`e16_capitulation.py` (pure logic + loader), `test_e16.py` (8/8 pass on
synthetic data, including a spacing-guard regression test for the
range=max failure mode).

### 2026-07-25 — E16 evaluation (single registered run; log: logs/phase2_e16_2026-07-25.log)

Machinery verified on synthetic data before the run (test_e16.py, 8/8
incl. no-lookahead, engineered-crash triggering, spacing-guard
regression). A real fill-timing bug was found and fixed BEFORE this
result was recorded: `run_backtest()` marked equity to market using the
full close-to-close return through EXIT bars, then applied cost on top
— meaning exits effectively filled at the next bar's CLOSE, not its
OPEN as the function's own docstring claimed (entries were already
correct). Caught by an adversarial audit via a synthetic zero-cost
trace, fixed by explicitly splitting each transition bar into an
exposed segment (up to the fill point) and a flat segment, re-verified
against test_e16.py (8/8 still pass) before this run.

E16 VERDICT: **FAIL — 5/6 gates.** Capitulation Finder (RSI+MA-distance+
volume-climax entry, reversion-to-MA/time-stop/hard-stop exit), BTC+ETH
daily 2014-09→2026-07 / 2017-11→2026-07, time_stop_bars=10 primary:
n=72 combined (BTC=39, ETH=33; gate ≥100, **FAIL**), PF 0.662 (gate
>1.3, **FAIL**), combined chronological half1 −0.262 / half2 −0.855
(both negative, **FAIL**), plateau time_stop{5,10,15} total_ret −0.438 /
−1.118 / −1.494 (all negative, **FAIL**), bootstrap (10k paths, 50/50
BTC/ETH blended daily) P(maxDD>40%) 95.8% (gate <10%, **FAIL**). Passing
gate: correlation vs. E4-v2 0.023, vs. E6 0.067 (gate ≤0.5, PASS) —
confirms the mechanism really is uncorrelated with the trend book, as
predicted, but that alone can't save a PF well below 1.

Read: the registered prior-against was correct — oversold/extended/
volume-climax readings in this window did not reliably resolve into a
reversal, particularly on ETH (half1 −0.752, half2 −0.651, both legs
losing; final 0.164x = −83.6% on the ETH book alone) where BTC's own
book fared comparatively better (final 1.785x, positive, driven by a
few large wins early, but not enough to rescue the combined picture).
The n=72 shortfall (vs. gate ≥100) compounds an already-clear sign
failure — this is not primarily an underpowered-test problem the way
E14 was; PF 0.662 and 95.8% ruin risk are decisive on their own. Kill
criterion applies: E16 falsified. No retune, no threshold search, no
swap to a different MA type/length. Mean-reversion-via-volume-climax now
falsified alongside VWAP-stretch reversion (E2) — two mean-reversion
mechanisms, two failures, for related but not identical reasons (E2:
wrong sign outright; E16: wrong sign AND underpowered).

Window ledger: BTC/ETH daily now has 5-6 prior evaluations depending on
asset (BTC: E4/E4-v2/E4-v3/E6/E16 = 5; ETH: E6/E16 = 2) — E16 was the
first mean-reversion mechanism run on this data, all others are the
trend family.

---

## E17 — REGISTERED 2026-07-25 (pre-test): Livermore pivot-structure breakout (BTC)

Provenance: public indicator "Pivot Levels & Candle Color (Dark Theme)"
(Tim-supplied script) — the most sophisticated of four indicators
audited this session. TWO structural bugs found and fixed in the port
(`e17_pivot_structure.py`): (1) a repaint/lookahead bug — the source
uses a pivot at bar i before the pivot_right_bars needed to confirm it
have actually elapsed; fixed with an explicit forward-availability
shift, verified by a dedicated test plus the standard no-lookahead
perturbation test; (2) an O(n²) performance issue in the reaction-low/
-high tracker, replaced with an O(1)-amortized accumulator, cross-checked
against a literal brute-force port of the source's own algorithm (0
mismatches across 2000 synthetic bars, not just asserted equivalent).

Economic rationale: breakout above a confirmed swing high is treated as
a genuine regime shift (stops and momentum-chasing flow extend it); the
reaction-low invalidation is a failure-swing check specifically (did the
breakout immediately fail), while a separate three-part stall detector
catches a different, later failure mode (trend gone quiet well after the
breakout, independent of any hard level being touched). Registered prior
against: mechanically related to E1 (ORB breakout, falsified) and
H3-EXT (SMC/ICT, falsified) — both price-structure breakout mechanisms;
not obviously fresh, and the correlation gate below is how that gets
checked rather than assumed away. Independent, directly relevant
evidence on the failure-swing leg specifically: practitioner sources
(not peer-reviewed, flagged as such) on the closely related Swing
Failure Pattern cite ~74% win rate in consolidation vs. ~52% in strong
trends for that pattern family — a citable claim that this style of
setup is regime-dependent, and a reason E17's own numbers might look
uneven across the sample rather than uniformly strong or weak. (That
regime-dependence claim is also the rationale for a drafted, NOT
registered, "E18" regime-switch combining this with E16 — see
IDEAS_AUDIT_AND_SYNTHESIS.md/E18_HYPOTHESIS_DRAFT.md; per the E4→E4-v2
precedent, E18 should not be evaluated before E16 and E17 both have real
standalone numbers, so it is deliberately not registered alongside them
here.)

Rules (ALL fixed before any run):
- Universe: BTC-USD, daily bars.
- Pivot detection: look-left/look-right (10/10) confirmation + timeframe-
  adaptive confirmation factor + significance filter, per the source's
  own design (audited, not simplified).
- Position tracks trend_state directly (E4-style: no separate stop/
  target leg — the state machine's own invalidation IS the exit).
  Long/flat by default; allow_short=True is a distinct, unregistered
  perp/futures variant.
- Costs: 0.35% fee/side + 10bps slip (E4/E4-v2 daily convention).
- Registered plateau parameter: pivot window (left=right, jointly) —
  7 / 10 / 15 bars — all three must be net positive. (neutral_lookback=5
  is the indicator's shipped default — FIXED, not swept.)
- Gates: n ≥ 100 trades; PF > 1.3; both sample halves net-positive;
  plateau (all three pivot-window cells) net-positive; bootstrap
  (10k paths) P(maxDD > 40%) < 10%; Sharpe ≥ BTC buy-hold Sharpe;
  correlation gate vs. E4-v2 and E6 — reported and interpreted, not just
  pass/fail: SOME correlation with the trend sleeves is economically
  expected here (unlike E16), so a very high correlation (rough guide:
  >0.8) should be read as "the same trend bet with extra steps," not
  treated as a simple pass.
- Kill criterion: any gate fails → E17 falsified on this window. No
  retune, no threshold search, no re-run with a different
  pivot-confirmation factor after seeing results.

Window ledger: BTC daily — same reused-price-data situation as E16
(4-5 prior evaluations, all trend-family). A price-structure breakout
mechanism is a different kind of test, logged honestly, not claimed as a
fresh window.

Data: `data/btc_usd_1d.json` (same file and provenance as E16's — see
that entry for the range=max loader finding). 4330 bars,
2014-09-17→2026-07-25, zero nulls, loader-verified. Code:
`e17_pivot_structure.py` (pure logic + loader, includes both the
production and brute-force-verification reaction-tracking
implementations), `test_e17.py` (8/8 pass on synthetic data, including
the pivot-availability-shift correctness check, the fast-vs-bruteforce
equivalence check, and the spacing-guard regression test).

### 2026-07-25 — E17 evaluation (single registered run; log: logs/phase2_e17_2026-07-25.log)

Machinery verified on synthetic data before the run (test_e17.py, 8/8
incl. pivot-availability-shift correctness and fast-vs-bruteforce
reaction-tracking equivalence, 0 mismatches/2000 bars). An adversarial
audit independently re-derived every reported number from a fresh run
(not just re-read the log) and confirmed all figures below; it also
flagged that the correlation gate initially had no committed,
reproducible script — fixed by adding the correlation computation
directly into phase2_e17.py (this run's log reflects that).

E17 VERDICT: **FAIL — kill criterion (2 gates fail; 4 pass).** Livermore
pivot-structure breakout (10/10 confirmation, failure-swing + stall-
detector invalidation), BTC daily 2014-09→2026-07, pivot_window=10
primary, long/flat: n=47 (gate ≥100, **FAIL**), bootstrap (10k paths)
P(maxDD>40%) 74.1% (gate <10%, **FAIL**). Passing: PF 7.618 (gate >1.3,
PASS), half1 +8.267 / half2 +1.523 (both positive, PASS), plateau
pivot_window{7,10,15} total_ret +9.546 / +9.789 / +9.252 (all positive,
PASS), Sharpe 1.410 vs. buy-hold 0.962 (PASS). Reported, not gated:
correlation vs. E4-v2 0.719, vs. E6 0.587 — below the registered 0.8
rough-guide for "redundant expression" but clearly substantial, not the
low-correlation profile a genuinely distinct mechanism would show.

Read: the signal itself looks real by every average-case measure this
pipeline has — PF 7.6 and Sharpe 1.41 are among the strongest this repo
has produced, comparable to E4's original 2.86 PF before its own ruin
gate failed. That comparison is the point: this is E4's story again.
Full-sizing carries near-buy-hold ruin risk (74.1% P(maxDD>40%) is close
to E4's original 97.8%), and n=47 over 11+ years means the signal fires
too rarely to clear the trade-count bar on its own, independent of the
ruin question. The 0.72/0.59 correlation with the trend book also means
that even if a sizing fix cleared the ruin gate the way E4-v2 did for
E4, this would not obviously add diversification beyond what E4-v2/E6
already provide — it may just be a slower-firing, more path-dependent
way to express the same trend bet. Kill criterion applies as registered:
E17 falsified on THIS registration (full sizing, no vol targeting). A
vol-targeted sizing variant would be a new, separate registration
(E17-v2, E4→E4-v2 precedent) — not run here, and not implied to be
worth running given the correlation finding above.

Window ledger: BTC daily now has 5 prior evaluations (E4/E4-v2/E4-v3/
E6/E17) — E17 is a price-structure-breakout mechanism, distinct in kind
from the trend-family signal the other four share, logged honestly per
E16's same reused-price-data caveat.

---

## E17-v2 — REGISTERED 2026-07-25 (pre-test): E17 signal at vol-targeted sizing

Rationale: E17 (Livermore pivot-structure breakout) passed 4/6 gates
decisively — PF 7.618, both halves positive, plateau strongly positive
across all three pivot windows, Sharpe 1.410 vs. buy-hold 0.962 — and
failed only on bootstrap ruin risk (74.1%, gate <10%) and trade count
(n=47, gate ≥100). This is the same shape as E4's original failure (PF
2.86, ruin gate FAIL, fixed by E4-v2's vol-targeting without touching
the signal). Registered fix is SIZING, not signal: `compute_signals()`
is byte-for-byte unchanged from E17; only exposure is vol-targeted,
`run_backtest_voltarget()` in `e17_pivot_structure.py`, mirroring
`crypto_trend.run_e4_voltarget` exactly (w_t = min(1, vol_target/
sigma_t), sigma_t = 30-day realized vol annualized, no lookahead).
Machinery-verified pre-run on a dedicated high-volatility (~67%
annualized, BTC-like) synthetic fixture: full-size maxDD −61.4% vs.
vol-targeted −18.9%, similar final return (test_e17.py, 9/9 pass).

**Stated in advance, per register-hypothesis discipline**: vol-targeting
cannot increase trade count. If every other gate clears but n stays at
47, this registration is STILL falsified on the n≥100 gate — that
outcome should be read as "the sizing mechanism is confirmed working,
the frequency problem is separate and unsolved," not quietly waived.

Rules (ALL fixed before any run):
- Universe/timeframe/signal: BTC-USD daily, pivot_left=pivot_right=10,
  neutral_lookback=5 — unchanged from E17.
- Sizing: w_t = min(1, vol_target/sigma_t) applied to trend_state's
  direction; sigma_t = 30-day realized vol of daily returns, annualized
  (√365), no lookahead (matches E4-v2 construction exactly).
- Costs: 0.35% fee/side + 10bps slip (unchanged).
- Long/flat by default (allow_short=False) — unchanged from E17.
- Registered plateau parameter: vol_target — 0.10 / 0.15 / 0.20 — all
  three must be net positive. (Pivot window 10/10 already cleared its
  own plateau under E17; not re-swept here. vol_win=30 is E4-v2's
  shipped default, fixed.)
- Gates: IDENTICAL bar to E17 — n≥100; PF>1.3; both halves net-positive;
  plateau (all three vol_target cells) net-positive; bootstrap (10k
  paths) P(maxDD>40%)<10%; Sharpe ≥ BTC buy-hold Sharpe; correlation vs.
  E4-v2/E6 reported and interpreted, not gated.
- Kill criterion: any gate fails → E17-v2 falsified on this window. No
  retune. A likely honest outcome (stated in advance): ruin gate passes,
  n gate still fails — record that distinction explicitly rather than
  collapsing it into an undifferentiated FAIL.

Window ledger: BTC daily evaluation #6 (E4/E4-v2/E4-v3/E6/E17/E17-v2) —
a sizing-only variant of an already-registered signal, same treatment
E4-v2 got relative to E4.

### 2026-07-25 — E17-v2 evaluation (single registered run; log: `logs/phase2_e17v2_2026-07-25.log`)

Independently adversarially audited (separate agent, no access to this
run's reasoning): every gate re-derived from scratch — manual PF/
Sharpe/maxDD recomputation, a 5-seed + 50k-path bootstrap robustness
check (not just the registered seed=7), a real-BTC-data lookahead
perturbation test on `run_backtest_voltarget` specifically (single-bar
spikes at 4 live-position bars confirm bar t's weight only ever touches
the t→t+1 return), and an entry/exit-date cross-check proving all 47
trades are byte-for-byte the same signal-timing as E17's own original
47 (vol-targeting changed position SIZE only, never entry/exit logic).
No discrepancy found that changes any gate outcome. `test_e17.py` 9/9,
`phase2_e17v2.py` reproducible byte-for-byte.

**E17-v2 VERDICT: FAIL — kill criterion (1 of 6 gates fails: n; 5
pass).** n=47 (gate ≥100, **FAIL** — structurally identical to E17's
47, confirmed via independent entry/exit-bar reconstruction; vol-
targeting cannot and did not change signal timing). Passing: PF 5.162
(gate >1.3, **PASS**, down from E17's 7.618 as de-risking trims the
largest trades, exactly as predicted), half1 +1.777/half2 +0.380
(**PASS**), plateau vol_target{0.10,0.15,0.20} +1.401/+2.157/+2.941
(all **PASS**), bootstrap (10k paths) P(maxDD>40%) 0.0% (gate <10%,
**PASS** — confirmed robust across 5 seeds and 50k paths, worst single
path only −36.4%), Sharpe 1.504 vs. buy-hold 0.962 (**PASS**, improved
from E17's 1.410). Reported, not gated: correlation vs. E4-v2 0.805,
vs. E6 0.640 (up from E17's 0.719/0.587) — mechanically explained by
the audit, not a bug: E17-v2 and E4-v2 now share the identical
30-day-vol/0.15-target sizing formula against the same BTC series,
producing exact 1.0000 exposure-size correlation whenever both are
simultaneously active, versus E17's binary 100%-exposure shape mismatch
against E4-v2's already-vol-scaled book. (Minor disclosed caveat,
inherited unchanged from E17's own original correlation reconstruction,
not new to this run: the comparator rebuilds E4-v2/E6 from
`data/*_usd_1d.json`, not the exact byte-identical file used in E4-v2/
E6's own original registrations, which no longer exists in the repo —
parameters match verbatim, only the price-data vintage may differ
slightly; unlikely to matter given the size of the shift, but disclosed
rather than assumed identical.)

Read: exactly the outcome predicted in advance — the sizing fix is
confirmed working (ruin gate cleared decisively and robustly, Sharpe
improved, PF stayed strong well above the bar), and the frequency
problem is confirmed separate and unsolved (n=47 is a property of the
10/10 pivot signal's own firing rate on daily BTC, invariant to sizing).
E17-v2 falsified on this window per the pre-registered kill criterion.
No retune, no re-run. A wider, pre-registered liquid-alt universe is
the legitimate next lever if trade count is to be addressed — a fresh
registration, not an edit to this one (see
`BOTTLENECK_DIAGNOSIS_2026-07-25.md`, "What 'just trade more tickers'
does and doesn't fix").

---

## E19 — REGISTERED 2026-07-25 (pre-test): delta-neutral perp funding-rate harvest (BTC/ETH/SOL, spot+perp hedged)

Rationale: E7 ("Perp funding-rate carry") was a naked directional bet on
the SIGN of funding — short the perp when funding ran hot, long when
negative, no offsetting spot leg — and failed decisively because the
unhedged directional position lost more on price than it collected in
funding ("funding leg +0.333 real but price leg −1.033 — carry is
priced"). That is not what "cash-and-carry" / "delta-neutral funding
harvest" means in practice: the standard professional construction
pairs the perp short with an equal-notional spot long, cancelling price
exposure so only the funding spread remains as P&L. E19 is that
construction — a structurally different risk profile, not a retune of
E7's thresholds. Perpetual funding is a structural payment from the
crowded (persistently leveraged) side to whoever takes the other side —
compensation for warehousing leverage demand, not a price forecast, the
same mechanism E7 correctly identified; the fix is entirely in position
construction. Research pulled 2026-07-25 found delta-neutral funding
strategies positive in every month of 2025 (documented max monthly
drawdown 0.80%) with professional implementations capturing ~19%
annualized in 2025, but funding has compressed materially into 2026
(high single digits by Q2 2026, per the same sources) — the honest
forward expectation registered here is modest (single-digit to low-
double-digit annualized), not the 2024-era headline numbers, and the
plateau/gate design below is calibrated to that, not to 2024 conditions.

**Long-funding-collection side only, stated in advance**: when trailing
funding is favorable, hold SHORT 1 unit perp + LONG 1 unit spot (delta
≈ 0). The mirror (long perp + short spot to collect negative funding) is
deliberately NOT registered — spot-shorting crypto requires a borrow
that isn't uniformly available/cheap at retail size, unlike E7's naked-
short design which could costlessly take either side. This is a real
executability constraint, not an oversight.

**Known modeling simplification, disclosed before any run**: the perp
leg is marked using the SAME spot-close series as the spot leg (no
separate perp mark-price history sourced). Spot and perp marks are
usually close but the basis WIDENS specifically during the high-funding
regimes this strategy targets — this simplification could bias hedge
quality in either direction exactly when it matters most, and is
reported as a limitation on any pass, not silently assumed away. A
mechanical consequence, verified in `test_e19.py`
(`test_hedge_neutrality_despite_large_price_move`): because both legs
are always opened/closed together at equal size against the identical
price series, the combined price-leg P&L is identically zero by
construction, for any price path — so the attribution gate below is
expected to pass trivially, and a near-miss or fail would itself
indicate an implementation bug, not evidence about real-world hedge
quality (which this proxy cannot see).

Rules (ALL fixed before any run):
- Universe: BTC, ETH, SOL — USDT-margined perps + equal-notional spot,
  independently per asset (E6/E7 convention: per-asset episodes),
  combined into one portfolio curve by equal-weight averaging the
  per-asset daily return series (not a book-level dot-product like E6/
  E7 — E19 has no book-level vol target, so summing raw per-asset
  returns would let 3 simultaneously-hedged assets imply undisclosed 3x
  gross exposure; averaging keeps the book ≤1x with no artificial cap,
  avoiding the kind of cap the gate-audit flagged as an artifact source
  in E12 — `run_e19()` in `e19_funding_basis.py`).
- Entry/exit: hysteresis band on trailing 3-day mean annualized funding
  — enter when > entry threshold, exit when < exit threshold (exit set
  lower than entry). LOOKBACK_D=3 and per-asset independence fixed, not
  swept.
- Sizing: fixed 1 unit per asset while hedged — edge measurement only
  (E4 pre-v2 convention). A vol-targeted/capital-efficient sizing
  variant is explicitly NOT part of this registration (E4→E4-v2
  precedent would apply to a future E19-v2, not here).
- Costs: entry/exit on BOTH legs — spot 10bps/side (E4/E4-v2
  convention), perp 6bps/side (E8-R Binance-perp convention), ~32bps
  round trip per hedge cycle — plus actual historical funding accrual
  (8h prints, Binance monthly archives, same source E7 established).
- Registered plateau parameter: entry/exit threshold pair — (6%/2%),
  (8%/3%), (12%/5%) — all three must be net positive. All other
  parameters fixed.
- Windowing: engine runs over each asset's full price history (funding-
  less pre-2020 bars come back as legitimately flat, not trimmed inside
  `run_e19`/`run_e19_single`); gates/Sharpe/bootstrap computed only over
  the funding-available window, 2020-01-01 onward (BTC/ETH) — same
  METRIC_START convention `phase2_e7.py` uses, applied in `phase2_e19.py`.

Gates (standard set + a STRICTER attribution gate than E7's): n≥100
hedge episodes (BTC+ETH+SOL combined, per-asset independent); PF>1.3;
both sample halves net-positive; plateau (all three threshold-pair
cells) net-positive; bootstrap (10k paths) P(maxDD>40%)<10% — predicted
to pass easily if the hedge works as designed, since a genuinely
delta-neutral book should never approach 40% drawdown from price risk
alone; attribution gate (stricter than E7's "funding>0 AND
funding>|price|"): |price-leg P&L| < 20% of |funding-leg P&L| — this
is the gate that actually tests hedge quality, not just whether funding
won on net (see disclosed simplification above re: expected to pass
trivially here); **correlation gate vs. E4-v2/E6 ≤ 0.5 (hard gate, not
merely reported/interpreted — unlike E17-v2's convention)** — low
correlation is expected and part of the investment case (a genuinely
delta-neutral book should show close to zero correlation with a
directional trend book — same logic as E16's correlation prediction,
which held: 0.02–0.07 measured), but it is registered here as a pass/
fail bar, per `E19_HYPOTHESIS_DRAFT.md`'s original wording.

Kill criterion: any gate fails → E19 falsified on this window, recorded,
no retune, no threshold search, no switching to sourcing real perp
marks after seeing unfavorable spot-proxy results (that would be a
fresh registration citing this one's result, not a silent edit).

Window ledger: Binance funding history (BTC/ETH 2020-01-01→2026-06-30,
SOL 2020-09-13→2026-06-30, confirmed present, 226 monthly archives) was
already burned for the DIRECTIONAL E7 hypothesis (evaluation #1
consumed) — a delta-neutral construction is a structurally different
mechanism (hedge quality and funding-sign timing, not price direction),
logged honestly as reused data, matching the disclosure convention used
for BTC/ETH price data reuse across the E4-family and E16/E17. Spot
price data (same `data/*_usd_1d.json` as E16/E17/E17-v2) covers the same
window.

Files: `e19_funding_basis.py` (`run_e19_single` — one asset; `run_e19` —
BTC/ETH/SOL wrapper), reusing `e7_carry.load_funding_daily` unchanged.
`test_e19.py` — 8/8 PASS on synthetic data (hysteresis transitions,
hedge-neutrality under a large synthetic price move, cost/funding
magnitude checks, no-lookahead, multi-asset combination arithmetic).

### 2026-07-25 — E19 evaluation (single registered run; log: `logs/phase2_e19_2026-07-25.log`)

Independently adversarially audited (separate agent, no access to this
run's reasoning) — re-derived every gate from scratch rather than
trusting the log: manual PF/win-loss recomputation, an independent
from-scratch replay of the full P&L loop, a second bootstrap
implementation (own RNG) plus a 10-day block-bootstrap robustness
variant, a trade-duration-distribution check (median 10 days, only
1/140 a 1-day flicker — ruling out n-laundering), and a forensic file-
mtime check proving the simplification disclosure and gate spec were
written and frozen on disk ~90 seconds *before* the run executed (not
a post-hoc excuse). `test_e19.py` 8/8, `phase2_e19.py` reproducible
byte-for-byte. No bug found that changes any gate outcome.

**E19 VERDICT: PASS — 7/7 gates, independently re-audited.** n=140
(BTC 48 / ETH 36 / SOL 56, gate ≥100, **PASS**), PF 9.075 (**PASS**),
half1 +1.312/half2 +0.428 (**PASS**), plateau entry/exit{6%/2%, 8%/3%,
12%/5%} +1.758/+1.740/+1.708 (all **PASS**), bootstrap (10k paths)
P(maxDD>40%) 0.0% (**PASS**, worst of 10k paths only −0.85%, and 0.0%
again under a 10-day block-bootstrap variant), attribution |price|
0.0 vs. funding +0.729 (**PASS**), correlation 0.070 vs. E4-v2 / 0.102
vs. E6, both ≤0.5 (**PASS**).

**This is a mechanism/signal-timing pass, not a real-world-risk pass,
and the two must not be conflated when deciding what this result
means.** The audit's central finding: the perp leg is marked off the
*same* spot-close array as the spot leg — not approximately equal,
literally the same array object in the code — so the combined price-
leg P&L is exactly 0.0 on every single day, for all three assets,
individually and combined (confirmed algebraically and by replaying
all 4,330 BTC bars: zero nonzero-price-P&L days). That makes gate #6
(the attribution gate) a **tautology, not a measurement** — it could
not have failed given this construction, regardless of how the hedge
would actually perform. It also means the maxDD (−2.8%) and Sharpe
(7.2, sustained over 6.5 years) describe a world with zero spot/perp
basis risk, zero cross-venue execution slippage, zero perp liquidation
risk, and zero exchange/counterparty risk — precisely the channels
`E19_HYPOTHESIS_DRAFT.md` itself flagged in advance as widening
specifically during the high-funding regimes this strategy targets,
i.e. exactly where the real risk is expected to concentrate. A Sharpe
of 7 held for 6.5 years is not a plausible real-world number for any
two-venue hedged strategy; it is the expected signature of a backtest
that has structurally removed its own primary risk channel by
disclosed construction, not evidence the strategy is actually that
safe. What this run DOES validate: the funding-sign timing logic is
real and causally clean (no lookahead — funding print settlement times
independently verified against Binance's 00:00/08:00/16:00 UTC schedule
predate the price-bar close they're used against), the 140 episodes
are economically plausible hold periods (median 10 days) rather than
flicker noise, and the low correlation to the existing trend book
(0.07–0.10) is real and matches the delta-neutral investment case, not
an artifact of the simplification. What it does NOT validate: hedge
quality under real market stress, which is the actual question a
capital-allocation decision needs answered.

Two smaller findings from the audit, neither gate-affecting: (1) SOL's
*price* history starts 2020-04-10 (not the funding-history start of
2020-09-13 the code comment cites) — for that ~92-day gap, the equal-
weight portfolio average divides by 2 assets instead of 3, inflating
the combined total-return multiple by ~2.5% relative (1.8288x vs. an
always-÷3 alternative of ~1.7847x) with zero effect on maxDD or any
trade-level gate — a documentation-precision issue in
`e19_funding_basis.py`'s comment, not a math bug, left uncorrected
since it doesn't change the verdict. (2) the E4-v2/E6 correlation
comparators are rebuilt from `data/*_usd_1d.json` rather than the
byte-identical files E4-v2/E6's own original registrations used (now
missing from the repo) — same disclosed caveat as E17-v2's correlation
figure above, immaterial at this margin (0.07/0.10 vs. a 0.5 bar) but
not assumed identical.

Kill criterion did not trigger — no gate failed. Per the pre-registered
kill criterion's own terms, that means no retune and no re-run apply
(there is nothing to retune); it does NOT mean this is ready to size
capital against. Before this supports a shadow/live deployment
decision, the honest next step — flagged in advance in
`E19_HYPOTHESIS_DRAFT.md` and confirmed necessary by this audit — is
either (a) sourcing actual Binance perp mark-price history to replace
the spot proxy and re-registering a fresh evaluation against it (E19-v2
territory, same E4→E4-v2/E17→E17-v2 precedent of not silently editing
a closed registration), or (b) a paper/shadow exposure that experiences
real basis behavior directly rather than through this backtest's proxy.
Not done here — recorded as the explicit next step, not implied to be
optional polish.

---

## E19-v2 — REGISTERED 2026-07-26 (pre-test): E19 with real Binance perp mark-price history replacing the spot proxy

Rationale: E19's own audit found that its attribution gate (|price-leg
P&L| < 20% of |funding-leg P&L|) was a **tautology, not a measurement**
— the perp leg was priced off the same spot-close array as the spot
leg (disclosed up front as a known simplification), making combined
price-leg P&L exactly, algebraically 0.0 every day, for any price path.
That made the Sharpe (7.2) and maxDD (−2.8%) numbers describe a world
with zero spot/perp basis risk — precisely the channel the original
draft flagged as widening during the high-funding regimes this
strategy targets. This is the direct, single-input fix: source real
Binance USDⓈ-M perp mark-price history (`data/perp_mark/`, 226 monthly
archives fetched 2026-07-26, identical coverage to the funding data —
BTC/ETH 2020-01-01→2026-06-30, SOL 2020-09-13→2026-06-30) and price the
perp leg off THAT instead of the spot proxy. **This is a risk-modeling
input swap, not a signal search**: the entry/exit hysteresis logic on
trailing funding, the fixed 1-unit sizing, the costs, the multi-asset
combination, and the registered plateau are all byte-for-byte unchanged
from E19 — same E4→E4-v2 / E17→E17-v2 precedent of touching exactly one
thing under test. `run_e19_single`/`run_e19` (E19's own, already-
evaluated functions) are untouched; `run_e19_single_v2`/`run_e19_v2` are
new, additive functions in the same file. Machinery-verified on
synthetic data before any real data was touched: `test_e19.py` is now
13/13, including a regression check that v2 reduces to byte-identical
output when fed the same series for both legs (confirming the only
behavioral difference is the price source), and an independent-replay
check that a real, deliberate basis divergence shows up in the
attribution correctly.

**Sourcing this data surfaced a real archive-format inconsistency,
worth recording since it could bite a future registration reusing this
data**: Binance's own monthly kline archives before ~2022-02 ship with
no header row; later ones do. A naive uniform `pd.read_csv` across all
226 files silently misaligns columns (one file's first data row gets
read as that file's header, corrupting the whole concatenated frame) —
caught before any number was computed, not after; `load_mark_price_daily`
detects and normalizes per file.

**Pre-registration basis analysis (exploratory, not gated — informs
the prediction below, not a retune)**: comparing real mark price
against the spot series over the full overlap window found the average
daily basis is small on BTC/ETH (~0.10–0.18% absolute) and — consistent
with the audit's prediction — larger on trailing-funding-hot days than
otherwise (BTC 0.131% vs 0.100%; ETH 0.177% vs 0.101%). SOL shows a
dramatic outlier: a **16.6% one-day basis blowout on 2022-11-09** (perp
mark low $9.92 vs. spot low $12.51), the acute FTX-collapse liquidation
cascade — verified against raw OHLC, not a parsing artifact. A pre-
registration integration smoke test (same precedent as E19 v1's own
pre-registration check: confirms the mechanism runs on real data,
computes no gate-relevant statistic) found trade count/timing unchanged
at n=140 (funding-timing logic is untouched, as intended, so this
cross-check is expected to hold exactly), a combined attribution ratio
of roughly 7% (|price| ≈ 0.051 vs |funding| ≈ 0.729 — comfortably under
the 20% bar, though the FORMAL gate battery has not yet been computed
and could differ), and — notably — SOL's own hedge WAS active through
the FTX-collapse window (entered 2022-11-07, exited 2022-11-09) and
that specific episode came out slightly positive, because the perp fell
harder than spot that day and this position is short the perp. Stated
precisely to avoid over-claiming in either direction: this shows the
largest basis dislocation in the whole window happened to cut in this
position's favor on this occasion — it is not evidence that basis risk
is generally benign for this construction, only a true fact about what
happened this one time.

### Exact specification (fixed before the registered run)

- Universe/mechanism: BTC/ETH/SOL, identical hysteresis entry/exit on
  trailing 3-day mean annualized funding, identical fixed 1-unit-per-
  asset sizing when hedged, identical costs (10bps spot + 6bps perp per
  side) — all unchanged from E19.
- **The only change**: perp leg priced off `load_mark_price_daily()`
  (real Binance mark-price daily close, `data/perp_mark/`) instead of
  the spot-proxy array. Spot leg still priced off `data/*_usd_1d.json`,
  unchanged.
- Registered plateau: SAME three entry/exit threshold pairs as E19 —
  (6%/2%), (8%/3%), (12%/5%) — not re-swept, per the "don't re-litigate
  an already-settled parameter" discipline. Primary cell: (8%/3%),
  unchanged.
- Multi-asset combination: same equal-weight averaging as `run_e19`,
  unchanged rationale.
- Windowing: same METRIC_START=2020-01-01 convention as E19/phase2_e7.

### Gates (IDENTICAL to E19's bar — not weakened, not strengthened)

n≥100 hedge episodes; PF>1.3; both sample halves net-positive; plateau
(all three threshold-pair cells) net-positive; bootstrap (10k paths)
P(maxDD>40%)<10%; attribution gate |price-leg P&L| < 20% of
|funding-leg P&L| — **this time a real, discriminating test, not a
tautology**; correlation vs. E4-v2/E6 ≤ 0.5 (hard gate, matching E19's
own convention).

### Prediction, stated in advance

Unlike E19 v1 (where the attribution gate literally could not fail),
this is a genuine test and the honest answer is that the outcome is
uncertain in a way it wasn't before. Best-informed guess from the
pre-registration analysis above: BTC/ETH's small, real basis (~0.1-0.18%
daily absolute) is unlikely on its own to flip the attribution gate or
meaingfully dent the bootstrap ruin gate, given funding income
(cumulative ≈0.73 in the v1 run) dwarfs it by roughly an order of
magnitude. SOL carries the real tail risk (the 16.6% FTX-collapse
blowout sits inside this window) but the one realized instance of a
hedge being active through it happened to cut favorably, not adversely
— whether OTHER, un-previewed dislocations in SOL's history land
favorably or adversely for this position direction is genuinely not
known in advance, and is exactly what running the full gate battery
(especially bootstrap and the correlation gate) will actually tell us.
If every gate still clears, that would be meaningfully stronger
evidence than E19 v1's clean sweep, precisely because this attribution
gate can now fail. If the attribution or bootstrap gate fails here, that
is the audit's concern being confirmed empirically, not a bug.

### Kill criterion

Any gate fails → E19-v2 falsified on this window, recorded, no retune,
no re-run, no switching back to the spot proxy to recover a pass (that
would be exactly the kind of post-hoc methodology reversal this
repo's discipline exists to prevent). A fail here is a genuinely
informative, not disappointing, result: it would mean the real
hedge-quality question the original E19 audit raised has been answered
in the negative for this specific historical window.

### Window ledger

Perp mark-price data: first use, this registration (previously
unsourced). Funding data reused a third time (E7 directional, E19
hedged-proxy, E19-v2 hedged-real) — logged per the same disclosure
convention as every other funding-data reuse this session. Spot price
data: same files as E19/E17-v2, reused again.

### Files

`e19_funding_basis.py` — `load_mark_price_daily`, `run_e19_single_v2`,
`run_e19_v2` added; `run_e19_single`/`run_e19` untouched.
`test_e19.py` — 13/13 PASS (8 v1 + 5 new v2: perp-equals-spot regression,
basis-divergence independent replay, no-lookahead, multi-asset
combination, mark-price-loader header/no-header handling).

### 2026-07-26 — E19-v2 evaluation (single registered run; log: `logs/phase2_e19v2_2026-07-26.log`)

Independently adversarially audited (separate agent, no access to this
run's reasoning), and held to a deliberately higher bar than E19 v1's
audit on the explicit reasoning that a SECOND consecutive clean sweep
is the moment to be most skeptical, not least. The audit re-derived
every gate from raw data via two independent from-scratch
reimplementations that never call the shipped engine; re-ran the
bootstrap across 7 seeds × 10k paths, 3 seeds × 50k paths, and a
10-day block bootstrap (~220k total paths); ran adversarial per-bar-
varying-noise perturbation tests at 11 real confirmed-hedged bars; and
hand-computed the FTX-window trades directly from the raw CSVs.

**E19-v2 VERDICT: PASS — 7/7 gates, independently re-derived.** n=140
(BTC 48 / ETH 36 / SOL 56, **PASS**), PF 6.780 (**PASS**), half1
+1.1532 / half2 +0.4340 (**PASS**), plateau {6%/2%, 8%/3%, 12%/5%}
+1.683/+1.587/+1.608 (all **PASS**), bootstrap P(maxDD>40%) 0.0%
(**PASS** — robust across 10 seed/path-count combinations; worst single
resampled path across ~220k paths −30.8%, still 9 points clear of the
bar; historical realized maxDD only −6.6%), attribution ratio 7.0%
(|price| 0.0507 vs. |funding| 0.7291, gate <20%, **PASS** — reproduced
to full float64 precision by the independent engine), correlation
−0.036 vs. E4-v2 / −0.083 vs. E6 (gate ≤0.5, **PASS**).

**The thing that makes this materially stronger than v1's pass: this
attribution gate could actually have failed, and didn't.** In v1 the
price leg was identically 0.0 by construction, so the gate was a
tautology. Here the price leg is genuinely nonzero (−0.0507, a real
cumulative hedge-slippage cost) driven by measured basis divergence,
and it still comes in at 7.0% of funding income — comfortably inside
the 20% bar that was registered before the run. Sharpe fell from v1's
implausible 7.2 to 1.483 and maxDD widened from −2.8% to −6.6%: the
numbers got *worse and more believable* in exactly the way they should
when a real risk channel stops being assumed away. Daily returns show
strong negative skew (−2.71) and heavy kurtosis (125.7) — consistent
with real, rare tail days rather than a smoothed artifact.

**FTX-collapse window, hand-verified from raw CSVs** (the concrete
tail-risk scenario this registration existed to test): BTC was hedged
2022-11-08→11-10 and **lost 0.52%** on realized basis; SOL was hedged
2022-11-07→11-09 and **gained 0.47%**, because SOL's perp fell harder
than spot that specific week (−19.6% vs −18.4% on 11-08) and this
position is short the perp; ETH was not hedged (nearest episode exited
11-04). Both hand-computations match the engine to ~1e-6. Note the
honest asymmetry: one episode helped, one hurt — this is not a
uniformly flattering result, which is itself evidence against
cherry-picked reporting. Also worth stating precisely: SOL's hedge had
already exited by 11-09, the single worst dislocation day (spot 13.94
vs perp 11.62 close, 16.65% basis; intraday lows $12.51 vs $9.92, both
confirmed from raw data), so this strategy did **not** actually sit
through the very worst moment — a matter of timing luck on this
occasion, not a demonstrated property of the mechanism.

**Two precision corrections to this registration's own pre-test text,
recorded here rather than by editing the pre-registration (editing a
registration after seeing results is exactly what this repo's
discipline forbids):**
1. The pre-test smoke-test paragraph above claims trade count/timing is
   "expected to hold exactly" vs. v1. **Trade COUNT holds exactly
   (140, and ETH/SOL are byte-identical); trade TIMING does not, in
   exactly one case**: BTC trade #11's entry shifts 2021-07-02 → 07-03.
   Root cause, fully traced by the audit: 2021-07-01 is a genuine
   one-day hole in Binance's own perp-mark archive, and it lands on the
   exact day BTC's trailing funding first crossed the entry threshold.
   `run_e19_single_v2`'s decision gate requires BOTH legs to have valid
   prices (v1's needed only spot), so the entry is acted on one day
   late. This is a data-AVAILABILITY effect, not a price-driven one —
   price levels never influence entry/exit in this construction, only
   price presence — so it is not the "signal contaminated by price"
   failure mode that would have been serious. Impact: 1 of 140 trades,
   6.1e-5 shift in BTC's funding attribution (0.008%). No gate affected.
2. `run_e19_single_v2`'s docstring claimed a data-gap day free-wheels
   "at zero P&L". **Only the PRICE leg is zeroed; funding still accrues
   against the frozen pre-gap weight** when a position is already held
   (deliberate — the funding print is real and present on those days;
   the hole is in the mark-price archive, not the funding archive).
   Measured: 10 held-and-gapped instances (3 BTC, 1 ETH, 6 SOL),
   +0.0024 raw funding ≈ 0.11% of total. The audit specifically checked
   whether gap days were suppressing losing days — they are not (gap
   dates are mundane, no worse than the 7th percentile of daily moves,
   and none coincide with 2022-11-09). Docstring corrected post-audit;
   **no code behavior changed, and the run was re-verified byte-for-byte
   reproducible after the docstring edit.**

Inherited caveats, unchanged from v1 and not re-litigated here: SOL's
spot history starts 2020-04-10 (before its funding history), so the
equal-weight average divides by 2 rather than 3 for ~100 early days
(~2.5% relative inflation of the total-return multiple, zero effect on
maxDD or any trade-level gate); the E4-v2/E6 correlation comparators
are rebuilt from `data/*_usd_1d.json` rather than those hypotheses'
own original (now-missing) files.

Kill criterion did not trigger — no gate failed, so no retune and no
re-run apply. **What this now does and does not establish.** It DOES
establish, with real (not assumed-away) basis data, that the funding
income on this construction has historically dwarfed realized hedge
slippage by roughly 14:1 on daily closes, that the mechanism is
lookahead-free under adversarial perturbation on real data, and that
its return stream is genuinely uncorrelated with the existing trend
book (−0.04/−0.08) — the diversification case is real. It does NOT
establish live viability: this is daily-close granularity only, and
models neither intraday liquidation mechanics on the perp leg, nor
funding-settlement timing risk, nor spot-borrow/margin constraints,
nor exchange/counterparty risk. The honest next step is unchanged from
v1's write-up and is now the ONLY blocking one: **paper/shadow
exposure that experiences real execution and real basis directly**,
sized as edge measurement, not capital deployment. A vol-targeted or
capital-efficiency-optimized sizing variant remains explicitly
unregistered (E19-v3 territory, E4→E4-v2 precedent).
