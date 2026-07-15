# STATE — noise_bot

Updated: 2026-07-15 (session: E1/E2 registration + evaluation, Cowork + Desktop Commander)

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

## Window ledger

Databento MNQ 2024-07→2026-07: 3 evaluations burned (baseline, E1, E2).
Yahoo 60-day: burned for selection (data-QA only).

## Blockers

None mechanical. The blocker is intellectual: no registered hypothesis
with a mechanism distinct from the three falsified families.

## Single next action

Tim picks the next edge FAMILY (different mechanism, session, or
instrument — not a variant of the three falsified ones). It gets an
economic rationale in HYPOTHESES.md BEFORE any code runs. No backtests
until then.
