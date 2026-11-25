#!/usr/bin/env python3
"""Lawyer-ready packet scorecard: the relay's finish line (Dalaun's lane).

The unit of work is tracing to source, not deciding what is right. A counsel
question is done when every claim in its answer carries a trace: the authority,
the exact quoted text, where it was read and the date; or, where nothing is on
point, "no authority found" and where the run searched. That second kind is a
finished answer too: it is exactly what the lawyer decides.

This file sits in Dalaun's lane (tests/, see .github/CODEOWNERS), so the agents
that write the packet never change how it is graded. The packet is agent-lane
work under rehearsal/synthetic/packet/. Plain words: rehearsal/loop/PACKET-SCORECARD.md.

  python3 tests/rehearsal/packet_scorecard.py --results FILE [--verify-quotes]
  python3 tests/rehearsal/packet_scorecard.py --results FILE --verify-quotes --all-green
  python3 tests/rehearsal/packet_scorecard.py --quotes-only     re-read every quote; exit 1 on any mismatch
  python3 tests/rehearsal/packet_scorecard.py --selftest

--verify-quotes and --quotes-only fetch each cited page and look for the quote
in its text. A page that cannot be read counts as a mismatch: a wrong cite costs
the lawyer more time than a missing one. keystone runs --quotes-only through
tests/rehearsal/pinned_checks.py, so a pull request with a bad quote cannot merge.

Criteria:
  PK1 traced     every counsel-queue question has packet/research/Q<n>.md whose every claim
                 has a trace (authority, "exact quote", URL, read date; or "no authority found",
                 searched: where); a confidence label; at most 2 follow-on questions, each in
                 the queue with the decision it changes
  PK2 framed     every question labelled likely or open says what the lawyer decides
  PK3 verified   every quote was re-read on its page and matches (needs --verify-quotes)
  PK4 labelled   every packet file says it is research for counsel review, not legal advice
  PK5 sized      both break-even scenarios re-run as a family of sizes (0.75x to 1.5x), a
                 realistic case named with a cited basis, table rows matching the engine
  PK6 memo       one structure memo: four sections, the layers, every likely or open question
  PK7 packet     one packet file linking every part, about an hour's reading (15,000 words)

The relay's first stop is the top tier (TOP_TIER below) fully traced and verified.

SYNTHETIC. Research for counsel review, not legal or tax advice.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
IDS = ["PK1", "PK2", "PK3", "PK4", "PK5", "PK6", "PK7"]
NAMES = {"PK1": "traced", "PK2": "framed", "PK3": "verified", "PK4": "labelled",
         "PK5": "sized", "PK6": "memo", "PK7": "packet"}
LABEL = "Research for counsel review, not legal advice."
CONFIDENCE = {"settled", "likely", "open"}
# Ranked by decision value (Dalaun's lane, 2026-11-25): an answer here changes the
# structure itself (grantor status and the trustee role, IRC 671-679 including 674
# and 677; the Foundation link, 4941 and 4947(a)(2); the funder's gift; the guarantee).
TOP_TIER = (2, 3, 4, 5, 7, 8, 9, 10, 15, 18)
PRIMARY_HOSTS = (
    "law.cornell.edu", "ecfr.gov", "uscode.house.gov", "govinfo.gov", "federalregister.gov",
    "irs.gov", "ilga.gov", "illinoiscourts.gov", "supremecourt.gov", "sba.gov", "treasury.gov",
)
MAX_FOLLOW_ON = 2
MIN_QUOTE_WORDS = 5
BREAK_EVEN_FAMILIES = ("asset_sized", "asset_sized_pipeline")
MEMO_SECTIONS = ("## the structure", "## decisions only dalaun makes", "## risks", "## what a lawyer must decide")
MEMO_LAYERS = ("business trust", "family trust", "foundation", "non-grantor")
MAX_WORDS = 15000
MEMO_MAX_WORDS = 3000
READ_RE = re.compile(r"\(read (\d{4}-\d{2}-\d{2})\)")
URL_RE = re.compile(r"https://[^\s)>\]|]+")
QUOTE_RE = re.compile(r"^[\"“](.+)[\"”]$", re.S)


def paths(root: Path) -> dict:
    syn = root / "rehearsal" / "synthetic"
    pk = syn / "packet"
    return {"queue": syn / "counsel-queue.md", "scenarios": syn / "scenarios.json", "packet": pk,
            "research": pk / "research", "memo": pk / "STRUCTURE-MEMO.md",
            "sens": pk / "SENSITIVITY.md", "main": pk / "LAWYER-PACKET.md"}


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


def queue(p) -> dict[int, str]:
    text = read(p["queue"])
    out = {}
    for m in re.finditer(r"^## Q(\d+)\.(.*?)(?=^## Q\d+\.|\Z)", text, re.M | re.S):
        out[int(m.group(1))] = m.group(2)
    return out


def host_ok(url: str) -> bool:
    host = re.sub(r"^https://", "", url).split("/")[0].lower()
    return any(host == h or host.endswith("." + h) for h in PRIMARY_HOSTS)


def block(text: str, name: str) -> str:
    m = re.search(rf"^-\s*{name}:\s*$(.*?)(?=^-\s*\w[\w -]*:|\Z)", text, re.M | re.S | re.I)
    return m.group(1) if m else ""


def claims(text: str) -> list[dict]:
    """Numbered claims under '- Claims:', each with its '- Trace:' lines."""
    out = []
    for ln in block(text, "Claims").splitlines():
        m = re.match(r"^\s+(\d+)\.\s+(.+)$", ln)
        if m:
            out.append({"text": m.group(2).strip(), "traces": []})
            continue
        t = re.match(r"^\s+-\s*Trace:\s*(.+)$", ln, re.I)
        if t and out:
            out[-1]["traces"].append(t.group(1).strip())
    return out


def parse_trace(t: str) -> dict:
    parts = [x.strip() for x in t.split(" | ")]
    if parts and parts[0].lower().startswith("no authority found"):
        rest = " | ".join(parts[1:])
        if not re.match(r"searched:\s*\S", rest, re.I) or not READ_RE.search(rest):
            return {"error": "no-authority trace needs 'searched: <where>' and a read date"}
        return {"kind": "none"}
    if len(parts) != 3:
        return {"error": f"trace needs authority | \"quote\" | URL (read date): {t[:60]}"}
    auth, quote, src = parts
    q = QUOTE_RE.match(quote)
    if not auth or not q:
        return {"error": f"trace quote is not in quotation marks: {t[:60]}"}
    if words(q.group(1)) < MIN_QUOTE_WORDS:
        return {"error": f"quote under {MIN_QUOTE_WORDS} words: {t[:60]}"}
    urls = URL_RE.findall(src)
    if not urls or not READ_RE.search(src) or "not read" in src.lower():
        return {"error": f"trace without a URL and a read date: {t[:60]}"}
    if not host_ok(urls[0]):
        return {"error": f"not a primary source: {urls[0][:60]}"}
    return {"kind": "authority", "authority": auth, "quote": q.group(1), "url": urls[0]}


def follow_ons(text: str) -> list[tuple[int, str]]:
    out = []
    for ln in block(text, "Follow-on").splitlines():
        m = re.match(r"^\s+-\s*Q(\d+):\s*(.*)$", ln)
        if m:
            out.append((int(m.group(1)), m.group(2).strip()))
    return out


def research(p) -> dict[int, dict]:
    out = {}
    for n in queue(p):
        text = read(p["research"] / f"Q{n}.md")
        out[n] = {"text": text, "confidence": field(text, "Confidence").lower().strip(" ."),
                  "decides": field(text, "Lawyer decides"), "claims": claims(text),
                  "follow": follow_ons(text)}
    return out


def research_problem(r: dict, q: dict[int, str]) -> str:
    if not r["text"]:
        return "no research file"
    if r["confidence"] not in CONFIDENCE:
        return "confidence is not settled, likely or open"
    if not r["claims"]:
        return "no numbered claims under '- Claims:'"
    for i, c in enumerate(r["claims"], 1):
        if not c["traces"]:
            return f"claim {i} has no trace"
        for t in c["traces"]:
            pt = parse_trace(t)
            if "error" in pt:
                return f"claim {i}: {pt['error']}"
    if len(r["follow"]) > MAX_FOLLOW_ON:
        return f"{len(r['follow'])} follow-on questions, cap {MAX_FOLLOW_ON}"
    for n, why in r["follow"]:
        if n not in q:
            return f"follow-on Q{n} is not in the counsel queue"
        if words(why) < 3 or not re.search(r"^\s*-\s*Changes decision:\s*\S", q[n], re.M | re.I):
            return f"follow-on Q{n} does not say which decision it changes"
    return ""


def all_quotes(p) -> list[dict]:
    out = []
    for n, r in research(p).items():
        for c in r["claims"]:
            for t in c["traces"]:
                pt = parse_trace(t)
                if pt.get("kind") == "authority":
                    out.append({"q": n, **pt})
    return out


# ------------------------------------------------------------------ quote check

def norm(text: str) -> str:
    text = html.unescape(text)
    text = text.translate({0x2018: "'", 0x2019: "'", 0x201c: '"', 0x201d: '"', 0x2013: "-",
                           0x2014: "-", 0xa0: " ", 0xa7: " "})
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def page_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    return norm(re.sub(r"(?s)<[^>]+>", " ", raw))


def fetch(url: str) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (quote-check; finch-dagen packet scorecard)",
                                               "Accept": "text/html,application/xhtml+xml,text/plain"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                ctype = r.headers.get("Content-Type", "")
                body = r.read()
            if "pdf" in ctype.lower():
                return None
            return body.decode("utf-8", "replace")
        except Exception:  # noqa: BLE001 - any failure is "could not read", which fails closed
            time.sleep(2 * (attempt + 1))
    return None


def verify(quotes: list[dict], fetcher=fetch) -> list[dict]:
    cache: dict[str, str | None] = {}
    out = []
    for qd in quotes:
        if qd["url"] not in cache:
            raw = fetcher(qd["url"])
            cache[qd["url"]] = page_text(raw) if raw is not None else None
        text = cache[qd["url"]]
        if text is None:
            out.append({**qd, "result": "could not read the page"})
        elif norm(qd["quote"]) in text:
            out.append({**qd, "result": "match"})
        else:
            out.append({**qd, "result": "quote not found on the page"})
    return out


# ------------------------------------------------------------------ criteria

def pk1(p, ctx):
    q, rs = queue(p), research(p)
    if not rs:
        return False, "no counsel-queue questions found"
    bad = {n: research_problem(r, q) for n, r in rs.items()}
    bad = {n: why for n, why in bad.items() if why}
    named = {f for r in rs.values() for f, _ in r["follow"]}
    for n in q:
        if n > 18 and n not in named:
            bad.setdefault(n, "added after 2026-11-25 but no research file names it as a follow-on")
    if bad:
        n = min(bad)
        return False, f"{len(rs) - len(bad)} of {len(rs)} traced; Q{n}: {bad[n]}"
    return True, f"all {len(rs)} questions traced to source"


def pk2(p, ctx):
    rs = research(p)
    if not rs or any(not r["text"] for r in rs.values()):
        return False, "waits on PK1: not every question has a research file"
    need = [n for n, r in rs.items() if r["confidence"] in ("likely", "open")]
    miss = [n for n in need if words(rs[n]["decides"]) < 5]
    if miss:
        return False, f"Q{miss[0]} is {rs[miss[0]]['confidence']} but says nothing a lawyer decides"
    return True, f"{len(need)} likely or open questions each name what the lawyer decides"


def pk3(p, ctx):
    checked = ctx.get("verified")
    if checked is None:
        return False, "quotes not re-read (run with --verify-quotes)"
    if not checked:
        return False, "no quotes yet"
    bad = [c for c in checked if c["result"] != "match"]
    if bad:
        b = bad[0]
        return False, f"{len(checked) - len(bad)} of {len(checked)} quotes match; Q{b['q']} {b['authority']}: {b['result']}"
    return True, f"all {len(checked)} quotes match their pages"


def packet_files(p) -> list[Path]:
    return [p["memo"], p["sens"], p["main"]] + [p["research"] / f"Q{n}.md" for n in queue(p)]


def pk4(p, ctx):
    missing = [f for f in packet_files(p) if LABEL not in read(f)]
    if missing:
        return False, f"{len(missing)} packet files lack the label, first {missing[0].name}"
    return True, "every packet file carries the research-not-advice label"


def asset_income(s: dict):
    for ln in s.get("extra_lines", []):
        if ln.get("id") == "asset_net_income" and isinstance(ln.get("annual"), (int, float)):
            return float(ln["annual"])
    return None


def pk5(p, ctx):
    res = ctx.get("results")
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


def pk6(p, ctx):
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
    return True, "memo has the four sections, the layers and every open question"


def pk7(p, ctx):
    main = read(p["main"])
    if not main:
        return False, "no LAWYER-PACKET.md"
    if "SYNTHETIC" not in main:
        return False, "packet does not say its numbers are synthetic"
    links = set(re.findall(r"\]\(([^)#\s]+)", main))
    need = ["STRUCTURE-MEMO.md", "SENSITIVITY.md"] + [f"research/Q{n}.md" for n in queue(p)]
    miss = [n for n in need if n not in links and f"./{n}" not in links]
    if miss:
        return False, f"packet does not link {miss[0]}"
    total = sum(words(read(f)) for f in packet_files(p))
    if total > MAX_WORDS:
        return False, f"packet is {total:,} words in all, cap {MAX_WORDS:,} (about an hour's reading)"
    return True, f"one packet, {total:,} words, links every part"


CHECKS = {"PK1": pk1, "PK2": pk2, "PK3": pk3, "PK4": pk4, "PK5": pk5, "PK6": pk6, "PK7": pk7}


def grade(root: Path, ctx: dict) -> dict:
    p = paths(root)
    return {cid: CHECKS[cid](p, ctx) for cid in IDS}


def progress(root: Path, ctx: dict) -> dict:
    p = paths(root)
    q, rs = queue(p), research(p)
    done = {n for n, r in rs.items() if not research_problem(r, q)}
    top = [n for n in TOP_TIER if n in q]
    checked = ctx.get("verified")
    ok_q = None if checked is None else {c["q"] for c in checked if c["result"] != "match"}
    top_verified = None if checked is None else all(n in done and n not in ok_q for n in top)
    return {"traced": len(done), "questions": len(rs), "top_traced": sum(n in done for n in top),
            "top": len(top), "open": sum(rs[n]["confidence"] == "open" for n in done),
            "quotes": None if checked is None else len(checked),
            "quotes_ok": None if checked is None else sum(c["result"] == "match" for c in checked),
            "top_tier_done": bool(top_verified)}


def report(out: dict, root: Path, ctx: dict) -> int:
    for cid in IDS:
        ok, why = out[cid]
        print(f"{'PASS' if ok else 'FAIL'} {cid} {NAMES[cid]}: {why}")
    g = progress(root, ctx)
    qv = "quotes not re-read" if g["quotes"] is None else f"quotes verified {g['quotes_ok']} of {g['quotes']}"
    n = sum(ok for ok, _ in out.values())
    print(f"Top tier: {'done' if g['top_tier_done'] else 'not done'} ({g['top_traced']} of {g['top']} traced)")
    print(f"Packet: {n} of {len(IDS)} pass; traced {g['traced']} of {g['questions']} "
          f"(top tier {g['top_traced']} of {g['top']}, {g['open']} open for the lawyer); {qv}")
    return n


# ------------------------------------------------------------------ selftest

QUOTE1 = "the term related or subordinate party means any nonadverse party"
PAGE1 = "<html><body><p>(c) The term <b>&ldquo;related or subordinate party&rdquo;</b> means any nonadverse party who is</p></body></html>"


def _fixture(tmp: Path):
    p = paths(tmp)
    p["research"].mkdir(parents=True)
    p["queue"].write_text("# Counsel queue\n\n## Q1. One?\n\n- Key: `a`\n\n## Q2. Two?\n\n- Key: `b`\n\n"
                          "## Q19. Three?\n\n- Key: `c`\n- Changes decision: whether the advisor can serve\n")
    auth = f'  - Trace: IRC 672(c) | "{QUOTE1}" | https://uscode.house.gov/view.xhtml?req=26+USC+672 (read 2026-11-25)\n'
    none = "  - Trace: no authority found | searched: IRC 671-679; Treas. Reg. 1.674(d)-2 (read 2026-11-25)\n"
    p["research"].joinpath("Q1.md").write_text(
        f"# Q1\n\n{LABEL}\n\n- Confidence: settled\n- Claims:\n  1. The test is related or subordinate.\n{auth}")
    p["research"].joinpath("Q2.md").write_text(
        f"# Q2\n\n{LABEL}\n\n- Confidence: open\n- Lawyer decides: whether the advisor counts as a trustee\n"
        f"- Claims:\n  1. The code defines the party.\n{auth}  2. Nothing addresses advisors.\n{none}"
        "- Follow-on:\n  - Q19: changes whether the advisor can serve\n")
    p["research"].joinpath("Q19.md").write_text(
        f"# Q19\n\n{LABEL}\n\n- Confidence: open\n- Lawyer decides: whether Illinois law lets the advisor serve\n"
        f"- Claims:\n  1. Nothing found.\n{none}")
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
        "## Decisions only Dalaun makes\n\nx\n\n## Risks\n\nx\n\n## What a lawyer must decide\n\n- Q2: the advisor.\n- Q19: Illinois.\n")
    p["main"].write_text(
        f"# Packet\n\nSYNTHETIC.\n\n{LABEL}\n\n[memo](STRUCTURE-MEMO.md) [table](SENSITIVITY.md) "
        "[Q1](research/Q1.md) [Q2](research/Q2.md) [Q19](research/Q19.md)\n")
    return p, res


def _ctx(root: Path, res, page=PAGE1):
    return {"results": res, "verified": verify(all_quotes(paths(root)), fetcher=lambda _u: page)}


def _break(cid: str, p):
    page = PAGE1
    q1, q2 = p["research"] / "Q1.md", p["research"] / "Q2.md"
    if cid == "PK1":
        q1.write_text(q1.read_text().replace("(read 2026-11-25)", "(not read)", 1))
    elif cid == "PK2":
        q2.write_text(re.sub(r"- Lawyer decides:.*\n", "", q2.read_text()))
    elif cid == "PK3":
        page = PAGE1.replace("nonadverse", "adverse")
    elif cid == "PK4":
        p["memo"].write_text(p["memo"].read_text().replace(LABEL, ""))
    elif cid == "PK5":
        p["sens"].write_text(p["sens"].read_text().replace("| 101 |", "| 9999 |"))
    elif cid == "PK6":
        p["memo"].write_text(p["memo"].read_text().replace("- Q2: the advisor.", "- the advisor."))
    elif cid == "PK7":
        p["main"].write_text(p["main"].read_text().replace("[Q2](research/Q2.md)", ""))
    return page


def selftest() -> int:
    fails = 0

    def check(ok, msg):
        nonlocal fails
        print(f"{'ok  ' if ok else 'FAIL'} {msg}")
        fails += not ok

    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "pass"
        _p, res = _fixture(root)
        out = grade(root, _ctx(root, res))
        for cid in IDS:
            check(out[cid][0], f"passing fixture: {cid} passes ({out[cid][1]})")
        check(progress(root, _ctx(root, res))["traced"] == 3, "progress counts 3 traced questions")
        for cid in IDS:
            broken = Path(d) / cid
            shutil.copytree(root, broken)
            page = _break(cid, paths(broken))
            out2 = grade(broken, _ctx(broken, res, page))
            check(not out2[cid][0], f"broken fixture: {cid} fails ({out2[cid][1]})")

        def variant(name, edit):
            v = Path(d) / name
            shutil.copytree(root, v)
            edit(paths(v))
            return grade(v, _ctx(v, res))["PK1"]

        def unquote(p):
            f = p["research"] / "Q1.md"
            f.write_text(f.read_text().replace(f'"{QUOTE1}"', QUOTE1))
        check(not variant("unquoted", unquote)[0], "PK1 fails a cite with no quotation marks")

        def blog(p):
            f = p["research"] / "Q1.md"
            f.write_text(f.read_text().replace("https://uscode.house.gov/view.xhtml?req=26+USC+672", "https://blog.example.com/672"))
        check(not variant("blog", blog)[0], "PK1 fails a trace to a non-primary source")

        def untraced(p):
            f = p["research"] / "Q1.md"
            f.write_text(f.read_text() + "  2. An extra claim with no trace.\n")
        check(not variant("untraced", untraced)[0], "PK1 fails a claim with no trace")

        def searchless(p):
            f = p["research"] / "Q2.md"
            f.write_text(f.read_text().replace("searched: IRC 671-679; Treas. Reg. 1.674(d)-2 ", ""))
        check(not variant("searchless", searchless)[0], "PK1 fails 'no authority found' without where it searched")

        def three(p):
            f = p["research"] / "Q2.md"
            f.write_text(f.read_text() + "  - Q1: changes x y z\n  - Q19: changes a b c\n")
        check(not variant("three", three)[0], "PK1 fails more than two follow-on questions")

        def orphan(p):
            p["queue"].write_text(p["queue"].read_text() + "\n## Q20. Orphan?\n\n- Changes decision: nothing named\n")
        check(not variant("orphan", orphan)[0], "PK1 fails a new question no research file names as a follow-on")

        def nodecision(p):
            p["queue"].write_text(p["queue"].read_text().replace("- Changes decision: whether the advisor can serve\n", ""))
        check(not variant("nodecision", nodecision)[0], "PK1 fails a follow-on that changes no named decision")

        unread = grade(root, {"results": res, "verified": verify(all_quotes(paths(root)), fetcher=lambda _u: None)})
        check(not unread["PK3"][0], "PK3 fails when the page cannot be read")
        check(not grade(root, {"results": res})["PK3"][0], "PK3 fails when quotes were not re-read")
        check(not grade(root, {"results": None, "verified": []})["PK5"][0], "PK5 fails without engine results")
    print(f"\n{fails} failed")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--results", help="engine results JSON (rehearsal_run.py --json FILE)")
    ap.add_argument("--root", default=str(REPO), help="repository root (default: this repo)")
    ap.add_argument("--verify-quotes", action="store_true", help="re-read every quote on its page")
    ap.add_argument("--quotes-only", action="store_true", help="only re-read the quotes; exit 1 on any mismatch")
    ap.add_argument("--all-green", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    root = Path(a.root)
    if a.quotes_only:
        checked = verify(all_quotes(paths(root)))
        for c in checked:
            print(f"{'ok  ' if c['result'] == 'match' else 'FAIL'} Q{c['q']} {c['authority']}: {c['result']} ({c['url']})")
        bad = sum(c["result"] != "match" for c in checked)
        print(f"Quotes: {len(checked) - bad} of {len(checked)} match")
        return 1 if bad else 0
    ctx = {"results": None}
    if a.results:
        try:
            ctx["results"] = json.loads(Path(a.results).read_text())
        except (OSError, ValueError):
            pass
    if a.verify_quotes:
        ctx["verified"] = verify(all_quotes(paths(root)))
    n = report(grade(root, ctx), root, ctx)
    return 0 if (not a.all_green or n == len(IDS)) else 1


if __name__ == "__main__":
    sys.exit(main())
