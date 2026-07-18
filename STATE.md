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
- Open housekeeping: two clones exist (~/noise_bot runs crons,
  ~/noisebot is the working copy) — pick the canonical one before the
  next substantive session and align commits.

## Single next action (2026-07-18)

Register the next hypothesis via /register-hypothesis with a mechanism
distinct from the falsified families (always-on momentum, ORB, VWAP
reversion) — the E4-v2/E6 shadow runs itself until ~2026-10-14.

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
