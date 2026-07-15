# STATE — noise_bot

Updated: 2026-07-14 (session: Phase 2 baseline run, burgerlaptop, Claude Code local)

## What changed this session

- MCP-bridge blocker RESOLVED by running Claude Code locally on the laptop —
  no bridge needed. Deployed files in ~/noise_bot sha256-verified identical
  to the canonical bundle (files/noise_bot_phase2_bundle.tar.gz) before any run.
- deploy_phase2.sh executed end-to-end, twice (identical results; full log:
  ~/noise_bot/logs/phase2_baseline_2026-07-14.log):
  - Loader unit tests 5/5 PASS; signal suite on Databento loader 5/5 PASS.
  - Parquet spec verified: 143,874 5m bars, 2024-06-30 → 2026-07-13,
    524 RTH days (21 short days skipped), coverage OK vs requested window.
  - Yahoo overlap QA: median |diff| 1 tick — aligned. FLAG: 355/3,744 bars
    >4 ticks, worst ~1,270 ticks all clustered on 2026-06-16 (June quarterly
    roll week; Yahoo front-month vs Databento volume-roll — QA note only,
    does not affect the Databento backtest).
- BASELINE RUN ON THE REAL DATABENTO WINDOW (lookback 14, 489 tradeable days):
  trades 512, WR 37.3%, PF 0.98, total $-773/ct, maxDD $-7,466/ct,
  half1 $-867 / half2 $94. Plateau: lb10 $-1,591 (PF 0.96), lb14 $-773
  (PF 0.98), lb20 $-2,077 (PF 0.95). Barrier MC: P(pass) 31.1%,
  P(blow) 68.9%.
- No execution/broker code written. No parameters changed, no re-tuning
  attempted (would be sweep-and-select; verdict stands as registered).

## Blockers (1)

1. HYPOTHESES.md with the REGISTERED H1 (relative-range regime filter) and
   H2 (dual trail) definitions is still missing from this machine (searched
   /home/tburger; bundle contains only HYPOTHESES_RESULTS_SKELETON.md).
   H1/H2 cannot be tested without the registered text — reconstructing
   thresholds/mechanics ad hoc would be sweep-and-select in disguise
   (non-negotiable 2). Restore canonical HYPOTHESES.md into ~/noise_bot
   (git sync from github.com/tburgernyc/noise_bot, or paste) first.

## Verdicts (definition of done: 3 lines)

- BASELINE: FAIL — PF 0.98 (gate >1.3), half1 negative, plateau 10/14/20
             all negative, MC P(blow) 68.9% (gate <10%). n=512, 489 days.
- H1:       PENDING — blocked on missing registered HYPOTHESES.md
- H2:       PENDING — blocked on missing registered HYPOTHESES.md

## Single next action

Tim decides: (a) restore canonical HYPOTHESES.md into ~/noise_bot and run the
registered H1/H2 variants against the same window (only path that could
rescue the edge without violating pre-registration), or (b) archive the
noise-area edge as falsified on MNQ 2024-07→2026-07 and move down the ranked
edge list. Baseline FAIL means no Phase 4, no paper trading, no capital.
