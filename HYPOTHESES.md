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
2005-01-01 → 2026-06-30 — FRESH, evaluation #1 on commodity daily
ladders in this repo. Cost quoted before pull; key stays in env.
Overlap disclosure: GC/SI/CL 2019→2026 sub-span overlaps the PB4
window (mechanism unknown). Mitigations recorded: (a) E9's signal is
basis-momentum (curvature), almost certainly orthogonal to whatever
PB4 is; (b) 2005-2019 is clean for those three and is the bulk of the
sample; (c) the other 11 roots are fully fresh; (d) PB4's own CSVs are
NOT reused — a clean pull is taken. When Tim imports the PB4 record,
reconcile.

Kill criterion: any gate fails → E9 falsified on this window. No
retune, no universe reshuffle, no threshold/lookback search.

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

Data window: CFTC CoT 2006-01 → 2026-06 — FRESH positioning window,
never used here (evaluation #1). Prices REUSE E9's commodity window
(disclosed shared-window multiplicity above — that window is mined
twice by design; both single-evaluation). Free data for the signal;
no incremental Databento spend beyond E9's pull.

Kill criterion: any gate fails → E11 falsified. No retune, no filter
additions, no post-hoc double-sort.

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
roots, 2005-01-01 → 2026-06-30 — FRESH FX window, evaluation #1. Cost
quoted before pull. Overlap disclosure: 6E/6B/6A/6J 2019→2026 sub-span
overlaps the PB4 window (mechanism unknown); mitigations mirror E9 —
signal is FX carry (orthogonal to plausible PB4 mechanisms), 2005-2019
clean, 6C/6S/6N/6M fully fresh, PB4 CSVs not reused. Reconcile on PB4
import.

Kill criterion: any gate fails → E12 falsified on this window. No
retune, no universe change, no threshold search.

---

### Window-ledger update — 2026-07-23 (E9/E11/E12 registration)
- Commodity daily ladders (14 GLBX roots) 2005→2026: reserved for E9
  (eval #1) and E11 (shares the price window — mined twice, disclosed).
- FX daily ladders (8 GLBX roots) 2005→2026: reserved for E12 (eval #1).
- Both pulls are FRESH; GC/SI/CL and 6E/6B/6A/6J carry a 2019→2026
  PB4-overlap caveat (recorded per-entry). No data pulled yet — costs
  quoted before any Databento spend.
