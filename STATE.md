# STATE — noise_bot

Updated: 2026-07-26 (session: E19-v2 -- real Binance perp mark-price sourced, replacing E19's spot proxy; PASSED 7/7 with a now-REAL attribution gate that could have failed; audit-confirmed, two self-reported precision corrections)

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

## 2026-07-25b session (E16/E17 evaluated, both falsified; audit caught and fixed 2 real bugs pre-record)

- Tim instructed: run E16 and E17. Both evaluated ONCE each, per their
  registrations, using data/btc_usd_1d.json + data/eth_usd_1d.json
  (already fetched) and a freshly-pulled data/sol_usd_1d.json (needed
  for E6 reconstruction, the correlation gate's comparison point; not
  committed, gitignored per repo convention).
- BEFORE writing anything to HYPOTHESES.md, ran an adversarial audit
  (general-purpose agent instructed to apply the repo's own
  .claude/agents/gate-auditor.md persona) that independently re-derived
  every number via fresh reruns, not just re-reading logs. It confirmed
  both FAIL verdicts and found two real, worth-fixing issues:
  1. Neither phase2_e16.py nor phase2_e17.py had committed,
     reproducible code for the required correlation-vs-E4-v2/E6 gate —
     the numbers had been computed in an ad hoc, uncommitted script.
     Fixed: correlation computation (reconstructing E4-v2 via
     crypto_trend.run_e4_voltarget and E6 via portfolio_trend.run_e6 on
     the same data) added directly into both phase2 scripts, matching
     the phase2_e7.py/phase2_e8.py precedent the audit pointed to.
  2. e16_capitulation.py's run_backtest() had a genuine fill-timing bug:
     exits were marked to market using the full close-to-close return
     through the exit bar, then had cost applied on top — meaning exits
     effectively filled at the NEXT bar's close, not its open, despite
     the function's own docstring claiming next-open fills for both
     entries and exits. Entries were already correct. Found via a clean
     synthetic zero-cost trace (see the fix's docstring in
     e16_capitulation.py for the exact repro). Fixed by splitting each
     transition bar into an exposed segment (up to the fill point) and
     a flat segment; re-verified against test_e16.py (8/8 still pass)
     BEFORE re-running the registered evaluation. The fix changed E16's
     exact numbers (PF 0.709->0.662, etc.) but not the verdict — still
     a decisive 5/6-gate fail either way.
  3. Also flagged (not fixed, does not block anything): e18_regime_
     switch.py's e16_position_series() adapter has a timing-convention
     mismatch with how run_backtest() consumes its output — noted
     in-file for whenever E18 is actually picked up. E18 remains
     unregistered and unevaluated.
- E16 VERDICT: FAIL, 5/6 gates (n=72<100, PF=0.662<1.3, both halves
  negative, plateau all negative, bootstrap ruin 95.8%>>10%). Only the
  correlation gate passed (0.023 / 0.067 vs E4-v2/E6) — confirms the
  mechanism is genuinely uncorrelated with the trend book, as predicted,
  it just isn't profitable on this data. Full verdict + Read in
  HYPOTHESES.md.
- E17 VERDICT: FAIL on kill criterion — n=47<100 and bootstrap ruin
  74.1%>>10% both fail independently, despite PF=7.618, both halves
  positive, all 3 plateau cells strongly positive, and Sharpe 1.41 vs
  buy-hold 0.96 all passing. Structurally similar to E4's original
  story (strong average performance, fails on ruin risk at full
  sizing) — noted as an observation, NOT acted on; a vol-targeted
  sizing variant would be its own new registration (E17-v2), not run
  here. Correlation vs E4-v2/E6 (0.72/0.59) is also high enough that
  such a variant may not add much diversification even if it passed.
  Full verdict + Read in HYPOTHESES.md.
- Both hypotheses' kill criteria applied: falsified, recorded, no
  retune, no threshold search. Twelfth falsified family territory (this
  repo has now falsified: always-on momentum, ORB, VWAP reversion,
  last-hour flow, funding carry, fast crypto trend, SMC/ICT, calendar
  rebalancing, threshold rebalancing, and now volume-climax mean
  reversion (E16) and full-sizing pivot-structure breakout (E17) — exact
  family count/naming not reconciled here with the parallel
  commodity/FX track's own tally; do that reconciliation before citing
  a specific number publicly).
- Tests at close: test_e15.py 8/8, test_e16.py 8/8, test_e17.py 8/8,
  test_e18.py 5/5 — all still passing after the fix.

## Single next action (2026-07-25b)

Nothing mechanically required on the E16/E17 track — both falsified and
recorded; no live path forward on crypto mean-reversion or full-sizing
pivot-structure without a fresh, distinct mechanism (same discipline as
the commodity/FX track: don't manufacture a retune-in-disguise). The
2026-07-24b blocker above (PB4 reconciliation, gating the E12xE4-v2
deployment path) is untouched by this session and still stands on its
own track, unaffected by E16/E17. E4-v2/E6 shadow continues accruing to
~2026-10-14 untouched throughout.

## 2026-07-25c session (bottleneck diagnosis; E17-v2 falsified on n only; E19 built and PASSED 7/7 -- flagged as mechanism-pass not risk-pass)

- Tim instructed: step back, find the common bottleneck across every
  failed hypothesis, and find creative, executable, "outside the box"
  solutions, up to and including different prop firms or tickers.
  Wrote BOTTLENECK_DIAGNOSIS_2026-07-25.md, reading all 18 prior
  hypotheses fresh from HYPOTHESES.md (not from memory). Finding: the
  bootstrap ruin gate is the dominant recurring killer (E4, E9, E11,
  E16, E17 all named it explicitly; E12's own "pass" turned out to be a
  gate-auditor-caught exposure-cap artifact masking the same problem).
  Split failures into two populations: strong-edge-killed-by-tail-risk
  (E4, E17 -- a sizing fix, proven once already, fixes this) vs.
  weak-edge-where-sizing-can't-help (E9/E11/E16 -- already vol-targeted,
  still failed on thin edge). Root cause stated plainly: this repo has
  a mature hypothesis-testing pipeline and almost no risk-engineering
  pipeline -- E4-v2 is a proof of concept nobody productized into a
  repeatable second step. Four solutions ranked by confidence: (1)
  apply E4-v2's fix to E17 [[[E17-v2]]], (2) build the delta-neutral
  funding harvest E7 should have been [[[E19]]], (3) prop-firm structural
  lever (FundedNext's EOD trailing/no-consistency-rule structure fits
  E17-shaped signals better than tick-by-tick trailing firms -- research
  only, not actioned), (4) Bitcoin spot-ETF-flow signal (genuinely fresh
  mechanism, ~53bp/$100M same-day correlation per cited research -- no
  data pipeline built, deliberately deferred past E17-v2/E19).
- Tim instructed: run E17-v2 and move E19 forward, pursue all viable
  strategies. Both registered in HYPOTHESES.md pre-test, both evaluated
  ONCE each, both sent to independent adversarial audits (separate
  general-purpose agents, repo's own .claude/agents/gate-auditor.md
  methodology, no access to this session's reasoning) before any
  verdict was written to the permanent record.
- E17-v2 (E17's unchanged signal, vol-targeted exposure -- direct reuse
  of E4-v2's proven construction): audit independently re-derived every
  gate from scratch (manual PF/Sharpe/maxDD, 5-seed + 50k-path
  bootstrap check, real-BTC-data lookahead perturbation test, entry/
  exit-date cross-check proving all 47 trades are byte-identical in
  timing to E17's own 47). Confirmed, no bugs. VERDICT: FAIL, kill
  criterion (n=47<100 only; PF 5.16, both halves positive, plateau all
  positive, bootstrap ruin 0.0% robust, Sharpe 1.50>0.96bh all PASS).
  Exactly the outcome predicted in the pre-registration: sizing
  mechanism confirmed working, frequency problem confirmed separate
  and unsolved. Full verdict in HYPOTHESES.md.
- E19 (delta-neutral BTC/ETH/SOL perp funding-rate harvest -- short
  perp + long spot, hedged, long-funding-collection side only, hysteresis
  entry/exit on trailing 3-day funding): built from scratch this
  session. Fetched 226 Binance monthly funding archives (data/funding/,
  matches E7's original data note exactly). New module
  e19_funding_basis.py (run_e19_single, run_e19 -- equal-weight 3-asset
  combination, deliberately NOT a book-level dot-product like E6/E7,
  to avoid an undisclosed-leverage artifact); test_e19.py 8/8 on
  synthetic data including a dedicated hedge-neutrality check. Registered
  in HYPOTHESES.md (7 gates -- the standard set plus a stricter
  attribution gate than E7's, plus correlation as a hard gate not just
  reported). Evaluated ONCE (logs/phase2_e19_2026-07-25.log): n=140
  (BTC48/ETH36/SOL56), PF=9.075, both halves positive, plateau clean
  across all 3 threshold pairs, bootstrap P(maxDD>40%)=0.0%, attribution
  and correlation (0.07/0.10 vs E4-v2/E6) both clear. **PASS 7/7 --
  first hypothesis in this repo's history to clear every registered
  gate cleanly on its first run.**
  Audit independently confirmed no implementation bug changes any gate,
  AND surfaced the load-bearing caveat that must travel with this
  result everywhere it's cited: the perp leg is priced off the SAME
  spot-close array as the spot leg (disclosed before the run), so the
  combined price-leg P&L is exactly, algebraically 0.0 every day --
  not small, zero. That makes the attribution gate a tautology, not a
  measurement, and means the Sharpe-7.2/maxDD--2.8% numbers describe a
  world with zero spot/perp basis risk, zero cross-venue slippage, zero
  liquidation risk, zero counterparty risk -- precisely the channels
  the hypothesis draft itself flagged as widening exactly during the
  high-funding regimes this strategy targets. **This is a mechanism/
  signal-timing pass, not a real-world-risk pass.** What IS validated:
  funding-sign timing logic is real and lookahead-free, 140 episodes
  are economically plausible (median hold 10 days, not flicker noise),
  and the low correlation to the existing trend book is real, not an
  artifact. What is NOT validated: hedge quality under real market
  stress -- the actual question a capital decision needs answered.
  Two minor non-gate-affecting audit findings recorded in HYPOTHESES.md:
  a SOL price-vs-funding start-date documentation imprecision (~2.5%
  relative inflation of the total-return multiple during a 92-day
  window, zero effect on maxDD or any gate), and a correlation-
  comparator data-provenance caveat shared with E17-v2 (rebuilt from
  data/*_usd_1d.json, not the exact byte-identical files E4-v2/E6's own
  original registrations used, which no longer exist in the repo).
- Prop-firm and ETF-flow fronts from the diagnosis: NOT actioned this
  session, deliberately -- the diagnosis doc itself sequenced them
  after E17-v2/E19 were through the pipeline, and both are separate,
  larger undertakings (a real deployment-structure decision; a new
  data pipeline) rather than a follow-up to already-built code. Left
  as explicit options for the next round, not silently dropped.
- Tests at close: test_e17.py 9/9, test_e19.py 8/8 -- all green.
- Both hypotheses' outcomes recorded in HYPOTHESES.md with full,
  independently-audited verdict text (E17-v2: falsified/kill criterion;
  E19: passed, with the mechanism-vs-risk distinction stated as the
  headline, not a footnote).

## 2026-07-26 session (E19-v2: real perp marks sourced; PASSED 7/7 with a genuinely falsifiable attribution gate)

- Tim instructed: source real Binance perp mark-price history for E19,
  then (after reviewing the basis analysis) "build it".
- Fetched 226 monthly Binance USDS-M mark-price kline archives into
  data/perp_mark/ (gitignored) -- coverage matches the funding data
  exactly: BTC/ETH 2020-01-01->2026-06-30, SOL 2020-09-13->2026-06-30.
- REAL DATA-FORMAT BUG FOUND AND FIXED BEFORE ANY NUMBER WAS COMPUTED:
  Binance's own monthly kline archives before ~2022-02 ship with NO
  header row; later ones DO. A naive uniform pd.read_csv across all 226
  files silently misaligns columns (one file's first data row is read
  as that file's header), corrupting the whole concatenated frame --
  visible as nonsense column names and a NaT max index. load_mark_price_
  daily() now detects and normalizes per file. Worth remembering for
  any future registration reusing Binance kline archives.
- Pre-registration basis analysis (exploratory, no gate computed):
  average daily |basis| is small on BTC/ETH (0.10-0.18%) and IS larger
  on hot-funding days than otherwise (BTC 0.131 vs 0.100; ETH 0.177 vs
  0.101) -- the audit's predicted direction, confirmed. SOL carries a
  16.65% one-day basis blowout on 2022-11-09 (FTX collapse), verified
  against raw OHLC, not a parsing artifact.
- E19-v2 registered pre-test in HYPOTHESES.md (gates IDENTICAL to E19's
  bar; plateau NOT re-swept; only ONE input changed -- what prices the
  perp leg). run_e19_single/run_e19 left byte-for-byte untouched;
  run_e19_single_v2/run_e19_v2/load_mark_price_daily are additive.
  test_e19.py 8/8 -> 13/13, including a perp-equals-spot regression
  proving v2 reduces to v1 when there's no basis, and an independent-
  replay check that real divergence lands in attribution correctly.
- E19-v2 VERDICT: **PASS 7/7.** n=140, PF 6.780, both halves positive,
  plateau all positive, bootstrap P(maxDD>40%) 0.0%, attribution 7.0%
  (gate <20%), correlation -0.036/-0.083 (gate <=0.5).
  **The key difference from v1: this attribution gate could actually
  have failed and didn't.** v1's price leg was identically 0.0 by
  construction (tautology); v2's is a real -0.0507 cumulative hedge-
  slippage cost measured against real mark prices. Sharpe fell 7.2 ->
  1.483 and maxDD widened -2.8% -> -6.6%: worse and more believable,
  exactly the direction expected when a real risk channel stops being
  assumed away.
- Independently audited at a deliberately higher bar (a SECOND clean
  sweep warrants more scrutiny, not less): two from-scratch engine
  reimplementations, ~220k bootstrap paths across 10 seed/path-count
  combos, adversarial per-bar-noise perturbation at 11 real hedged
  bars, and hand-computation of the FTX-window trades from raw CSVs.
  CONFIRMED, and it caught two precision errors in my own write-up,
  both recorded in HYPOTHESES.md rather than papered over:
  1. Trade TIMING is not exactly unchanged vs v1 (count is): one BTC
     entry shifts 2021-07-02 -> 07-03, because 2021-07-01 is a genuine
     one-day hole in Binance's perp-mark archive landing exactly on the
     day the entry threshold first crossed, and v2's decision gate
     needs BOTH legs valid. Data-availability effect, NOT price-driven
     (price levels never touch entry/exit) -- 1/140 trades, 0.008% of
     BTC funding attribution.
  2. Gap-day docstring said "zero P&L"; in fact only the PRICE leg is
     zeroed, funding still accrues on a held position (deliberate --
     the funding print is real, the hole is in the mark archive). 10
     instances, +0.0024 raw funding, ~0.11% of total. Docstring
     corrected; no behavior changed; run re-verified byte-identical.
- FTX-collapse window, hand-verified: BTC hedged 11-08->11-10 LOST
  0.52% on realized basis; SOL hedged 11-07->11-09 GAINED 0.47% (its
  perp fell harder than spot, and this position is short the perp);
  ETH not hedged. One helped, one hurt -- not uniformly flattering.
  Note SOL had already exited before 11-09, the worst dislocation day,
  so the mechanism did not actually sit through the worst moment --
  timing luck on this occasion, not a demonstrated property.
- Tests at close: test_e19.py 13/13; phase2_e19v2.py byte-for-byte
  reproducible; phase2_e19.py (v1) still reproduces its own log.

## Single next action (2026-07-26)

E19-v2 has cleared every registered gate with a genuinely falsifiable
attribution gate, real basis data, and an independent audit at an
elevated bar. The remaining gap is no longer modeling -- it is
execution realism. **The single blocking next step is paper/shadow
exposure** (daily signal + both legs logged, sized as edge measurement
not capital), because the backtest is daily-close granularity and
models none of: intraday perp liquidation mechanics, funding-settlement
timing risk, spot-borrow/margin constraints, or exchange/counterparty
risk. Precedent for exactly this step exists in-repo: E4-v2 went to a
90-day Phase 4 shadow before any capital discussion, and that shadow is
still accruing (~2026-10-14). A vol-targeted / capital-efficiency
sizing variant is explicitly NOT registered (E19-v3 territory, E4->E4-v2
precedent). Untouched and still standing on their own tracks: the PB4
reconciliation blocker (2026-07-24b), the wider-alt-universe option for
E17-v2, the FundedNext deployment-structure re-expression, and the
Bitcoin spot-ETF-flow signal (still needs a data pipeline built).

## Single next action (2026-07-25c)

E19 is NOT ready for a shadow/capital decision despite the clean gate
sweep -- the honest next step, stated in the hypothesis draft and
confirmed necessary by the audit, is either (a) sourcing real Binance
perp mark-price history to replace the spot-proxy simplification and
registering a fresh evaluation against it (E19-v2 territory, same
E4->E4-v2/E17->E17-v2 precedent: a new registration, not a silent edit
to this one), or (b) a paper/shadow exposure that experiences actual
spot/perp basis behavior directly. Secondary, lower-urgency options on
the table from the diagnosis, neither started: a pre-registered wider
liquid-alt universe for E17-v2 if n=47 is worth chasing further; the
FundedNext-vs-generic-40%-bar deployment-structure re-expression for
E17-v2/E4-v2; the Bitcoin spot-ETF-flow signal (needs a new data
pipeline, fully unbuilt). E4-v2/E6 shadow continues accruing to
~2026-10-14 untouched throughout this entire session.

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
