#!/usr/bin/env python3
"""Lawyer-ready packet scorecard: the relay's finish line (Dalaun's lane).

The relay runs until every criterion here passes. This file sits in Dalaun's
lane (tests/, see .github/CODEOWNERS), so the agents that write the packet can
never change how the packet is graded. The packet itself is agent-lane work,
written under rehearsal/synthetic/packet/. Plain-words version:
rehearsal/loop/PACKET-SCORECARD.md.

  python3 tests/rehearsal/packet_scorecard.py --results FILE          one line per criterion
  python3 tests/rehearsal/packet_scorecard.py --results FILE --all-green   exit 1 unless all pass
  python3 tests/rehearsal/packet_scorecard.py --selftest              a passing fixture, then one break per criterion

--results is the engine's output (rehearsal_run.py --json FILE), needed by PK4.

Criteria:
  PK1 researched      every counsel-queue question has packet/research/Q<n>.md with a
                      draft answer, a confidence label and at least two primary cites,
                      one of them a statute or regulation, each marked as read on a date
  PK2 framed          every question labelled likely or open says what the lawyer decides
  PK3 labelled        every packet file says it is research for counsel review, not legal advice
  PK4 sized           both break-even scenarios are re-run as a sensitivity family
                      (at least 3 sizes, spanning 0.75x to 1.5x), a realistic case is named
                      with a cited basis, and every table row matches the engine's output
  PK5 memo            one structure memo with the four sections, the three layers, and every
                      likely or open question listed for the lawyer
  PK6 packet          one packet file that links the memo, the sensitivity table and every
                      research file, and reads in an hour (15,000 words in all)

SYNTHETIC. Research for counsel review, not legal or tax advice.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
IDS = ["PK1", "PK2", "PK3", "PK4", "PK5", "PK6"]
LABEL = "Research for counsel review, not legal advice."
CONFIDENCE = {"settled", "likely", "open"}
PRIMARY_HOSTS = (
    "law.cornell.edu", "ecfr.gov", "uscode.house.gov", "govinfo.gov", "federalregister.gov",
    "irs.gov", "ilga.gov", "illinoiscourts.gov", "supremecourt.gov", "sba.gov", "treasury.gov",
)
LAW_PATTERNS = (
    r"law\.cornell\.edu/uscode", r"law\.cornell\.edu/cfr", r"ecfr\.gov", r"uscode\.house\.gov",
    r"govinfo\.gov", r"federalregister\.gov", r"ilga\.gov",
)
BREAK_EVEN_FAMILIES = ("asset_sized", "asset_sized_pipeline")
MEMO_SECTIONS = ("## the structure", "## decisions only dalaun makes", "## risks", "## what a lawyer must decide")
MEMO_LAYERS = ("business trust", "family trust", "foundation", "non-grantor")
MAX_WORDS = 15000
MEMO_MAX_WORDS = 3000
READ_RE = re.compile(r"\(read (\d{4}-\d{2}-\d{2})\)")
URL_RE = re.compile(r"https://[^\s)>\]]+")


def paths(root: Path) -> dict:
    syn = root / "rehearsal" / "synthetic"
    pk = syn / "packet"
    return {
        "queue": syn / "counsel-queue.md", "scenarios": syn / "scenarios.json",
        "packet": pk, "research": pk / "research", "memo": pk / "STRUCTURE-MEMO.md",
        "sens": pk / "SENSITIVITY.md", "main": pk / "LAWYER-PACKET.md",
    }


def read(p: Path) -> str:
    try:
        return p.read_text()
    except OSError:
        return ""


def words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def field(text: str, name: str) -> str:
    m = re.search(rf"^\s*-\s*{re.escape(name)}:\s*(.*)$", text, re.M | re.I)
    return m.group(1).strip() if m else ""


def queue_ids(p) -> list[int]:
    return sorted({int(n) for n in re.findall(r"^## Q(\d+)\.", read(p["queue"]), re.M)})


def cite_lines(text: str) -> list[str]:
    m = re.search(r"^\s*-\s*Cites:\s*$(.*?)(?=^\s*-\s*\w[\w ]*:|\Z)", text, re.M | re.S | re.I)
    if not m:
        return []
    return [ln.strip() for ln in m.group(1).splitlines() if ln.strip().startswith("-")]


def host_ok(url: str) -> bool:
    host = re.sub(r"^https://", "", url).split("/")[0].lower()
    return any(host == h or host.endswith("." + h) for h in PRIMARY_HOSTS)


def research(p) -> dict[int, dict]:
    out = {}
    for n in queue_ids(p):
        f = p["research"] / f"Q{n}.md"
        text = read(f)
        out[n] = {"file": f, "text": text, "answer": field(text, "Draft answer"),
                  "confidence": field(text, "Confidence").lower().strip(" ."),
                  "decides": field(text, "Lawyer decides"), "cites": cite_lines(text)}
    return out


def research_problem(r: dict) -> str:
    if not r["text"]:
        return "no research file"
    if words(r["answer"]) < 25:
        return "draft answer missing or under 25 words"
    if r["confidence"] not in CONFIDENCE:
        return "confidence is not settled, likely or open"
    good, law = 0, 0
    for c in r["cites"]:
        urls = URL_RE.findall(c)
        if not urls or not READ_RE.search(c) or "not read" in c.lower():
            return f"cite without a URL and a read date: {c[:60]}"
        if host_ok(urls[0]):
            good += 1
            law += any(re.search(pat, urls[0]) for pat in LAW_PATTERNS)
    if good < 2:
        return f"{good} primary cites, needs 2"
    if law < 1:
        return "no statute or regulation cite"
    return ""


# ------------------------------------------------------------------ criteria

def pk1(p, _res):
    rs = research(p)
    if not rs:
        return False, "no counsel-queue questions found"
    bad = {n: research_problem(r) for n, r in rs.items()}
    bad = {n: why for n, why in bad.items() if why}
    done = len(rs) - len(bad)
    if bad:
        n = min(bad)
        return False, f"{done} of {len(rs)} researched; Q{n}: {bad[n]}"
    return True, f"all {len(rs)} questions researched with primary cites"


def pk2(p, _res):
    rs = research(p)
    if not rs or any(not r["text"] for r in rs.values()):
        return False, "waits on PK1: not every question has a research file"
    need = [n for n, r in rs.items() if r["confidence"] in ("likely", "open")]
    miss = [n for n in need if words(rs[n]["decides"]) < 5]
    if miss:
        return False, f"Q{miss[0]} is {rs[miss[0]]['confidence']} but says nothing a lawyer decides"
    return True, f"{len(need)} likely or open questions each name what the lawyer decides"


def packet_files(p) -> list[Path]:
    fs = [p["memo"], p["sens"], p["main"]]
    fs += [p["research"] / f"Q{n}.md" for n in queue_ids(p)]
    return fs


def pk3(p, _res):
    missing = [f for f in packet_files(p) if LABEL not in read(f)]
    if missing:
        return False, f"{len(missing)} packet files lack the label, first {missing[0].relative_to(p['packet'].parents[2])}"
    return True, "every packet file carries the research-not-advice label"


def asset_income(s: dict):
    for ln in s.get("extra_lines", []):
        if ln.get("id") == "asset_net_income" and isinstance(ln.get("annual"), (int, float)):
            return float(ln["annual"])
    return None


def pk4(p, res):
    try:
        scen = {s["id"]: s for s in json.loads(read(p["scenarios"]))["scenarios"]}
    except (ValueError, KeyError, TypeError):
        return False, "scenarios.json unreadable"
    if res is None:
        return False, "no --results given"
    ran = {r["scenario"]: r for r in res.get("results", [])}
    sens = read(p["sens"])
    if not sens:
        return False, "no SENSITIVITY.md"
    rows = {}
    for m in re.finditer(r"^\|\s*([a-z0-9_]+)\s*\|\s*([a-z0-9_]+)\s*\|\s*([-\d,\.]+)\s*\|\s*([-\d,\.]+)\s*\|", sens, re.M):
        rows[m.group(1)] = (m.group(2), float(m.group(3).replace(",", "")), float(m.group(4).replace(",", "")))
    for base in BREAK_EVEN_FAMILIES:
        if base not in scen or asset_income(scen[base]) is None:
            return False, f"{base} missing from scenarios.json"
        b = asset_income(scen[base])
        fam = [sid for sid, s in scen.items() if sid == base or s.get("sensitivity_of") == base]
        incomes = [asset_income(scen[sid]) for sid in fam]
        if len(fam) < 3 or None in incomes:
            return False, f"{base}: {len(fam)} sizes, needs 3 with an asset_net_income line"
        if min(incomes) > 0.75 * b or max(incomes) < 1.5 * b:
            return False, f"{base}: sizes span {min(incomes):,.0f} to {max(incomes):,.0f}, needs 0.75x to 1.5x of {b:,.0f}"
        for sid in fam:
            if sid not in ran:
                return False, f"{sid} is not in the engine results"
            if sid not in rows:
                return False, f"{sid} has no row in SENSITIVITY.md"
            ver, inc, diff = rows[sid]
            v = ran[sid].get("versions", {}).get(ver)
            if v is None:
                return False, f"{sid}: version {ver} not in the engine results"
            if abs(inc - asset_income(scen[sid])) > 1 or abs(diff - v.get("score_vs_A", 1e18)) > 1:
                return False, f"{sid}: table row does not match the engine ({ver} B minus A is {v.get('score_vs_A')})"
        m = re.search(rf"^\s*-\s*Realistic case \({re.escape(base)}\):\s*([a-z0-9_]+)\b(.*)$", sens, re.M)
        if not m:
            return False, f"{base}: no 'Realistic case ({base}):' line"
        rid, basis = m.group(1), m.group(2)
        if rid not in fam or rid == base:
            return False, f"{base}: realistic case {rid} is not a sized variant in its family"
        if not URL_RE.search(basis) or not READ_RE.search(basis):
            return False, f"{base}: realistic case has no cited basis with a read date"
    return True, "both break-even scenarios re-run across sizes, realistic cases cited, rows match the engine"


def pk5(p, _res):
    memo = read(p["memo"])
    if not memo:
        return False, "no STRUCTURE-MEMO.md"
    low = memo.lower()
    for s in MEMO_SECTIONS:
        if s not in low:
            return False, f"memo lacks the section '{s[3:]}'"
    for layer in MEMO_LAYERS:
        if layer not in low:
            return False, f"memo never names '{layer}'"
    if words(memo) > MEMO_MAX_WORDS:
        return False, f"memo is {words(memo)} words, cap {MEMO_MAX_WORDS}"
    section = low.split("## what a lawyer must decide", 1)[1].split("\n## ", 1)[0]
    rs = research(p)
    need = [n for n, r in rs.items() if r["confidence"] in ("likely", "open")]
    miss = [n for n in need if not re.search(rf"\bq{n}\b", section)]
    if miss:
        return False, f"'What a lawyer must decide' does not list Q{miss[0]}"
    return True, "memo has the four sections, the three layers and every open question"


def pk6(p, _res):
    main = read(p["main"])
    if not main:
        return False, "no LAWYER-PACKET.md"
    if "SYNTHETIC" not in main:
        return False, "packet does not say its numbers are synthetic"
    links = set(re.findall(r"\]\(([^)#\s]+)", main))
    need = ["STRUCTURE-MEMO.md", "SENSITIVITY.md"] + [f"research/Q{n}.md" for n in queue_ids(p)]
    miss = [n for n in need if n not in links and f"./{n}" not in links]
    if miss:
        return False, f"packet does not link {miss[0]}"
    total = sum(words(read(f)) for f in packet_files(p))
    if total > MAX_WORDS:
        return False, f"packet is {total:,} words in all, cap {MAX_WORDS:,} (about an hour's reading)"
    return True, f"one packet, {total:,} words, links every part"


CHECKS = {"PK1": pk1, "PK2": pk2, "PK3": pk3, "PK4": pk4, "PK5": pk5, "PK6": pk6}
NAMES = {"PK1": "researched", "PK2": "framed", "PK3": "labelled", "PK4": "sized", "PK5": "memo", "PK6": "packet"}


def grade(root: Path, res):
    p = paths(root)
    return {cid: CHECKS[cid](p, res) for cid in IDS}


def progress(root: Path) -> str:
    rs = research(paths(root))
    done = sum(1 for r in rs.values() if not research_problem(r))
    return f"research {done} of {len(rs)} questions"


def report(out: dict, root: Path) -> int:
    for cid in IDS:
        ok, why = out[cid]
        print(f"{'PASS' if ok else 'FAIL'} {cid} {NAMES[cid]}: {why}")
    n = sum(ok for ok, _ in out.values())
    print(f"Packet: {n} of {len(IDS)} pass; {progress(root)}")
    return n


# ------------------------------------------------------------------ selftest

def _fixture(tmp: Path):
    p = paths(tmp)
    p["research"].mkdir(parents=True)
    p["queue"].write_text("# Counsel queue\n\n## Q1. One?\n\n- Key: `a`\n\n## Q2. Two?\n\n- Key: `b`\n")
    cites = ("- Cites:\n"
             "  - IRC 674(c), https://www.law.cornell.edu/uscode/text/26/674 (read 2026-11-25)\n"
             "  - Treas. Reg. 1.674(d)-2, https://www.ecfr.gov/current/title-26/section-1.674(d)-2 (read 2026-11-25)\n")
    answer = "- Draft answer: " + " ".join(["word"] * 30) + "\n"
    p["research"].joinpath("Q1.md").write_text(f"# Q1\n\n{LABEL}\n\n{answer}- Confidence: settled\n{cites}")
    p["research"].joinpath("Q2.md").write_text(
        f"# Q2\n\n{LABEL}\n\n{answer}- Confidence: open\n- Lawyer decides: whether the advisor counts as a trustee\n{cites}")
    fam = []
    for base, b in (("asset_sized", 150000), ("asset_sized_pipeline", 350000)):
        for sid, x in ((base, b), (base + "_lo", 0.75 * b), (base + "_hi", 1.5 * b)):
            s = {"id": sid, "extra_lines": [{"id": "asset_net_income", "annual": x}]}
            if sid != base:
                s["sensitivity_of"] = base
            fam.append(s)
    p["scenarios"].write_text(json.dumps({"scenarios": fam}))
    res = {"results": [{"scenario": s["id"], "versions": {"steward_r2": {"score_vs_A": 100 + i}}} for i, s in enumerate(fam)]}
    rows = "\n".join(f"| {s['id']} | steward_r2 | {asset_income(s):,.0f} | {100 + i} |" for i, s in enumerate(fam))
    p["sens"].write_text(
        f"# Sensitivity\n\n{LABEL}\n\n| scenario | version | asset net income | B minus A |\n|---|---|---|---|\n{rows}\n\n"
        "- Realistic case (asset_sized): asset_sized_lo, cap rates https://example.com/caps (read 2026-11-25)\n"
        "- Realistic case (asset_sized_pipeline): asset_sized_pipeline_hi, SDE https://example.com/sde (read 2026-11-25)\n")
    p["memo"].write_text(
        f"# Memo\n\n{LABEL}\n\n## The structure\n\nbusiness trust, Family Trust, Foundation, non-grantor.\n\n"
        "## Decisions only Dalaun makes\n\nx\n\n## Risks\n\nx\n\n## What a lawyer must decide\n\n- Q2: the advisor.\n")
    p["main"].write_text(
        f"# Packet\n\nSYNTHETIC.\n\n{LABEL}\n\n[memo](STRUCTURE-MEMO.md) [table](SENSITIVITY.md) "
        "[Q1](research/Q1.md) [Q2](research/Q2.md)\n")
    return p, res


def _break(cid: str, p, res):
    if cid == "PK1":
        t = p["research"].joinpath("Q1.md").read_text().replace("(read 2026-11-25)", "(not read)", 1)
        p["research"].joinpath("Q1.md").write_text(t)
    elif cid == "PK2":
        t = p["research"].joinpath("Q2.md").read_text()
        p["research"].joinpath("Q2.md").write_text(re.sub(r"- Lawyer decides:.*\n", "", t))
    elif cid == "PK3":
        p["memo"].write_text(p["memo"].read_text().replace(LABEL, ""))
    elif cid == "PK4":
        p["sens"].write_text(p["sens"].read_text().replace("| 101 |", "| 9999 |"))
    elif cid == "PK5":
        p["memo"].write_text(p["memo"].read_text().replace("- Q2: the advisor.", "- the advisor."))
    elif cid == "PK6":
        p["main"].write_text(p["main"].read_text().replace("[Q2](research/Q2.md)", ""))
    return res


def selftest() -> int:
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "pass"
        _p, res = _fixture(root)
        out = grade(root, res)
        for cid in IDS:
            ok = out[cid][0]
            print(f"{'ok  ' if ok else 'FAIL'} passing fixture: {cid} passes ({out[cid][1]})")
            fails += not ok
        for cid in IDS:
            broken = Path(d) / cid
            shutil.copytree(root, broken)
            res2 = _break(cid, paths(broken), json.loads(json.dumps(res)))
            out2 = grade(broken, res2)
            ok = not out2[cid][0]
            print(f"{'ok  ' if ok else 'FAIL'} broken fixture: {cid} fails ({out2[cid][1]})")
            fails += not ok
        # Extra fail-closed cases.
        weak = Path(d) / "weak"
        shutil.copytree(root, weak)
        q1 = paths(weak)["research"] / "Q1.md"
        q1.write_text(q1.read_text().replace("https://www.law.cornell.edu/uscode/text/26/674", "https://blog.example.com/674")
                      .replace("https://www.ecfr.gov/current/title-26/section-1.674(d)-2", "https://www.irs.gov/pub/irs-pdf/p559.pdf"))
        ok = not grade(weak, res)["PK1"][0]
        print(f"{'ok  ' if ok else 'FAIL'} PK1 fails with one primary cite and no statute or regulation")
        fails += not ok
        out3 = grade(weak, None)
        ok = not out3["PK4"][0]
        print(f"{'ok  ' if ok else 'FAIL'} PK4 fails without engine results")
        fails += not ok
    print(f"\n{fails} failed")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--results", help="engine results JSON (rehearsal_run.py --json FILE)")
    ap.add_argument("--root", default=str(REPO), help="repository root (default: this repo)")
    ap.add_argument("--all-green", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    res = None
    if a.results:
        try:
            res = json.loads(Path(a.results).read_text())
        except (OSError, ValueError):
            res = None
    n = report(grade(Path(a.root), res), Path(a.root))
    return 0 if (not a.all_green or n == len(IDS)) else 1


if __name__ == "__main__":
    sys.exit(main())
