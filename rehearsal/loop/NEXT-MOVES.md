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
- Status: open

### 2. question: Will the Family Trust pay out all of its income each year, or keep part of it?

- Key: `trust-distributes-dni`
- Opened: 2026-11-23
- For: lawyer, then CPA
- Why it matters: the engine assumes the trust distributes 100 percent of its distributable net income (DNI) to the two adult beneficiaries, who are taxed at their own lower brackets. In a scratch run (not committed) that assumed only 50 percent is distributed, break-even with an unrelated individual trustee roughly doubles, from about 148,000 to about 313,000 a year of asset income, because retained income is taxed at the compressed trust brackets (and above the top trust bracket start, NIIT applies). Whether income goes out is a trustee-discretion or mandatory-payout choice written into the instrument, so it decides how big the asset must be.
- The one thing for Dalaun: ask his lawyer, "Should the Family Trust be written to require distributing its income each year, or leave it to the trustee's discretion, and what does each do to who pays the tax?" Then ask his CPA to confirm the tax result.
- Status: open

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
  - If the trust pays for things I am legally obliged to provide my minor children, that income is taxed to me (677(b)). How should the document keep distributions to them separate from my support duties?
- Status: open

## Closed

(none yet)
