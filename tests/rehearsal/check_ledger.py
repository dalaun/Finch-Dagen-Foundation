#!/usr/bin/env python3
"""Check the score ledger's newest rows are what the engine produces now.

The rehearsal loop appends its scores to rehearsal/loop/score-ledger.csv.
The lane guard makes sure earlier rows are never rewritten. This check makes
sure the newest block of rows (one per scenario and structure version) is
exactly what the engine in this commit computes on the seeded synthetic year,
so a score cannot be typed in by hand.

  python3 tests/rehearsal/check_ledger.py

Dalaun's lane (.github/CODEOWNERS). SYNTHETIC.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SYN = REPO / "rehearsal" / "synthetic"
LEDGER = REPO / "rehearsal" / "loop" / "score-ledger.csv"


def main() -> int:
    rows = list(csv.DictReader(LEDGER.open()))
    with tempfile.TemporaryDirectory() as d:
        subprocess.run([sys.executable, str(SYN / "synthetic_year.py"), "--out", d], check=True, capture_output=True)
        out = Path(d) / "results.json"
        subprocess.run([sys.executable, str(SYN / "rehearsal_run.py"), "--ledgers", d, "--json", str(out)],
                       check=True, capture_output=True)
        results = json.loads(out.read_text())["results"]
    expected = []
    for r in results:
        be = ["none" if x is None else str(int(x)) for x in r["break_even"].values()]
        for vid, v in r["versions"].items():
            expected.append([r["scenario"], vid, v["status"], str(v["checks_pass"]), str(v["score_vs_A"]),
                             str(v["structure_value"]), str(v["structure_gap"]), *be])
    cols = ["scenario", "version", "status", "checks_pass", "score_vs_A", "structure_value", "structure_gap",
            "break_even_grantor", "break_even_professional", "break_even_individual"]
    tail = rows[-len(expected):]
    got = [[row[c] for c in cols] for row in tail]
    if len(rows) < len(expected) or len({row["date"] for row in tail}) != 1:
        print(f"FAIL  the newest {len(expected)} ledger rows are not one dated run")
        return 1
    bad = [(g, e) for g, e in zip(got, expected) if g != e]
    for g, e in bad:
        print(f"FAIL  ledger row {g[:2]}: ledger {g[2:]} vs engine {e[2:]}")
    print("ok    newest ledger rows match the engine" if not bad else f"\n{len(bad)} rows differ")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
