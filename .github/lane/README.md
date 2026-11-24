# Two lanes into main

**The rulebook:** [approvals](approvals) (his lane) is the one file that says who approves what: which paths are the agent lane, which are his, which files may only gain lines, and whether each rule is enforced or only observed. [../CODEOWNERS](../CODEOWNERS) shows the same lane to GitHub; the guard checks the two match.

**Agent lane** (merges itself): a pull request whose every file is an agent path in [approvals](approvals). Today that is the rehearsal loop's own work: `rehearsal/loop/BACKLOG.md`, `rehearsal/loop/score-ledger.csv` and `rehearsal/synthetic/` (the seeded synthetic year, its public benchmarks and the engine), except the answer-key facts.

**Dalaun's lane** (waits for him): every other file. That includes every check (validators, `tests/`, the pinned rehearsal checks, the lane guard), `rehearsal/loop/GOAL.md`, the ontology and shapes, `.github/` (workflows, CODEOWNERS), docs, and anything about real entities or trust documents. A new file anywhere is his lane until CODEOWNERS says otherwise.

## How a pull request moves

1. An agent opens a ready (not draft) pull request from a branch of this repository.
2. **Lane guard** (`lane-guard`, run from main by `pull_request_target`) reads the file list. Agent lane: it turns on auto-merge. Dalaun's lane: it turns auto-merge off and fails, with the reason.
3. **Keystone check** (`keystone`) runs every check on the pull request, including the pinned rehearsal checks and the ledger check.
4. **Verifier pass** (`Verifier pass`): an agent that did not write the pull request reruns the checks at the exact head commit, runs the rehearsal end to end, reads the diff, and records PASS, PASS+NOTES or FAIL on that commit (see "The verifier" below). Any new push leaves the new head with no verdict.
5. When all three are green, GitHub merges it (as github-actions). If any is red, missing or still running, nothing merges.
6. A Dalaun's-lane pull request shows a red lane guard on purpose. He reviews it and merges with his bypass, as before.

## The verifier

Green checks and a bot review are not a verdict (Lauren Tan's rule, from the note in his 00 Inbox, quoting her pstack playbook). The verdict has to come from an agent that did not write the code, and it has to name the commit being merged.

- **Verdicts:** `PASS`, `PASS+NOTES` (mergeable; the notes don't block) or `FAIL`. Only three things fail a pull request: a result a user of the rehearsal would get wrong, a failed check, or a shipped doc that is wrong. Anything else is a note.
- **What the verifier does, in this order:** (1) reruns every check at the head commit in a fresh checkout, (2) runs the rehearsal end to end the way he would use it and checks the result makes sense, (3) reads the diff for anything that games a check. Most of the time goes to (1) and (2), which are code; (3) is short. Her own finding: adversarial reviews are "mostly a waste of tokens", so a mistake a verifier keeps catching by reading should become a check.
- **Who:** the verdict is posted by the verifier app, `dalaun-finchdagen-verifier[bot]`, the only login in [verifiers](verifiers) (his lane). The agent that did the verifying is whoever dispatched the run; the script refuses if that account wrote or committed any of the pull request, and the verdict comment names it. No badge that writes pull requests is listed, because a listed login could post the status directly and skip the script's checks (the selftest fails if one is). Copilot and other review bots never count, even if listed.
- **How it is recorded:** the verifier dispatches [verifier-pass](../workflows/verifier-pass.yml) with its verdict and report. That workflow, from main, posts the commit status `Verifier pass` (`<VERDICT> <commit> by <badge>: <one line>`) under the verifier badge, and the report as a comment. The script refuses if the head moved, the badge or whoever dispatched it wrote any of the pull request, the report doesn't name the full commit, or (for a pass) `lane-guard` and `keystone` aren't green on that commit.
- **Why a commit status:** it belongs to one commit and has one current value, so a new push resets it, and an old red result can't block a later pass (the vault's PR 41 lesson about check reruns).
- **After the fact:** [lane-audit](../workflows/lane-audit.yml) runs daily (a github-actions merge starts no push workflow) and goes red if any merge not made by Dalaun lacked a valid pass. Red means: open a revert pull request for him.
- **Who verifies whom:** the foundation badge (`dalaun-finchdagen-claude[bot]`) writes the rehearsal loop's pull requests; the verifier app (`dalaun-finchdagen-verifier`, a different GitHub App) only posts verdicts and never writes code. One cheap pass per head is enough; a fresh full run only for new behavior.

## Observe first, then enforce

A new rule goes into [approvals](approvals) as `observe`. The lane guard works it out on every pull request and only reports: a line in the step summary, a notice on the check, and one comment on the pull request ("Lane guard, observe-only") when the answer would differ from today's. Nothing waits on an observe rule. Once the comments show the rule catches what it should and nothing it shouldn't, Dalaun switches it on: `observe` becomes `enforce` in approvals and the same path goes into CODEOWNERS, in one pull request that he merges.

Observed since 2026-11-24: the goal scorecard (`scorecard.py`) and the grantor check (`grantor_check.py`) to his lane, and `SCORECARD.md` and `grantor-routes.json` to grows-only. Replayed on the merged pull requests, they would have sent #26, #39 and #47 to him.

## The stop word

A line that is only `@finchdagen-claude stop`, in Dalaun's comment on a pull request or on the issue it closes, halts that pull request: the lane guard puts it in his lane on its next run (every push), the verifier refuses a pass, and the badge answers "Stopped" ([CLAUDE.md](../../CLAUDE.md)). `@finchdagen-claude go` lifts it; his newest word wins; nobody else's counts. Limit: a pull request that already holds a pass merges seconds after its last check, so a stop after that is too late for it (use the Revert button). Cancelling a run that is already working, and turning auto-merge off the moment the stop is written, need a workflow that listens to comments, which only Dalaun can add (the badge cannot edit workflows, by design).

## Ranked findings and the fix log

A verifier report may rank each finding on its own line: `Important:` (blocks; the three FAIL reasons), `Nit:` (worth doing, doesn't block) or `Pre-existing:` (already wrong on main). The verifier script refuses a verdict that disagrees with the ranks (FAIL with no Important, a pass with an Important, PASS with a Nit). The report comment shows the ranked findings first, then the report, then a fix log: every commit, who wrote it and how to undo it. The badge also writes each fix commit with What changed, Why and Rollback lines ([CLAUDE.md](../../CLAUDE.md)).

## Why the line sits where it does

An agent that could edit its own checks could make anything pass. So the agent lane holds the work and Dalaun's lane holds everything that judges the work:

- **Checks inside agent files only grow:** `selftest()` in `rehearsal_run.py` and `main()` (with `--check`) in `synthetic_year.py` are check code inside the agent lane. The lane guard lets an agent add lines there, but changing or removing any existing line is his lane. Adding a stricter check rides the lane; loosening one waits for him.
- **The pinned checks** (`tests/rehearsal/pinned_checks.py`) are the floor: 2026 tax figures from Rev. Proc. 2025-32, the structure answer key SK1-SK14, name invariance, and w = 0. The engine's own selftest can grow; the floor moves only with his review.
- **The ledger check** (`tests/rehearsal/check_ledger.py`): the newest ledger rows must be exactly what this commit's engine computes, so a score cannot be typed in. The lane guard adds that earlier rows are never rewritten.
- **The guard runs from main**, so a pull request cannot change the rules it is judged by.
- **Forks never ride the lane**: this repository is public, so a stranger's pull request always waits for Dalaun.

## What it cannot stop

Agent sessions that push as Dalaun's GitHub account are admins, so GitHub cannot tell them from him, and the audit trusts any merge made as `dalaun`. The foundation badge (PR 20) closes that for the daily loop: its pull requests carry the badge's name and it cannot bypass. Claude chat sessions still use his account until they move to a badge too. An engine change could also game a check by special-casing its inputs; that is what the verifier's read of the diff is for. "Only grows" is a text check: a verifier still has to read what a new line does.

## The settings that switch it on (his, once)

1. **Settings → General → Pull Requests:** tick **Allow auto-merge**.
2. **Settings → Rules → Rulesets → main: owner merges:** untick **Restrict updates**; tick **Require status checks to pass** and add `lane-guard`, `keystone` and `Verifier pass`. For `Verifier pass`, set its source to the `dalaun-finchdagen-verifier` app, so a status from any other login can't satisfy it. Keep the Repository admin bypass.
3. **Settings → Environments → New environment `verifier`:** limit deployment branches to `main`; add variable `VERIFIER_APP_ID` and secret `VERIFIER_APP_KEY` for the verifier app `dalaun-finchdagen-verifier` (not the foundation badge), installed on this repository only, with **Commit statuses**, **Pull requests** and **Issues: read and write** and nothing else. The report comment goes through the issues API, and every report comment got HTTP 403 (runs 11 to 15, 2026-11-24) while the installation held Issues but, as far as we know, not Pull requests; the script now prints the permission GitHub asks for, so the next failure names its own cause. After changing a permission, accept the update on the app's installation page, or it doesn't take effect. Its bot login, `dalaun-finchdagen-verifier[bot]`, is the one line in [verifiers](verifiers).

Undo: reverse either step. With auto-merge off, nothing merges itself and every pull request waits for him again.
