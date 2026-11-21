# Insider branches: the two trusts, run both ways

**Status:** rehearsal, 2026-11-20. Synthetic cases, roles only. Nothing here moves money or changes a trust.

**This is design and education, not legal or tax advice.** Counsel decides which branch matches the real trust documents.

## The question

The [spend decision model](../docs/wiki/Spend-Decision-Model.md) treats the family trust, the business trust and the operating company the business trust owns as disqualified persons ("insiders") until counsel says otherwise. This page runs every worked spend both ways:

- **Branch A (default, fail closed):** the trusts are insiders.
- **Branch B:** they are not.

## The perspective shift: the answer is written on the deed

Whether a trust is an insider isn't a fact waiting to be discovered. The trust documents set it, the same way the names on a deed decide who owns a house. Under 4946(a)(1)(G), a trust is an insider when insiders "hold more than 35 percent of the beneficial interest". 4946(a)(4) counts that interest "in accordance with the rules for constructive ownership of stock provided in section 267(c)", so an interest held through another trust counts toward the people behind that trust.

So the real choice isn't A or B. It's who sits on each trust's deed.

## Is branch B even possible?

**Only in one shape, and that shape gives the family's interest away.** Branch B holds only if the foundation holds the whole beneficial interest of the family trust, and through it the business trust's interest, while the founder and family hold none. Once the family keeps more than 35 percent, (G) makes the trust an insider, and branch A is simply what the law says, not extra caution.

That one shape brings three more problems:

1. **The trust becomes a substantial contributor.** 7701(a)(1) defines a person to "include an individual, a trust, estate". So a trust that funds the foundation can become a substantial contributor, and therefore an insider under 4946(a)(1)(A). The likely way out is 4947(a)(1). A trust whose unexpired interests are all charitable, "for which a deduction was allowed", is "treated as an organization described in section 501(c)(3)". Treasury Regulation 53.4946-1(a)(8) then says the insider list for self-dealing "shall not include any organization which is described in section 501(c)(3)". The regulation doesn't name 4947 trusts, which is a question for counsel.
2. **The trust stops being the family's.** A wholly charitable trust holds charity's assets, not the family's personal assets. It also takes on its own private-foundation duties. That second point is not verified: see below.
3. **The foundation becomes the business's owner.** 4943(d)(1) says stock "owned, directly or indirectly, by or for a ... trust shall be considered as being owned proportionately by or for its ... beneficiaries." With the foundation as the only beneficiary at the end of the chain, the operating company's stock counts as the foundation's own, so the 20 percent excess-business-holdings limit applies to it. The statute's exception covers only "an income or remainder interest of a private foundation" in a split-interest trust (4947(a)(2)), and the trusts in this shape aren't split-interest.

## What flips

`python3 decide_spend.py --compare` (26 synthetic proposals, three of them new on this page):

| Proposal | Branch A | Branch B | Why |
|---|---|---|---|
| P22 Rent to the family trust for program space, at market | block (R1) | allow | Leasing from an insider is self-dealing at any price. Without the insider status, it's an ordinary lease. |
| P23 Program T-shirts bought from the operating company, at its outside price | block (R1) | needs counsel (H2) | The insider rule drops, but the operating company pays the founder's management company a fee, so value still reaches an insider. The hack test catches it. |
| P24 Grant to the family trust to run a program, no expenditure responsibility | block (R1, R6) | block (R6) | It stays blocked: a grant to a non-charity needs expenditure responsibility in either branch. |
| P25 Rent to a family trust that still pays a family beneficiary | block (R1) | needs counsel (H2) | The stress case: assume B while a family member benefits, and the hack test flags it. In real life, (G) would put it back in branch A. |
| P14 Buy 15 percent of the operating company from an unrelated seller | needs counsel (R7, R8) | needs counsel (R7, R8) | It doesn't flip. In A the business trust's 30 percent counts against the limit; in B it counts as the foundation's own (15 + 30 = 45 percent). |

The other 21 proposals grade the same in both branches.

## What each branch costs and unlocks

- **Branch A keeps** the family's interest in both trusts and the business. **It costs** every deal between the foundation and the stack (leases, purchases, grants to the trusts), which stays blocked at any price. The one open door stays open in both branches: reasonable pay for necessary personal services, with a comparability record (P05).
- **Branch B unlocks** ordinary market deals between the foundation and the trusts (P22). **It costs** the family's beneficial interest in both trusts, probably a private foundation's duties for the family trust itself, and an excess-business-holdings problem for the operating company that doesn't depend on any insider answer.

## Not considered until now: a third branch

A split-interest shape sits in between: the family keeps an income interest and the foundation holds the remainder. 4947(a)(2) then applies the self-dealing and taxable-expenditure rules to the trust itself "as if such trust were a private foundation". In exchange, 4943(d)(1) stops counting the trust's business stock as the foundation's while the foundation "holds only an income interest or only a remainder interest". Whether the family's income interest crosses the 35 percent line depends on how the two interests are valued, which this page has not checked. It's the branch most likely to keep both the family's interest and a clean foundation, and it can run the same way as A and B, as a third facts file.

## The counsel question, now one line

"Who holds the beneficial interest in each trust, counted through 267(c), and was a charitable deduction ever allowed for amounts in either? Branch A blocks every deal with the stack; branch B allows market deals but gives up the family's interest and makes the operating company an excess business holding."

## Not verified

- The text of 267(c)(1) itself. It was read only through the IRS attribution page's paraphrase: "considered owned proportionately by or for its shareholders, partners, or beneficiaries".
- The substantial-contributor thresholds in 507(d)(2), and whether a trust's distribution to its charitable beneficiary counts as a contribution.
- How a 4947(a)(1) trust is classified under 509, which is why "private foundation duties" above is marked "probably".
- How income and remainder interests are valued against the 35 percent line, and how grantor-trust status affects it.
- The 4943 disposition periods and exceptions (for example, for business holdings acquired by gift or bequest).

## How to run it

```
pip install rdflib pyshacl
python3 decide_spend.py              # branch A, graded against tests/decision/expected.ttl
python3 decide_spend.py --branch B   # branch B, graded against expected.ttl plus expected-branch-b.ttl
python3 decide_spend.py --compare    # what flips
```

Each branch is a facts file, `tests/decision/branch-a.ttl` or `branch-b.ttl`, that states the insider answer as data. A third branch is one more file.

## Sources

- [26 USC 4946](https://uscode.house.gov/us/usc/119-118/t26/s4946/) (current through PL 119-120)
- [26 USC 4947](https://uscode.house.gov/us/usc/119-118/t26/s4947/)
- [26 USC 4943](https://uscode.house.gov/us/usc/119-118/t26/s4943/)
- [26 USC 7701 (2011 edition)](https://www.govinfo.gov/content/pkg/USCODE-2011-title26/html/USCODE-2011-title26-subtitleF-chap79-sec7701.htm)
- [Treas. Reg. 53.4946-1](https://ecfr.io/Title-26/Section-53.4946-1) and [53.4943-8](https://ecfr.io/Title-26/Section-53.4943-8)
- [IRS: attribution of ownership rules](https://www.irs.gov/charities-non-profits/private-foundations/attribution-of-ownership-rules-definition-of-disqualified-persons) and [IRS: split-interest trusts](https://www.irs.gov/charities-non-profits/private-foundations/split-interest-trusts)
