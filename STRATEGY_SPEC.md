# STRATEGY SPEC — Noise-Area Intraday Momentum (MNQ)

Edge family: intraday time-series momentum with a noise filter
(Zarattini/Barbon/Aziz "Beat the Market" model — Tim's ranked primary edge).
Mechanism: order flow after the open exhibits positive autocorrelation once
price escapes the day's typical "noise" range; moves beyond the noise band
tend to extend toward the close.

Instrument: MNQ (Micro Nasdaq-100, $2/pt, tick 0.25 = $0.50)
Timeframe: 5-minute bars, RTH structure (NY time)
Session:   Signals 09:45–15:30 ET, hard flatten 15:55 ET

## ENTRY (all must be true)
1. Noise bands: for each 5-min slot t, mu_t = mean over prior 14 sessions of
   |close_t / day_open − 1|. Upper_t = max(open, prev_close)·(1+mu_t);
   Lower_t = min(open, prev_close)·(1−mu_t).
2. LONG when bar CLOSES above Upper_t; SHORT when bar closes below Lower_t.
3. Fill next bar open + 1 tick adverse slippage. One position at a time;
   reversal allowed on opposite-band close.

## EXIT
- Stop/trail: session VWAP — long exits on bar close < VWAP, short on close
  > VWAP (fill next open, adverse tick).
- Time exit: 15:55 ET flatten, no exceptions. No overnight. Ever.

## RISK
- Backtest sizing: 1 contract (edge measurement only).
- Deployment sizing: buffer-aware — contracts = clamp(0.20 · (equity −
  trailing threshold) / avg_loss_bt, 1, 6), computed with avg_loss assumed
  5 WR-points worse than backtest.
- Costs modeled: $2.50/contract round trip (commission + 1 tick/side).
- Max daily loss: 2 losing reversals → done for the day (max 3 entries/day).
- Martingale/grid: never.

## VALIDATION GATES (pre-registered)
- Phase 2 pass: ≥100 trades, PF > 1.3, profitable in both halves of sample,
  parameter plateau (lookback 10–20 days all positive).
- Phase 4 pass: ≥15 trading days AND ≥30 trades paper, expectancy within
  1 SE of backtest net of costs, zero critical errors.
- DECAY RULE (live): strategy OFFLINE if rolling 30-trade WR < breakeven
  WR + 3pts, or realized DD > 1.5× backtest max DD. Re-validation required
  to redeploy. No mid-flight parameter changes.

## KNOWN LIMITATIONS / FAILURE MODE
- Yahoo 5m history caps at ~60 days → Phase 2 here runs Tier A (5m, faithful,
  small n) + Tier B (hourly, 2 yrs, coarse momentum variant, large n).
  Tick-grade Databento re-run required before live capital.
- Named failure mode: WR estimation lag — ±7.7pt SE at 30 trades means decay
  is detected late; mitigated by sizing as if WR is 5pts below backtest.
