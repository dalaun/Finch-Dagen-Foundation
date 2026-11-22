#!/usr/bin/env python3
"""Generate a SYNTHETIC twelve-month ledger for the trustee rehearsal.

Every number comes from a public benchmark (benchmarks-ce.json,
benchmarks-tax.json) or from an assumption that scenarios.json states and
labels. Nothing here is the founder's spending. The output has the same
columns the real, sorted bank and card export will have once it exists
(rehearsal/06-handoff-transaction-export.md), plus the evidence flags the
twin needs, so rehearsal_run.py can run on either.

  python3 synthetic_year.py                    write every scenario's ledger to ./out
  python3 synthetic_year.py --out DIR          write somewhere else
  python3 synthetic_year.py --scenario base    one scenario
  python3 synthetic_year.py --mix FILE.json    reshape transaction counts per domain
                                               (a private counts file; never commit one)
  python3 synthetic_year.py --check            regenerate twice and prove it is reproducible

Seeded: the same seed gives byte-identical files. Standard library only.
Design and education, not legal, tax or financial advice.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLUMNS = ["date", "description", "amount", "direction", "domain", "payer_role", "payee_role",
           "business_share", "evidence", "scenario", "synthetic"]
MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# Season shapes: multiplier per month (Jan..Dec), each averaging 1.0.
SEASONS = {
    "flat": [1.0] * 12,
    # Chicago heating: gas and electric heavier Nov-Mar. Shape is an assumption, not a BLS figure.
    "heating": [1.6, 1.5, 1.25, 0.95, 0.75, 0.7, 0.75, 0.75, 0.7, 0.85, 1.1, 1.4],
    "holiday": [0.85, 0.8, 0.9, 0.95, 1.0, 1.0, 0.95, 1.05, 0.95, 0.95, 1.15, 1.45],
    "summer": [0.7, 0.7, 0.85, 0.95, 1.1, 1.3, 1.4, 1.35, 1.0, 0.95, 0.85, 0.85],
}
for name, s in SEASONS.items():
    k = 12 / sum(s)
    SEASONS[name] = [v * k for v in s]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def benchmarks() -> dict:
    out = {}
    for f in ("benchmarks-ce.json", "benchmarks-tax.json"):
        p = HERE / f
        if p.exists():
            out.update({k: v for k, v in load_json(p).items() if isinstance(v, dict)})
    return out


def resolve(ref, bm: dict) -> float:
    """A number, or "group.key" pointing into the benchmarks, or {"ref":..., "times":...}."""
    if isinstance(ref, (int, float)):
        return float(ref)
    if isinstance(ref, dict):
        return resolve(ref["ref"], bm) * float(ref.get("times", 1.0))
    group, key = ref.split(".", 1)
    try:
        return float(bm[group][key])
    except KeyError:
        sys.exit(f"benchmark {ref} not found: a missing figure blocks the run, it never defaults to zero")


def split_amounts(rng: random.Random, total: float, n: int, cv: float) -> list:
    """n positive amounts with the given spread that sum exactly to total (in cents)."""
    if n <= 0 or total <= 0:
        return []
    w = [max(rng.lognormvariate(0, cv) if cv > 0 else 1.0, 1e-6) for _ in range(n)]
    cents = round(total * 100)
    raw = [cents * x / sum(w) for x in w]
    out = [int(r) for r in raw]
    for i in sorted(range(n), key=lambda i: raw[i] - out[i], reverse=True)[: cents - sum(out)]:
        out[i] += 1
    return [c / 100 for c in out]


def scale_of(sc: dict, bm: dict) -> float:
    s = sc.get("spending_scale", 1.0)
    if isinstance(s, dict) and "over" in s:
        return resolve(s["ref"], bm) / resolve(s["over"], bm)
    return resolve(s, bm)


def line_rows(rng, line: dict, sc: dict, bm: dict, mix: dict) -> list:
    year = sc.get("year", 2026)
    annual = resolve(line["annual"], bm)
    if line.get("scaled", True):
        annual *= scale_of(sc, bm)
    annual *= sc.get("line_scale", {}).get(line["id"], 1.0)
    if annual <= 0:
        return []
    # Year-level draw: a real household is above or below the mean on each line.
    if line.get("year_cv", 0) > 0:
        annual *= rng.lognormvariate(-line["year_cv"] ** 2 / 2, line["year_cv"])
    season = SEASONS[line.get("season", "flat")]
    per_month = line.get("per_month", 1)
    per_month = mix.get(line["domain"], {}).get(line["id"], per_month) if mix else per_month
    ev_rate = line.get("evidence_rate", sc.get("evidence_rate", 1.0))
    rows = []
    for m in range(12):
        if line.get("months") and (m + 1) not in line["months"]:
            continue
        months_on = len(line["months"]) if line.get("months") else 12
        month_total = annual * season[m] / (12 if not line.get("months") else months_on) \
            if not line.get("months") else annual / months_on
        n = per_month if isinstance(per_month, int) else max(1, round(per_month))
        if line.get("count_jitter") and n > 1:
            n = max(1, n + rng.choice([-1, 0, 0, 1]))
        for amt in split_amounts(rng, month_total, n, line.get("cv", 0.25)):
            day = rng.randint(1, MONTH_DAYS[m]) if not line.get("day") else line["day"]
            evidence = line.get("evidence", [])
            # Records are imperfect: each line keeps its evidence only at the scenario's rate.
            has = evidence if (evidence and rng.random() < ev_rate) else []
            rows.append({
                "date": date(year, m + 1, day).isoformat(),
                "description": f"SYNTHETIC {line['label']}",
                "amount": f"{amt:.2f}",
                "direction": line.get("direction", "debit"),
                "domain": line["domain"],
                "payer_role": line.get("payer", "founder"),
                "payee_role": line.get("payee", "unrelated"),
                "business_share": f"{line.get('business_share', 0.0):.2f}",
                "evidence": "|".join(has),
                "scenario": sc["id"],
                "synthetic": "SYNTHETIC",
            })
    return rows


def generate(sc: dict, lines: list, bm: dict, mix: dict | None = None) -> list:
    rng = random.Random(sc["seed"])
    rows = []
    for line in lines + sc.get("extra_lines", []):
        if line["id"] in sc.get("drop_lines", []):
            continue
        rows.extend(line_rows(rng, line, sc, bm, mix or {}))
    rows.sort(key=lambda r: (r["date"], r["domain"], r["description"], r["amount"]))
    return rows


def to_csv(rows: list) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default=str(HERE / "scenarios.json"))
    ap.add_argument("--scenario")
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--mix")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    spec = load_json(Path(a.scenarios))
    bm = benchmarks()
    mix = load_json(Path(a.mix)) if a.mix else None
    scs = [s for s in spec["scenarios"] if not a.scenario or s["id"] == a.scenario]
    if not scs:
        sys.exit(f"no scenario {a.scenario}")
    if a.check:
        bad = 0
        for sc in scs:
            h1 = hashlib.sha256(to_csv(generate(sc, spec["lines"], bm, mix)).encode()).hexdigest()
            h2 = hashlib.sha256(to_csv(generate(sc, spec["lines"], bm, mix)).encode()).hexdigest()
            rows = generate(sc, spec["lines"], bm, mix)
            synthetic = all(r["synthetic"] == "SYNTHETIC" and r["description"].startswith("SYNTHETIC") for r in rows)
            ok = h1 == h2 and synthetic and rows
            bad += not ok
            print(f"{sc['id']:<16} {len(rows):>5} lines  reproducible={h1 == h2}  all-labelled={synthetic}  sha256={h1[:12]}")
        sys.exit(1 if bad else 0)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for sc in scs:
        rows = generate(sc, spec["lines"], bm, mix)
        (out / f"ledger-{sc['id']}.csv").write_text(to_csv(rows))
        print(f"wrote {out / ('ledger-' + sc['id'] + '.csv')}  ({len(rows)} lines)")


if __name__ == "__main__":
    main()
