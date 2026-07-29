# E19 — DRAFT REGISTRATION, SPEC ONLY (not yet in HYPOTHESES.md, no code yet — Tim's sign-off required before implementation begins)

Per `.claude/skills/register-hypothesis`. Unlike E17-v2 (a small, low-risk
change to already-tested code, implemented and machinery-verified this
session), E19 is a genuinely new mechanism with no existing module to
extend — the spec below is deliberately written for review BEFORE any
implementation effort, so design disagreements get caught before code is
written, not after. This is the "outside the box" candidate: a real,
currently-practiced 2025-2026 strategy family this repo has never
actually tested, despite E7 sitting adjacent to it and getting the
implementation wrong.

## E19 — Delta-neutral perp funding-rate harvest (BTC/ETH/SOL, spot+perp hedged)

### Why this isn't E7 again

E7 ("Perp funding-rate carry") was registered as a **directional bet on
the sign of funding** — short the perp when funding ran hot (collect
funding), long when funding ran negative — with **no offsetting spot
leg**. It failed decisively: "funding leg +0.333 real but price leg
−1.033 (carry is priced)" — the position was net-short BTC perps,
unhedged, through a mostly-up market, and the directional loss swamped
the real funding income. **That is not what "cash-and-carry" or
"delta-neutral funding harvest" means in practice, and it is not what
professional desks running this strategy actually do.** The standard
construction pairs the perp short with an equal-notional spot long,
cancelling price exposure so ONLY the funding spread remains as P&L.
E19 is that construction, registered as a distinct hypothesis with a
structurally different risk profile — not a retune of E7's thresholds.

### Economic rationale, with current (2026) evidence

Perpetual funding is a structural payment from the crowded side
(persistently leveraged directional traders) to whoever takes the other
side — compensation for warehousing that leverage demand, not a price
forecast (same underlying mechanism E7 correctly identified). The fix is
entirely in position construction: hedge the price leg so the payment is
harvested without directional risk. This is a real, currently-active
professional strategy, not a backtest artifact — research pulled during
this session (2026-07-25, sources below) found: delta-neutral funding
strategies produced positive returns in every month of 2025 with a
documented maximum *monthly* drawdown of 0.80%, and professional
implementations captured ~19% annualized in 2025. **Registered prior for
calibrating expectations, not overselling**: the same research is
explicit that funding has compressed substantially into 2026 ("as of Q2
2026 the rate has compressed into the high single digits... cooled from
late-2024 highs") — the honest forward expectation for this registration
is a modest, single-digit-to-low-double-digit annualized return, not the
2024-era headline numbers, and the plateau/gate design below should be
read with that calibration in mind.

### Exact specification (fixed before any run — this is what needs review before implementation starts)

- Universe: BTC, ETH, SOL USDT-margined perps + equal-notional spot,
  independently per asset (E6/E7 convention: per-asset episodes).
- **Position (long-funding-collection side only)**: when trailing
  funding is favorable, hold SHORT 1 unit perp + LONG 1 unit spot
  (equal notional, delta ≈ 0). **The mirror (long perp + short spot to
  collect negative funding) is deliberately NOT registered**: spot-
  shorting crypto requires a borrow that isn't uniformly available or
  cheap at retail size, unlike E7's naked-short design which could take
  either side costlessly. When funding isn't favorable: flat, both legs
  closed. This asymmetry is a real executability constraint, not an
  oversight — flagged explicitly rather than silently assumed away.
- Entry/exit (hysteresis band, avoiding whipsaw on funding noise near a
  single threshold — same idea as E6's band rebalancing): enter the
  hedge when trailing 3-day mean annualized funding > entry threshold;
  unwind when trailing 3-day mean annualized funding < exit threshold
  (exit threshold set LOWER than entry, e.g. entry 8%/exit 3% as the
  base case — see registered plateau below). Funding accrues every 8h
  while the hedge is held, from the actual historical prints (same data
  E7 already established: Binance monthly funding archives, 8h prints).
- Sizing: fixed 1 unit per asset while hedged (edge measurement only,
  matching E4's pre-v2 convention) — a vol-targeted or capital-
  efficiency-optimized sizing variant (this position's realized vol
  should be very low by construction, meaning it may be capital-
  inefficient at 1x margin — a leveraged/capital-efficient version
  would be a separate future registration, E4→E4-v2 precedent applies
  here too) is explicitly NOT part of this registration.
- **Known modeling simplification, disclosed before any run**: this
  spec prices the spot leg using the same spot-close series already in
  `data/btc_usd_1d.json`/`eth_usd_1d.json`/(new) `sol_usd_1d.json` as a
  proxy for the perp mark price, rather than sourcing actual perp mark
  prices. Spot and perp marks are usually close, but the basis WIDENS
  specifically during the high-funding regimes this strategy targets —
  meaning this simplification could bias the hedge quality in either
  direction exactly when it matters most. If the implementation can
  source actual Binance perp mark-price history instead, that removes
  this caveat; if not, it must be reported as a limitation on any pass,
  not silently assumed away.
- Costs: entry/exit costs on BOTH legs (spot: ~10bps taker per E4/E4-v2
  convention; perp: 6bps/side per E8-R's Binance-perp convention) —
  total ~16bps per side, ~32bps round trip per hedge cycle, plus the
  funding payments themselves (sign-aware, from actual historical
  prints).
- **Registered plateau parameter: entry/exit threshold pair — (6%/2%),
  (8%/3%), (12%/5%) — all three must be net positive.** All other
  parameters (3-day funding lookback, per-asset independence) fixed.

### Gates (standard set + a stronger attribution gate than E7's)

n ≥ 100 hedge episodes (BTC+ETH+SOL combined, per-asset independent —
E6 convention); PF > 1.3; both sample halves net-positive; plateau (all
three threshold-pair cells) net-positive; bootstrap (10k paths)
P(maxDD > 40%) < 10% — **predicted to pass easily if the hedge is
working as designed, since a genuinely delta-neutral book should never
approach a 40% drawdown from price risk alone; a near-miss or fail here
would itself indicate the hedge isn't actually neutral (the spot-vs-perp
proxy simplification above being the likely first suspect)**;
**attribution gate, stricter than E7's**: cumulative price-leg P&L
(spot leg + perp leg combined, i.e. the hedge residual) must be SMALL in
absolute terms relative to cumulative funding-leg P&L (registered bar:
|price-leg| < 20% of |funding-leg|, versus E7's weaker "funding > 0 AND
funding > |price|" bar which a badly-hedged book could still technically
clear) — this is the gate that actually tests whether the hedge is doing
its job, not just whether funding happened to win on net; correlation
gate vs. E4-v2 and E6 ≤ 0.5 — **low correlation is expected and part of
the investment case** (a genuinely delta-neutral book should show close
to zero correlation with a directional trend book, same logic as E16's
correlation prediction, which held: E16 actually measured 0.02-0.07).

### Kill criterion

Any gate fails → E19 falsified on this window, recorded, no retune, no
threshold search, no switch to sourcing perp marks after seeing
unfavorable spot-proxy results (that would be exactly the kind of
post-hoc methodology change this repo's discipline exists to prevent —
if the spot-proxy simplification needs fixing, that's a fresh
registration citing this one's result as the reason, not a silent edit).

### Data / multiplicity

Binance funding-rate history (BTC/ETH 2020-01→2026-06-30, SOL from
2020-09 listing — per E7's original data note; needs re-verifying still
present, since `data/` is gitignored and this session's clone doesn't
carry it) — this window was already burned for the DIRECTIONAL E7
hypothesis (evaluation #1 consumed). A delta-neutral construction is a
different mechanism (hedge quality and funding-sign timing, not price
direction), logged honestly as "reused funding data, structurally
different mechanism," matching the same disclosure convention used for
reusing BTC/ETH price data across E4-family and E16/E17. Spot price data
(BTC/ETH already fetched this session; SOL fetched for the E16/E17
correlation gate, `data/sol_usd_1d.json`, present locally but not
committed, gitignored) covers the same window.

### What's NOT done yet (unlike E17-v2)

This is a specification, not working code. Before this can be evaluated:
(1) Tim's review of the design above, especially the spot-vs-perp proxy
simplification and the single-sided (long-funding-collection-only)
construction; (2) an implementation (`e19_funding_basis.py`, pure logic
+ loader, matching repo convention) with the same no-lookahead/synthetic-
verification discipline every other module here has had; (3) confirming
the funding data is actually available in this environment or re-
fetchable; (4) copying this entry into `HYPOTHESES.md` and sign-off;
(5) the actual registered run.
