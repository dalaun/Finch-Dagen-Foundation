#!/usr/bin/env python3
"""Copilot approval: a second reader for engine changes, from another vendor.

Posts the commit status "Copilot approval" on a pull request's head commit:

  success  the pull request touches no path in .github/lane/copilot-paths, or
           Copilot's newest review on this exact head commit is an approval;
  failure  Copilot's newest review on this head commit requests changes;
  pending  anything else (no review yet, a comment-only review, a review of an
           older commit).

Why: the Verifier pass (verifier_pass.py) proves the verifier is a different
identity from the writer, but both are Claude. Copilot code review runs models
from other providers. It only reads the code; it never reruns the checks or
runs the engine, so it adds to the Verifier pass and never replaces it.

Copilot's approval counts only when "Copilot can approve" is on for this repo
(GitHub, generally available 2026-10-28). Who asks for the review: the
verifier run requests it as Dalaun (his AI credits), because a review asked
for automatically is billed to the pull request's author, and the badges have
no Copilot license.

This script and copilot-paths always come from main (the workflow checks out
main), never from the pull request.

  python3 copilot_review.py --pr N      in GitHub Actions (GH_TOKEN, GITHUB_REPOSITORY)
  python3 copilot_review.py --selftest  its own cases

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from fnmatch import fnmatchcase
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATHS = ROOT / ".github" / "lane" / "copilot-paths"
REVIEWER = "copilot-pull-request-reviewer[bot]"   # as GitHub's API names it (PR 15, 2026-11-21)
CONTEXT = "Copilot approval"


def globs(text: str) -> list[str]:
    return [l.strip() for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]


def needs_review(files: list[dict], patterns: list[str]) -> list[str]:
    hit = []
    for f in files:
        for name in {f.get("filename", ""), f.get("previous_filename") or ""} - {""}:
            if any(fnmatchcase(name, p) for p in patterns):
                hit.append(name)
    return sorted(set(hit))


def decide(files: list[dict], reviews: list[dict], head: str, patterns: list[str]) -> tuple[str, str]:
    """Return (state, description) for the head commit."""
    hit = needs_review(files, patterns)
    if not hit:
        return "success", "not needed: no engine or input file changed"
    mine = [r for r in reviews
            if (r.get("user") or {}).get("login") == REVIEWER and r.get("commit_id") == head
            and r.get("state") in ("APPROVED", "CHANGES_REQUESTED", "COMMENTED")]
    if not mine:
        return "pending", f"waits for Copilot's review of {head[:12]} ({len(hit)} engine file(s))"
    last = max(mine, key=lambda r: r.get("submitted_at") or "")
    if last["state"] == "APPROVED":
        return "success", f"Copilot approved {head[:12]}"
    if last["state"] == "CHANGES_REQUESTED":
        return "failure", f"Copilot requested changes on {head[:12]}"
    return "pending", f"Copilot commented on {head[:12]} but did not approve"


def api(path: str, method: str = "GET", body: dict | None = None):
    out, url = [], "https://api.github.com" + path
    while url:
        req = urllib.request.Request(url, method=method,
                                     data=json.dumps(body).encode() if body else None, headers={
            "Authorization": "Bearer " + os.environ["GH_TOKEN"],
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "copilot-approval",
        })
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
            link = r.headers.get("Link") or ""
        if method != "GET" or not isinstance(data, list):
            return data
        out += data
        nxt = [p.split(";")[0].strip(" <>") for p in link.split(",") if 'rel="next"' in p]
        url = nxt[0] if nxt else None
    return out


def run(pr: int) -> int:
    repo = os.environ["GITHUB_REPOSITORY"]
    head = api(f"/repos/{repo}/pulls/{pr}")["head"]["sha"]
    files = api(f"/repos/{repo}/pulls/{pr}/files?per_page=100")
    reviews = api(f"/repos/{repo}/pulls/{pr}/reviews?per_page=100")
    state, desc = decide(files, reviews, head, globs(PATHS.read_text()))
    api(f"/repos/{repo}/statuses/{head}", "POST",
        {"state": state, "context": CONTEXT, "description": desc[:140]})
    print(f"{state}: {desc}")
    return 0


def selftest() -> int:
    bad = 0

    def ok(cond, msg):
        nonlocal bad
        print(("ok    " if cond else "FAIL  ") + msg)
        bad += not cond

    pats = globs(PATHS.read_text())
    ok(bool(pats), "copilot-paths lists at least one glob")
    head, old = "a" * 40, "b" * 40
    eng = [{"filename": "rehearsal/synthetic/rehearsal_run.py"}]
    doc = [{"filename": "rehearsal/loop/NEXT-MOVES.md"}]

    def rv(state, sha=head, who=REVIEWER, at="2026-11-26T01:00:00Z"):
        return {"user": {"login": who}, "state": state, "commit_id": sha, "submitted_at": at}

    ok(decide(doc, [], head, pats)[0] == "success", "a docs-only pull request needs no Copilot review")
    ok(decide(eng, [], head, pats)[0] == "pending", "an engine change with no review waits")
    ok(decide(eng, [rv("APPROVED")], head, pats)[0] == "success", "Copilot's approval on the head commit passes")
    ok(decide(eng, [rv("APPROVED", old)], head, pats)[0] == "pending", "an approval of an older commit doesn't count")
    ok(decide(eng, [rv("COMMENTED")], head, pats)[0] == "pending", "a comment-only review is not an approval")
    ok(decide(eng, [rv("CHANGES_REQUESTED")], head, pats)[0] == "failure", "changes requested fails")
    ok(decide(eng, [rv("APPROVED", who="dalaun-finchdagen-verifier[bot]")], head, pats)[0] == "pending",
       "someone else's approval is not Copilot's")
    ok(decide(eng, [rv("APPROVED", at="2026-11-26T01:00:00Z"),
                    rv("CHANGES_REQUESTED", at="2026-11-26T02:00:00Z")], head, pats)[0] == "failure",
       "only Copilot's newest review on the head counts")
    ok(decide([{"filename": "rehearsal/synthetic/x.md", "previous_filename": "rehearsal/synthetic/stack.json"}],
              [], head, pats)[0] == "pending", "renaming an engine input away still needs review")
    ok(decide([{"filename": "rehearsal/synthetic/benchmarks-2026.json"}], [], head, pats)[0] == "pending",
       "a benchmark change needs review")
    print(f"\n{bad} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr", type=int)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else run(a.pr))
