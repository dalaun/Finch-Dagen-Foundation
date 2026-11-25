# Packet A memo: the trust terms and how they are written

Research for counsel review, not legal advice.

Packet A covers the terms of the Family Trust itself: who the trustees are, how income is paid out, and what powers the founder keeps. It is for the lawyer who drafts the instrument.

## Coverage flags, every A question

Stated first so the reader can see which A questions could read as a business or investment interest:

- Q2: none
- Q4: none
- Q5: none
- Q6: none
- Q7: none
- Q10: none
- Q13: the trust would later hold LLC interests in a business or rental, which could read as a business or investment interest.

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

## Questions in packet A

- **Q2. Will the Family Trust pay out all of its income each year, or keep part of it?** Confidence: likely.
  - Lawyer decides: Whether the instrument makes the payout mandatory or discretionary; the CPA then reads the tax result.
  - Trace file: [research/Q2.md](../research/Q2.md)
- **Q4. Can the instrument split the trusteeship (administrative trustee and special distribution trustee) and who serves as independent distribution trustee?** Confidence: open. Illinois claim pending, needs Dalaun (1 claim).
  - Lawyer decides: Whether Illinois law allows the split and who can serve as the independent distribution trustee.
  - Trace file: [research/Q4.md](../research/Q4.md)
- **Q5. Is his power to remove the distribution trustee limited to appointing an independent one?** Confidence: likely.
  - Lawyer decides: Whether the drafted removal power is limited enough that its exercise could not change the trust in a disqualifying way.
  - Trace file: [research/Q5.md](../research/Q5.md)
- **Q6. Should income be mandatory in fixed shares, and how do shares adjust for a death or after-born child?** Confidence: open.
  - Lawyer decides: How shares adjust on a death; the after-born exception is traced below.
  - Trace file: [research/Q6.md](../research/Q6.md)
- **Q7. Do the powers he keeps cause gift or estate tax problems for the funder?** Confidence: open.
  - Lawyer decides: Whether the powers the founder keeps as trustee (route R2 or R3) pull trust property into his estate or make his transfers incomplete gifts; the standard-limited power cases were not found in the pages read.
  - Trace file: [research/Q7.md](../research/Q7.md)
- **Q10. How do distributions for minor children stay separate from his support duties?** Confidence: likely.
  - Lawyer decides: How the instrument words the trustee's power so that distributions never discharge his legal support duty, and whether his state law treats a given expense as support.
  - Trace file: [research/Q10.md](../research/Q10.md)
- **Q13. What must the Family Trust have before it can hold title to an asset?** Confidence: open. Illinois claim pending, needs Dalaun (1 claim).
  - Lawyer decides: What the Illinois instrument, trustee acceptance and signing authority must contain; the federal EIN step is traced below.
  - Trace file: [research/Q13.md](../research/Q13.md)
- **Q23. Does the Family Trust, or an Illinois Foundation, have to register or report to the Illinois Attorney General?** Confidence: open. Illinois claim pending, needs Dalaun (1 claim). Coverage flag: none
  - Lawyer decides: Whether naming the Foundation as a beneficiary makes the Family Trust (or its set-aside) a charitable trust holding assets for a charitable purpose in Illinois, and so registrable.
  - Trace file: [research/Q23.md](../research/Q23.md)

## Pending Illinois text

The Illinois Trust Code pages (760 ILCS 3, Articles 4, 5, 8 and 12) would not load for the research runs. Claims that rest on them are marked `pending, needs Dalaun` in the research files and listed in [../NEEDS-DALAUN.md](../NEEDS-DALAUN.md). Q4, Q8 and Q13 are affected. Nothing here treats them as traced.

## What this memo does not do

It does not decide any question. Each `likely` or `open` question above needs a lawyer or CPA. Working assumptions are rehearsal choices, labelled ASSUMPTION in `counsel-queue.md`, and never legal or tax advice.
