# Packet B memo: the tax result and the asset around the trust

Research for counsel review, not legal advice.

Packet B covers what the trust's terms do to tax, the asset that would pay for the structure, and the foundation share. It is for the CPA and, for Q3, Q8, Q9, Q15 and Q16, the lawyer.


## What packet A rests on from packet B

Packet A's trustee terms rest on packet B's answers to Q3 and Q8. Whether the Family Trust stays non-grantor depends on who decides distributions: if the founder (or his spouse) decides who benefits with no exception that fits, IRC 674(a) makes it a grantor trust and the savings below disappear. The A terms that depend on this:

- The independent distribution trustee and the split trusteeship (Q4): they only work if Q8's answer says an independent trustee, or a non-trustee advisor, satisfies the 674(c) exception.
- The founder's power to remove that trustee (Q5): its limit matters only while the independent-trustee route is what keeps the trust non-grantor.
- Mandatory income in fixed shares and a health, education, support and maintenance (HEMS) standard for principal (Q6): this is the second route (R3), and it rests on Q3's reading of 674(b)(5)(A).
- The powers he keeps as trustee and the estate and gift tax result (Q7), and the payout rule (Q2): both are drafted after B's answers fix who decides.
- Who is trustee, and who signs, before the trust holds title (Q13): the same trustee terms again.

If packet B answers Q3 or Q8 differently, these A terms are redrafted. They are not settled by packet A alone.

Illinois situs for the Family Trust is the research's working assumption, not a finding. Q4, Q8 and Q13 each carry `- Assumes: Illinois situs for the Family Trust (see Q22)`; if Q22 picks Wyoming or Delaware, those answers are redrafted under that state's law.

## Synthetic figures

All figures come from the seeded synthetic year (`rehearsal/synthetic`), not anyone's real money. Every scenario figure here is an engine output on assumptions listed in `counsel-queue.md`. Run on 2026-11-25, 7 of 7 scorecard checks pass, 8 of 17 structure checks pass for the steward versions (the other 9 are amber until documents exist, none red).

- Base year, doing nothing versus the structure: the structure costs 6,015 a year (structure gap).
- Break-even extra asset income, unrelated individual trustee: 149,500 a year (route R2 or R3); with a professional trustee none up to 1,000,000.
- With a 10 percent Foundation share (route R2): break-even 343,600 a year.
- `asset_sized` (150,000 a year of asset income, ASSUMPTION): route R2 beats doing nothing by 1,592 a year.
- `asset_sized_pipeline` (350,000 a year, ASSUMPTION): route R2 beats doing nothing by 26,384 a year; with the 10 percent Foundation share, by 2,029.

## Questions in packet B

- **Q1. Do the rentals, and a bought business run by a hired manager, count as passive?** Confidence: likely.
  - Lawyer decides: Whether his own facts (hours, who runs the business) meet material participation or the real estate professional test; the CPA decides, the statute's tests are traced below.
  - Trace file: [research/Q1.md](../research/Q1.md)
- **Q3. Keep the Family Trust non-grantor while he stays its steward** Confidence: likely.
  - Lawyer decides: Whether the drafted terms, including who counts as related or subordinate, actually fit the 674(c) or 674(b)(5)(A) exception.
  - Trace file: [research/Q3.md](../research/Q3.md)
- **Q8. Does a non-trustee distribution trust advisor satisfy the independent-trustee exception?** Confidence: open. Illinois claim pending, needs Dalaun (1 claim).
  - Lawyer decides: Whether a non-trustee advisor is treated as a trustee for 674(c), and how 760 ILCS 3/808 defines the advisor's role.
  - Trace file: [research/Q8.md](../research/Q8.md)
- **Q9. How do we keep him and his family clear of self-dealing if the trust deducts payments to the foundation?** Confidence: likely.
  - Lawyer decides: Whether the trust is split-interest on its terms, whether to segregate the charitable share into a separate trust, and how each transaction with the founder's family is cleared.
  - Trace file: [research/Q9.md](../research/Q9.md)
- **Q11. Is a 7 percent yield a fair stand-in for sizing the asset that clears break-even?** Confidence: open.
  - Lawyer decides: Not a legal question; the CPA or an appraiser must supply a market yield. Nothing read here gives one.
  - Trace file: [research/Q11.md](../research/Q11.md)
- **Q12. Which classes of asset (rental building, bought business, other) can credibly produce that income?** Confidence: open.
  - Lawyer decides: Which class fits; the CPA or appraiser supplies market yields and multiples, which no authority read here gives. The SBA terms are traced below.
  - Trace file: [research/Q12.md](../research/Q12.md)
- **Q14. What other income will the two adult beneficiaries have, so their own tax brackets are known?** Confidence: open.
  - Lawyer decides: The beneficiaries' real other income is a fact for Dalaun and the CPA; the rules below only say that distributed income is taxed to them.
  - Trace file: [research/Q14.md](../research/Q14.md)
- **Q15. How is a 10 percent set-aside to the foundation taxed, and does it make the trust a split-interest trust?** Confidence: likely.
  - Lawyer decides: Whether the instrument's wording meets 642(c)(1) (paid under the governing instrument, from gross income), and whether the trust is split-interest.
  - Trace file: [research/Q15.md](../research/Q15.md)
- **Q16. How should the Family Trust hold the asset, and what must be on paper for the checks?** Confidence: open.
  - Lawyer decides: Whether the founder as trustee and paid LLC manager is acceptable, and what the operating agreement must say.
  - Trace file: [research/Q16.md](../research/Q16.md)
- **Q17. How big must the asset be to fund a 10 percent Foundation share and still beat doing nothing?** Confidence: open.
  - Lawyer decides: Whether the 10 percent share is worth its cost; the size itself is an engine output and a yield assumption, which no authority read here gives.
  - Trace file: [research/Q17.md](../research/Q17.md)
- **Q18. What financing, lender-consent and insurance questions does an LLC held by the Family Trust raise?** Confidence: open.
  - Lawyer decides: Whether a lender will accept a trust-owned LLC, whether the founder must guarantee, and how a guarantee bears on the non-grantor result; insurance naming was not researched.
  - Trace file: [research/Q18.md](../research/Q18.md)
- **Q22. Which state's law should govern the Family Trust, and where should it be administered?** Confidence: open. Illinois, Wyoming and 35 ILCS 5/1501 claims pending, needs Dalaun (3 claims).
  - Lawyer decides: Which state governs and where the trust is administered, whether the founder's Illinois residence makes it an Illinois resident trust whatever its state, and what an in-state trustee or agent is required.
  - Trace file: [research/Q22.md](../research/Q22.md)

## Pending Illinois text

The Illinois Trust Code pages (760 ILCS 3, Articles 4, 5, 8 and 12) would not load for the research runs. Claims that rest on them are marked `pending, needs Dalaun` in the research files and listed in [../NEEDS-DALAUN.md](../NEEDS-DALAUN.md). Q4, Q8 and Q13 are affected. Nothing here treats them as traced.

## What this memo does not do

It does not decide any question. Each `likely` or `open` question above needs a lawyer or CPA. Working assumptions are rehearsal choices, labelled ASSUMPTION in `counsel-queue.md`, and never legal or tax advice.
