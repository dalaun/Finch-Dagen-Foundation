#!/usr/bin/env python3
"""Goal scorecard: seven yes/no criteria that say whether the rehearsal has reached its goal.

SYNTHETIC. Not legal or tax advice. The scorecard is a finish line, not a target:
it only reads the files below. It never changes an engine number, a stack fee or
the legacy weight w.

  python3 scorecard.py --results out/results.json     print one line per criterion
  python3 scorecard.py --results FILE --all-green     exit 1 unless all seven pass
  python3 scorecard.py --selftest                     a passing and a failing fixture for each criterion

Inputs (a missing file fails the criteria that need it):
  stack.json                     versions, each family_trust with grantor and terms
  grantor-routes.json            routes and their ask_counsel questions
  --results FILE                 the engine's results (rehearsal_run.py --json FILE)
  ../loop/NEXT-MOVES.md          the moves
  counsel-queue.md               questions for counsel with working assumptions
  benchmarks-tax.json            cited tax sources
  SCORECARD.md                   plain-words explanation and the "Documents that would clear it" list

Output: "PASS <id> <reason>" or "FAIL <id> <reason>" per criterion, then
"Scorecard: <n> of 7 pass". Exit code 0 always, except --all-green exits 1 unless all pass.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import grantor_check  # noqa: E402

IDS = ["SC1", "SC2", "SC3", "SC4", "SC5", "SC6", "SC7"]
NAMES = {
    "SC1": "steward-non-grantor",
    "SC2": "no-open-disqualifier",
    "SC3": "beats-status-quo",
    "SC4": "asset-sized",
    "SC5": "asset-to-program",
    "SC6": "checks-clear",
    "SC7": "nothing-blocks",
}
CLEAR_HEADING = "documents that would clear it"


# ------------------------------------------------------------------ helpers

def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def read_text(path):
    try:
        return Path(path).read_text()
    except (OSError, UnicodeDecodeError):
        return None


def read_json(path):
    t = read_text(path)
    if t is None:
        return None
    try:
        return json.loads(t)
    except ValueError:
        return None


def sections(text: str) -> list:
    """Split a markdown file at every heading line; keep each piece."""
    return re.split(r"(?m)^#+ ", text)


def parse_moves(text: str) -> list:
    """Moves in NEXT-MOVES.md: a list of {title, body, open}. Moves are '### ' blocks."""
    m_open = re.search(r"(?m)^## Open", text)
    m_closed = re.search(r"(?m)^## Closed", text)
    start = m_open.start() if m_open else 0
    cut = m_closed.start() if m_closed else len(text)
    parts = []
    if cut >= start:
        parts.append((text[start:cut], True))
        parts.append((text[cut:], False))
    else:
        parts.append((text, True))
    moves = []
    for chunk, is_open in parts:
        for piece in re.split(r"(?m)^### ", chunk)[1:]:
            lines = piece.split("\n", 1)
            body = lines[1] if len(lines) > 1 else ""
            moves.append({"title": lines[0].strip(), "body": body, "open": is_open})
    return moves


def move_key(move: dict):
    m = re.search(r"(?im)^\s*[-*]\s*key:\s*`?([A-Za-z0-9_\-]+)`?", move["body"])
    return m.group(1) if m else None


def has_assumption(move: dict) -> bool:
    return bool(re.search(r"(?im)^\s*[-*]?\s*working assumption:", move["body"]))


def clear_list(md):
    """Lines of the list under the 'Documents that would clear it' heading."""
    if md is None:
        return None
    lines = md.split("\n")
    out, inside = [], False
    for ln in lines:
        if re.match(r"^#+ ", ln):
            inside = CLEAR_HEADING in ln.lower()
            continue
        if inside and re.match(r"^\s*[-*] ", ln):
            out.append(ln)
    return out


def version_route_questions(vid: str, version: dict, routes: dict) -> list:
    """The ask_counsel questions of the route a stack version follows.
    A version may name its route with family_trust.route; otherwise every route whose terms equal the version's terms."""
    ft = version["family_trust"]
    found = []
    for rt in routes.get("routes", []):
        if ft.get("route") == rt.get("id") or (ft.get("route") is None and rt.get("terms") == ft.get("terms")):
            found.extend(rt.get("ask_counsel", []))
    return found


# ------------------------------------------------------------------ criteria
# Each returns (passed: bool, reason: str). ctx holds the already-loaded inputs.

def sc1_versions(ctx) -> list:
    """Stack versions with the founder as a Family Trust trustee, non-grantor status, grantor false."""
    stack = ctx.get("stack")
    if not stack:
        return []
    good = []
    for vid, v in stack.get("versions", {}).items():
        try:
            ft = v["family_trust"]
            terms = ft["terms"]
            res = grantor_check.evaluate(terms)
        except Exception:
            continue
        if "founder" in terms.get("trustees", []) and res["status"] == "non-grantor" and ft.get("grantor") is False:
            good.append((vid, res))
    return good


def sc1(ctx):
    if not ctx.get("stack"):
        return False, "stack.json is missing or unreadable"
    good = sc1_versions(ctx)
    if good:
        return True, "founder is a trustee and the trust is non-grantor in: " + ", ".join(v for v, _ in good)
    return False, "no stack version has the founder as a trustee with a non-grantor trust and grantor false"


def sc2(ctx):
    good = sc1_versions(ctx)
    if not good:
        return False, "no SC1 version to check"
    if ctx.get("routes") is None:
        return False, "grantor-routes.json is missing or unreadable"
    queue = ctx.get("queue")
    if queue is None:
        return False, "counsel-queue.md is missing"
    pieces = [(norm(p), p) for p in sections(queue)]
    for vid, res in good:
        bad = [x["rule"] for x in res["rules"] if x["status"] in ("fail", "amber")]
        if bad:
            return False, f"{vid}: grantor_check rules not passing: {', '.join(bad)}"
        for q in version_route_questions(vid, ctx["stack"]["versions"][vid], ctx["routes"]):
            nq = norm(q)[:60]
            hit = [p for n, p in pieces if nq and nq in n and "assumption" in n]
            if not hit:
                return False, f"{vid}: counsel question has no queue entry with a working assumption: {q[:70]}"
    return True, "no failing or amber rule, and every counsel question has a queue entry with a working assumption"


# Sensitivity rules (pstack hillclimb: a check must be able to fail on a known past mistake).
# On 2026-11-24 SC3 and SC5 passed "by construction": the only winning scenario was sized at the
# version's own break-even, so the win was a rounding hair above zero (+66/yr on a 150,000 asset).
# A win now counts only when it clears a margin and holds at several asset sizes.
# PROPOSED numbers, Dalaun's to set:
MIN_SIZES = 3            # distinct asset-income sizes the win must hold at
MARGIN_SHARE = 0.01      # structure value must exceed this share of the scenario's asset income


def clears_margin(r: dict, v: dict) -> bool:
    """A win that is not just sitting on its own break-even."""
    income = r.get("inputs", {}).get("asset_income", 0)
    return income > 0 and v.get("structure_value", -1) > MARGIN_SHARE * income and v.get("score_vs_A", 0) > 0


def winning_sizes(ctx, vid, need_program=False) -> list:
    """Distinct asset-income sizes where vid clears the margin (and, if asked, sends asset income to the Foundation)."""
    sizes = set()
    for r in (ctx.get("results") or {}).get("results", []):
        v = r.get("versions", {}).get(vid)
        if not v or not clears_margin(r, v):
            continue
        if need_program and not (v.get("program_output", 0) > 0 and v.get("program_source") == "asset_income"):
            continue
        sizes.add(r["inputs"]["asset_income"])
    return sorted(sizes)


def sc3_pairs(ctx) -> list:
    """(scenario, version id) pairs where an SC1 version beats the status quo by the margin,
    kept only for versions whose win holds at MIN_SIZES or more asset sizes."""
    results = ctx.get("results")
    if not results:
        return []
    ids = [v for v, _ in sc1_versions(ctx) if len(winning_sizes(ctx, v)) >= MIN_SIZES]
    pairs = []
    for r in results.get("results", []):
        for vid in ids:
            v = r.get("versions", {}).get(vid)
            if v and clears_margin(r, v):
                pairs.append((r.get("scenario"), vid))
    return pairs


def sc3(ctx):
    if not ctx.get("results"):
        return False, "results file is missing (run rehearsal_run.py --json FILE and pass --results FILE)"
    if not sc1_versions(ctx):
        return False, "no SC1 version"
    pairs = sc3_pairs(ctx)
    if pairs:
        vid = pairs[0][1]
        return True, f"{vid} beats the status quo by more than {MARGIN_SHARE:.0%} of asset income at {len(winning_sizes(ctx, vid))} asset sizes"
    best = max(((len(winning_sizes(ctx, v)), v) for v, _ in sc1_versions(ctx)), default=(0, None))
    return False, (f"no SC1 version beats the status quo by more than {MARGIN_SHARE:.0%} of asset income at {MIN_SIZES} or more "
                   f"asset sizes (best: {best[1]} at {best[0]})")


def sc4(ctx):
    text = ctx.get("next_moves")
    if text is None:
        return False, "NEXT-MOVES.md is missing"
    moves = parse_moves(text)
    for step in ("B1", "B2"):
        found = None
        for m in moves:
            for ln in re.findall(r"(?im)^\s*[-*]\s*step:\s*(.*)$", m["body"]):
                if re.search(r"\b" + step + r"\b", ln):
                    found = m
        if found is None:
            return False, f"no move for route step {step}"
        if found["open"] and not has_assumption(found):
            return False, f"the move for {step} is open and has no Working assumption line"
    return True, "B1 and B2 each have a move that is closed or carries a Working assumption"


def has_4942_with_url(node) -> bool:
    if isinstance(node, dict):
        scalars = [v for v in node.values() if isinstance(v, str)]
        if any("4942" in s for s in scalars) and any(s.startswith("http") for s in scalars):
            return True
        return any(has_4942_with_url(v) for v in node.values())
    if isinstance(node, list):
        return any(has_4942_with_url(v) for v in node)
    return False


def sibling(ctx, vid):
    """The same route and terms with no Foundation share: the version this one would be without the gift."""
    vs = ctx["stack"]["versions"]
    ft = vs[vid]["family_trust"]
    for oid, o in vs.items():
        ot = o.get("family_trust", {})
        if oid != vid and ot.get("route") == ft.get("route") and ot.get("terms") == ft.get("terms") \
                and not ot.get("foundation_share_of_distribution"):
            return oid
    return None


def double_count(ctx, vid):
    """The family can't come out ahead by giving money away. Against its no-share sibling, a
    Foundation-sending version must cost the family more than 0 and no more than what it sent
    (a deduction saves part of the gift, never more than all of it). PR 45's first head counted
    the Foundation's share as kept by the family and broke this. Returns a reason, or None."""
    sib = sibling(ctx, vid)
    if sib is None:
        return None
    w = ctx["stack"].get("legacy_weight_w", 0.0)
    for r in ctx["results"].get("results", []):
        v, s = r.get("versions", {}).get(vid), r.get("versions", {}).get(sib)
        if not v or not s or not v.get("to_foundation", 0) > 0:
            continue
        cost = (s["score_vs_A"] - w * s.get("program_output", 0)) - (v["score_vs_A"] - w * v.get("program_output", 0))
        if not (0 < cost <= v["to_foundation"] + 1):
            return (f"{vid} in {r.get('scenario')}: the gift of {v['to_foundation']} costs the family {cost} against {sib}, "
                    "outside 0 to the gift (Foundation money counted twice?)")
    return None


def sc5(ctx):
    if not ctx.get("results"):
        return False, "results file is missing"
    bench = ctx.get("bench")
    if bench is None:
        return False, "benchmarks-tax.json is missing"
    if not has_4942_with_url(bench):
        return False, "benchmarks-tax.json does not cite IRC 4942's minimum distribution with a URL"
    senders = [v for v, _ in sc1_versions(ctx)
               if any(r.get("versions", {}).get(v, {}).get("program_source") == "asset_income"
                      for r in ctx["results"].get("results", []))]
    for vid in senders:
        bad = double_count(ctx, vid)
        if bad:
            return False, bad
    for vid in senders:
        sizes = winning_sizes(ctx, vid, need_program=True)
        if len(sizes) >= MIN_SIZES:
            return True, (f"{vid} sends asset income to the Foundation and beats the status quo by more than "
                          f"{MARGIN_SHARE:.0%} of asset income at {len(sizes)} asset sizes")
    if not senders:
        return False, "no SC1 version sends asset income to the Foundation (results lack program_source: asset_income)"
    best = max((len(winning_sizes(ctx, v, need_program=True)), v) for v in senders)
    return False, (f"no version that sends asset income to the Foundation beats the status quo by more than "
                   f"{MARGIN_SHARE:.0%} of asset income at {MIN_SIZES} or more sizes (best: {best[1]} at {best[0]})")


def sc6(ctx):
    results = ctx.get("results")
    if not results:
        return False, "results file is missing"
    listed = clear_list(ctx.get("scorecard_md"))
    if listed is None:
        return False, "SCORECARD.md is missing"
    why = "no SC1 version"
    for vid, _ in sc1_versions(ctx):
        reds, ambers, seen = set(), set(), False
        for r in results.get("results", []):
            v = r.get("versions", {}).get(vid)
            if v:
                seen = True
                reds.update(v.get("checks_red", []))
                ambers.update(v.get("checks_amber", []))
        if not seen:
            why = f"{vid} is not in the results"
            continue
        if reds:
            why = f"{vid} has red checks: {', '.join(sorted(reds))}"
            continue
        missing = [a for a in sorted(ambers) if not any(re.search(r"\b" + re.escape(a) + r"\b", ln) for ln in listed)]
        if missing:
            why = f"{vid} amber checks not named under 'Documents that would clear it': {', '.join(missing)}"
            continue
        return True, f"{vid} has no red check and every amber one is named with its document"
    return False, why


def sc7(ctx):
    text = ctx.get("next_moves")
    if text is None:
        return False, "NEXT-MOVES.md is missing"
    queue = ctx.get("queue")
    if queue is None:
        return False, "counsel-queue.md is missing"
    pieces = [norm(p) for p in sections(queue)]
    for m in parse_moves(text):
        if not m["open"]:
            continue
        if not has_assumption(m):
            return False, f"open move without a Working assumption line: {m['title'][:70]}"
        key = move_key(m)
        if not key or not any(norm(key) in p for p in pieces):
            return False, f"open move without a counsel-queue entry: {m['title'][:70]}"
    return True, "every open move has a Working assumption line and a counsel-queue entry"


CHECKS = {"SC1": sc1, "SC2": sc2, "SC3": sc3, "SC4": sc4, "SC5": sc5, "SC6": sc6, "SC7": sc7}


def run_all(ctx) -> dict:
    out = {}
    for cid in IDS:
        try:
            out[cid] = CHECKS[cid](ctx)
        except Exception as e:  # a broken input fails the criterion, never the run
            out[cid] = (False, f"could not check: {type(e).__name__}: {e}")
    return out


# ------------------------------------------------------------------ selftest

def fixture() -> dict:
    """A context where every criterion passes. Built in memory."""
    terms = grantor_check.base_terms()
    terms["trustees"] = ["founder", "independent"]
    bad_terms = grantor_check.base_terms()
    question = "Can the instrument split the trusteeship this way?"
    return {
        "stack": {"versions": {
            "good": {"family_trust": {"grantor": False, "route": "RX", "terms": terms}},
            "pipe": {"family_trust": {"grantor": False, "route": "RX", "terms": terms, "foundation_share_of_distribution": 0.1}},
            "bad": {"family_trust": {"grantor": False, "terms": bad_terms}},
        }, "legacy_weight_w": 0.0},
        "routes": {"routes": [{"id": "RX", "terms": terms, "ask_counsel": [question]}]},
        "results": {"results": [
            {"scenario": f"s{i}", "inputs": {"asset_income": size},
             "versions": {
                 "good": {"structure_value": 5000, "score_vs_A": 5000, "program_output": 0, "to_foundation": 0,
                          "program_source": "fixed_assets", "checks_red": [], "checks_amber": ["S5"]},
                 "pipe": {"structure_value": 4000, "score_vs_A": 4000, "program_output": 1000, "to_foundation": 1000,
                          "program_source": "asset_income", "checks_red": [], "checks_amber": ["S5"]}}}
            for i, size in enumerate((100000, 200000, 300000), 1)]},
        "next_moves": ("# Moves\n\n## Open\n\n"
                       "### 1. asset: size\n\n- Key: `size-key`\n- Step: B1\n- Working assumption: see queue\n\n"
                       "### 2. asset: classes\n\n- Key: `class-key`\n- Step: B2\n- Working assumption: see queue\n\n"
                       "## Closed\n\n(none yet)\n"),
        "queue": ("# Queue\n\n## Split\n\n" + question + "\nASSUMPTION: yes.\n\n"
                  "## Size\n\nKey: `size-key`\nASSUMPTION: small.\n\n"
                  "## Classes\n\nKey: `class-key`\nASSUMPTION: rental.\n"),
        "bench": {"distribution": {"rule": "IRC 4942 minimum distribution", "url": "https://www.law.cornell.edu/uscode/text/26/4942"}},
        "scorecard_md": "# Scorecard\n\n## Documents that would clear it\n\n- S5: the trust deed\n",
    }


def selftest() -> int:
    fails = 0

    def ok(cond, msg):
        nonlocal fails
        print(("ok    " if cond else "FAIL  ") + msg)
        fails += not cond

    good = run_all(fixture())
    for cid in IDS:
        ok(good[cid][0], f"{cid} passes on the passing fixture ({good[cid][1]})")

    def broken(change):
        ctx = copy.deepcopy(fixture())
        change(ctx)
        return run_all(ctx)

    def only_trustee_independent(ctx):
        ctx["stack"]["versions"].pop("good")
        ctx["stack"]["versions"].pop("pipe")

    def drop_queue_question(ctx):
        ctx["queue"] = "# Queue\n\n## Size\n\nKey: `size-key`\nASSUMPTION: small.\n\n## Classes\n\nKey: `class-key`\nASSUMPTION: rental.\n"

    def negative_value(ctx):
        for r in ctx["results"]["results"]:
            for v in r["versions"].values():
                v["structure_value"] = -1

    # Known-bad, 2026-11-24 (relay/state.md turn 9): SC3 passed on one scenario sized at the version's own
    # break-even, +66/yr structure value on a 150,000 asset. The old rule (structure value >= 0 in any one
    # scenario) passed this; the new one must not.
    def nov24_break_even(ctx):
        ctx["results"]["results"] = [{
            "scenario": "asset_sized", "inputs": {"asset_income": 150000},
            "versions": {"good": {"structure_value": 66, "score_vs_A": 1592, "program_output": 0, "to_foundation": 0,
                                  "program_source": "fixed_assets", "checks_red": [], "checks_amber": ["S5"]}}}]

    # Known-bad: a win at only two sizes, both well clear, still fails (one size short).
    def two_sizes(ctx):
        ctx["results"]["results"].pop()

    # Known-bad: three sizes, but one sits on break-even (inside the margin), so only two count.
    def one_at_break_even(ctx):
        for r in ctx["results"]["results"]:
            if r["inputs"]["asset_income"] == 300000:
                r["versions"]["good"]["structure_value"] = 66
                r["versions"]["pipe"]["structure_value"] = 66

    # Known-bad, PR 45 first head c350736f: the Foundation's share was also counted as kept by the family,
    # so the version that gives money away scores as well as or better than the one that doesn't.
    def pr45_double_count(ctx):
        for r in ctx["results"]["results"]:
            v = r["versions"]["pipe"]
            v["score_vs_A"] += v["to_foundation"]
            v["structure_value"] += v["to_foundation"]

    def drop_b2(ctx):
        ctx["next_moves"] = ctx["next_moves"].replace("- Step: B2", "- Step: C2")

    def drop_4942(ctx):
        ctx["bench"] = {"distribution": {"rule": "something else"}}

    def unlisted_amber(ctx):
        for r in ctx["results"]["results"]:
            for v in r["versions"].values():
                v["checks_amber"] = ["S9"]

    def no_assumption(ctx):
        ctx["next_moves"] = ctx["next_moves"].replace("- Working assumption: see queue\n", "", 1)

    cases = [
        ("SC1", only_trustee_independent),
        ("SC2", drop_queue_question),
        ("SC3", negative_value),
        ("SC3", nov24_break_even),
        ("SC5", nov24_break_even),
        ("SC3", two_sizes),
        ("SC5", two_sizes),
        ("SC3", one_at_break_even),
        ("SC5", pr45_double_count),
        ("SC4", drop_b2),
        ("SC5", drop_4942),
        ("SC6", unlisted_amber),
        ("SC7", no_assumption),
    ]
    for cid, change in cases:
        res = broken(change)
        ok(not res[cid][0], f"{cid} fails on {change.__name__} ({res[cid][1]})")

    # The Nov 24 case is only worth having if the old rule let it through.
    nov = copy.deepcopy(fixture())
    nov24_break_even(nov)
    old_rule = any(v.get("structure_value", -1) >= 0 and v.get("score_vs_A", 0) > 0
                   for r in nov["results"]["results"] for v in r["versions"].values())
    ok(old_rule, "the old SC3 rule (structure value >= 0 in any one scenario) passed nov24_break_even")

    missing = run_all({})
    ok(all(not v[0] for v in missing.values()), "every criterion fails when every input is missing")
    print(f"\n{fails} failed")
    return 1 if fails else 0


# ------------------------------------------------------------------ main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stack", default=str(HERE / "stack.json"))
    ap.add_argument("--routes-file", default=str(HERE / "grantor-routes.json"))
    ap.add_argument("--results", default=str(HERE / "out" / "results.json"))
    ap.add_argument("--next-moves", default=str(HERE.parent / "loop" / "NEXT-MOVES.md"))
    ap.add_argument("--counsel-queue", default=str(HERE / "counsel-queue.md"))
    ap.add_argument("--benchmarks", default=str(HERE / "benchmarks-tax.json"))
    ap.add_argument("--scorecard-md", default=str(HERE / "SCORECARD.md"))
    ap.add_argument("--all-green", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    ctx = {
        "stack": read_json(a.stack),
        "routes": read_json(a.routes_file),
        "results": read_json(a.results),
        "next_moves": read_text(a.next_moves),
        "queue": read_text(a.counsel_queue),
        "bench": read_json(a.benchmarks),
        "scorecard_md": read_text(a.scorecard_md),
    }
    res = run_all(ctx)
    n = 0
    for cid in IDS:
        passed, reason = res[cid]
        n += bool(passed)
        print(f"{'PASS' if passed else 'FAIL'} {cid} {NAMES[cid]}: {reason}")
    print(f"Scorecard: {n} of 7 pass")
    return 1 if a.all_green and n < 7 else 0


if __name__ == "__main__":
    sys.exit(main())
