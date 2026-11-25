# Rehearsal loop: next moves

[Back to the goal](GOAL.md) · [How the daily run picks a move](DAILY-RUN.md)

**SYNTHETIC.** The figures here come from the seeded year in [../synthetic](../synthetic/README.md), not the founder's money. This repo is public, so moves never name real pay, rents, addresses, accounts or entity-private details. Design and education, not legal or tax advice.

The simulator is the map; this file is the GPS. Each daily run checks where the structure stands against the goal (the smallest income-producing asset that makes the structure pay for itself, with every check passing on documents) and writes **one next move**. Every move ends as one thing for Dalaun to approve or ask. Agents research, model and draft. Buying, signing, forming or funding anything stays with him and his lawyer.

## Kinds of move

- **question:** a question whose answer unblocks the numbers, for his CPA or lawyer. Written when an engine ASSUMPTION moves a break-even by more than 10 percent.
- **asset:** a step toward the first income-producing asset: what kind and size clears break-even, then classes that fit, then real candidates.
- **structure:** a step the trusts need before they can hold that asset, with the counsel question it raises.

## The route

The run takes the first step below that has no move yet and whose earlier step in the same leg is closed. A question move can come first on any day (DAILY-RUN.md, step 5).

| Step | Kind | What the move produces | Needs before it |
|---|---|---|---|
| B1 | asset | The asset that clears break-even: kind, yearly net income under each trustee path, and the price that income implies at cited public yields | none |
| C1 | structure | What the Family Trust needs before it can hold title (instrument, trustee, tax ID, state, bank account), as a checklist with the counsel question | none |
| B2 | asset | Two or three classes of asset that fit B1's size, each with cited public market data (yields, typical cash flow, financing such as SBA 7(a)) | B1 closed |
| C2 | structure | How the asset would be held (for example the trust owning an LLC that owns the asset) and which checks S1 to S17 that needs on documents | C1 closed |
| B3 | asset | A shortlist in the class he picks: public listings by link only, no contact with anyone | B2 closed, his pick |
| C3 | structure | Financing and title questions for counsel (lender consent, guarantees, insurance) for the shortlisted kind | C2 closed |

## Rules for this file

- Number moves in order and never reuse a number. Each move has a **key** (a short slug); a run never writes a second move with a key already here, open or closed.
- **Open** moves wait on Dalaun. **Answered** needs his word on main: a commit by `dalaun` that writes an `Answer:` line under the move, or the answer recorded in [05-questions-for-attorney-and-cpa.md](../05-questions-for-attorney-and-cpa.md). **Superseded** is for a move today's numbers no longer need, with the figure that shows it. A run may mark a move superseded, never answered.
- Answered and superseded moves stay in the file, under Closed, so the route remembers them.

## Open

### 1. question: Do the rentals, and a bought business run by a hired manager, count as passive?

- Key: `passive-469`
- Opened: 2026-11-23, from the NIIT work in PR 24
- For: CPA
- Why it matters: the engine assumes both are passive under IRC 469, so the 3.8 percent net investment income tax (IRC 1411) applies to them. On the synthetic base year that assumption lowers break-even with an unrelated individual trustee from 178,500 to 149,500 a year, about 16 percent. Material participation, or real estate professional status under 469(c)(7), would take the tax off and push break-even back up.
- The one thing for Dalaun: ask his CPA, "Would my rental income, and a business I buy and run through a hired manager, be passive activities for me under section 469, and could I qualify as a real estate professional?"
- Last checked: 2026-11-25
- Status: open
- Working assumption: see counsel-queue.md Q1

### 2. question: Will the Family Trust pay out all of its income each year, or keep part of it?

- Key: `trust-distributes-dni`
- Opened: 2026-11-23
- For: lawyer, then CPA
- Why it matters: the engine assumes the trust distributes 100 percent of its distributable net income (DNI) to the two adult beneficiaries, who are taxed at their own lower brackets. In a scratch run (not committed) that assumed only 50 percent is distributed, break-even with an unrelated individual trustee roughly doubles, from about 148,000 to about 313,000 a year of asset income, because retained income is taxed at the compressed trust brackets (and above the top trust bracket start, NIIT applies). Whether income goes out is a trustee-discretion or mandatory-payout choice written into the instrument, so it decides how big the asset must be.
- The one thing for Dalaun: ask his lawyer, "Should the Family Trust be written to require distributing its income each year, or leave it to the trustee's discretion, and what does each do to who pays the tax?" Then ask his CPA to confirm the tax result.
- Status: open
- Working assumption: see counsel-queue.md Q2

### 3. structure: Keep the Family Trust non-grantor while he stays its steward

- Key: `non-grantor-steward`
- Opened: 2026-11-23
- For: lawyer, then CPA
- Why it matters: the savings with an independent trustee assume the Family Trust is its own taxpayer. If he funds it and, as trustee, decides who gets how much, IRC 674(a) makes it a grantor trust and all its income is taxed to him. `grantor_check.py` now tests the trust's modeled terms against IRC 671-679 on every run. It grades nine design routes in `grantor-routes.json`; [../synthetic/NON-GRANTOR-ROUTES.md](../synthetic/NON-GRANTOR-ROUTES.md) explains them. Two routes keep him as trustee and pass. R2: he runs investments and administration, and an independent special distribution trustee decides who gets what (674(c)). R3: income is paid out every year in fixed shares, and principal goes out only for health, education, support or maintenance (674(b)(5)(A)).
- The one thing for Dalaun: ask his lawyer, "Can the Family Trust be written so I am trustee for investments and administration, while either an independent co-trustee makes distribution decisions or income is paid in fixed shares with principal limited to health, education, support and maintenance? Which keeps it a non-grantor trust with the least risk?" Then ask these follow-ups:
  - Does an Illinois distribution trust advisor under 760 ILCS 3/808 who is not a trustee qualify for the 674(c) exception, or should that person be a co-trustee?
  - Is my power to remove the distribution trustee limited to appointing another independent one (Reg. 1.674(d)-2(a))?
  - If the trust deducts payments to the foundation (642(c)(1)), it becomes a 4947(a)(2) split-interest trust under the self-dealing rules. How do we keep me and my family clear, and should the charitable share be segregated?
  - Do the powers I keep cause gift or estate tax problems for me as the funder?
  - If the trust pays for things I am legally obliged to provide any minor children, that income is taxed to me (677(b)). How should the document keep distributions to them separate from my support duties?
- Status: open
- Working assumption: see counsel-queue.md Q3

### 4. asset: How big must the income-producing asset be to clear break-even?

- Key: `asset-size-b1`
- Step: B1
- Opened: 2026-11-24
- For: CPA or appraiser
- Why it matters: the structure only pays for itself if the asset earns more than break-even. The engine's break-even extra yearly net asset income, on main today, for both steward routes and flat_independent:

  | Trustee path | base | lean | asset_rental | asset_business |
  |---|---|---|---|---|
  | Unrelated individual trustee | 149,500 | 146,900 | 137,200 | 147,700 |
  | Independent professional trustee | no break-even up to 1,000,000 | no break-even up to 1,000,000 | no break-even up to 1,000,000 | no break-even up to 1,000,000 |

  With a professional trustee, no asset income up to 1,000,000 a year clears break-even, so no asset size is implied for that path.
- Rough value, base case with an unrelated individual trustee: 149,500 a year divided by `asset_yield_for_value` (0.07 in stack.json) is 149,500 / 0.07 = about 2,135,700. The same division gives about 2,098,600 (lean), 1,960,000 (asset_rental) and 2,110,000 (asset_business). The 0.07 is itself an ASSUMPTION in stack.json for perspective, not a market rate; no public yield was read for this move.
- The one thing for Dalaun: ask his CPA or an appraiser, "Is a yield of about 7 percent a fair stand-in for what an asset of this kind earns after costs, so that about 150,000 a year of net income means an asset of roughly 2.1 million?"
- Status: open
- Working assumption: the asset is sized to clear the unrelated-individual-trustee break-even (149,500 a year in the base case), worth roughly 2,135,700 at the assumed 0.07 yield; see counsel-queue.md Q11

### 5. asset: Which classes of asset could produce that income?

- Key: `asset-classes-b2`
- Step: B2
- Opened: 2026-11-24
- For: CPA or appraiser
- Why it matters: B1's income (about 149,500 a year net, in the base case) has to come from something real. Two or three classes could produce it. **No market data was read in this run**: the yields below are not from a public source.
  - A rental building (an engine asset kind). Public data that would settle it: published cap rates for the property type and region (for example from a brokerage's or appraisal firm's cap-rate survey), and typical operating cost ratios.
  - A bought operating business run by a hired manager (an engine asset kind). Public data that would settle it: business sale multiples from published sale-transaction databases or survey reports, and SBA 7(a) loan terms (rate, term, down payment, guarantee rules) from the SBA's published program pages.
  - Optionally a third class, such as a small portfolio of rental units rather than one building, settled by the same cap-rate data plus per-unit cost and vacancy figures.
- The one thing for Dalaun: ask his CPA or an appraiser, "Which of these classes can credibly net about 150,000 a year at the size B1 implies, and what yield, multiple or loan terms should the rehearsal use for each?"
- Status: open
- Working assumption: the two kinds the engine models (a rental building and a bought operating business) at the engine's assumed yields, not yet read from a public source; see counsel-queue.md Q12

### 6. structure: What must the Family Trust have before it can hold title to an asset?

- Key: `trust-title-c1`
- Step: C1
- Opened: 2026-11-24
- For: lawyer
- Why it matters: on today's synthetic numbers the structure costs 6,015 a year in the base case and only an asset earning about 149,500 a year (an unrelated individual trustee) clears it, so the Family Trust must be able to hold that asset. Checklist of what it needs (read: IRS employer ID page, https://www.irs.gov/businesses/small-businesses-self-employed/employer-id-numbers, which lists trusts as needing an EIN "except certain grantor-owned revocable trusts"; not read: the Illinois Trust Code, 760 ILCS 3, whose page would not load in this run):
  1. A signed written instrument with the terms of the chosen route (move 3: R2 or R3), naming the trustee(s) and, for R2, the independent distribution trustee.
  2. A trustee who accepts the office, with an unrelated individual or professional named as in moves 3 and 4.
  3. Its own tax ID (EIN), because under the rehearsal's route the trust is a non-grantor taxpayer.
  4. A governing-law and situs choice (Illinois assumed in the engine).
  5. A bank account in the trust's name, opened by the trustee, never mixed with the founder's.
  6. Title and any lender consent for the asset taken in the trust's name or its LLC's (decided in C2).
- The one thing for Dalaun: ask his lawyer, "For a non-grantor Family Trust under route R2 or R3, what must exist before it can take title to an income-producing asset: instrument terms, trustee acceptance, EIN, Illinois situs, bank account, and who signs for the trust?"
- Status: open
- Working assumption: the trust is written under Illinois law with the trustee named per move 3, gets its own EIN and its own account, and the asset is bought only after those exist; see counsel-queue.md Q13

### 7. question: What other income will the two adult beneficiaries have, so their own tax brackets are known?

- Key: `beneficiary-income`
- Opened: 2026-11-24
- For: Dalaun (his own family facts), then CPA
- Why it matters: the engine taxes the Family Trust's distributions to the two adult beneficiaries at their own rates (IRC 652(a), 662(a)) on top of "other income" it assumes for each: 46,080 a year, the BLS second-income-fifth average (stack.json `beneficiary_other_income`). In a scratch run (not committed) that assumed 78,584 instead (the BLS third-fifth average), break-even with an unrelated individual trustee on the base year rose from 149,500 to 198,000 a year, about 32 percent, because the beneficiaries' higher brackets eat more of the trust's income. The tax-rule side was not re-read in this run; the two income figures are from benchmarks-ce.json (BLS CE, https://www.bls.gov/news.release/cesan.nr0.htm, not re-fetched in this run).
- The one thing for Dalaun: say roughly what range of other yearly income the two adult beneficiaries are likely to have (under about 50,000, about 50,000 to 80,000, or over 80,000), or ask his CPA, "At what income level do the beneficiaries' own brackets make a trust distribution cost more tax than it saves?" Answer with a range only, never real pay in this public repo.
- Status: open
- Working assumption: the beneficiaries have the BLS second-fifth average other income (46,080) and file single; see counsel-queue.md Q14

### 8. structure: How would the Family Trust hold the asset, and which checks does that need on documents?

- Key: `asset-holding-c2`
- Step: C2
- Opened: 2026-11-24
- For: lawyer, then CPA
- Why it matters: on today's synthetic numbers the base-case structure costs 6,015 a year, and the `asset_sized` scenario (a generic asset netting 150,000 a year, ASSUMPTION per move 4) is the first where `steward_r2` and `steward_r3` beat the status quo (structure value +66 a year, score vs A +1,592; 8 of 17 checks pass, none red). The other 9 are amber until documents exist. Holding design the rehearsal assumes: the Family Trust owns an LLC, and the LLC owns the asset (a rental building, or a bought business with a hired manager), as `07-structure-integrity-checks.md` already recommends (its case SK2 against SK1, where a trust running the business fails S1, S5 and S12). Checks this design needs on documents, taken from the definitions in `07-structure-integrity-checks.md` and the amber list in `SCORECARD.md`:
  - S5 and S12: the asset sits in an LLC that files as a business, not as a trust, and anyone who works in it is paid market wages. Documents: the LLC's operating agreement and its tax classification, wage records.
  - S9: each contract, lease or invoice is in the LLC's name. Documents: the leases or customer contracts and invoices.
  - S6 and S7: the LLC deducts no personal or family cost and depreciates no family residence. Documents: the LLC's books and depreciation schedule.
  - S3 and S4: payment tools on the trust's and LLC's accounts are in the trustee's hands only, and trust transactions follow the instrument. Documents: bank signer cards, trustee minutes.
  - S2: the trustee applies the instrument. Documents: a decision log showing at least one request declined or modified.
  - Not read in this run: any primary source on single-member LLC tax classification (Treas. Reg. 301.7701-3) or on LLC ownership by a trust; the design above is the repo's own, not a cited legal reading.
- The one thing for Dalaun: ask his lawyer, "If the Family Trust owns an LLC and the LLC owns the income-producing asset, what must be in the trust instrument, the operating agreement and the trustee's records so that checks S2 to S9 and S12 pass on documents, and does the founder as an R2 or R3 trustee being the LLC's manager cause a problem?"
- Status: open
- Working assumption: the Family Trust owns 100 percent of one LLC per asset, the LLC is the contracting and banking entity, and the founder is its manager paid market wages as an employee; see counsel-queue.md Q16

### 9. asset: How big must the asset be if 10 percent of the trust's income goes to the Foundation?

- Key: `asset-size-pipeline`
- Step: B1
- Opened: 2026-11-24
- For: CPA or appraiser
- Why it matters: the Foundation's program money must come from the asset's income (scorecard SC5), and with w = 0 that 10 percent share is money out of the family. In the `asset_sized` scenario (150,000 a year of asset income) `steward_r2_pipeline` loses 10,891 a year against doing nothing. The engine's break-even for route R2 with a 10 percent Foundation share and an unrelated individual trustee, on the base year, is 343,600 a year of net asset income (337,300 lean). Rounded up to the next 10,000 that is 350,000, and the new scenario `asset_sized_pipeline` holds exactly that. There the pipeline version's structure value is +395 a year (score vs A +2,029), so SC5 passes by construction at break-even, not because anything was tuned. Compared with `asset_sized`: 200,000 more yearly asset income, and at the assumed 0.07 yield (stack.json, an ASSUMPTION, no public yield read) an asset of about 5,000,000 against about 2,142,900, roughly 2,857,100 more. Caution: the engine's search assumes the value rises steadily with income, and for this version it wobbles (in the base year it is +812 at 500,000 a year and -2,421 at 700,000), so 343,600 is the first crossing, not a guaranteed floor. The same search run on `asset_sized`, which already holds 150,000, gives 727,300 extra, which is that wobble and should not be read as a size. With the other two trustee paths (professional trustee) no break-even exists up to 1,000,000.
- The one thing for Dalaun: decide whether a 10 percent Foundation share is worth an asset of roughly 5 million instead of 2.1 million, or ask his CPA, "What share of the trust's income should go to the foundation, given that each 10 percent needs this much more asset?"
- Status: open
- Working assumption: the asset nets 350,000 a year, the base-case break-even of the pipeline version rounded up; see counsel-queue.md Q17

### 10. structure: What do lenders, title and insurance need if the Family Trust's LLC buys the asset?

- Key: `financing-title-c3`
- Step: C3
- Opened: 2026-11-24
- For: lawyer
- Why it matters: the asset that clears break-even (about 150,000 a year net, `asset_sized`; about 350,000 with a 10 percent Foundation share, `asset_sized_pipeline`) would likely be bought with a loan, and a loan can put the founder's own guarantee, or the lender's consent, between the trust and the asset. Read in this run: the SBA 7(a) page, https://www.sba.gov/funding-programs/loans/7a-loans, which lists "Be an operating business" and "Operate for profit" as eligibility terms and says nothing about trusts, personal guarantees or down payments. Not read: SBA's lender rules (SOP 50 10) and any lender's terms. Questions for counsel: (1) Will a lender lend to an LLC owned by a non-grantor trust, and what consent does it want from the trustee? (2) If the founder must guarantee the loan, does that change the checks S1 to S17 or the non-grantor result (IRC 671-679)? (3) Who is named on title and on the property or liability insurance: the LLC, the trust, or both? (4) What if the lender wants the founder to hold the LLC directly?
- The one thing for Dalaun: ask his lawyer, "If the Family Trust's LLC buys the asset with a loan, will lenders accept that ownership, must I guarantee it personally, and does a guarantee put the trust or the checks at risk?"
- Status: open
- Working assumption: the lender consents to trust ownership and the founder's guarantee, if asked, is accepted as not breaking the non-grantor result; see counsel-queue.md Q18

## Closed

(none yet)
