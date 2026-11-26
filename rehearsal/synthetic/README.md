# Synthetic year

[Back to the rehearsal overview](../README.md) · [Loop goal and score](../loop/GOAL.md)

**Everything here is SYNTHETIC.** No line is the founder's spending, income, merchants, accounts or names. Each amount comes from a public benchmark with its URL, or from an assumption that is labelled ASSUMPTION or PLACEHOLDER where it is set. Design and education, not legal, tax or financial advice.

## Why it exists

The rehearsal (03-ab-rehearsal-spec.md) needs twelve months of transactions to fly. Real exports don't exist yet (06-handoff-transaction-export.md). This builds a stand-in year with the same columns, so the runner works now and runs unchanged on the real export later.

## Files

| File | What it holds |
|---|---|
| benchmarks-ce.json | BLS Consumer Expenditure Survey, Chicago area and US income fifths: what an average household spends by category |
| benchmarks-tax.json | 2026 federal brackets and deductions (Rev. Proc. 2025-32), payroll and pre-tax payroll rules (125, 3121), Illinois rates and fees, Chicago wages (BLS OEWS), HUD fair market rents, Cook County property tax, and the grantor-trust rule text |
| scenarios.json | The spending lines, each mapped to a domain in 02, and four scenarios: base, lean, a rental held in the stack, a bought service business held in the stack |
| stack.json | Stack versions in roles (today, flat, flat with an independent trustee), the facts each one asserts for checks S1-S17, placeholder fees, and which spend case grades each flow |
| synthetic_year.py | Seeded generator. Same seed, byte-identical ledger |
| rehearsal_run.py | Arm A, B-ops and each stack version: 2026 tax engine, structure checks from facts, spend flows graded by a real `decide_spend.py` run or the answer key, break-even asset income |
| structure-cases-facts.json | Facts for structure cases SK1-SK14, so the selftest proves the fact-based checks match structure-check-cases.ttl |
| declared_plan.py, declared-plan-synthetic.json | Declared plans ([DECLARED-PLAN.md](DECLARED-PLAN.md)): the accountable plan (Reg. 1.62-2) on the management company, and the same declare-prove-reconcile shape for Foundation reimbursements, expenditure responsibility and the Form 1023 narrative |
| substance.py, substance-synthetic.json | Substance at every step ([SUBSTANCE.md](SUBSTANCE.md)): each route declares a non-tax purpose first, every step must change something real apart from tax (7701(o), substance over form), and each route is tagged with the tool it uses |
| hiring.py, hiring-synthetic.json | Hiring to meet the owner limits ([HIRING.md](HIRING.md)): arm's length, substance, attribution (1563, 318) and board approval on every hire; family, unrelated staff, the brother, unlock-only, household staff and a family-office case; AI agents never count as employees |

## Run it

```
python3 synthetic_year.py                       # writes out/ledger-<scenario>.csv
python3 synthetic_year.py --check               # proves reproducible and labelled
python3 rehearsal_run.py --selftest             # tax figures, SK cases, rename invariance
python3 rehearsal_run.py --json out/results.json --record ../loop/score-ledger.csv
```

`rehearsal_run.py` needs rdflib and pyshacl (for `decide_spend.py`). If the spend checks cannot run, every flow they grade is Insufficient: it fails closed.

## Rules the runner keeps

- A missing benchmark or fee stops the run. Nothing defaults to zero.
- Arm A deducts no business-shaped line (spec, Arm A). B-ops is the management company carrying lines whose evidence the ledger shows. The structure is credited only with what it adds beyond B-ops.
- A flow with no grading case is Insufficient, never Allow.
- Structure checks read facts, never names. Renaming every entity changes no verdict (selftest).
- `--mix` reshapes counts per domain from a private file. Never commit one, and never commit output made with one.
