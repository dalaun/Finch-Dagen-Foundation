#!/usr/bin/env python3
"""Substance at every step: each route declares its non-tax purpose first, and
every step it takes has to do something real apart from tax.

The economic substance doctrine (IRC 7701(o)) and substance over form apply to
every route the rehearsal runs. The rehearsal checks them the same way it
checks the keystone constraint and the accountable plan: at each step, not
only at the end. A step whose only effect is a tax result fails.

  python3 substance.py                    every route in substance-synthetic.json
  python3 substance.py --as-of 2026-06-30  the routes as they stood that day
  python3 substance.py --json out.json     also write the results
  python3 substance.py --selftest          the check's own cases

Verdicts: pass, fail, amber (a fact is unknown, or the text read does not
settle it: a counsel question). A missing field is an error, never a pass.

Sources read 2026-11-26 (quotes in SUBSTANCE.md):
- 7701(o)(1), (o)(5)(A)-(D): Patel v. Commissioner, 165 T.C. No. 10 (2025), as
  quoted in The Tax Adviser, Feb 28, 2026; (o)(1)(A)-(B) also in the register
  (A1, govinfo 2020 edition) and in the Solicitor General's 2019 brief in
  Tucker v. Commissioner. (o)(2)-(o)(4) were NOT read.
- IRS Notice 2010-62.
- IRC 6664(c)(2), https://www.law.cornell.edu/uscode/text/26/6664.
- Substance over form: register A2 (Notice 97-24, Markosian) and A3 (Court
  Holding). Each tool's own test: the trace named on the route.
SYNTHETIC. Design and education, not legal or tax advice.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT = HERE / "substance-synthetic.json"

# Purposes 7701(o)(3) and (o)(4) speak to. Those paragraphs were NOT read, so
# a purpose of this kind turns SB4 amber, never pass.
UNREAD_PURPOSE_KINDS = {"state_local_tax", "financial_accounting"}

ROUTE_FIELDS = ["id", "tool", "family", "tool_test", "tool_trace", "federal_tax_benefit",
                "individual_business_or_income", "declared_purpose", "steps", "end_state", "form"]


def _d(s):
    return date.fromisoformat(s) if s else None


def _v(val):
    return "pass" if val is True else ("fail" if val is False else "amber")


def _need(route: dict):
    missing = [k for k in ROUTE_FIELDS if k not in route]
    if missing:
        raise KeyError(f"{route.get('id', '?')}: missing field(s) {missing} (fail closed)")
    for k in ["economic_position_changed", "living_costs_paid_untaxed"]:
        if k not in route["end_state"]:
            raise KeyError(f"{route['id']}: end_state missing {k} (fail closed)")
    for k in ["terms_followed", "relationship_to_property_changed"]:
        if k not in route["form"]:
            raise KeyError(f"{route['id']}: form missing {k} (fail closed)")


def relevance(route: dict):
    """(applies, why). 7701(o)(1) runs only on a transaction to which the doctrine
    is relevant; (o)(5)(C) says relevance is judged as if (o) were never enacted,
    and Patel (2025) holds the question is separate from the two-part test.
    The rehearsal settles it the cautious way (ASSUMPTION, Q45)."""
    if not route["federal_tax_benefit"]:
        return False, "no federal tax benefit claimed, so there is nothing for the doctrine to deny"
    if route["individual_business_or_income"] is False:
        return False, "an individual's personal transaction, outside a trade or business or income activity (7701(o)(5)(B))"
    return True, "treated as relevant, the cautious reading (ASSUMPTION, Q45)"


def run_route(route: dict, rates: dict, as_of=None) -> dict:
    _need(route)
    steps = sorted((s for s in route["steps"] if as_of is None or _d(s["date"]) <= as_of), key=lambda s: s["date"])
    applies, why = relevance(route)
    purpose = route["declared_purpose"]
    checks = []

    checks.append(("SB0", "pass", f"Relevance: {'applies' if applies else 'does not apply'}, {why}",
                   "IRC 7701(o)(1), (o)(5)(B), (o)(5)(C); Patel, 165 T.C. No. 10 (2025)"))

    # SB1 the non-tax purpose is declared, in writing, before the first step.
    first = _d(steps[0]["date"]) if steps else None
    declared = _d(purpose.get("declared_on")) if purpose else None
    ok1 = bool(purpose and purpose.get("text") and declared and (first is None or declared <= first))
    checks.append(("SB1", "pass" if ok1 else "fail",
                   "Non-tax purpose written and dated before the first step", "IRC 7701(o)(1)(B); timing ASSUMPTION, Q46"))

    # SB2 the step invariant: every step so far does something real apart from tax.
    # The doctrine tests the transaction, and (o)(5)(D) makes that include a series;
    # holding each step too is stricter, never looser (ASSUMPTION, Q47).
    tax_only = [s for s in steps if s["effects"].get("tax") and not s["effects"].get("nontax")]
    lab2 = "Every step so far changes something real apart from tax (who owns, risks, controls or is owed what)"
    if tax_only:
        lab2 += f" (tax-only step(s): {', '.join(s['id'] for s in tax_only)}; first {tax_only[0]['date']})"
    checks.append(("SB2", "fail" if tax_only and applies else ("amber" if tax_only else "pass"), lab2,
                   "IRC 7701(o)(1)(A), (o)(5)(D); per-step ASSUMPTION, Q47"))

    # SB3 the series, collapsed: start to end, the economic position changes, and
    # the end result is not the founder paying his own living costs untaxed.
    es = route["end_state"]
    ok3 = es["economic_position_changed"] is True and es["living_costs_paid_untaxed"] is False
    unknown3 = es["economic_position_changed"] is None or es["living_costs_paid_untaxed"] is None
    checks.append(("SB3", "amber" if unknown3 else ("pass" if ok3 or not applies else "fail"),
                   "Collapse the steps: the end state changes the economic position apart from tax, and isn't living costs paid with untaxed money",
                   "IRC 7701(o)(1)(A), (o)(5)(D); Court Holding (register A3)"))

    # SB4 the declared purpose is real: it is one of the non-tax effects the steps produced.
    produced = {e for s in steps for e in s["effects"].get("nontax", [])}
    kind = purpose.get("kind") if purpose else None
    if kind in UNREAD_PURPOSE_KINDS:
        v4, lab4 = "amber", f"Declared purpose is a {kind.replace('_', ' ')} benefit: 7701(o)(3)/(o)(4) not read (NOT TRACED)"
    else:
        realized = bool(purpose) and purpose.get("effect") in produced
        v4 = "pass" if realized or not applies else "fail"
        lab4 = "The declared non-tax purpose is an effect the steps actually produced" + ("" if realized else " (not produced)")
    checks.append(("SB4", v4, lab4, "IRC 7701(o)(1)(B)"))

    # SB5 form follows substance: the arrangement follows its own terms and, for a
    # transfer, the old owner's relationship to the property really changed.
    f = route["form"]
    vals = [f["terms_followed"]] + ([f["relationship_to_property_changed"]] if f["relationship_to_property_changed"] != "n/a" else [])
    v5 = "fail" if False in vals else ("amber" if None in vals else "pass")
    checks.append(("SB5", v5, "Form follows substance: terms followed, and a transfer really changes the old owner's relationship to the property",
                   "Notice 97-24; Markosian, 73 T.C. 1235 (register A2)"))

    # SB6 the tool's own statutory test, from its trace (the substance checks sit on top of it).
    checks.append(("SB6", {"pass": "pass", "fail": "fail"}.get(route["tool_test"], "amber"),
                   f"The tool's own test ({route['tool']}): {route.get('tool_note', route['tool_test'])}", route["tool_trace"]))

    # Consequence. A relevant route that fails SB2, SB3 or SB4 loses the tax
    # benefit; 6662(b)(6) adds 20%, 6662(i) 40% if not disclosed, and 6664(c)(2)
    # removes the reasonable-cause defense. Amounts are placeholders.
    fails = [c[0] for c in checks if c[1] == "fail" and c[0] in ("SB2", "SB3", "SB4")]
    benefit = float(route.get("benefit_placeholder", 0))
    if applies and fails:
        under = benefit * rates["federal_marginal"]
        pct = 0.20 if route.get("disclosed") else 0.40
        consequence = {"lacks_substance": True, "failed": fails, "benefit_denied_placeholder": benefit,
                       "underpayment_placeholder": round(under, 2), "penalty_rate": pct,
                       "penalty_placeholder": round(under * pct, 2),
                       "reasonable_cause_defense": False,
                       "basis": "IRC 6662(b)(6), 6662(i) (register A1); 6664(c)(2)"}
    else:
        consequence = {"lacks_substance": False, "failed": fails}
    return {"id": route["id"], "tool": route["tool"], "family": route["family"], "label": route["label"],
            "checks": [{"id": c[0], "verdict": c[1], "label": c[2], "cite": c[3]} for c in checks],
            "consequence": consequence}


def run(inputs: dict, as_of=None) -> list:
    return [run_route(r, inputs["rates"], as_of) for r in inputs["routes"]]


def summarize(results: list) -> str:
    lines = ["SYNTHETIC substance run. Not legal or tax advice.", ""]
    tot = {"pass": 0, "amber": 0, "fail": 0}
    fam = None
    for r in results:
        if r["family"] != fam:
            fam = r["family"]
            lines.append(f"## {fam}")
        c = [x["verdict"] for x in r["checks"]]
        for v in c:
            tot[v] += 1
        lines.append(f"== {r['id']} [{r['tool']}]: {c.count('pass')} pass / {c.count('amber')} amber / {c.count('fail')} fail")
        for x in r["checks"]:
            if x["verdict"] != "pass" or x["id"] == "SB0":
                lines.append(f"   {x['verdict']:5}  {x['id']} {x['label']}  [{x['cite']}]")
        k = r["consequence"]
        if k["lacks_substance"]:
            lines.append(f"   consequence: benefit denied; penalty {k['penalty_rate']:.0%} of the underpayment, no reasonable-cause defense "
                         f"(placeholder {k['penalty_placeholder']:,.0f})")
    lines.append("")
    lines.append(f"Routes: {len(results)}. Checks: {sum(tot.values())} ({tot['pass']} pass, {tot['amber']} amber, {tot['fail']} fail)")
    return "\n".join(lines)


def selftest() -> int:
    bad = 0

    def expect(name, cond):
        nonlocal bad
        print(("ok   " if cond else "FAIL ") + name)
        bad += 0 if cond else 1

    inputs = json.loads(DEFAULT.read_text())
    res = {r["id"]: r for r in run(inputs)}
    v = lambda r, cid: next(c["verdict"] for c in r["checks"] if c["id"] == cid)
    get = lambda rid: json.loads(json.dumps(next(x for x in inputs["routes"] if x["id"] == rid)))
    expect("every route names its tool", all(r["tool"] for r in res.values()))
    expect("accountable plan route passes every substance check",
           all(c["verdict"] == "pass" for c in res["R-62c"]["checks"]))
    expect("circular loans: tax-only steps fail at the step", v(res["R-loop"], "SB2") == "fail")
    expect("circular loans: the collapsed series fails too", v(res["R-loop"], "SB3") == "fail")
    expect("circular loans: penalty 40% when not disclosed, no reasonable cause",
           res["R-loop"]["consequence"]["penalty_rate"] == 0.40 and res["R-loop"]["consequence"]["reasonable_cause_defense"] is False)
    expect("gift and back before death: series fails the collapse", v(res["R-giftback"], "SB3") == "fail")
    expect("spendthrift clause: no tax benefit, so the doctrine doesn't apply",
           res["R-spendthrift"]["checks"][0]["label"].startswith("Relevance: does not apply"))
    expect("cafeteria plan stays amber until 125 is traced", v(res["R-125"], "SB6") == "amber")
    expect("education plan fails its own test while he is the only employee", v(res["R-127"], "SB6") == "fail")
    # purpose written after the first step fails SB1
    r = get("R-62c"); r["declared_purpose"]["declared_on"] = "2026-12-31"
    expect("purpose written after the first step fails SB1", v(run_route(r, inputs["rates"]), "SB1") == "fail")
    # one tax-only step in an otherwise real route fails SB2 at that step
    r = get("R-132"); r["steps"].append({"id": "s9", "date": "2026-09-01", "effects": {"tax": True, "nontax": []}})
    rr = run_route(r, inputs["rates"])
    expect("one tax-only step fails SB2 and names it", v(rr, "SB2") == "fail" and "s9" in rr["checks"][2]["label"])
    # as of a day before that step, the route is still clean
    expect("as of the day before, the same route is clean", v(run_route(r, inputs["rates"], as_of=date(2026, 8, 31)), "SB2") == "pass")
    # declared purpose never produced fails SB4
    r = get("R-674c"); r["declared_purpose"]["effect"] = "something_else"
    expect("a declared purpose the steps never produce fails SB4", v(run_route(r, inputs["rates"]), "SB4") == "fail")
    # state-tax purpose stays amber (7701(o)(3) not read)
    r = get("R-674c"); r["declared_purpose"]["kind"] = "state_local_tax"
    expect("a state-tax purpose stays amber until (o)(3) is read", v(run_route(r, inputs["rates"]), "SB4") == "amber")
    # trust that ignores its own terms fails SB5
    r = get("R-674c"); r["form"]["terms_followed"] = False
    expect("a trust that ignores its terms fails SB5", v(run_route(r, inputs["rates"]), "SB5") == "fail")
    # a missing field is an error
    r = get("R-62c"); del r["end_state"]
    try:
        run_route(r, inputs["rates"]); expect("missing field raises", False)
    except KeyError:
        expect("missing field raises", True)
    # a disclosed failing route gets 20%, not 40%
    r = get("R-loop"); r["disclosed"] = True
    expect("disclosed failure: 20% penalty", run_route(r, inputs["rates"])["consequence"]["penalty_rate"] == 0.20)
    print(f"\n{bad} failure(s)")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="?", default=str(DEFAULT))
    ap.add_argument("--json")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--as-of", help="YYYY-MM-DD: judge each route as it stood that day")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    inputs = json.loads(Path(a.inputs).read_text())
    results = run(inputs, _d(a.as_of))
    print(summarize(results))
    if a.json:
        Path(a.json).write_text(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
