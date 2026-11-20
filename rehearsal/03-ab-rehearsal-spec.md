# 03. A/B rehearsal spec

[Back to the rehearsal overview](README.md)

The twin takes twelve months of real transactions and runs them twice. Arm A is life as it is now. Arm B is the same spending, sent through the entity stack wherever an instrument in the [register](01-instrument-register.md) lawfully carries it. Nothing in either arm moves money. It is a rehearsal.

## Inputs

| Input | Source | Notes |
|---|---|---|
| Transaction ledger | Bank and card export (CSV), see [handoff](06-handoff-transaction-export.md) | The only input only the founder can give |
| Domain map | [Taxonomy](02-expense-domain-taxonomy.md) | Each line sorted into one domain; low-confidence lines wait for a person |
| Entity facts | Founder plus formation documents | Which entities exist, who owns what, grantor or non-grantor, state of formation, what each holds |
| Instrument register | [Register](01-instrument-register.md) | Versioned. Every run records the register version it used |
| Cost table | Quotes from the CPA, trustee, registered agent | Parameters, not guesses. Missing costs block a run rather than default to zero |

## Before any run: the structure checks

Every structure version (which entities exist, who controls what, how money flows between them) must pass the [structure integrity checks](07-structure-integrity-checks.md) S1 to S17 before its ledger routes are scored. They turn the IRS's descriptions of abusive trust arrangements (Notice 97-24 and its abusive-trust guidance) into yes/no questions about facts. Any red check removes the whole version; any amber check blocks it and becomes a professional question. Checks read fact fields only, and every check run is repeated with all names randomized: the verdicts must not change.

## Arm A: personal

Every line is paid by the founder as an individual and treated as it is today: wages, Schedule E for the building, the existing business returns. Arm A is the baseline, not a straw man.

## Arm B: route-seeking

For each line, the twin searches for every route that could carry it, scores each one, and keeps the best one that passes every gate.

A **route** is: line + layer + instrument + evidence. The search runs layer by layer:

1. **L1 Operating companies.** Is this an ordinary and necessary cost of a real trade or business (162)? Is it a reimbursement under an accountable plan (62(c), Reg. 1.62-2)? A working condition fringe (132(d))? Education under a written 127 plan? Does the price between related entities hold up at arm's length (482)?
2. **L2 Rental property.** Is it a cost of the building? It is already deductible on Schedule E without any trust.
3. **L3 Family Trust.** Can the trust pay it as a distribution to a beneficiary under the trust's own standard (for example health, education, maintenance and support)? If so, it is lawful but taxable to the beneficiary through DNI (643, 652/662), and the twin says so. It is a route to *pay*, not a route to *deduct*. Grantor vs non-grantor is tested as a switch (see increments).
4. **L4 Foundation.** Is it program delivery for the charitable purpose? Or reasonable compensation for personal services that are necessary to the purpose and not excessive (4941(d)(2)(E))? That is the founder's one door into foundation money, and it is taxable wages to him.
5. **L5 Estate and legacy.** Is it a transfer that uses an exclusion (2503(b) annual, 2503(e) direct tuition and medical, the 2010 basic exclusion, the 2631 GST exemption) or a charitable split-interest vehicle (664 remainder trust, 170(f)(2)(B) lead trust, donor-advised fund)?

If no route passes, the line stays in Arm A and is marked **no route yet**, with the facts that would have to be true for a route to exist. Example: "Groceries: no route yet. Would need: a program that feeds participants, with participant records, run by the foundation, and the food used by participants, not the household."

### Gates (any red gate removes the route)

| Gate | Test | Source |
|---|---|---|
| G1 Personal | Is the expense personal, living or family? If yes, only an express section can carry it | 262(a) |
| G2 Business | Is there a real trade or business, beyond managing one's own money? | 162(a); Higgins (1941) |
| G3 Reasonable | Is pay at the market rate for like services by like enterprises? | Reg. 1.162-7(b)(3); 4941(d)(2)(E) |
| G4 Self-dealing | Does foundation money or property reach a disqualified person other than through the (d)(2)(E) door? | 4941(d)(1), 4946(a) |
| G5 Substance | Does the route change the founder's economic position in a meaningful way, apart from tax, and have a substantial non-tax purpose? | 7701(o)(1) |
| G6 Sham and step | Does the trust or entity act independently of the founder, with its own accounts and decisions? Would collapsing the steps give a different result? | Markosian (1980); Gregory (1935); Court Holding (1945) |
| G7 Substantiation | Are the records that the instrument names actually present? | 274(d); Reg. 1.62-2(e) |
| G8 Holdings | Do the foundation and its insiders together exceed 20% of a business's voting stock? | 4943(c)(2)(A) |
| G9 Payout | Does the foundation meet roughly 5% of non-charitable assets each year? | 4942(d), (e)(1) |
| G10 Classification | Is a "trust" that runs a business really a business entity for tax? | Reg. 301.7701-4(b) |

A gate the twin cannot decide from the evidence is amber. Amber blocks the route and becomes a question for the attorney or CPA, never a pass.

### Costs counted against Arm B

Each line that goes to Arm B carries a share of the stack's fixed cost, plus its own variable cost.

| Cost | Kind | Source |
|---|---|---|
| Trust income tax returns (Form 1041), one per non-grantor trust | Preparer fee | CPA quote |
| Foundation annual return (Form 990-PF), every year even with no activity | Preparer fee | IRS, Form 990-PF page; CPA quote |
| Foundation excise tax, 1.39% of net investment income | Tax | 4940(a) |
| Minimum payout, about 5% of non-charitable assets | Required outflow to programs | 4942(e)(1) |
| Trustee or independent trustee fees | Fee | Trustee quote |
| State costs: registered agent, annual reports, Illinois charitable registration | Fee | State schedules |
| Entity books and payroll | Fee | Bookkeeper quote |
| Compressed trust brackets on income a non-grantor trust keeps | Tax | Rev. Proc. for the year; 1(e) |
| Penalty exposure if a route fails | Expected cost | 6662(b)(6), (i): 20%, 40% if undisclosed |

The payout is not waste. It is the asset-to-program pipeline working, and Arm B scores it as program output, not loss.

## Objective

For each run:

**Score = (Arm A total cost) − (Arm B total cost) + w × (program output) − (expected penalty)**

- Arm cost = taxes + fees + required outflows that are not program output.
- Program output = qualifying distributions and documented capability built (the repo's C4 "builds capability" check).
- Expected penalty = for each route, the chance a gate is wrong times the 6662 penalty and back tax. Any route with an amber gate is excluded, so this term stays small and honest.
- w is the founder's weight on legacy versus money. It is a setting he chooses, written down, not tuned to make B win.

A route counts only when its evidence score is complete. Partial evidence means the line stays in Arm A for that run.

## The increment loop

One **optimization step** changes exactly one thing, then reruns both arms on the same ledger.

Examples of one step:
- Move software tools (D1) to the management company, paid from the management company's account, with a use log.
- Adopt an accountable plan at the management company and route business travel through it.
- Switch the Family Trust from grantor to non-grantor in the model (a rehearsal of the trade-off, not an election).
- Fund the Family Trust with one named asset in the model and let its income flow.
- Add one foundation program with a budget, and price the founder's role at a benchmark.
- Use a donor-advised fund in place of a foundation grant for one year.

A step is **kept** when the score rises, no gate goes red or amber, and every new route has its evidence. Otherwise it is rolled back and logged as a tried idea with the reason.

A step **stops the loop** and becomes a question for the attorney or CPA when making it real would need any of: signing a document, funding or retitling an asset, filing a return or election, changing who is a trustee or beneficiary, or paying anyone. The twin can rehearse those steps; it cannot take them.

Every step is logged as a dated event: what changed, the register version, both arm totals, the gates, and the verdict. That log is the machine-readable history the score is tested against later, when real outcomes arrive.

## First increments to rehearse, in order

1. **Sort the ledger** and run both answer keys. No optimizing until K1 to K27 and SK1 to SK16 all match.
2. **Move business-shaped lines to the operating companies** (D1, D5, business share of D3, D11, D12) with an accountable plan. Expected: the first real gain, no trust needed.
3. **Fix classification facts** in the model (the business trust as a business entity; the management company's real classification), then rehearse the flat version: an ordinary business entity in place of the business trust, paying the founder market wages. Expected: some routes close, and structure checks S5, S11 and S12 move toward passing; better now than in an audit.
4. **Price the founder's Foundation role** for one program at a benchmark. Expected: lawful wages, a cost to the Foundation, no tax saving; it tests the one door.
5. **Fund the Family Trust in the model** with one named asset, grantor first, then non-grantor. Expected: this is where Arm B can start to beat Arm A, and it shows how large an asset has to be before the stack's fixed costs are covered.
6. **Compare Foundation vs donor-advised fund** at the modeled asset level. Expected: the fund wins while assets are small; the Foundation wins once there is enough to support staff and a 5% payout.

Steps 5 and 6 stop for the attorney and CPA before anything real happens.

## Guards against gaming the score

1. The optimizer may not reclassify a line to win. Reclassification needs new evidence, and a person confirms it.
2. The register is version-pinned per run. Changing a rule is its own step with a source quote.
3. The answer keys (below, and in the structure checks) must pass before any optimizer output is trusted.
4. A route that only changes labels, not who owns or pays, fails G5.
5. A structure change that only renames an entity is not a step. The structure checks must give identical verdicts before and after any rename.

## Answer key (the eval)

These are cases where the law gives a clear answer. The twin must reproduce every one before its optimizer runs. The machine-readable version is [answer-key-cases.ttl](answer-key-cases.ttl).

| Case | Line | Expected verdict | Why |
|---|---|---|---|
| K1 | Household groceries paid by the foundation | Fail: self-dealing | 4941(d)(1)(E) |
| K2 | Household groceries paid by the management company | Fail: personal | 262(a) |
| K3 | Household groceries paid by the Family Trust as a support distribution | Pass: lawful, taxable to the beneficiary, no saving | 643, 652/662 |
| K4 | AI tool used for client work, invoiced to and paid by the management company | Pass | 162(a) |
| K5 | Same tool, no use record, paid by the management company | Amber: substantiation | Reg. 1.62-2(e) |
| K6 | Foundation pays the founder a curriculum-development salary at a documented market benchmark, approved without his vote | Pass | 4941(d)(2)(E); Reg. 53.4941(d)-3(c) |
| K7 | Same, at twice the benchmark | Fail: excessive | 4941(d)(2)(E) |
| K8 | Foundation rents space in the founder's building at market rent | Fail: self-dealing (leasing), whatever the price | 4941(d)(1)(A) |
| K9 | Founder rents his home to the management company for meetings under 15 days a year | Amber: works only if the management company is a separate taxpayer (not a disregarded single-member LLC), the meetings are real, and the rent is at market (a CPA question) | 280A(g); 162; 482 |
| K10 | Business trust that runs the operating company filed as a trust | Fail: classification | Reg. 301.7701-4(b) |
| K11 | Daily commute rides paid by the management company | Fail: personal | 262(a) |
| K12 | Tuition paid directly to a school for a family member | Pass: excluded from gift tax | 2503(e) |
| K13 | Rent on the founder's own residence paid by the foundation | No route yet: only wages for real work can reach it | 4941(d)(1)(E), (d)(2)(E) |
| K14 | Founder borrows against appreciated assets he holds, under a real loan; proceeds spent personally | Pass: proceeds are not income; interest not deductible | Woodsam Associates, 198 F.2d 357: borrowing is not a disposition; interest is personal under 163(h)(1) |
| K15 | Foundation lends to the founder at a market rate | Fail: self-dealing | IRC 4941(d)(1)(B): lending is self-dealing whatever the rate |
| K16 | Founder lends to the Foundation interest-free; proceeds used only for programs | Pass | IRC 4941(d)(2)(B) |
| K17 | Founder gives an appreciated asset to a relative who dies within a year and leaves it back to him; basis reset claimed | Fail: no basis reset | IRC 1014(e) |
| K18 | Founder, paid wages by the management company, deducts a home office on his own return | Fail: employee deduction suspended | IRC 67(h); 280A(c)(1): route is reimbursement under the company's accountable plan |
| K19 | Home office that doubles as a guest room | Fail: not exclusive | IRC 280A(c)(1): exclusive use |
| K20 | Foundation-owned art hung in the founder's home; public visits by appointment he controls | Fail: self-dealing | IRC 4941(d)(1)(E); Rev. Rul. 74-600 |
| K21 | Operating foundation museum at its own site, open to the public, spending 90% of adjusted net income running it, most assets in the collection | Pass | IRC 4942(j)(3)(A), (B)(i); Treas. Reg. 53.4942(b)-1 |
| K22 | Business suits for client meetings bought by the management company | Fail: personal | Pevsner, 628 F.2d 467: adaptable to street wear |
| K23 | Required crew uniforms, not street wear, bought by the operating company from the apparel company at its outside-customer price | Pass | IRC 162(a); 132(a)(3); 482; Pevsner |
| K24 | Same uniforms sold to a sister company at twice the outside price | Fail: not arm's length | IRC 482; structure check S8 |
| K25 | Plain polos with only a company logo, given to staff | Amber: CPA question | Pevsner street-wear test; no source read settles logo-only clothing |
| K26 | Foundation buys program shirts from the apparel company | Amber: attorney question | IRC 4941(d)(1)(A), (C); 4946: red if the apparel company is a disqualified person |
| K27 | Entities in the stack lend to each other in a circle at interest, each deducting interest, with no outside purpose | Fail: no substance | IRC 7701(o); Notice 97-24; structure checks S8, S11 |
