#!/usr/bin/env python3
"""Run the trustee rehearsal (rehearsal/03-ab-rehearsal-spec.md) on a ledger.

For each scenario it reads the twelve-month ledger written by synthetic_year.py
(or, later, the founder's own sorted export, kept privately) and flies the same
year several ways:

  A        no structure: everything personal, as the spec's baseline
  B-ops    only the operating-company layer: business-shaped lines that carry
           their evidence and pass their check move to the management company
  B:<v>    the whole stack in structure version <v> (stack.json): B-ops plus
           the trusts and the Foundation, with their running costs

Every route is graded before it counts: by a real run of decide_spend.py
(insider branch A, fail closed) or by the rehearsal answer key
(answer-key-cases.ttl), or by gate G7 (records present). Anything else is
Insufficient and stays personal. Every structure version is run through checks
S1 to S17 (07-structure-integrity-checks.md): a red check removes the version;
an amber check makes its score provisional.

The score (rehearsal/loop/GOAL.md):
  structure value  = score(B:<v>) - score(B-ops): what the trusts and the
                     Foundation add on top of plain good bookkeeping, per year
  structure gap    = what the structure still costs per year (0 when it pays)
  break-even asset = the yearly net income an income-producing asset held in
                     the stack must earn before the structure value reaches 0

  python3 rehearsal_run.py                     all scenarios, report to stdout
  python3 rehearsal_run.py --ledgers DIR       ledgers from DIR (default ./out)
  python3 rehearsal_run.py --json FILE         also write the full results
  python3 rehearsal_run.py --record LEDGER.csv append today's scores (the loop's history)
  python3 rehearsal_run.py --selftest          tax engine, structure answer key, rename invariance

Standard library only (decide_spend.py itself needs rdflib and pyshacl; if it
cannot run, every flow it grades is Insufficient). SYNTHETIC inputs. Design
and education, not legal or tax advice.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import string
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
from synthetic_year import benchmarks, resolve, load_json  # noqa: E402

BM = benchmarks()
FED = BM["federal_2026"]
PAY = BM["payroll_2026"]
IL = BM["illinois"]
STRUCTURE_CHECKS = [f"S{i}" for i in range(1, 18)]


# ------------------------------------------------------------------ tax engine

def bracket_tax(taxable: float, brackets: list) -> float:
    tax = 0.0
    for i, (lo, rate) in enumerate(brackets):
        hi = brackets[i + 1][0] if i + 1 < len(brackets) else float("inf")
        if taxable > lo:
            tax += (min(taxable, hi) - lo) * rate
    return tax


def employee_fica(fica_wages: float) -> float:
    return min(fica_wages, PAY["ss_wage_base"]) * 0.062 + fica_wages * 0.0145


def niit_individual(nii: float, magi: float) -> float:
    """IRC 1411(a)(1): 3.8% of the lesser of net investment income and MAGI over the threshold
    (1411(b)(3): 200,000 for a single filer). MAGI = AGI here (1411(d), no foreign exclusion)."""
    n = BM["niit"]
    return n["rate"] * min(max(nii, 0.0), max(magi - n["threshold_single"], 0.0))


def niit_trust(undistributed_nii: float, agi: float) -> float:
    """IRC 1411(a)(2): 3.8% of the lesser of undistributed net investment income and AGI over the
    dollar amount where the highest trust bracket begins (the last trust_brackets entry)."""
    top = FED["trust_brackets"][-1][0]
    return BM["niit"]["rate"] * min(max(undistributed_nii, 0.0), max(agi - top, 0.0))


def person_tax(wages=0.0, sched_c=0.0, sched_e=0.0, other_ordinary=0.0, qbi_income=0.0,
               mortgage_interest=0.0, property_tax=0.0, charity=0.0,
               deferral_401k=0.0, cafeteria_125=0.0, nii=0.0) -> dict:
    """One single filer's 2026 federal, payroll and Illinois tax. Returns the parts.
    wages is W-2 gross pay. cafeteria_125 leaves income-tax and FICA wages (125(a), 3121(a)(5)(G));
    deferral_401k leaves income-tax wages only (402(e)(3), 3121(v)(1)(A)). benchmarks-tax.json payroll_pretax."""
    cafeteria_125 = min(max(cafeteria_125, 0.0), max(wages, 0.0))
    deferral_401k = min(max(deferral_401k, 0.0), max(wages - cafeteria_125, 0.0))
    fica_wages = wages - cafeteria_125
    income_wages = wages - cafeteria_125 - deferral_401k
    se_base = max(sched_c, 0.0) * PAY["se_net_earnings_factor"]
    oasdi_room = max(PAY["ss_wage_base"] - fica_wages, 0.0)
    se_tax = min(se_base, oasdi_room) * PAY["se_rate_oasdi"] + se_base * PAY["se_rate_hi"]
    fica = employee_fica(fica_wages)
    agi = income_wages + sched_c + sched_e + other_ordinary - se_tax / 2
    il_tax = max(agi, 0.0) * IL["individual_rate"]
    salt = min(il_tax + property_tax, FED["salt_cap_2026"])  # AGI far below the phase-down threshold
    itemized = mortgage_interest + salt + charity
    deduction = max(FED["standard_deduction_single"], itemized)
    before_qbi = max(agi - deduction, 0.0)
    qbi = FED["qbi_rate"] * min(max(qbi_income, 0.0), before_qbi)
    taxable = before_qbi - qbi
    fed = bracket_tax(taxable, FED["single_brackets"])
    niit = niit_individual(nii, agi)
    return {"agi": agi, "taxable": taxable, "federal": fed, "se": se_tax, "fica": fica, "niit": niit,
            "illinois": il_tax, "itemized": itemized > FED["standard_deduction_single"],
            "total": fed + se_tax + fica + il_tax + niit}


def trust_tax(retained: float, nii: float | None = None) -> float:
    """Trust tax on retained income, plus NIIT (1411(a)(2)) on the retained part that is net
    investment income (nii; defaults to all of it, retained income being the trust's AGI here)."""
    retained = max(retained, 0.0)
    n = retained if nii is None else nii
    return (bracket_tax(retained, FED["trust_brackets"]) + retained * (IL["trust_rate"] + IL["trust_replacement_tax"])
            + niit_trust(n, retained))


# ------------------------------------------------------------------ checks

def decide_outcomes() -> dict:
    """Run decide_spend.py once; map case id -> outcome. Fail closed if it can't run."""
    try:
        r = subprocess.run([sys.executable, str(REPO / "decide_spend.py")], cwd=REPO,
                           capture_output=True, text=True, timeout=600)
    except Exception:  # noqa: BLE001
        return {}
    out = {}
    for line in r.stdout.splitlines():
        m = re.match(r"^([A-Z]\d+\w*)\s+(allow|block|insufficient|needs counsel)\b", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def answer_key() -> dict:
    text = (HERE.parent / "answer-key-cases.ttl").read_text()
    out = {}
    for m in re.finditer(r"k:(K\d+) a rh:TestCase\b(.*?)rh:expectedVerdict rh:(\w+)", text, re.S):
        out[m.group(1)] = {"Green": "allow", "Red": "block", "Amber": "needs counsel",
                           "NoRouteYet": "block"}[m.group(3)]
    return out


class Grader:
    def __init__(self, stack: dict):
        self.map = stack["spend_check_map"]
        self.decide = decide_outcomes()
        self.key = answer_key()
        self.used = defaultdict(int)

    def grade(self, flow: str, evidence_present: bool | None = None) -> tuple:
        """Return (outcome, grader) for a flow kind. No mapping = insufficient."""
        if flow.startswith("gate:G7"):
            return ("allow" if evidence_present else "insufficient", "gate G7 records (274(d), Reg. 1.62-2(e))")
        ref = self.map.get(flow)
        if not ref:
            return ("insufficient", "no mapped case (fail closed)")
        src, case = ref.split(":", 1)
        outcome = (self.decide if src == "decide" else self.key).get(case)
        self.used[ref] += 1
        if outcome is None:
            return ("insufficient", f"{ref} not graded (decide_spend.py unavailable?)")
        return (outcome, ref)


def _v(x, bad):
    """bad=True means the fact being True is the red flag."""
    if x is None:
        return "amber"
    return "fail" if bool(x) == bad else "pass"


def structure_verdicts(facts: dict) -> dict:
    """Checks S1-S17 from fact fields only (never names or labels).
    A fact that is missing or null is amber: unknown never passes and never fails."""
    f = facts
    out = {}
    trust = f.get("has_trust", True)
    rep = f.get("trust_reported_as")
    ctrl = f.get("founder_controls_trust")
    # S1: tax position matches who controls
    if not trust:
        out["S1"] = "pass"
    elif ctrl is None or rep is None:
        out["S1"] = "amber"
    else:
        out["S1"] = "fail" if (ctrl and rep == "separate") else "pass"
    # S2: a trust claimed separate needs a trustee who is not related or subordinate and acts independently
    if not trust or rep == "grantor":
        out["S2"] = "pass"
    elif rep is None:
        out["S2"] = "amber"
    else:
        rel, log = f.get("trustee_related_or_subordinate"), f.get("trustee_decision_log_with_declines")
        signs = f.get("trustee_signs_whatever_founder_sends")
        if rel or signs:
            out["S2"] = "fail"
        elif rel is False and log:
            out["S2"] = "pass"
        else:
            out["S2"] = "amber"
    out["S3"] = "pass" if not trust else _v(f.get("trust_payment_tools_outside_trustee"), True)
    out["S4"] = "pass" if not trust else _v(f.get("trust_transactions_follow_terms"), False)
    s5 = [f.get("founder_relationship_to_trust_property_unchanged"), f.get("founder_runs_trust_owned_business_day_to_day")]
    out["S5"] = "fail" if any(x is True for x in s5) else ("pass" if all(x is False for x in s5) else "amber")
    n = f.get("personal_lines_deducted")
    out["S6"] = "amber" if n is None else ("fail" if n > 0 else "pass")
    s7 = [f.get("residence_or_furnishings_depreciated"), f.get("stepped_up_basis_claimed_on_transfer")]
    out["S7"] = "fail" if any(x is True for x in s7) else ("pass" if all(x is False for x in s7) else "amber")
    flows = f.get("related_party_flows")
    if flows is None:
        out["S8"] = "amber"
    else:
        parts = [fl.get(k) for fl in flows for k in ("at_market", "documented", "service_or_use_real", "paid")]
        out["S8"] = "fail" if any(x is False for x in parts) else ("pass" if all(x is True for x in parts) else "amber")
    out["S9"] = _v(f.get("income_lands_with_who_earned_it"), False)
    out["S10"] = _v(f.get("se_or_payroll_tax_reduction_claimed"), True)
    k = f.get("chain_layers_without_own_activity")
    out["S11"] = "amber" if k is None else ("fail" if k > 0 else "pass")
    out["S12"] = _v(f.get("business_run_by_entity_filing_as_trust"), True)
    if f.get("has_charity") is False:
        out["S13"] = "pass"
    else:
        ex, pays = f.get("charity_exempt_or_application_filed"), f.get("charity_pays_family_costs")
        out["S13"] = "fail" if (ex is False or pays is True) else ("pass" if (ex and pays is False) else "amber")
    out["S14"] = _v(f.get("foreign_trust_unreported"), True)
    out["S15"] = _v(f.get("transfers_reported_inconsistently"), True)
    out["S16"] = _v(f.get("retained_use_assumed_outside_estate"), True)
    out["S17"] = _v(f.get("purpose_includes_irs_false_claim"), True)
    return out


# ------------------------------------------------------------------ the year

def read_ledger(path: Path) -> list:
    with path.open() as f:
        return list(csv.DictReader(f))


def summarize(rows: list) -> dict:
    s = defaultdict(float)
    for r in rows:
        a = float(r["amount"])
        d, payer, payee, desc = r["domain"], r["payer_role"], r["payee_role"], r["description"]
        if r["direction"] == "credit":
            s[f"in_{d}"] += a
            continue
        if payer == "building":
            s["building_costs"] += a
        elif payer == "asset":
            s["asset_principal" if d == "A2" else "asset_costs"] += a
        elif d == "SAV":
            s["saving"] += a
        else:
            s["living"] += a
            s[f"living_{d}"] += a
        if "mortgage interest, own unit" in desc:
            s["own_mortgage_interest"] += a
        if "property tax, own unit" in desc:
            s["own_property_tax"] += a
        if d == "D17" and "acknowledgment_letter" in r["evidence"]:
            s["charity_acknowledged"] += a
    return s


def business_routes(rows: list, grader: Grader, assumptions: dict) -> tuple:
    """B-ops: which personally paid lines may move to the management company."""
    routed = 0.0
    log = defaultdict(lambda: {"lines": 0, "amount": 0.0, "outcome": "", "grader": ""})
    probes = []
    for r in rows:
        if r["direction"] != "debit" or r["payer_role"] != "founder":
            continue
        d = r["domain"]
        share = float(r["business_share"])
        amt = float(r["amount"])
        ev = bool(r["evidence"])
        if share <= 0:
            continue
        if d == "D12":
            flow = "mileage_with_log" if ev else "mileage_without_log"
        elif d == "D1":
            flow = "software_with_use_log" if ev else "software_without_use_log"
        elif d in ("D7", "D11", "D5", "D6"):
            flow = "gate:G7"
        else:
            flow = "unmapped:" + d
        outcome, g = grader.grade(flow, ev)
        deductible = amt * share * (assumptions["meals_deductible_share"] if d == "D7" else 1.0)
        key = (d, flow, outcome)
        log[key]["lines"] += 1
        log[key]["amount"] += deductible
        log[key]["outcome"], log[key]["grader"] = outcome, g
        if outcome == "allow":
            routed += deductible
    # Probes: lines the twin is tempted to route and must refuse.
    for flow, label in [("groceries_through_company", "groceries through the management company"),
                        ("commute_through_company", "commute rides through the management company"),
                        ("suits_through_company", "business suits through the management company"),
                        ("family_vacation_through_company", "the personal share of trips through the company"),
                        ("groceries_through_foundation", "groceries through the Foundation"),
                        ("home_office_mailing_address_only", "a home office that is only a mailing address"),
                        ("tuition_paid_to_school", "tuition paid straight to the school (gift-tax exclusion, no income-tax saving)")]:
        outcome, g = grader.grade(flow)
        probes.append({"flow": label, "outcome": outcome, "grader": g})
    rows_out = [{"domain": k[0], "flow": k[1], "outcome": v["outcome"], "grader": v["grader"],
                 "lines": v["lines"], "deductible": round(v["amount"])} for k, v in sorted(log.items())]
    return routed, rows_out, probes


def run_year(sc: dict, rows: list, stack: dict, grader: Grader, extra_asset_net: float = 0.0,
             versions: list | None = None) -> dict:
    A = stack["assumptions"]
    if sc.get("trustee_kind"):  # a scenario may fix its trustee kind (ASSUMPTION stated in the scenario)
        A = dict(A, trustee_kind=sc["trustee_kind"])
    fees = {k: (resolve(v, BM) if not isinstance(v, str) or "." in v else v)
            for k, v in stack["fees_placeholder"].items() if k != "note"}
    s = summarize(rows)
    wages = s["in_I1"]
    rent = s["in_I2"]
    mgmt_rev = s["in_I3"]
    dep_b = A["building_depreciable_basis"] * A["building_rented_share"] / A["residential_recovery_years"]
    sched_e_building = rent - s["building_costs"] - dep_b

    kind = (sc.get("asset") or {}).get("kind")
    asset_in = s["in_I4"]
    if kind == "rental":
        asset_dep = A["asset_building_depreciable_basis"] / A["residential_recovery_years"]
    elif kind == "business":
        asset_dep = A["asset_business_amortizable_basis"] / A["intangible_amortization_years"]
    else:
        asset_dep = 0.0
    asset_net = asset_in - s["asset_costs"] - asset_dep + extra_asset_net
    asset_qbi = asset_net if kind == "business" else 0.0
    # NIIT: rent is net investment income unless earned in a non-passive trade or business (1411(c)(1)(A)(i));
    # a business is net investment income if passive under 469 (1411(c)(2)(A)). ASSUMPTION (benchmarks-tax.json
    # niit): the founder rents out and does not materially participate, and the bought business runs under a
    # hired manager, so both are passive. Consulting is self-employment income, excluded by 1411(c)(6).
    asset_nii_share = 1.0 if kind in ("rental", "business") else 0.0
    asset_cash = asset_in - s["asset_costs"] - s["asset_principal"] + extra_asset_net

    bene_income = resolve(A["beneficiary_other_income"], BM)
    n_bene = A.get("adult_beneficiaries", 2)
    bene_base = person_tax(wages=bene_income)["total"] * n_bene

    itemize = dict(mortgage_interest=s["own_mortgage_interest"], property_tax=s["own_property_tax"],
                   charity=s["charity_acknowledged"])

    # Payroll: pre-tax deductions by section (scenarios.json "payroll" and "pretax").
    pay = sc.get("payroll") or {}
    pretax = {"125": 0.0, "401k": 0.0}
    for d in sc.get("pretax") or []:
        if str(d["section"]) not in pretax:
            raise ValueError(f"pretax section {d['section']!r}: only 125 or 401k")
        pretax[str(d["section"])] += float(d["annual"])
    listed_401k = pretax["401k"]  # not a ledger line, so it is saving taken out of pay here
    if pay.get("retirement_line_includes_fica"):
        # The CE line already holds the employee FICA that person_tax computes (ce_glossary),
        # so only the rest of the line is saving; it is taxed as its stated section.
        saving_line = max(s["saving"] - employee_fica(wages - min(pretax["125"], wages)), 0.0)
        if pay.get("retirement_rest_section", "401k") == "401k":
            pretax["401k"] += saving_line
    else:
        saving_line = s["saving"]
    saving_out = saving_line + listed_401k

    def founder(sched_c, asset_ord, asset_q):
        return person_tax(wages=wages, sched_c=sched_c, sched_e=sched_e_building + asset_ord,
                          qbi_income=max(sched_c, 0) + asset_q, nii=sched_e_building + asset_ord,
                          deferral_401k=pretax["401k"], cafeteria_125=pretax["125"], **itemize)

    # Arm A: no structure; business-shaped lines paid personally and not deducted (spec, Arm A)
    fa = founder(mgmt_rev, asset_net, asset_qbi)
    cost_a = fa["total"] + bene_base

    # Arm B-ops: the management company carries documented business lines
    routed, route_rows, probes = business_routes(rows, grader, A)
    llc_fee = fees["llc_annual_report"] + fees["registered_agent_each"] + fees["bookkeeping_each_entity"]
    fo = founder(mgmt_rev - routed, asset_net, asset_qbi)
    cost_ops = fo["total"] + bene_base + llc_fee
    score_ops = cost_a - cost_ops

    gross_in = wages + rent + mgmt_rev + asset_in + extra_asset_net
    property_out = s["building_costs"] + s["asset_costs"] + s["asset_principal"]

    def money_view(cost_taxes_fees):
        # The family as one pool: the founder's household plus the adult beneficiaries' share.
        # Their own baseline tax on their own pay (bene_base) is not this money, so it is taken out.
        after = gross_in - property_out - (cost_taxes_fees - bene_base)
        return {"after_taxes_and_fees": round(after), "left_after_living": round(after - s["living"] - saving_out),
                "saving_payroll": round(saving_out)}

    w = stack.get("legacy_weight_w", 0.0)
    out_versions = {}
    for vid in versions or [sc.get("stack_version", "today"), "flat", "flat_independent", "steward_r2", "steward_r3", "steward_r2_pipeline"]:
        if vid in out_versions:
            continue
        v = stack["versions"][vid]
        checks = structure_verdicts(v["facts"])
        n_llc = len(v["llcs"]) + (1 if kind else 0)
        fee = n_llc * llc_fee + len(v["trusts_filing_1041"]) * fees["form_1041_prep_each"]
        f = v["foundation"]
        program = 0.0
        if f["exists"]:
            fee += fees["form_990pf_prep"] + fees["il_ag_charity_annual_fee"] + fees["bookkeeping_each_entity"]
            excise = f["net_investment_income"] * 0.0139
            fee += excise
        fee += fees["bookkeeping_each_entity"]  # the Family Trust's own books, grantor or not
        ft = v["family_trust"]
        trust_tax_paid = 0.0
        to_foundation = 0.0
        bene_tax = bene_base
        held_in_trust = bool(kind) or extra_asset_net > 0
        if ft["grantor"] or not held_in_trust:
            fb = founder(mgmt_rev - routed, asset_net, asset_qbi)
        else:
            # Non-grantor, independent trustee: the trust's income is taxed to the adult
            # beneficiaries it distributes to (652(a), 662(a)); what it keeps, at trust rates.
            fb = founder(mgmt_rev - routed, 0.0, 0.0)
            dist = asset_net * A["trust_distributes_share_of_dni"]
            share = ft.get("foundation_share_of_distribution", 0.0)
            if f["exists"] and share > 0:
                # ASSUMPTION (counsel-queue.md Q9): the trust pays this share of its distribution to the Foundation
                # as a 642(c)(1) charitable set-aside paid from gross income, deducted from retained income; the
                # beneficiaries are taxed on the rest. It makes the trust a 4947(a)(2) split-interest trust.
                to_foundation = max(dist * share, 0.0)
            dist_taxed = dist - to_foundation
            retained = asset_net - dist
            trust_tax_paid = trust_tax(retained, retained * asset_nii_share)
            share_each = dist_taxed / n_bene
            q_each = asset_qbi * A["trust_distributes_share_of_dni"] / n_bene
            bene_tax = n_bene * person_tax(wages=bene_income, other_ordinary=share_each, qbi_income=q_each,
                                                nii=share_each * asset_nii_share)["total"]
            asset_value = max(asset_net, 0.0) / A["asset_yield_for_value"]
            trustee = (max(fees["independent_trustee_minimum"], fees["independent_trustee_rate_of_assets"] * asset_value)
                       if A.get("trustee_kind", "professional") == "professional" else fees.get("unrelated_individual_trustee", 1000))
            fee += trustee + fees["form_709_prep_once"]
        # Program output: what the trust sends the Foundation when it does; else the fixed 5 percent figure.
        if to_foundation > 0:
            program, program_source = to_foundation, "asset_income"
        else:
            program = 0.05 * f["assets"] if f["exists"] else 0.0
            program_source = "fixed_assets"
        # The set-aside leaves the family's money (w, not this line, values what it does at the Foundation).
        cost_b = fb["total"] + bene_tax + trust_tax_paid + fee + to_foundation
        score = cost_a - cost_b + w * program
        value = score - score_ops
        red = [k for k, x in checks.items() if x == "fail"]
        amber = [k for k, x in checks.items() if x == "amber"]
        out_versions[vid] = {
            "label": v["label"], "fees": round(fee), "taxes": round(cost_b - fee - to_foundation), "program_output": round(program),
            "program_source": program_source, "to_foundation": round(to_foundation),
            "score_vs_A": round(score), "structure_value": round(value), "structure_gap": round(max(0.0, -value)),
            "checks_pass": sum(1 for x in checks.values() if x == "pass"), "checks_amber": amber, "checks_red": red,
            "status": "out (red check)" if red else ("provisional (amber checks)" if amber else "scored"),
            "facts_basis": v["facts_basis"], "money": money_view(cost_b), "trust_tax": round(trust_tax_paid),
            "management_fee_check": grader.grade("management_fee_" + v["management_fee_flow"]),
        }
    return {
        "scenario": sc["id"], "label": sc["label"],
        "inputs": {k: round(val) for k, val in [("wages", wages), ("rent", rent), ("management_revenue", mgmt_rev),
                                                ("building_costs", s["building_costs"]), ("asset_income", asset_in),
                                                ("asset_costs", s["asset_costs"]), ("asset_net_taxable", asset_net),
                                                ("asset_cash_after_principal", asset_cash),
                                                ("living", s["living"]), ("payroll_saving", saving_out),
                                                ("pretax_401k", pretax["401k"]), ("pretax_125", pretax["125"])]},
        "A": {"taxes": round(cost_a), "founder": {k: round(v) if isinstance(v, float) else v for k, v in fa.items()},
              "money": money_view(cost_a)},
        "B_ops": {"routed_deductions": round(routed), "taxes_and_fees": round(cost_ops), "score_vs_A": round(score_ops),
                  "money": money_view(cost_ops), "routes": route_rows},
        "probes": probes,
        "versions": out_versions,
    }


def break_even(sc, rows, stack, grader, vid, trustee_kind, cap=1_000_000.0):
    """Smallest extra yearly net income from an asset held in the stack at which version vid's
    structure value reaches 0. None if it never does up to cap."""
    st = json.loads(json.dumps(stack))
    st["assumptions"]["trustee_kind"] = trustee_kind
    sc2 = {k: x for k, x in sc.items() if k != "trustee_kind"}
    sc2["asset"] = sc.get("asset") or {"kind": "generic"}

    def value(x):
        return run_year(sc2, rows, st, grader, extra_asset_net=x, versions=[vid])["versions"][vid]["structure_value"]

    if value(0.0) >= 0:
        return 0.0
    lo, hi = 0.0, cap
    if value(hi) < 0:
        return None
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if value(mid) >= 0 else (mid, hi)
    return round(hi, -2)


# ------------------------------------------------------------------ selftest

def selftest() -> int:
    fails = 0

    def ok(cond, msg):
        nonlocal fails
        print(("ok    " if cond else "FAIL  ") + msg)
        fails += not cond

    b = FED["single_brackets"]
    ok(round(bracket_tax(50400, b)) == 5800, "single 2026: tax at 50,400 is 5,800 (Rev. Proc. 2025-32 base)")
    ok(round(bracket_tax(105700, b)) == 17966, "single 2026: tax at 105,700 is 17,966")
    ok(round(bracket_tax(16000, FED["trust_brackets"])) == 3851, "trusts 2026: tax at 16,000 is 3,851")
    t = person_tax(wages=16100)
    ok(round(t["federal"]) == 0, "wages equal to the standard deduction owe no federal income tax")
    ok(round(person_tax(sched_c=10000)["se"]) == round(10000 * 0.9235 * 0.153), "self-employment tax on 10,000")
    # Pre-tax payroll: 401(k) leaves income-tax wages only; section 125 leaves both (payroll_pretax).
    d, w55, w60 = person_tax(wages=60000, deferral_401k=5000), person_tax(wages=55000), person_tax(wages=60000)
    ok(round(d["federal"]) == round(w55["federal"]) and round(d["illinois"]) == round(w55["illinois"])
       and round(d["fica"]) == round(w60["fica"]),
       "401(k) deferral of 5,000 on 60,000: income tax as on 55,000, FICA as on 60,000")
    c, w57 = person_tax(wages=60000, cafeteria_125=3000), person_tax(wages=57000)
    ok(round(c["federal"]) == round(w57["federal"]) and round(c["fica"]) == round(w57["fica"]),
       "section 125 amount of 3,000 on 60,000: income tax and FICA as on 57,000")
    ok(round(person_tax(wages=1000, deferral_401k=5000)["agi"]) == 0, "a deferral never exceeds pay")
    # NIIT (IRC 1411): individual 200,000 single threshold, trust threshold at the top bracket start.
    ok(round(niit_individual(50000, 190000)) == 0, "NIIT: MAGI under 200,000 owes none")
    ok(round(niit_individual(50000, 230000)) == round(0.038 * 30000), "NIIT: lesser of NII 50,000 and excess 30,000")
    ok(round(niit_individual(10000, 300000)) == 380, "NIIT: NII 10,000 under a large excess is 380")
    top = FED["trust_brackets"][-1][0]
    ok(round(niit_trust(20000, 20000)) == round(0.038 * (20000 - top)), "NIIT trust: retained 20,000 pays on the excess over the top bracket start")
    ok(round(niit_trust(20000, top)) == 0, "NIIT trust: retained income at the top bracket start owes none")
    ok(round(trust_tax(20000) - trust_tax(20000, 0.0)) == round(niit_trust(20000, 20000)) and niit_trust(20000, 20000) > 0,
       "NIIT trust: retained income that is not investment income adds no NIIT")
    ok(round(person_tax(wages=250000, nii=40000)["niit"]) == round(0.038 * 40000), "NIIT flows through person_tax")
    # Structure answer key: encode SK1-SK14 as facts and compare with structure-check-cases.ttl
    text = (HERE.parent / "structure-check-cases.ttl").read_text()
    expected = {}
    for m in re.finditer(r"sk:(SK\d+) a rh:StructureCase\b(.*?)(?=\nsk:|\Z)", text, re.S):
        fails_ = set(re.findall(r"s:(S\d+)", " ".join(re.findall(r"rh:failsCheck ([^;.]+)", m.group(2)))))
        passes_ = set(re.findall(r"s:(S\d+)", " ".join(re.findall(r"rh:passesCheck ([^;.]+)", m.group(2)))))
        expected[m.group(1)] = (fails_, passes_)
    cases = load_json(HERE / "structure-cases-facts.json")["cases"]
    for cid, (exp_fail, exp_pass) in sorted(expected.items(), key=lambda kv: int(kv[0][2:])):
        if cid not in cases:
            continue
        v = structure_verdicts(cases[cid]["facts"])
        got_fail = {k for k, x in v.items() if x == "fail"}
        got_pass = {k for k, x in v.items() if x == "pass"}
        ok(got_fail == exp_fail and exp_pass <= got_pass,
           f"{cid}: fails {sorted(got_fail) or '-'} (key {sorted(exp_fail) or '-'}), passes include {sorted(exp_pass) or '-'}")
    # Rename invariance: renaming every entity in a case changes no verdict.
    rng = random.Random(7)
    for cid in ("SK1", "SK3"):
        c = cases[cid]
        renamed = {"".join(rng.choice(string.ascii_lowercase) for _ in range(8)): e for e in c.get("entities", [])}
        c2 = {"entities": list(renamed), "facts": c["facts"]}
        ok(structure_verdicts(c2["facts"]) == structure_verdicts(c["facts"]), f"{cid} renamed: same verdicts")
    missing = [k for k in expected if k not in cases and k not in ("SK15", "SK16")]
    ok(not missing, f"every structure case has facts ({missing or 'all'})")
    # Grantor trust rules (IRC 671-679): the check's own cases, and every stack version's
    # grantor flag must match what its modeled terms derive (grantor_check.py).
    import grantor_check
    ok(grantor_check.selftest() == 0, "grantor trust check: its own cases, the stack's flags and the design routes")
    ok(__import__("scorecard").selftest() == 0, "goal scorecard: a passing and a failing fixture for each criterion")
    # Pipeline: a steward_r2 copy that sends 25 percent of the trust's distribution to the Foundation
    # takes program output from the asset's income, and more income gives more program output.
    st_p = json.loads(json.dumps(load_json(HERE / "stack.json")))
    st_p["versions"]["pipeline_test"] = json.loads(json.dumps(st_p["versions"]["steward_r2"]))
    st_p["versions"]["pipeline_test"]["family_trust"]["foundation_share_of_distribution"] = 0.25
    sc_p = {"id": "pipeline", "label": "pipeline test", "payroll": {}, "asset": {"kind": "generic"}}
    grader_p = Grader(st_p)

    def pipeline(x):
        return run_year(sc_p, [], st_p, grader_p, extra_asset_net=x, versions=["pipeline_test"])["versions"]["pipeline_test"]

    lo_p, hi_p = pipeline(40000.0), pipeline(80000.0)
    ok(lo_p["program_output"] > 0 and lo_p["program_source"] == "asset_income",
       "pipeline: a share of the trust's distribution to the Foundation makes program output come from asset income")
    ok(hi_p["program_output"] > lo_p["program_output"], "pipeline: a larger asset income gives a larger program output")
    ok(run_year(sc_p, [], st_p, grader_p, extra_asset_net=40000.0, versions=["steward_r2"])["versions"]["steward_r2"]["program_source"] == "fixed_assets",
       "pipeline: with no share the program output stays the fixed 5 percent of Foundation assets")
    # The trust's deduction is the whole distribution (661 for the beneficiaries, 642(c)(1) for the Foundation),
    # so the share moves no income from the trust's retained side: its tax equals the no-share value.
    ok(pipeline(40000.0)["trust_tax"] == run_year(sc_p, [], st_p, grader_p, extra_asset_net=40000.0, versions=["steward_r2"])["versions"]["steward_r2"]["trust_tax"],
       "pipeline: the Foundation's share does not change the trust's retained income or its tax")
    # R7: money sent to the Foundation is paid out of the family's pocket, so it lowers the score by that amount (w = 0).
    base_p = run_year(sc_p, [], st_p, grader_p, extra_asset_net=40000.0, versions=["steward_r2"])["versions"]["steward_r2"]
    ok(lo_p["score_vs_A"] < base_p["score_vs_A"] and base_p["score_vs_A"] - lo_p["score_vs_A"] <= lo_p["to_foundation"],
       "pipeline: the set-aside costs the family money, so the score falls, by no more than the gift (the beneficiaries' tax falls a little)")
    # A scenario may fix its trustee kind; break_even must still be free to vary it.
    sc_t = dict(sc_p, trustee_kind="individual")
    fee_ind = run_year(sc_t, [], st_p, grader_p, extra_asset_net=80000.0, versions=["steward_r2"])["versions"]["steward_r2"]["fees"]
    fee_pro = run_year(sc_p, [], st_p, grader_p, extra_asset_net=80000.0, versions=["steward_r2"])["versions"]["steward_r2"]["fees"]
    ok(fee_ind < fee_pro, "scenario trustee_kind individual prices the trustee below the professional default")
    print(f"\n{fails} failed")
    return 1 if fails else 0


# ------------------------------------------------------------------ report

def money(x):
    return f"{x:,.0f}" if x is not None else "none up to 1,000,000"


def report(results: list) -> str:
    out = ["SYNTHETIC rehearsal run. Not the founder's numbers. Not legal or tax advice.", ""]
    for r in results:
        i = r["inputs"]
        out.append(f"== {r['scenario']}: {r['label']}")
        out.append(f"   wages {money(i['wages'])}, rent {money(i['rent'])}, consulting {money(i['management_revenue'])}, "
                   f"asset income {money(i['asset_income'])}, living {money(i['living'])}")
        out.append(f"   A      taxes {money(r['A']['taxes'])}; left after living {money(r['A']['money']['left_after_living'])}")
        out.append(f"   B-ops  routes {money(r['B_ops']['routed_deductions'])} of business lines; "
                   f"score vs A {r['B_ops']['score_vs_A']:+,}")
        for vid, v in r["versions"].items():
            out.append(f"   B:{vid:<17} fees {money(v['fees'])}, score vs A {v['score_vs_A']:+,}, "
                       f"structure value {v['structure_value']:+,}/yr, checks pass {v['checks_pass']}/17, {v['status']}")
        be = r.get("break_even", {})
        for k, x in be.items():
            out.append(f"   break-even asset income, {k}: {money(x)}")
        for k, x in r.get("route_break_even", {}).items():
            out.append(f"   break-even asset income, {k}: {money(x)}")
        out.append("")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default=str(HERE / "scenarios.json"))
    ap.add_argument("--stack", default=str(HERE / "stack.json"))
    ap.add_argument("--ledgers", default=str(HERE / "out"))
    ap.add_argument("--json")
    ap.add_argument("--record")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        sys.exit(selftest())
    spec = load_json(Path(a.scenarios))
    stack = load_json(Path(a.stack))
    grader = Grader(stack)
    import grantor_check
    try:
        grantor_lines, grantor_errors = grantor_check.check_stack(stack)
    except grantor_check.MissingTerm as e:
        sys.exit(f"grantor trust check: missing or unreadable term {e} (fail closed)")
    if not grader.decide:
        print("decide_spend.py could not run: every flow it grades is Insufficient (fail closed)", file=sys.stderr)
    results = []
    for sc in spec["scenarios"]:
        sc = dict(sc, payroll=spec.get("payroll", {}))
        p = Path(a.ledgers) / f"ledger-{sc['id']}.csv"
        if not p.exists():
            sys.exit(f"missing ledger {p}: run synthetic_year.py first")
        rows = read_ledger(p)
        r = run_year(sc, rows, stack, grader)
        r["break_even"] = {
            "him as trustee (grantor trust)": break_even(sc, rows, stack, grader, "flat", "professional"),
            "independent professional trustee": break_even(sc, rows, stack, grader, "flat_independent", "professional"),
            "independent unrelated individual trustee": break_even(sc, rows, stack, grader, "flat_independent", "individual"),
        }
        r["route_break_even"] = {
            "route R2 independent distribution trustee, professional": break_even(sc, rows, stack, grader, "steward_r2", "professional"),
            "route R2 independent distribution trustee, unrelated individual": break_even(sc, rows, stack, grader, "steward_r2", "individual"),
            "route R3 fixed shares, professional": break_even(sc, rows, stack, grader, "steward_r3", "professional"),
            "route R3 fixed shares, unrelated individual": break_even(sc, rows, stack, grader, "steward_r3", "individual"),
            "route R2 with a 10 percent Foundation share, unrelated individual": break_even(sc, rows, stack, grader, "steward_r2_pipeline", "individual"),
        }
        results.append(r)
    print(report(results))
    print("Grantor trust status of the Family Trust, from its modeled terms (IRC 671-679, grantor_check.py):")
    print("\n".join(grantor_lines))
    if grantor_errors:
        sys.exit("grantor trust check: a version's terms make it a different kind of trust than the engine taxes it as")
    if a.json:
        Path(a.json).write_text(json.dumps({"run_on": date.today().isoformat(), "results": results,
                                            "graders_used": dict(grader.used)}, indent=2))
    if a.record:
        rec = Path(a.record)
        new = not rec.exists()
        with rec.open("a", newline="") as f:
            wr = csv.writer(f)
            if new:
                wr.writerow(["date", "scenario", "version", "status", "checks_pass", "score_vs_A",
                             "structure_value", "structure_gap", "break_even_grantor",
                             "break_even_professional", "break_even_individual"])
            for r in results:
                be = list(r["break_even"].values())
                for vid, v in r["versions"].items():
                    wr.writerow([date.today().isoformat(), r["scenario"], vid, v["status"], v["checks_pass"],
                                 v["score_vs_A"], v["structure_value"], v["structure_gap"],
                                 *["none" if x is None else int(x) for x in be]])


if __name__ == "__main__":
    main()
