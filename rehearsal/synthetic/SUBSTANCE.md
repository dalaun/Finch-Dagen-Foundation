# Substance at every step, and the tool map

[Back to the synthetic year](README.md) · [Declared plans](DECLARED-PLAN.md) · [Counsel queue](counsel-queue.md)

**SYNTHETIC.** Roles only, placeholder amounts, no real names or accounts. Design and education, not legal or tax advice.

## The rule

Every route declares its non-tax purpose in writing before its first step. Then every step has to change something real apart from tax: who owns, risks, controls or is owed what. A step whose only effect is a tax result fails on the day it happens. This works the same way as the keystone constraint and the accountable plan: the route has to hold at every step, not only at the end.

Two layers run on each route:

1. **The tool's own test.** This is the section of the Code or the trust statute the route relies on, such as 119's business premises or 127's limit on owners. It answers whether the tool fits the facts at all (SB6).
2. **The substance doctrines on top.** Economic substance (7701(o)) and substance over form. These answer whether the route is real even when the tool's words fit (SB0 to SB5).

A route can pass its tool's test and still fail substance, as the circular loans do. It can also pass substance and fail its tool, as the education plan does while the founder is the only employee.

`substance.py` runs 19 synthetic routes. `--as-of` judges any route as it stood on a given day. The circular loans fail on their first step, February 1, not at year end.

## What was read (2026-11-26)

- **7701(o)(1):** "In the case of any transaction to which the economic substance doctrine is relevant, such transaction shall be treated as having economic substance only if —" (A) "the transaction changes in a meaningful way (apart from Federal income tax effects) the taxpayer's economic position," and (B) "the taxpayer has a substantial purpose (apart from Federal income tax effects) for entering into such transaction." These come from register A1 and the Solicitor General's 2019 brief in Tucker v. Commissioner, No. 19-41.
- **7701(o)(5)(B):** "In the case of an individual, paragraph (1) shall apply only to transactions" "entered into in connection with a trade or business or an activity engaged in for the production of income."
- **7701(o)(5)(C):** "The determination of whether the economic substance doctrine is relevant to a transaction shall be made in the same manner as if this subsection had never been enacted."
- **7701(o)(5)(D):** "The term "transaction" includes a series of transactions."
- **Patel v. Commissioner, 165 T.C. No. 10 (2025):** the Tax Court held "that the codified economic substance doctrine requires a relevancy determination". It said that "Conflating the relevancy determination with the two–part test would ignore that direction". It sustained the 6662(b)(6) penalty, and the 40% rate for two of the years.
  - A federal district court in Colorado reached the opposite view on relevance in Liberty Global (D. Colo., Oct. 31, 2023).
  - Source: The Tax Adviser, Feb 28, 2026, https://www.thetaxadviser.com/issues/2026/feb/penalties-under-codified-economic-substance-doctrine-upheld/. The (o)(5) quotes are that article's quotes of the statute, not the official text.
- **IRS Notice 2010-62,** https://www.irs.gov/pub/irs-drop/n-10-62.pdf: "The Treasury Department and the IRS do not intend to issue general administrative guidance" on "the types of transactions to which the economic substance doctrine either applies or does not apply." So there is no IRS list of safe routes.
- **IRC 6664(c)(2),** https://www.law.cornell.edu/uscode/text/26/6664: the reasonable-cause defense "shall not apply to any portion of an underpayment" "attributable to one or more transactions described in section 6662(b)(6)". The 20% and 40% rates are in register A1 (6662(b)(6), (i)).
- **NOT READ:** 7701(o)(2) (profit potential), (o)(3) (state and local tax) and (o)(4) (financial accounting). A route whose purpose is one of these stays amber.

## The checks

| Check | Test | Authority |
|---|---|---|
| SB0 | Relevance. The doctrine has nothing to deny when there is no federal tax benefit. It doesn't reach an individual's personal transaction. Everything else is treated as relevant, the cautious reading | 7701(o)(1), (o)(5)(B), (o)(5)(C); Patel; ASSUMPTION, Q45 |
| SB1 | Non-tax purpose written and dated before the first step | 7701(o)(1)(B); timing ASSUMPTION, Q46 |
| SB2 | Step invariant: every step so far changes something real apart from tax | 7701(o)(1)(A), (o)(5)(D); per-step ASSUMPTION, Q47 |
| SB3 | Collapse the steps. The end state changes the economic position, and isn't the founder's living costs paid with untaxed money | 7701(o)(1)(A), (o)(5)(D); Court Holding (register A3) |
| SB4 | The declared purpose is an effect the steps actually produced. Amber if the purpose is a state-tax or accounting benefit | 7701(o)(1)(B); (o)(3), (o)(4) NOT TRACED |
| SB5 | Form follows substance. The arrangement follows its own terms, and a transfer really changes the old owner's relationship to the property | Notice 97-24; Markosian (register A2) |
| SB6 | The tool's own test, from its trace | the route's tool |

When a relevant route fails SB2, SB3 or SB4, the tax benefit is denied. A 20% penalty applies, 40% if the route wasn't disclosed, and there is no reasonable-cause defense. Amounts are placeholders.

Holding each step is stricter than the statute, which judges the transaction and lets a series count as one (Q47). It is never looser.

## The tool map

The accountable plan is one tool. A cafeteria plan is not inside it. They are separate tools in the company family:

- **Accountable plan (62(c)):** repays costs the employee fronted for the job.
- **Cafeteria plan (125):** lets the employee choose between cash and benefits such as health coverage (106) or dependent care (129), before tax.
- **Health reimbursement (105(b)):** repays medical costs under the health plan.

| Family | Route | Tool | Tool's own test | Substance |
|---|---|---|---|---|
| Company | Reimburse job costs | 62(c), Reg. 1.62-2 | pass (DECLARED-PLAN.md) | pass |
| Company | Health coverage | 105(b), 106(a) | pass: C corporation employee | pass |
| Company | Housing and meals at his home | 119(a) | fail: not the employer's premises | fail: living costs untaxed |
| Company | Choose cash or benefits | 125 | amber: NOT TRACED | pass |
| Company | Courses | 127 | fail: sole employee and owner | pass |
| Company | Child care | 129 | amber: owner limit not read | pass |
| Company | Business vehicle use | 132(d) | pass, with a log | pass |
| Company | Retirement | 401(a), 401(k) | pass | pass |
| Trust | Creditor protection | 760 ILCS 3/502 spendthrift | pass | no tax benefit, so it doesn't apply |
| Trust | Governing law, place of administration | 760 ILCS 3/107, 108 | pass | doesn't apply |
| Trust | Privacy with banks | 760 ILCS 3/1013 certification of trust | pass | doesn't apply |
| Trust | Non-grantor status | 674(c) independent trustees | pass | pass |
| Foundation | Pay for program work | 4941(d)(2)(E) | pass | pass |
| Foundation | Grant to a non-charity partner | 4945(h) | pass | pass |
| Gift and estate | Annual gift to the trust | 2503(b) | amber: present interest not traced | doesn't apply (personal transaction) |
| Gift and estate | Sale to the trust at full value | 2512(b), the reverse case | pass | no tax benefit |
| Gift and estate | Hold the rental until death | 1014(a) | pass | pass |
| Built to fail | Circular loans in the stack | 163 interest | fail (spec K27) | fail from the first step |
| Built to fail | Gift to a dying relative and back | 1014(e) | fail | fail |

## The promises with no route

The promise map (PROMISE-MAP.md on branch claude/project-thread-hpjad5, traced in its packet/research/Q40.md) has five "no route" rows. Next to each is the nearest lawful tool. The nearest tool doesn't deliver the promise as written. It delivers the part that has a route.

| Promise | Why there's no route | Nearest lawful tool |
|---|---|---|
| Food, everyday clothing | Personal living costs (262(a)) | Meals on the employer's premises for its convenience (119, narrow). Uniforms not suited to street wear, bought by the employer (132(a)(3), Pevsner; register F4) |
| Any company benefit paid by the Foundation instead | Self-dealing (4941(d)(1)(E)) | Reasonable pay for real program work (4941(d)(2)(E)) |
| Secrecy from beneficiaries | The trustee must tell qualified beneficiaries the trust exists (760 ILCS 3/813.1) | Certification of trust for banks and title companies (760 ILCS 3/1013) |
| Rejecting courts' authority | No statute read allows it | Governing-law and place-of-administration clauses (760 ILCS 3/107, 108) |
| Untaxed units; setting its own taxes or money | No statute read allows it | None found |

## Run it

```
python3 substance.py                    # all 19 routes
python3 substance.py --as-of 2026-02-01  # each route as it stood that day
python3 substance.py --selftest          # 17 cases
```

Run on 2026-11-26: 7 checks per route, 133 verdicts in total: 117 pass, 3 amber, 13 fail. The fails are in the two routes built to fail, plus the 119 housing route and the 127 education route, which fail for real reasons.
