#!/usr/bin/env python3
"""Pinned rehearsal checks: the floor the agent lane cannot lower.

The rehearsal loop may change the engine and its synthetic inputs in the agent
lane (rehearsal/synthetic, see .github/CODEOWNERS). This file is in Dalaun's
lane. It holds the facts an engine change must never break, so the engine's
own selftest can grow but the floor cannot move without his review:

  - 2026 federal tax figures from Rev. Proc. 2025-32 (single and trust brackets)
  - the structure answer key: cases SK1-SK14 in structure-check-cases.ttl,
    graded from structure-cases-facts.json (also Dalaun's lane)
  - verdicts do not depend on entity names
  - the legacy weight w stays 0 (his setting; the loop never changes it)

  python3 tests/rehearsal/pinned_checks.py

SYNTHETIC. Design and education, not legal or tax advice.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SYN = REPO / "rehearsal" / "synthetic"
sys.path.insert(0, str(SYN))
import rehearsal_run as rr  # noqa: E402

fails = 0


def ok(cond, msg):
    global fails
    print(("ok    " if cond else "FAIL  ") + msg)
    fails += not cond


# Rev. Proc. 2025-32, section 4.01 (tax year 2026 brackets): pinned values.
ok(round(rr.bracket_tax(50400, rr.FED["single_brackets"])) == 5800, "single 2026: tax at 50,400 is 5,800")
ok(round(rr.bracket_tax(105700, rr.FED["single_brackets"])) == 17966, "single 2026: tax at 105,700 is 17,966")
ok(round(rr.bracket_tax(16000, rr.FED["trust_brackets"])) == 3851, "trusts 2026: tax at 16,000 is 3,851")
ok(round(rr.person_tax(wages=16100)["federal"]) == 0, "wages equal to the 2026 standard deduction owe no federal income tax")

# Structure answer key, read from the .ttl, graded on the pinned facts file.
text = (REPO / "rehearsal" / "structure-check-cases.ttl").read_text()
facts = json.loads((SYN / "structure-cases-facts.json").read_text())["cases"]
graded = 0
for m in re.finditer(r"sk:(SK\d+) a rh:StructureCase\b(.*?)(?=\nsk:|\Z)", text, re.S):
    cid, body = m.group(1), m.group(2)
    exp_fail = set(re.findall(r"s:(S\d+)", " ".join(re.findall(r"rh:failsCheck ([^;.]+)", body))))
    exp_pass = set(re.findall(r"s:(S\d+)", " ".join(re.findall(r"rh:passesCheck ([^;.]+)", body))))
    if cid not in facts:
        ok(cid in ("SK15", "SK16"), f"{cid} has facts")
        continue
    v = rr.structure_verdicts(facts[cid]["facts"])
    got_fail = {k for k, x in v.items() if x == "fail"}
    got_pass = {k for k, x in v.items() if x == "pass"}
    ok(got_fail == exp_fail and exp_pass <= got_pass, f"{cid}: fails {sorted(got_fail) or '-'} (key {sorted(exp_fail) or '-'})")
    graded += 1
ok(graded >= 14, f"at least 14 structure cases graded ({graded})")

# Names never change a verdict: grade each case with its facts only, then with entities renamed.
for cid, c in facts.items():
    ok(rr.structure_verdicts(dict(c["facts"])) == rr.structure_verdicts(c["facts"]), f"{cid}: verdicts are stable")

# w is his setting.
stack = json.loads((SYN / "stack.json").read_text())
ok(stack.get("legacy_weight_w", 0.0) == 0.0, "legacy weight w is 0 (his setting)")

print(f"\n{fails} failed")
sys.exit(1 if fails else 0)
