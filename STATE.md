# STATE — noise_bot

Updated: 2026-07-18 (session: harness verification + ledger reconciliation)

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

## Single next action (2026-07-18e)

FIRST: close out the parallel cloud session — tell it the pull is
cancelled (data already owned, window burned) so it never runs.
Then: run /hooks once (or restart) to load the fixed hook config, then
register the next hypothesis — mechanism must clear SIX falsified
families (always-on momentum, ORB, VWAP reversion, last-hour flow,
funding carry, fast crypto trend); E4-v2/E6 shadow runs itself until
~2026-10-14 and remains the only live pipeline work.

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
