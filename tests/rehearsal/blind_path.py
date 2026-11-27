#!/usr/bin/env python3
"""Blind-goal adversarial path: the builder walks toward a goal it cannot see
the answer to, and every step is checked against the closest known-bad pattern
and the keystone claim. Only the grader holds the answer key, and it says pass
or fail, nothing else.

Spec: rehearsal/11-blind-goal-adversarial-path.md

  python3 tests/rehearsal/blind_path.py --check PATH.json      step checks on a builder's path
  python3 tests/rehearsal/blind_path.py --grade PATH.json      grade against the key (BLIND_KEY_JSON
                                                               or --key FILE); prints pass or fail only
  python3 tests/rehearsal/blind_path.py --privacy-scan         no counsel-private material in tracked files
  python3 tests/rehearsal/blind_path.py --selftest             the checks' own known-bad cases

Checks on every step (BG), on the counsel packet (CR), on the grader (GR) and
on the repository (PV). A missing fact field is an error, never a pass.

Analogy: a driving test with the route sealed in an envelope. The learner
(builder) drives; the instructor in the passenger seat (adversary) points at
the nearest way to crash and asks what is different; the map (keystone) says
whether each turn still heads to the same destination; only the examiner
(grader) opens the envelope, and only says pass or fail.

SYNTHETIC. Design and education, not legal or tax advice.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LIB = HERE / "blind-path" / "adversaries.json"
COMMIT = HERE / "blind-path" / "commitments.json"
LOG = HERE / "blind-path" / "heldout-log.csv"
DEMO = ROOT / "rehearsal" / "synthetic" / "paths" / "demo-foundation-pay.json"

VERDICTS = {"supports", "blocks", "silent", "unresolved"}
KEY_KINDS = {"statute": "key", "reg": "key", "case": "key", "rev_rul": "key",
             "plr": "weak", "counsel": "counsel", "none": "none"}
# Words that mean "this is the answer key" anywhere in what the builder holds.
KEY_WORDS = {"expected", "expectedverdict", "expected_verdict", "answer_key", "salt", "commitment",
             "key_verdict", "heldout_verdict"}
# Markers that mean "counsel-private: never in the public repo".
PRIVATE_MARKERS = ["PRIVILEGED AND CONFIDENTIAL", "ATTORNEY-CLIENT PRIVILEGED", "COUNSEL-PRIVATE",
                   "ATTORNEY WORK PRODUCT"]
EXCEPTION_OK = {"none", "credit_in_interest_free"}


def load_lib(path=LIB) -> dict:
    return json.loads(Path(path).read_text())


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def commit_of(case: str, verdict: str, salt: str) -> str:
    return sha(f"{case}|{verdict}|{salt}")


def facts_hash(path: dict) -> str:
    return sha(json.dumps([s["facts"] for s in path["steps"]], sort_keys=True))


# ------------------------------------------------------------------ BG checks

def walk(obj, out, where=""):
    """Every key and string in the builder's file, for the one-way check."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.append((f"{where}.{k}", str(k)))
            walk(v, out, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, out, f"{where}[{i}]")
    elif isinstance(obj, str):
        out.append((where, obj))


def need(path: dict, lib: dict):
    for k in ["id", "design_version", "goal_id", "goal", "keystone_claim", "builder_inputs", "steps", "answer"]:
        if k not in path:
            raise KeyError(f"{path.get('id', '?')}: missing {k} (fail closed)")
    for s in path["steps"]:
        for k in ["id", "facts", "adversary", "keystone", "key_source"]:
            if k not in s:
                raise KeyError(f"{path['id']}/{s.get('id', '?')}: missing {k} (fail closed)")
        missing = [f for f in lib["facts"] if f not in s["facts"]]
        if missing:
            raise KeyError(f"{path['id']}/{s['id']}: fact field(s) {missing} not stated (fail closed)")


def score(facts: dict, sig: dict) -> tuple[float, bool]:
    """(share of the signature the step matches, whether an unknown helped).
    An unknown fact counts as a match: it could be the bad value."""
    hit, unknown = 0, False
    for f, bad in sig.items():
        v = facts.get(f)
        if v is None:
            hit, unknown = hit + 1, True
        elif v == bad:
            hit += 1
    return hit / len(sig), unknown


def check_step(step: dict, path: dict, lib: dict) -> list[tuple[str, str, str]]:
    out = []
    facts, adv = step["facts"], step["adversary"]
    pats = {p["id"]: p for p in lib["patterns"]}
    scored = {pid: score(facts, p["signature"]) for pid, p in pats.items()}
    best = max(v[0] for v in scored.values())

    # BG1 an adversary is named, from the library.
    named = adv.get("nearest")
    out.append(("BG1", "pass" if named in pats else "fail", f"Adversary named from the library ({named})"))
    if named not in pats:
        return out
    pat = pats[named]

    # BG2 it is the closest bad pattern, not a strawman.
    ok2 = scored[named][0] >= best
    closest = sorted(pid for pid, v in scored.items() if v[0] >= best)
    out.append(("BG2", "pass" if ok2 else "fail",
                f"Named pattern is the closest ({scored[named][0]:.2f}; closest {best:.2f}: {', '.join(closest)})"))

    # BG3 the difference is in substance: a fact field of that pattern, really different.
    d = adv.get("difference") or {}
    fld = d.get("field")
    ok3 = (fld in pat["signature"] and fld not in lib["label_fields"] and fld in facts
           and facts[fld] is not None and facts[fld] == d.get("step_value")
           and d.get("pattern_value") == pat["signature"][fld] and facts[fld] != pat["signature"][fld])
    out.append(("BG3", "pass" if ok3 else "fail",
                f"Difference is a fact in the pattern's signature that really differs ({fld})"))

    # BG4 the strongest authority against the move is engaged, and why it doesn't control.
    why = (adv.get("why_not_controlling") or "").split()
    ok4 = adv.get("contrary_authority") in pat["authority"] and len(why) >= 8
    out.append(("BG4", "pass" if ok4 else "fail",
                f"Contrary authority is the pattern's own ({adv.get('contrary_authority')}), with a reason"))

    # BG5 no pattern is matched whole. Known facts matching a whole signature fail;
    # a whole match that needs an unknown is amber (state the fact).
    whole = [pid for pid, v in scored.items() if v[0] >= 1.0]
    known_whole = [pid for pid in whole if not scored[pid][1]]
    v5 = "fail" if known_whole else ("amber" if whole else "pass")
    out.append(("BG5", v5, "No known-bad pattern matched whole" + (f" ({', '.join(whole)})" if whole else "")))

    # BG6 keystone: one claim held through the trace; per-link verdict; and the
    # verdict agrees with the facts (a foundation deal with an insider blocks).
    ks = step["keystone"]
    same = ks.get("claim") == path["keystone_claim"] and path["keystone_claim"] in lib["keystone_claims"]
    verdict = ks.get("verdict")
    insider = facts["foundation_party"] is not False and (
        facts["counterparty_disqualified"] is not False or facts["passes_to_disqualified"] is not False)
    excepted = (facts["deal_kind"] in EXCEPTION_OK and facts["passes_to_disqualified"] is False) or (
        facts["deal_kind"] == "compensation" and facts["compensation_reasonable_necessary"] is True
        and facts["passes_to_disqualified"] is False)
    must_block = insider and not excepted
    if not same or verdict not in VERDICTS:
        v6, lab6 = "fail", "Keystone claim changed mid-trace or verdict not one of supports/blocks/silent/unresolved"
    elif must_block and verdict == "supports":
        v6, lab6 = "fail", "Keystone verdict says supports, but the facts move foundation value to an insider"
    elif verdict == "blocks":
        v6, lab6 = "fail", "Keystone blocks this link"
    elif verdict in ("silent", "unresolved"):
        v6, lab6 = "amber", f"Keystone {verdict} on this link (counsel queue)"
    else:
        v6, lab6 = "pass", "Keystone supports this link"
    out.append(("BG6", v6, lab6))

    # BG7 where the step's outside answer comes from; no key means ASSUMPTION.
    src = step["key_source"]
    kind = KEY_KINDS.get(src.get("kind"))
    label = step.get("mark", "")
    if kind is None:
        v7, lab7 = "fail", f"Key source kind unknown ({src.get('kind')})"
    elif kind == "key":
        v7, lab7 = ("pass", f"Outside answer: {src.get('cite')}") if src.get("cite") else ("fail", "Key source has no cite")
    elif kind == "weak":
        v7 = "amber" if label == "WEAK AUTHORITY" else "fail"
        lab7 = "Private letter ruling: weaker authority, must be marked WEAK AUTHORITY"
    elif kind == "counsel" and src.get("signed_off"):
        v7, lab7 = "pass", "Counsel signed off on this step"
    else:
        v7 = "amber" if label == "ASSUMPTION" else "fail"
        lab7 = "No outside answer for this step: must be marked ASSUMPTION and queued for counsel"
    out.append(("BG7", v7, lab7))
    return out


def check_path(path: dict, lib: dict) -> dict:
    need(path, lib)
    res = {"path": path["id"], "steps": {}, "path_checks": []}

    # BG0 one-way flow: nothing in the builder's file, or its inputs, is answer-key material.
    seen: list = []
    walk(path, seen)
    leaks = [w for w, s in seen if s.lower().replace("-", "_") in KEY_WORDS]
    bad_in = [f for f in path["builder_inputs"] if "blind-path/commitments" in f or "heldout" in f.lower()
              or f.endswith("key.json")]
    res["path_checks"].append(("BG0", "fail" if leaks or bad_in else "pass",
                               "Answer flows one way: no key material in the builder's file or inputs"
                               + (f" (found {leaks[:3] + bad_in})" if leaks or bad_in else "")))
    for s in path["steps"]:
        res["steps"][s["id"]] = check_step(s, path, lib)

    # BG8 rename invariance: scramble every label field; every verdict must stay the same.
    scr = copy.deepcopy(path)
    for i, s in enumerate(scr["steps"]):
        for f in lib["label_fields"]:
            if f in s:
                s[f] = f"x{i}{f}"
    again = {s["id"]: check_step(s, scr, lib) for s in scr["steps"]}
    same = all([c[:2] for c in again[k]] == [c[:2] for c in v] for k, v in res["steps"].items())
    res["path_checks"].append(("BG8", "pass" if same else "fail", "Renaming every label changes no verdict"))

    # CR counsel packet, when there is one.
    if path.get("counsel"):
        res["path_checks"] += check_counsel(path, lib)

    allv = [c[1] for c in res["path_checks"]] + [c[1] for v in res["steps"].values() for c in v]
    res["verdict"] = "fail" if "fail" in allv else ("amber" if "amber" in allv else "pass")
    return res


# ------------------------------------------------------------------ CR counsel lane

def check_counsel(path: dict, lib: dict) -> list[tuple[str, str, str]]:
    """Reliance on professional advice (6664(c)(1); Reg. 1.6664-4(b), (c); the
    three-part test in Neonatology) and the privilege boundary."""
    c = path["counsel"]
    out = []
    # PV0 the packet record points to the private folder, never the public repo.
    loc = c.get("location", "")
    out.append(("PV0", "pass" if loc.startswith("private:") else "fail",
                "Counsel packet and advice are kept in the private folder, not the public repo"))
    if c.get("status") != "advised":
        out.append(("CR0", "amber", "No advice yet: nothing to rely on (counsel queue)"))
        return out
    # CR1 competence: a licensed professional, basis written down.
    ok1 = c.get("counsel_role") in {"licensed_attorney", "licensed_cpa", "enrolled_agent"} and bool(c.get("competence_basis"))
    out.append(("CR1", "pass" if ok1 else "fail", "Adviser is a licensed professional with the basis recorded"))
    # CR2 full disclosure: every fact field of every step went to counsel, unchanged since.
    given = set(c.get("facts_given", []))
    wanted = {f"{s['id']}.{f}" for s in path["steps"] for f in lib["facts"]} | set(path.get("material_facts", []))
    missing = sorted(wanted - given)
    changed = c.get("facts_given_sha256") != facts_hash(path)
    v2 = "fail" if missing or changed else "pass"
    lab2 = "Full disclosure: every material fact went to counsel, and none changed since"
    if missing:
        lab2 += f" (left out: {', '.join(missing[:4])}{'...' if len(missing) > 4 else ''})"
    if changed:
        lab2 += " (facts changed after the packet was given)"
    out.append(("CR2", v2, lab2))
    # CR3 the advice's assumptions are true on the facts.
    flat = {f"{s['id']}.{k}": v for s in path["steps"] for k, v in s["facts"].items()}
    wrong = [k for k, v in c.get("advice_assumptions", {}).items() if flat.get(k, "?") != v]
    out.append(("CR3", "fail" if wrong else "pass",
                "Advice rests on no assumption the facts contradict" + (f" ({', '.join(wrong)})" if wrong else "")))
    # CR4 actual reliance, in order: given, then advised, then acted.
    try:
        g, a, t = (date.fromisoformat(c[k]) for k in ("given_on", "advice_on", "acted_on"))
        ok4 = g <= a <= t
    except (KeyError, TypeError, ValueError):
        ok4 = False
    out.append(("CR4", "pass" if ok4 else "fail", "Reliance in order: facts given, advice received, then acted on"))
    return out


# ------------------------------------------------------------------ GR grader

def emit(path_id: str, result: str) -> dict:
    """The grader's only output. Answer flows one way: no reason, no hint."""
    out = {"path": path_id, "result": result}
    assert set(out) == {"path", "result"} and result in ("pass", "fail")
    return out


def grade(path: dict, key: list[dict], commitments: dict, lib: dict, heldout_log: list | None = None,
          budget: int | None = None) -> dict:
    # GR1 the key is the one committed to before the run: no answer moved to fit.
    for k in key:
        want = commitments["cases"].get(k["case"])
        if want is None or commit_of(k["case"], k["verdict"], k["salt"]) != want:
            raise ValueError(f"GR1: key case {k['case']} does not match its commitment")
    row = next((k for k in key if k["case"] == path["goal_id"]), None)
    if row is None:
        raise ValueError(f"GR1: no key for {path['goal_id']}")
    # GR3 the held-out set is graded rarely: a budget per design version, logged.
    if row.get("set") == "heldout":
        log = heldout_log if heldout_log is not None else []
        used = sum(1 for r in log if r["design_version"] == path["design_version"])
        cap = budget if budget is not None else commitments.get("budget_per_design_version", 1)
        if used >= cap:
            raise PermissionError(f"GR3: held-out budget spent for design version {path['design_version']} ({used}/{cap})")
    # GR4 a right answer on a path that fails a step is still a fail: the path must be traceable.
    checked = check_path(path, lib)
    ok = checked["verdict"] != "fail" and path["answer"].get("verdict") == row["verdict"]
    result = emit(path["id"], "pass" if ok else "fail")
    if row.get("set") == "heldout" and heldout_log is not None:
        heldout_log.append({"design_version": path["design_version"], "case": row["case"],
                            "graded_at": date.today().isoformat(), "result": result["result"]})
    return result


# ------------------------------------------------------------------ PV privacy scan

def privacy_scan(files: dict[str, str]) -> list[str]:
    """Tracked files that carry a counsel-private marker. The public repo, like
    any AI log, is not privileged; counsel material belongs in the private folder."""
    # These files name the markers to define or plant them; they hold no counsel material.
    me = {"tests/rehearsal/blind_path.py", "rehearsal/11-blind-goal-adversarial-path.md", ".github/mutation/checks.json"}
    return sorted(f for f, text in files.items() if f not in me and any(m in text for m in PRIVATE_MARKERS))


def tracked_texts() -> dict[str, str]:
    r = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True)
    out = {}
    for f in [p for p in r.stdout.split("\0") if p]:
        try:
            out[f] = (ROOT / f).read_text(errors="replace")
        except (OSError, UnicodeDecodeError, IsADirectoryError):
            pass
    return out


# ------------------------------------------------------------------ selftest

def selftest() -> int:
    lib = load_lib()
    demo = json.loads(DEMO.read_text())
    fails = []

    def expect(name, fn, code, verdict="fail"):
        try:
            got = fn()
        except (KeyError, ValueError, PermissionError, AssertionError) as e:
            ok = code in str(e) or code == "error"
            print(f"  {'ok ' if ok else 'BAD'} {name}: raised ({str(e)[:90]})")
            if not ok:
                fails.append(name)
            return
        if isinstance(got, dict) and "result" in got:
            ok = got["result"] == verdict
            print(f"  {'ok ' if ok else 'BAD'} {name}: grader says {got['result']}")
        else:
            checks = got["path_checks"] + [c for v in got["steps"].values() for c in v]
            hit = [c for c in checks if c[0] == code and c[1] == verdict]
            ok = bool(hit)
            print(f"  {'ok ' if ok else 'BAD'} {name}: {code} {verdict if ok else 'not ' + verdict}")
        if not ok:
            fails.append(name)

    def mut(fn):
        p = copy.deepcopy(demo)
        fn(p)
        return p

    base = check_path(demo, lib)
    print(f"demo path {demo['id']}: {base['verdict']}")
    if base["verdict"] == "fail":
        fails.append("demo path must not fail")
        for k, v in base["steps"].items():
            print("   ", k, [c[:2] for c in v])
        print("   ", base["path_checks"])

    s0 = lambda p: p["steps"][0]  # noqa: E731
    print("known-bad cases (each must go red for the named reason):")
    expect("KB1 builder file carries the answer", lambda: check_path(mut(lambda p: p["answer"].update(expectedVerdict="allow")), lib), "BG0")
    expect("KB2 builder was handed the held-out file", lambda: check_path(mut(lambda p: p["builder_inputs"].append("tests/rehearsal/blind-path/heldout-key.json")), lib), "BG0")
    expect("KB3 strawman adversary instead of the closest", lambda: check_path(mut(lambda p: s0(p)["adversary"].update(nearest="ADV-RESIDENCE-COSTS")), lib), "BG2")
    expect("KB4 difference named on a label, not a fact", lambda: check_path(mut(lambda p: s0(p)["adversary"].update(difference={"field": "name", "step_value": "Program Pay", "pattern_value": "Salary"})), lib), "BG3")
    expect("KB5 difference claims a fact the step doesn't have", lambda: check_path(mut(lambda p: s0(p)["facts"].update(compensation_reasonable_necessary=False)), lib), "BG3")
    expect("KB6 lease to an insider matches 4941(d)(1)(A) whole", lambda: check_path(mut(lambda p: s0(p)["facts"].update(deal_kind="property")), lib), "BG5")
    expect("KB7 step carries the abandoned trust text forward", lambda: check_path(mut(lambda p: p["steps"][2]["facts"].update(adopts_abandoned_trust_text=True)), lib), "BG5")
    expect("KB8 trustee is a relative who follows directions", lambda: check_path(mut(lambda p: p["steps"][2]["facts"].update(trustee_related_or_promoter=True, trustee_follows_owner_directions=True)), lib), "BG5")
    expect("KB9 tax-only step (7701(o))", lambda: check_path(mut(lambda p: p["steps"][2]["facts"].update(federal_tax_benefit=True, nontax_effect=False)), lib), "BG5")
    expect("KB10 contrary authority dodged", lambda: check_path(mut(lambda p: s0(p)["adversary"].update(contrary_authority="IRC 162(a)")), lib), "BG4")
    expect("KB11 keystone claim swapped mid-trace", lambda: check_path(mut(lambda p: p["steps"][1]["keystone"].update(claim="KS-OTHER")), lib), "BG6")
    expect("KB12 keystone says supports on unreasonable pay to an insider",
           lambda: check_path(mut(lambda p: s0(p)["facts"].update(compensation_reasonable_necessary=False) or s0(p)["adversary"].update(nearest="ADV-4941-PAY", difference={"field": "deal_kind", "step_value": "compensation", "pattern_value": "compensation"})), lib), "BG6")
    expect("KB13 no outside answer and no ASSUMPTION label", lambda: check_path(mut(lambda p: p["steps"][2].pop("mark")), lib), "BG7")
    expect("KB14 letter ruling used as a full key", lambda: check_path(mut(lambda p: s0(p).update(key_source={"kind": "plr", "cite": "PLR (synthetic)"})), lib), "BG7")
    expect("KB15 a fact field left unstated", lambda: check_path(mut(lambda p: s0(p)["facts"].pop("deal_kind")), lib), "fail closed")
    expect("KB16 counsel packet stored in the public repo", lambda: check_path(mut(lambda p: p["counsel"].update(location="rehearsal/packet.md")), lib), "PV0")

    advised = mut(lambda p: p["counsel"].update(
        status="advised", counsel_role="licensed_attorney", competence_basis="licensed tax attorney (synthetic)",
        facts_given=sorted({f"{s['id']}.{f}" for s in p["steps"] for f in lib["facts"]}),
        facts_given_sha256=facts_hash(p), advice_assumptions={"s1.compensation_reasonable_necessary": True},
        given_on="2027-01-04", advice_on="2027-01-20", acted_on="2027-02-01"))
    ok_adv = check_path(advised, lib)
    cr = [c for c in ok_adv["path_checks"] if c[0].startswith("CR")]
    good = all(c[1] == "pass" for c in cr) and len(cr) == 4
    print(f"  {'ok ' if good else 'BAD'} advised packet, full disclosure: {[c[:2] for c in cr]}")
    if not good:
        fails.append("advised packet must pass CR1-CR4")

    def adv(fn):
        p = copy.deepcopy(advised)
        fn(p)
        return p
    expect("KB17 a material fact left out of the packet", lambda: check_path(adv(lambda p: p["counsel"]["facts_given"].remove("s2.passes_to_disqualified")), lib), "CR2")
    expect("KB18 facts changed after counsel saw them", lambda: check_path(adv(lambda p: p["steps"][2]["facts"].update(related_party_flow=True)), lib), "CR2")
    expect("KB19 advice assumes a fact that is false", lambda: check_path(adv(lambda p: p["counsel"]["advice_assumptions"].update({"s3.terms_followed": False})), lib), "CR3")
    expect("KB20 acted before the advice came", lambda: check_path(adv(lambda p: p["counsel"].update(acted_on="2027-01-10")), lib), "CR4")
    expect("KB21 adviser not a licensed professional", lambda: check_path(adv(lambda p: p["counsel"].update(counsel_role="ai_model")), lib), "CR1")

    # Grader.
    salt = "selftest-salt-not-a-real-key"
    key = [{"case": demo["goal_id"], "verdict": "allow", "salt": salt, "set": "practice"},
           {"case": "HO-1", "verdict": "allow", "salt": salt + "2", "set": "heldout"}]
    com = {"budget_per_design_version": 1, "cases": {k["case"]: commit_of(k["case"], k["verdict"], k["salt"]) for k in key}}
    g = grade(demo, key, com, lib)
    print(f"  {'ok ' if g == {'path': demo['id'], 'result': 'pass'} else 'BAD'} grader on the demo path: {g}")
    if g != {"path": demo["id"], "result": "pass"}:
        fails.append("grader must pass the demo path, with path and result only")
    # The builder answered deny; someone moves the key to deny to make it pass. Only the commitment stops it.
    expect("KB22 key moved after it was committed", lambda: grade(mut(lambda p: p["answer"].update(verdict="deny")),
           [dict(key[0], verdict="deny")] + key[1:], com, lib), "GR1")
    expect("KB23 right answer, but a step fails", lambda: grade(mut(lambda p: s0(p)["facts"].update(deal_kind="property")), key, com, lib), "GR4")
    expect("KB24 wrong answer on a clean path", lambda: grade(mut(lambda p: p["answer"].update(verdict="deny")), key, com, lib), "GR4")
    ho = mut(lambda p: p.update(goal_id="HO-1"))
    log: list = []
    first = grade(ho, key, com, lib, heldout_log=log)
    print(f"  {'ok ' if first['result'] == 'pass' and len(log) == 1 else 'BAD'} held-out graded once, logged: {first}")
    if not (first["result"] == "pass" and len(log) == 1):
        fails.append("held-out first grade must pass and log")
    expect("KB25 held-out graded twice for one design version", lambda: grade(ho, key, com, lib, heldout_log=log), "GR3")
    expect("KB26 grader leaks a reason", lambda: emit(demo["id"], "pass because K6") , "error")

    # Privacy scan.
    planted = {"rehearsal/notes.md": "COUNSEL-PRIVATE: memo on the trust", "README.md": "public"}
    hit = privacy_scan(planted)
    print(f"  {'ok ' if hit == ['rehearsal/notes.md'] else 'BAD'} KB27 counsel-private memo in the repo: {hit}")
    if hit != ["rehearsal/notes.md"]:
        fails.append("KB27")

    if fails:
        print(f"\nFAIL: {len(fails)} known-bad case(s) not caught: {fails}")
        return 1
    print("\nAll known-bad cases caught.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", nargs="*")
    ap.add_argument("--grade")
    ap.add_argument("--key")
    ap.add_argument("--heldout-log", default=str(LOG))
    ap.add_argument("--privacy-scan", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    lib = load_lib()
    if a.privacy_scan:
        hits = privacy_scan(tracked_texts())
        for h in hits:
            print(f"PV1 fail: {h} carries a counsel-private marker; move it to the private folder")
        print("PV1 pass: no counsel-private marker in tracked files" if not hits else "")
        return 1 if hits else 0
    if a.check is not None:
        worst = 0
        for f in a.check or [str(DEMO)]:
            r = check_path(json.loads(Path(f).read_text()), lib)
            print(f"{r['path']}: {r['verdict']}")
            for c in r["path_checks"]:
                print(f"  {c[0]} {c[1]:5} {c[2]}")
            for sid, cs in r["steps"].items():
                for c in cs:
                    print(f"  {sid} {c[0]} {c[1]:5} {c[2]}")
            worst = max(worst, 1 if r["verdict"] == "fail" else 0)
        return worst
    if a.grade:
        raw = Path(a.key).read_text() if a.key else os.environ.get("BLIND_KEY_JSON")
        if not raw:
            print("GR0: no key configured (BLIND_KEY_JSON or --key); nothing graded")
            return 2
        log_rows = list(csv.DictReader(open(a.heldout_log))) if Path(a.heldout_log).exists() else []
        n = len(log_rows)
        r = grade(json.loads(Path(a.grade).read_text()), json.loads(raw), json.loads(COMMIT.read_text()), lib, log_rows)
        if len(log_rows) > n:
            with open(a.heldout_log, "a", newline="") as fh:
                csv.DictWriter(fh, ["design_version", "case", "graded_at", "result"]).writerow(log_rows[-1])
        print(json.dumps(r))
        return 0 if r["result"] == "pass" else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
