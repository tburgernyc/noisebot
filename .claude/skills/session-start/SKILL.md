---
name: session-start
description: Open a noise_bot working session. Reads STATE.md, HYPOTHESES.md, and STRATEGY_SPEC.md, restates the current blocker and the single next action, and refuses to start side-quests. Run at the start of every session.
---

# Session start

1. Read STATE.md, HYPOTHESES.md, STRATEGY_SPEC.md in full. If STATE.md
   is missing, create it from the "Current state" section of CLAUDE.md
   and say so.
2. Output, in under 10 lines: current phase, the single blocker, the
   registered next action, and any gates recently passed/failed with
   their n.
3. If the user's opening request does not advance the blocker, name
   that explicitly ("this is a side-quest; the blocker is X") and ask
   for a one-word confirmation before proceeding with it anyway.
4. Never begin backtesting any variant not already in HYPOTHESES.md —
   route to /register-hypothesis first.
