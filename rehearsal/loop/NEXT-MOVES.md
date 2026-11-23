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

## Closed

(none yet)
