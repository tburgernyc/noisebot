<!--
NON-CANONICAL — archived import, 2026-07-18.
This is the STATE.md of a PARALLEL cloud session that was working from
a STALE snapshot of this project (pre-dating the Databento purchase,
the falsified baseline, and the entire E1–E8 series). Its "blocker"
and "staged next action" are obsolete: the Databento data it stages a
pull for is already owned (data/databento_1m.parquet) and that window
is burned (4 evaluations). Kept verbatim below for the record because
its H3 AMD/IFVG falsification is a real registered-and-failed test —
imported into the canonical HYPOTHESES.md as H3-EXT.
The canonical ledger is /home/tburger/noisebot/STATE.md. Do not treat
anything below as current project state.
-->

# STATE.md — Project State

Updated: 2026-07-19 (session: AMD/IFVG request)

## Noise-area MNQ system (primary mission)

- Phase: 2 (NOT passed)
- Blocker (unchanged): Databento NQ/MNQ 1-min, 2+ years, not yet
  acquired. Baseline 500+ day test, then H1/H2, cannot start without it.
- Nothing in this session advanced this blocker.

## H3 detour — AMD/IFVG EURUSD (this session)

- Tim supplied an external SMC/ICT brief (AMD cycle + IFVG entry,
  prop-firm risk shell) and confirmed: own trading, MQL5 target,
  EURUSD/majors.
- Gate ruling applied: non-negotiable #1 — no MQL5/execution code until
  H3 passes Phase 2. Tim did not override.
- Done this session (in progress):
  - HYPOTHESES.md created (H1/H2 migrated as registered-untested; H3
    fully pre-registered with rationale, parameters, pass criteria).
  - STATE.md created (this file — was missing despite session protocol).
  - AMD_IFVG_SPEC.md — exact coded rules (Phase 1).
  - Signal module + unit tests, Phase 2 backtest harness, Dukascopy
    EURUSD M5 2023-07-01→2026-06-30.
- Verdict: **H3 FAILED the Phase 2 gate.** PF 0.657 (n=297), both
  halves negative, all 5 plateau variants negative, loses gross of
  costs (−0.59 pips/trade before commissions), WR 3.2 SE below
  breakeven. Full record in HYPOTHESES.md. Per non-negotiable #1 the
  MQL5 EA was NOT built. Failed test stays on the record.
- Artifacts (session workspace, delivered to Tim): AMD_IFVG_SPEC.md,
  amd_ifvg_signals.py, amd_ifvg_backtest.py, test_amd_ifvg.py (10/10),
  run_phase2.py, phase2_report.json, trades_full.csv.

## Noise-area baseline — staged, blocked on data handoff (2026-07-19)

- Tim directed: pull Databento and run the baseline. Cloud session can
  reach hist.databento.com but has no key (key lives in Tim's local env
  only — his rule) and the desktop bridge was not connected.
- Staged and verified (synthetic end-to-end dry run, 5/5 unit tests,
  correct null behavior on random-walk input: PF 0.80 ≈ cost drag):
  - pull_databento.py — Tim runs LOCALLY; quotes cost first ($25 cap),
    pulls GLBX.MDP3 ohlcv-1m NQ.v.0 + MNQ.v.0, 2023-07-01→2026-07-18.
  - databento_loader.py — Databento CSV → data contract → 5m; validates
    ≥500 full RTH days; overnight-gap scan.
  - test_signals_db.py — the five test_signals.py assertions run against
    the actual Databento frame before any results are read.
  - run_baseline.py — tests → tier-A lookback 14 → registered plateau
    10/14/20 → halves → barrier-MC → baseline_report.json + trades CSV.
- Registered choices: NQ.v.0 = analysis series (MNQ economics $2/pt as
  in backtest.py); window 2023-07-01→2026-07-18; lookback 14 operating,
  10/14/20 plateau must all be positive; noise_area.py unchanged.

## Single next action

Tim: run pull_databento.py locally (key stays in your env), then attach
the two CSVs from ./databento_out/ — or open the desktop app and point
the session at the folder. The baseline runs the moment data lands.
H3a/H3b/H3c stay parked unless explicitly green-lit.
