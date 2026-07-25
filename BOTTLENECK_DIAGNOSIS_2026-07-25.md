# Bottleneck diagnosis: why does almost everything fail here?

Scope: every hypothesis this repo has ever registered (18 total: baseline,
H1/H2, E1-E9, E4-v2, E4-v3, E11, E12, E14, E16, E17, H3-EXT), read in full
from `HYPOTHESES.md`, not from memory. Goal: find the actual common
mechanism behind the failures, not just list them again.

## The scorecard

| ID | Mechanism | Verdict | What killed it |
|---|---|---|---|
| baseline | Always-on intraday momentum (MNQ) | FAIL | PF≈1 (no edge) |
| E1 | ORB+compression (MNQ) | FAIL | decayed half2, plateau cell negative |
| E2 | VWAP mean-reversion (MNQ) | FAIL | decisively wrong sign |
| E3 | Last-hour flow (MNQ) | FAIL | decisively wrong sign, sub-friction |
| E4 | BTC trend, full size | FAIL 6/7 | **ruin gate** (PF 2.86 real, P(maxDD>40%)=97.8%) |
| **E4-v2** | **BTC trend, vol-targeted** | **PASS 7/7** | — (ruin fixed by sizing) |
| E4-v3 | E4-v2 + GARCH sizing | FAIL vs E4-v2 | added complexity, no benefit |
| E5 | Month-end rebal (ES) | FAIL | real mechanism, **~$2.85/trade — sub-friction** |
| **E6** | **Multi-asset crypto trend** | **PASS 7/7** | — (barely: Sharpe 0.97 vs bh 0.96) |
| E7 | Perp funding carry (naked) | FAIL | **unhedged price leg** dominated the real funding capture |
| E8-R | ETH 15m trend cascade | FAIL | sub-friction at 15m granularity |
| H3-EXT | SMC/ICT (EURUSD) | FAIL | loses gross of costs — sign failure |
| E9 | Commodity basis-momentum | FAIL 1/6 | PF 1.08, **ruin 84.5%**, below passive benchmark |
| E11 | Commodity CoT positioning | FAIL 2/7 | real+orthogonal mechanism, PF 1.10, **ruin 76.6%** |
| **E12** | **FX carry (term structure)** | **PASS 6/6*** | *audit: pass is a cap ARTIFACT — true-target ruin is 55.7% |
| E14 | Threshold rebalancing (MES) | FAIL 4/6 | n=17 — underpowered, ~1 trade/yr |
| E16 | Capitulation (volume climax) | FAIL 5/6 | PF 0.66, n=72, **ruin 95.8%** |
| E17 | Livermore pivot-structure | FAIL kill-crit | PF 7.6 real, n=47, **ruin 74.1%** |

## The pattern

**The ruin/crash-risk gate (bootstrap P(maxDD>40%)) is the single most
common cause of death in this entire corpus — and it's not close.** Count
the hypotheses where it's explicitly named as a failing or decisive gate:
E4 (97.8%), E9 (84.5%), E11 (76.6%), E16 (95.8%), E17 (74.1%), and — this
is the sharpest finding in this review — **E12's own gate-auditor found
its ruin-gate PASS (3.8%) was not real**: it passed only because an
unrelated gross-exposure cap happened to bind on 96.6% of days, holding
realized vol at ~7.4% instead of the registered 15% target. Re-scaled to
what was actually registered, the same book gives P(maxDD>40%)=55.7% — a
catastrophic fail. **Of the three "passing" hypotheses this repo has ever
produced, one (E4-v2) passed because ruin was deliberately engineered
away, and one (E12) only reads as passing because of an accounting
accident that masks the same ruin problem everything else has.** E6 is
the only pass where the ruin gate wasn't the central drama.

This is not "crypto/futures are risky, therefore everything fails" — it's
sharper than that. Overlay the PF each hypothesis produced BEFORE the
ruin gate got a vote, and two distinct populations fall out:

**Population 1 — strong signal, killed by tail risk alone**: E4 (PF 2.86)
and E17 (PF 7.6) both have real, large average edges. Both fail
*specifically and only* because full-notional sizing exposes the whole
account to the signal's fat left tail. E4's fix (E4-v2: vol-target the
exposure, same signal) is proven — it survived independent audit and is
in live shadow trading right now. **E17 has never received this
treatment.** It was registered "edge measurement only... sizing is a
SEPARATE future registration — E4-v2 precedent" and nobody has taken that
next step yet. This is the most obvious unexploited move in the entire
portfolio.

**Population 2 — weak signal, ruin gate is just the last nail**: E9
(PF 1.08), E11 (PF 1.10), E16 (PF 0.66) all *already* ran at reduced,
vol-targeted sizing and *still* failed the ruin gate, because a thin edge
sized down to survive its own volatility has nothing left over — sizing
can convert "big edge, unsurvivable risk" into "big edge, survivable
risk," but it cannot manufacture edge that was never there. **The
sizing fix that worked for E4 will not work for E9/E11/E16-shaped
problems, and it's important not to conflate the two** when deciding
where to spend the next registration.

A second, independent pattern, smaller but real: **institutional-scale
edges that are structurally too small for retail costs** — E5 ($2.85/
trade), E7's funding leg in isolation (real: +0.333 cumulative, just
overwhelmed by being naked), E11 (Fan & Zhang's own single-sort Sharpe
is 0.24; this repo's honest construction only reached 0.12 net), E9
(explicitly benchmarked as worse than passive commodity beta). These
aren't wrong, they're *correctly priced for the institutions who can
access them at the size and cost structure where they clear their own
hurdle* — and wrong for a $2-5k account regardless of how the signal is
sized.

A third pattern: **crowded, public, retail-known setups are dead on the
most liquid instruments** — VWAP fades, ORB breakouts, RSI/volume
capitulation, SMC/ICT structure — all decisively falsified (not just
underpowered) on MNQ, EURUSD, and BTC/ETH. The one time a crowded-pattern
family was tested somewhere LESS picked-over (E11's CoT positioning,
genuinely orthogonal per corr(E9)=-0.008), the mechanism turned out to be
real — it just wasn't big enough. Crowding-avoidance finds real
mechanisms; it doesn't by itself make them large enough to trade.

## The actual bottleneck, stated plainly

This repo is good — genuinely good, better than almost any retail
process — at *finding real, statistically distinguishable structure*. It
has found it *at least six times* (E4, E7's funding leg, E9's basis
factor pre-cost, E11's positioning factor, E12's carry factor, E17). The
bottleneck is not discovery. **The bottleneck is that only one of those
six real structures (E4, via E4-v2) has ever been carried through a
proper risk-engineering step, and every other one either never got that
treatment (E17) or turned out too thin to survive it even when it was
applied (E9, E11, E12 for real, E16 never had a large edge to begin
with).** Put differently: the process has a mature, rigorous
*hypothesis-testing* pipeline and almost no *risk-engineering* pipeline —
E4-v2 is a proof of concept that's never been productized into a
repeatable second step.

Everything below is organized around fixing exactly that.

## Solutions, ranked by confidence

### 1. Apply the proven fix to E17 (highest confidence, lowest effort)

E17's raw numbers (PF 7.618, both halves positive, all three plateau
cells strongly positive, Sharpe 1.410 vs. buy-hold 0.962) are the
strongest this repo has ever produced on any single-sizing gate battery
— stronger than E4's own original PF 2.86. It failed for the *exact*
reason E4 failed, and E4's fix is sitting right there, already proven,
already independently audited, already in live shadow trading. Applying
it to E17 isn't a new idea, it's finishing a step that was explicitly
flagged as pending when E17 was first registered ("sizing is a SEPARATE
future registration — E4-v2 precedent") and never followed up on.

**Done this session**: `run_backtest_voltarget()` added to
`e17_pivot_structure.py` (mirrors `crypto_trend.run_e4_voltarget`
exactly — same vol-targeting formula, same no-lookahead construction),
machinery-verified on a dedicated high-volatility synthetic fixture
(full-size maxDD −61.4% → vol-targeted −18.9%, similar final return).
Full spec in `E17-v2_HYPOTHESIS_DRAFT.md`. **Calibrated expectation,
stated honestly in the draft itself**: this will very likely still fail
the n≥100 gate (n=47 is a signal-frequency property sizing can't fix) —
the realistic best outcome is "confirms the ruin-gate mechanism works,
falsified on trade count," which is still valuable information, not a
disguised failure.

### 2. Register the mechanism E7 should have been (high confidence, needs new code)

E7's own numbers show the funding payment is real (+0.333 cumulative)
— it just wasn't hedged, so an unrelated directional bet ate it. A
genuinely delta-neutral spot+perp construction is standard, currently-
practiced professional practice: research pulled this session found
documented positive returns in every month of 2025 with 0.80% max
*monthly* drawdown for this strategy family, professional
implementations near 19% annualized in 2025 (compressed to high-single-
digits by Q2 2026 — the honest forward expectation is modest, not
2024-era numbers). Full spec, including an explicit executability
constraint (long-funding-collection side only — the mirror needs a
spot-borrow retail can't reliably get) and a disclosed modeling
simplification (spot price as a perp-mark proxy) in
`E19_HYPOTHESIS_DRAFT.md`. This is spec-only — no code yet, deliberately,
so the design gets reviewed before implementation effort is spent.

### 3. Deployment structure: the RIGHT prop firm may matter as much as sizing

Research pulled this session (2026-07-25) confirms the account
structure itself is a real lever, not just the strategy math:
**FundedNext uses EOD trailing drawdown with no consistency rule** — the
most compatible structure for a strategy like E17's raw signal (rare,
large moves; intraday volatility doesn't permanently tighten the floor
under an EOD model the way it would under tick-by-tick trailing).
**HyroTrader is stricter by default** (tick-by-tick trailing, mandatory
5-minute stop-loss, 40% consistency cap during evaluation) but offers a
paid "Swing" upgrade converting to static daily drawdown, and its real
differentiator is genuine Bybit exchange execution rather than a
synthetic price feed — worth knowing about even if not the first choice.
This doesn't contradict anything above: FundedNext is already E4-v2's
own registered deployment target (`E4-v2 → FundedNext DEPLOYMENT PLAN`,
gated on PB4 reconciliation, untouched by this session). The actionable
point for E17-v2 specifically: **the registered 40% bootstrap-ruin bar
is a generic, repo-wide safety threshold, not a specific firm's actual
rule.** A real FundedNext-style account has a concrete dollar trailing
floor computed on EOD balance, which may tolerate a different drawdown
profile than the generic test assumes. Worth a follow-up registration
once E17-v2's own numbers are in: re-express the same equity curve
against FundedNext's actual published rules (not the generic 40% bar)
and see if the gap closes. Not done here — flagged as the next
structural lever if E17-v2's own gate battery doesn't fully clear.
Sources: [HyroTrader Review 2026 (Velotrade)](https://velotrade.com/blog/hyrotrader-review) ·
[HyroTrader vs BrightFunded 2026 (Velotrade)](https://velotrade.com/blog/hyrotrader-vs-brightfunded) ·
[Top Prop Firms in 2026 (Velotrade)](https://velotrade.com/blog/top-prop-firms-2026) ·
[Best Crypto Prop Firm in 2026 (Coinpedia)](https://coinpedia.org/press-release/best-crypto-prop-firm-in-2026-how-the-industry-reached-20b)

### 4. Next research frontier: Bitcoin spot ETF flows (genuinely fresh, not yet drafted)

Everything tested here so far is a price/volume/positioning technical
on assets this repo already knows well. Research this session surfaced
a mechanism family never touched: **spot Bitcoin ETF net flows are
reported, by Citigroup research, to correlate with roughly a 53bp
same-day BTC price move per $100M of net inflow, cumulative ~96bp over
10 trading days** — described as "the single most reliable short-term
driver of BTC price in 2026" now that spot ETFs hold 6-7% of circulating
supply. This is live and current: a 10-day, $2.73B outflow streak ran
into early July 2026, reversing to $510M of inflows across the next
three sessions. This is genuinely orthogonal to everything registered
here (it's an institutional-flow signal, not a price-derived technical
or a positioning-survey signal like E11's CoT data) and has a
real, currently-reported data source (daily ETF flow trackers).
**Not drafted as a hypothesis this session** — no data pipeline exists
for it yet, and building one is real, separate effort; flagged here as
the most promising genuinely-new direction once E17-v2/E19 are through
the pipeline, not competing with them for attention right now.
Sources: [Bitcoin ETF Inflows Hit $510M (Tech Times)](https://www.techtimes.com/articles/319974/20260709/bitcoin-etf-inflows-hit-510m-over-3-days-when-blackrock-leads-bitcoin-follows.htm) ·
[How Bitcoin ETF Flows Impact BTC Price in 2026 (KuCoin)](https://www.kucoin.com/blog/how-bitcoin-etf-inflows-and-outflows-impact-btc-price-in-2026) ·
[BTC US Spot ETF Net Flows (Glassnode)](https://studio.glassnode.com/charts/institutions.UsSpotEtfFlowsNet?a=BTC)

### What "just trade more tickers" does and doesn't fix

The user-suggested lever of "identifying different tickers" is real but
narrower than it sounds once the two-population split above is taken
seriously. **It helps Population 1 problems (E17-shaped: strong edge,
underpowered n)** — E16 already tried exactly this (BTC+ETH combined
specifically to reach n≥100) and still landed at n=72; extending E16 to
more alts might close that specific gap, but E16's PF (0.66) is a
Population-2 problem — no amount of universe expansion fixes a mechanism
that loses money on average, it can only make the "not enough trades"
symptom go away while leaving the "not profitable" disease untouched.
**Universe expansion is worth pursuing specifically for E17-v2 if n=47
turns out to be the sole remaining blocker after sizing is fixed** — a
pre-registered, wider liquid-alt universe (not a post-hoc "let's just
add coins until n clears," which would be the exact sweep-and-select
pattern this repo's whole discipline exists to prevent) is a legitimate
next step, but only after E17-v2's own numbers are in, and only as its
own fresh registration.
