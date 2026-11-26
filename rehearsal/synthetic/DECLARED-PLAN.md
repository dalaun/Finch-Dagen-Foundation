# Declared plans

[Back to the synthetic year](README.md) · [Counsel queue](counsel-queue.md)

**SYNTHETIC.** Roles only, placeholder amounts, no real names or accounts. Design and education, not legal or tax advice.

## The pattern

Several parts of the tax code work the same way. You declare in advance what you will do. You do it. You prove each step with records made at the time. You reconcile what happened against what you declared. If the arrangement fails, the same money is taxed or penalized as something else.

A useful comparison is a regulator that accepts the plan you file and then holds you to it. The tests reward following your own declared plan, with traceable records, not just landing on a defensible answer after the fact.

`declared_plan.py` models this once and runs four instances of it. Each check names its authority. Where the text was not read, the check says ASSUMPTION or NOT TRACED and points to the counsel queue.

| Instance | Declared up front | Proved by | Reconciled by | If it fails |
|---|---|---|---|---|
| Accountable plan (Reg. 1.62-2) | Written plan: covered lines, 60-day substantiation, 120-day return of excess | Receipts and logs per payment | Advances against substantiated expenses | Reimbursements become wages |
| Foundation reimbursement (Reg. 53.4941(d)-3(c)(1)) | Expense policy tied to a program | Records under the policy | Amount against a benchmark | Tested as self-dealing |
| Expenditure responsibility (IRC 4945(h)) | Grant purpose in writing | Grantee reports | Spending against the purpose; report to the IRS | Taxable expenditure |
| Exemption narrative (Form 1023) | Activities described in the application | Program records | Activities against the narrative | NOT TRACED (Q43) |

What this does not do: it doesn't fund a program or close the asset to program gap. An accountable plan lowers the founder's taxable pay from the management company; it moves no money to the Foundation.

## The first instance: the management company's accountable plan

The management company (a C corporation) reimburses the founder, its employee, for a home office, business mileage and the business share of a phone. Three synthetic runs: a clean year, a badly run year, and a year where failure is the routine.

Quotes, Treas. Reg. 1.62-2, read 2026-11-26 at https://www.law.cornell.edu/cfr/text/26/1.62-2 (Cornell LII reproduction; not checked against the official eCFR):

- Business connection, (d)(1): an arrangement "provides advances, allowances" ... "reimbursements only for business expenses" ... "that are paid or incurred by the employee in connection with the performance of services as an employee of the employer."
- Substantiation, (e)(1): "it requires each business expense to be substantiated to the payor" ... "within a reasonable period of time".
- Return of excess, (f)(1): it requires the employee to return "within a reasonable period of time" any amount "in excess of the expenses substantiated in accordance with paragraph (e) of this section." (The LII page prints "may amount" for "any amount".)
- Reasonable period, (g)(1): "The determination of a reasonable period of time will depend on the facts and circumstances."
- Fixed date method, (g)(2)(i): "An advance made within 30 days of when an expense is paid or incurred," "an expense substantiated to the payor within 60 days after it is paid or incurred," "or an amount returned to the payor within 120 days after an expense is paid or incurred will be treated as having occurred within a reasonable period of time."
- Failing the tests, (c)(3)(i): "If an arrangement does not satisfy one or more of the requirements of paragraphs (d), (e), or (f) of this section," "all amounts paid under the arrangement are treated as paid under a "nonaccountable plan.""
- What that means, (c)(5): such amounts "are included in the employee's gross income," "must be reported as wages or other compensation on the employee's Form W-2," "and are subject to withholding and payment of employment taxes".
- Pattern of abuse, (k): "If a payor's reimbursement or other expense allowance arrangement evidences a pattern of abuse of the rules of section 62(c) and this section, all payments made under the arrangement will be treated as made under a nonaccountable plan."

Other quotes used are already in [../01-instrument-register.md](../01-instrument-register.md): B4 (accountable plan; a disregarded owner can't use one), B5 (274(d) records), 280A(c)(1) and (c)(6) (an employee's home office needs the employer's convenience; renting the home to the employer closes it).

| Check | Test | Authority |
|---|---|---|
| DP0 | Plan written and dated before the first payment | ASSUMPTION, Q39 |
| DP1 | Declared terms inside the 30/60/120-day method (amber if longer) | 1.62-2(g)(1), (g)(2)(i) |
| DP3 | No amendment reaches back: each payment is held to the terms in force the day it was paid | ASSUMPTION, Q44 |
| AP0 | The person reimbursed is the payor's employee | 1.62-2(d)(1); register B4 |
| AP1 | Business connection; home office also needs the employer's convenience and no rental to the employer | 1.62-2(d)(1); 280A(c)(1), (c)(6) |
| AP2 | Substantiated within the declared period, with the records the line needs | 1.62-2(e)(1), (g)(2)(i); 274(d) |
| AP3 | Advances no more than 30 days before the expense | 1.62-2(g)(2)(i) |
| AP4 | Excess returned within the declared period | 1.62-2(f)(1), (g)(2)(i) |
| DP2 | Step invariant: on every day so far, nothing is past its deadline. Open items inside their window are allowed | 1.62-2(g)(2)(i) |
| AP5 | No pattern of abuse (half or more of payments failing is a pattern) | 1.62-2(k); ASSUMPTION, Q38 |
| DP4 | Early drift: the first broken payment is flagged as risk to the whole plan, dated, with the day the share reached the threshold | 1.62-2(k); threshold ASSUMPTION, Q38 |

### True at every step, not only at year end

The plan has to hold the whole way, the same way the keystone constraint is checked at every step rather than only at the finish. Three rules, checked against the 1.62-2 text above:

- **Nothing overdue, not everything closed.** On any day, a receipt or an excess still inside its 60-day or 120-day window is fine. The plan breaks the day after a deadline passes with the item still open (DP2). This is the fixed date method, (g)(2)(i). `--as-of` judges the year as it stood on any day: the badly run plan is clean on March 15 and first breaks on April 2.
- **Order.** The plan exists before the first payment (DP0) and an amendment counts only from the day it's adopted, so it can't be written later to cover a payment already made (DP3). The regulation read doesn't speak to either point in words, so both are ASSUMPTION (Q39, Q44). Even an amendment adopted in time can't stretch a term past the 60/120-day caps.
- **Drift is plan-level risk.** Under (k) a pattern makes every payment wages, so the first break is flagged against the whole arrangement (DP4, amber), not only against that payment. In the badly run plan the drift starts April 2 and the share reaches the threshold on June 11.

Reconciling: when AP0 or AP5 fails, every payment is wages ((c)(3)(i), (c)(5), (k)). When one payment fails under a plan that otherwise holds, the rehearsal counts only that payment as wages (ASSUMPTION, Q40). The added tax uses placeholder rates, not anyone's brackets.

## Where the same shape repeats

- **Foundation reimbursement**, IRC 4941(d)(2)(E) and Reg. 53.4941(d)-3(c)(1) (register D2): "the payment of compensation (and the payment or reimbursement of expenses)" ... "for personal services which are reasonable and necessary to carrying out the exempt purpose of the private foundation" ... "shall not be an act of self-dealing if the compensation (or payment or reimbursement) is not excessive". Checks FR1 (tied to a named program), FR2 (not excessive against a benchmark), FR3 (approved without the payee's vote) and FR4 (substantiated under the declared policy). FR3 and FR4 are design controls, not the regulation's words (ASSUMPTION, Q41).
- **Expenditure responsibility**, IRC 4945(h) (traced in [packet/research/Q35.md](packet/research/Q35.md)): the foundation must "see that the grant is spent solely for the purpose for which made, (2) to obtain full and complete reports from the grantee on how the funds are spent, and (3) to make full and detailed reports with respect to such expenditures to the Secretary." A grant without it is a taxable expenditure under 4945(d)(4)(B). Checks ER0 (not needed for a public charity grantee), ER1 (purpose in writing first: ASSUMPTION, Q42, Reg. 53.4945-5 not traced), ER2 to ER4 (the three duties).
- **The Form 1023 narrative**, IRC 508(a) and Reg. 1.508-1(a)(2)(i) (register D11): notice is "a properly completed and executed Form 1023" "within 15 months from the end of the month in which the organization was organized". Check EX1 traces to that. EX2 (activities stay inside the narrative) and EX3 (changes reported) are NOT TRACED: the rehearsal has read no text that says what drifting from the narrative costs (Q43). They stay amber until it is read.

## Run it

```
python3 declared_plan.py              # every plan in declared-plan-synthetic.json
python3 declared_plan.py --selftest   # 20 cases
python3 declared_plan.py --as-of 2026-04-02   # the year as it stood that day
python3 declared_plan.py --json out.json
```

Run on 2026-11-26: 23 distinct checks (11 on the accountable plan, 12 across the three Foundation instances, ER0 only when the grantee is a public charity); the synthetic plans give 44 verdicts, 30 pass, 5 amber, 9 fail. The fails are all in the two plans built to fail.
