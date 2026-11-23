# The keystone rule, checked on every path

The spend checks in this repo grade one deal at a time. This folder asks a
different question: is there **any order of moves** between the roles in the
stack that gets the foundation's value to an insider, even when every single
move passes its own check? A model checker (TLC, for the TLA+ language) tries
every order and either says "none" or hands back the shortest path that breaks
the rule, step by step.

You judge one sentence, not the code. Modeling, not legal advice.

## The rule (yours to judge)

> **No step moves the foundation's money or property to a disqualified person,
> or lets one use it, directly or through someone who passes it on, except pay
> for program work the person actually did, at no more than the market rate,
> and repayment of a loan the person made to the foundation without interest.**

Where each part comes from:

| Part of the sentence | Authority |
|---|---|
| "moves money or property to", "lets one use it" | 26 USC 4941(d)(1)(A)-(E): sale, exchange or lease; loan; furnishing goods, services or facilities; paying compensation; transfer to or use by or for the benefit of a disqualified person |
| "directly or through someone who passes it on" | 4941(d)(1), "any direct or indirect"; 26 CFR 53.4941(d)-1(b) |
| "pay for program work actually done, at no more than the market rate" | 4941(d)(2)(E): personal services "reasonable and necessary to carrying out the exempt purpose", compensation "not excessive" |
| "repayment of a loan made without interest" | 4941(d)(2)(B): a disqualified person's loan to the foundation without interest, used for exempt purposes |
| "disqualified person" | 4946(a)(1); substantial contributor 507(d)(2) |

Two neighbour rules are checked beside it:

- **No taxable grant:** no grant to an organization that is not a public charity
  without expenditure responsibility (4945(d)(4), (h)).
- **No excess holding:** the foundation does not still hold the management
  company's stock when the gift disposition period ends (4943(c)(2)(A), (c)(6)).

How it fits the keystone in [the wiki](../../docs/wiki/Keystone-Constraint.md):
for an insider, the only private enablement the law permits is the 4941(d)(2)(E)
pay. "Incidental" there is "necessary to the exempt purpose" here, and "within
market rate" (K5) is "not excessive". The keystone's wider test for pay to people
who are not insiders (private benefit) is not in this model.

**Pushback on the brief's wording.** The brief said "from the Family Trust or the
foundation". The rule covers the foundation's value only. The family trust is a
private trust: paying its own beneficiaries is its job, not self-dealing. The
letter would reach it only if it were a split-interest trust with a charitable
deduction (4947(a)(2)), and the branch settings say no deduction is claimed. If
that ever changes, 4941 applies to the trust too and the model needs a second
pool of value. That is counsel question 1.

## What the checker found

Run `sh formal/keystone/run.sh` (about 25 seconds). Every config, its result and
the moves on the shortest path:

| Config | Settings | Result |
|---|---|---|
| `pass-branch-b` | family under 35%, insider status from the gift ledger | **holds** on all 103,816 states |
| `pass-branch-a` | family over 35%, insider status from the gift ledger | **holds** on all 31,828 states |
| `finding-typed-screen` | insider status typed by hand (the repo today) | **breaks 4941** in 2 moves |
| `finding-stock-period` | gifted management company stock | **breaks 4943** in 2 moves |
| `break-lease` | lease guard removed on purpose | breaks 4941 in 3 moves |
| `break-excess` | "pay only for work done" removed on purpose | breaks 4941 in 3 moves |
| `break-er` | grant without expenditure responsibility allowed on purpose | breaks 4945 in 2 moves |
| `break-er-keystone` | same, rule 4941 only | breaks 4941 in 3 moves |

Every move in the model fires somewhere in the passing runs except three that are
closed on purpose: leasing the equipment out (PG13 sends personal-property rent
to counsel), lending out (R7 sends it to counsel), and updating the insider
settings (not needed when status comes from the ledger). So the pass is not
empty: gifts, sales, wages, grants, loans in, repayments and private payments
inside the stack all happen, in every order, and none reaches an insider.

### Finding 1: a new big donor is not treated as an insider

Path, in the model's words:

1. An unrelated vendor gives the foundation enough to become a substantial
   contributor (507(d)(2): over $5,000 and over 2% of everything the foundation
   has received).
2. The foundation buys program supplies from that vendor at market price.

Step 2 is self-dealing (4941(d)(1)(A), (C)): the vendor became a disqualified
person at step 1 (4946(a)(1)(A)), and market price does not cure it. Every check
allows it, because insider status in the repo is a setting someone types
(`dm:substantialContributor`, `dm:dqScreened`), not something derived from the
gifts the foundation has received. Nothing makes the setting change before the
next payment.

Replayed on the real checks: a scratch case for that purchase (payee an unrelated
vendor, screened, at market) grades **Allow** in `decide_spend.py`. The scratch
case is not committed.

The fix the model checks: when insider status is derived from a gift ledger
(`DeriveScreen = TRUE`), the rule holds on every path. Building that ledger is a
change to the decision model, so it belongs in its own PR. It is not made here.

### Finding 2: a disposal plan is not a disposal

Path: the founder gives the foundation stock in his management company, with a
written plan to dispose of it (PG3b passes); the disposition period ends with the
stock still held. Because the company is the founder's, the foundation's
permitted holding is nil (4943(c)(2)(A)), so on that day the holding is excess.
The checks grade a holding only when someone asks, and PG3a fires only once the
period is over, which is after the breach. The stock also cannot simply be sold
back to an insider: that sale is itself self-dealing (the model shows only an
unrelated buyer can take it). A dated disposal deadline that a routine watches
would close this. Counsel question 3.

### Proof that the check can fail

Each guard below was removed on purpose, one at a time, and the checker found the
break. All three are restored in the committed model.

- **Equipment lease to the management company** (guards AL0, R3, PG13): the
  founder gives; the foundation buys the equipment; the foundation leases it to
  the management company. That is a lease to and use by a disqualified person
  (4941(d)(1)(A), (E)) whatever the rent.
- **Pay without work** (guards K5, ST1c): the founder gives; the pay record is
  written; the foundation pays the founder with no work done. A record alone is
  not reasonable compensation.
- **Grant without expenditure responsibility** (guard R6): the founder gives;
  the foundation grants to an outside grantee with no agreement (4945 breaks
  here); the grantee pays the founder (4941 breaks here, as an indirect transfer).

Charts of each path, drawn with pstack's `/statechart`, are in [`chart/`](chart/).

## How the model works

- Roles: founder (trustee), a relative, the family trust, the business trust, the
  management company, the foundation, an unrelated vendor, an outside grantee
  that is not a public charity, and a public charity. No real names or amounts.
- Value is three tokens. One token is one unit at market price. A token is
  "the foundation's value" from the moment the foundation receives it until it
  is spent at market or reaches a public charity. A grant stays the foundation's
  value at the grantee until the grantee spends it on its purpose.
- Each move is one action. Its guard is the repo check that must say Allow, and
  the check id is in the comment beside it (`R1`, `AL0`, `H2`, `ST1a`, `K5`,
  `R6`, `PG3b`, `PG13`, `R7`). Anything a check sends to counsel counts as not
  allowed.
- The rule is written separately, from the statute, in `Law` and the invariants
  at the bottom of [`Keystone.tla`](Keystone.tla). No guard reads it.

## What the rule does not cover

- **The family trust's own payouts**, unless it is a 4947(a)(2) split-interest
  trust (see the pushback above).
- **A prearranged kickback.** A purchase at market from an unrelated seller ends
  the foundation's claim to that token. A side deal where the seller pays the
  founder back is outside the model.
- **Grantees that break their agreement.** Under expenditure responsibility the
  model trusts the grantee to spend on the grant's purpose. What the foundation
  must do when one does not (53.4945-5(e)) is not modeled.
- **Organizations the foundation controls.** Their deals with insiders are
  indirect self-dealing (53.4941(d)-1(b)); the model has none.
- **Amounts.** One token is the market rate. Whether a figure is reasonable is
  the benchmark's job (K4, K5, ST1c) and counsel's.
- **Exceptions the repo is stricter than.** An insider's interest-free loan or
  rent-free lease to the foundation is lawful (4941(d)(2)(B), (C)); AL0 holds both
  for review. The model follows the repo, so those routes stay closed.
- **Gifts with debt** (4941(d)(2)(A), PG10), **jeopardy investments** (4944),
  **payout** (4942), **politics** (4945(d)(1)-(2)), **government officials**
  (4946(c)), **the 10-year end of substantial-contributor status**
  (507(d)(2)(C)), and the **4941(d)(2)(F)** corporate-redemption exception.
- **Bounds.** Three tokens, one piece of equipment, one stock block, one unit of
  owed work at a time. A pass covers every order of moves within those bounds.

## Rerun and upkeep

```
sh formal/keystone/run.sh
```

It prints the commit, the files the model covers ([`COVERAGE`](COVERAGE)), any of
them changed since the sync commit, and one line per config with `ok` or
`UNEXPECTED`. It exits 1 if a pass fails, or if a finding or a break stops failing
by the expected path.

To redraw the charts, run pstack's `/statechart` on `Keystone.tla` with a config
from `configs/` and `--view chart/view.mjs`.

The next agent changing any covered file follows
[`.claude/skills/verify-keystone-model/SKILL.md`](../../.claude/skills/verify-keystone-model/SKILL.md).

Counsel questions raised by the model are in [`COUNSEL-QUESTIONS.md`](COUNSEL-QUESTIONS.md).

Method: Lauren Tan's pstack skills `create-formal-verification-skill` and
`statechart`, at commit 7a58391 of cursor/plugins.
