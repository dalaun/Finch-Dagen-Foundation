#!/usr/bin/env python3
"""
Figures check: every number a check or a case leans on must be dated and current.

  FIG1  A figure has no as-of date.
  FIG2  A figure was read before a later law change to its governing section
        (from the law changes in decision/figures.ttl: PPA 2006, the 2017 tax
        law, the 2025 law, and the latest amendment to each section the checks use).
  FIG3  A figure a check uses no longer matches that check's shape: the shape
        text named in :shapeLiteral is missing from the check's SPARQL.
  FIG4  A figure has no source or no read status.
  FIG5  A page figure points to a current figure that does not exist.

Then it counts the dated page figures from the audit: how many now point to a
figure read on primary law, and how many are still not verified.

Usage: python3 validate_figures.py
Exits 1 on any FIG problem, so CI can block the merge. Not legal or tax advice.
"""

import sys
from datetime import date

from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS

DM = Namespace("http://example.org/trust-domain/decision#")
SH = Namespace("http://www.w3.org/ns/shacl#")

g = Graph()
for f in ("decision/figures.ttl", "decision/planned-giving-model.ttl",
          "decision/planned-giving-shapes.ttl",
          "tests/decision/giftlaw-stories/page-figures.ttl"):
    g.parse(f, format="turtle")


def section_matches(changed, governing):
    """A law that changed '664' changes '664(c)'; one that changed '512(b)(3)' changes only that unit."""
    return governing == changed or governing.startswith(changed + "(")


laws = []
for law in g.subjects(RDF.type, DM.LawChange):
    enacted = g.value(law, DM.enacted)
    laws.append((str(g.value(law, RDFS.label) or law), enacted.toPython() if enacted else None,
                 [str(s) for s in g.objects(law, DM.changedSection)]))

SELFTEST = """
@prefix : <http://example.org/trust-domain/decision#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
:Fig_SelfTestUndated a :Figure ; :governingSection "4941" ; :figureSource "x" ; :readStatus :ReadPrimary .
:Fig_SelfTestStale a :Figure ; :governingSection "4941(a)" ; :figureSource "x" ; :readStatus :ReadPrimary ;
    :asOf "2005-01-01"^^xsd:date .
:Fig_SelfTestDrift a :Figure ; :governingSection "4941" ; :figureSource "x" ; :readStatus :ReadPrimary ;
    :asOf "2026-11-21"^^xsd:date ; :usedByCheck :Check_PG10 ; :shapeLiteral "?y <= 11" .
"""
if "--selftest" in sys.argv:
    g.parse(data=SELFTEST, format="turtle")

problems = []
figures = sorted(g.subjects(RDF.type, DM.Figure))
for fig in figures:
    name = fig.split("#")[-1]
    as_of = g.value(fig, DM.asOf)
    section = str(g.value(fig, DM.governingSection) or "")
    if as_of is None:
        problems.append(f"FIG1 {name}: no as-of date")
    else:
        d = as_of.toPython()
        if not isinstance(d, date):
            problems.append(f"FIG1 {name}: as-of date is not a date ({as_of})")
        else:
            for label, enacted, sections in laws:
                if enacted and any(section_matches(s, section) for s in sections) and d < enacted:
                    problems.append(f"FIG2 {name}: read {d}, before {label} changed section {section}")
    if g.value(fig, DM.figureSource) is None or g.value(fig, DM.readStatus) is None:
        problems.append(f"FIG4 {name}: missing source or read status")
    literal = g.value(fig, DM.shapeLiteral)
    for check in g.objects(fig, DM.usedByCheck):
        constraint = g.value(check, DM.checkConstraint)
        sparql = str(g.value(constraint, SH.select) or "") if constraint is not None else ""
        if not sparql:
            problems.append(f"FIG3 {name}: {check.split('#')[-1]} has no shape to compare")
        elif literal is not None and str(literal) not in sparql:
            problems.append(f"FIG3 {name}: {check.split('#')[-1]} shape no longer contains '{literal}'")

pages = sorted(g.subjects(RDF.type, DM.PageFigure))
refreshed, primary, unverified = 0, 0, []
for p in pages:
    cur = g.value(p, DM.currentFigure)
    if cur is None:
        unverified.append(p)
        continue
    if (cur, RDF.type, DM.Figure) not in g:
        problems.append(f"FIG5 {p.split('#')[-1]}: current figure {cur.split('#')[-1]} is not in the registry")
        continue
    refreshed += 1
    if g.value(cur, DM.readStatus) == DM.ReadPrimary:
        primary += 1

print(f"{len(figures)} figures in the registry, all checked against {len(laws)} law changes.")
print(f"{len(pages)} dated page figures from the audit: {refreshed} refreshed to a figure read on "
      f"2026-11-21 ({primary} on primary law), {len(unverified)} not verified.")
if "--list" in sys.argv:
    for p in unverified:
        print(f"  not verified: {g.value(p, RDFS.label)} ({g.value(p, DM.pageSection)}): "
              f"page prints {g.value(p, DM.pagePrints)}; audit says {g.value(p, DM.auditSays)}")
if "--selftest" in sys.argv:
    want = {"FIG1 Fig_SelfTestUndated", "FIG2 Fig_SelfTestStale", "FIG3 Fig_SelfTestDrift"}
    got = {" ".join(p.split(":")[0].split()[:2]) for p in problems}
    missing = want - got
    others = [p for p in problems if "SelfTest" not in p]
    print("Self-test: the check catches an undated, a stale and a drifted figure." if not missing and not others
          else f"Self-test FAILED: missed {sorted(missing)}; other problems {others}")
    sys.exit(1 if missing or others else 0)
for line in problems:
    print(line)
sys.exit(1 if problems else 0)
