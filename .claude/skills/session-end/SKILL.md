---
name: session-end
description: Close a noise_bot working session. Updates STATE.md with what changed and the single next action, records any test/gate results with sample sizes, and commits. Run before ending every session.
---

# Session end

1. Append to STATE.md (dated): what changed this session (files,
   decisions, results — every metric with its n), what was attempted
   and failed (failures stay on the record), and THE single next
   action (one line, concrete, runnable).
2. If any hypothesis was tested, confirm its outcome is recorded in
   HYPOTHESES.md — pass or fail — before writing STATE.md.
3. Run `python3 test_signals.py` one final time; record the result.
4. `git add -A && git commit` with a message summarizing the session.
   Never commit anything matching *key*, *.env, or credentials (check
   `git status` output first).
5. Print the single next action as the last line of the session.
