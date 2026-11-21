# Stewardship: "Own nothing, steward everything"

**Status:** draft, proposed 2026-11-21. Synthetic cases, roles only, illustrative amounts. **Not legal or tax advice.**

The founder's own words set the principle. He is the family trust's trustee, not a beneficiary. He runs the foundation, the trusts and the companies, but he owns no share of what they hold. A steward holds the keys, and the beneficiaries own the rent.

That position holds only while three things stay true. The checks below turn each one into a yes/no question about facts.

## The three stewardship checks

| Check | The question | If it fails | What it guards against |
|---|---|---|---|
| **ST1 Reasonable pay** | Is every dollar that reaches the founder pay for real work, at a price set from comparables, with every benefit counted and coded? | ST1a no comparables: needs counsel. ST1b wage plus benefits above the range: needs counsel. ST1c foundation pay plus benefits above its benchmark: block. ST1d a benefit not coded taxable or excluded: insufficient | Becoming an insider by control. 162(a)(1) allows "a reasonable allowance for salaries"; 53.4941(d)-3(c)(1) lets a foundation pay a disqualified person only if the pay "is not excessive" |
| **ST2 Decision record** | Was the deal decided in writing, citing the mission, before money moved? | insufficient | Alter ego or sham: entities that never decide anything apart from the person who controls them |
| **ST3 Independent reviewer** | Did someone who is neither the founder nor related or subordinate to him review it, with the power to refuse? | needs counsel | Grantor-trust ownership. 674(c) relies on trustees "none of whom is the grantor" and "no more than half of whom are related or subordinate parties"; 672(c) lists who is related |

**The sibling gap.** A sibling is not "family" for self-dealing ("a brother or sister of an individual is not a member of his family", 53.4946-1(h)), but is a related party under 672(c) ("brother or sister"). So the founder's sibling can be paid by the foundation without the self-dealing ban (it goes to the hack test instead), but cannot serve as the independent reviewer. Case D04 shows it.

## The arm's-length check between the founder's roles

Deals between the operating company, the management company and the trusts have no self-dealing rule of their own. What polices them is 482: between businesses "owned or controlled directly or indirectly by the same interests", the IRS may reallocate income and deductions "clearly to reflect the income". So each such deal needs:

- **AL1 Market price:** a range from a named comparable source (AL1a, insufficient without one), and a price inside it (AL1b, needs counsel outside it).
- **AL2 Written terms:** insufficient without them.
- **ST2 and ST3** as above.

**Arm's length does not cure self-dealing.** When the foundation is one side and the other side is a disqualified person, AL0 blocks at any price, because 4941(d)(1) lists the acts (sale, lease, loan, services, pay) with no fair-price exception. When the other side is not an insider but passes value to one, AL4 sends it to counsel ("indirect", "for the benefit of"). Case D07 is a market-rate lease with every paper in place: it blocks in branch A and goes to counsel in branch B.

## Two sides of every benefit: deduct and exclude

Public company proxies show the pattern the founder was pointed to. In the Summary Compensation Table, "All other compensation" lists perquisites, tax "gross-ups", plan contributions and "insurance premiums paid by, or on behalf of, the registrant", and any perquisite "whose value exceeds $10,000 must be identified and quantified in a footnote" (17 CFR 229.402(c)(2)(ix)). The company deducts the pay as an ordinary and necessary expense. The executive includes it in income unless a law excludes it. Both tests apply to the same dollar, so the model runs two:

- **BD: what the business may deduct.** BD1 ordinary and necessary (162(a)). BD2 personal, living or family (262(a)), "wherever it is paid from"; a trust "can't be used to transform a taxpayer's personal, living, or educational expenses into deductible items" (1041 instructions). BD3 capital (263(a)), unless the section 179 election applies. BD4 start-up costs, unless the 195(b) election applies and the business has begun. BD5 timing: cash, accrual, and the related-party wait. BD6 home office (Pub 587).
- **FX: what the employee may exclude.** FX0 no law excludes it. FX1 the person is a 2% S corporation shareholder, partner or sole proprietor, and the exclusion is for employees only. FX2 the plan favors key or highly paid employees. FX3 over the edition's limit. FX4 a reimbursement with no records. FX5 lodging without all three 119 tests.

Limits come from the edition named, with its year: Pub 15-B (2026) for health FSA ($3,400), dependent care ($7,500), parking ($340 a month), educational assistance ($5,250); 79(a) for group-term life ($50,000 of coverage).

## Comparables: where the ranges come from

| Source | What it shows | How well read |
|---|---|---|
| Public company proxy, Summary Compensation Table (Item 402) | Which perks are disclosed and priced; the pay mix at large companies | Read in the regulation |
| Externally managed REIT or BDC 10-K and proxy | The management-fee model: fee basis, services covered, independent director approval | Inferred; capture those three fields from a filing when used |
| Peer foundations' 990-PF Part VII | Officer, trustee and top-employee pay at similar foundations: the comparables that matter for 4941 | Headings read |
| Public charities' 990 Schedule J | Detailed pay and benefits at larger charities | Not read |
| Independent pay or fee survey | Similar-size organizations | Inferred |

Executives' Forms 3, 4 and 5 report stock holdings, not pay, so they are not a source. A proxy is a source for prices and disclosure, never a template for perks: a perk that is wages at a public company is wages here too.

## Who can sponsor a cafeteria plan with the founder in it

Pub 15-B (2026) opens a cafeteria plan to "A current common-law employee". A 2% S corporation shareholder is treated "as you would a partner", and partners and the self-employed are not on the list. So the sponsor has to be an entity where the founder is a common-law employee and not an owner in pass-through form:

- **The management company, if taxed as a C corporation.** This is the cleanest fit (cases D10, D16).
- **The operating company, if taxed as a C corporation.** If it is an S corporation, whether the founder counts as a 2% shareholder through the trusts depends on attribution rules (318, 1372) that were not read. That is a counsel question.
- **The foundation.** It can sponsor one for its employees, but every benefit counts toward the 4941 "not excessive" test (inferred; the regulation does not name fringe benefits, so the model fails closed, case P25).

With the founder as the only participant, the plan likely fails the key-employee test ("more than 25% of the total of the nontaxable benefits"). That is inferred, not read. A small-employer "simple cafeteria plan" (100 or fewer employees on average) has its own safe harbor.

## Worked cases

All in `tests/decision/entity-deal-cases.ttl`; answers in `tests/decision/expected.ttl`.

| Case | Result | Why |
|---|---|---|
| D01 management fee inside an external-manager range, written, decided, independent reviewer | allow | Every check passes |
| D02 the same fee on a handshake | insufficient AL2 | No written terms |
| D03 fee above the range | needs counsel AL1b | 482 reallocation risk |
| D04 reviewed by the founder's sibling | needs counsel ST3 | Related under 672(c) |
| D05 no market range | insufficient AL1a FC0 | No comparable source |
| D06 paid first, decided later | insufficient ST2 | No decision record before payment |
| D07 family trust rents foundation space at market | block AL0 (branch B: needs counsel AL4) | Arm's length does not cure self-dealing |
| D08 accrual operating company deducts a fee owed to the cash-method management company, unpaid at year end | block BD5 | Related payee: no deduction until paid |
| D10 wage plus health coverage, C corporation employee | allow | Excluded benefit, package inside range |
| D11 the same as a 2% S corporation shareholder | block FX1 | Not an employee for fringe benefits |
| D12 the same, premiums put in wages | allow | The lawful route; then Form 7206 |
| D13 pay with no comparables | needs counsel ST1a | |
| D14 wage inside the range, package above it | needs counsel ST1b | Benefits counted |
| D15 group-term life not coded | insufficient ST1d | |
| D16 cafeteria plan: health FSA and dependent care inside 2026 limits | allow | |
| D17 cafeteria plan that favors key employees | block FX2 | Benefits they could have chosen become wages |
| D18 cafeteria plan for a 2% shareholder | block FX1 | |
| D19 dependent care above $7,500 | block FX3 | |
| D20 flat car allowance left out of wages | block FX0 | No law excludes it |
| D21 mileage reimbursed with a log | allow | Working condition benefit |
| D22 mileage with no log | block FX4 | |
| D23 group-term life at $50,000 | allow | |
| D24 $100,000 of coverage, all excluded | block FX3 | Cost above $50,000 is wages |
| D25 entity pays for a home that is an entity's mailing address, claimed under 119 | block FX5 | Not business premises, not required |
| D30 family vacation | block BD1 BD2 | |
| D31 hobby purchase | block BD1 | |
| D32 roof as a repair | block BD3 | Capital |
| D33 equipment with a 179 election | allow | |
| D34 start-up costs with the 195 election | allow | |
| D35 start-up costs, no election | block BD4 | |
| D36 cash-method bill unpaid at year end | block BD5 | |
| D37 home office, home is only a mailing address | block BD6 | |
| D38 room used only for the business's administration | allow | |
| D39 deduction claim with facts blank | insufficient BD0 FC0 | |
| D40 D10's pay with the benefit's yearly value left out | insufficient FC0 | ST1b used to count a missing benefit value as 0 |
| D41 D01's fee paid to a payee whose name is misspelled | insufficient FC0 | A name no case file declares is not known to be an outsider |
| P25 foundation pay under its benchmark, over it with benefits | block ST1c | |

## Not verified

- Treas. Reg. 1.162-7 (what makes pay reasonable), which 53.4941(d)-3(c)(1) points to.
- That fringe benefits count toward the 4941 test (inferred; the model fails closed).
- 15-B's own text on cash allowances and on lodging; the allowance and mailing-address results are inferred from the general rule and 119.
- 162(m), 274, 280G and 409A, named in the proxy context only.
- Attribution of S corporation stock through the trusts (318, 1372).
- The alter-ego and sham doctrines (case law).
- Whether the family trust is a grantor trust at all.

## Files

- `decision/stewardship-model.ttl`: the principle, vocabulary, benefit kinds with limits, comparable sources, and every check with its outcome, pressure and source.
- `decision/stewardship-shapes.ttl`: the SHACL checks.
- `decision/irs-instruments.ttl`: the IRS publications as instruments, linked to roles and checks ([rehearsal/10](../../rehearsal/10-irs-instruments.md)).
- `tests/decision/entity-deal-cases.ttl`: the worked deals.

```
pip install rdflib pyshacl
python3 decide_spend.py              # foundation spends and entity deals, branch A
python3 decide_spend.py --branch B
```
