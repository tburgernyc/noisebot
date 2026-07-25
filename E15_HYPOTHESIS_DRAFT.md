# E15 — DRAFT REGISTRATION (not yet in HYPOTHESES.md — Tim's sign-off required before any run)

Per `.claude/skills/register-hypothesis`: written and echoed back per that
skill's required fields. Running this against real data is a separate,
explicit instruction — nothing here has been evaluated on real data.
`e15_alphascope.py` and `test_e15.py` have been machinery-verified on
SYNTHETIC data only (`python3 test_e15.py`, 5/5 pass) — that is a code
sanity check, not an evaluation, exactly like E7/E8-R's pre-run synthetic
verification.

## E15 — Alpha-Scope Channel Breakout (BTC-USD, candidate)

### Provenance / structural audit

Source: a public indicator, "Mean Reversion & Momentum Hybrid |
Alpha-Scope" (Tim supplied the script). Despite the name, tracing the
actual `myBuyCondition`/`mySellCondition` logic (not the plot/coloring
code) surfaces three findings that change what this indicator actually
is:

1. **`myScore` and `mySig` are the same calculation.** Both are
   `for_every(myLongFil, myShortFil, (_long, _short, _prev) => { if
   (_long && !_short) return 1; if (_short) return -1; return _prev || 0;
   })` — verbatim, twice. The buy/sell condition requires both
   `_sig === 1 && _score === 1`, which is one trend filter counted as two
   confirmations. Collapsed here into a single `trend_state` series.
2. **The "momentum" is dead code.** The 75th/25th-percentile
   momentum block (`momentum_length`, `mult_75`, `mult_25`) is computed
   but never referenced by `myBuyCondition`/`mySellCondition` — only by
   unused intermediate variables. It contributes NOTHING to the
   tradeable signal as written. Not ported. (See "E15-alt" below if you
   want it wired in for real.)
3. **Mixed price sourcing.** The close-based Bollinger calc (width
   filter) and the OHLC4-based Bollinger calc (%B position filter) are
   two separate band calculations, and only the RMA/ATR leg respects the
   user's "Source" input. Preserved as-is for a faithful port (see
   `e15_alphascope.py` docstring), not because it's obviously intentional.

**What's actually left, once the marketing name is stripped**: a Keltner-
channel-style breakout filter (price vs. a Wilder-smoothed midline ±ATR)
gated by (a) a loose, symmetric ±5-around-50 BB%-position deadband that
mostly just confirms which side of the recent average price is on, and
(b) a minimum-bandwidth/no-squeeze filter. This is a **channel/volatility
breakout system**, not a mean-reversion system, despite the name.

**Registered prior AGAINST** (stated up front, per house style): this
mechanism family — price breaking a smoothed channel by a volatility
multiple — is a close cousin of the noise-area baseline and E1 (ORB
breakout), both already falsified on MNQ, and shares the general
"breakout/momentum" cluster with E8-R (also falsified). It is not
obviously a fresh mechanism. The correlation gate below (vs. E4-v2/E6)
is how we check whether it's even distinct from what's already live.

### Economic rationale

Channel breakouts are a classic CTA/trend-following primitive: a
volatility-scaled breakout of a smoothed reference level is used as a
proxy for a genuine regime shift (vs. noise), on the theory that stops
and momentum-chasing flow extend the move once triggered. This is the
same general family as Donchian/Keltner breakout systems. Distinct from
E4-v2/E6's mechanism (trailing-return sign + vol targeting) only in HOW
the trend state is detected, not the underlying "trend persists" bet —
which is exactly why a correlation gate against them is required for
this to count as a separate hypothesis rather than a relabeled version
of the same book.

### Exact specification (fixed before any run)

- Universe: BTC-USD. (ETH-USD deliberately NOT registered alongside —
  see Data window/multiplicity note below.)
- Signal (all thresholds are the indicator's shipped defaults):
  - `bb_state`: OHLC4-based %B position vs. a 20-period, 2.0-stdev band.
    +1 when %B > 55, -1 when %B < 45, else carries forward.
  - `trend_state`: price vs. Wilder RMA(15) ± Wilder ATR(20). +1 when
    price > RMA+ATR, -1 when price < RMA-ATR, else carries forward.
  - `width_ok`: close-based Bollinger bandwidth (20, 2.0) > 0.5% of
    price (squeeze filter).
  - LONG when `bb_state==1 AND trend_state==1 AND width_ok`. SHORT
    (or flat, spot venue) mirror. Position tracks the condition directly
    (E4-style: no separate stop/target leg) — flat whenever neither
    holds.
- Fill: signal decided at bar close, exposure applied to the next bar's
  return (no lookahead); cost charged on turnover.
- Sizing: fixed 1x when in a position, no vol targeting — edge
  measurement only, matching E4's (pre-v2) convention. A vol-targeted
  variant would be a separate registration (E15-v2), same precedent as
  E4->E4-v2.
- Venue/costs — TWO registered cells, matching existing cost-fixture
  precedent by granularity:
  - Daily: 0.35% fee/side + 10bps slip (E4/E4-v2 convention).
  - 1H / 4H: 0.05% taker + 0.01% half-spread per side, 6bps/side
    all-in (E8-R convention).
- **Registered plateau: TIMEFRAME — 1H / 4H / 1D, all other parameters
  held fixed at the values above.** This is the direct, pre-registered
  answer to "what timeframe suits it" — the plateau reveals that, rather
  than a guess.
- Long/flat by default (`allow_short=False` in `e15_alphascope.py`,
  matching the E4-v2/E6 spot convention). A long/short perp variant
  (`allow_short=True`) is a distinct registration if you want it tested
  — noted, not registered here.

### Prediction (what confirms / falsifies)

If the mechanism is real and distinct: PF > 1.3 on at least one
timeframe cell, all three plateau cells net-positive (a mechanism that
only works at exactly one of three adjacent timeframes and fails the
other two is a fragile fit, not an edge), both sample halves profitable,
and daily-return correlation vs. the E4-v2 and E6 backtest books ≤ 0.5.
If it's just the same trend bet relabeled (corr > 0.5) or fails the
breakout family's known failure mode (cost-dominated at faster
timeframes, per E8-R/E3 precedent) — falsified.

### Gates (standard set + correlation)

n ≥ 100 trades/episodes; PF > 1.3; both sample halves net-positive;
plateau (all 3 timeframe cells) net-positive; bootstrap (10k paths)
P(maxDD > 40%) < 10%; Sharpe ≥ BTC buy-hold Sharpe on the identical
window; **correlation gate**: daily-return correlation vs. E4-v2 and
vs. E6 backtest books ≤ 0.5 (else verdict = "redundant expression,"
per E8-R precedent, not a fresh sleeve regardless of PF).

### Data window / multiplicity

- BTC daily: **already 4x mined** (E4, E4-v2, E4-v3, E6 all evaluated on
  it) — treat a daily-cell pass with elevated skepticism, exactly as the
  window ledger already flags for this data.
- BTC 1H / 4H (Binance klines): fresh granularity, evaluation #1 at this
  resolution.
- ETH-USD intentionally NOT included in this registration. Per
  multiplicity discipline, see what the BTC timeframe-plateau result
  says first; an ETH-USD cell at the winning timeframe would be a
  natural E15-ETH follow-on, not a simultaneous sweep.

### Kill criterion

Any gate fails on all three timeframe cells -> E15 falsified on this
window, recorded, no retune, no threshold search. A pass on exactly one
timeframe cell that fails the plateau requirement is NOT a partial pass
-- report it, but the plateau gate governs.

### E15-alt (noted, not registered)

If you actually want the percentile-momentum block to gate signals
(recovering the indicator's namesake "momentum hybrid" behavior instead
of the dead-code version above), that is a one-line change
(`buy = buy & long_momentum`, mirror for sell) and a DIFFERENT
hypothesis — register it separately if you want both tested, per the
E4/E4-v2/E4-v3 precedent for variants.

### Files (delivered, not yet run on real data)

- `e15_alphascope.py` — pure signal logic + backtest runner (no I/O,
  matches repo convention).
- `test_e15.py` — machinery tests on synthetic data: state-domain sanity,
  no-lookahead perturbation test (mirrors `test_signals.py`), long-flat
  and long-short backtest smoke tests, flat-zone sanity. **5/5 PASS on
  synthetic data.** Real evaluation still requires: (1) this entry
  copied into `HYPOTHESES.md` as-is or edited, (2) your sign-off, (3) a
  Binance klines loader for 1H/4H/1D BTC-USD wired in (reuse the E8-R
  Binance Vision loader pattern), (4) the actual registered run.
