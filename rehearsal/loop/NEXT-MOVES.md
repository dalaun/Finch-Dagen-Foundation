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
- Why it matters: the engine assumes both are passive under IRC 469, so the 3.8 percent net investment income tax (IRC 1411) applies to them. On the synthetic base year that assumption lowered break-even with an unrelated individual trustee from 178,500 to 149,500 a year, about 16 percent (at the time; the founder NII fix of PR 94 later moved the base figure to 170,300, because a generic asset's income is not investment income, so the pre-fix figures here are history). Material participation, or real estate professional status under 469(c)(7), would take the tax off and push break-even back up.
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
  | Unrelated individual trustee | 170,300 | 166,000 | 137,200 | 147,700 |
  | Independent professional trustee | no break-even up to 1,000,000 | no break-even up to 1,000,000 | no break-even up to 1,000,000 | no break-even up to 1,000,000 |

  With a professional trustee, no asset income up to 1,000,000 a year clears break-even, so no asset size is implied for that path.
- Rough value, base case with an unrelated individual trustee: 170,300 a year divided by `asset_yield_for_value` (0.07 in stack.json) is 170,300 / 0.07 = about 2,432,900. The same division gives about 2,371,400 (lean), 1,960,000 (asset_rental) and 2,110,000 (asset_business). The 150,000-a-year `asset_sized` scenario was sized to the earlier 149,500 and is not resized; the engine now gives 20,200 more on top of its 150,000 (170,200 in all). The 0.07 is itself an ASSUMPTION in stack.json for perspective, not a market rate; no public yield was read for this move.
- The one thing for Dalaun: ask his CPA or an appraiser, "Is a yield of about 7 percent a fair stand-in for what an asset of this kind earns after costs, so that about 170,000 a year of net income means an asset of roughly 2.4 million?"
- Status: open
- Working assumption: the asset is sized to clear the unrelated-individual-trustee break-even (170,300 a year in the base case after the PR 94 NII fix; 149,500 before it), worth roughly 2,432,900 at the assumed 0.07 yield; see counsel-queue.md Q11

### 5. asset: Which classes of asset could produce that income?

- Key: `asset-classes-b2`
- Step: B2
- Opened: 2026-11-24
- For: CPA or appraiser
- Why it matters: B1's income (about 170,300 a year net, in the base case) has to come from something real. Two or three classes could produce it. **No market data was read in this run**: the yields below are not from a public source.
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
- Why it matters: on today's synthetic numbers the structure costs 6,015 a year in the base case and only an asset earning about 170,300 a year (an unrelated individual trustee) clears it, so the Family Trust must be able to hold that asset. Checklist of what it needs (read: IRS employer ID page, https://www.irs.gov/businesses/small-businesses-self-employed/employer-id-numbers, which lists trusts as needing an EIN "except certain grantor-owned revocable trusts"; not read: the Illinois Trust Code, 760 ILCS 3, whose page would not load in this run):
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
- Why it matters: the engine taxes the Family Trust's distributions to the two adult beneficiaries at their own rates (IRC 652(a), 662(a)) on top of "other income" it assumes for each: 46,080 a year, the BLS second-income-fifth average (stack.json `beneficiary_other_income`). In a scratch run (not committed) that assumed 78,584 instead (the BLS third-fifth average), break-even with an unrelated individual trustee on the base year rose from 170,300 to 232,600 a year (R15 rerun on today's engine; 149,500 to 198,000 before PR 94's fix), about 37 percent, because the beneficiaries' higher brackets eat more of the trust's income. The tax-rule side was not re-read in this run; the two income figures are from benchmarks-ce.json (BLS CE, https://www.bls.gov/news.release/cesan.nr0.htm, not re-fetched in this run).
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
- Why it matters: the Foundation's program money must come from the asset's income (scorecard SC5), and with w = 0 that 10 percent share is money out of the family. In the `asset_sized` scenario (150,000 a year of asset income) `steward_r2_pipeline` loses 12,284 a year against doing nothing in structure value (R15 rerun after the PR 94 fix). The engine's break-even for route R2 with a 10 percent Foundation share and an unrelated individual trustee, on the base year, was 343,600 a year of net asset income (337,300 lean) when this move was written; it is now none up to 1,000,000 in every scenario, because the 10 percent gift is a family cost at w = 0 and the founder NII fix lowered Arm A's tax that the trust saves against. Rounded up to the next 10,000 that is 350,000, and the new scenario `asset_sized_pipeline` holds exactly that. When written, the pipeline version's structure value there was +395 a year (score vs A +2,029); on today's engine it is -8,598 a year (score vs A -7,150, stewarded vs A +27,850), so SC5's by-construction pass at break-even no longer holds (see the scorecard line of the run report). Compared with `asset_sized`: 200,000 more yearly asset income, and at the assumed 0.07 yield (stack.json, an ASSUMPTION, no public yield read) an asset of about 5,000,000 against about 2,142,900, roughly 2,857,100 more. Caution: the engine's search assumes the value rises steadily with income, and for this version it wobbles (in the base year it is +812 at 500,000 a year and -2,421 at 700,000), so any single crossing was not a guaranteed floor. With the other two trustee paths (professional trustee) no break-even exists up to 1,000,000.
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

### 11. asset: Which public rental-building listings fit the size that clears break-even?

- Key: `shortlist-b3-rental`
- Step: B3
- Opened: 2026-11-25
- For: Dalaun
- Why it matters: B2's two classes (move 5) are a rental building and a bought business. On today's synthetic numbers the rental needs the lower income to clear break-even with an unrelated individual trustee (`asset_rental` 137,200 a year against `asset_business` 147,700; base 170,300), so the scorecard favors the rental. ASSUMPTION: the pick is the rental building; he can override it with an `Answer:` line. At the engine's assumed 0.07 yield (not a market rate) 150,000 a year is an asset of about 2.1 million. **No listing was read in this run:** the three public listing sites tried (LoopNet, Crexi, Redfin) refused the runner with HTTP 403, so the shortlist is empty. The search to run by hand: multifamily, Chicago area, asking price about 1.5 to 2.5 million, with the stated net operating income or cap rate.
- The one thing for Dalaun: confirm the rental building as the class to shortlist, then open a public multifamily search yourself at about 1.5 to 2.5 million and send back the links, or tell me to wait for a source the runner can read.
- Status: open
- Working assumption: the class is the rental building at the 0.07 yield; no listing, seller or broker is contacted; it is Dalaun's own search, not a counsel question

### 12. question: Does the founder file as single or as married filing jointly?

- Key: `founder-filing-status`
- Opened: 2026-11-25
- For: Dalaun (his own family fact), then CPA
- Why it matters: the engine taxes the founder as a single filer (`person_tax` uses the single brackets, the single standard deduction and the 200,000 NIIT threshold). In a scratch run (not committed) that gave the founder's own return the 2026 married-filing-jointly brackets and standard deduction (both already in benchmarks-tax.json `federal_2026`, Rev. Proc. 2025-32) and a rough 250,000 NIIT threshold, break-even with an unrelated individual trustee on the base year rose from 149,500 to 361,300 a year, about 142 percent (lean 146,900 to 345,600; asset_rental 137,200 to 805,700; asset_business 147,700 to 887,300; these scratch figures were computed before the PR 94 NII fix and are not rerun, so read them as direction only, against today's base 170,300). The scratch change was crude: the beneficiaries stayed single, Illinois personal exemptions were not touched, and the NIIT threshold was approximated; read it as the direction and rough size, not a result. Wider joint brackets leave less top-bracket income for the trust to move, so the structure needs a much larger asset.
- The one thing for Dalaun: tell your assistant privately whether the rehearsal should treat the founder as filing single or jointly (the repo is public, so write only "single-like" or "joint-like" in an `Answer:` line, never family details), or ask the CPA, "At what income does filing jointly versus single change how much tax the trust's split saves?"
- Status: open
- Working assumption: the founder files single (2026 single brackets, Rev. Proc. 2025-32); see counsel-queue.md Q25

### 13. question: How many adult beneficiaries will share the Family Trust's distributions?

- Key: `adult-beneficiary-count`
- Opened: 2026-11-25
- For: Dalaun (his own family fact), then lawyer
- Why it matters: the engine splits the trust's distributions across 2 adult beneficiaries (`adult_beneficiaries` in stack.json, no source), each taxed at their own brackets (IRC 652(a), 662(a)). In scratch runs (not committed) that changed only that count, break-even with an unrelated individual trustee on the base year went from 170,300 to none up to 1,000,000 a year with 1 beneficiary (asset_rental 707,200, asset_business 725,300) and to 141,600 with 3 (about 17 percent less; R15 rerun on today's engine). The 10 percent Foundation share finds no break-even up to 1,000,000 with 1, 2 or 3 beneficiaries in the base year (only asset_rental with 3 reaches one, 269,700). More beneficiaries means more low brackets to fill, so a smaller asset clears break-even.
- The one thing for Dalaun: tell your assistant privately whether the rehearsal should count one, two or three adult beneficiaries (write only the number in an `Answer:` line, never names or family details), or ask his lawyer, "Who should be the beneficiaries of the Family Trust, and should the count be fixed in the instrument?"
- Status: open
- Working assumption: two adult beneficiaries; see counsel-queue.md Q27

### 14. question: What would an unrelated individual trustee really charge, and will one serve?

- Key: `individual-trustee-fee`
- Opened: 2026-11-25
- For: lawyer
- Why it matters: every break-even above that uses an unrelated individual trustee rests on a 1,000 a year fee (stack.json `fees_placeholder.unrelated_individual_trustee`, a PLACEHOLDER with no source). With an independent professional trustee (2,500 minimum or 1 percent of assets) no asset income up to 1,000,000 clears break-even. In a scratch run (not committed) that set the individual's fee to 5,000, break-even on the base year rose from 170,300 to 217,700 a year, about 28 percent (lean 166,000 to 214,200; asset_rental 137,200 to 175,000; asset_business 147,700 to 192,000; R15 rerun on today's engine). So the size of asset in moves 4 and 9 depends on a number nobody has quoted.
- The one thing for Dalaun: ask his lawyer, "Would an unrelated individual (not a family member, not a company) serve as trustee or distribution trustee of the Family Trust, what yearly fee is realistic, and what duties and liability would they carry?"
- Status: open
- Working assumption: an unrelated individual trustee serves for 1,000 a year (placeholder, not a quote); see counsel-queue.md Q28

### 15. question: Does a minor-only household change the answer? (No: the tax case fails.)

- Key: `minor-beneficiary-kiddie`
- Opened: 2026-11-25
- For: lawyer, then CPA
- Result in one line: with one minor beneficiary and no other income, income splitting saves nothing (the kiddie tax, IRC 1(g), puts the child's income above 2,700 at the founder's rate), the only federal saving left is the child's own 200,000 NIIT threshold (at most 3.8 percent of 200,000, 7,600 a year), against about 9,400 a year of added trust costs even with the 1,000 individual-trustee placeholder, so `base_minor_only` and `asset_rental_minor_only` have no break-even at any asset income up to 1,000,000, with an unrelated individual or a professional trustee.
- Why it matters: a private scratch run had said the same; this move confirms it with the traced rule. Traced (benchmarks-tax.json `kiddie_tax`, READ 2026-11-25): 1(g)(2)(A) covers a child under 18 at year end, or 18 (or a full-time student 19 to 23, by 152(c)(3)) whose earned income is not over half of support, with a parent alive; 1(g)(1), (3), (4) tax net unearned income at the parent's rate; Rev. Proc. 2025-32 sets the 2026 step at 1,350 (the dependent standard deduction and the 1(g)(4)(A)(ii)(I) amount), so the first 1,350 is free, the next 1,350 is at the child's rate, the rest at the parent's. The Form 8615 instructions say the child's NIIT is 3.8 percent of the lesser of net investment income or the excess of "the child's modified adjusted gross income (MAGI)" over the threshold: the child's own MAGI, not the parent's. The engine's rental figures: at 200,000 and 300,000 of extra asset income the structure value is -4,035 a year both times (the NIIT saving has hit its cap), while the same rental with an adult beneficiary breaks even at 137,200. For the base case the scratch figure of about 306,000 was real but came from founder-side NIIT charged on a generic asset's income in arm A (item 3 of backlog R14); with the engine fixed it is 304,600 under the old rule and none after. The earlier moves' break-even figures (4, 5, 9, 11 to 14) were written before that fix and were replaced by backlog R15 on 2026-11-25: base-case break-even with an unrelated individual trustee is 170,300 a year, not 149,500 (lean 166,000, not 146,900).
- What is left, as separate unscored lines (not dollars): (a) control and creditor protection of assets for a minor; (b) succession if the founder dies or is disabled; (c) the Foundation route (Q15, Q17); (d) the age at which the kiddie tax stops (19, or 24 for a full-time student, or when earned income is over half of support) and the adult-beneficiary math of move 13 applies again.
- Not modeled: the 1(g)(7) parental election, a minor's earned income or QBI, the Illinois exemption.
- The one thing for Dalaun: ask his lawyer, "If the beneficiaries are minors, is there any reason beyond control, creditor protection and succession to hold the asset in the Family Trust, given that income splitting is gone until they are adults?" Do not write family details in the answer line.
- Status: open
- Working assumption: one minor beneficiary under 18 with no other income and a living parent (a scenario, not a fact about anyone); the kiddie tax applies as traced; see counsel-queue.md Q29

### 16. question: Who is the independent co-trustee, and what does a professional or corporate one cost?

- Key: `independent-cotrustee`
- Opened: 2026-11-25
- For: lawyer
- Why it matters: route R2 needs an independent distribution trustee who is not related or subordinate under 672(c), and family cannot fill it. Published fee schedules of two trust companies (benchmarks-tax.json `fees.corporate_trustee_note`, READ 2026-11-25): Members Trust Company, 3,000 minimum for an irrevocable trust and 1.25 percent of the first million; BOKF, NA, Directed Personal Trust 5,000 minimum and 0.50 percent of the first million, closely held assets 4,000 minimum and 1.25 percent. The engine's placeholders (2,500 and 1 percent) are replaced by 3,000 and 1.25 percent (the lowest minimum read, and the rate both schedules show for assets that are not marketable securities). At the engine's 0.07 yield that fee is 17.9 percent of the asset's net income, so with a professional or corporate co-trustee there is no break-even at any asset income up to 1,000,000 in any scenario, including the minor-only ones (before the change: also none). With an unrelated individual at 1,000 a year the base-case figure is 170,300. A schedule is a list price for a managed trust; a trustee who only decides distributions may quote less, or may not serve at all (Citi and Schwab pages did not load).
- The one thing for Dalaun: ask his lawyer, "Who can serve as the independent distribution trustee of the Family Trust (not a relative, not an employee), would a trust company or a lawyer accept a distribution-only role for a flat fee, and what would they charge?"
- Status: open
- Working assumption: an unrelated individual serves for 1,000 a year; a corporate co-trustee is priced at the published schedules and kills the money case; see counsel-queue.md Q30
- Note: paid services by an adult sibling of the founder are ordinary income to that sibling at market pay, separate from the trust's beneficiary math; a sibling cannot be the independent co-trustee (672(c)(2), 674(c)); see counsel-queue.md Q31

### 17. question: What do the yearly tax filings and bookkeeping for the Family Trust and the Foundation really cost?

- Key: `yearly-filing-fees`
- Opened: 2026-11-25
- For: CPA
- Why it matters: the engine's yearly filing costs are PLACEHOLDERS with no quote behind them (stack.json `fees_placeholder`: Form 990-PF preparation 2,000, Form 1041 preparation 1,200 for each filing trust, bookkeeping 600 for each entity, Form 709 once 800). In scratch runs (not committed) that tripled one placeholder at a time, break-even with an unrelated individual trustee on the base year (route R2, today 170,300 a year) went to 217,700 with 990-PF at 6,000 (about 28 percent more), to 239,300 with bookkeeping at 1,800 for each entity (about 41 percent more), to 191,800 with the 709 at 2,400 (about 13 percent more) and to 200,400 with the 1041 at 3,600 (about 18 percent more). The 10 percent Foundation share finds no break-even up to 1,000,000 even at today's placeholders. Tripling is a stress test, not a forecast; the point is that the asset size in moves 4 and 9 moves by more than 10 percent with fees nobody has quoted.
- The one thing for Dalaun: ask his CPA, "What would you charge each year to prepare Form 990-PF for a small private foundation, Form 1041 for a non-grantor trust with two beneficiaries, and the trust's bookkeeping, and what would the first Form 709 cost?"
- Last checked: 2026-11-25
- Status: open
- Working assumption: the placeholders stand (990-PF 2,000, 1041 1,200, bookkeeping 600 for each entity, 709 800), not quotes; see counsel-queue.md Q32

### 18. question: Is 10 percent the right share of the trust's income for the Foundation, when a 2 percent share still has a break-even and 10 percent has none?

- Key: `foundation-share-pct`
- Opened: 2026-11-25
- For: CPA
- Why it matters: on today's engine (after the PR 94 founder NII fix, backlog R15) the base-year break-even for route R2 with a 10 percent Foundation share and an unrelated individual trustee is none up to 1,000,000 a year, where move 9 had 343,600, and scorecard SC5 (asset income reaches program output) fails, 6 of 7. The 10 percent is an ASSUMPTION (counsel-queue.md Q15) and the gift is a plain cost to the family at w = 0. In scratch runs (not committed) that changed only the share in `steward_r2_pipeline`: at 2 percent the base-year break-even is 206,100 a year (lean 202,000) and SC5 passes, 7 of 7 (program output 7,000 from the asset's income in `asset_sized_pipeline`); at 5 percent there is still no break-even up to 1,000,000, but SC5 passes (program output 17,500). Against the 170,300 a year for no share (move 4), a 2 percent share costs about 35,800 a year more of asset income, at the assumed 0.07 yield (not a market rate) about 511,400 more asset. The 10 percent in `asset_sized_pipeline` (350,000) is not resized. The share is the family's choice and a rehearsal never tunes it; the number only shows where the structure stops paying.
- The one thing for Dalaun: ask his CPA, "If the Foundation is to be funded from the trust's income, what yearly share (or fixed dollar amount) is sensible, and can the trust instrument let the trustee choose each year's amount and still get the 642(c)(1) deduction for amounts actually paid?"
- Last checked: 2026-11-25
- Status: open
- Working assumption: the share stays 10 percent in the engine (Q15, not changed); a share near 2 percent is the largest one the engine shows still paying for itself, a reading, not advice; see counsel-queue.md Q33

## Closed

(none yet)
