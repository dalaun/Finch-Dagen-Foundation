#!/usr/bin/env python3
"""Grantor trust check: does the Family Trust stay a separate (non-grantor) taxpayer?

Reads a trust's modeled terms and tests them against the grantor trust rules,
IRC 671-679, one rule at a time. Any rule that fails makes the founder (the
grantor) the owner for income tax, so the trust's income is taxed to him and
the income-splitting in the rehearsal disappears. Each result names the term
that caused it.

  python3 grantor_check.py                 every stack version and every design route
  python3 grantor_check.py --routes        the design routes only (grantor-routes.json)
  python3 grantor_check.py --selftest      the check's own cases

Verdicts per rule: pass, fail, or amber (the statute's text does not settle it;
a question for counsel). A missing term is an error, never a pass (fail closed).

Assumption, stated once: the founder is the grantor, because his own assets
fund the trust. "spouse" is treated as the founder (IRC 672(e)(1)).

Sources read 2026-11-23 on law.cornell.edu: IRC 672, 673, 674, 675, 676, 677,
678, 679, 7701(a)(30)(E); Treas. Reg. 1.674(b)-1, 1.674(c)-1, 1.674(d)-1,
1.674(d)-2. Illinois: 760 ILCS 3/808 (directed trusts). SYNTHETIC. Not legal
or tax advice.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Who can hold a power. The founder and his spouse count as the grantor (672(e)).
GRANTOR_SIDE = {"founder", "spouse"}
# 672(c): spouse living with him, parents, issue, siblings, his employees,
# his controlled corporation or its employees. Presumed subservient for 674 and 675.
RELATED = {"related_subordinate"}
INDEPENDENT = {"independent"}          # nonadverse, not related or subordinate
ADVERSE = {"adverse"}                  # 672(a): substantial beneficial interest hurt by the power
# 760 ILCS 3/808(c): an independent distribution trust advisor who is not a trustee.
ADVISOR = {"independent_distribution_advisor"}
HOLDERS = GRANTOR_SIDE | RELATED | INDEPENDENT | ADVERSE | ADVISOR

KINDS = {"discretionary", "mandatory_fixed_shares", "charity_only", "withhold_temporarily",
         "withhold_during_disability_or_under_21"}
STANDARDS = {"none", "reasonably_definite", "reasonably_definite_external"}
REMOVAL = {"none", "only_to_appoint_another_independent", "on_limited_conditions", "unrestricted"}

REQUIRED = {
    "domestic": ["us_court_primary_supervision", "us_persons_control_substantial_decisions"],
    "revocation": ["revocable", "revoke_power_holders"],
    "reversion_value_share_at_inception": None,
    "benefit_to_grantor": ["income_may_go_to_founder_or_spouse", "income_may_pay_premiums_on_founder_or_spouse"],
    "admin": ["deal_for_less_than_adequate_consideration", "founder_may_borrow_without_adequate_interest_or_security",
              "founder_loan_unrepaid", "vote_closely_held_stock_nonfiduciary",
              "direct_investments_in_closely_held_stock_nonfiduciary", "swap_power_nonfiduciary"],
    "trustees": None,
    "powers": None,
    "anyone_may_add_beneficiaries": None,
    "founder_power_to_remove_replace_trustee": None,
    "beneficiary_sole_power_to_vest_in_self": None,
}


class MissingTerm(Exception):
    pass


def need(terms: dict, path: str):
    cur = terms
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise MissingTerm(path)
        cur = cur[part]
    if cur is None:
        raise MissingTerm(path)
    return cur


def validate(terms: dict) -> None:
    for key, subs in REQUIRED.items():
        need(terms, key)
        for s in subs or []:
            need(terms, f"{key}.{s}")
    for i, p in enumerate(need(terms, "powers")):
        for f in ("name", "over", "kind", "holders", "standard", "needs_adverse_consent"):
            if f not in p or p[f] is None:
                raise MissingTerm(f"powers[{i}].{f}")
        if p["kind"] not in KINDS:
            raise MissingTerm(f"powers[{i}].kind: unknown {p['kind']!r}")
        if p["standard"] not in STANDARDS:
            raise MissingTerm(f"powers[{i}].standard: unknown {p['standard']!r}")
        if p["over"] not in ("income", "corpus"):
            raise MissingTerm(f"powers[{i}].over: unknown {p['over']!r}")
        bad = [h for h in p["holders"] if h not in HOLDERS]
        if bad or not p["holders"]:
            raise MissingTerm(f"powers[{i}].holders: unknown or empty {bad}")
    if terms["founder_power_to_remove_replace_trustee"] not in REMOVAL:
        raise MissingTerm("founder_power_to_remove_replace_trustee: unknown value")
    bad = [t for t in terms["trustees"] if t not in HOLDERS - ADVISOR]
    if bad or not terms["trustees"]:
        raise MissingTerm(f"trustees: unknown or empty {bad}")


def r(rule, status, why, term):
    return {"rule": rule, "status": status, "why": why, "term": term}


def check_power(p: dict, terms: dict) -> dict:
    """IRC 674 for one power over beneficial enjoyment."""
    name = f"powers.{p['name']}"
    holders = set(p["holders"])
    add_ben = terms["anyone_may_add_beneficiaries"]
    removal = terms["founder_power_to_remove_replace_trustee"]
    trustees = terms["trustees"]
    # 674(a) reaches a power held by the grantor or a nonadverse party without an adverse party's consent.
    if p["needs_adverse_consent"] or holders <= ADVERSE:
        return r("674(a)", "pass", "the power needs an adverse party's consent", name)
    if p["kind"] == "mandatory_fixed_shares":
        return r("674(a)", "pass", "no discretion: the instrument fixes who gets what, so no one holds a power of disposition", name)
    if p["kind"] == "charity_only":
        return r("674(b)(4)", "pass", "allocation only among charitable beneficiaries; the amounts are irrevocably payable for 170(c) purposes", name)
    # Reg. 1.674(d)-2(b): a power to add beneficiaries kills (b)(5), (b)(6), (b)(7), (c) and (d).
    if add_ben:
        return r("674(a); Reg. 1.674(d)-2(b)", "fail",
                 "someone can add beneficiaries, so no exception in 674(b)(5)-(7), (c) or (d) is available", "anyone_may_add_beneficiaries")
    if p["kind"] == "withhold_temporarily" and p["over"] == "income":
        return r("674(b)(6)", "pass", "income may only be withheld for the same beneficiary and must reach that beneficiary in the end", name)
    if p["kind"] == "withhold_during_disability_or_under_21" and p["over"] == "income":
        return r("674(b)(7)", "pass", "income may only be withheld while a beneficiary is under 21 or disabled", name)
    if p["over"] == "corpus" and p["standard"] in ("reasonably_definite", "reasonably_definite_external"):
        return r("674(b)(5)(A)", "pass", "principal goes out only under a reasonably definite standard (health, education, support, maintenance), whoever holds it", name)
    # From here the power is discretionary over income, or over principal with no standard.
    removal_ok = removal in ("none", "only_to_appoint_another_independent", "on_limited_conditions")
    holder_trustees = holders <= set(trustees) | ADVISOR
    if holders & GRANTOR_SIDE:
        if p["over"] == "income" and p["standard"] == "reasonably_definite_external":
            return r("674(d)", "fail", "674(d) is closed to a power the founder or his spouse holds, even with a standard", name)
        return r("674(a)", "fail", "the founder (or his spouse) decides who benefits, with no exception that fits", name)
    if not removal_ok:
        return r("674(c)/(d); Reg. 1.674(d)-2(a)", "fail",
                 "the founder can fire the independent holder and appoint anyone, himself included", "founder_power_to_remove_replace_trustee")
    if holders & ADVISOR:
        return r("674(c)", "amber",
                 "674(c) speaks of trustees; whether an Illinois distribution trust advisor (760 ILCS 3/808(c), a fiduciary under 808(e)) counts is for counsel. Naming the advisor a co-trustee removes the doubt", name)
    if not holder_trustees:
        return r("674(a)", "fail", "the holder is not a trustee, so 674(c) and (d) do not apply", name)
    related = sum(1 for h in p["holders"] if h in RELATED)   # count people, not kinds
    if related * 2 <= len(p["holders"]):
        return r("674(c)", "pass", "held only by trustees who are not the founder, no more than half related or subordinate", name)
    if p["over"] == "income" and p["standard"] == "reasonably_definite_external":
        return r("674(d)", "pass", "held by trustees other than the founder or his spouse, limited by a reasonably definite external standard", name)
    return r("674(c)", "fail", "more than half the holders are related or subordinate to the founder (presumed subservient, 672(c))", name)


def evaluate(terms: dict) -> dict:
    validate(terms)
    out = []
    d = terms["domestic"]
    if d["us_court_primary_supervision"] and d["us_persons_control_substantial_decisions"]:
        out.append(r("7701(a)(30)(E); 679", "pass", "a US court supervises it and US persons control every substantial decision, so it is a domestic trust", "domestic"))
    else:
        out.append(r("7701(a)(30)(E); 679", "fail", "a foreign trust: a US person who funds it is its owner while any beneficiary is a US person (679(a)(1))", "domestic"))
    rv = terms["revocation"]
    revokers = set(rv["revoke_power_holders"])
    if rv["revocable"] or (revokers - ADVERSE):
        out.append(r("676(a)", "fail", "the founder or a nonadverse party can take the property back", "revocation"))
    else:
        out.append(r("676(a)", "pass", "no one but an adverse party can revoke", "revocation"))
    rev = float(terms["reversion_value_share_at_inception"])
    out.append(r("673(a)", "fail" if rev > 0.05 else "pass",
                 f"reversion to the founder worth {rev:.0%} of the trust at inception (limit 5%)", "reversion_value_share_at_inception"))
    b = terms["benefit_to_grantor"]
    if b["income_may_go_to_founder_or_spouse"]:
        out.append(r("677(a)(1)-(2)", "fail", "income may be paid or saved for the founder or his spouse", "benefit_to_grantor.income_may_go_to_founder_or_spouse"))
    else:
        out.append(r("677(a)(1)-(2)", "pass", "no income can go to the founder or his spouse", "benefit_to_grantor.income_may_go_to_founder_or_spouse"))
    out.append(r("677(a)(3)", "fail" if b["income_may_pay_premiums_on_founder_or_spouse"] else "pass",
                 "income may pay life insurance on the founder or spouse" if b["income_may_pay_premiums_on_founder_or_spouse"]
                 else "income cannot pay life insurance on the founder or spouse", "benefit_to_grantor.income_may_pay_premiums_on_founder_or_spouse"))
    a = terms["admin"]
    for key, rule, why in [
        ("deal_for_less_than_adequate_consideration", "675(1)", "someone can buy or deal with trust property for less than it is worth"),
        ("founder_may_borrow_without_adequate_interest_or_security", "675(2)", "the founder can borrow trust money without adequate interest or security"),
        ("founder_loan_unrepaid", "675(3)", "the founder borrowed trust money and has not repaid it before the year began"),
        ("vote_closely_held_stock_nonfiduciary", "675(4)(A)", "someone votes a controlling block of stock in a nonfiduciary capacity"),
        ("direct_investments_in_closely_held_stock_nonfiduciary", "675(4)(B)", "someone directs or vetoes investments in a controlling block in a nonfiduciary capacity"),
        ("swap_power_nonfiduciary", "675(4)(C)", "someone can take trust property back by swapping in property of equal value (the planners' deliberate grantor-trust switch)"),
    ]:
        out.append(r(rule, "fail" if a[key] else "pass", why if a[key] else "not in the terms", f"admin.{key}"))
    for p in terms["powers"]:
        out.append(check_power(p, terms))
    if terms["beneficiary_sole_power_to_vest_in_self"]:
        out.append(r("678(a)", "fail", "a beneficiary can take income or principal alone, so that beneficiary is taxed as owner of it", "beneficiary_sole_power_to_vest_in_self"))
    else:
        out.append(r("678(a)", "pass", "no one other than the founder can take property for themselves alone", "beneficiary_sole_power_to_vest_in_self"))
    status = "grantor" if any(x["status"] == "fail" for x in out) else (
        "unsettled" if any(x["status"] == "amber" for x in out) else "non-grantor")
    return {"status": status, "rules": out}


def show(title: str, res: dict, verbose: bool = True) -> str:
    lines = [f"{title}: {res['status'].upper()}"]
    for x in res["rules"]:
        if verbose or x["status"] != "pass":
            lines.append(f"   {x['status']:<5} {x['rule']:<32} {x['why']}  [{x['term']}]")
    return "\n".join(lines)


def check_stack(stack: dict) -> tuple[list, int]:
    """Each version's declared grantor flag must match what its terms derive. A mismatch is an error."""
    lines, errors = [], 0
    for vid, v in stack["versions"].items():
        ft = v["family_trust"]
        if "terms" not in ft:
            raise MissingTerm(f"versions.{vid}.family_trust.terms")
        res = evaluate(ft["terms"])
        declared = "grantor" if ft["grantor"] else "non-grantor"
        mismatch = res["status"] == "grantor" and declared == "non-grantor" or (
            res["status"] == "non-grantor" and declared == "grantor")
        errors += mismatch
        tag = "MISMATCH: the engine taxes it as " + declared if mismatch else f"engine taxes it as {declared}"
        lines.append(show(f"family trust in {vid} ({tag})", res, verbose=False))
    return lines, errors


def base_terms() -> dict:
    """A clean non-grantor layout used by the selftest: independent trustee, fixed payout."""
    return {
        "domestic": {"us_court_primary_supervision": True, "us_persons_control_substantial_decisions": True},
        "revocation": {"revocable": False, "revoke_power_holders": []},
        "reversion_value_share_at_inception": 0.0,
        "benefit_to_grantor": {"income_may_go_to_founder_or_spouse": False, "income_may_pay_premiums_on_founder_or_spouse": False},
        "admin": {k: False for k in REQUIRED["admin"]},
        "trustees": ["independent"],
        "powers": [{"name": "income", "over": "income", "kind": "discretionary", "holders": ["independent"],
                    "standard": "none", "needs_adverse_consent": False}],
        "anyone_may_add_beneficiaries": False,
        "founder_power_to_remove_replace_trustee": "none",
        "beneficiary_sole_power_to_vest_in_self": False,
    }


def selftest() -> int:
    import copy
    fails = 0

    def ok(cond, msg):
        nonlocal fails
        print(("ok    " if cond else "FAIL  ") + msg)
        fails += not cond

    def with_(**changes):
        t = copy.deepcopy(base_terms())
        for path, val in changes.items():
            cur = t
            parts = path.split("__")
            for part in parts[:-1]:
                cur = cur[int(part)] if isinstance(cur, list) else cur[part]
            cur[int(parts[-1]) if isinstance(cur, list) else parts[-1]] = val
        return evaluate(t)

    def failing(res):
        return {x["rule"] for x in res["rules"] if x["status"] == "fail"}

    ok(evaluate(base_terms())["status"] == "non-grantor", "independent trustee with discretion over income: non-grantor (674(c))")
    res = with_(powers__0__holders=["founder"], trustees=["founder"])
    ok(res["status"] == "grantor" and "674(a)" in failing(res), "founder as trustee deciding who gets income: grantor (674(a))")
    res = with_(powers__0__holders=["spouse"], trustees=["spouse"])
    ok(res["status"] == "grantor", "his spouse holding the same power counts as him (672(e))")
    res = with_(powers__0__holders=["founder"], trustees=["founder"], powers__0__standard="reasonably_definite_external")
    ok("674(d)" in failing(res), "founder holding an income power under a definite standard: 674(d) closed to him")
    res = with_(powers__0__holders=["independent"], powers__0__standard="reasonably_definite_external")
    ok(res["status"] == "non-grantor", "independent trustee with an income standard: non-grantor")
    res = with_(powers__0__holders=["founder"], trustees=["founder"], powers__0__over="corpus", powers__0__standard="reasonably_definite")
    ok(res["status"] == "non-grantor", "founder distributing principal only for health, education, support: 674(b)(5)(A) holds whoever holds it")
    res = with_(powers__0__holders=["founder"], trustees=["founder"], powers__0__kind="mandatory_fixed_shares")
    ok(res["status"] == "non-grantor", "founder as trustee, income paid out in fixed shares: no power of disposition")
    res = with_(powers__0__holders=["founder"], trustees=["founder"], powers__0__kind="charity_only")
    ok(res["status"] == "non-grantor", "founder choosing only among charities: 674(b)(4)")
    res = with_(powers__0__holders=["related_subordinate", "related_subordinate", "independent"],
                trustees=["related_subordinate", "related_subordinate", "independent"])
    ok("674(c)" in failing(res), "two of three trustees related or subordinate: more than half, 674(c) fails")
    res = with_(powers__0__holders=["related_subordinate", "independent"], trustees=["related_subordinate", "independent"])
    ok(res["status"] == "non-grantor", "one of two trustees related: exactly half is allowed (674(c))")
    res = with_(founder_power_to_remove_replace_trustee="unrestricted")
    ok(res["status"] == "grantor", "founder can fire the independent trustee and appoint himself: grantor (Reg. 1.674(d)-2(a))")
    res = with_(founder_power_to_remove_replace_trustee="only_to_appoint_another_independent")
    ok(res["status"] == "non-grantor", "founder may only swap one independent trustee for another: still non-grantor")
    res = with_(anyone_may_add_beneficiaries=True)
    ok(res["status"] == "grantor", "a power to add beneficiaries kills the 674(c) exception (Reg. 1.674(d)-2(b))")
    res = with_(anyone_may_add_beneficiaries=True, powers__0__kind="mandatory_fixed_shares")
    ok(res["status"] == "non-grantor", "fixed shares are not a power of disposition, even with an add-beneficiary clause elsewhere")
    res = with_(powers__0__holders=["independent_distribution_advisor"])
    ok(res["status"] == "unsettled", "Illinois distribution trust advisor who is not a trustee: amber, a question for counsel")
    res = with_(powers__0__holders=["adverse"])
    ok(res["status"] == "non-grantor", "a power held only by an adverse party is outside 674(a)")
    res = with_(powers__0__holders=["founder"], trustees=["founder"], powers__0__needs_adverse_consent=True)
    ok(res["status"] == "non-grantor", "founder's power that needs an adverse party's consent is outside 674(a)")
    ok(failing(with_(domestic__us_persons_control_substantial_decisions=False)) == {"7701(a)(30)(E); 679"},
       "a foreign trust fails the domestic test and is his under 679")
    ok(failing(with_(revocation__revocable=True)) == {"676(a)"}, "revocable: grantor (676)")
    ok(failing(with_(revocation__revoke_power_holders=["independent"])) == {"676(a)"}, "a nonadverse party who can revest it in him: grantor (676)")
    ok(with_(revocation__revoke_power_holders=["adverse"])["status"] == "non-grantor", "a revocation power only an adverse party holds: not 676")
    ok(failing(with_(reversion_value_share_at_inception=0.06)) == {"673(a)"}, "reversion worth 6%: grantor (673)")
    ok(with_(reversion_value_share_at_inception=0.05)["status"] == "non-grantor", "reversion worth exactly 5%: not over the limit")
    ok(failing(with_(benefit_to_grantor__income_may_go_to_founder_or_spouse=True)) == {"677(a)(1)-(2)"}, "income may go to him or his spouse: grantor (677)")
    ok(failing(with_(benefit_to_grantor__income_may_pay_premiums_on_founder_or_spouse=True)) == {"677(a)(3)"}, "income may pay premiums on his life: grantor (677(a)(3))")
    for key, rule in [("deal_for_less_than_adequate_consideration", "675(1)"),
                      ("founder_may_borrow_without_adequate_interest_or_security", "675(2)"),
                      ("founder_loan_unrepaid", "675(3)"), ("vote_closely_held_stock_nonfiduciary", "675(4)(A)"),
                      ("direct_investments_in_closely_held_stock_nonfiduciary", "675(4)(B)"),
                      ("swap_power_nonfiduciary", "675(4)(C)")]:
        ok(failing(with_(**{f"admin__{key}": True})) == {rule}, f"{key}: grantor ({rule})")
    ok(failing(with_(beneficiary_sole_power_to_vest_in_self=True)) == {"678(a)"}, "a beneficiary who can take it alone is its owner (678)")
    # Fail closed: every missing term is an error, never a pass.
    for key in REQUIRED:
        t = base_terms()
        del t[key]
        try:
            evaluate(t)
            ok(False, f"missing {key}: error")
        except MissingTerm:
            ok(True, f"missing {key}: error")
    t = base_terms()
    del t["admin"]["swap_power_nonfiduciary"]
    try:
        evaluate(t)
        ok(False, "missing admin.swap_power_nonfiduciary: error")
    except MissingTerm:
        ok(True, "missing admin.swap_power_nonfiduciary: error")
    t = base_terms()
    t["powers"][0]["holders"] = ["trust_protector"]
    try:
        evaluate(t)
        ok(False, "an unknown holder is an error")
    except MissingTerm:
        ok(True, "an unknown holder is an error")
    # The stack and the routes file: every version consistent, every route's expected verdict met.
    lines, errors = check_stack(json.loads((HERE / "stack.json").read_text()))
    ok(errors == 0, "every stack version's grantor flag matches what its terms derive")
    routes = json.loads((HERE / "grantor-routes.json").read_text())["routes"]
    for rt in routes:
        got = evaluate(rt["terms"])["status"]
        ok(got == rt["expect"], f"route {rt['id']}: {got} (expected {rt['expect']})")
    print(f"\n{fails} failed")
    return 1 if fails else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stack", default=str(HERE / "stack.json"))
    ap.add_argument("--routes-file", default=str(HERE / "grantor-routes.json"))
    ap.add_argument("--routes", action="store_true", help="design routes only")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    errors = 0
    try:
        if not a.routes:
            lines, errors = check_stack(json.loads(Path(a.stack).read_text()))
            print("\n".join(lines))
            print()
        for rt in json.loads(Path(a.routes_file).read_text())["routes"]:
            res = evaluate(rt["terms"])
            print(show(f"route {rt['id']} {rt['name']}", res, verbose=False))
    except MissingTerm as e:
        print(f"ERROR missing or unreadable term: {e} (fail closed)", file=sys.stderr)
        return 2
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
