# Counsel queue

[Back to the rehearsal](README.md)

**SYNTHETIC.** Questions the rehearsal could not answer on its own. Each runs on a stated assumption so the loop never waits. Nothing here is a legal conclusion; it is design and education, not legal or tax advice. Every status is `assumed, awaiting counsel` until Dalaun records an answer.

Each entry has a stable id (Q1, Q2, ...). Moves in [../loop/NEXT-MOVES.md](../loop/NEXT-MOVES.md) point here with a `Working assumption:` line, and `scorecard.py` (SC2, SC7) finds an entry by its question text or by the move's key. Ids are never reused.

## Q1. Do the rentals, and a bought business run by a hired manager, count as passive?

- Key: `passive-469`
- Raised by: NEXT-MOVES.md move 1
- For: CPA
- Question: Would my rental income, and a business I buy and run through a hired manager, be passive activities for me under section 469, and could I qualify as a real estate professional?
- ASSUMPTION: The rehearsal treats the rentals and a business run by a hired manager as passive activities under IRC 469, so the 3.8 percent net investment income tax (IRC 1411) applies to that income.
- Primary cite: IRC 469(c)(7)(B) and 469(h)(1), https://www.law.cornell.edu/uscode/text/26/469 (not read by the run that wrote this entry).
- What the text says (as read, not a conclusion): Section 469(h)(1) is read as asking whether the taxpayer is involved in the operations of the activity on a regular, continuous and substantial basis; 469(c)(7)(B) is read as asking for more than half of personal services in real property trades or businesses in which he materially participates and more than 750 hours in the year. Whether his facts meet either is for the CPA.
- If counsel says otherwise: If counsel says the income is nonpassive, the 3.8 percent tax comes off that income and break-even with an unrelated individual trustee rises from about 149,500 back toward about 178,500 a year (move 1's figures). The engine's passive flag would change in scenarios.json and benchmarks-tax.json.
- Status: assumed, awaiting counsel

## Q2. Will the Family Trust pay out all of its income each year, or keep part of it?

- Key: `trust-distributes-dni`
- Raised by: NEXT-MOVES.md move 2
- For: lawyer, then CPA
- Question: Should the Family Trust be written to require distributing its income each year, or leave it to the trustee's discretion, and what does each do to who pays the tax?
- ASSUMPTION: The rehearsal runs on the trust distributing 100 percent of its distributable net income to the two adult beneficiaries, who are taxed at their own brackets.
- Primary cite: IRC 643(a) (distributable net income), https://www.law.cornell.edu/uscode/text/26/643 (not read by the run that wrote this entry).
- What the text says (as read, not a conclusion): Section 643(a) is read as defining distributable net income as the trust's taxable income with listed modifications; how much of it goes out each year is set by the instrument (mandatory or discretionary), which is for the lawyer, and the tax result is for the CPA.
- If counsel says otherwise: If the instrument leaves payout to discretion and the trustee keeps part, retained income is taxed at trust brackets. A scratch run at 50 percent distributed roughly doubled break-even, from about 148,000 to about 313,000 a year. The engine's distribution share would change.
- Status: assumed, awaiting counsel

## Q3. Keep the Family Trust non-grantor while he stays its steward

- Key: `non-grantor-steward`
- Raised by: NEXT-MOVES.md move 3
- For: lawyer, then CPA
- Question: Can the Family Trust be written so I am trustee for investments and administration, while either an independent co-trustee makes distribution decisions or income is paid in fixed shares with principal limited to health, education, support and maintenance? Which keeps it a non-grantor trust with the least risk?
- ASSUMPTION: The rehearsal runs on route R2 or R3 in grantor-routes.json passing grantor_check.py, so the Family Trust is its own taxpayer. Sole-trustee discretion (R1) is treated as a grantor trust under 674(a).
- Primary cite: IRC 674(a), 674(b)(5)(A) and 674(c), https://www.law.cornell.edu/uscode/text/26/674 (not read by the run that wrote this entry).
- What the text says (as read, not a conclusion): Section 674(a) is read as treating the grantor as owner where he or a nonadverse party can decide who benefits; 674(c) as excepting a power solely exercisable by trustees none of whom is the grantor and no more than half of whom are related or subordinate; 674(b)(5)(A) as excepting principal distributions limited by a reasonably definite standard in the instrument. Whether the drafted terms fit is for counsel.
- If counsel says otherwise: If counsel says neither route holds, the Family Trust is a grantor trust, its income is taxed to him, and the independent-trustee savings in flat_independent disappear; the stack version would revert to the grantor treatment already used in today and flat.
- Status: assumed, awaiting counsel

## Q4. Can the instrument split the trusteeship (administrative trustee and special distribution trustee) and who serves as independent distribution trustee?

- Key: `route-r2-split-trusteeship`
- Raised by: grantor-routes.json R2
- For: lawyer
- Question: Can the instrument split the trusteeship this way (administrative trustee and special distribution trustee) under the Illinois Trust Code, and who is a good independent distribution trustee at a fee the structure can carry?
- ASSUMPTION: The rehearsal runs on the split being allowed and on an unrelated individual distribution trustee at the modeled fee. Illinois law was not read for this entry.
- Primary cite: IRC 674(c), https://www.law.cornell.edu/uscode/text/26/674 (not read by the run that wrote this entry).
- What the text says (as read, not a conclusion): Section 674(c) is read as requiring that the distribution power be solely exercisable by trustees who are not the grantor and are not mostly related or subordinate. Illinois trust law on splitting duties is for the lawyer.
- If counsel says otherwise: If Illinois law or the available trustees do not allow it, R2 fails and the fee line changes; the structure falls back to R3 or loses its non-grantor status.
- Status: assumed, awaiting counsel

## Q5. Is his power to remove the distribution trustee limited to appointing an independent one?

- Key: `route-r2-removal-power`
- Raised by: grantor-routes.json R2; NEXT-MOVES.md move 3
- For: lawyer
- Question: Confirm my power to remove the distribution trustee is limited to appointing another independent trustee (Reg. 1.674(d)-2(a)).
- ASSUMPTION: The rehearsal runs on his removal power being limited to naming another independent trustee, as in route R2.
- Primary cite: Treas. Reg. 1.674(d)-2(a), https://www.law.cornell.edu/cfr/text/26/1.674(d)-2 (not read by the run that wrote this entry).
- What the text says (as read, not a conclusion): Paragraph (a) is read as saying a power to remove, substitute or add trustees may prevent the trust from qualifying under 674(c) or (d), and does not disqualify it if its exercise could not change the trust in a disqualifying way. Counsel reads the drafted power.
- If counsel says otherwise: If the power is wider, route R6 applies: the trust is a grantor trust and the non-grantor savings are lost.
- Status: assumed, awaiting counsel

## Q6. Should income be mandatory in fixed shares, and how do shares adjust for a death or after-born child?

- Key: `route-r3-fixed-shares`
- Raised by: grantor-routes.json R3
- For: lawyer
- Question: Should income be mandatory in fixed shares, and how do the shares adjust when a beneficiary dies or a new child is born (after-born children are the one addition the rules allow)?
- ASSUMPTION: The rehearsal runs on income paid out each year in fixed shares, with changes only for after-born or after-adopted children.
- Primary cite: Treas. Reg. 1.674(d)-2(b), https://www.law.cornell.edu/cfr/text/26/1.674(d)-2 (not read by the run that wrote this entry).
- What the text says (as read, not a conclusion): Paragraph (b) is read as making the listed exceptions unavailable if any person can add beneficiaries, except after-born or after-adopted children. How shares adjust on a death is for counsel.
- If counsel says otherwise: If shares need a flexible adjustment, route R7 applies and the trust may be a grantor trust; the fixed-share route would then need an independent trustee (R2).
- Status: assumed, awaiting counsel

## Q7. Do the powers he keeps cause gift or estate tax problems for the funder?

- Key: `route-r3-gift-estate`
- Raised by: grantor-routes.json R3; NEXT-MOVES.md move 3
- For: lawyer, then CPA
- Question: Does my holding a principal power under a health, education, support or maintenance standard cause estate or gift tax problems for me as the funder (sections not modeled here)?
- ASSUMPTION: The rehearsal runs on no gift or estate tax effect, which is not modeled. This is an assumption, not a finding.
- Primary cite: IRC 2036(a), https://www.law.cornell.edu/uscode/text/26/2036 (not read by the run that wrote this entry).
- What the text says (as read, not a conclusion): Section 2036(a) is read as including in the gross estate property transferred in trust where he retained the income or the right, alone or with another, to designate who enjoys the property or income. Gift-tax sections were not read here.
- If counsel says otherwise: If counsel finds an estate or gift effect, the assets could stay in his estate or the transfer be an incomplete gift, and the structure value would need a new line.
- Status: assumed, awaiting counsel

## Q8. Does a non-trustee distribution trust advisor satisfy the independent-trustee exception?

- Key: `route-r4-advisor`
- Raised by: grantor-routes.json R4; NEXT-MOVES.md move 3
- For: lawyer
- Question: Does a distribution trust advisor under 760 ILCS 3/808 who is not a trustee qualify for the 674(c) independent-trustee exception, or should the advisor be a co-trustee?
- ASSUMPTION: The rehearsal treats R4 as unsettled and does not rely on it; the advisor is assumed to be a co-trustee (R2). 760 ILCS 3/808 was not read for this entry.
- Primary cite: IRC 674(c), https://www.law.cornell.edu/uscode/text/26/674 (not read by the run that wrote this entry).
- What the text says (as read, not a conclusion): Section 674(c) is read as speaking of trustees; whether a non-trustee advisor counts is for counsel.
- If counsel says otherwise: If an advisor qualifies, R4 becomes usable and the founder keeps the trustee role without a co-trustee; if not, only the co-trustee form (R2) stands.
- Status: assumed, awaiting counsel

## Q9. How do we keep him and his family clear of self-dealing if the trust deducts payments to the foundation?

- Key: `route-r9-split-interest`
- Raised by: grantor-routes.json R9; NEXT-MOVES.md move 3
- For: lawyer
- Question: If the Family Trust deducts payments to the foundation under 642(c)(1), it becomes a 4947(a)(2) split-interest trust. How do we keep me and my family clear of self-dealing (4941) with that trust, and should the charitable share be segregated (4947(a)(2)(B))?
- ASSUMPTION: The rehearsal runs on the trust being treated as a split-interest trust under the private foundation rules if it deducts payments to the foundation, and on segregation being an open design choice.
- Primary cite: IRC 4947(a)(2), https://www.law.cornell.edu/uscode/text/26/4947 (not read by the run that wrote this entry).
- What the text says (as read, not a conclusion): Section 4947(a)(2) is read as reaching a trust with amounts for which a deduction was allowed; (a)(2)(B) as excluding amounts segregated from those for which no deduction was allowable. 4941 and 642(c) were not read for this entry.
- If counsel says otherwise: If counsel says it applies, every transaction between the trust and him or his family becomes a self-dealing question, and the charitable share would need to sit in a separate trust.
- Changes decision: Q15 (from Q9's trace): whether the set-aside to the foundation is made at all, since 4947(a)(2) lists 642(c) deductions and 4941 among the sections that then apply.
- Status: assumed, awaiting counsel

## Q10. How do distributions for minor children stay separate from his support duties?

- Key: `trust-support-677b`
- Raised by: NEXT-MOVES.md move 3
- For: lawyer, then CPA
- Question: If the trust pays for things I am legally obliged to provide any minor children, that income is taxed to me (677(b)). How should the document keep distributions to them separate from my support duties?
- ASSUMPTION: The rehearsal runs on no trust income being used for his legal support duties. The synthetic beneficiaries are the two adults.
- Primary cite: IRC 677(b), https://www.law.cornell.edu/uscode/text/26/677 (not read by the run that wrote this entry).
- What the text says (as read, not a conclusion): Section 677(b) is read as limiting when trust income used for a grantor's support obligation is taxed to him. Its full text was only partly retrieved; counsel reads it in full.
- If counsel says otherwise: If distributions to minors count as his support, that income is taxed to him and the retained-income and bracket results shift for those amounts.
- Status: assumed, awaiting counsel

## Q11. Is a 7 percent yield a fair stand-in for sizing the asset that clears break-even?

- Key: `asset-size-b1`
- Raised by: NEXT-MOVES.md move 4
- For: CPA or appraiser
- Question: Is a yield of about 7 percent a fair stand-in for what an asset of this kind earns after costs, so that about 150,000 a year of net income means an asset of roughly 2.1 million?
- ASSUMPTION: The rehearsal sizes the asset to clear the unrelated-individual-trustee break-even (149,500 a year in the base case; 146,900 lean, 137,200 asset_rental, 147,700 asset_business) and divides by `asset_yield_for_value` (0.07 in stack.json), giving about 2,135,700 in the base case. The 0.07 is an ASSUMPTION for perspective, not a market rate. With an independent professional trustee there is no break-even up to 1,000,000 a year, so no size is implied.
- Primary cite: none. No public source was read for this entry.
- What the text says (as read, not a conclusion): nothing was read. The break-even figures are the engine's own output on main; the yield is the stack.json assumption.
- If counsel says otherwise: If the right yield is higher or lower, the implied value moves in inverse proportion (for example 149,500 / 0.05 is about 2,990,000; 149,500 / 0.09 is about 1,661,100). The engine's `asset_yield_for_value` would change in stack.json.
- Status: assumed, awaiting counsel

## Q12. Which classes of asset (rental building, bought business, other) can credibly produce that income?

- Key: `asset-classes-b2`
- Raised by: NEXT-MOVES.md move 5
- For: CPA or appraiser
- Question: Which of a rental building, a bought operating business run by a hired manager, or a small portfolio of rental units can credibly net about 150,000 a year at the size move 4 implies, and what yield, sale multiple or SBA 7(a) loan terms should the rehearsal use for each?
- ASSUMPTION: The rehearsal runs on the two asset kinds the engine models (a rental building and a bought operating business) at the engine's assumed yields. No market data was read in this run: no cap rates, business sale multiples or SBA 7(a) terms.
- Primary cite: none. No public source was read for this entry.
- What the text says (as read, not a conclusion): nothing was read. Data that would settle it: published cap rates for the property type and region, published business sale multiples, and the SBA's published 7(a) program terms.
- If counsel says otherwise: If real yields or multiples differ from the engine's, the asset size needed, the financing cost and the asset_rental and asset_business scenarios would change, and a third class might replace one of the two.
- Status: assumed, awaiting counsel

## Q13. What must the Family Trust have before it can hold title to an asset?

- Key: `trust-title-c1`
- Raised by: NEXT-MOVES.md move 6
- For: lawyer
- Question: For a non-grantor Family Trust under route R2 or R3, what must exist before it can take title to an income-producing asset: instrument terms, trustee acceptance, EIN, Illinois situs, bank account, and who signs for the trust?
- ASSUMPTION: The trust is written under Illinois law with the trustee named per Q3 and Q11, gets its own EIN and its own bank account, and takes title only after those exist.
- Primary cite: IRS, Employer ID Numbers, https://www.irs.gov/businesses/small-businesses-self-employed/employer-id-numbers (read: trusts need an EIN except certain grantor-owned revocable trusts). Illinois Trust Code 760 ILCS 3 not read (page failed to load).
- What the text says (as read, not a conclusion): only the IRS EIN statement above. The page does not say how grantor status affects the exception.
- If counsel says otherwise: extra setup steps and fees (placeholders in stack.json) could be added to the structure cost, raising break-even.
- Status: assumed, awaiting counsel

## Q14. What other income will the two adult beneficiaries have, so their own tax brackets are known?

- Key: `beneficiary-income`
- Raised by: NEXT-MOVES.md move 7
- For: Dalaun, then CPA
- Question: Roughly what other yearly income will the two adult beneficiaries have, and at what level does a trust distribution to them cost more tax than it saves?
- ASSUMPTION: Each adult beneficiary has 46,080 a year of other income (BLS CE second-income-fifth average, `ce_us_quintiles_2025.second_quintile_income` in benchmarks-ce.json) and files single (`beneficiary_filing_status`).
- Primary cite: BLS Consumer Expenditures, https://www.bls.gov/news.release/cesan.nr0.htm (figure taken from benchmarks-ce.json; not re-fetched in this run). IRC 652(a) and 662(a) (beneficiaries taxed on distributed income) are the rules the engine applies; not re-read in this run.
- What the text says (as read, not a conclusion): nothing was read in this run beyond the repo's own figures. In a scratch run with 78,584 (third-fifth average) break-even with an unrelated individual trustee, base year, went from 149,500 to 198,000.
- If counsel says otherwise: break-even, and so the asset size, moves with the beneficiaries' brackets (about 32 percent for the third-fifth figure). A beneficiary in a high bracket could make the trust's retained-income bracket compare differently.
- Status: assumed, awaiting counsel

## Q15. How is a 10 percent set-aside to the foundation taxed, and does it make the trust a split-interest trust?

- Key: `pipeline-set-aside`
- Raised by: backlog item R7; stack version `steward_r2_pipeline`
- For: CPA, then lawyer
- Question: If the Family Trust pays 10 percent of its distribution to the foundation as a set-aside deduction under 642(c)(1), how is that taxed to the trust and the beneficiaries, and does it make the trust a 4947(a)(2) split-interest trust? (See Q9 for the self-dealing side.)
- ASSUMPTION: The 10 percent share is a placeholder for Dalaun's own choice. The trust pays it from gross income and deducts it in full; the beneficiaries are taxed only on the other 90 percent of the distribution; the trust is treated as split-interest (Q9). The rehearsal's engine does not apply the 642(c) percentage limits or the 4942 distribution rules to this flow.
- Primary cite: IRC 642(c)(1), https://www.law.cornell.edu/uscode/text/26/642 and IRC 4947(a)(2), https://www.law.cornell.edu/uscode/text/26/4947 (neither read by the run that wrote this entry).
- What the text says (as read, not a conclusion): nothing was read in this run beyond the repo's own notes.
- If counsel says otherwise: if the set-aside is not deductible as modeled, or the share must be a different amount, the program output and the trust's and beneficiaries' tax change, and the split-interest rules may require a separate charitable trust.
- Changes decision: Q9 (from Q15's trace): whether the charitable share is segregated into a separate trust, since 4947(a)(2)(B) turns on segregation.
- Status: assumed, awaiting counsel

## Q16. How should the Family Trust hold the asset, and what must be on paper for the checks?

- Key: `asset-holding-c2`
- Raised by: NEXT-MOVES.md move 8
- For: lawyer, then CPA
- Question: If the Family Trust owns an LLC and the LLC owns the income-producing asset, what must be in the trust instrument, the operating agreement and the trustee's records so checks S2 to S9 and S12 pass on documents, and does the founder, as an R2 or R3 trustee, also managing the LLC cause a problem?
- ASSUMPTION: The Family Trust owns 100 percent of one LLC per asset; the LLC contracts, banks and files as a business; the founder is its manager paid market wages as an employee. This follows `07-structure-integrity-checks.md` (SK2 against SK1).
- Primary cite: none. No primary source was read for this entry (Treas. Reg. 301.7701-3 on LLC classification would be the first to read).
- What the text says (as read, not a conclusion): nothing was read. The repo's own check definitions are the only basis.
- If counsel says otherwise: the holding design, the fees in stack.json and which checks stay amber would change; break-even could rise if extra entities or filings are needed.
- Status: assumed, awaiting counsel

## Q17. How big must the asset be to fund a 10 percent Foundation share and still beat doing nothing?

- Key: `asset-size-pipeline`
- Raised by: NEXT-MOVES.md move 9; backlog item R8
- For: CPA or appraiser
- Question: If 10 percent of the Family Trust's distribution goes to the foundation (see Q15), what yearly net asset income, and so what asset size, makes the structure pay for itself, and is the share worth that size?
- ASSUMPTION: The asset nets 350,000 a year, the engine's base-case break-even for `steward_r2_pipeline` with an unrelated individual trustee (343,600) rounded up to the next 10,000. At the assumed 0.07 yield (stack.json, not a market rate) that is an asset of about 5,000,000. Set from the break-even only, never adjusted to make a version pass.
- Primary cite: none new. The tax rules are those of Q15 (IRC 642(c)(1), 4947(a)(2)), not read in this run.
- What the text says (as read, not a conclusion): nothing was read in this run.
- If counsel says otherwise: a different share, a different set-aside treatment (Q15) or different beneficiary brackets (Q14) moves the break-even, and the engine's search for it is not monotone for this version, so its figure is a first crossing.
- Status: assumed, awaiting counsel

## Q18. What financing, lender-consent and insurance questions does an LLC held by the Family Trust raise?

- Key: `financing-title-c3`
- Raised by: NEXT-MOVES.md move 10
- For: lawyer
- Question: If the Family Trust owns an LLC that buys a rental building or an operating business with a loan, will a lender lend to a trust-owned LLC, who must guarantee the loan, and what insurance must name whom?
- ASSUMPTION: The founder, as the LLC's manager, may be asked to guarantee personally, and the lender must consent to the trust's ownership. A guarantee by the founder is a fact the checks (S1 to S17) and the grantor test must be re-run on; the rehearsal does not model it.
- Primary cite: SBA 7(a) program page, https://www.sba.gov/funding-programs/loans/7a-loans (read 2026-11-24). It lists "Be an operating business" and "Operate for profit" and links a list of ineligible business types.
- What the text says (as read, not a conclusion): the page says nothing about trusts, personal guarantees or down payments. Those rules were not read.
- If counsel says otherwise: a lender that refuses a trust-owned LLC, or a guarantee that counts as the founder's own power or benefit, would change C2's holding design.
- Status: assumed, awaiting counsel
