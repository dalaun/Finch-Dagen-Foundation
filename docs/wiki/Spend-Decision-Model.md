# The Spend Decision Model

[← Back to Home](Home.md) | [← Keystone Constraint](Keystone-Constraint.md)

**Status: draft, proposed 2026-11-21. Design and education, not legal or tax advice. Counsel reviews before any of this is relied on.**

Every proposed foundation spend gets one of four answers before money moves:

| Outcome | Means |
|---|---|
| **allow** | Every check passes. |
| **block** | The mission trace or the letter of the law fails. No judgment cures it. |
| **needs counsel** | The facts are known and pass the letter, but the intent question is a judgment. Counsel decides; the spend waits. |
| **insufficient** | A fact a check needs is missing. Never treated as allow. |

When checks disagree, the most severe answer wins: **block > insufficient > needs counsel > allow**. Insufficient ranks above counsel on purpose: nobody should pay a lawyer to judge an incomplete record.

## The idea, and where it comes from

The founder paired two books by Bruce Schneier:

- **Liars and Outliers (2012)** asks why people cooperate. Society uses four *pressures* to keep defectors in line: **moral** (guilt, duty), **reputational** (what others will say), **institutional** (rules, laws, who can decide) and **security** (locks, logs, technical limits).
- **A Hacker's Mind (2023)** asks how rules get gamed. Schneier: "Hacks follow the rules of a system but subvert its goals or intent." His main example is the tax code: "It has vulnerabilities—we call them loopholes." Systems answer a hack in one of two ways: "They either change the system to prevent the hack or they incorporate the hack into the system," and "Courts adjudicate hacks."

The analogy that makes the pairing work: **a private foundation is a system that was already hacked and patched.** Before 1969, deals between a foundation and its insiders only had to be at arm's length. The IRS's own training text says "IRC 503 imposed arm's length standards on prohibited transactions," and those standards "proved to require disproportionately great enforcement efforts." In the Tax Reform Act of 1969 Congress replaced them with "fixed standards that are not dependent in their application on arm's length standards" (IRS EO CPE 1985, eotopicq85). That is Schneier's first answer to a hack: change the system.

So the model has two jobs. Follow the patch exactly (the letter). Then look for the hacks the patch left open (the intent).

## The four stages

```
Proposed spend
  │
  ├─ 0 Evidence      payee known, screened against IRC 4946, spend kind stated  → else insufficient
  ├─ 1 Mission trace the existing keystone and cascade checks (K1–K5, C1–C4, A1) → else block
  ├─ 2 Rule check    the letter of IRC 4941–4945                                 → block, or counsel where the
  │                                                                                law itself is a judgment
  ├─ 3 Hack test     passes the letter, bends the intent                         → needs counsel
  └─ 4 Outcome       most severe answer from stages 0–3
```

Stage 1 is not new. It is the [Keystone](Keystone-Constraint.md) and [Authority Cascade](Authority-Cascade.md) checks, run on the spend, grant or asset each proposal points to.

### Stage 2: the letter (IRC Chapter 42)

Statute text read 2026-11-21 at uscode.house.gov ("current through Public Law 119-120 (October 7, 2026)"); rates from irs.gov pages last updated June to August 2026.

| Check | Rule | Outcome on fail | Source |
|---|---|---|---|
| R1 | The payee is a disqualified person and this is not pay for personal services | block | 4941(d)(1): "any direct or indirect" sale, lease, loan, "furnishing of goods, services, or facilities", or transfer between the foundation and a disqualified person |
| S1 | The spend benefits a disqualified person (existing check) | block | 4941(d)(1)(E): "transfer to, or use by or for the benefit of, a disqualified person" |
| R3 | A disqualified person also uses a foundation asset | block | 4941(d)(1)(E), "use by" |
| R4 | Paid to influence legislation or an election | block | 4945(d)(1) and (d)(2) |
| R5 | Grant to an individual for travel or study, no procedure approved in advance by the IRS | block | 4945(d)(3), (g): "awarded on an objective and nondiscriminatory basis" "pursuant to a procedure approved in advance by the Secretary" |
| R6 | Grant to an organization that is not a public charity, no expenditure responsibility | block | 4945(d)(4), (h): see the grant is spent "solely for the purpose for which made" and get full reports |
| R7 | An investment that is not program-related | needs counsel | 4944(a)(1) "jeopardize the carrying out of any of its exempt purposes"; 4944(c) excepts investments whose "primary purpose" is charitable with "no significant purpose" of income or appreciation |
| R8 | Business holdings over the limit | needs counsel | 4943(c)(2)(A): 20 percent of voting stock "reduced by" what disqualified persons own |

R7 and R8 send to counsel, not block, because the statute's own test there is a judgment (prudence) or has exceptions this draft does not model.

**Who is disqualified (4946).** Substantial contributors, foundation managers ("an officer, director, or trustee"), 20 percent owners of a substantial contributor, members of their family, and corporations, partnerships, trusts or estates in which those persons hold more than 35 percent. "Members of family" is a closed list: spouse, ancestors, children, grandchildren, great grandchildren, and the spouses of those descendants.

**What it costs (4941, current rates on irs.gov).** The self-dealer pays 10 percent of the amount involved per year, then 200 percent if not corrected; a manager who knowingly takes part pays 5 percent, then 50 percent. "There is no maximum on the liability of the self-dealer." And unlike the other four taxes, self-dealing's initial tax cannot be set aside for reasonable cause. Taxable expenditures (4945): 20 percent on the foundation, then 100 percent. Failure to distribute (4942): 30 percent, then 100 percent.

### Stage 3: the hack test

These are moves that pass every letter check above and still bend the intent. Each goes to counsel.

| Check | The hack | Why the letter misses it |
|---|---|---|
| H1 | Pay someone who sits right next to a disqualified person: a sibling, a friend, a business partner, a company the founder owns 35 percent or less of | 4946(d) leaves siblings out of "family"; the 35 percent line leaves minority stakes out |
| H2 | Pay a third party who passes the value on to a disqualified person (a grantee that hires the founder's child) | Reaches the letter only as "indirect" self-dealing or "for the benefit of"; the IRS says the indirect rules exist "to prevent transactions from taking place indirectly" that could not be done directly |
| H3 | A real program whose eligible class is drawn around insiders or their business (training open only to the founder's consulting clients) | The mission label passes; the charitable class does not (4945(d)(5), (g)) |
| H4 | Split one person's pay across two programs, each under its own benchmark | A hack of **this model**, now patched: K5 tests one payment at a time, so H4 sums per payee per year |
| H5 | Insider pay with no written comparability record | 4941(d)(2)(E) allows pay to a disqualified person only if reasonable, necessary and "not excessive"; the founder setting his own pay is where that judgment is disputed |
| J1, J2 | Anything the rules above did not foresee | The bounded scorer (below) |

### The bounded scorer (the Jev pattern)

A local model answers one closed question per proposal: *"In substance, does this spend's benefit reach a disqualified person, or serve something other than the charitable class?"* It may answer only **no**, **yes** or **cannot tell**.

- **yes** raises the outcome to needs counsel (J1).
- **cannot tell** raises it to insufficient (J2). It is never folded into "no".
- **no** changes nothing.

The scorer can only raise an outcome, never lower one. A blocked spend stays blocked whatever the model says. That keeps the model where it is useful (catching what the rules did not foresee) and out of where it is dangerous (talking a rule out of a block). The graded cases below are the answer key that calibrates it.

## The pressures: who enforces each check

Every check names the pressure that enforces it in the real world:

- **Institutional:** the Chapter 42 excise taxes, IRS examination, counsel review.
- **Security:** these checks run before money moves; the repo's merge lock; trustee-only signers.
- **Reputational:** the foundation's annual return is public (the public-inspection rule is not verified in this draft).
- **Moral:** the founder's own sense of duty.

One rule follows from the book's point, in a reviewer's words, that "Moral pressure is most effective in smaller groups". In a foundation one person controls, that person is both the conscience and the possible defector. So **check P1 fails any check that only moral pressure (or none) enforces**. An honor-system check, such as "the founder attests the spend serves the mission", is where a hack lives. The probe `Probe_HonorCheck` fails P1 on purpose.

The founder's pressure table maps straight onto this: moral, reputational, institutional and security name the enforcer; "none" (not a pressure, not enough signal) is the gap P1 looks for.

## Worked cases

All synthetic, all amounts illustrative. Run `python3 decide_spend.py` to grade them.

| Case | Outcome | Checks failed | Lesson |
|---|---|---|---|
| P01 Unrelated trainer at market | allow | none | The normal case |
| P02 Curriculum grant to a public charity | allow | none | |
| P03 Founder's personal travel | block | C1 R1 S1 | Fails the mission trace and the letter three ways |
| P04 Founder paid to direct a program, no comparability record | needs counsel | H5 | Legal if reasonable; prove it first |
| P05 Same pay with a written comparability record | allow | none | The record is what moves it |
| P06 Founder's management company paid a market fee | needs counsel | H5 | Whether the pay-for-services exception reaches a company the founder owns is a counsel question (not verified) |
| P07 Founder's sibling hired as instructor at market | needs counsel | H1 | Passes the letter; a sibling is not "family" under 4946(d) |
| P08 Grant to a friend's charity that will hire the founder's child | needs counsel | H1 H2 | Likely indirect self-dealing |
| P09 Scholarships picked by the founder, no approved procedure | block | R5 | |
| P10 Grant to a resident LLC, no expenditure responsibility | block | R6 | |
| P11 The same grant with expenditure responsibility | allow | none | Same money, different paperwork, different answer |
| P12 Low-interest loan to a resident-owned co-op | allow | none | Program-related investment |
| P13 Endowment into an index fund | needs counsel | R7 | Prudence is a judgment |
| P14 Buy 15 percent of the operating company while the business trust holds 30 percent | needs counsel | R7 R8 | Insiders hold 30, so the limit is 20 − 30 and any holding is over. The foundation's own total is 27: 15 bought plus 12 attributed through the trust chain (4943(d)(1)). Exceptions to check. Bought from the business trust itself, it would also be R1 |
| P15 Lobbying contract | block | C1 R4 | |
| P16 Program van the founder drives on weekends | block | R3 | Passes the asset-to-program check; fails "use by" |
| P17 Training cohort only for the management company's clients | needs counsel | H3 | Mission label, private class |
| P18a/b One contractor paid by two programs | needs counsel | H4 | Each payment passes K5; the sum does not |
| P19 Payee never screened | insufficient | E1 | |
| P20 Resort workshop series, scorer says yes | needs counsel | J1 | |
| P21 Same, scorer says cannot tell | insufficient | J2 | |
| P22 Rent to the family trust for program space, at market | block | R1 | Leasing with a disqualified person is self-dealing at any price |
| P23 Program T-shirts bought from the operating company | block | R1 | A sale of goods with a disqualified person, at any price |
| P24 Grant to the family trust, no expenditure responsibility | block | R1 R6 | Insider, and a non-charity grantee with no expenditure responsibility |

These are the default answers (insider branch A: the family trust is over the line). [Insider branches](../../rehearsal/09-insider-branches.md) runs the same cases with the family trust under the line and sweeps its settings one at a time.

## What this draft found that changes the plan

1. **For anything that touches a disqualified person, the letter is already the strict part.** Since 1969 the IRS applies the self-dealing rules "without regard to whether the foundation has suffered a detriment"; "it is immaterial whether the transaction results in a benefit or a detriment to the private foundation." So a fair-priced deal with an insider is a block, not a counsel question. The only door is reasonable pay for personal services. The hack test matters where the law still uses judgment, and at the edges of the 4946 definition.
2. **The stack's own entities need a disqualified-person answer.** The management company is disqualified if insiders own more than 35 percent (4946(a)(1)(E)). The family trust and the business trust turn on whether they fund the foundation (substantial contributor) and who holds more than 35 percent of their beneficial interest (4946(a)(1)(G)). The chain ends at the foundation as a beneficiary, which makes this non-obvious. Until counsel answers, the model treats both trusts as disqualified (fail closed). [Insider branches](../../rehearsal/09-insider-branches.md) sets the family trust's facts (family share, substantial contributor, trustee pay, charitable deduction) and derives the answer from them.
3. **The existing asset-to-program check (A1) is stricter than the law.** It would block an ordinary endowment investment, which 4942's "minimum investment return" assumes a foundation has. Investments skip stage 1 and go to R7 and R8 instead. **Decided (Nov 20, 2026, the founder's call):** keep investments on their own test. A1 stays the rule for spending, and investments are judged by R7 and R8.

## Not verified in this draft

- Treasury regulations were not read: the incidental-benefit rule for self-dealing, whether the pay-for-services exception covers payments to an entity, the prudence standard for jeopardizing investments, expenditure responsibility for program-related investments, and whether "legislation" covers local councils.
- The 4943 exceptions (de minimis, third-party control, disposal periods) are not modeled.
- The public-inspection rule for a foundation's annual return was not read.
- Schneier was read through his own essay on *A Hacker's Mind* and a published review of *Liars and Outliers*, not the books themselves. The pressure descriptions above are the reviewer's summary.

## Questions for counsel

1. Are the family trust and the business trust disqualified persons as to the foundation, under 4946(a)(1)(A) or (G)?
2. Does 4941(d)(2)(E) cover a management fee paid to a company the founder owns, or only pay to individuals?
3. Is pay to a founder's sibling, at market and for real services, acceptable, and what record should support it?
4. Should the foundation hold an endowment at all at this size, and if so under what investment policy?

## Files

- `decision/spend-decision-model.ttl`: outcomes, pressures, every check with its stage, outcome on failure, enforcer and source.
- `decision/spend-decision-shapes.ttl`: the SHACL checks for stages 0, 2 and 3, and P1.
- `tests/decision/decision-cases.ttl` and `expected.ttl`: the worked cases and the answer key.
- `decide_spend.py`: runs stage 1 (the keystone shapes) and stages 0, 2 and 3 together and grades the result.

```
pip install rdflib pyshacl
python3 decide_spend.py
```
