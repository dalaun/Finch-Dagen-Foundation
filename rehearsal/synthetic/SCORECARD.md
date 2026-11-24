# Goal scorecard

**SYNTHETIC.** Nothing here is real money, and none of it is legal or tax advice. The scorecard is a finish line the relay can check, not a target to tune toward. No engine number, stack fee or legacy weight is ever changed to make a criterion pass. Today the expected result is that few or none pass.

## The seven criteria

**SC1 steward-non-grantor.** The founder can stay a trustee of the Family Trust, and the trust still counts as its own taxpayer, not as the founder's own pocket. This passes when at least one version of the structure names the founder as a trustee, the grantor-trust check (`grantor_check.py`) calls it non-grantor and settled, and the structure's own flag says it is not a grantor trust.

**SC2 no-open-disqualifier.** For each version that passes SC1, no grantor-trust rule fails or is left uncertain, and every question that version's design route says to ask a lawyer has an entry in `counsel-queue.md` with a working assumption, so the work does not wait on an answer.

**SC3 beats-status-quo.** In at least one scenario where the asset earns income, a version that passes SC1 comes out at least even against the plain operating setup (its structure value is zero or more) and ahead of today's setup (its score versus A is above zero).

**SC4 asset-sized.** `NEXT-MOVES.md` has a move for route step B1 (what asset, how big) and one for B2 (which kinds of asset fit). Each is either closed or carries a `Working assumption:` line. A move names its step with a line such as `- Step: B1`.

**SC5 asset-to-program.** In a scenario that passes SC3, the passing version produces program output above zero, and that output comes from the asset's income reaching the Foundation (the results mark it `program_source: asset_income`). `benchmarks-tax.json` must also cite the 5 percent minimum distribution rule (IRC 4942) with its web address.

**SC6 checks-clear.** The passing version has no red structure check (S-check). Every amber one is named in the list below, along with the document that would clear it.

**SC7 nothing-blocks.** Every open move in `NEXT-MOVES.md` has a `Working assumption:` line and an entry in `counsel-queue.md` (found by the move's `Key:`), so no open question stops the loop.

## How to run it

From the `rehearsal/synthetic` folder:

1. Write the engine's results: `python3 rehearsal_run.py --json out/results.json` (run `synthetic_year.py` first if the ledgers are missing).
2. Score: `python3 scorecard.py --results out/results.json`. It prints `PASS` or `FAIL` for each criterion with a reason, then `Scorecard: <n> of 7 pass`. It always exits 0.
3. To make a script stop unless everything passes: add `--all-green` (exit 1 unless all seven pass).
4. Check the scorecard's own logic: `python3 scorecard.py --selftest`. This also runs inside `rehearsal_run.py --selftest`.

A missing input file fails the criteria that need it.

## Documents that would clear it

Each amber check of the passing version goes here as a list line that names the check and the document, for example `- S5: signed trust deed`. For now:

- S2: "a decision log showing the trustee applying the instrument, including at least one request declined or modified"
- S3: (definition names no document)
- S4: "trustee minutes"
- S7: "depreciation schedules of every entity"
- S9: "the contract and invoice" (whose name and taxpayer number are on them)
- S13: "exemption letter or filed Form 1023"
- S14: "Forms 3520 and 3520-A filed"
- S15: "the founder's return and the receiving entity's return" (how each transfer is characterized on both)
- S16: (definition names no document)
