# 07. Structure integrity checks: designing away from abusive trust patterns

[Back to the rehearsal overview](README.md)

The ledger gates in the [spec](03-ab-rehearsal-spec.md) test one spending line at a time. These checks test the **structure itself**: every version of the stack the twin rehearses must pass them before any of its routes are scored. They come from the IRS's own descriptions of abusive trust arrangements, so a version that passes them has designed away from those patterns on the facts, not by avoiding words.

The goal is durable; the structure is not. Any entity, trust or flow in today's stack can be replaced if a check says so.

**This is design and education, not legal or tax advice.**

## Sources (read 2026-11-20, quoted verbatim)

| Short name | Source |
|---|---|
| N97-24 | IRS Notice 97-24, Certain Trust Arrangements, 1997-16 I.R.B. 6. https://www.irs.gov/pub/irs-drop/pub_n_97.24.pdf |
| TP | IRS, Abusive trust tax evasion schemes: Talking points. https://www.irs.gov/businesses/small-businesses-self-employed/abusive-trust-tax-evasion-schemes-talking-points |
| QA | IRS, Abusive trust tax evasion schemes: Questions and answers. https://www.irs.gov/businesses/small-businesses-self-employed/abusive-trust-tax-evasion-schemes-questions-and-answers |
| F-I to F-IV | IRS, Abusive trust tax evasion schemes: Facts, Sections I to IV. https://www.irs.gov/businesses/small-businesses-self-employed/abusive-trust-tax-evasion-schemes-facts-section-i (and -section-ii, -iii, -iv) |
| L-I, L-V | IRS, Abusive trust tax evasion schemes: Law and arguments, Sections I and V. https://www.irs.gov/businesses/small-businesses-self-employed/abusive-trust-tax-evasion-schemes-law-and-arguments-section-i (and -section-v) |

Long passages appear as exact pieces joined by "...".

## The rule behind every check: facts, not labels

The IRS says it plainly: "Mere association of the term "trust" with a financial arrangement does not make it a legitimate trust" (TP), and "No matter how carefully written the trust documents are, if the intent is to evade taxes," ... "the trust will be treated as abusive." (TP). The controlling doctrine: "Substance--not form--controls taxation." (N97-24, III.1).

So the twin enforces three rules:

1. **Checks read fact fields only.** Who signs, who decides, whose account, who lives in the property, what was paid, to whom, at what price, reported how. An entity's name or type label is never an input.
2. **Rename invariance.** Before every check run, the twin replaces every entity name and label with a random id. Results must be identical. A version that changes verdict when renamed is a bug in the checks.
3. **Renaming fixes nothing.** A candidate change that only renames ("call it an LLC", "drop the word trust") is rejected by the optimizer, the same way guard 4 in the spec rejects label-only routes.

## The checks

Each check is a yes/no question. **Yes passes.** A question the evidence can't answer is amber: it blocks the version and becomes a question for the attorney or CPA.

### Control and the trustee

**S1. Is the tax position consistent with who actually controls the assets?**
If the founder keeps control or benefit, the trust is reported as his (grantor trust, income on his return). Only a trust he has truly let go of may be treated as a separate taxpayer.
- Facts read: who can direct distributions, investments and sales; who can remove the trustee; how each trust files.
- Source: "if the owner of property transferred to a trust retains an economic interest in," ... "or control over, the trust, the owner is treated for income tax purposes as the owner of the trust property," (N97-24, III.2). "Under non-grantor trust arrangements, you must give up significant control over income and assets." (TP)
- The abuse pattern: "the original owner of the assets that are nominally subject to the trust effectively retains authority" ... "to cause the financial benefits of the trust to be directly or indirectly returned or made available to the owner." (N97-24, II)

**S2. Does the trustee exercise independent control, and not simply carry out the founder's directions?**
- Facts read: trustee's identity and relationship to the founder; a decision log showing the trustee applying the instrument, including at least one request declined or modified; who prepares and approves trust transactions.
- Source: "A trustee is designated to hold legal title to the trust property, to exercise independent control over it," ... "and to be responsible for its management." (TP). The abuse pattern: "the trustee may be the promoter, or a relative or friend of the owner who simply carries out the directions of the owner" ... "whether or not permitted by the terms of the trust." (N97-24, II)
- Note: a founder can lawfully be trustee of his own grantor trust. S2 matters for any trust claimed to be separate from him (S1).

**S3. Are the trust's payment tools in the trustee's hands only?**
- Facts read: signers on each trust account; names on any card; any signature stamp.
- Source: "Often, the trustee gives the owner checks that are pre-signed by the trustee," ... "checks that are accompanied by a rubber stamp of the trustee's signature, a credit card or a debit card" (N97-24, II)

**S4. Do the trust's actual transactions follow its own terms?**
- Facts read: each distribution matched to the instrument's standard; trustee minutes.
- Source: Markosian: "the trust was a sham because the parties did not comply with the terms of the trust" (N97-24, III.1). "The trustee ... is required to administer the trust on behalf of the beneficiaries" ... "according to the express terms and provisions of the trust agreement." (QA)

**S5. After the transfer, is the founder's relationship to the property materially different?**
- Facts read: who uses the property; who pays its costs; whether rent is set at market and actually paid; whether the founder's day-to-day role changed.
- Source: Markosian: "the relationship of the grantors to the property transferred did not differ in any material aspect" ... "after the creation of the trust" (N97-24, III.1). Business trust pattern: "In reality, through trustees or other entities controlled by the taxpayer, he or she still runs the day-to-day activities" (F-III)

### Expenses and income

**S6. Does every entity in the version deduct zero personal, living, family or education costs of the founder or family, and zero cost of setting up trusts?**
- Facts read: every deducted ledger line, joined to its domain in the [taxonomy](02-expense-domain-taxonomy.md).
- Source: "Personal expenses such as those for home maintenance, education, and personal travel are not deductible" ... "unless expressly authorized by the tax laws. See section 262." ... "The courts have consistently held that non-deductible personal expenses cannot be transformed into deductible expenses" ... "by the use of trusts." ... "Furthermore, the costs of creating these trusts are not deductible." (N97-24, III.5). "personal living expenses such as food, utilities, recreational expenses, children's education," ... "are not allowed as a trust deduction any more than as an individual deduction." (QA)
- This is gate G1, lifted to the whole structure: a version where any entity takes such a deduction fails as a version, not just on that line.

**S7. Is no family residence or furnishings depreciated, and no stepped-up basis claimed on a transfer to a trust the founder controls?**
- Facts read: depreciation schedules of every entity; basis claimed on every asset received from the founder.
- Source: "The trust claims the exchange results in a stepped-up basis for the property, while the owner reports no gain." (N97-24, Example 3). "The trust deducts depreciation and the expenses of maintaining and operating the residence" ... "including gardening, pool service and utilities." (F-III). Consequence: "the tax basis of property transferred to the trust would not be stepped-up for depreciation purposes." (N97-24, III.2)

**S8. Is every rent, fee, sale or loan between entities in the stack priced at market, documented, for services or property actually provided, and actually paid?**
- Facts read: for each related-party flow, the contract, the benchmark, the service or use record, and the payment.
- Source: "Funds may flow from one trust to another trust by way of rental agreements, fees for services," ... "purchase and sale agreements, and distributions." (N97-24, I). "The equipment trust is formed to hold equipment that is rented or leased to the business trust, often at inflated rates." ... "The service trust is formed to provide services to the business trust, often for inflated fees." (N97-24, Example 2). "in most cases, little or no rent is actually paid." (N97-24, Example 3). Pricing rule: IRC 482 (register B9).

**S9. Is income taxed to whoever earned it?**
- Facts read: who performed the services; whose name and taxpayer number are on the contract and invoice; where the payment landed.
- Source: "Income that is earned by one person cannot be assigned to another for federal income tax purposes." (QA). "Income remains taxable to the individual who earns it. Lucas v. Earl, 281 U.S. 111 (1930)." (TP)

**S10. Does the version claim no reduction of the founder's self-employment or payroll taxes from the arrangement itself?**
- Facts read: how the founder is paid for work he does for the operating companies, and whether self-employment or payroll tax is paid on it.
- Source: "the owner claims the arrangement reduces or eliminates the owner's self-employment taxes" (N97-24, Example 1). Promoter claim the IRS lists as false: "Establishing a trust will reduce or eliminate income taxes or self-employment taxes." (TP)

### Shape of the stack

**S11. If income passes through more than one entity, does each layer have its own non-tax purpose, and does each layer's deductions stand on their own?**
- Facts read: the flow graph of income from where it is earned to where it rests; each layer's purpose statement and its own activity.
- Source: "These arrangements frequently involve more than one trust, each holding different assets of the taxpayer" (N97-24, I). "Trusts involved in both schemes are vertically layered with each trust distributing income to the next layer." ... "The goal of this layered distribution of income is to reduce taxable income to nominal amounts." (TP). The end point: "the U.S. owner of one or more abusive trusts establishes a trust (the "final trust")" ... "that holds trust units of the owner's other trusts and is the final distributee of their income." (N97-24, Example 5)
- A chain is not unlawful by itself. It means S1 to S10 must pass at every layer, and the twin never scores a chain green on its shape.

**S12. Is a business run by an entity classified as a business, not filed as a trust?**
- Facts read: what the entity does; how it files.
- Source: "The Internal Revenue Code generally does not allow trusts to operate a trade or business." (TP). Reg. 301.7701-4(b) (register A3, gate G10).

**S13. Is any charity in the version real: exempt (or with its exemption application filed), with a genuinely charitable purpose, and paying nothing for the personal, education, living or recreation costs of the founder or family?**
- Facts read: exemption letter or filed Form 1023; program records; every payment's recipient and purpose.
- Source: "Payments are made to charitable organizations; however, in fact, the payments are principally for the personal" ... "educational, living, or recreational expenses of the owner or the owner's family." (N97-24, Example 4). "A genuine charity must benefit in order to claim a valid charitable deduction." ... "supposed charitable payments made by a trust are not deductible charitable contributions" ... "where the payments are really for the benefit of the owner or the owner's family members." (N97-24, III.6). "These alleged charitable organizations often are not qualified and have no IRS exemption letter; hence, contributions are not deductible." (F-III)
- The Foundation's self-dealing rules (4941) are stricter still; this check is the floor, not the ceiling.

**S14. Are all trusts domestic, or is every foreign transfer and distribution reported?**
- Facts read: each trust's domestic or foreign status; Forms 3520 and 3520-A filed.
- Source: "a U.S. person who directly or indirectly transfers property to a foreign trust is treated as the owner of that property" ... "if there is a U.S. beneficiary of the trust." (N97-24, III.2). "a U.S. person that fails to report a transfer of property to a foreign trust or the receipt of a distribution from a foreign trust" ... "is subject to a tax penalty equal to 35 percent of the gross value of the transaction." (N97-24, III.7)

### Consistency over time

**S15. Is every transfer into the stack reported the same way by both sides?**
A gift is a gift on both returns (with a Form 709 where required); a sale is a sale, with gain to the seller and cost basis to the buyer.
- Facts read: how each transfer is characterized on the founder's return and the receiving entity's return.
- Source: "The trust takes the position that the trust has "purchased" the equipment with a known value (its fair market value)" ... "The owner, on the other hand, takes the inconsistent position that the value of the trust units received cannot be determined," (N97-24, Example 2). "The parties claim inconsistent tax treatment for the trust and the owner" (N97-24, Example 3)

**S16. If the founder keeps the use or income of property until death, does the version count it in his estate?**
- Facts read: retained use, enjoyment or income; the version's estate assumption.
- Source: "if the owner retains until the owner's death the use of, enjoyment of, or income from the property placed in a trust," ... "the property will be subject to federal estate tax when the transferor dies. Section 2036(a)." (N97-24, III.4). Pattern: "the trust units are supposed to be canceled at death or "sold" at a nominal price to the owner's children," (N97-24, Example 1)

### The reason the version exists

**S17. Is the version's stated purpose free of every promoter claim the IRS lists as false?**
- Facts read: the written purpose of each entity and of each optimization step.
- Claims that fail it (TP, verbatim): "Establishing a trust will reduce or eliminate income taxes or self-employment taxes." / "You can transfer your income into a trust, thus eliminating income taxation on that income." / "You will retain complete control over your income and assets with the establishment of a trust." / "Taxpayers may deduct personal expenses paid by the trust on their tax return." / "Taxpayers can depreciate their personal residence and furnishings and take them as deductions on their tax return."
- Purposes the IRS names as legitimate: "Legal trusts are used in such matters as estate planning; to facilitate the genuine charitable transfer of assets;" ... "to hold assets for minors and those unable to handle their financial affairs." (TP)

## What failing costs (why the checks block a run)

- "Civil sanctions can include a fraud penalty up to 75% of the underpayment of tax attributable to the fraud" ... "in addition to the taxes owed." (TP)
- "Criminal convictions may result in fines up to $250,000 and/or up to five years in prison for each offense." (TP)
- "Should a taxpayer choose to participate in an abusive trust scheme, the taxpayer will not be shielded from potential civil and criminal sanctions." (TP)
- "The Tax Court, other federal courts, and bankruptcy courts have been virtually unanimous in finding for the Service where trusts are created to avoid income taxes." (TP)

So in the score, a version with any red structure check has no score. It is not a cheaper version with a risk discount; it is out.

## Today's stack, in roles, against the checks

What is known: a business trust owns the operating company; the management company manages the operating company; the Family Trust is the business trust's beneficiary; the Foundation is the Family Trust's beneficiary; the founder separately owns the transport company and the building. Who the trustees are, how each trust files, and whether the Foundation's exemption application was filed are **not known**. Unknown facts are amber, never pass and never fail.

| Check | Today | Why | Candidate method change (to rehearse, not a conclusion) |
|---|---|---|---|
| S1 Control matches tax position | Amber | Trustees and filing positions unknown | Either report each trust the founder controls as his grantor trust, or give it a trustee he does not control |
| S2 Independent trustee | Amber | Trustee unknown | For any trust treated as separate from him: a professional or corporate trustee, not related or subordinate to him (672(c)), with a decision log |
| S3 Payment tools | Amber | Account signers unknown | Trustee-only signers and cards on trust accounts |
| S4 Terms followed | Amber | No trust transaction records seen | Trustee minutes; every distribution tied to the instrument's standard |
| S5 Relationship changed | Amber, leaning red for the business trust | The founder runs the operating company day to day through the management company, which matches the pattern the IRS describes | Hold the business in an ordinary business entity (LLC or corporation) and pay the founder market wages for the work he does. That removes the pattern instead of defending it |
| S6 No personal deductions | Pass by design | Arm B never deducts a personal line (gate G1, K2, K11) | Keep |
| S7 No residence depreciation or step-up | Pass by design | No residence is in a trust; the building is on Schedule E | Keep. If the building ever moves into a trust, it moves at carryover basis with no step-up claimed |
| S8 Arm's-length flows | Amber | The management fee from the operating company has no benchmark on file | A written services agreement, a market benchmark, monthly service records, and real payments |
| S9 Income to who earned it | Amber | Who contracts and invoices for each line of work not confirmed | Each contract in the name of the entity that does the work; founder paid wages for his share |
| S10 No self-employment tax claim | Pass by design | The twin never counts a self-employment tax saving from the arrangement | Keep |
| S11 Layering | Amber | Business trust to Family Trust to Foundation is a vertical chain; its shape matches the IRS's description | Rehearse the flat alternative: the Family Trust (or the founder) owns the business entity directly; the Foundation is funded by gifts or a split-interest trust, not as the end of an income chain |
| S12 Business not filed as a trust | Amber, leaning red | A trust that runs a business is generally a business entity (K10) | Same change as S5 |
| S13 Real charity | Amber | Exemption application status unknown | File (or confirm) the exemption application before the Foundation receives anything; no payment for any family cost (K1, K13) |
| S14 Domestic or reported | Amber | Whether any trust was ever formed or treated as foreign is not confirmed | Confirm domestic status for every trust; clean up any foreign-trust filings with counsel |
| S15 Consistent transfers | Amber | How assets reached each trust is not documented | Paper every transfer as a gift (with Form 709) or a sale (with gain), the same on both sides |
| S16 Estate consistency | Not yet tested | The twin does not model estate exclusion yet | When it does, any property he keeps using stays in his estate |
| S17 Stated purpose | Pass | The written goals (programs, legacy, asset protection by real transfer) match purposes the IRS calls legitimate; none of the false claims is a goal | Keep each entity's purpose in writing |

**The one change that clears the most checks:** replace the business trust with an ordinary business entity that pays the founder market wages. It removes the IRS's first example pattern (S5, S11, S12) instead of defending it, and it fixes the classification problem the register already found. The Family Trust then holds the business entity's interests as a real asset, which is what the asset-to-program pipeline needs anyway. This is a candidate for the twin to rehearse and for counsel to confirm, not a step to take.

## Eval cases

These are synthetic structure versions with clear answers. The twin must reproduce every one, and must give the same verdicts after every name is randomized. Machine-readable: [structure-check-cases.ttl](structure-check-cases.ttl).

| Case | Structure version | Expected | Fails or passes |
|---|---|---|---|
| SK1 | A trust owns the business; the founder, as trustee, runs it day to day; the trust files as a trust and deducts payments to the founder's other trusts | Fail | S1, S5, S12 |
| SK2 | Same business owned by an LLC that the Family Trust holds; founder paid market wages with payroll tax; LLC files as a business | Pass on S5, S9, S10, S12 | — |
| SK3 | Family residence moved to a trust; family keeps living there; little rent paid; trust deducts depreciation, utilities and upkeep | Fail | S5, S6, S7, S8 |
| SK4 | Trustee is the founder's relative who signs whatever he sends; founder holds pre-signed trust checks; trust is reported as a separate taxpayer | Fail | S1, S2, S3 |
| SK5 | Professional trustee, unrelated to the founder; decision log shows a declined distribution request; trust reported as a separate taxpayer | Pass on S1, S2, S3 | — |
| SK6 | Management company bills the operating company a fee with no services performed and no benchmark | Fail | S8 |
| SK7 | Same fee with a written agreement, market benchmark, service records and payments | Pass on S8 | — |
| SK8 | Founder signs a client contract personally; payment deposited to a trust, which reports it | Fail | S9 |
| SK9 | Organization with no exemption letter and no filed application receives gifts deducted as charitable | Fail | S13 |
| SK10 | Foundation pays a family member's school tuition | Fail | S13 (and 4941) |
| SK11 | Three entities in a chain, each paying the next, each deducting the payment, last one paying almost no tax, none with its own activity | Fail | S11 |
| SK12 | Foreign trust with a U.S. beneficiary; no Form 3520 filed | Fail | S14 |
| SK13 | Asset transferred to a trust; trust claims fair market value basis; founder reports no gain and no gift | Fail | S15, S7 |
| SK14 | Founder keeps living in a house placed in a trust until death; version assumes it is out of his estate | Fail | S16 |
| SK15 | SK1 with every name and label replaced by random ids | Same verdicts as SK1 | Rename invariance |
| SK16 | SK3 with the trust renamed "Legacy Holdings LLC" and no fact changed | Same verdicts as SK3 | Renaming fixes nothing |

## Not found in the sources read

- None of the IRS pages read names the Markosian factors "independent trustee" or "economic interest did not pass" in those words; the Markosian factors quoted are noncompliance with the trust's terms and an unchanged relationship to the property. S2 rests on the IRS's own statements about trustees instead.
- None of the pages read uses the phrases "pure trust" or "constitutional trust".
- The IRS memorandum AM 2023-006, linked from the Talking points and Facts pages, was not read.
