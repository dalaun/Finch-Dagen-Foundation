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

Run `sh formal/keystone/run.sh` (about 40 seconds). Every config, its result and
the moves on the shortest path:

| Config | Settings | Result |
|---|---|---|
| `pass-branch-b` | family under 35%, the repo's checks | **holds** on all 147,016 states |
| `pass-branch-a` | family over 35%, the repo's checks | **holds** on all 44,868 states |
| `limit-stock-sale` | gifted management company stock, nobody sells | breaks 4943 in 3 moves, **after** the checks block the holding |
| `break-typed-screen` | insider status typed by hand, as the repo had it | breaks 4941 in 2 moves |
| `break-undated-plan` | disposal plan with no date, as the repo had it | breaks 4943 with no warning, in 2 moves |
| `break-lease` | lease guard removed on purpose | breaks 4941 in 3 moves |
| `break-excess` | "pay only for work done" removed on purpose | breaks 4941 in 3 moves |
| `break-er` | grant without expenditure responsibility allowed on purpose | breaks 4945 in 2 moves |
| `break-er-keystone` | same, rule 4941 only | breaks 4941 in 3 moves |

Every move in the model fires somewhere in the passing runs except three that are
closed on purpose: leasing the equipment out (PG13 sends personal-property rent
to counsel), lending out (R7 sends it to counsel), and updating the insider
settings by hand (gone since insider status comes from the ledger). So the pass
is not empty: gifts, sales, wages, grants, loans in, repayments and private
payments inside the stack all happen, in every order, and none reaches an insider.

### Finding 1, fixed: a new big donor is now treated as an insider

The checker's path, before the fix:

1. An unrelated vendor gives the foundation enough to become a substantial
   contributor (507(d)(2): over $5,000 and over 2% of everything the foundation
   has received by the end of that year).
2. The foundation buys program supplies from that vendor at market price.

Step 2 is self-dealing (4941(d)(1)(A), (C)): the vendor became a disqualified
person at step 1 (4946(a)(1)(A)), and market price does not cure it. The checks
allowed it, because insider status was a setting someone typed.

The fix: insider rule **IR10** derives every substantial contributor from the
foundation's gift ledger (`tests/decision/gift-ledger.ttl` for the worked cases),
testing the 2% line at the close of each year the person gave, so a later large
gift from someone else cannot dilute a status already reached (507(d)(2)(B)(iv)).
Check **L1** makes every spend Insufficient while the ledger is not confirmed
complete or holds a gift with no giver, no amount as a number or no date. The
config that typed status by hand is now `break-typed-screen`: it must keep
failing, so nobody can bring typed status back without the checker saying so.

Worked cases: P27 (vendor gave 4.1%: Block, R1), P28 (gave over $5,000 but
1.2%: Allow), P29 (gave in the first year, now under 2%: still Block, R1). With
IR10 and L1 switched off, P27 and P29 grade Allow.

### Finding 2, fixed as far as checks can: a plan must have a date

Before the fix: the founder gives stock in his management company with a written
plan to dispose of it (PG3b passes), and the disposition period ends with the
stock still held. The foundation's permitted holding is nil (4943(c)(2)(A)), so
on that day the holding is excess, and the first check that noticed (PG3a)
fired after the breach.

The fix, in `decision/planned-giving-shapes.ttl`:

- A written plan must state when the holding was received, the date it sells by,
  and the date the case is graded, or the gift is Insufficient (FC0).
- **PG3c** (needs counsel): the plan's date is on or after the end of the
  4943(c)(6) period (five years from the gift, ten with a (c)(7) extension).
- **PG3d** (block): the plan's date has passed and the excess is still held, or
  the dates show the period is over whatever `yearsSinceAcquired` says.

Worked cases: G46 (on track: Allow), G47 (no date: Insufficient), G48 (dated the
day the period ends: PG3c), G49 (date passed, still held: PG3d), G50 (years typed
as 3, dates show year 6: PG3d). With PG3c, PG3d and the date requirement switched
off, G47 to G50 grade Allow.

What a check cannot do is sell the stock. `limit-stock-sale` shows the honest
limit: if nobody sells, the period still ends with the stock held. The new
property **AlarmBeforeBreach** holds on every path: before that day comes, the
checks have already blocked the holding at the plan's own date, while a sale can
still cure it. `break-undated-plan` shows the old code broke it. A reminder that
watches each plan's date turns that block into a message in time.

### Proof that the check can fail

Each guard below was removed on purpose, one at a time, and the checker found the
break. All are restored in the committed model.

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
- **Insider status typed by hand** and **an undated plan**: the two findings above.

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
  `R6`, `PG3b`, `PG3c`, `PG3d`, `PG13`, `R7`, `IR10`, `L1`). Anything a check sends to
  counsel counts as not allowed.
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
- **Who counts as a substantial contributor, at the edges.** IR10 does not add a
  spouse's gifts to the person's own, treat a trust's creator as a contributor,
  or end the status after ten years (507(d)(2)(A), (C)). It treats a giver as an
  insider for every spend once the line is crossed, even a spend dated before the
  gift that crossed it, which is stricter than the law may be (counsel question 2).
  In the model, any gift is big enough.
- **Selling the stock.** The checks block the holding before the period ends; a
  person still has to sell it (`limit-stock-sale`).
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
`UNEXPECTED`. It exits 1 if a pass fails, or if a limit or a break stops failing
by the expected path.

To redraw the charts, run pstack's `/statechart` on `Keystone.tla` with a config
from `configs/` and `--view chart/view.mjs`.

The next agent changing any covered file follows
[`.claude/skills/verify-keystone-model/SKILL.md`](../../.claude/skills/verify-keystone-model/SKILL.md).

Counsel questions raised by the model are in [`COUNSEL-QUESTIONS.md`](COUNSEL-QUESTIONS.md).

Method: Lauren Tan's pstack skills `create-formal-verification-skill` and
`statechart`, at commit 7a58391 of cursor/plugins.
