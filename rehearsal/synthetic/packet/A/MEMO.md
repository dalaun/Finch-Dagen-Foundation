# Packet A memo: the trust terms and how they are written

Research for counsel review, not legal advice.

Packet A covers the terms of the Family Trust as a personal irrevocable trust: who the trustee and the independent co-trustee are, who the beneficiaries are (the Foundation and family members), how income is paid out, what powers the founder keeps, and the paperwork to fund it (a certification of trust, deeds and title). It is for the lawyer who drafts the instrument. All figures are SYNTHETIC. Roles, not names.

## The trust

- An irrevocable trust, the Family Trust, funded by the founder's gift (Q7).
- Trustee: the founder serves as the administrative trustee; an independent co-trustee or distribution trustee decides distributions (Q4, Q5, Q8). Who that is, and the cost, is Q28 to Q31.
- Beneficiaries: the Foundation (a set-aside share, Q15, Q33) and family members, adult and minor (Q10, Q27, Q29).
- Income terms: mandatory fixed shares or discretionary payout (Q2, Q6).
- To hold an asset it needs an employer identification number, a signed instrument, trustee acceptance, and a certification of trust for banks and title companies (Q13).

## Decisions only Dalaun makes

These are not for the lawyer to pick; the research states a working assumption for each and he can override it.

- Who he asks to be the independent co-trustee, and whether a family member serves (Q30, Q31).
- How many adult beneficiaries the trust has, and how the share for each is set (Q27).
- Whether the trust is funded at all, and with what (Q11, Q12, Q26 in packet B's memo).
- What share, if any, goes to the Foundation (Q33).
- Which state's law governs, and where the trust is administered (Q22).

## Coverage flags

Stated first so the reader can see which A questions could read as a business or investment interest (the prepaid plan's exclusions):

- Q2: none
- Q4: none
- Q5: none
- Q6: none
- Q7: none
- Q10: none
- Q13: the trust would later hold LLC interests in a business or rental, which could read as a business or investment interest.
- Q22: none
- Q23: none
- Q27: none
- Q28: none
- Q38: none

## Risks

- Packet A's trustee terms rest on packet B's answers (next section). If B answers Q3 or Q8 differently, the terms are redrafted.
- The founder keeping powers over distributions can make the trust a grantor trust (IRC 674(a)) or pull property into his estate (Q7). Neither is settled.
- Any part flagged above may be outside a prepaid plan's scope.
- An Illinois trust protector may be given power to change beneficiaries' interests or to remove and appoint trustees (760 ILCS 3/808(d)(2), (d)(4)); without limits either power makes the trust a grantor trust (Q8). A trustee's acceptance should be signed before the trust takes title, since 120 days of silence is a decline (Q13).
- A Wyoming or Delaware situs does not move the Family Trust's Illinois income tax while the founder is domiciled in Illinois (Illinois residence test, below).

## What packet A rests on from packet B

Packet A's trustee terms rest on packet B's answers to Q3 and Q8. Whether the Family Trust stays non-grantor depends on who decides distributions: if the founder (or his spouse) decides who benefits with no exception that fits, IRC 674(a) makes it a grantor trust and the savings below disappear. The A terms that depend on this:

- The independent distribution trustee and the split trusteeship (Q4): they only work if Q8's answer says an independent trustee, or a non-trustee advisor, satisfies the 674(c) exception.
- The founder's power to remove that trustee (Q5): its limit matters only while the independent-trustee route is what keeps the trust non-grantor.
- Mandatory income in fixed shares and a health, education, support and maintenance (HEMS) standard for principal (Q6): this is the second route (R3), and it rests on Q3's reading of 674(b)(5)(A).
- The powers he keeps as trustee and the estate and gift tax result (Q7), and the payout rule (Q2): both are drafted after B's answers fix who decides.
- Who is trustee, and who signs, before the trust holds title (Q13): the same trustee terms again.

If packet B answers Q3 or Q8 differently, these A terms are redrafted. They are not settled by packet A alone.

Illinois situs for the Family Trust is the research's working assumption, not a finding. Q4, Q8 and Q13 each carry `- Assumes: Illinois situs for the Family Trust (see Q22)`; if Q22 picks Wyoming or Delaware, those answers are redrafted under that state's law.

## What the lawyer must decide

Each is `likely` or `open`; what the lawyer decides on each is stated in the cover and in the linked file.

- **Q2. Will the Family Trust pay out all of its income each year, or keep part of it?** Confidence: likely. [Q2](../research/Q2.md)
- **Q4. Can the instrument split the trusteeship (administrative trustee and special distribution trustee) and who serves as independent distribution trustee?** Confidence: open. [Q4](../research/Q4.md)
- **Q5. Is his power to remove the distribution trustee limited to appointing an independent one?** Confidence: likely. [Q5](../research/Q5.md)
- **Q6. Should income be mandatory in fixed shares, and how do shares adjust for a death or after-born child?** Confidence: open. [Q6](../research/Q6.md)
- **Q7. Do the powers he keeps cause gift or estate tax problems for the funder?** Confidence: open. [Q7](../research/Q7.md)
- **Q10. How do distributions for minor children stay separate from his support duties?** Confidence: likely. [Q10](../research/Q10.md)
- **Q13. What must the Family Trust have before it can hold title to an asset?** Confidence: open. [Q13](../research/Q13.md)
- **Q22. Which state's law should govern the Family Trust, and where should it be administered?** Confidence: open. Linn paragraph 33 pending, needs Dalaun (1 claim). [Q22](../research/Q22.md)
- **Q23. Does the Family Trust, or an Illinois Foundation, have to register or report to the Illinois Attorney General?** Confidence: open. [Q23](../research/Q23.md)
- **Q27. How many adult beneficiaries will the Family Trust have?** Confidence: likely. [Q27](../research/Q27.md)
- **Q28. What would an unrelated individual trustee really charge, and will one serve?** Confidence: open. [Q28](../research/Q28.md)
- **Q38. Without moving, what can an Illinois founder lawfully get from a Delaware or Wyoming trust, and what can't he?** Confidence: open. [Q38](../research/Q38.md)

## Synthetic figures

All figures come from the seeded synthetic year (`rehearsal/synthetic`), not anyone's real money. Every scenario figure here is an engine output on assumptions listed in `counsel-queue.md`. Run on 2026-11-25, 7 of 7 scorecard checks pass, 8 of 17 structure checks pass for the steward versions (the other 9 are amber until documents exist, none red).

- Base year, doing nothing versus the structure: the structure costs 6,015 a year (structure gap).
- Break-even extra asset income, unrelated individual trustee: 170,300 a year (route R2 or R3; 149,500 before the PR 94 founder NII fix); with a professional trustee none up to 1,000,000.
- With a 10 percent Foundation share (route R2): none up to 1,000,000 a year (343,600 before the PR 94 fix; the 10 percent gift is a family cost at w = 0).
- `asset_sized` (150,000 a year of asset income, ASSUMPTION): route R2 is about even with doing nothing (+13 a year; +1,592 before the PR 94 fix), consistent with the 20,200 extra the engine now needs on top of 150,000.
- `asset_sized_pipeline` (350,000 a year, ASSUMPTION): route R2 beats doing nothing by 26,384 a year; with the 10 percent Foundation share, by 2,029.

## Illinois residence test

Dalaun's standing check (2026-11-26): a trust named under another state's law can be an Illinois trust, and there is a way it is not. Illinois decides by the grantor's or decedent's domicile at one moment, never by the state the instrument names (35 ILCS 5/1501(a)(20); traced in [Q22](../research/Q22.md) claims 6, 9 and 17 to 19; the full test is in `rehearsal/synthetic/NON-GRANTOR-ROUTES.md`).

- **Illinois branch:** a living trust is resident if its grantor was domiciled in Illinois when it became irrevocable; a trust made by will, if the decedent died domiciled in Illinois.
- **Not yet tested:** for this rule a trust counts as irrevocable only while the grantor is not taxed as its owner, so the test runs on the day it stops being a grantor trust. Counsel confirms that timing.
- **Out branch:** a grantor domiciled outside Illinois on that day leaves it a nonresident; Linn held that Illinois cannot tax a trust with too few Illinois contacts (para. 33 still to be quoted).
- **Either branch:** a nonresident trust still owes Illinois tax on Illinois-source income, such as an Illinois rental.
- **Where the founder lands today:** the Illinois branch. He is domiciled in Illinois and would be the Illinois trustee. To land in the out branch, his domicile would have to be outside Illinois on the day the trust stops being a grantor trust, or the trust would need too few Illinois contacts under Linn, which an Illinois trustee rules out.
- **Fails the check:** any claim that a Wyoming or Delaware situs, a Wyoming trustee, or a protector's move of situs by itself lowers the trust's Illinois income tax. Another state may still buy protection and control.

## Out-of-state routes without moving

How Illinois residents hold Delaware or Wyoming trusts without moving, each graded for this founder ([Q38](../research/Q38.md)). Illinois's rate on trust income is 4.95 percent plus 1.5 percent replacement tax.

- **Grantor trust in Delaware or Wyoming** (asset protection or dynasty trust): no Illinois tax change; buys protection, duration and directed-trust tools.
- **Founder as Delaware investment adviser:** Delaware allows it, not as trustee; keeps investment control; no tax change, and an Illinois advisor is an Illinois contact under Linn.
- **Non-grantor trust with too few Illinois contacts:** the only route that changes Illinois tax, and only if trustee, protector, beneficiaries, property and administration all leave Illinois; his own trusteeship rules it out.
- **Incomplete-gift non-grantor trust (ING):** no gain in Illinois; it becomes an Illinois resident trust the day it is non-grantor.
- **P.O. box, registered agent or shell company:** changes nothing; Illinois tests his domicile, and a real Delaware trust needs a Delaware trustee who does real work there.

## Illinois text

Dalaun copied the Illinois Trust Code (760 ILCS 3), the Charitable Trust Act (760 ILCS 55) and 35 ILCS 5/1501 on 2026-11-26, and Q4, Q8, Q13, Q22, Q23 and Q28 are traced to that text. Still pending, listed in [../NEEDS-DALAUN.md](../NEEDS-DALAUN.md): the Linn opinion's paragraph 33 (Q22), Wyoming's perpetuities period and revenue statement (Q22), and 35 ILCS 5/201(b) and (c) (Q34).

## What this memo does not do

It does not decide any question. Each `likely` or `open` question above needs a lawyer or CPA. Working assumptions are rehearsal choices, labelled ASSUMPTION in `counsel-queue.md`, and never legal or tax advice.
