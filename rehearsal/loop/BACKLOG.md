# Rehearsal loop backlog

[Back to the goal](GOAL.md)

The daily loop takes the **top open item**, works it, and opens one PR: ready if every file is in the agent lane (it then merges itself once checks pass), draft otherwise. An item is done only when its done test passes. Move a finished item to the Done list with the date and PR. Add new items at the bottom of their section. Keep this file SYNTHETIC: no real amounts, names or accounts.

## Open, in order

2. **QBI-RENTAL.** The rental's Schedule E income gets no 199A deduction in the engine. Done test: Rev. Proc. 2019-38 safe harbor (250 hours, separate books) is read; the engine gives the rental QBI only when a scenario says the safe-harbor facts are present; a selftest case shows both ways.
3. **KIDDIE-TAX.** Add a scenario variant where a beneficiary is under the 152(c)(3) age limits. Done test: 152(c)(3) and 1(g) text read and cited; the variant taxes that beneficiary's unearned income at the parent's rate; the report shows the income-splitting result vanish.
4. **170P.** Confirm from the statute text whether the new non-itemizer deduction (170(p), 2026 on) covers gifts to a private non-operating foundation. Done test: the text is quoted with its URL in benchmarks-tax.json; the engine applies it only if the text says so.
5. **674C-SPOUSE.** Read 674(c) and 672(c) in full for how a spouse trustee counts. Done test: the rule's exact sentence is quoted in benchmarks-tax.json grantor_trust and the trustee_related_or_subordinate fact cites it.
6. **CE-SPREAD.** The year-level spread on each spending line is an assumption. Done test: the BLS CE standard errors (XLSX tables) are read for the Chicago area; each line's `year_cv` cites one or is marked ASSUMPTION with a reason.
7. **OWNED-SPLIT.** The 40/35/10/15 split of owned-dwelling cost is an assumption. Done test: replaced with BLS CE owned-dwelling subcategories (mortgage interest, property taxes, maintenance, insurance) with the table URL.
8. **REAL-PROPTAX.** Property tax uses the Cook County average rate. Done test: the rate is from a Cook County Treasurer or Clerk source for the current tax year, with URL and as-of date.
9. **FEE-QUOTES.** Every fee in stack.json is a placeholder except two state fees. Done test: each fee has a published price page or a quote range with URL and date, or stays marked PLACEHOLDER with why.
10. **IL-EXEMPTION.** Illinois treatment of a foundation and of a grantor trust is assumed to follow federal. Done test: Illinois statute or Department of Revenue page cited for each.
11. **280E-CHECK.** Confirm the transport company has no line the engine routes that a special disallowance blocks. Done test: each routed domain lists its blocking sections checked, with citations.
12. **REALISM.** Synthetic-data realism checks. Done test: a script compares each scenario's domain totals to the CE table it came from and fails if any line drifts more than 10 percent from its benchmark after scaling; it runs in CI.
13. **REGISTER-GAPS.** Instruments in 01-instrument-register.md marked unverified. Done test: each one has its primary-source quote and URL, or is moved to a "could not verify" list.
14. **COUNSEL-QS.** Questions for counsel that the runs raised. Done test: each is added to 05-questions-for-attorney-and-cpa.md in plain words, in roles, with the scenario that raised it. Start with: whether an unrelated individual trustee at a nominal fee is realistic and what duties it carries; whether the Family Trust holding an LLC that pays the founder wages keeps S5 and S12 passing.
15. **HEALTH-SWAP.** Leaving W-2 pay means replacing employer family health coverage. Done test: a scenario variant prices individual-market family coverage from a cited Illinois or federal marketplace source, applies the self-employed health deduction (162(l)) where it fits, and the transition report shows it.
16. **UTILITY-PASS.** Utilities charged to tenants are not modeled. Done test: scenarios.json can mark a utility as tenant-paid per unit; for a unit under a housing voucher, the engine lowers the approved contract rent by the utility allowance instead of adding the charge (the HUD rule that gross rent, contract rent plus utility allowance, is what the payment standard caps, read and cited); a selftest case shows both kinds of unit.

## Done

- **PRETAX** (2026-11-22, draft PR on branch claude/rehearsal-loop-20261122). scenarios.json states pre-tax payroll by section; the engine takes section 125 amounts out of income-tax and FICA wages and 401(k) deferrals out of income-tax wages only, with the rule text cited in benchmarks-tax.json payroll_pretax. Found on the way: the BLS CE retirement line already includes the employee's Social Security tax (ce_glossary), so the money view counted FICA twice; the runner now treats only the rest of that line as saving. Structure values did not move; break-even with an unrelated individual trustee rose about 3 percent because the founder's taxable wages fell.
- **NIIT** (2026-11-23, draft PR on branch claude/rehearsal-loop-20261123). IRC 1411 read and cited in benchmarks-tax.json `niit`; the engine applies 3.8% to the founder's rental and passive-business income above 200,000 MAGI and to trust retained income above the top trust bracket start, with selftest cases. Passive status of the rental and the bought business is an ASSUMPTION. Break-even with an unrelated individual trustee fell about 16 percent (base 178,500 to 149,500); structure values did not move. Open question for counsel: material participation or real-estate-professional status.
