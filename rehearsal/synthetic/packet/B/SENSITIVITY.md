# Packet B: how the result moves with the asset's size

Research for counsel review, not legal advice.

Each row is an engine output on the synthetic year (run 2026-11-25). The scenarios are the base `asset_sized` (150,000 a year of asset income) and `asset_sized_pipeline` (350,000), each at 0.75, 1.0 and 1.5 times that income, set in `rehearsal/synthetic/scenarios.json` with `sensitivity_of`. The sizes are fixed multiples, never picked to make arm B win. The asset income is an ASSUMPTION (counsel-queue.md Q11, Q17); no market yield was read for it. "B minus A" is the engine's score of the version against doing nothing, in dollars a year: positive means the structure beats doing nothing.

Versions: `flat` (the founder as trustee, grantor trust), `steward_r2` (independent distribution trustee, non-grantor), `steward_r2_pipeline` (the same with 10 percent of the trust's distribution to the Foundation).

| scenario id | version | asset net income | B minus A | B minus A, stewarded |
|---|---|---|---|---|
| asset_sized_x075 | flat | 112,500 | -4,531 | -4,531 |
| asset_sized_x075 | steward_r2 | 112,500 | -2,355 | -2,355 |
| asset_sized_x075 | steward_r2_pipeline | 112,500 | -10,573 | +677 |
| asset_sized_x100 | flat | 150,000 | -4,275 | -4,275 |
| asset_sized_x100 | steward_r2 | 150,000 | +13 | +13 |
| asset_sized_x100 | steward_r2_pipeline | 150,000 | -10,944 | +4,056 |
| asset_sized_x150 | flat | 225,000 | -4,167 | -4,167 |
| asset_sized_x150 | steward_r2 | 225,000 | +6,133 | +6,133 |
| asset_sized_x150 | steward_r2_pipeline | 225,000 | -9,853 | +12,647 |
| asset_sized_pipeline_x075 | flat | 262,500 | -4,167 | -4,167 |
| asset_sized_pipeline_x075 | steward_r2 | 262,500 | +9,609 | +9,609 |
| asset_sized_pipeline_x075 | steward_r2_pipeline | 262,500 | -9,042 | +17,208 |
| asset_sized_pipeline_x100 | flat | 350,000 | -4,167 | -4,167 |
| asset_sized_pipeline_x100 | steward_r2 | 350,000 | +17,205 | +17,205 |
| asset_sized_pipeline_x100 | steward_r2_pipeline | 350,000 | -7,150 | +27,850 |
| asset_sized_pipeline_x150 | flat | 525,000 | -4,167 | -4,167 |
| asset_sized_pipeline_x150 | steward_r2 | 525,000 | +17,248 | +17,248 |
| asset_sized_pipeline_x150 | steward_r2_pipeline | 525,000 | -14,279 | +38,221 |

"B minus A, stewarded" adds back the money the family steward still directs at the Foundation (`stewarded_vs_A` = the family-only score plus `to_foundation`). It is a view, never a goal: no check or move is tuned to raise it, and the family-only column is unchanged. It differs from the first only for the Foundation share version.

What the table shows: `steward_r2` is about even at 150,000 a year of asset income (+13) and positive above it; the Foundation share version stays negative on the family-only score at every size up to 525,000, and turns positive only on the stewarded view; `flat` stays negative at every size. After the founder NII fix (PR 94) the base break-evens are 170,300 for route R2 with an unrelated individual and none up to 1,000,000 for the 10 percent Foundation share; MEMO.md now carries the same figures (backlog item R15, 2026-11-25).
