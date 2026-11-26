#!/usr/bin/env python3
"""Declared plans: say in advance what you will do, do it, prove it, reconcile.

One pattern, several instances in the tax code. An arrangement is declared
before money moves. Each payment is then held to what was declared, with
records, and reconciled against it. If the arrangement fails, the money is
taxed (or penalized) as something else.

  accountable_plan            Treas. Reg. 1.62-2 (IRC 62(c)): the management
                              company reimburses the founder, its employee.
                              Fail: reimbursements become wages.
  foundation_reimbursement    IRC 4941(d)(2)(E), Treas. Reg. 53.4941(d)-3(c)(1):
                              the Foundation reimburses a foundation manager.
                              Fail: tested as self-dealing.
  expenditure_responsibility  IRC 4945(d)(4)(B), 4945(h): a grant to an
                              organization that is not a public charity.
                              Fail: a taxable expenditure.
  exemption_narrative         IRC 508(a), Reg. 1.508-1(a)(2)(i): the activities
                              described in Form 1023. Consequence NOT TRACED.

  python3 declared_plan.py                 run every plan in declared-plan-synthetic.json
  python3 declared_plan.py --json out.json also write the results
  python3 declared_plan.py --as-of 2026-04-02   judge the year as it stood that day
  python3 declared_plan.py --selftest      the check's own cases

Verdicts: pass, fail, amber (a fact is unknown, or the text read does not
settle it: a counsel question). A missing fact field is an error, never a pass.

Sources read 2026-11-26: Treas. Reg. 1.62-2 at
https://www.law.cornell.edu/cfr/text/26/1.62-2 (LII reproduction, not the
official eCFR; quotes in DECLARED-PLAN.md). Others are the quotes already in
rehearsal/01-instrument-register.md (B4, B5, D2, D11, 280A) and
packet/research/Q35.md (4945). SYNTHETIC. Design and education, not legal or
tax advice.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT = HERE / "declared-plan-synthetic.json"

# 1.62-2(g)(2)(i), the fixed date method: advance within 30 days, substantiate
# within 60 days, return excess within 120 days.
SAFE_ADVANCE_DAYS = 30
SAFE_SUBSTANTIATE_DAYS = 60
SAFE_RETURN_DAYS = 120

# ASSUMPTION (counsel queue Q38): 1.62-2(k) gives no number for a "pattern of
# abuse". The rehearsal calls it a pattern when half or more of the year's
# payments fail a test. Most defensible reading, not the most favorable: a
# lower share would be safer for the payor, so this threshold is a flag, never
# a safe harbor.
ABUSE_SHARE = 0.5

LINE_EVIDENCE = {
    # 274(d): time, place, business purpose (register B5)
    "mileage": {"log_time_place_purpose"},
    # 280A(c)(1): exclusive, regular use; a worksheet of the space and the bills
    "home_office": {"square_footage_worksheet", "utility_bills"},
    # business share of a mixed-use bill needs a use log (register domain D1)
    "phone": {"bill", "business_use_log"},
}


def _d(s):
    return date.fromisoformat(s) if s else None


def _v(val):
    return "pass" if val is True else ("fail" if val is False else "amber")


def _need(facts: dict, keys: list, plan_id: str):
    missing = [k for k in keys if k not in facts]
    if missing:
        raise KeyError(f"{plan_id}: missing fact field(s) {missing} (fail closed)")


# ------------------------------------------------------------ accountable plan

def terms_in_force(plan: dict, on) -> dict:
    """Terms that govern a payment made on `on`: the declared terms plus every
    amendment adopted on or before that day. An amendment counts from the day
    it was adopted, whatever effective date it claims, so a later amendment can
    never reach back to cover a payment already made (ASSUMPTION, Q44)."""
    t = dict(plan["terms"])
    for a in sorted(plan.get("amendments", []), key=lambda a: a["adopted_on"]):
        if on is None or _d(a["adopted_on"]) <= on:
            t.update(a["terms"])
    return t


def deadlines(ev: dict, t: dict) -> dict:
    """The dates each open item must be closed by, fixed date method (g)(2)(i)."""
    inc = _d(ev["incurred"])
    out = {"substantiate_by": inc + timedelta(days=min(t["substantiation_days"], SAFE_SUBSTANTIATE_DAYS))}
    if max(0.0, ev.get("advance", 0) - ev["amount"]) > 0:
        out["return_by"] = inc + timedelta(days=min(t["return_excess_days"], SAFE_RETURN_DAYS))
    return out


def event_tests(ev: dict, plan: dict, as_of=None) -> dict:
    """Each test is True (met), False (broken) or None (open, deadline not yet
    passed on `as_of`). An open item is not a failure until its deadline passes."""
    f = plan["facts"]
    t = terms_in_force(plan, _d(ev["paid"]))
    dl = deadlines(ev, t)
    out = {}
    # AP1 business connection, 1.62-2(d)(1)
    ok = bool(ev.get("business_purpose")) and ev["line"] in t["covered_lines"]
    if ev["line"] == "home_office":
        ok = ok and f["home_office_for_convenience_of_employer"] is True and f["home_rented_to_employer"] is False
    out["AP1"] = ok
    # AP2 substantiation, 1.62-2(e)(1), safe harbor (g)(2)(i)
    sub = _d(ev.get("substantiated"))
    has_ev = LINE_EVIDENCE.get(ev["line"], set()) <= set(ev.get("evidence", []))
    if sub and (as_of is None or sub <= as_of):
        out["AP2"] = sub <= dl["substantiate_by"] and has_ev
    else:
        out["AP2"] = None if (as_of is not None and as_of <= dl["substantiate_by"]) else False
    # AP3 advance timing, (g)(2)(i)
    if ev.get("advance", 0) > 0:
        out["AP3"] = (_d(ev["incurred"]) - _d(ev["paid"])).days <= min(t["advance_max_days_before_expense"], SAFE_ADVANCE_DAYS)
    else:
        out["AP3"] = True
    # AP4 return of excess, 1.62-2(f)(1), safe harbor (g)(2)(i)
    if "return_by" in dl:
        ret = _d(ev.get("excess_returned"))
        if ret and (as_of is None or ret <= as_of):
            out["AP4"] = ret <= dl["return_by"]
        else:
            out["AP4"] = None if (as_of is not None and as_of <= dl["return_by"]) else False
    else:
        out["AP4"] = True
    return out


def breaches(ev: dict, plan: dict) -> list:
    """(date, test) for each way this payment broke the plan, dated the day the
    break became true: the payment day for AP1/AP3, the day after a missed
    deadline for AP2/AP4."""
    r = event_tests(ev, plan)
    t = terms_in_force(plan, _d(ev["paid"]))
    dl = deadlines(ev, t)
    paid = _d(ev["paid"])
    out = []
    for k in ("AP1", "AP3"):
        if r[k] is False:
            out.append((paid, k))
    if r["AP2"] is False:
        sub = _d(ev.get("substantiated"))
        late = dl["substantiate_by"] + timedelta(days=1)
        out.append((max(paid, late) if (sub is None or sub > dl["substantiate_by"]) else max(paid, sub), "AP2"))
    if r["AP4"] is False:
        out.append((max(paid, dl["return_by"] + timedelta(days=1)), "AP4"))
    return out


def run_accountable(plan: dict, rates: dict, as_of=None) -> dict:
    _need(plan["facts"], ["home_office_for_convenience_of_employer", "home_rented_to_employer",
                          "founder_is_employee_not_disregarded_owner"], plan["id"])
    as_of = as_of or _d(plan.get("as_of"))
    t = plan["terms"]
    events = [e for e in plan["events"] if as_of is None or _d(e["paid"]) <= as_of]
    checks = []
    first_paid = min((_d(e["paid"]) for e in events), default=None)
    declared = _d(plan.get("declared_on"))
    # DP0 declared before money moves. ASSUMPTION (Q39): the regulation tests an
    # "arrangement"; it does not say in words that it must be written and dated
    # first. The rehearsal requires a dated written plan as the evidence of one.
    checks.append(("DP0", "pass" if declared and (first_paid is None or declared <= first_paid) else "fail",
                   "Plan declared (written, dated) before the first payment under it", "ASSUMPTION, Q39"))
    # DP1 the declared terms sit inside the fixed date safe harbor
    inside = (t["substantiation_days"] <= SAFE_SUBSTANTIATE_DAYS and t["return_excess_days"] <= SAFE_RETURN_DAYS
              and t["advance_max_days_before_expense"] <= SAFE_ADVANCE_DAYS)
    checks.append(("DP1", "pass" if inside else "amber",
                   "Declared terms are inside the 30/60/120-day fixed date method (longer can still be reasonable on the facts)",
                   "Reg. 1.62-2(g)(1), (g)(2)(i)"))
    # DP3 no amendment reaches back to cover a payment already made. ASSUMPTION
    # (Q44): the text read says nothing about amendments; the rehearsal holds
    # each payment to the terms in force on the day it was paid.
    retro = []
    for am in plan.get("amendments", []):
        eff, adopted = _d(am.get("effective_on") or am["adopted_on"]), _d(am["adopted_on"])
        retro += [e["id"] for e in events if eff <= _d(e["paid"]) < adopted]
    checks.append(("DP3", "fail" if retro else "pass",
                   "No amendment adopted after a payment claims to cover it; each payment is held to the terms in force when paid"
                   + (f" (reached back to: {', '.join(retro)})" if retro else ""), "ASSUMPTION, Q44"))
    # AP0 the payee is an employee (register B4: a disregarded owner can't use one)
    checks.append(("AP0", _v(plan["facts"]["founder_is_employee_not_disregarded_owner"]),
                   "The person reimbursed is an employee of the payor", "Reg. 1.62-2(d)(1); register B4"))
    per = {e["id"]: event_tests(e, plan, as_of) for e in events}
    labels = {
        "AP1": ("Every payment is for a business expense of the employee's job (home office also needs the employer's convenience and no rental to the employer)", "Reg. 1.62-2(d)(1); IRC 280A(c)(1), (c)(6)"),
        "AP2": ("Every expense substantiated to the payor within the declared period, with the records the line needs", "Reg. 1.62-2(e)(1), (g)(2)(i); IRC 274(d)"),
        "AP3": ("Every advance paid no more than 30 days before the expense", "Reg. 1.62-2(g)(2)(i)"),
        "AP4": ("Every amount above the substantiated expense returned within the declared period", "Reg. 1.62-2(f)(1), (g)(2)(i)"),
    }
    for k, (lab, cite) in labels.items():
        bad = [i for i, r in per.items() if r[k] is False]
        open_ = [i for i, r in per.items() if r[k] is None]
        note = (f" (fails: {', '.join(bad)})" if bad else "") + (f" (open, not yet due: {', '.join(open_)})" if open_ else "")
        checks.append((k, "fail" if bad else "pass", lab + note, cite))
    # DP2 the step invariant: on every day of the year so far, nothing is past
    # its deadline. Open items inside their window are fine; the invariant is
    # "nothing overdue", not "everything closed". Read from (g)(2)(i).
    dated = sorted(br for e in events for br in breaches(e, plan) if as_of is None or br[0] <= as_of)
    first = dated[0] if dated else None
    checks.append(("DP2", "fail" if first else "pass",
                   "On every day so far, nothing was past its deadline (open items still inside their window are allowed)"
                   + (f" (first broken {first[0].isoformat()}, {first[1]})" if first else ""),
                   "Reg. 1.62-2(g)(2)(i)"))
    failing = [i for i, r in per.items() if any(v is False for v in r.values())]
    share = len(failing) / len(events) if events else 0.0
    abuse = share >= ABUSE_SHARE
    checks.append(("AP5", "fail" if abuse else "pass",
                   f"No pattern of abuse: {len(failing)} of {len(events)} payments fail a test (threshold {ABUSE_SHARE:.0%}, ASSUMPTION)",
                   "Reg. 1.62-2(k); ASSUMPTION, Q38"))
    # DP4 early drift: a pattern under (k) is a plan-level failure, so the first
    # broken payment is flagged as risk to the whole arrangement, dated, with
    # the day the running share first reached the threshold if it did.
    first_break = sorted(min(br[0] for br in bs) for bs in (
        [br for br in breaches(e, plan) if as_of is None or br[0] <= as_of] for e in events) if bs)
    crossed = None
    for n, day in enumerate(first_break, 1):
        made = [e for e in events if _d(e["paid"]) <= day]
        if made and n / len(made) >= ABUSE_SHARE:
            crossed = day
            break
    if first:
        lab = (f"Drift flagged at plan level from {first[0].isoformat()}: {len(failing)} of {len(events)} payments broken"
               + (f"; share reached {ABUSE_SHARE:.0%} on {crossed.isoformat()}" if crossed else
                  f"; {max(0, math.ceil(ABUSE_SHARE * len(events)) - len(failing))} more broken payment(s) reach the threshold"))
    else:
        lab = "No drift: no payment has broken the plan"
    checks.append(("DP4", "amber" if first else "pass", lab, "Reg. 1.62-2(k); threshold ASSUMPTION, Q38"))
    # Reconcile: what is wages. Arrangement-level failure (k, or the employee
    # test) makes every payment wages (1.62-2(c)(3)(i), (c)(5), (k)). A single
    # failed payment under a plan that otherwise holds is counted as wages for
    # that payment only: ASSUMPTION, Q40 (the per-payment rule was not read).
    paid_total = sum(max(e["amount"], e.get("advance", 0)) for e in events)
    whole_fails = abuse or plan["facts"]["founder_is_employee_not_disregarded_owner"] is not True
    if whole_fails:
        wages = paid_total
        basis = "whole arrangement nonaccountable (Reg. 1.62-2(c)(3)(i), (c)(5), (k))"
    else:
        wages = 0.0
        for e in events:
            r = per[e["id"]]
            if r["AP1"] is False or r["AP2"] is False:
                wages += max(e["amount"], e.get("advance", 0))
            elif r["AP4"] is False:
                wages += max(0.0, e.get("advance", 0) - e["amount"])
        basis = "only the failed payments (ASSUMPTION, Q40)" if wages else "nothing; all payments accountable"
    emp = rates["employee_income_tax_marginal"] + rates["state_income_tax"] + rates["employee_fica"]
    cost = round(wages * emp + wages * rates["employer_fica"], 2)
    return {"id": plan["id"], "instance": plan["instance"], "label": plan["label"],
            "checks": [{"id": c[0], "verdict": c[1], "label": c[2], "cite": c[3]} for c in checks],
            "reconcile": {"paid_total": paid_total, "treated_as_wages": round(wages, 2), "basis": basis,
                          "added_tax_cost_placeholder_rates": cost}}


# ------------------------------------------------------- the same shape again

def run_foundation_reimbursement(plan: dict) -> dict:
    keys = ["expense_tied_to_named_program", "amount_at_or_below_documented_benchmark",
            "approved_without_payee_vote", "substantiated_under_declared_policy"]
    _need(plan["facts"], keys, plan["id"])
    f = plan["facts"]
    checks = [
        ("FR1", _v(f["expense_tied_to_named_program"]), "Reimbursed expense is reasonable and necessary to an exempt purpose (a named program)", "IRC 4941(d)(2)(E); Reg. 53.4941(d)-3(c)(1)"),
        ("FR2", _v(f["amount_at_or_below_documented_benchmark"]), "Amount is not excessive, against a documented benchmark", "Reg. 53.4941(d)-3(c)(1)"),
        ("FR3", _v(f["approved_without_payee_vote"]), "Approved by people other than the payee", "ASSUMPTION, Q41 (governance control, not in the regulation's words)"),
        ("FR4", _v(f["substantiated_under_declared_policy"]), "Substantiated under the Foundation's declared expense policy", "ASSUMPTION, Q41 (the regulation does not require an accountable plan)"),
    ]
    return _pack(plan, checks, "If FR1 or FR2 fails, the payment is tested as self-dealing (IRC 4941(d)(1)(E)).")


def run_expenditure_responsibility(plan: dict) -> dict:
    keys = ["grantee_is_public_charity_or_exempt_operating", "written_grant_agreement_states_purpose",
            "spent_solely_for_declared_purpose", "full_reports_obtained_from_grantee", "reported_to_irs_on_990pf"]
    _need(plan["facts"], keys, plan["id"])
    f = plan["facts"]
    if f["grantee_is_public_charity_or_exempt_operating"] is True:
        checks = [("ER0", "pass", "Grantee is a public charity or exempt operating foundation: expenditure responsibility not required", "IRC 4945(d)(4)")]
    else:
        checks = [
            ("ER1", _v(f["written_grant_agreement_states_purpose"]), "Purpose declared in writing before the grant is paid", "ASSUMPTION, Q42 (Reg. 53.4945-5 not traced)"),
            ("ER2", _v(f["spent_solely_for_declared_purpose"]), "Grant spent solely for the purpose for which made", "IRC 4945(h)(1)"),
            ("ER3", _v(f["full_reports_obtained_from_grantee"]), "Full and complete reports obtained from the grantee", "IRC 4945(h)(2)"),
            ("ER4", _v(f["reported_to_irs_on_990pf"]), "Full and detailed reports made to the Secretary", "IRC 4945(h)(3)"),
        ]
    return _pack(plan, checks, "If ER2 to ER4 fail, the grant is a taxable expenditure (IRC 4945(d)(4)(B)).")


def run_exemption_narrative(plan: dict) -> dict:
    keys = ["form_1023_filed_with_narrative", "actual_activities_within_narrative", "material_change_reported_on_990pf"]
    _need(plan["facts"], keys, plan["id"])
    f = plan["facts"]
    checks = [
        ("EX1", _v(f["form_1023_filed_with_narrative"]), "Form 1023 filed within 15 months, with the activities described", "IRC 508(a); Reg. 1.508-1(a)(2)(i)"),
        ("EX2", "amber" if f["actual_activities_within_narrative"] is True else _v(f["actual_activities_within_narrative"]),
         "Activities stay inside the narrative given in Form 1023", "NOT TRACED, Q43"),
        ("EX3", "amber" if f["material_change_reported_on_990pf"] is True else _v(f["material_change_reported_on_990pf"]),
         "Any material change from the narrative is reported", "NOT TRACED, Q43"),
    ]
    return _pack(plan, checks, "Consequence of drifting from the narrative is NOT TRACED (Q43); EX2 and EX3 stay amber until it is.")


def _pack(plan, checks, consequence):
    return {"id": plan["id"], "instance": plan["instance"], "label": plan["label"],
            "checks": [{"id": c[0], "verdict": c[1], "label": c[2], "cite": c[3]} for c in checks],
            "reconcile": {"consequence": consequence}}


RUNNERS = {
    "foundation_reimbursement": run_foundation_reimbursement,
    "expenditure_responsibility": run_expenditure_responsibility,
    "exemption_narrative": run_exemption_narrative,
}


def run(inputs: dict, as_of=None) -> list:
    out = []
    for p in inputs["plans"]:
        if p["instance"] == "accountable_plan":
            out.append(run_accountable(p, inputs["rates"], as_of))
        else:
            out.append(RUNNERS[p["instance"]](p))
    return out


def summarize(results: list) -> str:
    lines = ["SYNTHETIC declared-plan run. Not legal or tax advice.", ""]
    tot = {"pass": 0, "amber": 0, "fail": 0}
    for r in results:
        c = [x["verdict"] for x in r["checks"]]
        for v in c:
            tot[v] += 1
        lines.append(f"== {r['id']} ({r['instance']}): {c.count('pass')} pass / {c.count('amber')} amber / {c.count('fail')} fail")
        for x in r["checks"]:
            lines.append(f"   {x['verdict']:5}  {x['id']:4} {x['label']}  [{x['cite']}]")
        rec = r["reconcile"]
        if "treated_as_wages" in rec:
            lines.append(f"   reconcile: paid {rec['paid_total']:,.0f}; treated as wages {rec['treated_as_wages']:,.0f} ({rec['basis']}); "
                         f"added tax at placeholder rates {rec['added_tax_cost_placeholder_rates']:,.0f}")
        else:
            lines.append(f"   reconcile: {rec['consequence']}")
    lines.append("")
    lines.append(f"Checks: {sum(tot.values())} ({tot['pass']} pass, {tot['amber']} amber, {tot['fail']} fail)")
    return "\n".join(lines)


def selftest() -> int:
    bad = 0

    def expect(name, cond):
        nonlocal bad
        print(("ok   " if cond else "FAIL ") + name)
        bad += 0 if cond else 1

    inputs = json.loads(DEFAULT.read_text())
    res = {r["id"]: r for r in run(inputs)}
    v = lambda pid, cid: next(c["verdict"] for c in res[pid]["checks"] if c["id"] == cid)
    expect("clean plan: every accountable-plan check passes", all(c["verdict"] == "pass" for c in res["AP-mgmt"]["checks"]))
    expect("clean plan: nothing treated as wages", res["AP-mgmt"]["reconcile"]["treated_as_wages"] == 0)
    expect("late receipt fails substantiation (60-day safe harbor)", v("AP-mgmt-late", "AP2") == "fail")
    expect("unreturned excess fails return-of-excess", v("AP-mgmt-late", "AP4") == "fail")
    expect("two of three failing is a pattern at the 50 percent threshold", v("AP-mgmt-late", "AP5") == "fail")
    expect("abuse case: every payment becomes wages (1.62-2(k))",
           res["AP-mgmt-abuse"]["reconcile"]["treated_as_wages"] == res["AP-mgmt-abuse"]["reconcile"]["paid_total"])
    # one late receipt among four: per-payment wages only, no pattern
    p = json.loads(json.dumps(next(x for x in inputs["plans"] if x["id"] == "AP-mgmt")))
    p["events"][0]["substantiated"] = "2026-05-01"
    r = run_accountable(p, inputs["rates"])
    expect("one late receipt of four: no pattern", next(c["verdict"] for c in r["checks"] if c["id"] == "AP5") == "pass")
    expect("one late receipt of four: only that payment is wages", r["reconcile"]["treated_as_wages"] == 150)
    # home office rented to the employer closes the door (280A(c)(6))
    p2 = json.loads(json.dumps(next(x for x in inputs["plans"] if x["id"] == "AP-mgmt")))
    p2["facts"]["home_rented_to_employer"] = True
    r2 = run_accountable(p2, inputs["rates"])
    expect("home rented to employer fails business connection", next(c["verdict"] for c in r2["checks"] if c["id"] == "AP1") == "fail")
    # plan dated after the first payment fails DP0
    p3 = json.loads(json.dumps(next(x for x in inputs["plans"] if x["id"] == "AP-mgmt")))
    p3["declared_on"] = "2026-03-15"
    expect("plan declared after money moved fails DP0",
           next(c["verdict"] for c in run_accountable(p3, inputs["rates"])["checks"] if c["id"] == "DP0") == "fail")
    # missing fact is an error, never a pass
    p4 = json.loads(json.dumps(next(x for x in inputs["plans"] if x["id"] == "FR-trustee")))
    del p4["facts"]["approved_without_payee_vote"]
    try:
        run_foundation_reimbursement(p4)
        expect("missing fact raises", False)
    except KeyError:
        expect("missing fact raises", True)
    expect("unknown 990-PF report stays amber", v("ER-grant", "ER4") == "amber")
    expect("1023 drift check stays amber until traced", v("EX-1023", "EX2") == "amber")
    # role names don't decide verdicts
    p5 = json.loads(json.dumps(next(x for x in inputs["plans"] if x["id"] == "AP-mgmt")))
    p5["payor_role"], p5["payee_role"] = "x", "y"
    expect("renaming roles changes no verdict",
           [c["verdict"] for c in run_accountable(p5, inputs["rates"])["checks"]] == [c["verdict"] for c in res["AP-mgmt"]["checks"]])
    # the step invariant: open items inside their window are not failures
    late = next(x for x in inputs["plans"] if x["id"] == "AP-mgmt-late")
    mid = run_accountable(late, inputs["rates"], as_of=date(2026, 3, 15))
    mv = lambda r, cid: next(c["verdict"] for c in r["checks"] if c["id"] == cid)
    expect("mid-March: f1 receipt still inside 60 days, nothing overdue (DP2 pass)", mv(mid, "DP2") == "pass" and mv(mid, "AP2") == "pass")
    after = run_accountable(late, inputs["rates"], as_of=date(2026, 4, 2))
    expect("April 2: f1 receipt now overdue, DP2 fails that day", mv(after, "DP2") == "fail" and "2026-04-02" in
           next(c["label"] for c in after["checks"] if c["id"] == "DP2"))
    expect("April 2: one break of three is drift (amber), not yet a pattern", mv(after, "DP4") == "amber" and mv(after, "AP5") == "pass")
    # amendments: an amendment can't reach back to cover a payment already made
    p6 = json.loads(json.dumps(late))
    p6["amendments"] = [{"adopted_on": "2026-05-01", "effective_on": "2026-01-01", "terms": {"substantiation_days": 120}}]
    r6 = run_accountable(p6, inputs["rates"])
    expect("amendment backdated to cover earlier payments fails DP3", mv(r6, "DP3") == "fail")
    expect("backdated amendment doesn't rescue the late receipt", mv(r6, "AP2") == "fail")
    p7 = json.loads(json.dumps(late))
    p7["amendments"] = [{"adopted_on": "2026-01-15", "terms": {"substantiation_days": 120}}]
    r7 = run_accountable(p7, inputs["rates"])
    expect("amendment adopted before the payment governs it, but the safe harbor still caps it at 60 days",
           mv(r7, "DP3") == "pass" and mv(r7, "AP2") == "fail" and mv(r7, "DP1") == "pass")
    print(f"\n{bad} failure(s)")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="?", default=str(DEFAULT))
    ap.add_argument("--json")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--as-of", help="YYYY-MM-DD: judge the accountable plans as they stood that day")
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
