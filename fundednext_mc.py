"""FundedNext Stellar 2-step MC using E4-v2's ACTUAL daily return stream.
Rules: Phase1 +8% target, Phase2 +5%, daily loss 5%, max loss 10% STATIC,
no time limit, min 5 trading days. Block bootstrap (20-day) of E4-v2
daily net returns at several vol targets. Reports P(pass), P(breach),
median calendar days per phase."""
import numpy as np
from crypto_trend import load_yahoo_daily, run_e4_voltarget

RNG = np.random.default_rng(7)
N, BLOCK, MAXD = 10_000, 20, 365 * 6


def phase(r, target, daily_lim=0.05, max_loss=0.10, n_paths=N):
    nblocks = len(r) - BLOCK
    passes = breaches = 0
    days_to_pass = []
    for _ in range(n_paths):
        eq, t, alive = 1.0, 0, True
        while t < MAXD:
            b = RNG.integers(0, nblocks)
            for x in r[b:b + BLOCK]:
                t += 1
                eq *= (1 + x)
                if x <= -daily_lim or eq <= 1 - max_loss:
                    breaches += 1; alive = False; break
                if eq >= 1 + target and t >= 5:
                    passes += 1; days_to_pass.append(t); alive = False; break
            if not alive:
                break
        # paths still alive at MAXD count as neither (censored)
    return (passes / n_paths, breaches / n_paths,
            int(np.median(days_to_pass)) if days_to_pass else -1)


df = load_yahoo_daily("data/btc_1d.json")
for vt in (0.05, 0.08, 0.10, 0.15):
    _, daily, eq = run_e4_voltarget(df, 28, vol_target=vt)
    r = daily.values
    p1, b1, d1 = phase(r, 0.08)
    p2, b2, d2 = phase(r, 0.05)
    chain = p1 * p2
    print(f"vol target {vt:.0%}: realized ann.vol {daily.std()*np.sqrt(365):.1%} "
          f"CAGR {(eq.iloc[-1]**(365/len(eq))-1):.1%}")
    print(f"  Phase1 (+8%): P(pass) {p1:.1%}  P(breach) {b1:.1%}  "
          f"median {d1}d | Phase2 (+5%): P(pass) {p2:.1%}  median {d2}d")
    print(f"  P(pass BOTH phases) {chain:.1%}   "
          f"(trading-day medians; calendar ≈ same, crypto trades daily)")
