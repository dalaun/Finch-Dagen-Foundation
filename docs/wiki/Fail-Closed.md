# Fail closed: a missing fact is never an allow

## The perspective shift

A guard who waves through anyone without an ID badge is not checking badges. The checks here work the same way: each one is a question asked of the facts on a case ("is the payout below 5 percent?"). If the fact is not there, the question cannot be asked, the check does not fire, and a case with no failed checks reads as **allow**. That is failing open. In a model built to stop self-dealing it is the most dangerous kind of bug, because it looks exactly like a clean result.

The Copilot reviews of PR 15 found seven of these. Deleting each fact from every worked case found the rest: across spends, entity deals and planned gifts, a missing deduction answer, holdings figure, lien answer, wage or benefit amount could turn a block into an allow, and so could a missing link: the seller or buyer in a bargain sale, the trustee of a lead trust, the payer's accounting method, the benefits on a pay deal, the scorer's answer.

## The rule

1. **Required inputs.** `decision/required-inputs.ttl` lists, for each situation, the facts a case in it must state. A split-interest trust must say whether a deduction is claimed, whether the property came under a lien and whether a sale was fixed before the gift. A claimed deduction must answer every test a deduction faces. Foundation pay that states an amount must also state the benchmark and the benefits on top. Each requirement names the checks that read its facts.
2. **Check FC0.** `decide_spend.py` runs every requirement against every case. A case that leaves out a required fact gets FC0, outcome **insufficient**, whatever else it passes. So the answer is "we cannot tell", never "allowed".
3. **State a no.** A "no" is written as `false`, `0` or a named "none" (`NoOneElse` for an asset with no other user, `noFringeBenefits true` for pay with no benefits), never left out. The 61 worked cases that relied on a missing fact meaning no now state it. Those values are assumptions consistent with each scenario, and each is marked in the case file. Examples: an expense claim that is not a home office says `homeOfficeClaim false`; a claim paid in the year says `paidByYearEnd true` and `payerMethod CashMethod`; a remainder unitrust with no stated term says `LivesOnly`; a grant with no insider class says `OpenSelection`; a spend the bounded scorer was not shown says `IntentClean`, which is how those cases were graded before (the scorer's "no" changes nothing).
4. **Conservative defaults.** A fact may be left out only where the check that reads it uses a default at least as strict as any real value. Two do today: PG8 treats missing debt and missing taxes as 0, which makes the required payout larger, never smaller.

## The test

`validate_fail_closed.py` makes one copy of every worked case per stated fact, with that one fact deleted, grades every copy under both insider branches, and fails CI if a copy is graded allow when

- **FC-A** the case itself is not allow (deleting a fact loosened it), or
- **FC-B** the deleted fact is one the case is required to state (FC0 should have caught it).

A copy of an allow case that loses a fact no requirement names may stay allow: that fact was optional, like an election or a note. `--selftest` switches FC0 off and shows the test catches fail-opens in each model.

## Limits

- The test deletes one fact at a time. Two missing facts together are covered only where each is required on its own.
- It covers the worked cases. A new kind of case needs its own requirement before it is protected; the test will flag a new case that fails open.
- The GiftLaw example stories are not held to FC0: they are summaries of pages, which leave facts out by nature. Their grading is in [GiftLaw stories](GiftLaw-Stories.md).

Not legal or tax advice.

## Files

- `decision/required-inputs.ttl`: the requirements.
- `decide_spend.py`: applies FC0 to every case.
- `validate_fail_closed.py`: the mutation test.
