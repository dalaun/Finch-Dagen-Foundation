---
name: verify-keystone-model
description: "Check a change to the Finch-Dagen spend checks against the keystone model in formal/keystone (TLA+, TLC). Use when a change touches the insider rules, the self-dealing, arm's-length, stewardship, keystone or planned-giving shapes, the branch settings, decide_spend.py, or the model itself, or when asked whether any order of moves gets foundation value to an insider."
---

# Verify the keystone model

`formal/keystone/Keystone.tla` models the moves between the stack's roles
(founder, relative, family trust, business trust, management company,
foundation, vendor, outside grantee, public charity). Each move's guard stands
for a repo check that must say Allow. The rule, written from 26 USC 4941, is:

> No step moves the foundation's money or property to a disqualified person, or
> lets one use it, directly or through someone who passes it on, except pay for
> program work the person actually did, at no more than the market rate, and
> repayment of a loan the person made to the foundation without interest.

Harm when it breaks: a self-dealing excise tax on the insider and, for a
manager who agreed, on the manager (4941(a)), and a correction duty (4941(b)).

## Does the change touch it?

The covered files and the sync commit are in `formal/keystone/COVERAGE`. A
change touches the model if it edits a covered file, adds a check that blocks or
allows a deal with an insider, adds a new kind of move between the roles, or
changes how insider status is decided. Each guard in `Keystone.tla` names its
check id in a comment:

| Guard in the model | Repo check | File |
|---|---|---|
| payee not an insider | R1, S1 | decision/spend-decision-shapes.ttl |
| no deal with an insider | AL0 | decision/stewardship-shapes.ttl |
| asset not used by an insider | R3 | decision/spend-decision-shapes.ttl |
| payee passes nothing on to an insider | H2, AL4 | spend-decision-shapes.ttl, stewardship-shapes.ttl |
| pay record before payment | ST1a, ST2, H5 | stewardship-shapes.ttl, spend-decision-shapes.ttl |
| pay only for work done, within benchmark | K5, ST1c | trust-domain-keystone-shapes.ttl, stewardship-shapes.ttl |
| grant needs expenditure responsibility | R6 | spend-decision-shapes.ttl |
| loan out goes to counsel | R7 | spend-decision-shapes.ttl |
| equipment rent goes to counsel | PG13 | decision/planned-giving-shapes.ttl |
| stock gift needs a disposal plan | PG3b | planned-giving-shapes.ttl |
| the plan's date falls before the period ends | PG3c, RI_DispositionPlanDates | planned-giving-shapes.ttl, decision/required-inputs.ttl |
| holding blocked once the plan's date passes | PG3d | planned-giving-shapes.ttl |
| who is an insider | IR3, IR4, IR5, IR10 (gift ledger), L1 | decision/spend-decision-model.ttl, tests/decision/branch-*.ttl, tests/decision/gift-ledger.ttl |

## Run it

```
sh formal/keystone/run.sh
```

Needs Java 11+ and curl; it fetches TLC 1.7.4 once and checks its sha256. About
40 seconds. Every line must say `ok`:

- `pass-*` configs must pass.
- `limit-*` configs show what checks cannot do (a person must still sell the
  gifted stock). They must fail on the named rule by the named path.
- `finding-*` configs, when there are any, are known findings in the current
  code. They must fail by the named path until the code is fixed.
- `break-*` configs remove one guard on purpose, or put back how the code worked
  before a finding was fixed. They must fail. If one passes, the model lost its
  ability to fail: fix the model, not the break.

## Read a result

Read every failing path with pstack's `/statechart` skill and the view in
`formal/keystone/chart/view.mjs`. It prints the shortest path in plain words.
Then replay the path on the real checks, one move per step, as a scratch case in
a copy of the repo graded by `python3 decide_spend.py`:

- If a step cannot happen in the checks, the model is wrong. Fix the model and
  say what was wrong.
- If every step happens and the last one grades Allow, it is a bug in the
  checks. Report it with the path in the checks' words and the harm in one
  sentence. Do not loosen the rule or the model to make it pass, and do not
  change product code unless asked.

## When a change is meant to change the promise

Change the rule sentence and the invariants only when the change says so on
purpose (the commit message, the wiki, or the answer key). Write the old and new
wording and the evidence in the PR.

## Keep it in step

After you confirm the model still describes the checks at a new commit, set
`sync-commit` in `formal/keystone/COVERAGE` to that commit, and add any new
covered file. Do not move the sync commit for a run you could not finish.

## When a finding is fixed

Do not flip a finding to pass. Change the guard constant that described the old
code (as `DeriveScreen` and `DatedPlan` did) so the passing configs describe the
fixed code, and rename the finding's config to `break-*`, so it keeps failing and
guards against the old behavior coming back. Do it in the same PR as the fix, with
worked cases that fail when the fix is switched off.
