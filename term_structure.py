"""term_structure.py — PURE logic for the commodity/FX term-structure
family (E9 basis-momentum, E11 hedger-positioning, E12 FX carry).

NO I/O and NO trading-venue imports (constitution: pure signal logic
only). Everything here operates on DataFrames/Series handed in by the
loader. Every function is unit-tested on SYNTHETIC data in
test_term_structure.py BEFORE any registered window is evaluated
(E7/E8 precedent).

Core invariants this module must guarantee:
  * outright/spread discrimination (calendar spreads never enter signals)
  * single-digit-year contract decode by NEXT-OCCURRENCE on/after obs date
  * front / second-nearby selection EXCLUDES the delivery month
  * return series are NO-SPLICE: a roll-day return uses the newly-held
    contract's OWN prior close, never a cross-contract price jump
  * no lookahead: the signal at date t is a function of data <= t only
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

# CME month codes -> calendar month number
MONTH_CODES = {
    "F": 1, "G": 2, "H": 3, "J": 4, "K": 5, "M": 6,
    "N": 7, "Q": 8, "U": 9, "V": 10, "X": 11, "Z": 12,
}
_MONTH_CHARS = "".join(MONTH_CODES)


def ym_key(year: int, month: int) -> int:
    """Monotone (year, month) -> integer for sequencing. month in 1..12."""
    return year * 12 + (month - 1)


def is_outright(symbol: str, root: str) -> bool:
    """True iff symbol is a plain outright of `root` (ROOT+MONTH+YEARDIGIT),
    e.g. CLN0, 6EF5. Calendar spreads / butterflies (contain '-' or ':')
    and anything else are rejected."""
    if "-" in symbol or ":" in symbol:
        return False
    return re.fullmatch(rf"{re.escape(root)}[{_MONTH_CHARS}]\d", symbol) is not None


def decode_expiry_ym(symbol: str, root: str, obs_year: int, obs_month: int) -> int:
    """Decode a single-digit-year outright to an expiry ym_key using the
    NEXT-OCCURRENCE rule: the earliest (year, month) whose year's last digit
    matches the symbol AND that is on/after the observation month. This is
    unambiguous for the near contracts the signals actually use; far-dated
    decade ambiguity never reaches front/second-nearby.
    """
    tail = symbol[len(root):]              # e.g. "N0"
    month = MONTH_CODES[tail[0]]
    digit = int(tail[1])
    obs = ym_key(obs_year, obs_month)
    # search a generous forward horizon of matching-digit years
    for yr in range(obs_year - 1, obs_year + 12):
        if yr % 10 == digit:
            k = ym_key(yr, month)
            if k >= obs:
                return k
    # fallback (should not happen for tradable near contracts)
    return ym_key(obs_year + (digit - obs_year % 10) % 10, month)


def select_front_second(expiry_by_symbol: dict[str, int], obs_ym: int
                        ) -> tuple[str | None, str | None]:
    """Given {symbol: expiry_ym} available on a date and the observation ym,
    return (front, second) where front is the nearest expiry STRICTLY AFTER
    the current month (delivery month excluded) and second is the next one.
    Ties resolved by symbol name for determinism."""
    live = sorted(
        ((k, s) for s, k in expiry_by_symbol.items() if k > obs_ym),
        key=lambda t: (t[0], t[1]),
    )
    front = live[0][1] if len(live) >= 1 else None
    second = live[1][1] if len(live) >= 2 else None
    return front, second


def nearby_return_series(panel: pd.DataFrame, which: str = "front"
                         ) -> pd.Series:
    """Build a NO-SPLICE daily return series for the front or second-nearby
    of ONE root.

    `panel` is a tidy long frame for a single root with columns:
        date (datetime64, sorted), symbol, close (float), expiry_ym (int)
    On each date we pick front/second per select_front_second, then the
    day's return is that held contract's OWN close-to-close using its own
    prior-session close. If the held contract has no prior-session close
    (brand new, i.e. a roll into a contract that did not trade yesterday),
    the return is NaN and is dropped — NEVER spliced across contracts.

    Returns a Series indexed by date (roll/first days that cannot be priced
    within-contract are dropped).
    """
    idx = 1 if which == "second" else 0
    df = panel[["date", "symbol", "close", "expiry_ym"]].copy()
    df["obs_ym"] = df["date"].dt.year * 12 + df["date"].dt.month - 1
    # candidate holds = expiry strictly after the delivery month, ranked near->far
    cand = df[df["expiry_ym"] > df["obs_ym"]].sort_values(
        ["date", "expiry_ym", "symbol"])
    cand["rk"] = cand.groupby("date").cumcount()
    held = cand.loc[cand["rk"] == idx, ["date", "symbol"]].set_index(
        "date")["symbol"]

    closes = panel.pivot_table(index="date", columns="symbol", values="close")
    prev = closes.shift(1)                       # same-contract prior session
    held = held.reindex(closes.index).dropna()
    col_pos = {c: i for i, c in enumerate(closes.columns)}
    ridx = closes.index.get_indexer(held.index)
    cidx = held.map(col_pos).to_numpy()
    now = closes.to_numpy()[ridx, cidx]
    pv = prev.to_numpy()[ridx, cidx]
    # NO-SPLICE (same contract for now & prev) AND non-positive-price guard:
    # a ratio return is undefined when either price <= 0 (e.g. the Apr-2020
    # negative-WTI print) — those days are excluded, never fabricated.
    good = np.isfinite(now) & np.isfinite(pv) & (now > 0) & (pv > 0)
    ret = np.where(good, now / pv - 1.0, np.nan)
    return pd.Series(ret, index=held.index).dropna()


def monthly_returns(daily_ret: pd.Series) -> pd.Series:
    """Compound a no-splice daily return series to month-end."""
    if daily_ret.empty:
        return daily_ret
    return (1.0 + daily_ret).resample("ME").prod() - 1.0


def momentum(monthly_ret: pd.Series, lookback_m: int) -> pd.Series:
    """Trailing lookback_m-month cumulative return, evaluated at each
    month-end (no skip). Uses only data <= the evaluation month (no
    lookahead: the rolling window is strictly backward-looking)."""
    logr = np.log1p(monthly_ret)
    cum = logr.rolling(lookback_m).sum()
    return np.expm1(cum)


def basis_momentum(front_monthly: pd.Series, second_monthly: pd.Series,
                   lookback_m: int) -> pd.Series:
    """E9 signal: mom(front) - mom(second), aligned on month-end."""
    a = momentum(front_monthly, lookback_m)
    b = momentum(second_monthly, lookback_m)
    return (a - b).dropna()


def fx_carry(front_price: pd.Series, second_price: pd.Series,
             dt_years: pd.Series) -> pd.Series:
    """E12 signal: annualized log-basis between front and second-deferred
    quarterly, sign-normalized so a forward DISCOUNT (front > deferred for
    a USD-quoted future => higher local rate) is POSITIVE carry => long.
    front/second_price and dt_years aligned on month-end."""
    with np.errstate(divide="ignore", invalid="ignore"):
        c = np.log(front_price / second_price) / dt_years
    return c.replace([np.inf, -np.inf], np.nan).dropna()


def cross_sectional_ls(signal_wide: pd.DataFrame, n_long: int, n_short: int,
                       tercile: bool = True) -> pd.DataFrame:
    """Map a wide (date x root) signal frame to long/short weights.

    If tercile=True, long the top third / short the bottom third of the
    roots that have a signal that date (equal-weight within leg). Otherwise
    long the top `n_long` / short the bottom `n_short` (used for the 8-name
    FX book: long 3 / short 3). Middle stays flat. Legs are equal-weighted
    to gross 1.0 per side BEFORE portfolio vol targeting.
    """
    w = pd.DataFrame(0.0, index=signal_wide.index, columns=signal_wide.columns)
    for d, row in signal_wide.iterrows():
        s = row.dropna()
        k = len(s)
        if k < 2:
            continue
        if tercile:
            nl = max(1, k // 3)
            ns = max(1, k // 3)
        else:
            nl, ns = n_long, n_short
        nl = min(nl, k // 2)
        ns = min(ns, k // 2)
        if nl < 1 or ns < 1:
            continue
        ranked = s.sort_values(ascending=False)
        longs = ranked.index[:nl]
        shorts = ranked.index[-ns:]
        w.loc[d, longs] = 1.0 / nl
        w.loc[d, shorts] = -1.0 / ns
    return w


def vol_target_scale(book_ret: pd.Series, target_ann: float = 0.15,
                     lam: float = 0.94, min_obs: int = 60,
                     ann: float = 252.0, gross_cap: float = 2.0) -> pd.Series:
    """Per-date leverage multiplier so the book targets `target_ann` vol,
    from an EWMA vol estimate SHIFTED one day (uses info <= t-1 only — no
    lookahead), clipped so 2.0-gross legs stay within gross_cap."""
    ew_var = book_ret.ewm(alpha=1 - lam, min_periods=min_obs).var()
    ew_vol = np.sqrt(ew_var * ann)
    mult = (target_ann / ew_vol).shift(1)          # shift => no lookahead
    mult = mult.clip(upper=gross_cap / 2.0).fillna(0.0)
    return mult


def apply_costs(weights: pd.DataFrame, bps_per_side: float) -> pd.Series:
    """Transaction cost per date = bps/side * traded notional |Δw| summed
    across roots. Returns a per-date cost (fraction of book)."""
    dw = weights.diff().abs().fillna(weights.abs())
    return (bps_per_side / 1e4) * dw.sum(axis=1)


def extract_episodes(weights: pd.DataFrame) -> list[dict]:
    """Per-root episode = a maximal run where sign(w) is constant and
    non-zero. Returns list of {root, start, end, side}. Used for PF/n."""
    episodes = []
    for root in weights.columns:
        w = weights[root]
        side = np.sign(w).replace(0, np.nan)
        run_start = None
        run_side = None
        prev_d = None
        for d, sd in side.items():
            if pd.isna(sd):
                if run_start is not None:
                    episodes.append(dict(root=root, start=run_start,
                                         end=prev_d, side=run_side))
                    run_start = None
            elif run_start is None:
                run_start, run_side = d, sd
            elif sd != run_side:
                episodes.append(dict(root=root, start=run_start, end=prev_d,
                                     side=run_side))
                run_start, run_side = d, sd
            prev_d = d
        if run_start is not None:
            episodes.append(dict(root=root, start=run_start, end=prev_d,
                                 side=run_side))
    return episodes


# ---- metrics ----------------------------------------------------------

def profit_factor(pnl: pd.Series) -> float:
    g = pnl[pnl > 0].sum()
    b = -pnl[pnl < 0].sum()
    return float(g / b) if b > 0 else np.inf


def sharpe(ret: pd.Series, ann: float = 252.0) -> float:
    sd = ret.std()
    return float(ret.mean() / sd * np.sqrt(ann)) if sd > 0 else 0.0


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    return float((equity / peak - 1.0).min())


def bootstrap_p_maxdd(ret: pd.Series, threshold: float = 0.40,
                      n_paths: int = 10000, seed: int = 0) -> float:
    """P(maxDD > threshold) via i.i.d. daily-return resample, full length."""
    r = ret.dropna().to_numpy()
    if len(r) == 0:
        return 1.0
    rng = np.random.default_rng(seed)
    hits = 0
    n = len(r)
    for _ in range(n_paths):
        samp = rng.choice(r, size=n, replace=True)
        eq = np.cumprod(1.0 + samp)
        dd = (eq / np.maximum.accumulate(eq) - 1.0).min()
        if -dd > threshold:
            hits += 1
    return hits / n_paths
