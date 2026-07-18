#!/usr/bin/env python3
"""PreToolUse hook: mechanical enforcement of the non-negotiables.

Covers Write/Edit/MultiEdit AND Bash, so autonomous (bypass-permissions)
mode cannot route around the gates via shell commands. Exit 2 = block,
with the reason fed back to Claude on stderr.

Gates (marker files created ONLY by a human in a real terminal):
  .gates/phase2_passed       -> unlocks broker/execution code
  .gates/data_pull_approved  -> unlocks Databento data spend
"""
import json
import re
import sys
from pathlib import Path


def block(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(2)


RAW = sys.stdin.read()
try:
    data = json.loads(RAW)
except json.JSONDecodeError:
    sys.exit(0)  # malformed input: fail open, don't crash the session

tool = str(data.get("tool_name", ""))
ti = data.get("tool_input", {}) or {}
path = str(ti.get("file_path", ""))
command = str(ti.get("command", ""))
content = " ".join(str(ti.get(k, "")) for k in ("content", "new_string", "file_text"))
blob = " ".join((path, command, content)).lower()

# --- 0. Gate-file integrity (always on) ---------------------------------
# Only a human at a real terminal touches .gates/. Claude never creates,
# edits, or deletes gate markers by any tool, in any mode.
if ".gates" in blob:
    block("BLOCKED: .gates/ markers are human-only. If a gate truly "
          "passed, report it and ask Tim to create the marker himself "
          "in his own terminal. Never self-approve.")

# --- 1. Secret guard (always on) ----------------------------------------
SECRET_PAT = re.compile(
    r"(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}",
    re.I,
)
if SECRET_PAT.search(content) or SECRET_PAT.search(command):
    block("BLOCKED: looks like a hardcoded secret. Secrets live in env "
          "vars only (repo rule). Use os.environ.")

# --- 2. Databento spend guard -------------------------------------------
# get_cost quotes are free and always allowed (quote_databento_cost.py).
# Anything that can incur spend (get_range / batch download / databento
# CLI) requires the human-created marker .gates/data_pull_approved,
# which Tim creates AFTER reviewing the quoted total.
SPEND_SIGNS = ("get_range", "timeseries.get_range", "batch.submit",
               "databento download", "databento batch")
is_quote = "quote_databento_cost" in blob and "get_range" not in blob
if (tool == "Bash"
        and any(s in blob for s in SPEND_SIGNS) and not is_quote
        and not Path(".gates/data_pull_approved").exists()):
    block("BLOCKED by spend gate: Databento data pulls cost real credit. "
          "Run quote_databento_cost.py, report the total to Tim, and "
          "wait for him to run  mkdir -p .gates && touch "
          ".gates/data_pull_approved  in his own terminal. "
          "(Writing pull code is fine; EXECUTING a pull is gated.)")

# --- 3. Execution-code guard (until Phase 2 passes) ---------------------
if Path(".gates/phase2_passed").exists():
    sys.exit(0)

BROKER_SIGNS = (
    "ib_async", "ib_insync", "ibapi", "tradovate", "projectx",
    "placeorder", "place_order", "submit_order", "createorder",
    "marketorder", "limitorder", "stoporder", "bracket_order",
    "executor.py", "live_trade", "broker",
)
if any(s in blob for s in BROKER_SIGNS):
    block("BLOCKED by Phase-2 gate: no execution/broker code until "
          ".gates/phase2_passed exists (non-negotiable #1) — created "
          "only by Tim after /phase2-gate PASS plus independent "
          "gate-auditor confirmation. This applies to Bash heredocs "
          "and every other write path, in every permission mode.")

sys.exit(0)
