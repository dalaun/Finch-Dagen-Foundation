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
           records a case owns (a benefit on a pay deal) count as the case's own.
  misspell one copy per named or typed value, with the value replaced by one no
           file declares (a misspelled name, a yes/no written as text).

Each copy is graded in place: the case itself is swapped for the copy in a graph
holding every other case as it is, so nothing else sees the copy and the copy
sees nothing it should not. Copies of different cases share a graph only when no
check reads both cases; H4 (split pay) is the one check that reads more than one
case, so the proposals one payee is paid in one year are never changed together.
A check that reads more than one case and is not declared in CROSS_CASE fails
the test, so a new one cannot quietly pool copies again.

The test fails if a copy is graded Allow when

  FC-A  the case itself is not Allow (deleting a fact loosened it),
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
from multiprocessing import Pool

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
# Copies of cases that share a key are graded in different graphs.
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


def misspelling(g, p, o):
    """The same fact with a value no file declares, or None if the value is a record."""
    if isinstance(o, BNode):
        return None
    if isinstance(o, Literal):
        ranges = set(g.objects(p, RDFS.range))
        return WRONG_TYPE if ranges & ({ds.XSD.boolean} | ds.NUMERIC) else None
    return UNKNOWN


def units(g, cases):
    """Cases that must not be changed in the same graph, grouped: [[case, ...]]."""
    key_of = defaultdict(set)
    for case in cases:
        for name, props in CROSS_CASE.items():
            vals = [tuple(g.objects(case, p)) for p in props]
            if all(vals):
                for combo in zip(*vals):
                    key_of[(name, combo)].add(case)
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


# The worker state is set before the pool forks, so each process shares it.
STATE = {}


def grade_batch(batch):
    """Grade one graph in which each listed case is swapped for its copy."""
    g = Graph()
    for t in STATE["raw"]:
        g.add(t)
    for case, (node, p, o), new in batch:
        g.remove((node, p, o))
        if new is not None:
            g.add((node, p, new))
    graded, _, _ = ds.run(STATE["branch"], data=ds.derive(g), fail_closed=STATE["fail_closed"])
    return [graded[case][0] for case, _, _ in batch]


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
                new = misspelling(raw, fact[1], fact[2])
                if new is not None:
                    tried.append((case, fact, new))
        changes[case] = tried

    # One unit's changes go in different graphs; different units share graphs.
    batches = defaultdict(list)
    for unit in units(raw, cases):
        for k, change in enumerate(ch for case in unit for ch in changes[case]):
            batches[k].append(change)
    order = [batches[k] for k in sorted(batches)]

    STATE.update(raw=raw, branch=b, fail_closed=fail_closed)
    with Pool(workers or min(4, os.cpu_count() or 1)) as pool:
        outcomes = pool.map(grade_batch, order, chunksize=1)

    problems = []
    for batch, graded in zip(order, outcomes):
        for (case, (node, p, o), new), got in zip(batch, graded):
            if got != ds.DM.Allow:
                continue
            was = base[case][0]
            where = "" if node == case else " on a linked record"
            if new is not None:
                problems.append(f"FC-C {ds.short(case)}: Allow with {ds.short(p)}{where} misspelled")
            elif was != ds.DM.Allow:
                problems.append(f"FC-A {ds.short(case)}: {ds.label(was)}, but Allow without {ds.short(p)}{where}")
            elif p in required.get(node, ()) and not any(v != o for v in raw.objects(node, p)):
                problems.append(f"FC-B {ds.short(case)}: Allow without {ds.short(p)}{where}, which is required")
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
                "P25_FounderPayPlusBenefits", "D14_PackageOverMarket"}
        _, n, nb, problems = check("A", fail_closed=False, only=only)
        kinds = {p.split()[0] for p in problems}
        caught = {c for c in only if any(c in p for p in problems)}
        print(f"selftest, FC0 off: {n} copies in {nb} graphs, {len(problems)} fail-opens caught "
              f"({', '.join(sorted(kinds))})")
        for p in problems:
            print("  " + p)
        want = {"FC-A", "FC-B", "FC-C"}
        linked = any("linked record" in p for p in problems)
        ok = caught == only and kinds == want and linked
        print("selftest " + ("passed: the test catches missing facts, missing facts on linked records "
                             "and misspelled values in every model." if ok
                             else f"FAILED: missed {sorted(only - caught) or sorted(want - kinds) or 'a linked record'}"))
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
