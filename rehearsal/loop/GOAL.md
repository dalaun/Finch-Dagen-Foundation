# Rehearsal loop: goal and score

[Back to the rehearsal overview](../README.md)

**SYNTHETIC.** Every number the loop scores comes from the seeded year in [../synthetic](../synthetic/README.md), built from public benchmarks. None of it is the founder's money. Design and education, not legal or tax advice.

## The goal, in one line

Find the smallest real, income-producing asset that makes the structure pay for itself, while every structure check passes on documents, not on design.

## The score

The loop keeps two numbers per scenario and stack version, and writes both to [score-ledger.csv](score-ledger.csv) with the date so runs chain.

1. **Structure gap** (dollars a year, lower is better). What the trust and foundation layers cost beyond what ordinary business bookkeeping already earns. It is `max(0, −structure value)`, where structure value is arm B for that version minus B-ops (03-ab-rehearsal-spec.md, Objective, with w = 0). B-ops is the management company carrying documented business lines; it needs no trust, so it is not credited to the structure.
2. **Break-even asset income** (dollars a year, lower is better, "none" is worst). The extra yearly net income from an asset held in the stack at which the structure gap reaches zero. It is computed three ways: him as trustee (grantor trust), an independent professional trustee, and an independent unrelated individual trustee.
3. **Checks passing** (out of 17, S1 to S17 in 07-structure-integrity-checks.md). Counted only on facts. A null fact is amber. A red check takes the version out of the score.

A run **moves the score** when any structure gap or break-even changes by more than 1 percent, or a check count changes. Anything else is a clean run.

## First scores (2026-11-22)

| Scenario | Version | Structure gap / yr | Checks pass | Break-even, him as trustee | Break-even, professional trustee | Break-even, unrelated individual trustee |
|---|---|---|---|---|---|---|
| base | today | 6,015 | 3 | none | none | 173,100 |
| base | flat | 4,815 | 10 | none | none | 173,100 |
| lean | flat | 4,815 | 10 | none | none | 168,800 |
| asset_rental | flat | 5,615 | 10 | none | none | 159,400 |
| asset_business | flat | 5,615 | 10 | none | none | 198,000 |

What the numbers say, in plain words:

- **With him as trustee the layers never pay on money.** A trust whose income he can direct is his grantor trust (IRC 674(a), 672(c)), so its income is taxed to him exactly as in arm A. The layers only add fees. No asset size changes that; their value there is control, continuity and the asset-to-program pipeline, which w = 0 does not count.
- **The money case for the trust needs a trustee who is not him** and not related or subordinate to him (674(c)), and adult beneficiaries in lower brackets (a child is taxed at the parent's rate under 1(g)). Even then it needs about 160,000 to 200,000 a year of extra asset income, and a professional trustee at 1 percent of assets never breaks even.
- **The flat version is the better structure today**: it clears 7 more checks than today's stack and costs 1,200 a year less, by dropping the business trust.
- **The real gain is B-ops**: documenting business lines through the management company is worth about 550 to 1,100 a year in these years and needs no trust.

Every fee is a placeholder until a professional quotes it (backlog FEE-QUOTES), so the break-evens will move.

## What the loop is not allowed to do

Tune anything to make arm B win. Change w (his setting). Use real amounts, merchants, names or accounts in this repository. Merge, approve or push to main.
