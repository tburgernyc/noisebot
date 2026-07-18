---
name: register-hypothesis
description: Pre-register a strategy variant or parameter change in HYPOTHESES.md BEFORE any backtest touches it. Enforces non-negotiable #2. Use whenever a new idea, filter, parameter, instrument, or variant is proposed for testing.
---

# Register hypothesis

Collect and write a HYPOTHESES.md entry with ALL of the following
before any code runs. Refuse to backtest until the entry exists.

Required fields:
- **ID** (H4, H5, ...) and one-line name.
- **Economic rationale**: why this edge/modification should exist in
  market microstructure terms. "It might improve PF" is not a
  rationale — reject it and ask for the mechanism.
- **Exact specification**: parameters fixed in advance, no ranges to
  be chosen after seeing results. A range is allowed ONLY as a
  pre-declared plateau check (all values must pass, not best-of).
- **Prediction**: what result is expected if the hypothesis is true,
  and what result falsifies it.
- **Data window**: which data it will be evaluated on, and
  confirmation that window is not already burned for selection
  (the 60-day Yahoo Tier A window is burned; final OOS windows are
  single-use per hypothesis).
- **Decision rule**: what happens on pass and on fail. Fail = recorded
  and abandoned, not tweaked-and-retried.

After writing the entry, echo it back and stop. Running the test is a
separate, explicit user instruction.
