#!/usr/bin/env python3
"""Verifier pass: an agent that did not write the code passes the exact commit.

Green checks and a bot review are not a verdict. An agent-lane pull request
merges only after a verifier records a verdict on the pull request's current
head commit. Her verdicts (pstack shipping.md): PASS, PASS+NOTES or FAIL.

  PASS         nothing to fix
  PASS+NOTES   mergeable; the notes are things worth doing that don't block
  FAIL         blocks. Only three things block: a bug a user would hit, a
               failed check, or a shipped doc that is wrong.

The verdict is a GitHub commit status:

  context      "Verifier pass"
  state        success for PASS and PASS+NOTES, failure for FAIL
  description  "<VERDICT> <first 12 of the sha> by <verifier>: <one line>"
  commit       the pull request's head commit, and only that one

and the full report goes on the pull request as a comment. The report must name
the full head commit: a result that doesn't record the commit it covers doesn't
count ("a gap does not count as a pass").

A status belongs to one commit, so any new push leaves the new head with no
pass and the merge waits again. Unlike a check that reruns on a review, a status
has one current value per commit, so an old red result can't block a later
pass (the vault's PR 41 lesson).

The verifier must be named in .github/lane/verifiers (Dalaun's lane), must not
be the pull request's author, and must not have authored or committed any of
its commits. Copilot and other review bots never count (her rule: a bot review
is not a verdict).

  verifier_pass.py --post --pr N --sha SHA --as LOGIN --verdict V --note "..."
                   --report FILE [--asked-by LOGIN]
      run by the verifier-pass workflow with the verifier badge's token, after
      the verifier's run. Refuses if SHA is not the current head, LOGIN or the
      agent that asked (--asked-by) wrote any of it, the report doesn't name
      the full head commit, or (for a pass) a check in GREEN_FIRST isn't green
      on that commit. Never run by the author.
  verifier_pass.py --check --pr N
      say whether the pull request's head has a valid pass (exit 0) or not (1)
  verifier_pass.py --audit-recent --days 2
      every pull request merged in the last DAYS days: if anyone but Dalaun
      merged it, its merged head had to carry a valid pass. Exit 1 otherwise,
      so the audit shows red. (A merge made by github-actions starts no push
      workflow, so the audit runs on a schedule, not on the merge.)
  verifier_pass.py --selftest

Standard library only. Needs GH_TOKEN and GITHUB_REPOSITORY (or --repo).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTEXT = "Verifier pass"
OWNER = "dalaun"
VERIFIERS = ROOT / ".github" / "lane" / "verifiers"
# A pass needs these checks green on the same commit first: the lane guard
# (it is an agent-lane pull request) and the keystone checks (the gates ran).
GREEN_FIRST = ["lane-guard", "keystone"]
VERDICTS = {"PASS": "success", "PASS+NOTES": "success", "FAIL": "failure"}
NEVER = {"copilot", "copilot-pull-request-reviewer[bot]", "copilot-swe-agent[bot]", "github-actions[bot]"}
# Badges that write pull requests or run errands here. None of them may be a
# verifier: a listed login can post the status directly, skipping --post's checks.
WRITER_BADGES = {"dalaun-finchdagen-claude[bot]", "dalaun-northstar-claude[bot]",
                 "dalaun-northstar-grokbot[bot]", "dalaun-northstar-muse[bot]"}


def allowed_verifiers(text: str) -> set:
    return {ln.split("#", 1)[0].strip().lower() for ln in text.splitlines()} - {""} - NEVER


def writers(pr: dict, commits: list) -> set:
    who = {((pr.get("user") or {}).get("login") or "").lower()}
    for c in commits:
        for k in ("author", "committer"):
            login = ((c.get(k) or {}) or {}).get("login")
            if login:
                who.add(login.lower())
    return who - {""}


def valid_pass(statuses: list, head_sha: str, allowed: set, wrote: set) -> tuple:
    """Return (ok, why). statuses: the head commit's statuses, newest first (GitHub's order)."""
    for s in statuses:
        if s.get("context") != CONTEXT:
            continue
        login = ((s.get("creator") or {}).get("login") or "").lower()
        # Only the newest status per context counts, as on GitHub.
        if s.get("state") != "success":
            return False, f"the newest '{CONTEXT}' is {s.get('state')}"
        if login not in allowed:
            return False, f"'{CONTEXT}' set by {login or 'unknown'}, who is not in .github/lane/verifiers"
        if login in wrote:
            return False, f"'{CONTEXT}' set by {login}, who wrote part of this pull request"
        desc = s.get("description") or ""
        verdict = desc.split(" ", 1)[0]
        if verdict not in ("PASS", "PASS+NOTES"):
            return False, f"'{CONTEXT}' does not open with PASS or PASS+NOTES"
        if desc.split(" ")[1:2] != [head_sha[:12]]:
            return False, f"'{CONTEXT}' does not name the commit {head_sha[:12]}"
        return True, f"{verdict} by {login} on {head_sha[:12]}"
    return False, f"no '{CONTEXT}' on {head_sha[:12]}"


# ------------------------------------------------------------------ GitHub API

def api(path: str, method: str = "GET", body: dict | None = None):
    req = urllib.request.Request("https://api.github.com" + path, method=method,
                                 data=json.dumps(body).encode() if body else None, headers={
        "Authorization": "Bearer " + os.environ["GH_TOKEN"],
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "verifier-pass",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:  # say which call failed and what GitHub says it needs
        try:
            msg = json.loads(e.read() or b"{}").get("message", "")
        except Exception:
            msg = ""
        need = e.headers.get("X-Accepted-GitHub-Permissions", "") if e.headers is not None else ""
        raise RuntimeError(f"{method} {path.split('?')[0]}: HTTP {e.code} {msg}".rstrip()
                           + (f" (GitHub says this call needs: {need})" if need else "")) from None


def pr_state(repo: str, number: int) -> tuple:
    pr = api(f"/repos/{repo}/pulls/{number}")
    commits = api(f"/repos/{repo}/pulls/{number}/commits?per_page=100")
    statuses = api(f"/repos/{repo}/commits/{pr['head']['sha']}/statuses?per_page=100")
    allowed = allowed_verifiers(VERIFIERS.read_text())
    return pr, commits, statuses, allowed


def check(repo: str, number: int) -> int:
    pr, commits, statuses, allowed = pr_state(repo, number)
    ok, why = valid_pass(statuses, pr["head"]["sha"], allowed, writers(pr, commits))
    print(("ok    " if ok else "WAIT  ") + why)
    return 0 if ok else 1


def post(repo: str, number: int, sha: str, login: str, verdict: str, note: str,
         report: str = "", asked_by: str = "") -> int:
    pr, commits, _, allowed = pr_state(repo, number)
    head = pr["head"]["sha"]
    login = login.lower()
    wrote = writers(pr, commits)
    if verdict not in VERDICTS:
        print(f"REFUSE  the verdict must be one of {', '.join(VERDICTS)}")
        return 1
    if verdict != "PASS" and not note.strip():
        print(f"REFUSE  {verdict} needs a note saying what was found")
        return 1
    if not sha or head[:len(sha)] != sha or len(sha) < 12:
        print(f"REFUSE  you reviewed {sha or 'no commit'}, but the head is now {head[:12]}: review the head again")
        return 1
    if login not in allowed:
        print(f"REFUSE  {login} is not in {VERIFIERS.relative_to(ROOT)}")
        return 1
    for who in (login, asked_by.lower()):
        if who and who in wrote:
            print(f"REFUSE  {who} wrote part of this pull request; a verifier must not have")
            return 1
    if head not in report:
        print(f"REFUSE  the report does not name the full head commit {head}: a gap does not count as a pass")
        return 1
    if VERDICTS[verdict] == "success":
        for name in GREEN_FIRST:
            runs = api(f"/repos/{repo}/commits/{head}/check-runs?check_name="
                       + urllib.parse.quote(name)).get("check_runs", [])
            if not any(r.get("conclusion") == "success" for r in runs):
                print(f"REFUSE  '{name}' has not passed on {head[:12]}: a pass comes after the checks")
                return 1
    desc = f"{verdict} {head[:12]} by {login}: {note or 'reran the checks, ran it, read the diff'}"[:140]
    api(f"/repos/{repo}/statuses/{head}", "POST",
        {"state": VERDICTS[verdict], "context": CONTEXT, "description": desc})
    print("posted  " + desc)
    try:
        api(f"/repos/{repo}/issues/{number}/comments", "POST",
            {"body": f"**{CONTEXT}: {verdict}** on `{head}` by {login}"
                     + (f", asked by {asked_by}" if asked_by else "") + "\n\n" + report})
    except RuntimeError as e:
        print(f"::error title=Report comment not posted::{e}. The verdict status above did post. "
              "If this is HTTP 403, the verifier app lacks a permission: on GitHub, Settings > Developer "
              "settings > GitHub Apps > dalaun-finchdagen-verifier > Permissions, set Pull requests to "
              "Read and write, save, then accept the update on the app's installation page.")
        return 1
    print("report  posted on the pull request")
    return 0


def audit_one(repo: str, pr: dict) -> tuple:
    merger = ((pr.get("merged_by") or {}).get("login") or "").lower()
    if merger == OWNER:
        return True, f"PR #{pr['number']}: Dalaun merged it, his call"
    commits = api(f"/repos/{repo}/pulls/{pr['number']}/commits?per_page=100")
    statuses = api(f"/repos/{repo}/commits/{pr['head']['sha']}/statuses?per_page=100")
    allowed = allowed_verifiers(VERIFIERS.read_text())
    ok, why = valid_pass(statuses, pr["head"]["sha"], allowed, writers(pr, commits))
    return ok, f"PR #{pr['number']} merged by {merger}: {why}"


def audit_recent(repo: str, days: int) -> int:
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - days * 86400))
    pulls = api(f"/repos/{repo}/pulls?state=closed&sort=updated&direction=desc&per_page=50")
    bad = 0
    for p in pulls:
        if not p.get("merged_at") or p["merged_at"] < since or p["base"]["ref"] != "main":
            continue
        ok, why = audit_one(repo, api(f"/repos/{repo}/pulls/{p['number']}"))
        print(("pass  " if ok else "FAIL  ") + why)
        bad += not ok
    if bad:
        print(f"\n{bad} merge(s) without a valid verifier pass. Open a revert pull request for Dalaun "
              "for each, and tell him in one line.")
    else:
        print("every merge in the window was Dalaun's or carried a valid verifier pass")
    return 1 if bad else 0


# ------------------------------------------------------------------ selftest

def selftest() -> int:
    fails = 0

    def ok(cond, msg):
        nonlocal fails
        print(("ok    " if cond else "FAIL  ") + msg)
        fails += not cond

    head = "abcdef1234567890" * 2
    allowed = allowed_verifiers("dalaun-northstar-grokbot[bot]\nCopilot\n# comment\n")
    pr = {"user": {"login": "dalaun-finchdagen-claude[bot]"}}
    commits = [{"author": {"login": "dalaun-finchdagen-claude[bot]"}, "committer": {"login": "web-flow"}}]
    wrote = writers(pr, commits)

    def st(login, state="success", desc=None, ctx=CONTEXT):
        return {"context": ctx, "state": state, "creator": {"login": login},
                "description": desc if desc is not None else f"PASS {head[:12]} by {login}: ok"}

    g = "dalaun-northstar-grokbot[bot]"
    ok(valid_pass([st(g)], head, allowed, wrote)[0], "a listed non-author verifier on the head: pass")
    ok(not valid_pass([], head, allowed, wrote)[0], "no status: wait")
    ok(not valid_pass([st("copilot")], head, allowed, wrote)[0], "Copilot never counts, even if listed")
    ok("copilot" not in allowed, "Copilot is dropped from the verifier list")
    ok(not valid_pass([st("dalaun-finchdagen-claude[bot]")], head,
                      allowed | {"dalaun-finchdagen-claude[bot]"}, wrote)[0], "the author verifying itself: wait")
    ok(not valid_pass([st("someone-else[bot]")], head, allowed, wrote)[0], "an unlisted verifier: wait")
    ok(not valid_pass([st(g, desc="PASS 000000000000 by x: ok")], head, allowed, wrote)[0],
       "a pass naming another commit: wait")
    ok(valid_pass([st(g, desc=f"PASS+NOTES {head[:12]} by {g}: rename a column")], head, allowed, wrote)[0],
       "PASS+NOTES merges: the notes don't block")
    ok(not valid_pass([st(g, state="failure", desc=f"FAIL {head[:12]} by {g}: ledger row wrong")],
                      head, allowed, wrote)[0], "FAIL: wait")
    ok(not valid_pass([st(g, desc=f"pass {head[:12]} by {g}: ok")], head, allowed, wrote)[0],
       "no verdict word: wait")
    ok(not valid_pass([st(g, desc=f"PASS by {g}: looked at {head[:12]}")], head, allowed, wrote)[0],
       "the commit must come right after the verdict, not just anywhere")
    ok(not valid_pass([st(g, state="failure"), st(g)], head, allowed, wrote)[0],
       "the newest status is a failure: wait (only the newest counts)")
    ok(valid_pass([st(g), st(g, state="failure")], head, allowed, wrote)[0],
       "a pass after an earlier failure: pass")
    ok(valid_pass([st("x", ctx="other"), st(g)], head, allowed, wrote)[0], "other contexts are ignored")
    co = [{"author": {"login": g}, "committer": {"login": "web-flow"}}]
    ok(not valid_pass([st(g)], head, allowed, writers(pr, co))[0], "a verifier that wrote a commit: wait")
    real = allowed_verifiers(VERIFIERS.read_text())
    ok(bool(real), "the real verifiers list names at least one verifier")
    ok(not (real & WRITER_BADGES), "no badge that writes pull requests is in the real verifiers list")
    ok(all(v.endswith("[bot]") for v in real), "every real verifier is an app, not a person's account")
    print(f"\n{fails} failed")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "dalaun/Finch-Dagen-Foundation"))
    ap.add_argument("--pr", type=int)
    ap.add_argument("--sha")
    ap.add_argument("--as", dest="login")
    ap.add_argument("--verdict", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--report", help="file with the verifier's full report (required to post)")
    ap.add_argument("--asked-by", default="", help="the login that dispatched the verifier run")
    ap.add_argument("--post", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--audit-recent", action="store_true")
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.audit_recent:
        return audit_recent(a.repo, a.days)
    if a.check:
        return check(a.repo, a.pr)
    if a.post:
        report = Path(a.report).read_text() if a.report else ""
        return post(a.repo, a.pr, a.sha or "", a.login or "", a.verdict.upper(), a.note, report, a.asked_by)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
