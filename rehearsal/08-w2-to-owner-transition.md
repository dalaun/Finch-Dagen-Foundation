# 08. From W-2 income to business owner: the transition, rehearsed

[Back to the rehearsal overview](README.md)

**Status:** design, proposed 2026-11-20. Runs on synthetic inputs only. Nothing here applies for a loan, contacts a seller or employer, or moves money.

**This is design and education, not legal, tax or lending advice.** Every number in this repository is a placeholder. The founder's real inputs live in the private project folder.

## Where this fits

The rehearsal's main finding was that the stack only pays once it holds an income-producing asset, and that the single best structural fix is an ordinary business entity paying the founder market wages. A business bought or grown while the founder keeps his W-2 is that asset and that entity. This file is the bridge: how to get the asset without giving up the salary first, and the test that says when the salary can stop.

The founder's own framing, treated as assumptions to test:

1. Buying a business is the best way to start. **Partly holds.** It is the fastest way to an earning asset, but only for a business big enough (see the size rule below). A small one can't replace the salary.
2. A thinking system like Northstar can be the value add that makes a business worth buying in the AI era. **Holds, with a condition.** Buyers pay for AI only through earnings ("AI's value to a buyer comes through stronger earnings rather than as a feature in its own right," BizBuySell Insight Report, Q3 2026). So the method has to show up as margin, measured before and after. And it must be provably his, not his employer's (check T2).
3. The W-2 is something to escape. **Doesn't hold.** The W-2 is the plan's collateral: it carries the founder's living costs while the business repays its loan, and it is part of what a lender weighs. It ends only on a measured trigger.

## The scenario in the twin

[`transition_twin.py`](transition_twin.py) runs each arm month by month over the same founder and the same six years. It tracks personal cash, business cash, debt service, wages paid to the founder, reserves, loan balances and the business's value, applies the step-down test every month, and runs the red-flag checks below. Standard library Python only.

```
python3 transition_twin.py                       # synthetic inputs, summary table
python3 transition_twin.py my-inputs.json        # the founder's private inputs
python3 transition_twin.py --csv out_dir         # month-by-month CSV per arm
python3 transition_twin.py --selftest            # built-in cases
```

| Arm | What it rehearses |
|---|---|
| A | Stay on the W-2 only. The baseline every other arm is scored against. |
| Bm | Buy a business the size of the Chicago median sale, keep the W-2, a manager runs it. |
| B | Buy a business just under the step-down size, keep the W-2, add AI margin gains. |
| B0 | The same purchase as B with no AI gain. The gap between B and B0 is what the AI work is worth. |
| C | Grow the transport company first, self-funded (SBA money is not available to it). The same arm, with the cannabis flag off, stands in for growing the government-contracting company. |

### What the synthetic run shows

Placeholders: a W-2 founder whose replacement income (salary plus the benefits he would have to buy) is 120 units, business sizes from public BizBuySell medians, rates from no particular lender. The **pattern** is the finding, not the numbers.

| Arm | Lender coverage at close | Step-down month | Result |
|---|---|---|---|
| A | n/a | never (by design) | Savings grow slowly; no asset. |
| Bm | 1.59x | not met in 6 years | The loan pays, but the business can never pay him a replacement wage. |
| B | 1.69x | 25 | AI margin gain lifts it over the size line; the W-2 ends in year three. |
| B0 | 1.69x | not met | Same business without the AI gain never clears the trigger. |
| C | n/a | 65 | No debt and no guarantee, but five years to the trigger, and the founder funds growth from savings. |

Four findings come out of it:

1. **The size rule.** For the founder to leave, the business must earn, before any owner labor, about **1.8 times his replacement income** (salary plus benefits). At a 2.49x purchase multiple (the Chicago 2025 average), 90% financed over ten years at a placeholder 10.5%, and 1.25x coverage after paying him, the closed form is `cash flow >= replacement / (1 - 1.25 x 0.9 x multiple x yearly debt factor)`. The twin prints this for every buy arm. A Chicago-median business (BizBuySell 2025 closed sales: cash flow $128,618 at a 2.49 average multiple) sits well under that line for a six-figure earner.
2. **AI decides the marginal deal.** A business just under the line, plus a few points of margin from automating its back office, clears it; the same business without that gain never does. The gain also compounds into value: cash flow times the multiple, and BizBuySell's Q3 2026 averages put businesses over $1 million at 3.73x cash flow against 2.30x below it, so margin that pushes a business over that size is worth more than its own dollars.
3. **Leaving has to pay on its own.** Staying on the W-2 while a paid manager runs the business usually beats stepping down, because the family gives up a salary and benefits to save one manager's wage. The step-down only pays when the manager wage saved plus what the founder adds full-time is at least the salary and benefits that stop. The twin makes this a test part (`step_down_pays`), and "what I add full-time" is the input the founder has to evidence.
4. **Growing what he has is slower and safer.** No personal guarantee and no equity check, but no outside money either, and the transport company's growth comes out of savings. Whether that beats buying depends almost entirely on the growth rate, which is the least-known input in the model.

## Buy versus build

| | Buy a business, keep the W-2 | Grow the transport company first | Grow the government-contracting company first |
|---|---|---|---|
| Earning asset | On day one | After growth | After awards |
| Needs | Cash for about 10% of the price plus closing and reserves; a business about 1.8x his replacement income; a manager in place; employer clearance | Capital from savings; time; separate books from everything else | Bids, past performance, compliance cost; possibly an SBA working-capital loan |
| SBA money | Yes, if the target is eligible | **No.** SBA treats a business that "grows, produces, processes, distributes, or sells marijuana" as ineligible (SOP 50 10 8, ch. 1). A licensed transporter likely reads as distribution (inference; confirm). | Possibly, if eligible. A management agreement giving a company "sole discretion over the business operations" makes a passive, ineligible business (SOP 50 10 8, ch. 1), which matters because a management company runs it today |
| Risks | Personal guarantee on most of the price; customer or key-staff loss after the sale; seller transition | Federal illegality of cannabis (banking, tax: ask whether IRC 280E reaches a transporter); state licensing; no outside capital | Lumpy awards; compliance (CMMC) cost before revenue |
| Fits the stack | It becomes the ordinary business entity paying market wages the rehearsal called for | Must stay fully walled off from any acquisition (check T13) | Already the operating company; the management structure needs the T16 look before any SBA loan |

**Recommendation:** prepare to buy, and keep the existing companies on a no-new-capital footing until the purchase is sized. Savings are the binding constraint: the same cash can be an SBA equity injection that controls a business many times its size, or slow self-funded growth. The twin shows the purchase reaching the trigger years sooner, provided the target is big enough and the margin gain is real. That is a placeholder result; the founder's own inputs decide it.

## Financing for a buyer who keeps a W-2

**Source note.** SOP 50 10 8.1 took effect October 1, 2026 (SBA Information Notice 5000-880695, read on SBA's page). SBA's PDF of the SOP refused automated reads, so the 8.1 points below come from lender and law-firm commentary, marked with their source, and must be confirmed against the SOP or a lender's term sheet before anyone relies on them. No copy or mirror of the SBA file was used.

### SBA 7(a), change of ownership

- **Equity injection:** at least 10% for an initial acquisition. The 8.1 text, as quoted on Searchfunder: "For Initial Acquisitions, the required equity injection cannot be reduced or eliminated." Cash counts if it is not borrowed. (Whiteford, May 6, 2025: "require at least 10 percent equity injection from the buyer.")
- **Seller note:** can supply up to half of the injection only if it is "subordinated to the Lender and on full standby" with "no payments of principal or interest for the term of the 7(a) loan" (8.1 text quoted on Searchfunder; same rule under SOP 50 10 8 per Whiteford and Windsor Advantage). The twin keeps that note on standby for the whole loan term (check T9).
- **Coverage:** for initial acquisitions the debt-service coverage floor "rises from 1.15x to 1.25x," and lenders "may not rely on" post-closing projections to meet it (MMCG, September 6, 2026). The twin's T15 uses last year's cash flow after a market manager wage.
- **Valuation:** "an independent Qualified Source valuation ... on every change of ownership" (MMCG). BizBuySell's Q3 2026 report says the same rule took effect October 1. Check T12.
- **Seller transition:** "Seller consulting after a full exit may now run up to 24 months in aggregate, up from 12" (MMCG). Partial and phased buyouts are restricted ("Multi-step partial changes of ownership remain ineligible," MMCG).
- **Guarantees:** 20%+ owners guarantee; for trusts, "the trustor should also provide a guaranty" (Starfield & Smith, July 2026), and "holding companies, trusts, and limited partnerships are aggregated for the ownership and guarantor tests" (MMCG). **Owning through a trust does not remove the founder's personal guarantee.** Check T4.
- **Citizenship:** SBA's March 2026 policy limits 7(a) financing to businesses owned by U.S. citizens and nationals (American Banker, February 4, 2026; SBA news release 26-35). Check T11 reads the fact.
- **Absentee or semi-absentee owner:** no source read says the owner must work in the business. Lenders weigh "experience of management" (Starfield & Smith, 2025), and a management company with "complete operational control" is prohibited (Whiteford). So the safe shape is a hired general manager who is an employee under the owner's direction. Check T16.
- **Buyer demand:** 78% of buyers surveyed expect to use SBA financing (BizBuySell, Q3 2026), so the founder competes with many SBA buyers; the edge has to be operational, not financial.

### Seller financing

The seller's note is the cheapest part of the capital stack and the strongest signal: a seller who carries paper believes the cash flow. Inside an SBA deal it must sit on full standby to count as equity; outside one, terms are open. Either way the twin treats it as debt the business carries.

### ROBS (retirement funds into a new C corporation)

- The IRS says ROBS plans are "not considered an abusive tax avoidance transaction" but "are questionable because they may solely benefit one individual" (IRS ROBS compliance project page). The structure requires a new C corporation whose plan buys its stock. Its findings: missing Form 5500 filings (the one-participant exception "does not apply to a ROBS plan"), stock valuation, missing Form 1099-R, plan amendments that shut later employees out, and businesses that "either failed or were on the road to failure."
- **The current employer's 401(k) is likely out of reach while he works there.** Elective deferrals "cannot be made until" severance, plan termination, age 59½ or hardship, and "Hardship distributions cannot be rolled over" (IRS 401(k) Resource Guide). Only older plans, an IRA, or a plan that allows a 59½ in-service rollover could fund a ROBS. Check T10.
- Recommendation: keep ROBS off the table unless there is an old plan balance, and even then only after a CPA and an ERISA attorney price the annual compliance.

## Targets where AI is a real value add

The buy box, in order of what the twin rewards:

1. **Size first:** cash flow before owner labor near 1.8x his replacement income, so the trigger is reachable at all.
2. **A manager or lead already in place**, so the business runs while he works the W-2 (and so the purchase is not a passive or management-company deal).
3. **A manual back office**: scheduling, dispatch, quoting, invoicing, collections, compliance paperwork, inventory, customer follow-up, done by people with spreadsheets and phones. That is where a few points of margin sit.
4. **Recurring or contracted revenue and many customers**, which BizBuySell says buyers prefer ("reliable cash flow, clean financials, limited owner dependence," Q3 2026) and which raises the exit multiple.
5. **Not cannabis-adjacent and not a supplier, customer or competitor of his employer** (checks T3, T13, T2).

Kinds of business that often fit: residential and commercial service trades (HVAC, plumbing, electrical, cleaning, pest control, landscaping), property-management and turnover services, medical and dental billing, staffing, logistics brokerage, specialty distribution, insurance agencies. Each is a hypothesis for the twin, not a pick: the twin scores a real listing once the founder's inputs are in.

How the gain shows up in value: value is cash flow times a multiple. A margin gain of a few points of revenue raises cash flow; the multiple turns each added dollar into two to four dollars of value; crossing $1 million in value moves the business into the higher-multiple band. The twin computes this monthly (`business_value`, `equity_value`). The gain has to be measured on the business's own books, before and after, the same discipline as the answer key.

## The step-down test

The W-2 ends only in a month when every part of this test has passed for **six months running** (`consecutive_months`), and every check below is green:

| Part | Passes when |
|---|---|
| History | At least 12 months of owning the business |
| Replacement wage | Trailing 12 months of cash flow before owner labor is at least his salary plus the benefits he would have to buy |
| Coverage | After paying him that wage, cash flow covers a full year of debt service at least 1.25x (the lender floor) |
| Leaving pays | Manager wage saved plus what his full-time work adds is at least the salary and benefits that stop |
| Personal reserve | Six months of living costs plus benefits in cash, outside the business |
| Business reserve | Three months of debt service plus the manager's wage in the business's account |
| Seller transition | The seller's transition period is finished |

These are design defaults chosen so the test is measurable, not figures from a source. The 1.25x mirrors the lender floor reported for SOP 50 10 8.1. The founder can tighten any of them in his private inputs.

## Red flags turned into checks

Each check reads facts only. Unknown facts are amber, and amber blocks the step-down. The twin reports every check per arm.

| Id | Check | Why (source) |
|---|---|---|
| T1 | Employer outside-work and conflict terms reviewed, and they permit this business | His employer's own documents decide this. Not read here; see the look-up list below |
| T2 | No employer time, equipment, data, customers or IP used; the business is not a supplier, customer or competitor of the employer | Keeps the AI method his and the business clean of conflicts |
| T3 | Target is SBA-eligible: not a marijuana business, not passive | SOP 50 10 8, ch. 1 |
| T4 | Every 20%+ owner, and the trustor of any owning trust, is named as guarantor, and the guarantee is counted in personal reserves | Starfield & Smith 2026; MMCG 2026 |
| T5 | The Foundation holds no interest, gives no guarantee or pledge, lends nothing and does no business with the deal or the founder's loan | 4941(d)(1)(B), (E); Reg. 53.4941(d)-2(f)(1): a foundation's "guarantee (of repayment) ... with respect to a loan to a disqualified person shall be treated as a use for the benefit of a disqualified person" |
| T6 | The owner is not a trust with the Foundation as beneficiary, or counsel has cleared excess business holdings | 4943(d)(1): a trust's holdings are "owned proportionately by or for its ... beneficiaries"; Reg. 53.4943-8(b)(1) attributes a trust's holdings to its remainder beneficiaries. The 20% limit (4943(c)(2)) counts all disqualified persons together |
| T7 | Every role the founder doesn't do is paid at market before any earnings count | No inflated cash flow (model rule) |
| T8 | The founder's wages from the business are for real, logged work at market for the hours worked | Ties to structure checks S8 and S9 |
| T9 | A seller note counted as equity is on full standby for the life of the SBA loan | SOP 50 10 8.1 as quoted (Searchfunder) |
| T10 | No ROBS funded from the current employer's plan while still employed | IRS 401(k) Resource Guide; IRS ROBS project |
| T11 | All owners meet SBA's current citizenship rule | SBA March 2026 policy (American Banker) |
| T12 | Independent business valuation on file | SOP 50 10 8.1 (MMCG; BizBuySell Q3 2026) |
| T13 | The transport company shares no accounts, staff, revenue or customers with the other business, and the lender has been told about it | Whether an owner's cannabis business affects a separate business's eligibility was not found in any source read: ask |
| T14 | The W-2 ends only on the step-down test | Model rule |
| T15 | Last year's cash flow, after a market manager wage, covers first-year debt service at the lender floor | SOP 50 10 8.1 (MMCG) |
| T16 | The manager is an employee under the owner's direction; no management company, the founder's own included, holds complete operational control | SOP 50 10 8, ch. 1; Whiteford 2025 |

**The biggest structural catch (T6).** The stack today runs the Family Trust's benefit to the Foundation. If the Family Trust owns the acquired business, the Foundation is likely treated as owning part of it, and the founder's own holdings count against the same 20% limit. That points to owning the buying company outside any trust the Foundation benefits from (for example, directly or through an ordinary LLC), with the trust question left to counsel. It also matches the rehearsal's earlier fix: ordinary business entity, market wages, Foundation at arm's length.

## Employer terms the founder should look up (not read here)

Nothing of the employer's was read for this file. These are the documents and questions to find, in his own employee materials or from HR:

1. Code of conduct sections on outside employment, outside business interests and conflicts of interest, and whether outside work needs disclosure or approval.
2. Any invention, IP or work-product assignment he signed at hire, and what it says about work done on his own time and equipment.
3. Confidentiality terms and the rule on using company devices, accounts, AI tools or data for anything personal.
4. Any non-compete or non-solicitation agreement, and whether it applies at his level.
5. Rules on doing business with the employer's suppliers, contractors or customers.
6. Whether ownership of a cannabis-licensed company needs disclosure under any policy.

## Questions for counsel and a CPA

1. **Employment counsel:** do my employer's outside-work, conflict and IP terms let me own and oversee a business while employed, and how do I keep my own method (Northstar) clearly mine?
2. **Entity counsel:** who should own the buying company: me, an LLC, or a trust? Given the trustor-guarantee rule and IRC 4943's attribution through a trust that benefits the Foundation, does the Family Trust belong anywhere in this deal?
3. **SBA lender or counsel:** does my ownership of a licensed cannabis transporter affect SBA eligibility or lender appetite for a separate, unrelated acquisition? Is a transporter a "distributor" under the SOP?
4. **Tax counsel or CPA:** does IRC 280E reach a cannabis transporter, and what does that do to growing it first?
5. **CPA:** for the acquired business, which tax election, what reasonable compensation for me before and after I step down, and what will replacing employer benefits actually cost?
6. **Lender:** confirm against the current SOP the equity, seller-note, coverage, valuation and seller-transition rules above, and whether my W-2 income counts toward coverage at close.
7. **ERISA attorney (only if old plan balances exist):** is a ROBS worth its compliance cost for me?
8. **Counsel:** if the government-contracting company ever seeks an SBA loan, does the management company's agreement make it a passive business under the SOP?

## What the founder supplies (privately)

The twin needs his real inputs, in the private project folder, never here: gross salary, the employer benefits he would have to replace, living costs (from the 12-month export already requested), cash available for a purchase, and his honest estimate of what his full-time work would add. With those, the twin prints his size rule, the cash a purchase needs, and the month each arm would let him step down.

## Sources read (2026-11-20)

- SBA Information Notice 5000-880695, Issuance of SOP 50 10 8.1 (effective October 1, 2026): https://legacy.sba.gov/document/information-notice-5000-880695-issuance-sop-50-10-81
- SBA SOP 50 10 8 (effective June 1, 2025), third-party copy: https://colemanreport.com/wp-content/uploads/2025/04/SOP-50-10-8-effective-6.1.2025-Final.pdf
- MMCG Invest, SOP 50 10 8.1 (September 6, 2026): https://www.mmcginvest.com/post/sba-stopped-lending-on-projections-sop-50-10-8-1-closes-acquisition-loans-on-last-year-s-numbers
- Searchfunder, New SOP Changes SOP 50 10 8.1 (forum post quoting SOP text; unverified): https://searchfunder.com/post/new-sop-changes-sop-50-10-81
- Whiteford, SOP 50 10 8 client alert (May 6, 2025): https://www.whitefordlaw.com/news-events/client-alert-sba-issues-sop-50-10-8-key-changes-impacting-sba-7a-lending
- Windsor Advantage, SOP 50 10 8 equity injection (July 28, 2025): https://www.windsoradvantage.com/news/updated-sba-equity-injection-rules-what-you-need-to-know-about-sop-50-10-8
- Starfield & Smith, equity injection (May 6, 2025): https://starfieldsmith.com/2025/05/best-practices-a-review-of-equity-injection-requirements-under-sop-50-10-8/
- Starfield & Smith, trust documentation in SBA loans (July 2026): https://starfieldsmith.com/2026/07/best-practices-reviewing-trust-documentation-in-sba-loans/
- American Banker, SBA citizenship rule (February 4, 2026): https://www.americanbanker.com/news/sba-re-tightens-its-eligibility-rules-hitting-noncitizens
- CRS Insight IN12549 (April 28, 2025): https://www.everycrsreport.com/reports/IN12549.html
- IRS, Rollovers as Business Start-Ups Compliance Project: https://www.irs.gov/retirement-plans/rollovers-as-business-start-ups-compliance-project
- IRS, Guidelines regarding rollovers as business start-ups (October 1, 2008): https://www.irs.gov/pub/irs-tege/robs_guidelines.pdf
- IRS, 401(k) Resource Guide, general distribution rules: https://www.irs.gov/retirement-plans/plan-participant-employee/401k-resource-guide-plan-participants-general-distribution-rules
- 26 U.S.C. 4941 and 4943; 26 CFR 53.4941(d)-1, 53.4941(d)-2, 53.4943-8 (Cornell LII and eCFR)
- BizBuySell Insight Report, Q3 2026, and data tables (Chicago 2025 closed sales): https://www.bizbuysell.com/insight-report/ and https://www.bizbuysell.com/insight-report-data-tables

**Not verified, so not relied on:** SOP 50 10 8.1's own text; whether SBA counts ROBS funds as equity under 8.1; Illinois non-compete and employee-invention statutes; whether 280E reaches a transporter.
