# Two lanes into main

**Agent lane** (merges itself): a pull request whose every file has no owner in [../CODEOWNERS](../CODEOWNERS). Today that is the rehearsal loop's own work: `rehearsal/loop/BACKLOG.md`, `rehearsal/loop/score-ledger.csv` and `rehearsal/synthetic/` (the seeded synthetic year, its public benchmarks and the engine), except the answer-key facts.

**Dalaun's lane** (waits for him): every other file. That includes every check (validators, `tests/`, the pinned rehearsal checks, the lane guard), `rehearsal/loop/GOAL.md`, the ontology and shapes, `.github/` (workflows, CODEOWNERS), docs, and anything about real entities or trust documents. A new file anywhere is his lane until CODEOWNERS says otherwise.

## How a pull request moves

1. An agent opens a ready (not draft) pull request from a branch of this repository.
2. **Lane guard** (`lane-guard`, run from main by `pull_request_target`) reads the file list. Agent lane: it turns on auto-merge. Dalaun's lane: it turns auto-merge off and fails, with the reason.
3. **Keystone check** (`keystone`) runs every check on the pull request, including the pinned rehearsal checks and the ledger check.
4. **Verifier pass** (`Verifier pass`): an agent that did not write the pull request reviews the diff, reruns the checks, and records a pass on the exact head commit (see "The verifier" below). Any new push leaves the new head with no pass.
5. When all three are green, GitHub merges it (as github-actions). If any is red, missing or still running, nothing merges.
6. A Dalaun's-lane pull request shows a red lane guard on purpose. He reviews it and merges with his bypass, as before.

## The verifier

Green checks and a bot review are not a verdict (Lauren Tan's rule, from the note in his 00 Inbox). The pass has to come from an agent that did not write the code, and it has to name the commit being merged.

- **Who:** a login in [verifiers](verifiers) (his lane) that is not the pull request's author and did not author or commit any of its commits. Copilot and other review bots never count, even if listed.
- **How:** with its own badge token, after reading the whole diff and rerunning the checks, the verifier runs `python3 .github/lane/verifier_pass.py --post --pr N --sha <head sha it reviewed> --as <its login> --note "<one line>"`. The script refuses if the head moved, the lane guard has not passed, or the verifier wrote any of it. It records a commit status `Verifier pass` naming the commit.
- **Why a commit status:** it belongs to one commit and has one current value, so a new push resets it, and an old red result can't block a later pass (the vault's PR 41 lesson about check reruns).
- **After the fact:** [lane-audit](../workflows/lane-audit.yml) runs daily (a github-actions merge starts no push workflow) and goes red if any merge not made by Dalaun lacked a valid pass. Red means: open a revert pull request for him.
- **Who verifies whom:** the foundation badge (`dalaun-finchdagen-claude[bot]`) writes the rehearsal loop's pull requests, so Grokbot's or Muse's badge verifies them. One cheap non-author pass is enough.

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
2. **Settings → Rules → Rulesets → main: owner merges:** untick **Restrict updates**; tick **Require status checks to pass** and add `lane-guard`, `keystone` and `Verifier pass`. Keep the Repository admin bypass.
3. Install the verifier's badge (Grokbot's or Muse's) on this repository with **Commit statuses: read and write**, if it isn't already.

Undo: reverse either step. With auto-merge off, nothing merges itself and every pull request waits for him again.
