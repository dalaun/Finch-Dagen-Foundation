#!/usr/bin/env python3
"""Hiring to pass the owner limits: who counts as owner-side, whether the hire
is real, who approved the pay, and what it's worth.

Three benefit tools stop working while the founder is the company's only
employee, because each caps how much can go to owners:

  127 educational assistance   owners get at most 5% of the year's spending
  129 dependent care           owners get at most 25%, and the non-highly-
                               compensated average must be at least 55% of
                               the highly compensated average
  125 cafeteria plan           key employees get at most 25% of the plan's
                               qualified benefits

Every hire gets four checks, and has to pass all four to count:

  HA1 arm's length    market pay for real work (IRC 162(a)(1), Reg. 1.162-7)
  HA2 substance       the hire has a non-tax purpose of its own, declared
                      before the hire (SUBSTANCE.md); a hire made only to
                      unlock a benefit fails
  HA3 attribution     not owner-side: 1563(d)-(e) for 127 and 129, 318 via
                      416(i) for 125. Siblings aren't attributed under either.
  HA4 board record    approved before the money moves, by approvers with no
                      stake who aren't attributed family, with market
                      comparables and minutes (the declared-plan pattern)

The board record is evidence for HA1. It never changes HA3: a parent approved
by a perfect board is still owner-side.

  python3 hiring.py              every case in hiring-synthetic.json
  python3 hiring.py --selftest   the check's own cases

Sources read 2026-11-26 at https://www.law.cornell.edu/uscode/text/26/ (127,
129, 125, 318, 1563, 416; quotes in HIRING.md). SYNTHETIC: roles, placeholder
pay and rates. Design and education, not legal or tax advice.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT = HERE / "hiring-synthetic.json"

LIMIT = {"127": 0.05, "129": 0.25, "125": 0.25}
AVG_TEST_129 = 0.55          # 129(d)(8)(A)
SALARY_REDUCTION_FLOOR = 25000  # 129(d)(8)(B): may disregard pay under this

# 1563(e)(5)-(6): spouse; children under 21; and, where the individual owns
# more than 50%, parents, grandparents, grandchildren and adult children.
ATTRIB_1563 = {"spouse": "always", "child_under_21": "always", "parent": "over_50",
               "grandparent": "over_50", "grandchild": "over_50", "child_21_plus": "over_50"}
# 318(a)(1): spouse, children, grandchildren, parents (no grandparents).
ATTRIB_318 = {"spouse", "child_under_21", "child_21_plus", "grandchild", "parent"}

# ASSUMPTION (Q49): pay counts as market when it sits within this band of the
# documented comparable. 1.162-7 caps pay at what is reasonable; the floor
# keeps a family hire from being a disguised gift of labor.
MARKET_BAND = (0.8, 1.1)


def _d(s):
    return date.fromisoformat(s) if s else None


def owner_side(rel: str, owner_share: float, test: str) -> bool:
    if rel in (None, "none", "sibling"):
        return False
    if test == "1563":
        rule = ATTRIB_1563.get(rel)
        return rule == "always" or (rule == "over_50" and owner_share > 0.5)
    return rel in ATTRIB_318


def hire_checks(h: dict, case: dict) -> list:
    out = []
    lo, hi = MARKET_BAND
    m = h["market_pay"]
    if h.get("work_for") == "owner_household":
        # maids, a butler, a cook: work in and around the owner's home is
        # household work for the owner is a personal cost, however much it frees the owner's time
        out.append(("HA1", "fail",
                    f"{h['id']}: household work in the owner's home is personal, not the company's work",
                    "IRC 262(a); IRS Pub. 926 and Topic 756 (household workers, Schedule H)"))
    else:
        arm = bool(h["real_work"]) and m > 0 and lo * m <= h["pay"] <= hi * m
        out.append(("HA1", "pass" if arm else "fail",
                    f"{h['id']}: market pay for real work ({h['pay']:,.0f} against {m:,.0f})",
                    "IRC 162(a)(1); Reg. 1.162-7 (register B1, B3); band ASSUMPTION, Q49"))
    p = h.get("purpose") or {}
    sub = bool(p.get("text")) and not h.get("unlock_only") and _d(p.get("declared_on")) is not None \
        and _d(p["declared_on"]) <= _d(h["start"])
    out.append(("HA2", "pass" if sub else "fail",
                f"{h['id']}: hired for the work, purpose written before the start, not only to unlock a benefit",
                "IRC 7701(o)(1); SUBSTANCE.md"))
    o1563 = owner_side(h["relation"], case["owner_share"], "1563")
    o318 = owner_side(h["relation"], case["owner_share"], "318")
    out.append(("HA3", "fail" if (o1563 or o318) else "pass",
                f"{h['id']}: not owner-side ({h['relation']}; 1563: {'owner-side' if o1563 else 'no'}, 318: {'owner-side' if o318 else 'no'})",
                "IRC 127(c)(4)(A), 129(e)(5)(A), 1563(e)(5)-(6); 125(b)(2), 416(i)(1)(B), 318(a)(1)"))
    b = h.get("board") or {}
    approvers = b.get("approvers", [])
    indep = bool(approvers) and all(not a.get("stake") and not owner_side(a.get("relation"), case["owner_share"], "318")
                                    and a.get("relation") != "self" for a in approvers)
    before = _d(b.get("approved_on")) is not None and _d(b["approved_on"]) <= _d(h["start"])
    ok = indep and before and bool(b.get("comparables")) and bool(b.get("minutes"))
    out.append(("HA4", "pass" if ok else ("amber" if b.get("independence_unsettled") and before else "fail"),
                f"{h['id']}: approved before the start by independent approvers, with comparables and minutes"
                + (" (approver independence depends on who can remove them: Q48)" if b.get("independence_unsettled") else ""),
                "declared-plan pattern (DECLARED-PLAN.md); evidence for 162, not a cure (Q48)"))
    return out


def family_office_checks(fo: dict) -> list:
    """Lender Management, LLC v. Commissioner, T.C. Memo. 2017-246, Docket Nos.
    25617-15, 25618-15, filed Dec. 13, 2017 (Kerrigan, J.), caption read on
    Leagle; the opinion text was behind a paywall and not read: a
    family-controlled manager carried on a trade or business under 162 because
    it ran a profit-seeking investment management business, not its owners'
    own portfolio (Higgins). The facts the court leaned on become checks."""
    keys = ["clients_mostly_non_owners", "paid_for_services_not_capital", "salaried_staff",
            "services_beyond_an_investor", "bona_fide_under_scrutiny"]
    missing = [k for k in keys if k not in fo]
    if missing:
        raise KeyError(f"family_office: missing {missing} (fail closed)")
    rows = [
        ("FO1", fo["clients_mostly_non_owners"], "Most of the money managed belongs to people who don't own the manager"),
        ("FO2", fo["paid_for_services_not_capital"], "Paid for its services (a fee or profits interest earned only on results), not a return on its own capital"),
        ("FO3", fo["salaried_staff"], "Real staff on salary doing the work"),
        ("FO4", fo["services_beyond_an_investor"], "Services go beyond keeping records and collecting income (Higgins)"),
        ("FO5", fo["bona_fide_under_scrutiny"], "Bona fide under heightened scrutiny: clients can leave, no promise to keep the manager forever, independent approval"),
    ]
    cite = "Lender Management, LLC v. Commissioner, T.C. Memo. 2017-246 (caption checked; holding and facts from secondary sources, Q51); Higgins, 312 U.S. 212 (register E1)"
    return [(cid, _v(val), lab, cite) for cid, val, lab in rows]


def _v(val):
    return "pass" if val is True else ("fail" if val is False else "amber")


def run_case(case: dict, rates: dict) -> dict:
    checks, counted, owner_side_hires = [], [], []
    for h in case["hires"]:
        hc = hire_checks(h, case)
        checks += hc
        v = {c[0]: c[1] for c in hc}
        if v["HA3"] == "fail":
            owner_side_hires.append(h)        # attributed: counts with the owner, whatever else
        elif v["HA1"] == "pass" and v["HA2"] == "pass":
            counted.append(h)                 # a real, unrelated hire
        # a hire failing HA1 or HA2 is disregarded (ASSUMPTION, Q50)
    own = case["owner_benefits"]
    tools = {}
    for t in ("127", "129", "125"):
        o_amt = own[t] + sum(h["uptake"].get(t, 0) for h in owner_side_hires)
        others = sum(h["uptake"].get(t, 0) for h in counted)
        total = o_amt + others
        share = o_amt / total if total else (1.0 if o_amt else 0.0)
        cap = others * LIMIT[t] / (1 - LIMIT[t])           # most the owner side can take
        ok = share <= LIMIT[t]
        note = f"owner side {o_amt:,.0f} of {total:,.0f} ({share:.0%}, limit {LIMIT[t]:.0%}); owner side could take at most {cap:,.0f}"
        if t == "129":
            pool = [h for h in counted if h["pay"] >= SALARY_REDUCTION_FLOOR or not case.get("salary_reduction")]
            nhce = sum(h["uptake"].get("129", 0) for h in pool) / len(pool) if pool else 0.0
            hce = own["129"]
            avg_ok = hce == 0 or nhce >= AVG_TEST_129 * hce
            cap = min(cap, nhce / AVG_TEST_129) if hce else cap
            note += f"; non-HCE average {nhce:,.0f} vs 55% of {hce:,.0f} = {AVG_TEST_129 * hce:,.0f}"
            ok = ok and avg_ok
            related = case.get("care_paid_to_related_individual")
            if related:
                ok = False
                note += "; care paid to a dependent or the employee's child under 19 (129(c))"
        # break-even: unrelated hires at this case's average uptake needed to fit the owner's amount
        per = (others / len(counted)) if counted else case["assumed_uptake"][t]
        need = math.ceil(o_amt * (1 - LIMIT[t]) / LIMIT[t] / per) if per else None
        if t == "129" and per and own["129"]:
            need = max(need, 1) if per >= AVG_TEST_129 * own["129"] else None
        tools[t] = {"pass": ok, "note": note, "owner_cap": round(cap, 2), "break_even_unrelated_hires": need,
                    "uptake_per_hire": round(per, 2)}
        checks.append((f"T{t}", "pass" if ok else "fail", f"IRC {t} owner limit: {note}",
                       {"127": "IRC 127(b)(3), (c)(4)(A)", "129": "IRC 129(d)(4), (d)(8), (e)(5)(A), 129(c)",
                        "125": "IRC 125(b)(2), (e)(1); 416(i)(1)"}[t]))
    # AI agents are never employees: not in headcount, not in any owner test.
    # They are a deductible cost that raises what each real hire produces.
    ai = case.get("ai") or {}
    if ai:
        checks.append(("AI0", "pass", f"AI agents ({ai.get('agents', 0)}) counted as employees: none; they change no owner test",
                       "IRC 127(c)(2), 129(e)(3), 125(d)(1)(A) (employees are people); AI as a 162 cost: ASSUMPTION, Q52"))
    fo = case.get("family_office")
    if fo:
        checks += family_office_checks(fo)
    # value: what the owner keeps out of wages, at placeholder rates; health under
    # 106(a) needs no other employees, so it is never counted as unlocked by a hire
    r = rates["wage_tax_avoided"]
    unlocked = {t: (own[t] if tools[t]["pass"] else min(own[t], tools[t]["owner_cap"])) for t in ("127", "129")}
    value = round(sum(unlocked.values()) * r, 2)
    payroll = sum(h["pay"] for h in case["hires"]) * (1 + rates["employer_payroll_tax"])
    benefits_cost = sum(h.get("employer_paid_benefits", 0) for h in case["hires"])
    admin = case.get("plan_admin_cost", 0)
    loaded = [h["pay"] * (1 + rates["employer_payroll_tax"]) for h in counted]
    avg_loaded = sum(loaded) / len(loaded) if loaded else 0.0
    out_per = case.get("output_per_hire_placeholder", 0)
    lift, ai_cost = ai.get("output_lift", 0.0), ai.get("cost_per_hire", 0.0)
    earns = {"output_needed_per_hire_without_ai": round(avg_loaded, 2),
             "output_needed_per_hire_with_ai": round((avg_loaded + ai_cost) / (1 + lift), 2) if loaded else 0.0,
             "hire_earns_pay_without_ai": bool(loaded) and out_per >= avg_loaded,
             "hire_earns_pay_with_ai": bool(loaded) and out_per * (1 + lift) - ai_cost >= avg_loaded}
    return {"id": case["id"], "label": case["label"], "tool": case.get("tool", "IRC 127, 129, 125"), "note": case.get("note"), "checks":
            [{"id": c[0], "verdict": c[1], "label": c[2], "cite": c[3]} for c in checks],
            "tools": tools,
            "economics": {"payroll_cost_with_employer_tax": round(payroll, 2), "employer_paid_benefits": benefits_cost,
                          "plan_admin_cost": admin, "owner_amount_unlocked": unlocked,
                          "tax_value_to_owner_placeholder": value,
                          "net_if_hires_are_only_for_the_benefit": round(value - payroll - benefits_cost - admin, 2),
                          "net_if_hires_earn_their_pay": round(value - benefits_cost - admin, 2),
                          "earns_its_pay": earns}}


def run(inputs: dict) -> list:
    return [run_case(c, inputs["rates"]) for c in inputs["cases"]]


def summarize(results: list) -> str:
    out = ["SYNTHETIC hiring run. Not legal or tax advice.", ""]
    for r in results:
        v = [c["verdict"] for c in r["checks"]]
        out.append(f"== {r['id']}: {r['label']}  ({v.count('pass')} pass / {v.count('amber')} amber / {v.count('fail')} fail)")
        for c in r["checks"]:
            out.append(f"   {c['verdict']:5}  {c['id']:4} {c['label']}")
        for t, x in r["tools"].items():
            out.append(f"   {t}: break-even unrelated hires {x['break_even_unrelated_hires']} at {x['uptake_per_hire']:,.0f} uptake each")
        if r.get("note"):
            out.append(f"   note: {r['note']}")
        e = r["economics"]
        ea = e["earns_its_pay"]
        if ea["output_needed_per_hire_without_ai"]:
            out.append(f"   each real hire must bring in {ea['output_needed_per_hire_without_ai']:,.0f} without AI, "
                       f"{ea['output_needed_per_hire_with_ai']:,.0f} with AI tools")
        out.append(f"   payroll {e['payroll_cost_with_employer_tax']:,.0f}; employer-paid benefits {e['employer_paid_benefits']:,.0f}; "
                   f"tax value to owner {e['tax_value_to_owner_placeholder']:,.0f}; net if hired only for the benefit "
                   f"{e['net_if_hires_are_only_for_the_benefit']:,.0f}; net if the hires earn their pay {e['net_if_hires_earn_their_pay']:,.0f}")
        out.append("")
    return "\n".join(out)


def selftest() -> int:
    bad = 0

    def expect(name, cond):
        nonlocal bad
        print(("ok   " if cond else "FAIL ") + name)
        bad += 0 if cond else 1

    inputs = json.loads(DEFAULT.read_text())
    res = {r["id"]: r for r in run(inputs)}
    v = lambda rid, cid: [c["verdict"] for c in res[rid]["checks"] if c["id"] == cid]
    expect("parent is owner-side when the owner holds over 50% (1563(e)(6)(B))", owner_side("parent", 1.0, "1563"))
    expect("parent is not owner-side under 1563 at 50% or less", not owner_side("parent", 0.5, "1563"))
    expect("parent is owner-side under 318 at any share", owner_side("parent", 0.1, "318"))
    expect("brother is not owner-side under 1563 or 318", not owner_side("sibling", 1.0, "1563") and not owner_side("sibling", 1.0, "318"))
    expect("grandparent: 1563 over 50% yes, 318 no", owner_side("grandparent", 1.0, "1563") and not owner_side("grandparent", 1.0, "318"))
    expect("family-only: every owner limit fails", all(not x["pass"] for x in res["H-family"]["tools"].values()))
    expect("family-only: the parent passes arm's length but fails attribution",
           v("H-family", "HA1") == ["pass"] and v("H-family", "HA3") == ["fail"])
    expect("unrelated staff: 129 and 125 pass", res["H-unrelated"]["tools"]["129"]["pass"] and res["H-unrelated"]["tools"]["125"]["pass"])
    expect("unrelated staff: 127 still fails at real uptake", not res["H-unrelated"]["tools"]["127"]["pass"])
    expect("brother: not owner-side, but one hire can't carry 129", v("H-brother", "HA3") == ["pass"] and not res["H-brother"]["tools"]["129"]["pass"])
    expect("hire only to unlock: fails arm's length and substance, and is disregarded",
           v("H-unlock", "HA2") == ["fail"] and not res["H-unlock"]["tools"]["129"]["pass"])
    # the board never changes attribution: give the parent a perfect board
    c = json.loads(json.dumps(next(x for x in inputs["cases"] if x["id"] == "H-family")))
    c["hires"][0]["board"] = json.loads(json.dumps(next(x for x in inputs["cases"] if x["id"] == "H-unrelated")["hires"][0]["board"]))
    r = run_case(c, inputs["rates"])
    expect("a perfect board record doesn't make a parent unattributed",
           [x["verdict"] for x in r["checks"] if x["id"] == "HA4"] == ["pass"] and
           [x["verdict"] for x in r["checks"] if x["id"] == "HA3"] == ["fail"])
    # the owner approving their own hire is not independent
    c = json.loads(json.dumps(next(x for x in inputs["cases"] if x["id"] == "H-unrelated")))
    c["hires"][0]["board"]["approvers"] = [{"relation": "self", "stake": True}]
    expect("the owner alone approving is not independent",
           [x["verdict"] for x in run_case(c, inputs["rates"])["checks"] if x["id"] == "HA4"][0] == "fail")
    # approval after the start fails
    c = json.loads(json.dumps(next(x for x in inputs["cases"] if x["id"] == "H-unrelated")))
    c["hires"][0]["board"]["approved_on"] = "2027-12-31"
    expect("approval dated after the start fails",
           [x["verdict"] for x in run_case(c, inputs["rates"])["checks"] if x["id"] == "HA4"][0] == "fail")
    # 129(c): care paid to a related individual fails 129
    c = json.loads(json.dumps(next(x for x in inputs["cases"] if x["id"] == "H-unrelated")))
    c["care_paid_to_related_individual"] = True
    expect("care paid to the employee's dependent fails 129 (129(c))", not run_case(c, inputs["rates"])["tools"]["129"]["pass"])
    # household staff in the owner's home are personal (262), whatever the board says
    expect("household staff fail arm's length (262; Schedule H)", set(v("H-household", "HA1")) == {"fail"})
    # AI agents never move an owner test: drop them and every tool verdict is the same
    c = json.loads(json.dumps(next(x for x in inputs["cases"] if x["id"] == "H-unrelated")))
    with_ai = {t: x["pass"] for t, x in run_case(c, inputs["rates"])["tools"].items()}
    c.pop("ai", None)
    without_ai = {t: x["pass"] for t, x in run_case(c, inputs["rates"])["tools"].items()}
    expect("AI agents change no owner test", with_ai == without_ai and v("H-unrelated", "AI0") == ["pass"])
    c = json.loads(json.dumps(next(x for x in inputs["cases"] if x["id"] == "H-unrelated")))
    c["ai"]["agents"] = 1000
    expect("a thousand agents still don't unlock 127", not run_case(c, inputs["rates"])["tools"]["127"]["pass"])
    expect("family office: FO1 to FO4 pass, FO5 stays amber", v("H-familyoffice", "FO5") == ["amber"] and
           all(v("H-familyoffice", f"FO{i}") == ["pass"] for i in range(1, 5)))
    try:
        family_office_checks({"salaried_staff": True}); closed = False
    except KeyError:
        closed = True
    expect("family office checks fail closed on missing facts", closed)
    expect("own portfolio only (Higgins) fails FO1",
           family_office_checks({"clients_mostly_non_owners": False, "paid_for_services_not_capital": True, "salaried_staff": True,
                                 "services_beyond_an_investor": True, "bona_fide_under_scrutiny": True})[0][1] == "fail")
    print(f"\n{bad} failure(s)")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="?", default=str(DEFAULT))
    ap.add_argument("--json")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    results = run(json.loads(Path(a.inputs).read_text()))
    print(summarize(results))
    if a.json:
        Path(a.json).write_text(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
