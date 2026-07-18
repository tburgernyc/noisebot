#!/usr/bin/env bash
# Deploy verified Phase 2 artifacts into ~/noise_bot and run session tasks 1-3.
# Idempotent. Stops on first failure. NO execution/broker code anywhere.
set -euo pipefail
cd "$(dirname "$0")"
DEST="$HOME/noisebot"

[ -f "$DEST/data/databento_1m.parquet" ] || {
  echo "FATAL: $DEST/data/databento_1m.parquet missing — pull per session task 1"; exit 1; }

cp noise_area.py test_signals.py backtest.py phase2_run.py test_loader.py "$DEST/"
cd "$DEST"

echo "== [1/4] loader unit tests =="
python3 test_loader.py

echo "== [2/4] parquet spec verification (task 1) =="
python3 - <<'EOF'
import datetime as dt
from noise_area import load_databento_parquet
df = load_databento_parquet('data/databento_1m.parquet')
print(f'5m bars: {len(df):,} | span: {df.index[0]} -> {df.index[-1]}')
a, b = df.index[0].date(), df.index[-1].date()
assert a <= dt.date(2024, 7, 8), f'coverage starts late: {a} (requested 2024-07-01)'
assert b >= dt.date(2026, 7, 10), f'coverage ends early: {b} (requested 2026-07-14)'
print('coverage OK vs requested 2024-07-01 .. 2026-07-14')
EOF

echo "== [3/4] signal suite on the Databento loader (task 2 gate) =="
NOISE_DATA_PARQUET=data/databento_1m.parquet python3 test_signals.py

echo "== [4/4] baseline + plateau + barrier MC vs gates (task 3) =="
[ -f data/nq_5m.json ] || curl -sk "https://query1.finance.yahoo.com/v8/finance/chart/NQ%3DF?interval=5m&range=60d&includePrePost=false" \
  -H "User-Agent: Mozilla/5.0" -o data/nq_5m.json
python3 phase2_run.py data/databento_1m.parquet --yahoo data/nq_5m.json
