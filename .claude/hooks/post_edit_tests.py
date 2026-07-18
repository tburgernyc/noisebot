#!/usr/bin/env python3
"""PostToolUse hook: if noise_area.py / backtest.py / test_signals.py was
edited, run the test suite immediately and surface failures to Claude.
Exit 2 feeds stderr back to Claude as something it must fix now."""
import json
import subprocess
import sys

RAW = sys.stdin.read()
try:
    data = json.loads(RAW)
except json.JSONDecodeError:
    sys.exit(0)

path = str((data.get("tool_input") or {}).get("file_path", ""))
WATCH = ("noise_area.py", "backtest.py", "test_signals.py")
if not any(w in path for w in WATCH):
    sys.exit(0)

r = subprocess.run(
    [sys.executable, "test_signals.py"], capture_output=True, text=True,
    timeout=300,
)
if r.returncode != 0:
    print("test_signals.py FAILED after your edit — fix before anything "
          "else:\n" + (r.stdout + r.stderr)[-2000:], file=sys.stderr)
    sys.exit(2)
print("test_signals.py passed.")
sys.exit(0)
