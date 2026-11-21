# The IRS publications as instruments

**Status:** read 2026-11-21 on irs.gov. Roles only. **Not legal or tax advice.** A publication explains the law; the Code and regulations are the law, and counsel decides how they apply to the real documents.

## The perspective shift

A publication is the IRS's own user manual for a set of instruments. It doesn't tell you what you're "allowed to get away with". It tells you which doors exist, what key opens each one, and who is standing on the wrong side of it. The same door that is open to an employee of a corporation is closed to the owner of a partnership. So the question is never "can I deduct this?" It is "which role am I in when this money moves, and does that role hold the key?"

That is also the executive-package lesson from public company proxies. Nothing there is creative in the sense of hidden. The company deducts the pay as an ordinary business expense. The executive pays tax on it unless a specific law excludes it. The proxy discloses both. The "creativity" is choosing pay in forms the law already excludes, at amounts the law allows, and keeping the records.

[01-instrument-register.md](01-instrument-register.md) reads the Code sections as instruments. This page does the same for the publications, and `decision/irs-instruments.ttl` records each one in RDF, linked to the roles and to the check its red flag became.

## Which publications are current

| Instrument | Edition | Status |
|---|---|---|
| Pub 15-B, fringe benefits | 2026 | Current |
| Pub 15 (Circular E) | 2026 | Current |
| Pub 15-A | 2026 | Current |
| Pub 334, small business | 2025 | Current |
| Pub 463, travel, gift and car | 2025 | Current |
| Pub 587, business use of home | 2025 | Current |
| Form 7206 instructions | 2025 | Current |
| Pub 525, taxable and nontaxable income | 2025 | Current |
| Pub 946, depreciation | 2025 | Current |
| Pub 526, charitable contributions | 2025 | Current |
| Pub 561, valuing donated property | Rev. 12/2025 | Current |
| Pub 557, tax-exempt status | Rev. 01/2025 | Current |
| Form 1041 instructions | 2025 | Current |
| Pub 538, accounting periods and methods | Rev. 01/2022 | Edition seen; whether it's still current not confirmed |
| Pub 4221-PF, private foundation compliance | Rev. 08/2014 | Listed; PDF not opened |
| Pub 535, business expenses | 2022 | **Discontinued.** "We have discontinued Publication 535, Business Expenses; the last revision was for 2022." Its content moved to the IRS business expense guide page, Pubs 334, 463 and 587, and Form 7206 |

## The four routes a typical household misses

1. **Be an employee of a corporation, not an owner of a pass-through.** Pub 15-B excludes health coverage, cafeteria plan choices, group-term life up to $50,000 of coverage and dependent care up to $7,500 (2026), but only for "A current common-law employee". A 2% S corporation shareholder is treated "as you would a partner", and the value goes in wages. So a management company taxed as a C corporation, with the founder as its employee, holds keys an S corporation or LLC owner does not. The owner's fallback is the Form 7206 deduction for health premiums. *Read in 15-B and the 7206 instructions. That a plan with the founder as its only participant fails the key-employee test is inferred.*
2. **Price everything between your roles from comparables, and write it down.** Reasonable pay is deductible (162(a)(1)), and it is the only pay the foundation may give an insider (4941, "not excessive"). Deals between your own companies are policed by 482. A market range from peer foundations' 990-PF Part VII, an external-manager disclosure or a survey, with written terms and an independent reviewer, turns the fee and the pay into something you can defend. *Statutes read; the comparable sources are partly inferred.*
3. **Take the elections.** Equipment can be deducted this year under section 179 ($2,560,000 limit for tax years beginning in 2026, Pub 946) instead of over years. Start-up costs of a new or acquired business get up to $5,000 at once and the rest over 180 months under 195(b), but only on election. *Read.*
4. **A home office through administration, not a mailing address.** Pub 587 counts a room used only and regularly for "administrative or management activities" when there is "no other fixed location" for that work. A home that is only an entity's mailing address doesn't qualify (inferred; 587 doesn't speak to mailing addresses). *Read, except the mailing-address point.*

And one that stays closed: a trust passes income, and its tax, to beneficiaries through distributions limited to distributable net income, but "Trusts can't be used to transform a taxpayer's personal, living, or educational expenses into deductible items" (1041 instructions, read).

## The catalog: permission, keyholder, red flag, check

| Instrument | Permits | Keyholder | Red flag | Becomes check | Evidence |
|---|---|---|---|---|---|
| 15-B health and cafeteria plan | exclude coverage and plan choices | common-law employee of the management company, operating company or foundation | owner claims an employee exclusion; plan favors key people | FX1, FX2, FX3, ST1b | read |
| 15-B group-term life | exclude cost up to $50,000 coverage | employee | coverage above the line left out of wages | FX2, FX3 | read |
| 15-B dependent care | exclude up to $7,500 (2026) | employee | over the limit | FX2, FX3 | read |
| 15-B working condition | tax-free mileage at the cents-per-mile rate | employee | flat allowance called a reimbursement; no log | FX0, FX4 | read; allowance text inferred |
| 15-B lodging (119) | exclude lodging on business premises | employee (not a 2% shareholder) | the home called business premises | FX5 | read |
| 7206 instructions | deduct health premiums | self-employed, partner, 2% shareholder | a month with an employer plan open | FX1 | read |
| 334 and 162 | deduct ordinary, necessary and reasonable pay | the companies and trusts, not the foundation | personal costs, capital costs | BD1, BD2, BD3, ST1a | statute read |
| 463 | travel, 50% meals, mileage | companies, employees, self-employed | no records | FX4, BD1 | read |
| 587 | home office | the founder as self-employed (individuals only) | mixed use; mailing address only | BD6 | read |
| 538 | cash or accrual timing | companies, trusts, self-employed | deduction before payment to a related party | BD5 | read |
| 946 | section 179, bonus depreciation | companies, self-employed | repair label on a capital item | BD3 | read |
| 195 (statute) | start-up cost election | companies, self-employed | deduction without the election | BD4 | statute read |
| 525 | leave excluded benefits out of income | employee | a benefit no law excludes | FX0 | read |
| 15 | family wages; payroll-tax relief for a minor child in an unincorporated business | self-employed, companies | wages for no real work | ST1a, AL1b | summary only |
| 15-A | worker status; officers are employees | companies, foundation | owner treated as an employee where the law says partner | FX1 | summary only |
| 561 | fair market value | every role | a price not set by a willing buyer and seller | AL1a, AL1b | read |
| 526 | charitable deduction | the founder, the family trust | gifts that make the trust a substantial contributor (rehearsal/09) | AL1a | read in part |
| 557 | operating foundation status | foundation | | | table of contents only |
| 1041 instructions | distribution deduction to DNI | family trust, business trust, trustee | personal costs run through a trust | BD2 | read |
| 4221-PF | foundation compliance | foundation | | | not opened |

## Not verified

- Pub 538's current status, Pub 4221-PF's text, and Pub 15, 15-A and 557, which were seen only as summaries or tables of contents.
- Pub 334's cash and accrual sections, Pub 463's commuting section, 15-B's text on cash allowances and on lodging.
- The 2026 standard mileage rate (not yet published when read).
- Pub 526's limits for gifts to a private nonoperating foundation.
- 280A, 1372, 318, 267 and 1.162-7, named but not read.
- Third-party links in the Pub 535 summary were treated as leads only.

## How it's built

`decide_spend.py` loads the catalog with the model and checks that every permission points at a check that exists and carries an evidence grade. A permission with a missing check or no evidence grade fails the run.
