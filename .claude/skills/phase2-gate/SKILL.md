---
name: phase2-gate
description: Run the full Phase 2 gate evaluation on the current backtest and report PASS/FAIL against the five pre-registered criteria, each with sample size. Use when a backtest run is complete and the user asks whether Phase 2 passes.
---

# Phase 2 gate evaluation

1. Run `python3 backtest.py` (or the Databento-era equivalent) fresh —
   never evaluate from remembered or pasted numbers.
2. Report each criterion separately, with its n, on NQ (the primary):
   - PF > 1.3                      → value, n trades
   - n >= 100 trades               → n
   - Both sample halves profitable → half1 $, half2 $, n each
   - Lookback plateau 10/14/20 all positive → totals + n each
   - Barrier-MC P(blow) < 10% at buffer-aware sizing → P(blow),
     P(pass), n paths, and the empirical trade-count feeding it
3. Then report the H3 family evidence (ES/YM/RTY confirms, GC/CL
   controls) as context — it does NOT substitute for the NQ gate.
4. Verdict: PASS only if all five NQ criteria hold. Anything else is
   FAIL. On FAIL: stop, summarize which criteria failed and by how
   much, and propose modifications ONLY as new /register-hypothesis
   entries. Never adjust and rerun in the same breath.
5. On PASS: instruct the USER to create `.gates/phase2_passed`
   themselves (`mkdir -p .gates && touch .gates/phase2_passed`).
   Claude never creates this file. Then hand off to the gate-auditor
   subagent for independent confirmation before the user does so.
