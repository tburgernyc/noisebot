# E16 — DRAFT REGISTRATION (not yet in HYPOTHESES.md — Tim's sign-off required before any run)

Per `.claude/skills/register-hypothesis`: written and echoed back per that
skill's required fields. Nothing here has been evaluated on real data.
`e16_capitulation.py` + `test_e16.py` machinery-verified on SYNTHETIC data
— 8/8 pass (state domain, engineered-crash triggering, no-lookahead
perturbation, backtest sanity, hard-stop enforcement, target-exit
enforcement, and two spacing-guard tests added below). A real RSI
implementation bug (Wilder-seed NaN poisoning the whole series via
`.diff()`'s leading NaN) was caught and fixed by this synthetic
verification BEFORE it could reach real data.

**Data loader now wired up** (`load_yahoo_daily_ohlcv` in
`e16_capitulation.py`) and verified against REAL BTC-USD and ETH-USD
daily history (Yahoo chart API), not just synthetic data — 4330 BTC bars
(2014-09-17 → 2026-07-25) and 3181 ETH bars (2017-11-09 → 2026-07-25),
zero nulls, correct OHLC ordering. **A real data-quality bug was caught in
the process**: fetching with `range=max` silently returns bars spaced
~30 days apart while still claiming `interval=1d` and reporting no error
— confirmed on an actual BTC-USD pull (143 "daily" bars over 12 years).
Re-fetched with explicit `period1`/`period2` Unix-timestamp bounds
instead, which returns genuine 1-day spacing (verified: every gap = 1
day). The loader now asserts this itself (`_assert_daily_spacing`) so a
future accidental `range=max` re-fetch fails loudly instead of silently
feeding monthly bars into RSI(14)/SMA(50)/volume(20) windows sized for
daily data — this exact failure mode is now a permanent regression test,
not just a one-time catch. `data/btc_usd_1d.json` and `data/eth_usd_1d.json`
are included with the delivered files, fetched and ready to use.

## E16 — Capitulation Finder: volume-confirmed mean reversion (BTC + ETH)

### Provenance

Source: public indicator "Capitulation Finder" (Tim supplied the
script). Unlike Alpha-Scope, no structural bugs or dead code found — the
entry logic is internally coherent. It is a **signal/marker only**: it
defines the entry trigger but no exit. The exit rule below (reversion
target, time stop, hard stop) is this registration's own design and is
flagged as such, not presented as if the original author specified it.

### Economic rationale

Forced-liquidation exhaustion: leveraged-long liquidation cascades during
a crypto selloff can push price through a volume-climax blow-off low that
overshoots any reasonable fair value; once forced sellers are exhausted,
price reverts toward its recent mean. Distinct from **E2** (VWAP-stretch
mean reversion, decisively falsified: PF 0.79, n=818) — E2's trigger was
pure price/VWAP distance with **no volume condition at all**. This
requires an actual climax event (volume ≥1.2x its 20-period average), not
just a price stretch, which is a mechanistically different (and, per the
research below, better-evidenced) trigger.

**Registered prior against** (stated up front): oversold readings do not
reliably resolve into a reversal — the research below explicitly cites
Bitcoin staying pinned at extreme-oversold through a large *additional*
decline in the Nov 2018 crash. This is why the hard stop is a first-class
part of the design, not an afterthought bolted onto a signal that "should"
work.

### Exact specification (fixed before any run)

- Universe: **BTC-USD AND ETH-USD**, per-asset independent episodes (E6
  convention) — registered together, not sequentially, because true
  triple-AND capitulation bars are rare by construction and a single
  asset risks starving the n≥100 gate. This is a data-frequency
  necessity, not a "test more things at once" shortcut.
- Timeframe: **daily**. Capitulation/exhaustion is mechanistically a
  slower, higher-timeframe phenomenon (multi-day panic, not an
  intrabar flicker) — daily is the deliberate choice even though it's the
  most-mined window (see below), not a dodge into a fresher timeframe
  that fits the mechanism worse.
- Signal (indicator's shipped defaults, all fixed): RSI(14) ≤ 30 AND
  close < SMA(50)×0.95 AND volume ≥ 1.2× its 20-period average, all on
  the same bar → LONG next bar open.
- Exit — first of:
  1. Target: close reverts to the SMA(50) (the mechanism's own definition
     of "reversion").
  2. Time stop: **registered plateau — 5 / 10 / 15 bars**, the one
     parameter this registration invented rather than inherited, so it
     is the one under plateau discipline.
  3. Hard stop: fixed 8% adverse move (risk backstop, not swept).
- Costs: 0.35% fee/side + 10bps slip (E4/E4-v2 daily convention).
- Long/flat only (`allow_short=False` default in `e16_capitulation.py`,
  matching E4-v2/E6's spot convention) — the mirrored bearish-capitulation
  short is computed but not traded in this registration.

### Prediction (what confirms / falsifies)

If real: PF > 1.3 combined across BTC+ETH, all three time-stop plateau
cells net-positive, both sample halves profitable, **and** — the
interesting part — low daily-return correlation with E4-v2/E6 (a mean-
reversion mechanism entering on the OPPOSITE condition trend-following
requires should, if real, look nothing like the trend book; a
confirmed low correlation would make this a genuinely diversifying
sleeve, not just another way to be long BTC trend). If it's just noise
dressed up as a signal, or if "oversold" keeps not mean-reverting in this
window the way the research above warns it might: falsified.

### Gates (standard set + correlation)

n ≥ 100 closed trades (BTC+ETH combined); PF > 1.3; both sample halves
net-positive; plateau (5/10/15-bar time stop, all three) net-positive;
bootstrap (10k paths) P(maxDD > 40%) < 10%; correlation gate: daily-return
correlation vs. E4-v2 and vs. E6 ≤ 0.5 (here a LOW correlation is the
hoped-for result, unlike E7/E8-R where low correlation couldn't save a
failing PF — flagged so a future reader doesn't misread this gate's
intent).

### Data window / multiplicity

BTC and ETH daily price history has 4-5 prior evaluations (E4, E4-v2,
E4-v3, E6, and the E15 draft if run) — but every one of them tested the
**same mechanism family** (trailing-return trend). A mean-reversion
trigger run on the same raw prices is a different kind of test, not a
free pass — logged honestly as "reused price data, fresh mechanism," not
claimed as a fresh window outright.

### Kill criterion

Any gate fails → E16 falsified on this window, recorded, no retune, no
threshold search, no swap to a different MA type/length after seeing
results.

### Files (delivered, not yet run on real data)

- `e16_capitulation.py` — pure signal logic + backtest runner + data
  loader (`load_yahoo_daily_ohlcv`), verified against real BTC/ETH data.
- `test_e16.py` — 8/8 PASS on synthetic data.
- `data/btc_usd_1d.json`, `data/eth_usd_1d.json` — real daily OHLCV,
  already fetched and loader-verified (shape/dtype/spacing only — NOT
  run through `compute_signals`/`run_backtest`; that would be an actual
  evaluation, which is still gated on your sign-off, not a data-plumbing
  task).
- Real evaluation still requires: (1) this entry copied into
  `HYPOTHESES.md` (or edited) and your sign-off, (2) the actual
  registered run — that's it, the loader is no longer a blocker.
