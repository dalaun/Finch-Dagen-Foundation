# Insider branches: when the family trust counts as an insider

**Status:** rehearsal, 2026-11-20. Synthetic settings, roles only. Nothing here moves money or changes a trust.

**This is design and education, not legal or tax advice.** Counsel reads the real trust documents and decides which settings are true.

## The facts this page starts from

- The founder is the family trust's **trustee**. He is not a beneficiary.
- The family trust's beneficiaries are **the foundation and family members**.
- The family trust holds the beneficial interest of the business trust, which owns the operating company. The operating company pays the founder's management company a fee.

The founder is an insider to the foundation in every case, as its manager. The open question is whether the **trust** is one too.

## The perspective shift: a steward's keys are not an owner's share

A trustee holds the keys to the building. The beneficiaries own the rent. The law looks at the rent. 4946(a)(1)(G) makes a trust an insider when insiders "hold more than 35 percent of the beneficial interest", and 53.4946-1(a)(4) measures that share "in proportion to the actuarial interest of such person in the trust." The founder's stewardship role puts nothing on that scale.

What does count is the founder's **family** as the tax code defines it: "spouse, ancestors, children, grandchildren, great grandchildren, and the spouses of children, grandchildren, and great grandchildren" (4946(d)). The regulation adds that "a brother or sister of an individual is not a member of his family" (53.4946-1(h)).

## The answer, in three lines

1. **The 35 percent line is real.** If the founder's 4946(d) family hold 35 percent or less of the trust's actuarial value, the 35 percent rule doesn't make it an insider. At 36 percent it is one. Siblings, nieces and nephews never count toward the line.
2. **The bigger trap is funding the foundation.** A trust is a "person" ("an individual, a trust, estate", 7701(a)(1)). One that gives the foundation "more than $5,000" and "more than 2 percent of the total contributions" becomes a substantial contributor (507(d)(2)(A)), which makes it an insider under 4946(a)(1)(A) **whatever the family's share is**. That status is close to permanent: a substantial contributor "shall remain a substantial contributor for all subsequent periods" (507(d)(2)(B)(iv)), unless a 10-year rule in 507(d)(2)(C) ends it. A trust whose job includes funding the foundation is likely to cross this line.
3. **Under the line is not the same as clean.** Even when the trust isn't an insider, money the foundation pays it can reach the family through distributions. That is the "for the benefit of" test in 4941(d)(1)(E), so those deals go to counsel instead of passing. Only with no family share at all does a market-rate lease simply pass.

## What the sweep shows

`python3 decide_spend.py --sweep` starts from branch B and changes one setting per row. The last column is the 4943 test on P14: the foundation's own share of the operating company, then the insiders' share.

| Family trust settings | Insider? | P22 rent to the trust | P23 buy from the operating company | P24 grant to the trust | P14 4943 % |
|---|---|---|---|---|---|
| Family 0%, siblings 30% | no | allow | needs counsel (H2) | block (R6) | 27 / 0 |
| **Family 30%, siblings 30% (branch B)** | no | needs counsel (H2) | needs counsel (H2) | block (H2, R6) | 27 / 9 |
| Family 35% | no | needs counsel (H2) | needs counsel (H2) | block (H2, R6) | 27 / 10.5 |
| Family 36% | **yes** | block (R1) | block (R1) | block (R1, R6) | 27 / 30 |
| **Family 60% (branch A, the default)** | yes | block (R1) | block (R1) | block (R1, R6) | 27 / 30 |
| Family 30%, trust is a substantial contributor | **yes** | block (R1) | block (R1) | block (R1, R6) | 27 / 30 |
| Family 30%, trustee paid | no | needs counsel (H2) | needs counsel (H2) | block (H2, R6) | 27 / 9 |
| Family 30%, deduction allowed, foundation holds remainder only | no | needs counsel (H2) | needs counsel (H2) | block (H2, R6) | 15 / 9 |

How to read it:

- **P23 never passes.** Even when no trust is an insider, the operating company pays the founder's management company, so the hack test (H2) sends it to counsel.
- **P24 never passes.** A grant to a trust that isn't a public charity needs expenditure responsibility in every row (4945(d)(4), (h)).
- **P14 never passes.** Under 4943(d)(1), stock held through the trusts counts "as being owned proportionately by or for its ... beneficiaries". The foundation's attributed 12 percent plus the 15 percent it buys puts it at 27, over the 20 percent limit, before any insider is counted. The excess-business-holdings question about the operating company exists whatever the insider answer is.

## Trustee pay

Paying the founder to be trustee doesn't make the trust an insider, because a fee isn't a beneficial interest. It is another path for foundation money to reach an insider, so the hack test flags any foundation payment to the trust. If the trust is split-interest (below), the trust itself is held to the self-dealing rules "as if such trust were a private foundation" (4947(a)(2)). Its trustee's pay would then need to meet the reasonable-pay exception: services "reasonable and necessary to carrying out the exempt purpose", where the pay "is not excessive" (4941(d)(2)(E)). Whether a split-interest trust's trustee is its "foundation manager" under 4946(b) is an inference, not verified.

## Split-interest: when the trust gets its own rules

4947(a)(2) applies to a trust with charitable and family interests only if it "has amounts in trust for which a deduction was allowed under section 170, 545(b)(2), 642(c), 2055, 2106(a)(2), or 2522". The 642(c) item is a trust's own deduction for amounts set aside for charity, so a trust can trigger this simply by taking its charitable deduction. That is an inference to confirm.

When it applies, the self-dealing, excess-business-holdings, jeopardizing-investment and taxable-expenditure rules apply to the trust itself. Payments to family under the trust's terms are carved out ("any amounts payable under the terms of such trust to income beneficiaries"). In exchange, if the foundation "holds only an income interest or only a remainder interest", 4943(d)(1) stops counting the trust's business stock as the foundation's. The last sweep row shows the effect: 27 drops to 15, but the family's insider share still squeezes the limit.

4947(a)(1), which treats a trust as a 501(c)(3) organization, needs "all of the unexpired interests" to be charitable. With family beneficiaries, it doesn't apply.

## The counsel questions, now short

1. What is the actuarial share held by the founder's 4946(d) family? It has to be 35 percent or less to keep the trust off the insider list under (G).
2. Do the trust's payments to the foundation count as "contributions" under 507(d)(2)? If they do, the trust becomes an insider once it gives enough, and stays one. **This is the question that decides the branch.**
3. Has a charitable deduction been allowed for amounts in the trust, including its own 642(c) deduction? If so, it is a split-interest trust with its own rules.
4. What should the plan be for the operating company under 4943? The attributed holdings are over the limit in every branch.

## How it's built

- Each branch is a facts file. `tests/decision/branch-a.ttl` (over the line, the default) and `branch-b.ttl` (under the line) set the family trust's settings: the family share, the share held by other relatives, the foundation's share and kind of interest, whether it is a substantial contributor, whether a deduction was allowed, and whether the trustee is paid.
- Nobody types in "insider: yes". The insider rules IR1 to IR9 in `decision/spend-decision-model.ttl` derive it from the settings, each with its source, before the checks run. That's the "red flags into checks" rule applied to the trusts.

```
pip install rdflib pyshacl
python3 decide_spend.py              # branch A, graded against tests/decision/expected.ttl
python3 decide_spend.py --branch B   # branch B, graded against expected.ttl plus expected-branch-b.ttl
python3 decide_spend.py --compare    # what flips between A and B
python3 decide_spend.py --sweep      # one setting at a time
```

## Not verified

- The text of 267(c)(1). It was read only through the IRS attribution page: stock "is considered owned proportionately by or for its shareholders, partners, or beneficiaries".
- Whether a trust's distributions to its charitable beneficiary are "contributions" for 507(d)(2) (counsel question 2).
- Whether a split-interest trust's trustee is its foundation manager under 4946(b), and whether the indirect self-dealing control test (53.4941(d)-1(b)(5)) reaches a trust the founder controls as trustee rather than as a foundation manager. The regulation counts control by "the foundation or one or more of its foundation managers (acting only in such capacity)".
- How grantor-trust status, if any, changes the beneficial-interest count.
- The 4943 exceptions and disposition periods, and the actuarial tables used to value income and remainder interests.

## Sources

- [26 USC 4946](https://uscode.house.gov/us/usc/119-118/t26/s4946/), [4947](https://uscode.house.gov/us/usc/119-118/t26/s4947/), [4943](https://uscode.house.gov/us/usc/119-118/t26/s4943/), [4941](https://uscode.house.gov/us/usc/119-118/t26/s4941/), [507](https://uscode.house.gov/us/usc/119-118/t26/s507/) (current through PL 119-120)
- [26 USC 7701 (2011 edition)](https://www.govinfo.gov/content/pkg/USCODE-2011-title26/html/USCODE-2011-title26-subtitleF-chap79-sec7701.htm)
- [Treas. Reg. 53.4946-1](https://ecfr.io/Title-26/Section-53.4946-1), [53.4943-8](https://ecfr.io/Title-26/Section-53.4943-8), [53.4941(d)-1](https://www.law.cornell.edu/cfr/text/26/53.4941(d)-1)
- IRS: [attribution of ownership rules](https://www.irs.gov/charities-non-profits/private-foundations/attribution-of-ownership-rules-definition-of-disqualified-persons), [split-interest trusts](https://www.irs.gov/charities-non-profits/private-foundations/split-interest-trusts), [indirect self-dealing: control](https://www.irs.gov/charities-non-profits/private-foundations/indirect-self-dealing-control-of-organization-by-private-foundation)
