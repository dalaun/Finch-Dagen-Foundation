# Trustee rehearsal: an A/B digital twin of the entity stack

**Status:** design, proposed 2026-11-20. Not run. Nothing here moves money, files anything, or opens an account.

**This is design and education, not legal or tax advice.** Every route the twin finds is a question for a licensed attorney or CPA before it becomes a real step.

## What it is, in one picture

Think of a flight simulator for the trustee's job. The real plane is the family's actual spending. The simulator flies the same twelve months twice:

- **Arm A:** everything paid personally, exactly as now.
- **Arm B:** the same spending, sent through the stack (operating companies, Family Trust, Foundation) wherever a section of the tax code lawfully carries it, with that section's evidence attached and the stack's running costs charged.

Then it changes one thing, flies again, and keeps the change only if the result improves and every rule still passes. That is the increment loop: small, logged, reversible steps toward a structure that earns its keep.

## The main finding to expect

**At today's asset level, the twin will most likely show Arm B costing more than Arm A.** Personal living costs (housing, food, clothing, personal transport) have no deduction route anywhere in the stack (IRC 262(a)). The lawful ways structure money reaches the family's living costs are all taxable income: wages for real work from an operating company or, narrowly, from the Foundation (4941(d)(2)(E)), or trust distributions taxed through distributable net income (643, 652/662). The stack adds fixed costs: returns every year, a 990-PF even with no activity, 1.39% on the Foundation's investment income, and about 5% of its assets paid out to programs.

What turns the result around is not routing spending. It is **assets**. The structure's real instruments (estate and GST exemptions, grantor trust sales, charitable lead and remainder trusts, the Foundation's payout) all multiply something the stack already holds. With nothing held, there is nothing to protect and nothing to pay out to programs. This is the founder's own asset-to-program idea, confirmed by the arithmetic: assets are the reason for the trust, and the first optimization step worth taking is putting a real, income-producing asset into the stack.

A second finding, about the structure itself: the IRS's own warning on abusive trusts (Notice 97-24) describes a business trust plus a family trust, the same names this stack uses. That is not a verdict on this stack. It means each trust has to prove it is real: its own accounts, a trustee who follows its terms, and a founder whose relationship to the assets actually changed. The twin treats that as gates G5 and G6, and the first attorney questions are about it.

**Designing away from the abusive pattern, on the facts.** The [structure checks](07-structure-integrity-checks.md) turn every red flag in that IRS guidance into a yes/no question about facts: who controls, who signs, who lives in the property, what was paid and at what price, how each transfer was reported. Names and labels are never evidence; renaming an entity changes no verdict. Today's stack, in roles, passes the checks the design already controls (no personal deductions, no residence depreciation, no self-employment tax claim) and is amber on the rest because the trustee, filing and transfer facts aren't on file. The single change that clears the most checks is replacing the business trust with an ordinary business entity that pays the founder market wages: it removes the IRS's first example pattern instead of defending it.

**The founder's own ideas, tested** (register section F). Borrowing against appreciated assets and an operating-foundation museum are real instruments, and both multiply assets that have to exist first. The home itself has no route; only documented business use and, later, a personal residence trust touch it. Work clothing works only as required uniforms that aren't street wear, bought by the employer; suits fail. The apparel company supplying uniforms to sister companies at its outside price is a real revenue line, not a personal-clothing route. Licensing a family brand from its own entity mostly nets out for federal tax; its value is keeping the brand out of the operating companies' creditors' reach and giving the Family Trust a real, income-producing asset.

A third likely finding: some business-shaped spending (software and AI tools, hosting, research, business travel, building costs) does have strong routes today, through the operating companies and the building's Schedule E. That is where the twin's early wins are, and none of them need a trust.

## The layers, as the twin sees them

- **Operating companies** (the management company, the operating company, the transport company) carry real business costs and pay market wages.
- **The building** already carries its own costs on Schedule E.
- **The Family Trust** carries family living costs as distributions under its standard. Lawful, and taxed to whoever receives them.
- **The Foundation** carries programs and legacy. Its one door to the founder is reasonable pay for necessary work.
- **Estate and legacy** instruments carry growth across generations, once there are assets to carry.

## Files

| File | What it holds |
|---|---|
| [01-instrument-register.md](01-instrument-register.md) | The tax code read as instruments: what each section allows, its evidence test, who cannot use it, with primary-source quotes |
| [02-expense-domain-taxonomy.md](02-expense-domain-taxonomy.md) | The boxes every transaction is sorted into, by layer |
| [03-ab-rehearsal-spec.md](03-ab-rehearsal-spec.md) | The two arms, the route search, the gates, the costs, the score, the increment loop, and the answer key |
| [04-ontology-notes.md](04-ontology-notes.md) and [rehearsal-ontology.ttl](rehearsal-ontology.ttl) | Ontology sketch on gist, reusing the trust-domain core |
| [answer-key-cases.ttl](answer-key-cases.ttl) | The cases the twin must get right before its optimizer is trusted |
| [07-structure-integrity-checks.md](07-structure-integrity-checks.md) and [structure-check-cases.ttl](structure-check-cases.ttl) | Checks S1 to S17 every structure version must pass, from the IRS's abusive-trust guidance; today's stack scored in roles; eval cases SK1 to SK16 |
| [08-w2-to-owner-transition.md](08-w2-to-owner-transition.md), [transition_twin.py](transition_twin.py), [transition-inputs-synthetic.json](transition-inputs-synthetic.json) and [transition-checks.ttl](transition-checks.ttl) | The move from W-2 income to business owner, rehearsed month by month with and without the founder's building, plus a business he lives in and a home-equity down payment; step-down test; checks T1 to T26 |
| [09-insider-branches.md](09-insider-branches.md) | When the family trust counts as an insider to the foundation: the 35 percent family line, the substantial-contributor trap, trustee pay, and what each setting does to the worked spends |
| [05-questions-for-attorney-and-cpa.md](05-questions-for-attorney-and-cpa.md) | What to ask, in plain words |
| [06-handoff-transaction-export.md](06-handoff-transaction-export.md) | The one thing only the founder can supply |

## How this fits the repository

The trust-domain core already says every dollar must trace back through the Authority Cascade (mission, purpose, activity, operator, expense domain, spend). The rehearsal adds the other side of the ledger: the family's own spending, tested against the same rule. A line either finds a lawful instrument and its evidence, or it stays personal.

## Privacy

This repository is public. The founder's real spending, even as categories and counts, stays in the private project folder. Only synthetic cases live here.
