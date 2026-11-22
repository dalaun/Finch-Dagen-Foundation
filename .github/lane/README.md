# Two lanes into main

**Agent lane** (merges itself): a pull request whose every file has no owner in [../CODEOWNERS](../CODEOWNERS). Today that is the rehearsal loop's own work: `rehearsal/loop/BACKLOG.md`, `rehearsal/loop/score-ledger.csv` and `rehearsal/synthetic/` (the seeded synthetic year, its public benchmarks and the engine), except the answer-key facts.

**Dalaun's lane** (waits for him): every other file. That includes every check (validators, `tests/`, the pinned rehearsal checks, the lane guard), `rehearsal/loop/GOAL.md`, the ontology and shapes, `.github/` (workflows, CODEOWNERS), docs, and anything about real entities or trust documents. A new file anywhere is his lane until CODEOWNERS says otherwise.

## How a pull request moves

1. An agent opens a ready (not draft) pull request from a branch of this repository.
2. **Lane guard** (`lane-guard`, run from main by `pull_request_target`) reads the file list. Agent lane: it turns on auto-merge. Dalaun's lane: it turns auto-merge off and fails, with the reason.
3. **Keystone check** (`keystone`) runs every check on the pull request, including the pinned rehearsal checks and the ledger check.
4. When both required checks are green, GitHub merges it (as github-actions). If either is red or still running, nothing merges.
5. A Dalaun's-lane pull request shows a red lane guard on purpose. He reviews it and merges with his bypass, as before.

## Why the line sits where it does

An agent that could edit its own checks could make anything pass. So the agent lane holds the work and Dalaun's lane holds everything that judges the work:

- **The pinned checks** (`tests/rehearsal/pinned_checks.py`) are the floor: 2026 tax figures from Rev. Proc. 2025-32, the structure answer key SK1-SK14, name invariance, and w = 0. The engine's own selftest can grow; the floor moves only with his review.
- **The ledger check** (`tests/rehearsal/check_ledger.py`): the newest ledger rows must be exactly what this commit's engine computes, so a score cannot be typed in. The lane guard adds that earlier rows are never rewritten.
- **The guard runs from main**, so a pull request cannot change the rules it is judged by.
- **Forks never ride the lane**: this repository is public, so a stranger's pull request always waits for Dalaun.

## What it cannot stop

Agents push as Dalaun's GitHub account, which is an admin, so GitHub cannot tell an agent from him. The lane removes the need for an agent to merge; it cannot take away an admin's power to bypass. The agents' own rules (never merge, approve, bypass or push to main) still carry that part. An engine change could also game a check by special-casing its inputs; the daily verifier pass and his review of the checks are the answer to that. Giving agents their own GitHub identity, without admin rights, would close the first gap.

## The settings that switch it on (his, once)

1. **Settings → General → Pull Requests:** tick **Allow auto-merge**.
2. **Settings → Rules → Rulesets → main: owner merges:** untick **Restrict updates**; tick **Require status checks to pass** and add `lane-guard` and `keystone` (source GitHub Actions). Keep the Repository admin bypass.

Undo: reverse either step. With auto-merge off, nothing merges itself and every pull request waits for him again.
