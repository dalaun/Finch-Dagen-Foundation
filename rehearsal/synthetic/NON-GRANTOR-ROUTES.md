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

Illinois supports splitting the jobs: 760 ILCS 3/808 lets the document name an investment trust advisor and a distribution trust advisor. A directing party is a fiduciary with a trustee's duties (808(e)). A directed trustee who follows directions is liable only for willful misconduct (808(f)). A trust protector may change beneficiaries' interests (808(d)(2)) and remove and appoint trustees and advisors (808(d)(4)); held without limit by him or a nonadverse party, those are the R7 and R6 traps, so the instrument must limit them. Section text copied by Dalaun 2026-11-26; traced in packet/research/Q4.md and Q8.md.

## Not checked here (counsel)

- **Foundation as a beneficiary.** A 642(c) deduction for payments to the foundation makes the Family Trust a split-interest trust under 4947(a)(2). The private foundation rules then apply to it: self-dealing (4941), excess business holdings (4943), jeopardizing investments (4944) and taxable expenditures (4945). With him as trustee and family as disqualified persons, every transaction between them and the trust becomes a self-dealing question. 4947(a)(2)(B) exempts segregated amounts that were never deducted.
- **Standing check: no personal benefit from charitable funds (IRC 4941 and 760 ILCS 55/17).** Every route fails if any money held for the Foundation, in the Foundation or in the Family Trust's charitable share, pays for anything that benefits him or his family personally. The federal side is 4941 self-dealing. The Illinois side is criminal: a trustee who "with malice and without lawful authority" uses charitable trust funds "for his personal benefit or personal use in an amount in excess of $1,000 within a 5 year period is guilty of a Class 2 felony", with punitive damages and a civil penalty of up to $50,000 for each knowing violation (760 ILCS 55/17, copied by Dalaun 2026-11-26; traced in packet/research/Q23.md). Sec. 15(a)(1) and (a)(5) add the duties to avoid self-dealing and to make no non-program loans, gifts or advances. The check reads who received the benefit, not what the payment was called.
- **Standing check: when an out-of-state trust is an Illinois trust, and when it is not (35 ILCS 5/1501(a)(20)).** Dalaun's check (2026-11-26). Illinois decides residence by the grantor's or decedent's domicile at one moment, never by the state the instrument names. Every memo or claim about the Family Trust's state tax must say which branch it is in and rest on these traced rules (packet/research/Q22.md claims 6, 9 and 17 to 19; statute text copied by Dalaun 2026-11-26):
  - *Illinois branch, living trust:* resident if "the grantor of which was domiciled in this State at the time such trust became irrevocable" (1501(a)(20)(D)).
  - *Illinois branch, trust made by will:* resident if the decedent died domiciled in Illinois (1501(a)(20)(C)).
  - *Not-yet branch, grantor-trust years:* the trust counts as irrevocable only while the grantor is not taxed as its owner, so in grantor-trust years the income is his and the trust files no Illinois fiduciary return. The day it turns non-grantor is the day his domicile is tested.
  - *Out branch, by statute:* a grantor domiciled outside Illinois on that day (or a decedent who died domiciled elsewhere) leaves the trust a nonresident, "a person who is not a resident" (1501(a)(14)).
  - *Out branch, by due process:* Linn v. Department of Revenue, 2013 IL App (4th) 121055, held that Illinois could not tax an inter vivos trust with too few Illinois contacts. The court's own words (para. 33) are still to be quoted; until then the facts that made the contacts too few are not stated here. An Illinois trustee or advisor, Illinois property, Illinois beneficiaries or Illinois administration are each a contact.
  - *Either branch, Illinois-source income:* a nonresident trust still owes Illinois tax on income from Illinois sources, such as an Illinois rental, and files a nonresident computation; rates in 35 ILCS 5/201(b), (c), still to be copied.
  - *Where the founder lands today:* the Illinois branch. He is domiciled in Illinois and would be the Illinois trustee, so a Family Trust that turns non-grantor while he lives here is an Illinois resident trust whatever state it names. To land in an out branch, his domicile would have to be outside Illinois on the day it turns non-grantor, or the trust would need too few Illinois contacts under Linn, which an Illinois trustee rules out; an Illinois rental stays taxable either way.
  - *Fails the check:* any claim that a Wyoming or Delaware situs, a Wyoming trustee, or a protector's later move of situs (760 ILCS 3/808(d)(6)) by itself lowers the trust's Illinois income tax. Wyoming or Delaware may still buy protection and control. Naming someone else as grantor to change the branch is a counsel question, not a route (see "Who the grantor is" below). The five ways Illinois residents use Delaware or Wyoming trusts without moving are graded against this check in packet/research/Q38.md.
- **Standing check: domestic or foreign, and who is taxed (IRC 7701(a)(30)(E), 679, 6048, 6677).** Dalaun's check (2026-11-26). Every trust in the stack must pass both tests on the same day: a U.S. court can exercise primary supervision, and U.S. persons control every substantial decision, with no foreign person holding a decision or a veto (26 CFR 301.7701-7). A trust that fails either is foreign. A foreign trust funded by a U.S. person with a U.S. beneficiary is that person's grantor trust (679), so a non-grantor claim on it fails; creating or funding it triggers Form 3520 notice and a yearly Form 3520-A return, with penalties of the greater of $10,000 or 35 percent (6048, 6677). `grantor_check.py` already fails a version whose terms make it foreign. Traced in packet/research/Q39.md.
- **Standing check: abusive-trust red flags (26 CFR 301.7701-4(b), IRS abusive-trust guidance).** Any instrument fails, and is not built on, if it carries on a business as a trust, pays the trustee's or family's living costs, calls itself a "pure" or "common law" trust, trades units of beneficial interest for nominal property as neither a sale nor a gift, denies courts' authority or claims to set its own taxes or money, ends itself if recorded, or names a trust that in turn names it as beneficiary. Traced in packet/research/Q39.md claims 8 to 10. These are not wording fixes: an instrument with them is replaced, not edited.
- **642(c) set-aside is not available.** For a trust created after October 9, 1969, only amounts the instrument requires to be *paid* from gross income are deductible (642(c)(1)). The set-aside rule in 642(c)(2) is for estates and pre-1969 trusts.
- **Gift and estate tax.** Powers he keeps can also decide whether his transfer is a completed gift and whether the assets stay in his estate. Those sections are not read or modeled here.
- **Revocability default.** Illinois makes a trust revocable only if the instrument expressly says so (760 ILCS 3/602(a), copied by Dalaun 2026-11-26; traced in packet/research/Q13.md). The instrument should still say "irrevocable" expressly.
- **Support obligations (677(b)).** Trust income actually used to support someone he is legally obliged to support (a minor child, for example) is taxed to him to the extent it is so used, even in a non-grantor trust. A power to use income that way does not by itself make it a grantor trust. The check does not model this; keep distributions for any minor children out of his support duties, or expect that tax.
- **Who the grantor is.** The check assumes he funds the trust. If someone else funds it, the analysis changes.

## Questions for counsel

The routes' `ask_counsel` lists, collected in `rehearsal/loop/NEXT-MOVES.md` as move 3.
