# Keeping the Family Trust non-grantor with the founder as steward

SYNTHETIC design note. Not legal or tax advice. Every route here is a question for counsel before it is a plan.

## Why it matters

A **grantor trust** is a trust the IRS looks through: its income is taxed to the person who funded it, as if the trust weren't there. A **non-grantor trust** is its own taxpayer; income it pays out is taxed to the family members who receive it, at their lower brackets. The rehearsal's savings with an independent trustee depend on the Family Trust being non-grantor.

The trap the founder hit (next move 2): if he funds the trust and, as trustee, decides which family member gets how much, IRC 674(a) makes it a grantor trust, whatever the trust's tax return says.

Analogy: the IRS asks one question, "who holds the steering wheel over who benefits?" If the funder can steer, the car is still his. He can still keep the car running (administration and investments), as long as someone independent, or the written terms themselves, does the steering.

## The check

`grantor_check.py` reads each version's `family_trust.terms` in `stack.json` and each route in `grantor-routes.json`, and tests them rule by rule:

| Rule | Fails when |
|---|---|
| 7701(a)(30)(E), 679 | the trust is foreign (no US court supervision or not all substantial decisions controlled by US persons); a US funder then owns it while any beneficiary is a US person |
| 676(a) | he or a nonadverse party can revoke it |
| 673(a) | his reversion is worth over 5% at inception |
| 677(a) | income can go to him or his spouse, or pay premiums on their lives |
| 675(1)-(4) | below-value dealing, borrowing without adequate interest or security, an unrepaid loan, or nonfiduciary voting, investment-control or swap powers |
| 674(a), with the (b)(4)-(7), (c) and (d) exceptions | he, his spouse, or a nonadverse party who doesn't qualify for an exception decides who benefits |
| Reg. 1.674(d)-2 | anyone can add beneficiaries, or he can fire the independent holder and appoint anyone |
| 678(a) | a beneficiary can take property alone |

A missing term stops the run (fail closed). Every engine run now prints each version's derived status. The run also fails if a version's terms make it a different kind of trust than the engine taxes it as. Today's versions are consistent: `today` and `flat` are grantor (674(a)); `flat_independent` is non-grantor (674(c)).

## Routes, graded

Run `python3 rehearsal/synthetic/grantor_check.py --routes`.

| Route | Result | What it costs him in control |
|---|---|---|
| **R2** He is trustee for investments and administration; an independent special distribution trustee decides who gets what; he may only swap that trustee for another independent one | non-grantor (674(c)) | Only the who-gets-how-much decision, plus an independent trustee's fee (the engine's "unrelated individual trustee" arm prices this) |
| **R3** He is sole trustee; income paid out every year in fixed shares; principal only for health, education, support or maintenance | non-grantor (no power over income; 674(b)(5)(A) for principal) | No steering of income at all; shares change only as the document says. Also answers next move 2: income goes out each year, so little is taxed at trust rates |
| **R4** He is trustee; an Illinois distribution trust advisor (760 ILCS 3/808(c)), not a trustee, directs distributions | unsettled | Same as R2. 674(c) speaks of *trustees*; whether a non-trustee advisor counts is for counsel. Making the advisor a co-trustee turns it into R2 |
| **R9** R3, plus he chooses which charities get the foundation's fixed share | non-grantor (674(b)(4)) | Keeps the charitable choice. See the 4947 warning below |
| R1 He is sole trustee with discretion | grantor (674(a)) | none: this is the problem |
| R5 He distributes income under a health, education, support or maintenance standard | grantor: 674(d) is closed to the funder and his spouse | the trap: a standard saves a *principal* power, not an *income* power he holds |
| R6 R2, but he can fire and appoint anyone, himself included | grantor (Reg. 1.674(d)-2(a)) | |
| R7 R2, with a power to add beneficiaries | grantor (Reg. 1.674(d)-2(b)) | |
| R8 R2, with his nonfiduciary swap power | grantor (675(4)(C)) | planners add this on purpose; keep it out |

**Best fit for "own nothing, steward everything":** R2 or R3. R2 keeps flexibility in someone else's hands. R3 keeps everything in his hands by giving up flexibility. A blend (fixed income shares, independent trustee for principal beyond the standard) also passes.

Illinois supports splitting the jobs: 760 ILCS 3/808 lets the document name an investment trust advisor and a distribution trust advisor. A directing party is a fiduciary with a trustee's duties (808(e)). A directed trustee who follows directions is liable only for willful misconduct (808(f)).

## Not checked here (counsel)

- **Foundation as a beneficiary.** A 642(c) deduction for payments to the foundation makes the Family Trust a split-interest trust under 4947(a)(2). The private foundation rules then apply to it: self-dealing (4941), excess business holdings (4943), jeopardizing investments (4944) and taxable expenditures (4945). With him as trustee and family as disqualified persons, every transaction between them and the trust becomes a self-dealing question. 4947(a)(2)(B) exempts segregated amounts that were never deducted.
- **642(c) set-aside is not available.** For a trust created after October 9, 1969, only amounts the instrument requires to be *paid* from gross income are deductible (642(c)(1)). The set-aside rule in 642(c)(2) is for estates and pre-1969 trusts.
- **Gift and estate tax.** Powers he keeps can also decide whether his transfer is a completed gift and whether the assets stay in his estate. Those sections are not read or modeled here.
- **Revocability default.** 760 ILCS 3/602 was not read. The instrument should say "irrevocable" expressly rather than rely on a default.
- **Support obligations (677(b)).** Trust income actually used to support someone he is legally obliged to support (a minor child, for example) is taxed to him to the extent it is so used, even in a non-grantor trust. A power to use income that way does not by itself make it a grantor trust. The check does not model this; keep distributions for any minor children out of his support duties, or expect that tax.
- **Who the grantor is.** The check assumes he funds the trust. If someone else funds it, the analysis changes.

## Questions for counsel

The routes' `ask_counsel` lists, collected in `rehearsal/loop/NEXT-MOVES.md` as move 3.
