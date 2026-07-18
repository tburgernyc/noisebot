# noise_bot × Claude Code — Setup & Execution Guide

Goal: run the 5-phase validation pipeline in Claude Code with the
non-negotiables enforced by machinery, not memory, ending in a live
prop-firm deployment. One honest sentence before the steps: nothing
below manufactures profit — the edge either survives Phase 2 on real
data or it doesn't. What this harness guarantees is that the answer you
get is trustworthy, which is the only kind of answer real capital
should ever ride on.

---

## PART A — One-time setup (~30 minutes)

### A1. Install / update Claude Code
Follow the official install instructions at
https://docs.claude.com/en/docs/claude-code/overview (npm package:
`@anthropic-ai/claude-code`). If already installed, update to current.
Verify: `claude --version`.

### A2. Drop this harness into the repo
Unzip the bundle so that, inside `noise_bot/`, you have:

    noise_bot/
      CLAUDE.md                      <- project constitution
      SETUP_GUIDE.md                 <- this file
      quote_databento_cost.py        <- from last session
      .claude/
        settings.json                <- wires the hooks
        hooks/gate_guard.py          <- blocks broker code pre-Phase-2
        hooks/post_edit_tests.py     <- auto-runs test_signals.py
        skills/session-start/SKILL.md
        skills/session-end/SKILL.md
        skills/register-hypothesis/SKILL.md
        skills/phase2-gate/SKILL.md
        agents/gate-auditor.md

Then: `chmod +x .claude/hooks/*.py`

### A3. Create the two ledger files if missing
- `STATE.md` — current truth. Seed it with: Phase 2 in progress;
  blocker = Databento pull; H3 registered; TQQQ rejected; forex/FTMO-US
  parked (eligible, MT5-only, US100.cash noted).
- `HYPOTHESES.md` — the pre-registration ledger. Seed with H1
  (relative-range regime filter), H2 (dual trail), H3 (cross-instrument
  robustness) including the H3 terms agreed in chat: unchanged
  baseline, NQ gate primary, ES/YM/RTY confirms, GC/CL controls,
  deployment by liquidity/cost not best-backtest, in-family failure
  counts as evidence against NQ too.

### A4. Bring your claude.ai skills into the repo (optional but useful)
Your `trading-bot-builder` skill (5-phase methodology) lives in your
claude.ai project. Copy its SKILL.md into `.claude/skills/
trading-bot-builder/SKILL.md` so Claude Code enforces the same
methodology locally.

### A5. Secrets
`export DATABENTO_API_KEY=...` in your shell profile. Never in files.
The gate_guard hook blocks hardcoded-secret patterns as a backstop,
but the rule is: keys exist only in env vars.

### A6. Smoke-test the harness (5 min, do not skip)
Start `claude` in the repo and verify each guard actually fires:
1. Type `/session-start` — it should read the ledgers and name the
   blocker.
2. Ask it to "create executor.py that places a Tradovate order" — the
   PreToolUse hook must BLOCK it. If it doesn't, stop and fix
   settings.json before anything else. An unenforced gate is a
   decoration.
3. Ask it to make a trivial whitespace edit to noise_area.py — the
   PostToolUse hook must run test_signals.py automatically.

---

## PART B — The execution loop (every session)

Open every session with `/session-start`. Close every session with
`/session-end`. In between, the sequence to Phase 2 is:

### B1. Quote the data cost  (this week's actual blocker)
    python3 quote_databento_cost.py
If total <= ~$15: proceed. Remainder of the ~$100 credit stays
reserved for a tick-grade pull on the finalist before live capital.

### B2. Build the Databento loader
Prompt Claude Code with exactly this scope:
  "Write load_databento_dbn() in a new file databento_loader.py
   matching the data contract in CLAUDE.md (tz-aware NY OHLCV
   DataFrame). Handle continuous-contract roll days per the
   convention: prev_close from same contract's prior session or
   exclude the day from band inputs. Then run test_signals.py against
   a small pulled sample before the full pull."
The hook will run the tests automatically on every edit.

### B3. Pull the H3 dataset
Six symbols, ohlcv-1m, ~2 years, per the registered H3 spec. Store
under data/ (gitignore raw data).

### B4. Extend backtest.py per registered hypotheses only
In order: baseline on NQ 500+ days -> H3 family run -> H1 -> H2, each
walk-forward with embargo, final OOS evaluated once. Also implement
the two validation upgrades already agreed: trade-order-shuffle /
block-bootstrap Monte Carlo, and rule-significance vs random entries
with matched exit logic. Anything new mid-stream goes through
/register-hypothesis first — no exceptions, that's the whole game.

### B5. Evaluate
    /phase2-gate
On FAIL: it stops and routes modifications to /register-hypothesis.
On claimed PASS: the gate-auditor subagent re-derives everything in a
fresh context. Only after AUDIT: CONFIRMED PASS do YOU run:
    mkdir -p .gates && touch .gates/phase2_passed
Claude never creates that file. That touch command is the single
human decision the whole harness funnels into.

### B6. After the gate (previews, do not start early)
- Phase 4: paper executor consuming signals.jsonl schema; 15+ days AND
  30+ trades; expectancy within 1 SE of backtest; zero critical
  errors. Now the broker-code hook no longer blocks — build the
  executor with broker-side brackets, independent EOD flatten,
  reconciliation loop, kill switch.
- Phase 5: one discounted eval (~$35) first. Verify Tradovate/ProjectX
  automation policy in writing. Withdraw at first payout eligibility.
- Forex/FTMO-US track opens only here: FTMO-variant barrier MC (static
  daily/total loss, not trailing), CFD cost model, written FTMO US
  automation-policy verification, MQL5 port of the signal module.

---

## PART C — What NOT to do (capability != leverage)

- Do NOT build a multi-agent research swarm to "explore strategies in
  parallel." Parallel hypothesis generation without pre-registration
  is industrial-scale sweep-and-select — it maximizes the speed at
  which you fool yourself. One session, one registered hypothesis.
- Do NOT add MCP servers for brokers/market data to Claude Code before
  Phase 2. Capability creates temptation; the hook can't block an MCP
  tool it doesn't know about.
- Do NOT let any session end without /session-end. The ledger is the
  project; unrecorded work is re-polishing waiting to happen.
- Do NOT interpret a green /phase2-gate on partial data as progress
  worth announcing. A gate evaluated on the wrong window is noise.
- The auditor exists because the builder is a bad judge of its own
  work — that applies to Claude and to you. Respect the split.

## First prompt to paste into Claude Code after /session-start

    Blocker is the Databento pull. Step B1: run
    quote_databento_cost.py and report the total. If <= $15, proceed
    to B2 (loader per CLAUDE.md data contract), then stop for my
    review before pulling the full dataset.
