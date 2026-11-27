#!/usr/bin/env python3
"""Mutation guard: every check must prove it can fail.

A check that is green on a broken input catches nothing. This guard keeps a
list of known-bad cases ("mutants"), one or more per check, in checks.json.
Each mutant loosens a rule in the check's own code or plants a broken input,
then runs the check. The guard is red when:

  SURVIVED     the check stayed green on its known-bad case
  CRASHED      the check went red only because the mutant broke Python or
               the shell (a traceback is not a catch)
  STALE        the text a mutant edits is gone, so the case no longer tests
               anything (update the mutant when the check changes)
  BASELINE     the check is red on the clean tree, so no mutant can be judged
  NOT WIRED    the check's command appears in no workflow that runs on pull
               requests, so CI never runs it
  UNLISTED     a file that looks like a check (see "discover") is in no
               entry and not exempt, so it has no known-bad case
  KILLED       a mutant marked "pending" (a known gap, with the fix named) is
               now caught: drop "pending" so the gap stays closed

Analogy: a smoke detector test button. Pressing it proves the alarm can
sound. This guard presses every button on every pull request.

  python3 .github/mutation/mutation_guard.py                 everything
  python3 .github/mutation/mutation_guard.py --static        wiring and listing only (seconds)
  python3 .github/mutation/mutation_guard.py --only ID[,ID]  some checks
  python3 .github/mutation/mutation_guard.py --list          inventory table
  python3 .github/mutation/mutation_guard.py --selftest      the guard's own known-bad cases

Each check runs in its own throwaway git worktree of HEAD, so the real
checkout is never edited. Standard library only. Same file in every repo;
only checks.json differs.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CRASH = re.compile(r"Traceback \(most recent call last\)|SyntaxError:|IndentationError:|"
                   r"NameError:|ModuleNotFoundError:|command not found|ReferenceError:|"
                   r"SyntaxError \[|ERR_MODULE_NOT_FOUND")


def sh(cmd, cwd, timeout=None, env=None):
    t = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True,
                           timeout=timeout, env=env)
        return p.returncode, (p.stdout or "") + (p.stderr or ""), time.time() - t
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"") if isinstance(e.stdout, bytes) else (e.stdout or "")
        if isinstance(out, bytes):
            out = out.decode(errors="replace")
        return 124, out + f"\n[timed out after {timeout}s]", time.time() - t


def norm(s: str) -> str:
    return " ".join(s.split())


# ------------------------------------------------------------------ static checks

def workflow_runs(root: Path, wf_dir: str) -> dict[str, str]:
    """Workflow file -> its text, for workflows that run on pull requests."""
    out = {}
    d = root / wf_dir
    for f in sorted(list(d.glob("*.yml")) + list(d.glob("*.yaml"))) if d.is_dir() else []:
        text = f.read_text()
        if re.search(r"^\s*pull_request(_target)?\s*:", text, re.M) or re.search(r"^on:\s*\[?.*pull_request", text, re.M):
            out[str(f.relative_to(root))] = text
    return out


def wired(check: dict, runs: dict[str, str], by_id: dict) -> tuple[bool, str]:
    if "wired_via" in check:
        via = by_id.get(check["wired_via"])
        if not via:
            return False, f"wired_via names unknown check {check['wired_via']!r}"
        ok, where = wired(via, runs, by_id)
        return ok, (f"through {via['id']} ({where})" if ok else f"through {via['id']}: {where}")
    cmd = norm(check.get("wired", check["run"]))
    for f, text in runs.items():
        if cmd in norm(text):
            return True, f
    return False, f"'{cmd}' is in no workflow that runs on pull requests"


def tracked(root: Path) -> list[str]:
    r = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, text=True)
    return [p for p in r.stdout.split("\0") if p]


def discovered(root: Path, rules: list[dict]) -> set[str]:
    files = tracked(root)
    hits = set()
    for rule in rules:
        pats = rule["glob"] if isinstance(rule["glob"], list) else [rule["glob"]]
        rx = re.compile(rule["grep"]) if rule.get("grep") else None
        for f in files:
            if not any(fnmatch.fnmatch(f, p) for p in pats):
                continue
            if any(fnmatch.fnmatch(f, p) for p in rule.get("not", [])):
                continue
            if rx:
                try:
                    if not rx.search((root / f).read_text(errors="replace")):
                        continue
                except (OSError, UnicodeDecodeError):
                    continue
            hits.add(f)
    return hits


def static(root: Path, cfg: dict) -> list[tuple[str, str, str]]:
    """(status, check id or path, detail) for wiring and listing problems."""
    probs = []
    by_id = {c["id"]: c for c in cfg["checks"]}
    if len(by_id) != len(cfg["checks"]):
        probs.append(("CONFIG", "-", "two checks share an id"))
    runs = workflow_runs(root, cfg.get("workflows", ".github/workflows"))
    for c in cfg["checks"]:
        if skipped(root, c):
            continue
        ok, where = wired(c, runs, by_id)
        if not ok:
            probs.append(("NOT WIRED", c["id"], where))
        if not [m for m in c.get("mutants", []) if not m.get("pending")]:
            probs.append(("NO KNOWN-BAD", c["id"], "every check needs at least one mutant that is not pending"))
        for m in c.get("mutants", []):
            if not m.get("why"):
                probs.append(("CONFIG", f"{c['id']}/{m.get('id')}", "a mutant needs a plain-words 'why'"))
    covered = {s for c in cfg["checks"] for s in c.get("source", [])}
    exempt = {e["path"] for e in cfg.get("exempt", []) if e.get("why")}
    for f in sorted(discovered(root, cfg.get("discover", []))):
        if f not in covered and f not in exempt:
            probs.append(("UNLISTED", f, "looks like a check but has no entry in checks.json (add one with a known-bad case, or exempt it with a reason)"))
    me = norm("mutation_guard.py")
    if not any(me in norm(t) for t in runs.values()):
        probs.append(("NOT WIRED", "mutation_guard", "no pull-request workflow runs the guard itself"))
    return probs


def skipped(root: Path, c: dict) -> bool:
    return any(not (root / r).exists() for r in c.get("requires", []))


# ------------------------------------------------------------------ mutants

class Stale(Exception):
    pass


def apply(wt: Path, m: dict) -> None:
    """One edit, or several under "edits" (for a move between files)."""
    for e in m.get("edits", [m]):
        edit(wt, e)
    if m.get("track") or m.get("commit"):
        subprocess.run(["git", "add", "-A"], cwd=wt, capture_output=True)
    if m.get("commit"):
        subprocess.run(["git", "-c", "user.name=mutation-guard", "-c", "user.email=guard@invalid",
                        "commit", "-qm", f"mutant {m['id']}", "--no-verify"], cwd=wt, capture_output=True)


def edit(wt: Path, m: dict) -> None:
    f = wt / m["file"]
    if "write" in m:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(m["write"])
    elif "append" in m:
        f.write_text(f.read_text() + m["append"])
    elif "delete" in m:
        if not f.exists():
            raise Stale(f"{m['file']} is gone")
        f.unlink()
    else:
        if not f.exists():
            raise Stale(f"{m['file']} is gone")
        text = f.read_text()
        n = text.count(m["find"])
        want = m.get("count", 1)
        if n != want:
            raise Stale(f"expected {want} copy of the text to edit in {m['file']}, found {n}")
        f.write_text(text.replace(m["find"], m["replace"]))


def reset(wt: Path, base: str) -> None:
    subprocess.run(["git", "reset", "-q", "--hard", base], cwd=wt, capture_output=True)
    subprocess.run(["git", "clean", "-qfd"], cwd=wt, capture_output=True)


def run_check(root: Path, cfg: dict, c: dict, verbose: bool) -> list[tuple[str, str, str]]:
    res = []
    base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()
    tmp = Path(tempfile.mkdtemp(prefix=f"mg-{c['id']}-"))
    wt = tmp / "wt"
    try:
        r = subprocess.run(["git", "worktree", "add", "-q", "--detach", str(wt), base], cwd=root,
                           capture_output=True, text=True)
        if r.returncode:
            return [("CONFIG", c["id"], "could not make a worktree: " + r.stderr.strip())]
        for link in cfg.get("link", []):
            if (root / link).exists() and not (wt / link).exists():
                os.symlink(root / link, wt / link)
        for step in c.get("setup", []):
            code, out, _ = sh(step, wt, c.get("timeout", 900))
            if code:
                return [("BASELINE", c["id"], f"setup '{step}' failed: {out.strip()[-300:]}")]
        timeout = c.get("timeout", 900)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        code, out, secs = sh(c["run"], wt, timeout, env)
        if code != 0:
            return [("BASELINE", c["id"], f"red on the clean tree (exit {code}): {out.strip()[-400:]}")]
        res.append(("ok", c["id"], f"clean tree green in {secs:.0f}s"))
        for m in c.get("mutants", []):
            name = f"{c['id']}/{m['id']}"
            try:
                apply(wt, m)
            except Stale as e:
                res.append(("STALE", name, str(e)))
                reset(wt, base)
                continue
            code, out, secs = sh(c["run"], wt, timeout, env)
            reset(wt, base)
            crashed = bool(CRASH.search(out)) and not m.get("crash_ok")
            expect = m.get("expect")
            caught = code != 0 and not crashed and (not expect or re.search(expect, out))
            if m.get("pending"):
                status = "KILLED" if caught else "known gap"
                detail = (f"now caught: drop 'pending' ({m['pending']})" if caught else
                          f"still survives, fix named: {m['pending']}")
            elif caught:
                status, detail = "ok", f"caught (exit {code}, {secs:.0f}s): {m['why']}"
            elif code != 0 and crashed:
                status, detail = "CRASHED", f"red only by crashing, not by the rule: {tail(out)}"
            elif code != 0:
                status, detail = "SURVIVED", f"red, but without the expected message /{expect}/: {tail(out)}"
            else:
                status, detail = "SURVIVED", f"stayed green: {m['why']}"
            res.append((status, name, detail))
            if verbose and status != "ok":
                print(out[-2000:], file=sys.stderr)
        return res
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=root, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)
        subprocess.run(["git", "worktree", "prune"], cwd=root, capture_output=True)


def tail(out: str) -> str:
    lines = [ln for ln in out.strip().splitlines() if ln.strip()]
    return (lines[-1] if lines else "(no output)")[:240]


BAD = {"SURVIVED", "CRASHED", "STALE", "BASELINE", "NOT WIRED", "UNLISTED", "KILLED", "CONFIG", "NO KNOWN-BAD"}


def guard(root: Path, cfg: dict, only: set[str] | None, static_only: bool, jobs: int, verbose: bool) -> int:
    rows = static(root, cfg)
    if not static_only:
        todo = [c for c in cfg["checks"] if (not only or c["id"] in only)]
        for c in todo:
            if skipped(root, c):
                rows.append(("skipped", c["id"], "needs " + ", ".join(c["requires"]) + " (not in this tree yet)"))
        todo = [c for c in todo if not skipped(root, c)]
        with cf.ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
            for part in ex.map(lambda c: run_check(root, cfg, c, verbose), todo):
                rows.extend(part)
    width = max([len(r[1]) for r in rows] + [10])
    for status, name, detail in rows:
        print(f"{status:<12} {name:<{width}}  {detail}")
    bad = [r for r in rows if r[0] in BAD]
    n_mut = sum(1 for r in rows if "/" in r[1])
    summary = (f"\n{len(cfg['checks'])} checks, {n_mut} known-bad cases run, "
               f"{sum(1 for r in rows if r[0] == 'known gap')} known gaps, {len(bad)} problems")
    print(summary)
    step = os.environ.get("GITHUB_STEP_SUMMARY")
    if step:
        with open(step, "a") as fh:
            fh.write("## Mutation guard\n\n| status | check | detail |\n|---|---|---|\n")
            for status, name, detail in rows:
                fh.write(f"| {status} | `{name}` | {detail.replace('|', '/')} |\n")
            fh.write(summary + "\n")
    return 1 if bad else 0


def inventory(root: Path, cfg: dict) -> int:
    runs = workflow_runs(root, cfg.get("workflows", ".github/workflows"))
    by_id = {c["id"]: c for c in cfg["checks"]}
    print(f"{'check':<28} {'in CI':<6} {'known-bad':<9} run")
    for c in cfg["checks"]:
        ok, _ = wired(c, runs, by_id)
        live = len([m for m in c.get("mutants", []) if not m.get("pending")])
        gaps = len([m for m in c.get("mutants", []) if m.get("pending")])
        print(f"{c['id']:<28} {'yes' if ok else 'NO':<6} {live:<3}{('+' + str(gaps) + ' gap') if gaps else '':<6} {c['run']}")
    return 0


# ------------------------------------------------------------------ selftest

def selftest() -> int:
    """The guard's own known-bad cases: each planted problem must turn it red."""
    fails = 0
    tmp = Path(tempfile.mkdtemp(prefix="mg-self-"))
    try:
        repo = tmp / "r"
        (repo / ".github/workflows").mkdir(parents=True)
        (repo / "check_limit.py").write_text(
            "import sys\nLIMIT = 120\nv = int(open('data.txt').read())\n"
            "sys.exit(0 if v <= LIMIT else 1)\n")
        (repo / "check_other.py").write_text("import sys\nsys.exit(0)\n")
        (repo / "data.txt").write_text("100\n")
        wf = ("on:\n  pull_request:\njobs:\n  a:\n    steps:\n      - run: python3 check_limit.py\n"
              "      - run: python3 .github/mutation/mutation_guard.py\n")
        (repo / ".github/workflows/ci.yml").write_text(wf)
        for args in (["init", "-q"], ["add", "-A"],
                     ["-c", "user.name=t", "-c", "user.email=t@invalid", "commit", "-qm", "base"]):
            subprocess.run(["git", *args], cwd=repo, capture_output=True)

        good = {"id": "limit", "source": ["check_limit.py"], "run": "python3 check_limit.py",
                "mutants": [{"id": "over", "why": "121 is over the limit", "file": "data.txt", "write": "121\n"}]}
        disc = [{"glob": "check_*.py"}]
        exempt = [{"path": "check_other.py", "why": "not a check"}]

        def case(label, cfg, want_red, want_status=None):
            nonlocal fails
            import io
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = guard(repo, cfg, None, False, 1, False)
            out = buf.getvalue()
            red = code != 0
            ok = red == want_red and (not want_status or re.search(rf"^{re.escape(want_status)}\b", out, re.M))
            print(f"{'ok  ' if ok else 'FAIL'}  {label}")
            if not ok:
                fails += 1
                print(out)

        base = {"discover": disc, "exempt": exempt, "checks": [good]}
        case("a check that catches its known-bad case is green", base, False)
        case("a mutant that changes nothing the check reads SURVIVES (red)",
             {**base, "checks": [{**good, "mutants": [{"id": "noop", "why": "x", "file": "data.txt", "write": "99\n"}]}]},
             True, "SURVIVED")
        case("loosening the rule in the check's own code is caught only if a case is over it",
             {**base, "checks": [{**good, "mutants": [{"id": "loose", "why": "limit 120 -> 1000",
                                  "file": "check_limit.py", "find": "LIMIT = 120", "replace": "LIMIT = 1000"}]}]},
             True, "SURVIVED")
        case("a mutant that only breaks Python is CRASHED, not a catch",
             {**base, "checks": [{**good, "mutants": [{"id": "boom", "why": "x", "file": "check_limit.py",
                                  "find": "LIMIT = 120", "replace": "LIMIT = = 120"}]}]}, True, "CRASHED")
        case("text the mutant edits is gone: STALE",
             {**base, "checks": [{**good, "mutants": [{"id": "gone", "why": "x", "file": "check_limit.py",
                                  "find": "LIMIT = 999", "replace": "LIMIT = 1"}]}]}, True, "STALE")
        case("a check no pull-request workflow runs: NOT WIRED",
             {**base, "checks": [{**good, "run": "python3 check_limit.py --strict"}]}, True, "NOT WIRED")
        case("a check-looking file with no entry: UNLISTED", {**base, "exempt": []}, True, "UNLISTED")
        case("a check red on the clean tree can't be judged: BASELINE",
             {**base, "checks": [{**good, "run": "python3 check_limit.py && false",
                                  "wired": "python3 check_limit.py"}]}, True, "BASELINE")
        case("a known gap that still survives is reported, not red",
             {**base, "checks": [{**good, "mutants": good["mutants"] + [
                 {"id": "gap", "why": "x", "file": "data.txt", "write": "50\n", "pending": "fix X"}]}]},
             False, "known gap")
        case("a known gap that is now caught is red until 'pending' is dropped (ratchet)",
             {**base, "checks": [{**good, "mutants": good["mutants"] + [
                 {"id": "gap", "why": "x", "file": "data.txt", "write": "500\n", "pending": "fix X"}]}]},
             True, "KILLED")
        case("a check whose only mutants are pending has NO KNOWN-BAD case",
             {**base, "checks": [{**good, "mutants": [{**good["mutants"][0], "pending": "x"}]}]}, True, "NO KNOWN-BAD")
        case("red with the wrong message doesn't count when 'expect' is set",
             {**base, "checks": [{**good, "mutants": [{**good["mutants"][0], "expect": "LIMIT EXCEEDED"}]}]},
             True, "SURVIVED")
        (repo / ".github/workflows/ci.yml").write_text(wf.replace("mutation_guard.py", "other.py"))
        case("the guard itself not in CI: NOT WIRED", base, True, "NOT WIRED")
        (repo / ".github/workflows/ci.yml").write_text(wf)
        before = (repo / "data.txt").read_text()
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            guard(repo, base, None, False, 1, False)
        if (repo / "data.txt").read_text() != before:
            fails += 1
            print("FAIL  the real checkout was edited")
        else:
            print("ok    the real checkout is never edited (mutants run in a worktree)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{fails} failed")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(HERE / "checks.json"))
    ap.add_argument("--root", default=None, help="repository root (default: the git top level)")
    ap.add_argument("--only", default="")
    ap.add_argument("--static", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--jobs", type=int, default=int(os.environ.get("MUTATION_JOBS", "2")))
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    root = Path(a.root) if a.root else Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE,
                                                           capture_output=True, text=True).stdout.strip())
    cfg = json.loads(Path(a.config).read_text())
    if a.list:
        return inventory(root, cfg)
    only = {x for x in a.only.split(",") if x} or None
    return guard(root, cfg, only, a.static, a.jobs, a.verbose)


if __name__ == "__main__":
    sys.exit(main())
