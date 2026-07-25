"""E19 registered module: delta-neutral perp funding-rate harvest,
BTC/ETH/SOL spot+perp hedged. Pure logic + loaders. No execution code.
Per E19_HYPOTHESIS_DRAFT.md.

Distinct from E7 (E7 was a naked directional bet on funding sign, no
spot leg, and failed because the unhedged short lost more on price than
it collected in funding). E19 pairs a short-perp with an equal-notional
long-spot whenever trailing funding is favorable, cancelling price
exposure so only the funding spread remains as P&L. Long-funding-
collection side only -- the negative-funding mirror (long perp + short
spot) is deliberately not modeled (retail spot-shorting isn't a
uniformly available/cheap constraint E7 didn't have to deal with).

Modeling simplification (disclosed up front, see E19_HYPOTHESIS_DRAFT.md
"Known modeling simplification"): the perp leg is marked using the SAME
spot-close series as the spot leg -- no separate perp mark-price history
is sourced. Because both legs are always opened/closed together at equal
size against that shared series, the combined price P&L is identically
zero by construction (spot_ret - perp_ret == 0 every step). That is a
property of the simplification, not independent evidence the hedge has
no real-world price risk -- basis widens specifically in the high-
funding regimes this strategy targets, which this proxy cannot see.
Reported honestly as a limitation on any pass, not hidden. Swapping in
real perp marks later only requires changing what `perp_ret` is built
from below.

Sign convention mirrors e7_carry: funding P&L per print = -w_perp *
rate; w_perp = -1 while hedged (short the perp), so hedged periods
collect +rate when rate > 0 -- the same direction as the entry
condition (enter on trailing funding > entry threshold).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from e7_carry import load_funding_daily  # reused as-is, no changes

SPOT_COST = 0.0010     # 10bps/side, E4/E4-v2 convention
PERP_COST = 0.0006     # 6bps/side, E8-R Binance-perp convention
LOOKBACK_D = 3          # trailing days for funding mean (FIXED, per spec)


def run_e19_single(px: pd.Series, fund: pd.DataFrame, *,
                    entry: float = 0.08, exit_thr: float = 0.03):
    """One asset. px: daily close, UTC-normalized DatetimeIndex. fund:
    daily funding frame (ann_mean, day_sum) from load_funding_daily,
    reindexed onto px's index internally. Hysteresis: enter (short perp
    + long spot, equal notional) when the trailing LOOKBACK_D-day mean
    annualized funding > entry; exit (flat both legs) when < exit_thr.
    Decide at bar t close using only data through t; position (and its
    P&L) takes effect over the t -> t+1 return, matching the e6/e7
    next-bar convention -- no lookahead.

    Returns (trades, daily_net, equity, attribution):
      trades: DataFrame[entry, exit, ret], one row per flat-to-flat
        hedge episode (ret includes that episode's entry+exit costs).
      daily_net: pd.Series of daily portfolio returns, indexed like px.
      equity: pd.Series, starts at 1.0.
      attribution: {"funding": ..., "price": ..., "costs": ...} additive
        sums of each step's simple-return contribution (approximate
        bookkeeping, matching e7_carry's convention -- not derived from
        the compounded equity curve).
    """
    idx = px.index
    T = len(idx)
    c = px.values.astype(float)
    valid = ~np.isnan(c)
    ret = np.zeros(T)
    with np.errstate(invalid="ignore"):
        ret[1:] = np.where(valid[1:] & valid[:-1], c[1:] / c[:-1] - 1.0, 0.0)
    spot_ret = ret
    perp_ret = ret  # simplification: spot proxy for perp mark, see module docstring

    f = fund.reindex(idx)
    fmean = f["ann_mean"].rolling(LOOKBACK_D, min_periods=LOOKBACK_D).mean().values
    fsum = f["day_sum"].fillna(0.0).values
    have_f = ~np.isnan(fmean)

    eq = np.ones(T)
    held = False
    w_spot_held, w_perp_held = 0.0, 0.0
    trades = []
    ep_ret, ep_open, entry_i = 0.0, False, None
    cum_fund = cum_price = cum_cost = 0.0

    for t in range(1, T - 1):
        if have_f[t] and valid[t]:
            if not held and fmean[t] > entry:
                held = True
            elif held and fmean[t] < exit_thr:
                held = False
        w_spot_new = 1.0 if held else 0.0
        w_perp_new = -1.0 if held else 0.0

        cost = (abs(w_spot_new - w_spot_held) * SPOT_COST
                + abs(w_perp_new - w_perp_held) * PERP_COST)
        w_spot_held, w_perp_held = w_spot_new, w_perp_new

        px_pnl = w_spot_held * spot_ret[t + 1] + w_perp_held * perp_ret[t + 1]
        fund_pnl = -(w_perp_held * fsum[t + 1])
        cum_price += px_pnl
        cum_fund += fund_pnl
        cum_cost += cost
        eq[t + 1] = eq[t] * (1.0 + px_pnl + fund_pnl - cost)

        if w_spot_held != 0.0 and not ep_open:
            ep_open, ep_ret, entry_i = True, 0.0, t + 1
        if ep_open:
            ep_ret += px_pnl + fund_pnl - cost
        if ep_open and w_spot_held == 0.0:
            trades.append({"entry": idx[entry_i], "exit": idx[t + 1], "ret": ep_ret})
            ep_open, ep_ret = False, 0.0

    if ep_open:
        trades.append({"entry": idx[entry_i], "exit": idx[-1], "ret": ep_ret})

    daily = pd.Series(eq, index=idx).pct_change().dropna()
    attribution = {"funding": cum_fund, "price": cum_price, "costs": cum_cost}
    cols = ["entry", "exit", "ret"]
    trades_df = pd.DataFrame(trades, columns=cols) if trades else pd.DataFrame(columns=cols)
    return trades_df, daily, pd.Series(eq, index=idx), attribution


def run_e19(px: pd.DataFrame, fund: dict[str, pd.DataFrame], *,
            entry: float = 0.08, exit_thr: float = 0.03):
    """Multi-asset wrapper: BTC/ETH/SOL run independently via
    run_e19_single (E6/E7 "per-asset episodes" convention), combined
    into ONE portfolio equity curve by EQUAL-WEIGHT AVERAGING the
    per-asset daily return series (skipping assets with no data yet,
    e.g. before SOL's funding history starts).

    NOTE on windowing (matches e7_carry/phase2_e7 precedent exactly):
    px is typically each asset's FULL price history (e.g. BTC from
    2014), long before funding data exists (2020-01 on). Bars before an
    asset's funding history starts are not trimmed here -- they come
    back from run_e19_single as well-defined, legitimately flat (0.0
    return) days, since `held` never turns on without funding data.
    The caller (phase2_e19.py) is responsible for slicing daily/equity
    to the funding-relevant window (e.g. .loc["2020-01-01":]) before
    computing Sharpe/bootstrap/gates, exactly as phase2_e7.py does via
    METRIC_START -- leaving years of trivial flat days in would dilute
    Sharpe and, more importantly, understate bootstrap ruin risk.

    This is a deliberate departure from E6/E7's book-level dot-product
    combination: those sleeves size each asset to a shared book-level
    vol target (weights sum to <=1 by construction, with a gross-
    exposure cap as a backstop). E19 has no book-level target -- each
    asset is independently sized to a fixed 1-unit-when-hedged bet
    ("edge measurement only", per the registered spec) -- so summing
    raw per-asset returns would let 3 simultaneously-hedged assets
    imply 3x gross book exposure with no cap and nothing in the spec
    disclosing that. Equal-weight averaging keeps the book at <=1x by
    construction with no artificial cap needed (the E12 gate-audit
    flagged exactly this kind of cap as an artifact source). Trades and
    the n/PF/half-split gates use the per-asset trade list directly and
    are unaffected by this combination choice.

    Returns (combined_trades, portfolio_daily, portfolio_equity,
    per_asset, attribution_total). per_asset[name] = (trades, daily,
    equity, attribution) from run_e19_single. attribution_total sums
    each asset's attribution scaled by 1/n_assets to stay on the same
    scale as the averaged portfolio curve -- note this scaling cancels
    out of the price-vs-funding attribution-gate ratio either way.
    """
    names = list(px.columns)
    per_asset = {}
    all_trades = []
    daily_frames = {}
    attribution_total = {"funding": 0.0, "price": 0.0, "costs": 0.0}
    for nm in names:
        s = px[nm].dropna()
        trades, daily, eq, att = run_e19_single(s, fund[nm], entry=entry, exit_thr=exit_thr)
        per_asset[nm] = (trades, daily, eq, att)
        if len(trades):
            t2 = trades.copy()
            t2.insert(0, "asset", nm)
            all_trades.append(t2)
        daily_frames[nm] = daily
        for k in attribution_total:
            attribution_total[k] += att[k] / len(names)

    combined_cols = ["asset", "entry", "exit", "ret"]
    combined_trades = (pd.concat(all_trades, ignore_index=True)
                        if all_trades else pd.DataFrame(columns=combined_cols))
    daily_df = pd.DataFrame(daily_frames)
    portfolio_daily = daily_df.mean(axis=1, skipna=True).dropna()
    portfolio_eq = (1.0 + portfolio_daily).cumprod()
    return combined_trades, portfolio_daily, portfolio_eq, per_asset, attribution_total
