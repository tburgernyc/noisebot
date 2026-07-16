"""QuantCrawler signal audit harness (registered protocol in HYPOTHESES.md).

Log every QC signal THE MOMENT it appears; score later against market
data with pessimistic adjudication. Append-only, hash-chained (tamper-
evident): each record contains sha256(prev_hash + record) so nothing can
be edited or reordered after the fact.

Usage:
  python3 shadow_qc.py log --symbol BTCUSD --dir long --entry 65000 \
      --stop 64000 --target 67000 [--note "ghost scalp"]
  python3 shadow_qc.py status          # count, days elapsed, open/closed
  python3 shadow_qc.py score           # adjudicate vs market data + gates

Decision rule (LOCKED before first signal): n>=60 closed signals AND
PF>=1.2 on R-multiples net of costs -> REGISTERABLE for pipeline entry;
otherwise REJECT and cancel subscription. Backfilled records (--ts) are
excluded from the registered count."""
from __future__ import annotations
import argparse, hashlib, json, os, sys, urllib.request
import datetime as dt

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "logs", "signals_qc.jsonl")
COST_BPS = 5.0  # per side, applied to R math via entry adjustment

YMAP = {"BTCUSD": "BTC-USD", "ETHUSD": "ETH-USD", "SOLUSD": "SOL-USD",
        "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "USDJPY=X",
        "NAS100": "NQ=F", "US100": "NQ=F", "SPX500": "ES=F", "US500": "ES=F",
        "XAUUSD": "GC=F", "USOIL": "CL=F"}


def _read():
    if not os.path.exists(OUT):
        return []
    return [json.loads(l) for l in open(OUT) if l.strip()]


def _chain_hash(prev_hash: str, rec: dict) -> str:
    body = json.dumps({k: v for k, v in rec.items() if k != "hash"},
                      sort_keys=True)
    return hashlib.sha256((prev_hash + body).encode()).hexdigest()


def cmd_log(a):
    recs = _read()
    prev = recs[-1]["hash"] if recs else "GENESIS"
    ts = a.ts or dt.datetime.now(dt.timezone.utc).isoformat()
    rec = {"ts_logged": ts, "symbol": a.symbol.upper(), "dir": a.dir,
           "entry": a.entry, "stop": a.stop, "target": a.target,
           "note": a.note or "", "backfilled": bool(a.ts),
           "prev_hash": prev}
    rec["hash"] = _chain_hash(prev, rec)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"logged #{len(recs)+1} {rec['symbol']} {rec['dir']} "
          f"@{rec['entry']} (backfilled={rec['backfilled']})")


def verify_chain(recs) -> bool:
    prev = "GENESIS"
    for r in recs:
        if r["prev_hash"] != prev or _chain_hash(prev, r) != r["hash"]:
            return False
        prev = r["hash"]
    return True


def fetch_hourly(ysym: str):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ysym}"
           f"?interval=1h&range=60d")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    r = json.loads(urllib.request.urlopen(req, timeout=30).read())
    res = r["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    return [(t, o, h, l, c) for t, o, h, l, c in
            zip(res["timestamp"], q["open"], q["high"], q["low"], q["close"])
            if None not in (o, h, l, c)]


def adjudicate(rec, bars):
    """Pessimistic: enter at first bar open after ts_logged (+cost);
    if stop and target both touch in one bar -> STOP (loss)."""
    t0 = dt.datetime.fromisoformat(rec["ts_logged"]).timestamp()
    sign = 1 if rec["dir"] == "long" else -1
    fut = [b for b in bars if b[0] > t0]
    if not fut:
        return {"state": "open", "r": None}
    entry = fut[0][1] * (1 + sign * COST_BPS / 1e4)
    risk = abs(entry - rec["stop"])
    if risk <= 0:
        return {"state": "invalid", "r": None}
    for t, o, h, l, c in fut:
        hit_stop = l <= rec["stop"] if sign == 1 else h >= rec["stop"]
        hit_tgt = h >= rec["target"] if sign == 1 else l <= rec["target"]
        if hit_stop:                       # pessimistic: stop first
            ex = rec["stop"] * (1 - sign * COST_BPS / 1e4)
            return {"state": "stopped", "r": sign * (ex - entry) / risk}
        if hit_tgt:
            ex = rec["target"] * (1 - sign * COST_BPS / 1e4)
            return {"state": "target", "r": sign * (ex - entry) / risk}
    last = fut[-1][4]
    return {"state": "open", "r": sign * (last - entry) / risk}


def cmd_score(a):
    recs = _read()
    if not recs:
        print("no signals logged"); return
    print("chain integrity:", "OK" if verify_chain(recs) else "BROKEN — AUDIT VOID")
    cache, rows = {}, []
    for rec in recs:
        ysym = YMAP.get(rec["symbol"], rec["symbol"])
        if ysym not in cache:
            try:
                cache[ysym] = fetch_hourly(ysym)
            except Exception as e:
                print(f"  fetch fail {ysym}: {e}"); cache[ysym] = []
        rows.append({**rec, **adjudicate(rec, cache[ysym])})
    closed = [r for r in rows if r["state"] in ("stopped", "target")
              and not r["backfilled"]]
    openn = [r for r in rows if r["state"] == "open"]
    for r in rows:
        print(f"  {r['ts_logged'][:16]} {r['symbol']:8} {r['dir']:5} "
              f"{r['state']:8} R={r['r'] if r['r'] is None else round(r['r'],2)}"
              f"{'  [backfilled—excluded]' if r['backfilled'] else ''}")
    if closed:
        rs = [r["r"] for r in closed]
        wins = [x for x in rs if x > 0]
        pf = sum(wins) / max(1e-9, -sum(x for x in rs if x <= 0))
        n = len(rs)
        print(f"\nCLOSED n={n}  WR {len(wins)/n:.1%}  PF {pf:.2f}  "
              f"avg R {sum(rs)/n:+.2f}  (open: {len(openn)})")
        print(f"GATE (n>=60 & PF>=1.2): "
              f"{'REGISTERABLE' if n >= 60 and pf >= 1.2 else 'NOT MET'}")
    else:
        print(f"\nno closed non-backfilled signals yet (open: {len(openn)})")


def cmd_status(a):
    recs = _read()
    if not recs:
        print("0 signals logged"); return
    real = [r for r in recs if not r["backfilled"]]
    t0 = dt.datetime.fromisoformat(real[0]["ts_logged"]) if real else None
    days = (dt.datetime.now(dt.timezone.utc) - t0).days if t0 else 0
    print(f"signals: {len(recs)} total, {len(real)} registered "
          f"({len(recs)-len(real)} backfilled/excluded); day {days} of audit; "
          f"chain: {'OK' if verify_chain(recs) else 'BROKEN'}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("log")
    pl.add_argument("--symbol", required=True)
    pl.add_argument("--dir", required=True, choices=["long", "short"])
    pl.add_argument("--entry", type=float, required=True)
    pl.add_argument("--stop", type=float, required=True)
    pl.add_argument("--target", type=float, required=True)
    pl.add_argument("--note")
    pl.add_argument("--ts", help="backfill timestamp (EXCLUDED from audit)")
    sub.add_parser("score")
    sub.add_parser("status")
    a = p.parse_args()
    {"log": cmd_log, "score": cmd_score, "status": cmd_status}[a.cmd](a)
