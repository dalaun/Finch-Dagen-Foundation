#!/usr/bin/env python3
"""
Grade the GiftLaw Pro example stories with the planned-giving checks.

  python3 grade_stories.py             every story file in tests/decision/giftlaw-stories/
  python3 grade_stories.py FILE.ttl    one file (with roles.ttl)
  python3 grade_stories.py --list      also print every graded story, agreeing or not

Each dm:StoryCase records a story from the shelf extract: the outcome the page
reaches and, when the checks can grade it, a dm:PlannedGift with its facts. The
checks run under insider branch A. A disagreement is a finding, not a failure:
"page block, ours allow" means the page turns on a rule we have no check for;
"page allow, ours block" means we are stricter than the page, or the page is
wrong. The run fails (exit 1) only on a malformed record. Not legal or tax advice.
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path
from rdflib import Graph, Namespace, RDF
from pyshacl import validate

HERE = Path(__file__).resolve().parent
DM = Namespace("http://example.org/trust-domain/decision#")
SH = Namespace("http://www.w3.org/ns/shacl#")
STORIES = HERE / "tests/decision/giftlaw-stories"
args = sys.argv[1:]
show_all = "--list" in args
files = [Path(a) for a in args if not a.startswith("--")] or sorted(
    p for p in STORIES.glob("*.ttl") if p.name not in ("roles.ttl", "audit-flags.ttl", "page-figures.ttl"))

data = Graph()
for f in [HERE / "trust-domain-ontology.ttl", HERE / "decision/spend-decision-model.ttl",
          HERE / "decision/stewardship-model.ttl", HERE / "decision/irs-instruments.ttl",
          HERE / "decision/planned-giving-model.ttl", HERE / "decision/giftlaw-stories-model.ttl",
          HERE / "tests/decision/branch-a.ttl", STORIES / "roles.ttl", STORIES / "audit-flags.ttl", *files]:
    data.parse(f, format="turtle")
shapes = Graph()
shapes.parse(HERE / "decision/planned-giving-shapes.ttl", format="turtle")

short = lambda u: str(u).split("#")[-1]
severity = {o: int(data.value(o, DM.severity)) for o in data.subjects(RDF.type, DM.Outcome)}
by_severity = {v: k for k, v in severity.items()}

_, report, _ = validate(data, shacl_graph=shapes, inference="rdfs", advanced=True, allow_warnings=True)
failed = defaultdict(set)
for r in report.subjects(RDF.type, SH.ValidationResult):
    failed[report.value(r, SH.focusNode)].add(report.value(r, SH.sourceConstraint))
check_of = {}
for chk in data.subjects(RDF.type, DM.DecisionCheck):
    c = data.value(chk, DM.checkConstraint)
    if c is not None:
        check_of[c] = (short(c).split("_")[0], data.value(chk, DM.onFail))

def trust_of(s):
    t = data.value(s, DM.pageTrust)
    if t is not None:
        return t
    sec = str(data.value(s, DM.storySection) or "")
    flags = [str(f) for f in data.objects(s, DM.auditFlag)]
    if sec.startswith("9"):
        return DM.PageLeadOnly
    if sec.startswith("4") or any("(H," in f for f in flags):
        return DM.PageClaimToTest
    return DM.PageMap


def flag_types(s):
    return [str(f) for f in data.objects(s, DM.auditFlag)]


bad, rows, ids = [], [], Counter()
trust_n, overturned, law_n, opposite, leads, unread = Counter(), [], Counter(), [], Counter(), []
scope_n, outside_n, verdict_n = Counter(), Counter(), Counter()
for s in sorted(data.subjects(RDF.type, DM.StoryCase), key=lambda x: str(data.value(x, DM.storyId))):
    sid = str(data.value(s, DM.storyId) or short(s))
    ids[sid] += 1
    for p in (DM.storyId, DM.storySection, DM.pageSays, DM.pageOutcome, DM.storyScope):
        if data.value(s, p) is None:
            bad.append(f"{sid}: no {short(p)}")
    page, scope = data.value(s, DM.pageOutcome), data.value(s, DM.storyScope)
    if page is not None and page not in severity and page != DM.PageGivesNoGrade:
        bad.append(f"{sid}: pageOutcome {short(page)} is not an outcome")
    scope_n[short(scope)] += 1
    trust = trust_of(s)
    trust_n[short(trust)] += 1
    flags = flag_types(s)
    law = data.value(s, DM.authorityOutcome)
    if law is not None:
        if law not in severity:
            bad.append(f"{sid}: authorityOutcome {short(law)} is not an outcome")
        if data.value(s, DM.authorityBasis) is None:
            bad.append(f"{sid}: authorityOutcome needs an authorityBasis")
        if page is not None and law != page:
            overturned.append((sid, short(page), short(law), str(data.value(s, DM.authorityBasis) or "")))
    if any("cited-for-opposite" in f for f in flags):
        if data.value(s, DM.citedForOpposite) is None:
            bad.append(f"{sid}: the audit says the page cites an authority for the opposite; record citedForOpposite")
        else:
            opposite.append((sid, bool(data.value(s, DM.citedAuthorityRead)), str(data.value(s, DM.citedForOpposite))))
    if trust == DM.PageLeadOnly:
        st = data.value(s, DM.authorityStatus)
        leads[str(st).split(":")[0] if st is not None else "status not checked"] += 1
    if data.value(s, DM.authorityUnread) is not None:
        unread.append((sid, str(data.value(s, DM.authorityUnread))))
    if scope == DM.OutsideModel:
        cat = data.value(s, DM.outsideCategory)
        if cat is None or data.value(s, DM.outsideReason) is None:
            bad.append(f"{sid}: outside the model needs outsideCategory and outsideReason")
        outside_n[short(cat)] += 1
        continue
    gift = data.value(s, DM.storyGift)
    if gift is None or (gift, RDF.type, DM.PlannedGift) not in data:
        bad.append(f"{sid}: graded by the model needs a storyGift that is a dm:PlannedGift")
        continue
    hits = {check_of[c][0]: check_of[c][1] for c in failed.get(gift, ()) if c in check_of}
    ours = by_severity[max([0, *(severity[o] for o in hits.values())])]
    if trust == DM.PageClaimToTest and law is None and data.value(s, DM.authorityUnread) is None and any(
            "outright-error" in f or "(H," in f for f in flags):
        bad.append(f"{sid}: flagged claim not regraded on primary authority (set authorityOutcome or authorityUnread)")
    if law is not None:
        law_n["ours matches the law" if law == ours else f"ours {short(ours)}, law {short(law)}"] += 1
        page = law
    if page == DM.PageGivesNoGrade:
        verdict = "page gives no result"
    elif page == ours:
        verdict = "agree"
    elif severity.get(page, 0) > severity[ours]:
        verdict = "page stricter"
    else:
        verdict = "ours stricter"
    verdict_n[verdict] += 1
    rows.append((sid, short(page), short(ours), " ".join(sorted(hits)) or "-", verdict,
                 str(data.value(s, DM.gapNote) or ""), str(data.value(s, DM.pageAccuracyNote) or "")))
bad += [f"{sid}: story id used {n} times" for sid, n in ids.items() if n > 1]

print(f"{'story':8} {'page':13} {'ours':13} {'checks':10} verdict")
for sid, page, ours, checks, verdict, gap, acc in rows:
    if show_all or verdict not in ("agree",):
        print(f"{sid:8} {page:13} {ours:13} {checks:10} {verdict}")
        for label, note in (("gap", gap), ("page accuracy", acc)):
            if note and verdict != "agree":
                print(f"{'':8} {label}: {note}")
print(f"\n{sum(ids.values())} stories: {scope_n['GradedByModel']} graded by the checks, "
      f"{scope_n['OutsideModel']} outside the model.")
print("graded: " + ", ".join(f"{v} {k}" for k, v in verdict_n.most_common()))
print("outside: " + ", ".join(f"{v} {k}" for k, v in outside_n.most_common()))
print("page trust: " + ", ".join(f"{v} {k}" for k, v in trust_n.most_common()))
print(f"regraded on primary authority: {sum(law_n.values())} graded stories; "
      + ", ".join(f"{v} {k}" for k, v in law_n.most_common()))
print(f"flagged claims left for an authority not yet read: {len(unread)}")
if show_all:
    for sid, note in unread:
        print(f"  {sid}: {note}")
print(f"page overturned by primary authority: {len(overturned)}")
for sid, page, law, basis in overturned:
    print(f"  {sid}: page {page}, law {law}. {basis}")
print(f"cited for the opposite of its holding: {len(opposite)} stories, "
      f"{sum(1 for _, r, _ in opposite if r)} with the case or ruling read")
for sid, read, note in opposite:
    print(f"  {sid} ({'read' if read else 'unread'}): {note}")
print("Chapter 9 leads (check a ruling has not been superseded before citing it): "
      + ", ".join(f"{v} {k}" for k, v in leads.most_common()))
for b in bad:
    print("MALFORMED", b)
sys.exit(1 if bad else 0)
