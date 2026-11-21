# Fail closed: a missing or unknown fact is never an allow

## The perspective shift

A guard who waves through anyone without an ID badge is not checking badges. The checks here work the same way: each one is a question asked of the facts on a case ("is the payout below 5 percent?"). If the fact is not there, the question cannot be asked, the check does not fire, and a case with no failed checks reads as **allow**. That is failing open. In a model built to stop self-dealing it is the most dangerous kind of bug, because it looks exactly like a clean result.

A badge with a misspelled name fails the same way. A check that looks for one term ("is the unitrust term `LifeThenTerm`?") does not see a near miss (`LifeThenTerms`), so a forged badge gets the same wave-through as no badge.

The Copilot reviews of PR 15 found seven of the first kind. Deleting each fact from every worked case found the rest.

## Why the first fail-closed check missed two more

The third review found two cases the first version let through:

- **A misspelled unitrust term was allowed.** The check asked only "is a term stated?", and a misspelled one is stated. It never asked whether the term was one the checks know.
- **A benefit with no yearly value counted as 0.** The value sits on the benefit's own record, linked from the pay deal. The check only looked at the deal itself, and the test only deleted facts on the deal, so neither ever reached the record.

The fix goes in at the root rather than one case at a time: every fact must be known, not only present, and a record a case links to is held to the same rule as the case.

## The rule

1. **Required inputs.** `decision/required-inputs.ttl` lists, for each situation, the facts a case in it must state. A split-interest trust must say whether a deduction is claimed, whether the property came under a lien and whether a sale was fixed before the gift, and so must a gift to the foundation that names who transfers it. Property under a lien must say whether the trust assumes the debt. A claimed deduction must answer every test a deduction faces. Foundation pay that states an amount must also state the benchmark and the benefits on top. Each requirement names the checks that read its facts.
2. **Linked records.** A requirement can be about a record the case links to. Each benefit on a pay deal must say what it is and what it is worth a year. An excluded benefit must also state what its limit and its nondiscrimination rule read. A missing fact there makes the deal insufficient.
3. **Known terms.** Every fact on a case, and on the records it links to, must mean something to the checks:
   - the property is declared in the model;
   - a value from a closed list (`owl:oneOf`, such as the unitrust terms) is on the list;
   - a value of any other declared kind is declared to be one. Every party a case names (payee, payer, trustee, buyer, reviewer) is declared a `dm:Party`, and every fiscal year a `dm:FiscalYear`, so a misspelled name is not a stranger who passes every insider check;
   - any other named value is declared somewhere;
   - a yes/no is a boolean and an amount is a number. Text there is set aside before the checks run, because a sum over text would stop the whole grading.
4. **Check FC0.** `decide_spend.py` applies rules 1 to 3 to every case. A case that breaks one gets FC0, outcome **insufficient**, whatever else it passes. So the answer is "we cannot tell", never "allowed".
5. **State a no.** A "no" is written as `false`, `0` or a named "none" (`NoOneElse` for an asset with no other user, `noFringeBenefits true` for pay with no benefits), never left out. The worked cases that relied on a missing fact meaning no now state it. Those values are assumptions consistent with each scenario, and each is marked in the case file.
6. **Conservative defaults.** A fact may be left out only where the check that reads it uses a default at least as strict as any real value. Two do today: PG8 treats missing debt and missing taxes as 0, which makes the required payout larger, never smaller.

The known-term rule also found a clash in the model itself: two files used the name `InterestKind` for two different closed lists. The planned-giving one is now `CharitableInterest`.

## The test

`validate_fail_closed.py` changes one fact at a time on every worked case, in two ways:

- **delete:** one copy per stated fact, with that fact deleted, including facts on the records the case links to;
- **misspell:** one copy per named or typed value, with the value replaced by one no file declares.

Each copy is **graded in place**: the case is swapped for its copy in a graph that holds every other case as it is. A copy never sits beside its own original or beside another copy that a check could add up with it. H4 (split pay) is the one check that reads more than one case, so proposals for one payee in one year are never changed in the same graph. A new check that reads more than one case fails the test until it is declared, so copies cannot be pooled again by accident.

The test fails CI if a copy is graded allow when

- **FC-A** the case itself is not allow (deleting a fact loosened it),
- **FC-B** the deleted fact is one the case or its record is required to state, or
- **FC-C** a value was misspelled.

A copy of an allow case that loses a fact no requirement names may stay allow: that fact was optional, like an election or a note. Deletions run under both insider branches, misspellings under branch A (whether a term is known does not depend on the branch). `--selftest` switches FC0 off and shows the test catches all three kinds, including a fact on a linked record.

## Speed, without sampling

The full test went from about 15 minutes to under 2, with every case and every fact still tried. Most of the time was going to rdflib reading the text of each check again for every case it graded. `fast_sparql.py` reads each text once and reuses it. The answers are the same: every grading in CI gave the same output before and after the change. The copies are graded four at a time.

## Limits

- The test changes one fact at a time. Two missing facts together are covered only where each is required on its own.
- It covers the worked cases. A new kind of case needs its own requirement before it is protected; the test will flag a new case that fails open.
- A misspelling that lands on another declared term of the right kind (one real party named in place of another) is a wrong fact, not an unknown one, and FC0 cannot see it.
- The GiftLaw example stories are not held to FC0: they are summaries of pages, which leave facts out by nature. Their grading is in [GiftLaw stories](GiftLaw-Stories.md).

Not legal or tax advice.

## Files

- `decision/required-inputs.ttl`: the requirements.
- `decide_spend.py`: applies FC0 (missing inputs and unknown terms) to every case.
- `validate_fail_closed.py`: the in-place delete and misspell test.
- `fast_sparql.py`: reads each check's text once.
