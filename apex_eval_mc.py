"""Apex 150k eval + PA Monte Carlo, using the repo's barrier-MC pattern.
Eval: start 150k, target +9k, intraday trail 4k (locks at start+100 on
PA only). 30-day expiry. PA: fresh 150k, trail 4k until locked at
150,100, approximate first-payout threshold +5k.
Scenarios: zero edge net of costs, modest edge, strong validated edge.
Sizing: buffer-aware like eval_barrier_mc (risk 20% of buffer/avg_loss,
1-20 micros). Trades/day=5, 21 trading days max in 30-day window."""
import numpy as np

RNG = np.random.default_rng(7)
N = 20_000
TRADES_MAX = 5 * 21          # 30-day expiry
WIN, LOSS = 150.0, 100.0     # $/micro after costs


def stage(p_win, start, target, trail, lock, max_trades, n_paths=N):
    passes = blows = expires = 0
    for _ in range(n_paths):
        eq = peak = start
        done = False
        for t in range(max_trades):
            thr = peak - trail if lock is None else min(peak - trail, lock)
            buf = eq - thr
            ct = int(max(1, min(20, buf * 0.20 // (LOSS * 1.3))))
            pnl = ct * (WIN if RNG.random() < p_win else -LOSS)
            # intraday trail: assume adverse excursion touches trail first
            # if the trade loses (pessimistic-realistic for trailing rules)
            eq += pnl
            peak = max(peak, eq)
            thr = peak - trail if lock is None else min(peak - trail, lock)
            if eq <= thr:
                blows += 1; done = True; break
            if eq >= target:
                passes += 1; done = True; break
        if not done:
            expires += 1
    return passes / n_paths, blows / n_paths, expires / n_paths


for label, p in (("zero edge (PF 1.00)", 0.400),
                 ("modest edge (PF~1.15)", 0.434),
                 ("validated edge (PF 1.30)", 0.464)):
    pf = p * WIN / ((1 - p) * LOSS)
    ev_pass, ev_blow, ev_exp = stage(p, 150_000, 159_000, 4_000, None,
                                     TRADES_MAX)
    pa_pay, pa_blow, pa_exp = stage(p, 150_000, 155_000, 4_000, 150_100,
                                    1_000)
    p1of5 = 1 - (1 - ev_pass) ** 5          # independent accounts
    print(f"\n== {label} (WR {p:.1%}, PF {pf:.2f}) ==")
    print(f"EVAL:  P(pass) {ev_pass:.1%}  P(blow) {ev_blow:.1%}  "
          f"P(expire) {ev_exp:.1%}")
    print(f"5-pack: P(>=1 pass) {p1of5:.1%} if INDEPENDENT; "
          f"= {ev_pass:.1%} if same trades copied (1 bet x5)")
    print(f"PA:    P(reach +5k payout buffer) {pa_pay:.1%}  "
          f"P(blow first) {pa_blow:.1%}")
    print(f"Chain per account: P(eval pass AND PA payout) "
          f"{ev_pass * pa_pay:.1%}")
