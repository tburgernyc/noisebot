# STATE — noise_bot

Updated: 2026-07-25 (session: 4 public indicators audited via Claude session, E16/E17 registered, loader wired)

## 2026-07-18 session

- Harness verified live: gate_guard blocked both probes from the
  harness test (a non-negotiable-#1 file write, and shell access to
  the gate-marker directory); the post-edit hook auto-ran
  test_signals.py on a noise_area.py edit. All as designed.
- data/nq_5m.json restored (gitignored, was lost with the data/ dir):
  re-fetched via the shadow_logger.py canonical Yahoo URL — 17,279
  5m bars, 2026-05-06→2026-07-17. test_signals.py: ALL 5 PASS.
  Fresh 60-day window; selection-burned status unchanged (QA only).
- CLAUDE.md "Current state" reconciled with STATE.md/HYPOTHESES.md
  (it predated the E1–E6 series; stale H3/TQQQ/forex lines removed).
- Verified Phase 4 shadow is LIVE: crons run in ~/noise_bot (a second
  clone of this repo), signals_e4v2/e6.jsonl accruing daily
  2026-07-16→2026-07-18, zero gaps, zero error lines so far.
- Prior next action (build shadow loggers) confirmed DONE pre-session.
- NOT done, on the record: quote_databento_cost.py not run (blocker is
  not a data pull); no backtests run; no hypotheses tested.
- RESOLVED same day: clones consolidated. ~/noisebot is canonical.
  Data (databento_1m.parquet + crypto dailies) and live shadow logs
  migrated (append-only superset verified by prefix hash); crons
  repointed to ~/noisebot and both shadow scripts verified running
  there (logged bar 2026-07-17, e4v2 signal ON, w=0.4502); old clone
  renamed to ~/noise_bot.retired-2026-07-18 (had zero unique commits).

## 2026-07-18b session (consolidation completed)

- Clone consolidation finished and VERIFIED: crons repointed and firing
  from ~/noisebot; logs/shadow_cron.log gitignored (kept local).
- Pre-deletion sweep of the retired clone found .xfer/p1-p5 transfer
  chunks (base64 tar.gz, 2026-07-14): five members byte-identical to
  tracked files, but make_synthetic_1m.py and deploy_phase2.sh existed
  NOWHERE in git — rescued, verified (py_compile / bash -n), committed
  (fca8cf5) with deploy DEST repointed to ~/noisebot. Tarball's
  STATE.md member was truncated (old snapshot; substance in git
  history). Old clone then deleted by Tim.
- test_signals.py final run: ALL 5 PASS. No hypotheses tested; no
  backtests run. HYPOTHESES.md unchanged (summary table produced for
  Tim from existing entries only).
- Shadow status at close: e4v2 logged through bar 2026-07-17, signal
  ON (r28 +0.0056, w 0.4502); e6 accruing; zero error lines.

## 2026-07-18c session (E7 registered, evaluated, falsified)

- E7 (perp funding-rate carry, standalone) registered pre-test with
  Tim's parameter sign-offs (threshold plateau ±10/15/20, PF>=1.2
  adaptation, Binance source + 10bps/side fixture), then evaluated
  ONCE. VERDICT: FAIL 2/8 gates — n=129 episodes, PF 0.58, both halves
  negative, plateau all negative, maxDD -63.7%, attribution gate FAIL:
  funding leg +0.333 real but price leg -1.033 (carry is priced).
  corr(E6) -0.486 (n=2,022 days) passed; worthless at PF 0.58.
  Once-only OOS 2026H1: -5.31%, Sharpe -1.66 (n=181 days). Recorded in
  HYPOTHESES.md; abandoned per kill criterion. Log:
  logs/phase2_e7_2026-07-18.log. Carry family now falsified alongside
  momentum, ORB, VWAP reversion.
- New data: Binance monthly funding archives via data.binance.vision
  (fapi geo-blocked): data/funding/, 226 CSVs, BTC/ETH 2020-01→
  2026-06-30, SOL from 2020-09 listing. Window burned (evaluation #1).
- New code: e7_carry.py (pure logic), test_e7.py (6/6 machinery tests
  incl. no-lookahead, run BEFORE the evaluation), phase2_e7.py.
- Harness bug found: hooks invoke gate_guard.py by RELATIVE path, so a
  shell cwd left outside repo root breaks every hooked tool (deadlock;
  escaped via subagent-created delegating stub, since removed).
  Durable fix: prefix the hook command with the project dir (e.g.
  $CLAUDE_PROJECT_DIR) in .claude/settings.json. NOT yet applied.
- Baseline suite green all session: test_signals.py ALL 5 PASS.

## 2026-07-18d session (E8-R registered, evaluated, falsified; hook fix)

- E8-R (ETHUSDT 15m trend continuation, redesigned from an audited
  public Jesse TEMA strategy) registered pre-test with Tim's cost
  fixture sign-off (6 bps/side + actual funding prints), then
  evaluated ONCE. VERDICT: FAIL 3/7 gates — body 2022→2025: n=951,
  PF 1.05, both halves positive, plateau 5/9 cells negative, top-5
  concentration 217% of net (pre-declared lottery falsifier),
  corr(E6) -0.008 (n=1,161 days). OOS 2026H1: n=126, -909 USDT/unit.
  Attribution: gross price +3,883 vs costs -2,759 (71% of gross) —
  sub-friction, same failure mode as E3/MNQ family. Skew signature
  MATCHED prediction (WR 33.1%, W/L 2.13): trend-shaped, no net edge
  at 15m. Plateau gradient points to the daily horizon (E4-v2/E6).
  Recorded in HYPOTHESES.md; abandoned. ETHUSDT 15m 2022→2026 burned.
- New data: data/klines/ (54 Binance Vision monthly 15m archives,
  157,632 bars). New code: e8_trend.py, test_e8.py (8/8 machinery
  incl. no-lookahead over 137 trades; TEMA init-transient bug found
  and fixed on SYNTHETIC data pre-run, warmup mask 3n→6n), phase2_e8.py.
- Hook-path bug FIXED: both hook commands in .claude/settings.json now
  cd to "${CLAUDE_PROJECT_DIR:-/home/tburger/noisebot}" first —
  invocation AND the guard's internal relative gate checks are now
  cwd-independent. Verified by stdin pipe-test from a foreign cwd
  (benign exit 0 / banned-content exit 2) + jq schema check. Takes
  effect on /hooks reload or next session start.
- Tests at close: test_signals.py 5/5, test_e7.py 6/6, test_e8.py 8/8.

## 2026-07-18e session (parallel-session import; E7 resubmission refused)

- A /register-hypothesis resubmission of E7 (funding carry, materially
  identical spec) was REFUSED without writing an entry: E7 is already
  on the record as falsified today (FAIL 2/8, n=129, PF 0.58; carry is
  priced) and its kill criterion plus the burned Binance funding
  2020→2026 window bar re-registration. Nothing was re-run.
- Discovered: a PARALLEL cloud session has been working from a STALE
  snapshot of this project (pre-Databento-purchase, pre-E-series). Its
  STATE.md arrived here; archived verbatim with a non-canonical header
  at imports/STATE_cloud-session_2026-07-19.md. Its staged next action
  (local Databento pull, 2023-07→2026-07) should be CANCELLED: the
  data is already owned (data/databento_1m.parquet) and the window
  overlaps the burned MNQ window (4 evaluations).
- Imported from that session: H3-EXT (AMD/IFVG EURUSD, SMC/ICT family)
  — registered and evaluated THERE, VERDICT FAIL (PF 0.657, n=297,
  both halves negative, all 5 plateau variants negative, loses gross
  of costs). Recorded in HYPOTHESES.md with full provenance caveat
  (numbers not independently re-derivable here). That makes SEVEN
  falsified families.
- pull_databento.py stored at repo root at Tim's request (verbatim from
  the cloud session, plus a canonical-repo caveat block added to the
  docstring: do not run for selection; window ledger governs any spend).
  It is Tim-run-locally tooling — the key stays in his env; nothing in
  this repo invokes it.
- 2026-07-19 addendum: PB4 data pull executed by Tim locally ($6.66,
  quoted first) — Databento daily expiry ladders, 9 CME roots,
  2019→2026-07, verified 9/9 CSVs in ~/pb4_pull/pb4_out/ (spread
  instruments included in parent symbology — flagged for downstream
  filtering). PB4 evaluates in a SEPARATE session; window-ledger note
  added to HYPOTHESES.md (eval #1 consumed externally). PB4's outcome
  should be imported here pass or fail, like H3-EXT.
- Session close (2026-07-19): test_signals.py ALL 5 PASS; tree clean;
  all imports committed and pushed (93f9eb6). No hypotheses evaluated
  in this repo this session (E7 resubmission refused pre-registration;
  H3-EXT was evaluated externally and only recorded here).

## 2026-07-21 session close (PB4 pull-assist wrap-up)

- Sessions 2026-07-19→21 in this repo were pull-assist + ledger only:
  located/verified Tim's pull_databento_daily.py (frozen PB4 spec),
  venv at ~/pb4_pull/.venv (databento 0.81.0), first run failed on a
  placeholder DATABENTO_API_KEY (env had literal dummy value — real
  key never entered this conversation); Tim ran the pull himself
  ($6.66). Acceptance 5/5 PASS on ~/pb4_pull/pb4_out/ (9 ladders,
  2019-01→2026-06-30, multi-contract; spread instruments present in
  parent symbology — flagged for downstream filtering). CSVs untouched;
  no continuous contracts, no backtests here.
- Window-ledger note committed (2aa6299): daily-ladder window eval #1
  consumed EXTERNALLY by PB4. PB4 outcome must be imported here pass
  OR fail (H3-EXT precedent).
- No hypotheses registered or evaluated in this repo this session.
- Shadow accruing through bar 2026-07-19: e4v2 signal ON (r28 +0.023,
  w 0.463); e6 eq_index 4.697; zero error lines. New log lines
  committed at close.
- test_signals.py at close: ALL 5 PASS.

## 2026-07-24 session (term-structure batch: E9/E11/E12 registered + evaluated)

- Deep-research sweep (108 agents, 25 claims adversarially verified)
  converged on ONE surviving family distinct from our 7 falsified ones:
  commodity/FX futures TERM-STRUCTURE risk premia. Rejected on
  verification or our own cost bar: Goldman-roll front-run, VIX-ETP
  flow, naive long-only roll (a "tax"), social sentiment, crypto term
  basis. Report archived: tasks/wt914flw4.output.
- Registered pre-test (Tim delegated the choice; forex added at his
  request): E9 commodity basis-momentum, E11 commodity hedger-positioning
  (CFTC CoT), E12 FX carry via futures term structure. E10 intentionally
  RESERVED/UNUSED (dropped commodity carry, swapped for E12). Window
  amended 2005→2010-06-06 PRE-DATA (GLBX.MDP3 availability).
- DATABENTO KEY IS AVAILABLE IN-SESSION (real db- prefix, 32 chars) —
  pulls can run here, not only Tim-local (updates the prior record).
  Pulled 22 daily expiry ladders (14 commodity + 8 FX), 2010-06→2026-06,
  quoted $43.63 / ~$100 first. Free CFTC CoT built: data/cot/cot_hedgers.csv
  (12,082 weekly rows, 14 roots, hedgers net-short all 14 — theory-consistent).
- NEW CODE (all committed/pushed): term_structure.py (pure), ladder_loader.py,
  cot_loader.py, termstructure_backtest.py (engine+gates), phase2_termstructure.py
  (one-shot driver). Machinery proven on SYNTHETIC first: test_term_structure.py
  28/28 (no-splice, no-lookahead, decode, signs, neg-price guard),
  test_backtest.py engine (aligned earns / reversed loses / book-level
  truncation-invariance exact). Negative-WTI Apr-2020 (CLK0 −2.67) handled
  by an outcome-neutral non-positive-price guard.
- RESULTS (each single registered run; all in HYPOTHESES.md):
  * E9  FAIL 1/6 — n=294, PF 1.08, half1 −0.25, plateau only lb6 positive
    (12/18 negative), P(maxDD>40%) 0.84, Sharpe 0.03 < bench 0.31, final
    0.87x, maxDD −52%. 8th falsified family.
  * E11 FAIL 2/7 — n=146, corr(E9) −0.008 PASS (genuinely distinct), but
    PF 1.10, half1 −0.02, plateau 4wk negative, P(maxDD>40%) 0.77, Sharpe
    0.12 < 0.31, final 1.16x, maxDD −56%. Real+distinct but sub-friction
    (E5/E7 signature). 9th falsified family.
  * E12 PASS 6/6 — n=115, PF 1.72, both halves +, plateau {1,3,6}mo all
    positive & monotone, P(maxDD>40%) 0.038, Sharpe 0.334 vs bench −0.092,
    final 1.55x, maxDD −24%. First pass since E4-v2/E6, on fresh FX data.
- E12 INDEPENDENT AUDIT (gate-auditor, clean re-derivation): CONFIRMED
  all 6 gates reproduce exactly; no lookahead, correct carry sign, costs
  over-charged, no fabrication. BUT stands with TWO SERIOUS CAVEATS:
  (A) ruin-gate pass is LITERAL-ONLY — gross-cap binds 96.6% of days
  holding vol at ~7.4% not 15%; at the registered 15% target the same
  book gives P(maxDD>40%)=0.56, maxDD −45.5% (fail). The 0.038 does NOT
  license 15%-vol deployment; this session's "vol-targeting tamed the
  skew" claim was WRONG and is corrected on the record. (B) ~84% of P&L
  is 2019–2026 (overlaps unresolved PB4 on 4/8 names incl. AUD); clean
  2010–2018 is FLAT (Sharpe 0.089). Verdict: confirmed-but-MARGINAL —
  same wall as E4/E5 (real signal, capital-constrained). NO gate marker.
- Bug fixed post-audit: episode_pnl hard-coded 5.0 bps → parameterized;
  E12's logged run used 5.0 (conservative vs its 3.0) and was NOT re-run.
- Shadow E4-v2/E6 still accruing (logs updated); untouched by this batch.

## 2026-07-24b session (E14 threshold-rebalancing: registered, falsified; edge well found dry)

- Tim asked for an all-out push to discover/create/test a NEW profitable
  edge ("do not stop until achieved"). REFRAMED up front: cannot promise a
  PASS without p-hacking (testing until one clears by luck is the exact
  failure the program exists to prevent); committed instead to the most
  aggressive DISCIPLINED discovery pass — register, test once, report.
- Focused deep-research sweep (106 agents, 25 claims adversarially
  verified; report tasks/wt2kwaacd.output). ALL FOUR seed candidates
  KILLED on their own evidence: (A) overnight equity drift documented
  DEAD post-2021 by its NY-Fed discoverers (2-3am window → ~0 since 2021;
  NightShares ETFs launched 2022, closed 14mo later); (B) VIX/VX carry
  ruinous (12-29% DD gross) + no micro contract; (C) crypto
  cross-sectional collapses to 5-MIN reversal (market-making), no slow
  structural premium; (D) month-end FX fix flow sub-friction, 72% reverts
  by next noon, WM fix widened 2015. One distinct lead survived:
  institutional 60/40 THRESHOLD rebalancing (Harvey-Mazzoleni-Melone 2025).
- Registered E14 (threshold band-breach 60/40 rebalancing, equity leg on
  MES) pre-test with the constitution-required E5-escape argument
  (magnitude-conditioning on band breach vs falsified E5 firing every
  month-end on tiny drifts). Reused es_zn_1d.csv (disclosed 2nd use); no
  data/spend. Machinery-first: rebalance_threshold.py (pure) + test_e14.py
  11/11 on SYNTHETIC (roll-safe returns, trigger dir, sub-band silence,
  exact P&L, roll exclusion, book reset, no-lookahead) before the window.
- E14 VERDICT: **FAIL — 4/6.** n=**17** trigger trades at δ=0.04 over 16
  YEARS (28/17/14 at δ 0.03/0.04/0.05; ≈1 trade/yr, gate ≥100 FAIL);
  half2 −$891 (FAIL); PF 1.350 PASS, plateau all-positive PASS
  (+$1,322/+$516/+$134), ruin gate 4.3% PASS. This is an UNDERPOWERED,
  too-rare-to-matter death — DIFFERENT from E5's sub-friction death, and
  regardless of edge sign ~1 trade/yr is no strategy for a $2-5k account.
  At n=17 the positive PF/plateau are NOISE. TENTH falsified family; per
  the registration the MANDATED-REBALANCING FAMILY IS CLOSED (calendar +
  threshold both dead). No retune permitted.
- Baseline test_signals.py 5/5 PASS at close. E4-v2/E6 shadow untouched.
- HONEST STRATEGIC FINDING: the accessible distinct-large-retail-edge well
  is now effectively DRY (10 falsified families; the research + E14
  exhausted the one surviving lead). Forward value is NOT more discovery —
  it is validating/combining what already passes. The two legitimate paths
  need NO new edge: (1) resolve PB4 → unlock an E12(FX-carry)×E4-v2(trend)
  blend (uncorrelated sleeves → deployable Sharpe neither clears alone);
  (2) let the E4-v2/E6 Phase-4 shadow mature to ~2026-10-14 (the real gate
  to capital). Both are Tim-decision / calendar-bound, not code-bound.

- GAP-FILL SWEEP (Tim-requested "exhaust the last gaps"; 89 agents,
  report tasks/w5108tdqm.output) — CLEAN NULL, nothing survives both walls
  + distinctness: (1a) crypto BAB/low-vol not even an identified crypto
  factor (subsumed by size+momentum); (1b) crypto SIZE real in-sample
  2014-18 but net-of-cost survivability REFUTED 0-3, illiquidity trap on
  tiny coins; (1c) crypto staking-yield/basis carry ZERO evidence,
  unevidenced; (2) treasury roll-down carry = same global-recession crash
  profile as marginal E12 FX carry (KMPV 2018), and the one distinct rates
  mechanism (dealer balance-sheet inconvenience yields, He-Nagel-Song) is
  crisis-only (COVID/2008) + levered-basis-desk capital, not a retail
  roll-down book. NONE registered (registering a refuted-survivability or
  same-as-E12 candidate would be knowingly-doomed padding). Two research
  sweeps (195 agents total) + E14 now EXHAUST the accessible
  distinct-large-retail-edge space. Discovery is closed for this cycle.

## Single next action (2026-07-24b)

Tim to identify what "PB4" is (it lives only in the parallel cloud
session) — it is now the gating decision for the ONLY live path to a
deployable result: the E12(FX-carry)×E4-v2(crypto-trend) blend, whose FX
leg is E12 and is contaminated/marginal until PB4 is reconciled. Until
then: no new discovery registrations (edge well is dry — manufacturing
more would be padding/p-hacking); E4-v2/E6 shadow continues accruing to
~2026-10-14 untouched.

---

## 2026-07-25 session (4 public indicators audited via a separate Claude
Code session; E16/E17 registered; loader wired; ID-collision near-miss
caught and fixed)

- SOURCE: not this session's own discovery sweep — Tim supplied 5 public
  indicator scripts (Alpha-Scope, Capitulation Finder, Ichimoku TK Cross,
  MTF Compass Pro, a Livermore-style pivot-structure indicator) to a
  separate Claude Code session working from a stale (2026-07-21) clone,
  for structural audit + translation into registerable hypotheses. This
  note reconciles that session's output into canonical STATE/HYPOTHESES.
- Audit found real, worth-recording bugs in the source indicators
  BEFORE any of them were ported: (1) Alpha-Scope computes its trend
  filter twice under two names and never actually uses its own
  "momentum" percentile block — dead code relative to the signal; (2)
  the pivot-structure indicator has a genuine repaint/lookahead bug (a
  pivot at bar i is used before the right-side bars needed to confirm it
  have elapsed) plus an O(n²) hot loop; (3) MTF Compass Pro's slope-
  normalization formula divides a raw price diff by a percentage number
  without unit conversion, making its "meaningful slope" filter almost
  always true (99.6% of bars in a test). All three fixed in the ports,
  not just noted.
- ID-COLLISION NEAR-MISS (caught before any push, no damage done): that
  session's stale clone predated this cycle's E9/E11/E12/E14
  term-structure batch and the reserved-E10 note above. Its drafted
  registrations (originally numbered E9-E12) would have collided with
  real, already-evaluated entries and the deliberately-reserved E10 slot
  if applied as-is. Caught on a fresh clone diff, confirmed the original
  E1-E8-R corpus is untouched (byte-identical), and renumbered
  E9->E15, E10->E16, E11->E17, E12->E18 (all files, imports, docstrings,
  cross-references) before touching this repo. Tim confirmed proceeding
  despite the "no new discovery registrations" note above (2026-07-24b)
  — these came from a separately-sourced audit, not the commodity/FX
  discovery sweep that note was scoped to.
- REGISTERED (pre-test, not evaluated): **E16** (Capitulation Finder ->
  volume-confirmed mean reversion, BTC+ETH daily) and **E17** (Livermore
  pivot-structure breakout, BTC daily). Full rationale/rules/gates in
  HYPOTHESES.md. **E15** (Alpha-Scope channel breakout) and **E18**
  (regime-switch combining E16 range-mode / E17 trend-mode, gated by a
  simplified MTF-Compass-derived classifier) are drafted
  (E15_HYPOTHESIS_DRAFT.md / E18_HYPOTHESIS_DRAFT.md) but deliberately
  NOT registered here — E15 carries a registered prior-against (cousin
  of the falsified breakout/momentum families), E18 is explicitly
  sequenced after E16/E17 have real standalone numbers (E4->E4-v2
  precedent).
- DATA LOADER GAP FOUND AND FIXED: crypto_trend.py's load_yahoo_daily
  only ever fetched open/close (fine for E4's trailing-return signal,
  insufficient for E16's volume filter or E17's high/low pivot
  detection). New `load_yahoo_daily_ohlcv` added to e16_capitulation.py
  and e17_pivot_structure.py (duplicated per this repo's existing
  per-module loader convention). REAL DATA-QUALITY BUG caught while
  building it: fetching Yahoo's chart API with `range=max` silently
  returns ~monthly-spaced bars while still claiming `interval=1d` and
  setting no error field (confirmed: a BTC-USD range=max pull came back
  as 143 "daily" bars over 12 years). Fixed by fetching with explicit
  `period1`/`period2` Unix-timestamp bounds instead (verified: 4330
  true daily bars, every gap exactly 1 day). The loader now asserts
  this itself (`_assert_daily_spacing`) with a permanent regression test
  in test_e16.py/test_e17.py, so a future accidental range=max re-fetch
  fails loudly instead of silently feeding monthly bars into RSI(14)/
  SMA(50)/pivot(10) windows sized for daily data.
- Data fetched and loader-verified (shape/dtype/spacing/OHLC ordering
  ONLY — not run through compute_signals/run_backtest, which would be an
  actual evaluation): data/btc_usd_1d.json (4330 bars, 2014-09-17 ->
  2026-07-25), data/eth_usd_1d.json (3181 bars, 2017-11-09 ->
  2026-07-25), both gitignored per repo convention, zero nulls.
- Machinery tests: test_e15.py 8/8, test_e16.py 8/8 (incl. 2 new
  spacing-guard tests), test_e17.py 8/8 (incl. pivot-availability-shift
  correctness + fast-vs-bruteforce reaction-tracking equivalence, 0
  mismatches/2000 synthetic bars), test_e18.py 5/5 — all synthetic data
  only, all passing before this commit.
- NOT done: no hypothesis has been evaluated on real data. E16/E17 are
  registered and loader-ready; running them is still a separate,
  explicit instruction per .claude/skills/register-hypothesis.

## Single next action (2026-07-25)

Run E16 and E17 (real BTC/ETH daily data in hand, loader verified) --
or register E15/E18 first if that's preferred; either way, that decision
and the actual run are Tim's explicit next step, not automatic from
registration. Separately, the 2026-07-24b blocker above (PB4
reconciliation, gating the E12xE4-v2 deployment path) is untouched by
this session and still stands on its own track.

---

## Previous state (2026-07-15c, session: E5 + E4-v2 evaluations)

## What changed this session

- HYPOTHESES.md canonical file confirmed UNRECOVERABLE (exhaustive search:
  machine, trash, .xfer chunks, all Claude transcripts, GitHub incl. private
  repos via authed SSH + logged-in web). Old H1/H2: UNTESTABLE — lost in the
  Windows→Ubuntu wipe. Noise-area edge ARCHIVED as falsified.
- Repo pushed to github.com/tburgernyc/noisebot (public; data/ excluded —
  Databento license). Process fix live: registration = commit + push.
- HYPOTHESES.md v2 written; E1 and E2 registered pre-test with Tim's
  approval, then evaluated ONCE each (log: logs/phase2_e1e2_2026-07-15.log).
- New code: edges.py (E1/E2 pure logic), test_edges.py (11/11 PASS incl.
  no-lookahead truncation invariance on real data), phase2_e1e2.py (gate
  runner reusing baseline metrics/barrier-MC). Baseline suite still green.
  noise_area.py untouched.

## Verdicts

- BASELINE (noise-area): FAIL — PF 0.98, n=512. Archived falsified.
- H1/H2 (old):           UNTESTABLE — registered definitions lost.
- E1 (ORB+compression):  FAIL — PF 1.12, n=183, half2 negative, OR10
                          plateau negative, P(blow) 50.9%. Falsified.
- E2 (VWAP reversion):   FAIL — PF 0.79, n=818, everything negative.
                          Falsified decisively.
- E3 (last-hour flow):   FAIL — PF 0.81, n=503. Falsified.
- E4 (BTC trend, full):  FAIL 6/7 — PF 2.86, n=167; ruin gate failed.
- E5 (month-end rebal):  FAIL — PF 1.06, n=771; mechanism real but edge
                          ~$2.85/trade, below retail viability. Falsified.
- E4-v2 (vol-targeted):  **PASS 7/7** — PF 2.84, n=167, maxDD -26%,
                          Sharpe 1.38 vs 0.96 bh. FIRST GATE PASS.
                          → Phase 4 shadow (90 days), NOT capital.

## Window ledger

Databento MNQ 2024-07→2026-07: 4 evaluations burned (baseline, E1, E2, E3). Window heavily mined — prefer NEW data for next registration.
Yahoo 60-day: burned for selection (data-QA only).

## Blockers

None mechanical. The blocker is intellectual: no registered hypothesis
with a mechanism distinct from the three falsified families.

## Parallel track (income)

Prop-firm risk guard EA (MQL5 marketplace utility) — spec at
~/mql5_products/prop_risk_guard/SPEC.md. Sells enforcement, not
performance. Zero client interaction.

## Single next action

Trading: build E4-v2 Phase 4 shadow logger (daily signal + w_t to
signals.jsonl, cron 00:05 UTC; 90-day gate registered in HYPOTHESES.md).
Income: build PropGuard EA v0.1 per ~/mql5_products/prop_risk_guard/SPEC.md.
