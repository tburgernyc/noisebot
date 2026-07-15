"""Phase 2: event-driven backtest. Pessimistic fills: signals act on bar
close, filled at NEXT bar open +/- 1 tick adverse. Costs $2.50/ct RT.
Reports per-contract MNQ dollars ($2/pt). Feeds empirical trade P&L into
the prop-eval barrier Monte Carlo (buffer-aware sizing)."""
from __future__ import annotations
import numpy as np
import pandas as pd

from noise_area import Day, build_days, load_yahoo_json, rth, signal_for_bar

PT, TICK, COST_RT = 2.0, 0.25, 2.50   # MNQ $/pt, tick size, cost per ct per trade
MAX_ENTRIES_PER_DAY = 3
RNG = np.random.default_rng(7)


def run_tier_a(days: list[Day]) -> pd.DataFrame:
    trades = []
    for day in days:
        pos, entry_px, entries = 0, 0.0, 0
        n = len(day.bars)
        for i in range(n - 1):
            sig = signal_for_bar(day, i, pos)
            if sig == "HOLD":
                continue
            nxt = day.bars["open"].iloc[i + 1]
            if sig == "EXIT" and pos:
                fill = nxt - TICK if pos == 1 else nxt + TICK
                trades.append(_close(day, entry_px, fill, pos))
                pos = 0
            elif sig in ("LONG", "SHORT"):
                want = 1 if sig == "LONG" else -1
                if pos and pos != want:  # reversal: close first
                    fill = nxt - TICK if pos == 1 else nxt + TICK
                    trades.append(_close(day, entry_px, fill, pos))
                    pos = 0
                if pos == 0 and entries < MAX_ENTRIES_PER_DAY:
                    entry_px = nxt + TICK if want == 1 else nxt - TICK
                    pos, entries = want, entries + 1
        if pos:  # force flatten at last bar close (defensive; FLATTEN should catch)
            last = day.bars["close"].iloc[-1]
            fill = last - TICK if pos == 1 else last + TICK
            trades.append(_close(day, entry_px, fill, pos))
    return pd.DataFrame(trades)


def _close(day: Day, entry: float, exit_: float, pos: int) -> dict:
    pnl = (exit_ - entry) * pos * PT - COST_RT
    return {"date": day.date, "dir": pos, "entry": entry, "exit": exit_, "pnl": pnl}


def run_tier_b(df1h: pd.DataFrame, lookback: int = 14) -> pd.DataFrame:
    """2-yr coarse variant of the same edge family: morning move (09:00->11:00
    NY) beyond its 14-day mean absolute move -> enter at 11:00, exit ~16:00."""
    r = df1h.between_time("09:00", "16:59")
    rows = []
    for d, g in r.groupby(r.index.date):
        g = g[~g.index.duplicated()]
        try:
            p9 = g.at_time("09:00")["open"].iloc[0]
            p11 = g.at_time("11:00")["open"].iloc[0]
            pcl = g.at_time("15:00")["close"].iloc[0]
        except IndexError:
            continue
        rows.append({"date": d, "p9": p9, "p11": p11, "pcl": pcl,
                     "mv": abs(p11 / p9 - 1.0)})
    t = pd.DataFrame(rows)
    if t.empty:
        return t
    t["mu"] = t["mv"].rolling(lookback).mean().shift(1)  # prior days only
    t = t.dropna()
    trig = t[t["mv"] > t["mu"]].copy()
    dirn = np.sign(trig["p11"] - trig["p9"])
    entry = trig["p11"] + dirn * TICK
    exit_ = trig["pcl"] - dirn * TICK
    trig["dir"] = dirn
    trig["pnl"] = (exit_ - entry) * dirn * PT - COST_RT
    return trig[["date", "dir", "pnl"]]


def metrics(tr: pd.DataFrame, label: str) -> dict:
    if tr.empty:
        print(f"{label}: NO TRADES"); return {}
    pnl = tr["pnl"]
    wins, losses = pnl[pnl > 0], pnl[pnl <= 0]
    eq = pnl.cumsum()
    dd = (eq - eq.cummax()).min()
    half = len(tr) // 2
    m = {
        "trades": len(tr), "win_rate": len(wins) / len(tr),
        "pf": wins.sum() / max(1e-9, -losses.sum()),
        "avg_trade": pnl.mean(), "avg_win": wins.mean() if len(wins) else 0,
        "avg_loss": -losses.mean() if len(losses) else 0,
        "total": pnl.sum(), "max_dd": dd,
        "half1": pnl.iloc[:half].sum(), "half2": pnl.iloc[half:].sum(),
    }
    print(f"\n== {label} ==")
    print(f"trades {m['trades']}  WR {m['win_rate']:.1%}  PF {m['pf']:.2f}  "
          f"avg ${m['avg_trade']:.2f}/ct  W ${m['avg_win']:.0f} L ${m['avg_loss']:.0f}")
    print(f"total ${m['total']:,.0f}/ct  maxDD ${m['max_dd']:,.0f}/ct  "
          f"half1 ${m['half1']:,.0f}  half2 ${m['half2']:,.0f}")
    return m


def barrier_mc(pnl: np.ndarray, n_paths=10_000, start=50_000.0, target=53_000.0,
               trail=2_500.0, lock=50_100.0, risk_frac=0.20, max_ct=6,
               max_trades=750) -> dict:
    """Eval survival using the EMPIRICAL trade distribution (bootstrap),
    buffer-aware sizing, avg_loss haircut as if WR were 5pts worse."""
    avg_loss = -pnl[pnl <= 0].mean() if (pnl <= 0).any() else 50.0
    passes = blows = 0
    tta = []
    for _ in range(n_paths):
        eq, peak = start, start
        for t in range(1, max_trades + 1):
            thr = min(peak - trail, lock)
            ct = int(max(1, min(max_ct, (eq - thr) * risk_frac // (avg_loss * 1.3))))
            eq += ct * RNG.choice(pnl)
            peak = max(peak, eq)
            if eq <= min(peak - trail, lock):
                blows += 1; break
            if eq >= target:
                passes += 1; tta.append(t); break
    p = passes / n_paths
    print(f"\n== Eval barrier MC (empirical dist, buffer-aware 1-{max_ct}ct) ==")
    print(f"P(pass) {p:.1%}  P(blow) {blows/n_paths:.1%}  "
          f"median trades-to-pass {np.median(tta) if tta else float('nan'):.0f}  "
          f"evals/funded {1/p if p else float('inf'):.2f}  fees@$35 ${35/p if p else float('inf'):.0f}")
    return {"p_pass": p, "p_blow": blows / n_paths, "n_paths": n_paths,
            "median_tta": float(np.median(tta)) if tta else float("nan")}


if __name__ == "__main__":
    df5 = load_yahoo_json("data/nq_5m.json")
    days = build_days(df5, lookback=14)
    print(f"5m data: {len(rth(df5))} RTH bars, {len(days)} tradeable days "
          f"({days[0].date} → {days[-1].date})" if days else "no days")
    ta = run_tier_a(days)
    ma = metrics(ta, "TIER A — Noise-Area 5m (faithful spec, ~60d)")

    df1h = load_yahoo_json("data/nq_1h.json")
    tb = run_tier_b(df1h)
    if not tb.empty:
        print(f"\n1h data: {tb['date'].min()} → {tb['date'].max()}")
    mb = metrics(tb, "TIER B — Morning-momentum family, hourly (~2yr)")

    # plateau check on Tier B lookback
    print("\n== Parameter plateau (Tier B lookback) ==")
    for lb in (10, 14, 20):
        t = run_tier_b(df1h, lookback=lb)
        print(f"lookback {lb:2d}: trades {len(t):4d}  total ${t['pnl'].sum():>9,.0f}  "
              f"PF {t['pnl'][t.pnl>0].sum()/max(1e-9,-t['pnl'][t.pnl<=0].sum()):.2f}")

    if not ta.empty:
        barrier_mc(ta["pnl"].values)
