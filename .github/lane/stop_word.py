#!/usr/bin/env python3
"""The stop word: "@finchdagen-claude stop" from Dalaun halts a pull request.

Analogy: the red button on a factory line. Dalaun writes a comment

    @finchdagen-claude stop

alone on a line of a comment on the pull request, or on the issue it closes
(a line like "@finchdagen-claude stop using X and ..." is an ask, not the stop
word), and from then on:

  - the lane guard puts that pull request in Dalaun's lane (auto-merge off) the
    next time it runs, which is on every new push;
  - the verifier script refuses to post a pass on it, so it cannot merge itself;
  - the foundation badge, told so in CLAUDE.md, answers "Stopped" and does nothing more.

"@finchdagen-claude go" (or "resume") from Dalaun lifts it. The newest of his
stop and go comments wins. Only Dalaun's comments count: this repository is
public, and a stranger must not be able to stall or restart the lane.

What it cannot do: a pull request that already holds a pass and has auto-merge on
merges within seconds of its last check; a stop written after that point is too
late for that one (revert it instead). Stopping a run that is already working
needs a workflow change (Dalaun's, see README).

Standard library only. Used by lane_guard.py and verifier_pass.py.
"""

from __future__ import annotations

import re

OWNER = "dalaun"
WORD = re.compile(r"^\s*@finchdagen-claude\s+(stop|go|resume)\s*[.!]?\s*$", re.IGNORECASE | re.MULTILINE)
CLOSES = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)\b", re.IGNORECASE)


def linked_issues(pr_body: str | None) -> list:
    """Issue numbers the pull request says it closes ("Closes #12")."""
    return sorted({int(n) for n in CLOSES.findall(pr_body or "")})


def latest_word(comments: list) -> tuple:
    """(word, created_at) of Dalaun's newest stop/go comment, or (None, None).
    comments: GitHub issue comments (dicts with body, user.login, created_at).
    The issue's or pull request's own body counts as a comment too when passed in."""
    best = (None, None)
    for c in comments:
        if ((c.get("user") or {}).get("login") or "").lower() != OWNER:
            continue
        words = WORD.findall(c.get("body") or "")
        if not words:
            continue
        word = "stop" if words[-1].lower() == "stop" else "go"
        at = c.get("created_at") or ""
        if best[1] is None or at >= best[1]:
            best = (word, at)
    return best


def stopped(sources: dict) -> tuple:
    """sources: {label: [comments]} for the pull request and each issue it closes.
    Return (True, why) if Dalaun's newest stop/go word, across all of them, is stop."""
    word, at, where = None, None, None
    for label, comments in sources.items():
        w, t = latest_word(comments)
        if w and (at is None or t >= at):
            word, at, where = w, t, label
    if word == "stop":
        return True, f"has Dalaun's stop word on {where} ({at}); his '@finchdagen-claude go' lifts it"
    return False, ""


def fetch_sources(api_get, repo: str, pr: dict, strict_issues: bool = True, skipped: list | None = None) -> dict:
    """Gather the comments to read. api_get(path) returns parsed JSON from api.github.com.
    strict_issues=False: a linked issue that can't be read is skipped (named in `skipped`)
    instead of raising. The lane guard's token may not read issues; the verifier's can,
    and it checks again before any pass."""
    def comments(number: int) -> list:
        out, page = [], 1
        while True:
            batch = api_get(f"/repos/{repo}/issues/{number}/comments?per_page=100&page={page}")
            out += batch
            if len(batch) < 100 or page >= 10:
                return out
            page += 1

    sources = {f"pull request #{pr['number']}": comments(pr["number"])}
    for n in linked_issues(pr.get("body")):
        try:
            issue = api_get(f"/repos/{repo}/issues/{n}")
            own = [{"body": issue.get("body"), "user": issue.get("user"), "created_at": issue.get("created_at")}]
            sources[f"issue #{n}"] = own + comments(n)
        except Exception as e:
            if strict_issues:
                raise
            if skipped is not None:
                skipped.append(f"issue #{n} ({type(e).__name__})")
    return sources


def selftest(ok) -> None:
    def c(body, at, who=OWNER):
        return {"body": body, "created_at": at, "user": {"login": who}}

    ok(linked_issues("Before... Closes #50 and fixes #7") == [7, 50], "stop word: reads 'Closes #N' links")
    ok(not stopped({"pr": []})[0], "stop word: no comments, not stopped")
    ok(stopped({"pr": [c("@finchdagen-claude stop", "2026-11-24T01:00:00Z")]})[0], "stop word: Dalaun's stop stops")
    ok(not stopped({"pr": [c("@finchdagen-claude stop", "2026-11-24T01:00:00Z", "stranger")]})[0],
       "stop word: a stranger's stop does nothing (public repo)")
    ok(not stopped({"pr": [c("@finchdagen-claude stop", "2026-11-24T01:00:00Z"),
                           c("@FinchDagen-Claude go", "2026-11-24T02:00:00Z")]})[0], "stop word: a later go lifts it")
    ok(stopped({"pr": [c("@finchdagen-claude go", "2026-11-24T01:00:00Z")],
                "issue #5": [c("@finchdagen-claude stop", "2026-11-24T02:00:00Z")]})[0],
       "stop word: a stop on the linked issue stops the pull request")
    ok(not stopped({"pr": [c("@finchdagen-claude please don't stop the relay", "2026-11-24T01:00:00Z")]})[0],
       "stop word: 'stop' must come right after the handle")
    ok(not stopped({"pr": [c("@finchdagen-claude stop using the old table and rebuild it", "2026-11-24T01:00:00Z")]})[0],
       "stop word: an ask that starts with 'stop' is not the stop word (it must stand alone on its line)")
    ok(stopped({"pr": [c("Hold on.\n@finchdagen-claude stop.\n", "2026-11-24T01:00:00Z")]})[0],
       "stop word: alone on its own line inside a longer comment")
    ok(stopped({"pr": [c("@finchdagen-claude go\nlater:\n@finchdagen-claude stop", "2026-11-24T01:00:00Z")]})[0],
       "stop word: inside one comment the last word wins")
