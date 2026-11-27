# Mutation guard: every check must prove it can fail

A check that stays green on a broken input catches nothing. Think of a smoke
detector's test button: pressing it proves the alarm can sound. This guard
presses every check's button on every pull request.

`checks.json` lists every check in this repo and, for each one, at least one
**known-bad case** (a "mutant"): a rule loosened in the check's own code, or a
broken input planted for it. The guard runs each check on a throwaway copy of
the commit, once clean and once per mutant. It goes red when:

| Status | Meaning | What to do |
|---|---|---|
| SURVIVED | the check stayed green on its known-bad case | add the test case the check is missing |
| CRASHED | the check went red only because the mutant broke Python | rewrite the mutant so it loosens a rule |
| STALE | the text a mutant edits is gone | update the mutant to the check's new code |
| BASELINE | the check is red on the clean commit | fix the check first |
| NOT WIRED | no pull-request workflow runs the check | add a step to a workflow |
| UNLISTED | a file looks like a check but has no entry | add an entry, or exempt it with a reason |
| KILLED | a gap marked `pending` is now caught | drop `pending` so it stays closed |

```
python3 .github/mutation/mutation_guard.py --list        inventory: in CI? how many known-bad cases?
python3 .github/mutation/mutation_guard.py --static      wiring and listing only (seconds)
python3 .github/mutation/mutation_guard.py --only ID     one check
python3 .github/mutation/mutation_guard.py               everything (CI runs this)
python3 .github/mutation/mutation_guard.py --selftest    the guard's own known-bad cases
```

## Adding a check

Add an entry to `checks.json` with its `run` command (exactly as the workflow
runs it), its `source` files, and at least one mutant with a plain-words `why`:

```json
{"id": "my-check", "source": ["my_check.py"], "run": "python3 my_check.py",
 "mutants": [{"id": "limit-loosened", "why": "a spend over the limit must be blocked",
              "file": "my_check.py", "find": "amount > limit", "replace": "amount > limit * 10"}]}
```

Mutant kinds: `find`/`replace` (exactly one copy, or `count`), `write` (a new
file), `append`, `delete`, or `edits` (several, for a move between files).
`expect` is text the red output must contain, so the check fails for the right
reason. `track: true` stages the change in git, for checks that read only
tracked files. `wired_via` names the check whose CI step runs this one.
`requires` lists files that must exist (an entry waits until they merge).
`pending` marks a known gap and names the fix; it does not count as coverage.

## Reuse

`mutation_guard.py` is the same file in every repo (standard library only);
only `checks.json` differs. It is written to become a skill or playbook: copy
the file, write the manifest, add the workflow step.

Not a required check: whether to require it is the owner's setting.
