# noise_bot — Claude Code constitution

Mission: carry the noise-area intraday momentum system (Zarattini/Barbon
edge family) through Tim's 5-phase gate process to prop-firm deployment.
The system's entire value over preset vendors is validation discipline.
Protect that above speed. Backtests are hypotheses, never forward
expectancy. Success metric: net cash withdrawn minus ALL fees.

## Current state (also see STATE.md — read it first, every session)
- Phase 2 NOT passed. Blocker: Databento pull + family backtest.
- H3 registered: cross-instrument robustness (NQ primary; ES/YM/RTY
  in-family confirms; GC/CL out-of-family controls). Gate stays on NQ.
- TQQQ rejected for prop path. Forex track (FTMO US, MT5, US100.cash)
  parked until Phase 2 passes + written automation-policy verification.

## NON-NEGOTIABLES — mechanically enforced by hooks; do not work around
1. NO execution/broker code (ib_async, tradovate, projectx, order
   placement of any kind) until `.gates/phase2_passed` exists. The
   pre-write hook blocks it. If Tim asks anyway: restate the cost
   explicitly first, and never delete the gate file yourself.
2. Pre-registration: no variant/parameter is backtested unless already
   in HYPOTHESES.md with economic rationale. Never sweep-and-select.
   Failed tests stay on the record. The 60-day Yahoo Tier A window is
   burned for selection — never tune against it.
3. Every backtest: pessimistic next-bar fills, 1-tick adverse slippage,
   $2.50/ct RT costs, 15:55 ET flatten, per-contract MNQ dollars.
   Every metric ships with its n. A green number without n is a
   violation.
4. Failed gate = stop, report, propose registered modifications. Never
   quietly retry.
5. Sizing assumes WR 5pts below backtest. Decay rule immutable.
6. Verify before asserting. Secrets (DATABENTO_API_KEY, broker creds)
   live in env vars only — never in files, commits, or output.

## Phase 2 pass definition (all required, evaluated on NQ)
PF > 1.3 AND n >= 100 trades AND both sample halves profitable AND
lookback plateau {10,14,20} all positive AND barrier-MC P(blow) < 10%
at buffer-aware sizing. Walk-forward with embargo; final OOS window
evaluated ONCE per hypothesis.

## Commands
- Tests (MANDATORY after any edit to noise_area.py; hook runs it too):
  `python3 test_signals.py`
- Backtest: `python3 backtest.py`
- Data cost quote (run before any Databento spend):
  `python3 quote_databento_cost.py`
- Shadow logger (cron): `python3 shadow_logger.py`

## Conventions
- Data contract: tz-aware America/New_York-indexed OHLCV DataFrame.
  Any new loader (Databento) must satisfy it and pass test_signals.py
  unchanged.
- Pure signal logic stays in noise_area.py: no I/O, no broker imports.
- Continuous-contract roll days: prev_close must come from the same
  contract's prior session or the day is excluded from band inputs —
  never splice across a roll silently.
- Report money per-contract in instrument dollars; state the
  multiplier used (MNQ $2/pt, MES $5/pt, MYM $0.50/pt, M2K $5/pt).

## Session protocol
- Start: run /session-start (reads STATE.md, HYPOTHESES.md,
  STRATEGY_SPEC.md; names the blocker).
- End: run /session-end (updates STATE.md: what changed + the single
  next action).
- If a session is re-polishing artifacts instead of advancing the
  blocker in STATE.md, say so and redirect.
