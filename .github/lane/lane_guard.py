#!/usr/bin/env python3
"""Lane guard: decide whether a pull request stays in the agent lane.

The agent lane is the set of paths in .github/CODEOWNERS that have no owner.
A pull request is in the agent lane only when ALL of these hold:

  1. every file it adds, changes, deletes or renames (old and new name) has no
     owner in CODEOWNERS (the last matching line wins, as on GitHub);
  2. it comes from a branch of this repository, not a fork;
  3. it is not a draft;
  4. rehearsal/loop/score-ledger.csv, if touched, only gains rows at the end
     (history is never rewritten) and is not deleted;
  5. the check code inside agent-lane files (CHECK_BLOCKS) only gains lines:
     every line it had is still there, so an agent can add a check but not
     loosen or remove one.

Anything else is Dalaun's lane. The guard fails closed: an unknown pattern,
an unreadable file list or an API error is Dalaun's lane.

It never runs the pull request's code. It reads the file list and, for the
ledger, the two versions of one CSV file as text, through the GitHub API.
CODEOWNERS and this script come from the base branch (pull_request_target),
so a pull request cannot change the rules it is judged by.

  python3 lane_guard.py              in GitHub Actions (reads the event)
  python3 lane_guard.py --selftest   the guard's own cases

Standard library only.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from fnmatch import fnmatchcase
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = "rehearsal/loop/score-ledger.csv"
# Check code that lives inside agent-lane files. Its lines may only grow: an
# agent may add a check, but changing or removing an existing line of it is
# Dalaun's lane (loosening a check waits for him).
CHECK_BLOCKS = {
    "rehearsal/synthetic/rehearsal_run.py": "selftest",
    "rehearsal/synthetic/synthetic_year.py": "main",
}


# ------------------------------------------------------------------ CODEOWNERS

def parse_codeowners(text: str) -> list:
    """Return [(pattern, owners)] in file order. Unknown pattern forms raise."""
    rules = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        pat, owners = parts[0], parts[1:]
        if pat != "*" and not pat.startswith("/"):
            raise ValueError(f"CODEOWNERS line {n}: the guard only reads '*' or patterns starting with '/': {pat}")
        if any(c in pat[1:] for c in "*?[]!") and pat != "*":
            raise ValueError(f"CODEOWNERS line {n}: wildcards inside a path are not supported: {pat}")
        rules.append((pat, owners))
    if not rules or rules[0] != ("*", rules[0][1]) or not rules[0][1]:
        raise ValueError("CODEOWNERS must open with '* <owner>' so every unlisted file has an owner")
    return rules


def _matches(pat: str, path: str) -> bool:
    if pat == "*":
        return True
    p = pat[1:]
    if p.endswith("/"):
        return path.startswith(p)
    return path == p or fnmatchcase(path, p)


def owners_of(path: str, rules: list) -> list:
    found = None
    for pat, owners in rules:
        if _matches(pat, path):
            found = owners
    return found if found is not None else ["(no rule)"]


# ------------------------------------------------------------------ decision

def block_lines(text: str, func: str) -> list:
    """The non-blank lines of top-level function `func`, stripped."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith(f"def {func}("):
            inside = True
        elif inside and line and not line[0].isspace() and not line.startswith(("#", ")")):
            break
        if inside and line.strip():
            out.append(line.strip())
    return out


def only_grows(base: str, head: str, func: str) -> bool:
    from collections import Counter
    b, h = Counter(block_lines(base, func)), Counter(block_lines(head, func))
    return bool(b) and not (b - h)


def decide(pr: dict, files: list, rules: list, ledger_versions=None, check_versions=None) -> tuple:
    """Return (lane, reasons). lane is 'agent' or 'owner'.
    check_versions: {path: (base_text, head_text)} for the CHECK_BLOCKS files touched."""
    reasons = []
    check_versions = check_versions or {}
    head_repo = ((pr.get("head") or {}).get("repo") or {}).get("full_name")
    base_repo = ((pr.get("base") or {}).get("repo") or {}).get("full_name")
    if not head_repo or head_repo != base_repo:
        reasons.append(f"comes from another repository ({head_repo or 'unknown'}), so Dalaun reviews it")
    if pr.get("draft"):
        reasons.append("is a draft")
    if not files:
        reasons.append("has no file list (fail closed)")
    for f in files:
        for name in filter(None, (f.get("filename"), f.get("previous_filename"))):
            own = owners_of(name, rules)
            if own:
                reasons.append(f"touches {name} (owned by {' '.join(own)})")
        if f.get("filename") == LEDGER or f.get("previous_filename") == LEDGER:
            if f.get("status") in ("removed", "renamed"):
                reasons.append("deletes or renames the score ledger")
            elif f.get("status") == "modified":
                if ledger_versions is None:
                    reasons.append("could not read the score ledger to check it only grows (fail closed)")
                else:
                    base, head = ledger_versions
                    if not head.startswith(base):
                        reasons.append("rewrites earlier rows of the score ledger (rows may only be added at the end)")
        for path, func in CHECK_BLOCKS.items():
            if path not in (f.get("filename"), f.get("previous_filename")):
                continue
            if f.get("status") in ("removed", "renamed"):
                reasons.append(f"deletes or renames {path}, which holds checks")
            elif f.get("status") == "modified":
                if path not in check_versions:
                    reasons.append(f"could not read {path} to check its checks only grow (fail closed)")
                elif not only_grows(*check_versions[path], func):
                    reasons.append(f"changes or removes an existing line of {func}() in {path} "
                                   "(checks may only be added)")
    return ("owner" if reasons else "agent"), reasons


# ------------------------------------------------------------------ GitHub API

def _get(url: str, token: str, raw: bool = False):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.raw" if raw else "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "lane-guard",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
    return body.decode() if raw else json.loads(body)


def pr_files(repo: str, number: int, token: str) -> list:
    out, page = [], 1
    while True:
        batch = _get(f"https://api.github.com/repos/{repo}/pulls/{number}/files?per_page=100&page={page}", token)
        out += batch
        if len(batch) < 100:
            return out
        page += 1
        if page > 30:  # GitHub lists at most 3000 files; more is fail closed
            raise RuntimeError("more than 3000 files")


def file_at(repo: str, path: str, sha: str, token: str) -> str:
    return _get(f"https://api.github.com/repos/{repo}/contents/{path}?ref={sha}", token, raw=True)


def run_in_actions() -> int:
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    pr = event["pull_request"]
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    try:
        rules = parse_codeowners((ROOT / ".github" / "CODEOWNERS").read_text())
        files = pr_files(repo, pr["number"], token)
        ledger_versions = None
        if any(f.get("filename") == LEDGER and f.get("status") == "modified" for f in files):
            ledger_versions = (file_at(repo, LEDGER, pr["base"]["sha"], token),
                               file_at(repo, LEDGER, pr["head"]["sha"], token))
        check_versions = {}
        for f in files:
            if f.get("filename") in CHECK_BLOCKS and f.get("status") == "modified":
                path = f["filename"]
                check_versions[path] = (file_at(repo, path, pr["base"]["sha"], token),
                                        file_at(repo, path, pr["head"]["sha"], token))
        lane, reasons = decide(pr, files, rules, ledger_versions, check_versions)
    except Exception as e:  # fail closed
        lane, reasons = "owner", [f"the guard could not finish ({type(e).__name__}: {e})"]
    if lane == "agent":
        msg = ("Agent lane: every file is the rehearsal loop's own work. It merges itself once every required "
               "check passes, including a Verifier pass on this exact commit from an agent that did not write it.")
    else:
        msg = "Dalaun's lane: this pull request needs Dalaun. It " + "; it ".join(reasons) + "."
    print(msg)
    with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as fh:
        fh.write(f"lane={lane}\n")
    with open(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull), "a") as fh:
        fh.write(f"### Lane guard\n\n{msg}\n")
    return 0


# ------------------------------------------------------------------ selftest

def selftest() -> int:
    fails = 0

    def ok(cond, msg):
        nonlocal fails
        print(("ok    " if cond else "FAIL  ") + msg)
        fails += not cond

    rules = parse_codeowners((ROOT / ".github" / "CODEOWNERS").read_text())
    same = {"head": {"repo": {"full_name": "o/r"}}, "base": {"repo": {"full_name": "o/r"}}, "draft": False}

    def lane(files, pr=same, lv=None, cv=None):
        return decide(pr, [{"filename": f, "status": "modified"} if isinstance(f, str) else f for f in files],
                      rules, lv, cv)[0]

    ok(lane(["rehearsal/loop/BACKLOG.md"]) == "agent", "backlog only: agent lane")
    ok(lane(["rehearsal/loop/NEXT-MOVES.md", "rehearsal/loop/score-ledger.csv"], lv=("", "")) == "agent",
       "next moves and the ledger: agent lane")
    ok(lane(["rehearsal/loop/NEXT-MOVES.md", "rehearsal/loop/DAILY-RUN.md"]) == "owner",
       "next moves with the run's own instructions: Dalaun's lane")
    rr = "rehearsal/synthetic/rehearsal_run.py"
    base = "def helper():\n    return 1\n\ndef selftest() -> int:\n    ok(a == 1, 'one')\n    ok(b == 2, 'two')\n\ndef main():\n    pass\n"
    grown = base.replace("    ok(b == 2, 'two')\n", "    ok(b == 2, 'two')\n    ok(c == 3, 'three')\n")
    loosened = base.replace("ok(b == 2, 'two')", "ok(True, 'two')")
    dropped = base.replace("    ok(b == 2, 'two')\n", "")
    helper_changed = base.replace("return 1", "return 2")
    ok(lane([rr, "rehearsal/synthetic/benchmarks-tax.json", "rehearsal/loop/BACKLOG.md"],
            cv={rr: (base, grown)}) == "agent", "engine + figures + backlog, a check added: agent lane")
    ok(lane([rr], cv={rr: (base, helper_changed)}) == "agent", "engine change outside the checks: agent lane")
    ok(lane([rr], cv={rr: (base, loosened)}) == "owner", "a check loosened: Dalaun's lane")
    ok(lane([rr], cv={rr: (base, dropped)}) == "owner", "a check removed: Dalaun's lane")
    ok(lane([rr]) == "owner", "engine file unreadable: Dalaun's lane (fail closed)")
    ok(lane([{"filename": rr, "status": "removed"}]) == "owner", "engine file deleted: Dalaun's lane")
    real = (ROOT / rr).read_text()
    ok(len(block_lines(real, "selftest")) > 20, "the real selftest() is found")
    ok(len(block_lines((ROOT / "rehearsal/synthetic/synthetic_year.py").read_text(), "main")) > 5,
       "the real synthetic_year main() is found")
    ok(lane(["rehearsal/synthetic/structure-cases-facts.json"]) == "owner", "answer-key facts: Dalaun's lane")
    ok(lane(["rehearsal/loop/GOAL.md"]) == "owner", "goal file: Dalaun's lane")
    ok(lane(["rehearsal/loop/BACKLOG.md", ".github/workflows/keystone-check.yml"]) == "owner",
       "one workflow file among agent files: Dalaun's lane")
    ok(lane([".github/CODEOWNERS"]) == "owner", "the lane map itself: Dalaun's lane")
    ok(lane([".github/lane/lane_guard.py"]) == "owner", "the guard itself: Dalaun's lane")
    ok(lane(["tests/rehearsal/pinned_checks.py"]) == "owner", "pinned checks: Dalaun's lane")
    ok(lane(["AGENTS.md"]) == "owner", "AGENTS.md: Dalaun's lane")
    ok(lane(["trust-domain-ontology.ttl"]) == "owner", "ontology: Dalaun's lane")
    ok(lane(["new-top-level-file.md"]) == "owner", "a new file anywhere else: Dalaun's lane (default)")
    ok(lane(["rehearsal/synthetic-extra/x.py"]) == "owner", "a look-alike folder name: Dalaun's lane")
    ok(lane([{"filename": "rehearsal/synthetic/x.json", "previous_filename": "rehearsal/loop/GOAL.md",
              "status": "renamed"}]) == "owner", "renaming a Dalaun-lane file into the agent lane: Dalaun's lane")
    ok(lane([]) == "owner", "no file list: Dalaun's lane (fail closed)")
    ok(lane(["rehearsal/loop/BACKLOG.md"], pr={**same, "draft": True}) == "owner", "a draft: Dalaun's lane")
    fork = {**same, "head": {"repo": {"full_name": "stranger/r"}}}
    ok(lane(["rehearsal/loop/BACKLOG.md"], pr=fork) == "owner", "a fork's pull request: Dalaun's lane")
    ok(lane(["rehearsal/loop/score-ledger.csv"], lv=("a\nb\n", "a\nb\nc\n")) == "agent", "ledger gains rows: agent lane")
    ok(lane(["rehearsal/loop/score-ledger.csv"], lv=("a\nb\n", "a\nX\nc\n")) == "owner",
       "ledger rewrites a row: Dalaun's lane")
    ok(lane(["rehearsal/loop/score-ledger.csv"]) == "owner", "ledger unreadable: Dalaun's lane (fail closed)")
    ok(lane([{"filename": "rehearsal/loop/score-ledger.csv", "status": "removed"}]) == "owner",
       "ledger deleted: Dalaun's lane")
    for bad in ("rehearsal/ @x\n", "* @dalaun\n/rehearsal/*.py\n", "/a/ @x\n"):
        try:
            parse_codeowners(bad)
            ok(False, f"rejects CODEOWNERS {bad.strip()!r}")
        except ValueError:
            ok(True, f"rejects CODEOWNERS {bad.strip()!r}")
    print(f"\n{fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(run_in_actions())
