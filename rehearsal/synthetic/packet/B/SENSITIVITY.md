# Packet B: how the result moves with the asset's size

Research for counsel review, not legal advice.

Each row is an engine output on the synthetic year (run 2026-11-25). The scenarios are the base `asset_sized` (150,000 a year of asset income) and `asset_sized_pipeline` (350,000), each at 0.75, 1.0 and 1.5 times that income, set in `rehearsal/synthetic/scenarios.json` with `sensitivity_of`. The sizes are fixed multiples, never picked to make arm B win. The asset income is an ASSUMPTION (counsel-queue.md Q11, Q17); no market yield was read for it. "B minus A" is the engine's score of the version against doing nothing, in dollars a year: positive means the structure beats doing nothing.

Versions: `flat` (the founder as trustee, grantor trust), `steward_r2` (independent distribution trustee, non-grantor), `steward_r2_pipeline` (the same with 10 percent of the trust's distribution to the Foundation).

| scenario id | version | asset net income | B minus A |
|---|---|---|---|
| asset_sized_x075 | flat | 112,500 | -4,377 |
| asset_sized_x075 | steward_r2 | 112,500 | -2,202 |
| asset_sized_x075 | steward_r2_pipeline | 112,500 | -10,420 |
| asset_sized_x100 | flat | 150,000 | -4,089 |
| asset_sized_x100 | steward_r2 | 150,000 | +1,592 |
| asset_sized_x100 | steward_r2_pipeline | 150,000 | -9,365 |
| asset_sized_x150 | flat | 225,000 | -3,981 |
| asset_sized_x150 | steward_r2 | 225,000 | +10,562 |
| asset_sized_x150 | steward_r2_pipeline | 225,000 | -5,424 |
| asset_sized_pipeline_x075 | flat | 262,500 | -3,981 |
| asset_sized_pipeline_x075 | steward_r2 | 262,500 | +15,462 |
| asset_sized_pipeline_x075 | steward_r2_pipeline | 262,500 | -3,188 |
| asset_sized_pipeline_x100 | flat | 350,000 | -3,981 |
| asset_sized_pipeline_x100 | steward_r2 | 350,000 | +26,384 |
| asset_sized_pipeline_x100 | steward_r2_pipeline | 350,000 | +2,029 |
| asset_sized_pipeline_x150 | flat | 525,000 | -3,981 |
| asset_sized_pipeline_x150 | steward_r2 | 525,000 | +33,076 |
| asset_sized_pipeline_x150 | steward_r2_pipeline | 525,000 | +1,550 |

What the table shows: the route R2 versions turn positive only once asset income passes about 150,000 a year, and the Foundation share version only once it passes about 350,000. `flat` stays negative at every size. That matches the break-evens in MEMO.md (149,500 and 343,600).
