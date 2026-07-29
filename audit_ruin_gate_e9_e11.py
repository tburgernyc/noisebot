"""audit_ruin_gate_e9_e11.py — gate-auditor-precedent check: does the E12
cap-binding artifact (gross_cap silently suppressing realized vol below the
registered target, distorting the reported P(maxDD>40%)) also affect E9 and
E11's already-reported ruin-gate numbers?

This is NOT a re-evaluation. It imports the exact registered code paths
(term_structure.py, termstructure_backtest.py) with IDENTICAL parameters to
phase2_termstructure.py's run_e9()/run_e11() — same signal, same tercile
split, same 5 bps/side, same target_vol=0.15/gross_cap=2.0 defaults — and
inspects one extra internal quantity (the vol-target multiplier `mult`) that
run_book() already computes but doesn't expose. No parameter is changed, no
new verdict is produced; this only asks whether the ALREADY-REPORTED
P(maxDD>40%) figures (E9: 0.845, E11: 0.766) are trustworthy the same way
E12's gate-auditor asked for E12 (E12's CAVEAT A, HYPOTHESES.md ~L947-956).

Precedent for why this is audit, not evaluation: the E12 gate-auditor ran
the same registered code and inspected an internal quantity it produced —
it did not alter the registered signal, universe, costs, or targets.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import cot_loader
import ladder_loader as L
import term_structure as ts
import termstructure_backtest as bt

DATA = "/home/tburger/noisebot/data"
COMMO = ["CL", "NG", "HO", "RB", "GC", "SI", "HG",
         "ZC", "ZW", "ZS", "ZL", "ZM", "LE", "HE"]

TARGET_VOL = 0.15
GROSS_CAP = 2.0
MULT_CEIL = GROSS_CAP / 2.0  # 1.0 at the registered default — matches run_book


def cap_diagnostics(w_daily: pd.DataFrame, daily_ret: pd.DataFrame, net: pd.Series,
                     label: str) -> dict:
    """Reconstruct the vol-target multiplier run_book() computed internally
    (identical inputs: unscaled gross book return, same target/cap), then
    report what E12's audit reported: % of days the cap bound, realized vol
    of the AS-REGISTERED (capped) book vs the 15% target, and — only if the
    E12 pattern actually reproduces (cap binds hard AND vol is suppressed) —
    the re-scaled P(maxDD>40%) had the cap not bound.
    """
    dr = daily_ret.reindex(w_daily.index).fillna(0.0)
    gross_unscaled = (w_daily * dr).sum(axis=1)
    mult = ts.vol_target_scale(gross_unscaled, TARGET_VOL, gross_cap=GROSS_CAP)

    live = mult[mult.index >= mult.first_valid_index()] if mult.notna().any() else mult
    live = live.dropna()
    pct_at_ceiling = float((live >= MULT_CEIL - 1e-9).mean()) if len(live) else float("nan")

    ann_vol = float(net.dropna().std() * np.sqrt(252.0))

    print(f"\n{'=' * 60}\n{label} — ruin-gate cap-binding audit\n{'=' * 60}")
    print(f"  days with valid multiplier         : {len(live)}")
    print(f"  % of days multiplier AT ceiling     : {pct_at_ceiling:.1%}")
    print(f"  realized annualized vol (as-reg.)   : {ann_vol:.1%}")
    print(f"  registered target vol               : {TARGET_VOL:.1%}")
    print(f"  reported P(maxDD>40%) (HYPOTHESES.md): see caller")

    result = dict(pct_at_ceiling=pct_at_ceiling, realized_vol=ann_vol,
                  target_vol=TARGET_VOL, net=net)

    # E12 pattern = cap binds on most days AND realized vol sits well under
    # target (E12: 96.6% / 7.4% vs 15%). Only then does a rescale-and-rerun
    # mean anything; otherwise the two numbers are just... the two numbers.
    suppressed = pct_at_ceiling > 0.50 and ann_vol < TARGET_VOL * 0.85
    result["e12_pattern_reproduces"] = suppressed
    if suppressed:
        scale = TARGET_VOL / ann_vol
        rescaled_net = net * scale
        p_blow_rescaled = ts.bootstrap_p_maxdd(rescaled_net, 0.40)
        result["p_blow_rescaled_to_target"] = p_blow_rescaled
        print(f"  ARTIFACT REPRODUCES — rescaling {scale:.2f}x to hit 15%:")
        print(f"  P(maxDD>40%) at TRUE 15% target     : {p_blow_rescaled:.3f}")
    else:
        print("  Cap is NOT the dominant constraint here (unlike E12) —")
        print("  reported ruin number is not a suppressed-vol artifact.")
    return result


def main():
    print("Loading commodity panels (E9/E11 shared universe) ...", flush=True)
    cpanels = {r: L.load_ladder(f"{DATA}/ladders_commodity/{r}_ladder_1d.csv", r)
               for r in COMMO}
    cdaily = bt.daily_front_returns(cpanels)

    # --- E9: identical to run_e9() in phase2_termstructure.py ---
    e9_sig = bt.e9_signal(cpanels, 12)
    e9_book = bt.run_book(e9_sig, cdaily, tercile=True, bps_per_side=5.0)
    e9_res = cap_diagnostics(e9_book["w_daily"], cdaily, e9_book["net"], "E9")
    print(f"  (reported in HYPOTHESES.md: P(maxDD>40%) = 0.845)")

    # --- E11: identical to run_e11() in phase2_termstructure.py ---
    month_ends = e9_sig.index
    cot = cot_loader.load_cot(f"{DATA}/cot/cot_hedgers.csv")
    e11_sig = -cot_loader.hp_signal_at_month_ends(cot, month_ends, 13)
    e11_book = bt.run_book(e11_sig, cdaily, tercile=True, bps_per_side=5.0)
    e11_res = cap_diagnostics(e11_book["w_daily"], cdaily, e11_book["net"], "E11")
    print(f"  (reported in HYPOTHESES.md: P(maxDD>40%) = 0.766)")

    print(f"\n{'=' * 60}\nSUMMARY\n{'=' * 60}")
    for name, res in (("E9", e9_res), ("E11", e11_res)):
        verdict = "ARTIFACT PRESENT" if res["e12_pattern_reproduces"] else "clean — no cap-suppression artifact"
        print(f"  {name}: {verdict} "
              f"(cap-at-ceiling {res['pct_at_ceiling']:.1%}, "
              f"realized vol {res['realized_vol']:.1%} vs {res['target_vol']:.0%} target)")


if __name__ == "__main__":
    main()
