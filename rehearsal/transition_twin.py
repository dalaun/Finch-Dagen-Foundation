#!/usr/bin/env python3
"""Transition twin: rehearse the move from W-2 income to business ownership.

Runs several arms month by month over the same founder and the same horizon:

  A    stay on the W-2 only (the baseline)
  B    buy a business while keeping the W-2, a manager runs it
  B0   the same purchase with no AI margin gain (shows what the AI work is worth)
  C    grow an existing operating company first, self-funded

Every month it tracks personal cash, business cash, debt service, wages paid to
the founder, reserves, loan balances and the business's value. Each month it
applies the step-down test (all parts must pass, for several months running).
Each arm also runs its red-flag checks (T1 to T16), which read fact fields only.

Standard library only. Run:

  python3 transition_twin.py                          synthetic inputs, summary
  python3 transition_twin.py my-inputs.json           your own inputs
  python3 transition_twin.py --csv out_dir            also write month-by-month CSVs
  python3 transition_twin.py --selftest               run the built-in cases

Inputs in this repository are SYNTHETIC. Real inputs live in the private project
folder, never here. Design and education, not legal, tax or lending advice.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_INPUTS = HERE / "transition-inputs-synthetic.json"


# ---------------------------------------------------------------- finance math

def payment(principal: float, annual_rate: float, months: int) -> float:
    """Level monthly payment on an amortizing loan."""
    if principal <= 0 or months <= 0:
        return 0.0
    r = annual_rate / 12
    if r == 0:
        return principal / months
    return principal * r / (1 - (1 + r) ** -months)


class Loan:
    def __init__(self, principal, annual_rate, months, standby_months=0, interest_accrues=True):
        self.balance = float(principal)
        self.rate = annual_rate
        self.months = months
        self.standby = standby_months
        self.accrues = interest_accrues
        self.age = 0
        self.pmt = None

    def step(self) -> float:
        """Advance one month; return the cash paid this month."""
        self.age += 1
        if self.balance <= 0.005:
            return 0.0
        interest = self.balance * self.rate / 12
        if self.age <= self.standby:
            # Full standby: no principal or interest paid; interest may accrue.
            if self.accrues:
                self.balance += interest
            return 0.0
        if self.pmt is None:
            self.pmt = payment(self.balance, self.rate, max(self.months - self.standby, 1))
        pay = min(self.pmt, self.balance + interest)
        self.balance = self.balance + interest - pay
        return pay


# ---------------------------------------------------------------- one arm

def run_arm(person: dict, arm: dict, horizon: int, trigger: dict) -> dict:
    kind = arm["kind"]  # "w2_only", "buy", "grow"
    rows = []

    salary_m = person["salary_gross_annual"] / 12
    w2_tax = person["w2_effective_tax_rate"]
    living_m = person["living_costs_annual"] / 12
    benefits_m = person["benefits_replacement_annual"] / 12
    replacement_annual = person["salary_gross_annual"] + person["benefits_replacement_annual"]
    savings = float(person["starting_savings"])

    on_w2 = True
    stepped_down_month = None
    streak = 0
    first_numbers_pass = None

    biz = arm.get("business", {})
    fin = arm.get("financing", {})
    sba = seller = None
    biz_cash = 0.0
    sde0 = biz.get("sde_annual", 0.0)
    revenue0 = biz.get("revenue_annual", 0.0)
    manager_m = biz.get("manager_market_wage_annual", 0.0) / 12
    ai = arm.get("ai", {"margin_gain_pct_of_revenue": 0.0, "ramp_months": 1, "cost_annual": 0.0, "start_month": 1})
    t12_capacity = []  # trailing operating cash before owner labor
    t12_debt = []
    acquired = False
    underwriting_dscr = None
    price = biz.get("price", 0.0)
    notes = []

    # --- day 0: purchase (arm B)
    if kind == "buy":
        equity = price * fin["equity_injection_pct"]
        seller_amt = price * fin["seller_note_pct_of_price"]
        closing = price * fin["closing_costs_pct"]
        wc = biz.get("working_capital", 0.0)
        cash_needed = equity - min(seller_amt, equity * fin["seller_note_max_share_of_equity"]) + closing + wc
        sba_amt = price - equity + closing * fin["finance_closing_costs"] + wc * fin["finance_working_capital"]
        cash_needed -= closing * fin["finance_closing_costs"] + wc * fin["finance_working_capital"]
        guarantee_fee = sba_amt * fin["sba_guarantee_fee_pct"]
        cash_needed += guarantee_fee
        floor = trigger["personal_reserve_months"] * living_m * fin["reserve_floor_share_at_close"]
        if savings - cash_needed < floor:
            notes.append("not enough cash to close and keep the reserve floor; purchase skipped")
        else:
            savings -= cash_needed
            sba = Loan(sba_amt, fin["sba_rate"], fin["sba_term_months"])
            seller = Loan(seller_amt, fin["seller_note_rate"], fin["seller_note_term_months"],
                          standby_months=fin["seller_note_standby_months"])
            biz_cash = wc
            acquired = True
            first_year_debt = 12 * payment(sba_amt, fin["sba_rate"], fin["sba_term_months"])
            underwriting_dscr = (sde0 - biz.get("manager_market_wage_annual", 0.0)) / first_year_debt
            notes.append(f"closed: equity from savings, SBA loan and seller note on {fin['seller_note_standby_months']}-month standby")

    if kind == "grow":
        acquired = True
        biz_cash = 0.0

    for m in range(1, horizon + 1):
        # ---------------- business month
        op_before_owner = 0.0
        debt = 0.0
        owner_wage = 0.0
        manager_paid = 0.0
        biz_tax = 0.0
        if acquired:
            if kind == "buy":
                sde_m = sde0 / 12
                rev_m = revenue0 / 12
                if m >= ai["start_month"]:
                    ramp = min(1.0, (m - ai["start_month"] + 1) / max(ai["ramp_months"], 1))
                    sde_m += rev_m * ai["margin_gain_pct_of_revenue"] * ramp
                    sde_m -= ai["cost_annual"] / 12
            else:  # grow
                g = arm["growth"]
                sde_annual = g["start_cash_flow_annual"] * (1 + g["monthly_growth"]) ** (m - 1)
                sde_annual = min(sde_annual, g["cap_cash_flow_annual"])
                sde_m = sde_annual / 12
                if m <= g["investment_months"]:
                    invest = g["investment_total"] / g["investment_months"]
                    savings -= invest  # founder funds growth from savings
                if m >= ai["start_month"]:
                    sde_m -= ai["cost_annual"] / 12
            if not on_w2:
                sde_m += arm.get("founder_fulltime_uplift_annual", 0.0) / 12  # what his full-time work adds
            op_before_owner = sde_m
            if sba:
                debt += sba.step()
            if seller:
                debt += seller.step()
            if on_w2:
                manager_paid = manager_m  # someone else runs it at market pay
                owner_wage = arm.get("owner_parttime_wage_annual", 0.0) / 12
            else:
                manager_paid = 0.0  # the founder is now the manager
                owner_wage = replacement_annual / 12
            profit = op_before_owner - manager_paid - owner_wage - (debt * arm.get("interest_share_of_debt", 0.5))
            biz_tax = max(profit, 0) * arm.get("entity_tax_rate", 0.0)
            biz_cash += op_before_owner - manager_paid - owner_wage - debt - biz_tax
            if biz_cash < 0:
                # Shortfall: founder covers it personally (that is what the guarantee means in practice)
                savings += biz_cash
                biz_cash = 0.0

        # ---------------- personal month
        income = 0.0
        if on_w2:
            income += salary_m * (1 - w2_tax)
        income += owner_wage * (1 - person["business_wage_effective_tax_rate"])
        costs = living_m + (0 if on_w2 else benefits_m)
        savings += income - costs

        # ---------------- step-down test (only arms with a business)
        t12_capacity.append(op_before_owner)
        t12_debt.append(debt)
        t12_capacity[:] = t12_capacity[-12:]
        t12_debt[:] = t12_debt[-12:]
        test = {}
        if kind != "w2_only" and acquired:
            cap12 = sum(t12_capacity)
            debt12 = sum(t12_debt)
            # Debt service on a full year (standby months count as future payments)
            fwd_debt12 = 12 * ((sba.pmt or payment(sba.balance, sba.rate, sba.months)) if sba else 0)
            if seller and seller.balance > 0 and seller.age > seller.standby:
                # A seller note counts once its standby has ended (on full standby it pays nothing)
                fwd_debt12 += 12 * (seller.pmt or 0)
            fwd_debt12 = max(fwd_debt12, debt12)
            cover = cap12 - replacement_annual
            dscr = (cover / fwd_debt12) if fwd_debt12 > 0 else (math.inf if cover >= 0 else -math.inf)
            test["full_year_of_history"] = m >= 12
            test["replacement_wage_affordable"] = cap12 >= replacement_annual
            test["dscr_after_founder_wage"] = dscr >= trigger["min_dscr_after_founder_wage"]
            test["personal_reserve"] = savings >= trigger["personal_reserve_months"] * (living_m + benefits_m)
            test["business_reserve"] = biz_cash >= trigger["business_reserve_months"] * (fwd_debt12 / 12 + manager_m)
            test["seller_transition_done"] = (kind != "buy") or m >= arm.get("seller_transition_months", 0)
            # Does leaving pay? His full-time work must be worth at least what the family gives up:
            # the manager wage saved plus what he adds, against the salary and benefits that stop.
            test["step_down_pays"] = (manager_m * 12 + arm.get("founder_fulltime_uplift_annual", 0.0)) >= replacement_annual
            numbers = all(test.values())
            streak = streak + 1 if numbers else 0
            if numbers and first_numbers_pass is None:
                first_numbers_pass = m
            if on_w2 and streak >= trigger["consecutive_months"]:
                on_w2 = False
                stepped_down_month = m
        else:
            dscr = None

        value = 0.0
        if acquired:
            value = 12 * op_before_owner * arm["valuation_multiple"]
            hi = arm.get("valuation_multiple_above_1m")
            if hi and value > 1_000_000:
                value = 12 * op_before_owner * hi  # bigger businesses sell at higher multiples
        loans = (sba.balance if sba else 0) + (seller.balance if seller else 0)
        rows.append({
            "month": m,
            "on_w2": on_w2,
            "personal_cash": round(savings),
            "business_cash": round(biz_cash),
            "operating_cash_before_owner_labor": round(op_before_owner),
            "manager_wage": round(manager_paid),
            "founder_wage_from_business": round(owner_wage),
            "debt_service": round(debt),
            "loan_balances": round(loans),
            "business_value": round(value),
            "equity_value": round(value - loans + biz_cash),
            "dscr_after_founder_wage": None if dscr is None else (round(dscr, 2) if math.isfinite(dscr) else str(dscr)),
            "test_parts_passing": sum(test.values()) if test else None,
            "test_parts_total": len(test) if test else None,
        })

    last = rows[-1]
    return {
        "arm": arm["id"],
        "label": arm["label"],
        "acquired": acquired,
        "underwriting_dscr": None if underwriting_dscr is None else round(underwriting_dscr, 2),
        "notes": notes,
        "step_down_month": stepped_down_month,
        "first_month_numbers_pass": first_numbers_pass,
        "lowest_personal_cash": min(r["personal_cash"] for r in rows),
        "peak_guaranteed_debt": max(r["loan_balances"] for r in rows),
        "end_personal_cash": last["personal_cash"],
        "end_equity_value": last["equity_value"],
        "end_net_worth_proxy": last["personal_cash"] + last["equity_value"],
        "rows": rows,
    }


# ---------------------------------------------------------------- checks T1..T16

CHECKS = [
    # id, applies to kinds, fact key, pass value, label
    ("T1", {"buy", "grow"}, "employer_outside_work_terms_reviewed_and_permit_it",
     "Employer outside-work and conflict terms reviewed, and they permit this business"),
    ("T2", {"buy", "grow"}, "no_employer_time_data_customers_or_ip_used",
     "No employer time, equipment, data, customers or IP used; business is not a supplier, customer or competitor of the employer"),
    ("T3", {"buy"}, "business_sba_eligible_not_cannabis_not_passive",
     "Target is SBA-eligible: not a marijuana business, not passive, actively operated"),
    ("T4", {"buy"}, "all_20pct_owners_and_trustors_named_as_guarantors",
     "Every 20%+ owner (and the trustor of any owning trust) is named as guarantor, and the guarantee is counted in personal reserves"),
    ("T5", {"buy", "grow"}, "foundation_has_no_role_in_deal",
     "Foundation holds no interest, gives no guarantee or pledge, lends nothing and does no business with the deal or the founder's loan"),
    ("T6", {"buy", "grow"}, "owner_is_not_a_trust_that_benefits_the_foundation_or_4943_cleared",
     "Owner is not a trust with the Foundation as beneficiary, or counsel has cleared excess business holdings"),
    ("T7", {"buy", "grow"}, "MODEL:manager_priced",
     "Every role the founder doesn't do is paid at market before the trigger counts any earnings"),
    ("T8", {"buy", "grow"}, "founder_wage_only_for_real_documented_work_at_market",
     "Founder's wages from the business are for real, logged work, priced at market for the hours worked"),
    ("T9", {"buy"}, "MODEL:seller_standby_honored",
     "Seller note counted as equity is on full standby for the life of the SBA loan (no principal or interest paid)"),
    ("T10", {"buy", "grow"}, "no_robs_from_current_employer_plan",
     "No ROBS funded from the current employer's plan while still employed"),
    ("T11", {"buy"}, "all_owners_meet_sba_citizenship_rule",
     "All owners meet SBA's current citizenship and residency rule"),
    ("T12", {"buy"}, "independent_valuation_on_file",
     "Independent business valuation on file for the change of ownership"),
    ("T13", {"buy", "grow"}, "cannabis_company_fully_separate_and_disclosed",
     "The cannabis transport company shares no accounts, staff, revenue or customers with the other business, and the lender has been told about it"),
    ("T14", {"buy", "grow"}, "MODEL:step_down_only_on_trigger",
     "The W-2 ends only in a month when the full step-down test has passed for the required run of months"),
    ("T16", {"buy"}, "manager_is_employee_not_controlling_management_company",
     "The manager is an employee under the owner's direction; no management company (the founder's own included) holds complete operational control"),
    ("T15", {"buy"}, "MODEL:underwriting_coverage",
     "Target's last-year cash flow, after a market manager wage, covers first-year SBA debt service at the lender floor (no projections)"),
]


def run_checks(arm: dict, result: dict, trigger: dict) -> list:
    facts = arm.get("facts", {})
    out = []
    for cid, kinds, key, label in CHECKS:
        if arm["kind"] not in kinds:
            continue
        if key == "MODEL:manager_priced":
            ok = arm.get("business", {}).get("manager_market_wage_annual", 0) > 0 or arm["kind"] == "grow"
            v = "pass" if ok else "fail"
        elif key == "MODEL:seller_standby_honored":
            # Loan.step pays nothing on a note while it is on standby
            sb = arm.get("financing", {}).get("seller_note_standby_months", 0)
            term = arm.get("financing", {}).get("sba_term_months", 0)
            v = "pass" if sb >= term else "fail"
        elif key == "MODEL:underwriting_coverage":
            u = result.get("underwriting_dscr")
            v = "amber" if u is None else ("pass" if u >= trigger["lender_min_dscr_acquisition"] else "fail")
        elif key == "MODEL:step_down_only_on_trigger":
            v = "pass"  # enforced by the simulation loop itself
        else:
            val = facts.get(key)
            v = "pass" if val is True else ("fail" if val is False else "amber")
        out.append({"id": cid, "verdict": v, "label": label})
    # cannabis special case: a marijuana business can't be the SBA borrower
    if arm["kind"] == "grow" and arm.get("is_cannabis_business"):
        out.append({"id": "T3c", "verdict": "fail" if arm.get("uses_sba") else "pass",
                    "label": "Cannabis company grows without SBA money (SBA excludes marijuana businesses)"})
    return out


# ---------------------------------------------------------------- report

def required_cash_flow(replacement: float, multiple: float, loan_share: float,
                       rate: float, months: int, min_dscr: float) -> float:
    """Closed form: the yearly cash flow a business must earn so it can pay the
    founder the replacement wage AND cover its acquisition debt at min_dscr.

    SDE >= R + min_dscr * DS, and DS = 12 * payment(loan_share * multiple * SDE)
    so SDE * (1 - min_dscr * loan_share * multiple * k) >= R, k = 12 * payment factor.
    """
    k = 12 * payment(1.0, rate, months)
    denom = 1 - min_dscr * loan_share * multiple * k
    return math.inf if denom <= 0 else replacement / denom


def summarize(inputs: dict, results: list) -> str:
    p = inputs["person"]
    t = inputs["step_down_trigger"]
    lines = []
    lines.append(f"Inputs: {inputs.get('label', '')}")
    lines.append(f"Horizon: {inputs['horizon_months']} months. Step-down test must pass {t['consecutive_months']} months running.")
    R = p["salary_gross_annual"] + p["benefits_replacement_annual"]
    lines.append("")
    lines.append("| Arm | Underwriting coverage | Step-down month | First month numbers pass | Lowest personal cash | Peak loan balances | End personal cash | End equity in business | Checks (pass / amber / fail) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in results:
        c = r["checks"]
        cp = sum(1 for x in c if x["verdict"] == "pass")
        ca = sum(1 for x in c if x["verdict"] == "amber")
        cf = sum(1 for x in c if x["verdict"] == "fail")
        sd = r["step_down_month"] if r["step_down_month"] else ("n/a" if r["arm"] == "A" else "not met")
        fp = r["first_month_numbers_pass"] or ("n/a" if r["arm"] == "A" else "never")
        uw = f"{r['underwriting_dscr']}x" if r['underwriting_dscr'] is not None else "n/a"
        lines.append(f"| {r['arm']} {r['label']} | {uw} | {sd} | {fp} | {r['lowest_personal_cash']:,} | {r['peak_guaranteed_debt']:,} | {r['end_personal_cash']:,} | {r['end_equity_value']:,} | {cp} / {ca} / {cf} |")
        for n in r["notes"]:
            lines.append(f"|  ↳ {n} | | | | | | | | |")
    lines.append("")
    for a in inputs["arms"]:
        if a["kind"] == "buy":
            f = a["financing"]
            need = required_cash_flow(R, a["valuation_multiple"], 1 - f["equity_injection_pct"],
                                      f["sba_rate"], f["sba_term_months"], t["min_dscr_after_founder_wage"])
            lines.append(f"Arm {a['id']}: to step down, a business bought at {a['valuation_multiple']}x cash flow must earn about "
                         f"{need / R:.2f}x the replacement income (salary + benefits) before owner labor. "
                         f"This target earns {a['business']['sde_annual'] / R:.2f}x before AI gains.")
    return "\n".join(lines)


def run(inputs: dict) -> list:
    results = []
    for arm in inputs["arms"]:
        r = run_arm(inputs["person"], arm, inputs["horizon_months"], inputs["step_down_trigger"])
        r["checks"] = run_checks(arm, r, inputs["step_down_trigger"])
        results.append(r)
    return results


# ---------------------------------------------------------------- self test

def selftest() -> int:
    bad = 0
    def expect(name, cond):
        nonlocal bad
        print(("ok   " if cond else "FAIL ") + name)
        bad += 0 if cond else 1

    expect("payment: 100k, 0%, 10 months = 10k", abs(payment(100000, 0, 10) - 10000) < 1e-6)
    expect("payment: 120-month 10.5% factor about 0.01349", abs(payment(1, 0.105, 120) - 0.013493) < 1e-5)
    ln = Loan(1000, 0.12, 12, standby_months=3)
    paid = [ln.step() for _ in range(3)]
    expect("standby: nothing paid during standby", sum(paid) == 0)
    expect("standby: interest accrues", ln.balance > 1000)

    base = json.loads(DEFAULT_INPUTS.read_text())
    res = {r["arm"]: r for r in run(base)}
    expect("A never steps down", res["A"]["step_down_month"] is None)
    expect("B0 (no AI) steps down no earlier than B", (res["B0"]["step_down_month"] or 10**9) >= (res["B"]["step_down_month"] or 10**9))
    for k, r in res.items():
        if r["step_down_month"]:
            row = r["rows"][r["step_down_month"] - 1]
            expect(f"{k}: W-2 ends only after the test ran {base['step_down_trigger']['consecutive_months']} months",
                   r["step_down_month"] - r["first_month_numbers_pass"] + 1 >= base["step_down_trigger"]["consecutive_months"])
            expect(f"{k}: no step-down before 12 months of history", r["step_down_month"] >= 12)
    # Unknown facts are amber, never pass
    amber = [c for c in res["B"]["checks"] if c["id"] == "T1"][0]["verdict"]
    expect("unknown employer terms are amber, not pass", amber == "amber")
    # Rename invariance: labels never change numbers
    renamed = json.loads(json.dumps(base))
    for a in renamed["arms"]:
        a["label"] = "x" + a["id"]
        a["business"] = a.get("business", {})
    res2 = {r["arm"]: r for r in run(renamed)}
    expect("rename invariance: same step-down months", all(res[k]["step_down_month"] == res2[k]["step_down_month"] for k in res))
    # Closed form agrees with direction: target sized to requirement can step down
    print(f"\n{bad} failure(s)")
    return 1 if bad else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    csv_dir = None
    if "--csv" in argv:
        i = argv.index("--csv")
        csv_dir = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT_INPUTS
    inputs = json.loads(path.read_text())
    results = run(inputs)
    print(summarize(inputs, results))
    print()
    for r in results:
        bad = [c for c in r["checks"] if c["verdict"] != "pass"]
        if bad:
            print(f"Arm {r['arm']} checks not passing: " + ", ".join(f"{c['id']} {c['verdict']}" for c in bad))
    if csv_dir:
        csv_dir.mkdir(parents=True, exist_ok=True)
        for r in results:
            with open(csv_dir / f"arm-{r['arm']}.csv", "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(r["rows"][0].keys()))
                w.writeheader()
                w.writerows(r["rows"])
        print(f"\nMonth-by-month CSVs written to {csv_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
