#!/usr/bin/env python3
"""
Fail-closed check: a case missing a fact the checks need, or stating a fact the
checks cannot read, is never graded Allow.

A SPARQL check fires only when every triple it matches is there, so a missing
fact can silently switch a check off, and a case with no failed checks is
graded Allow. A misspelled value does the same: a check that looks for one term
does not see a near miss. This test tries both on purpose, on every worked case
(spends, entity deals, planned gifts):

  delete   one copy per stated fact, with that one fact deleted. Facts on the
           records a case owns (a benefit on a pay deal, inline or named) count
           as the case's own.
  misspell copies per named or typed value, with the value replaced by one the
           checks cannot read: a name no file declares, the right name written
           as text, or text where a yes/no or an amount belongs.

Each copy is graded in place: the case itself is swapped for the copy in a graph
holding every other case as it is, so nothing else sees the copy and the copy
sees nothing it should not. Copies of different cases share a graph only when no
check reads both cases. H4 (split pay) and its fail-closed partner FC1 read more
than one case, so proposals that share a payee or a year form one unit, as do
cases that share a record: a unit's cases are never changed in the same graph, and
every case in the unit is graded each time one of them is changed. A check that
reads more than one case and is not declared in CROSS_CASE fails the test, so a
new one cannot quietly pool copies again.

The test fails if a copy is graded Allow when

  FC-A  the case itself, or another case in its unit, is not Allow (a missing or
        misspelled fact loosened it),
  FC-B  the deleted fact is one decision/required-inputs.ttl requires of this
        case or its record, and no other value of it remains (FC0 should have
        made it Insufficient), or
  FC-C  a value was misspelled (FC0 should have made it Insufficient).

A copy of an Allow case that loses a fact no requirement names may stay Allow:
that fact was optional (an election, a later year).

  python3 validate_fail_closed.py              both insider branches
  python3 validate_fail_closed.py --branch A   one branch
  python3 validate_fail_closed.py --selftest   with FC0 switched off, show the test catches fail-opens

Misspellings are tried on branch A only: whether a term is known does not depend
on the insider branch. Exits 1 on any problem, so CI can block the merge.
Not legal or tax advice.
"""
import os
import re
import sys
import time
from collections import defaultdict
from multiprocessing import get_context

args = sys.argv[1:]
sys.argv = sys.argv[:1]          # decide_spend reads its own flags at import
import decide_spend as ds        # noqa: E402
from rdflib import BNode, Graph, Literal, URIRef  # noqa: E402
from rdflib.namespace import RDF, RDFS  # noqa: E402

SKIP = {RDF.type, RDFS.label, RDFS.comment}
SH_SELECT = URIRef("http://www.w3.org/ns/shacl#select")
UNKNOWN = URIRef("http://example.org/trust-domain/decision#NotADeclaredTerm")
WRONG_TYPE = Literal("not a yes/no or amount")

# Checks that read more than one case, and the facts that tie cases together.
# Cases that share any one of these values are graded as one unit: never changed in
# the same graph, and each is graded whenever another in its unit is changed. H4 and
# its fail-closed partner FC1 tie proposals by payee or by year (a proposal missing
# its payee is tied to the rest of its year, one missing its year to its payee).
CROSS_CASE = {"H4": (ds.DM.payee, ds.DM.fiscalYear)}


def cross_case_guard():
    """Any check that matches a second case by its class must be declared above."""
    graded = "|".join(ds.short(k) for k in ds.GRADED)
    undeclared = []
    for c, q in ds.shapes.subject_objects(SH_SELECT):
        name = ds.short(c).split("_")[0]
        if re.search(rf"\?\w+\s+(a|rdf:type)\s+dm:({graded})\b", str(q)) and name not in CROSS_CASE:
            undeclared.append(name)
    return undeclared


def facts(g, case):
    """Every fact the case states, on itself or a record it owns: [(node, p, o)]."""
    return [(n, p, o) for n in ds.records(g, case) for p, o in g.predicate_objects(n)
            if p not in SKIP and "Note" not in str(p)]


def misspellings(g, p, o):
    """The same fact with values the checks cannot read: a named term no file declares,
    the right term written as text, or text where a yes/no or an amount belongs."""
    if isinstance(o, BNode):
        return []
    if isinstance(o, Literal):
        ranges = set(g.objects(p, RDFS.range))
        return [WRONG_TYPE] if ranges & ({ds.XSD.boolean} | ds.NUMERIC) else []
    return [UNKNOWN, Literal(ds.short(o))]


def units(g, cases):
    """Cases that must not be changed in the same graph, grouped: [[case, ...]]. Two
    cases are in one unit when they share a value of any CROSS_CASE fact, or own the
    same record (a benefit two deals link to)."""
    key_of = defaultdict(set)
    for case in cases:
        for name, props in CROSS_CASE.items():
            for p in props:
                for v in g.objects(case, p):
                    key_of[(name, p, v)].add(case)
        for rec in ds.records(g, case)[1:]:
            key_of[("record", rec)].add(case)
    parent = {c: c for c in cases}

    def find(c):
        while parent[c] != c:
            c = parent[c]
        return c
    for members in key_of.values():
        first, *rest = sorted(members, key=str)
        for m in rest:
            parent[find(m)] = find(first)
    groups = defaultdict(list)
    for c in sorted(cases, key=str):
        groups[find(c)].append(c)
    return list(groups.values())


# Each worker receives the graph and settings once, through the pool's initializer,
# so the test runs the same under every start method (fork, spawn, forkserver).
STATE = {}


def init_worker(raw, branch, fail_closed):
    STATE.update(raw=raw, branch=branch, fail_closed=fail_closed)


def grade_batch(batch):
    """Grade one graph in which each listed case is swapped for its copy. Returns, per
    change, the grade of every case in the changed case's unit."""
    g = Graph()
    for t in STATE["raw"]:
        g.add(t)
    for _, (node, p, o), new, _ in batch:
        g.remove((node, p, o))
        if new is not None:
            g.add((node, p, new))
    graded, _, _ = ds.run(STATE["branch"], data=ds.derive(g), fail_closed=STATE["fail_closed"])
    return [{c: graded[c][0] for c in unit} for _, _, _, unit in batch]


def check(b, fail_closed=True, only=None, misspell=True, workers=None):
    raw = ds.load(b, derived=False)
    base_data = ds.derive(Graph() + raw)
    base, _, _ = ds.run(b, data=base_data, fail_closed=fail_closed)
    required, _ = ds.required_inputs(base_data)
    cases = [c for c in base if only is None or ds.short(c) in only]

    # Every change to try, per case: (case, fact, replacement or None for delete).
    changes = {}
    for case in cases:
        tried = []
        stated = facts(raw, case)
        for fact in stated:
            tried.append((case, fact, None))
        if misspell:
            for fact in stated:
                for new in misspellings(raw, fact[1], fact[2]):
                    tried.append((case, fact, new))
        changes[case] = tried

    # One unit's changes go in different graphs; different units share graphs. Every
    # case in the changed case's unit is graded, since a fact on one can loosen another.
    all_units = units(raw, list(base))
    unit_of = {c: tuple(u) for u in all_units for c in u}
    batches = defaultdict(list)
    for unit in all_units:
        mine = [ch for case in unit if case in changes for ch in changes[case]]
        for k, (case, fact, new) in enumerate(mine):
            batches[k].append((case, fact, new, unit_of[case]))
    order = [batches[k] for k in sorted(batches)]

    ctx = get_context()
    with ctx.Pool(workers or min(4, os.cpu_count() or 1), initializer=init_worker,
                  initargs=(raw, b, fail_closed)) as pool:
        outcomes = pool.map(grade_batch, order, chunksize=1)

    problems = []
    for batch, graded in zip(order, outcomes):
        for (case, (node, p, o), new, unit), grades in zip(batch, graded):
            where = "" if node == case else " on a linked record"
            what = f"{ds.short(p)}{where} misspelled" if new is not None else f"without {ds.short(p)}{where}"
            theirs = (f"has {ds.short(p)}{where} misspelled" if new is not None
                      else f"has no {ds.short(p)}{where}")
            for other in unit:
                if other != case and grades[other] == ds.DM.Allow and base[other][0] != ds.DM.Allow:
                    problems.append(f"FC-A {ds.short(other)}: {ds.label(base[other][0])}, but Allow "
                                    f"when {ds.short(case)} {theirs}")
            got = grades[case]
            if got != ds.DM.Allow:
                continue
            was = base[case][0]
            if new is not None:
                problems.append(f"FC-C {ds.short(case)}: Allow with {what}")
            elif was != ds.DM.Allow:
                problems.append(f"FC-A {ds.short(case)}: {ds.label(was)}, but Allow {what}")
            elif p in required.get(node, ()) and not any(v != o for v in raw.objects(node, p)):
                problems.append(f"FC-B {ds.short(case)}: Allow {what}, which is required")
    n = sum(len(v) for v in changes.values())
    return len(cases), n, len(order), problems


def main():
    undeclared = cross_case_guard()
    if undeclared:
        print("Checks that read more than one case but are not in CROSS_CASE: " + ", ".join(sorted(undeclared)))
        return 1

    if "--selftest" in args:
        # FC0 off, on cases each known to fail open without it (one per model).
        only = {"D30_FamilyVacation", "G01_LeadAnnuityClean", "G29_UnitrustMortgagedLand",
                "P25_FounderPayPlusBenefits", "D14_PackageOverMarket", "P18b_ContractorSteward"}
        _, n, nb, problems = check("A", fail_closed=False, only=only)
        kinds = {p.split()[0] for p in problems}
        caught = {c for c in only if any(c in p for p in problems)}
        sibling = any(" when P18b_ContractorSteward has " in p for p in problems)
        print(f"selftest, FC0 off: {n} copies in {nb} graphs, {len(problems)} fail-opens caught "
              f"({', '.join(sorted(kinds))})")
        for p in problems:
            print("  " + p)
        want = {"FC-A", "FC-B", "FC-C"}
        linked = any("linked record" in p for p in problems)
        # FC-A on the case itself, not only through a sibling ("... when X has ...").
        direct = any(p.startswith("FC-A ") and " when " not in p for p in problems)
        ok = caught == only and kinds == want and linked and sibling and direct
        print("selftest " + ("passed: the test catches missing facts, missing facts on linked records, "
                             "misspelled values in every model, and a missing fact that loosens another case." if ok
                             else f"FAILED: missed {sorted(only - caught) or sorted(want - kinds) or ('a linked record' if not linked else 'a sibling case' if not sibling else 'a case that fails open on its own missing fact')}"))
        return 0 if ok else 1

    branches = [args[args.index("--branch") + 1].upper()] if "--branch" in args else ["A", "B"]
    bad = 0
    for b in branches:
        t = time.time()
        n, m, nb, problems = check(b, misspell=(b == "A"))
        what = "missing or misspelled" if b == "A" else "missing"
        print(f"Insider branch {b}: {n} cases, {m} copies each with one fact {what}, graded in place "
              f"in {nb} graphs; {len(problems)} graded Allow when they must not be ({time.time() - t:.0f}s)")
        for p in problems:
            print("  " + p)
        bad += len(problems)
    print("Fail closed: " + ("no case is Allow on a missing or unknown fact." if not bad else f"{bad} problem(s)."))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
