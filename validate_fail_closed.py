#!/usr/bin/env python3
"""
Fail-closed check: a case missing a fact the checks need is never graded Allow.

A SPARQL check fires only when every triple it matches is there, so a missing
fact can silently switch a check off, and a case with no failed checks is
graded Allow. This test tries that on purpose. For every worked case (spends,
entity deals, planned gifts) it makes one copy per stated fact with that one
fact deleted, grades every copy with decide_spend.py, and fails if a copy is
graded Allow when either

  FC-A  the case itself is not Allow (deleting a fact loosened it), or
  FC-B  the deleted fact is one decision/required-inputs.ttl requires of this
        case, and the case states no other value of it (check FC0 should have
        made it Insufficient).

A copy of an Allow case that loses a fact no requirement names may stay Allow:
that fact was optional (an election, a note, a later year).

Facts deleted: every fact stated on the case (values and links to parties,
vehicles and acts) except its type, labels, comments and notes.
The copies sit in one graph beside the real cases, so a check that sums across
cases (H4, split pay) also sees them; that can only make a copy stricter.

  python3 validate_fail_closed.py              both insider branches
  python3 validate_fail_closed.py --branch A   one branch
  python3 validate_fail_closed.py --selftest   with FC0 switched off, show the test catches fail-opens

Exits 1 on any FC problem, so CI can block the merge. Not legal or tax advice.
"""
import sys
import time

args = sys.argv[1:]
sys.argv = sys.argv[:1]          # decide_spend reads its own flags at import
import decide_spend as ds        # noqa: E402
from rdflib import URIRef  # noqa: E402
from rdflib.namespace import RDF, RDFS  # noqa: E402

SKIP = {RDF.type, RDFS.label, RDFS.comment}


def mutate(g, cases):
    """Add one copy of each case per stated fact, without that fact. Returns {copy: (case, property)}."""
    copies = {}
    for case in cases:
        facts = [(p, o) for p, o in g.predicate_objects(case) if p not in SKIP and "Note" not in str(p)]
        for k, (gone_p, gone_o) in enumerate(facts):
            copy = URIRef(f"{case}__without_{ds.short(gone_p)}_{k}")
            for p, o in list(g.predicate_objects(case)):
                if (p, o) != (gone_p, gone_o):
                    g.add((copy, p, o))
            for s, p in list(g.subject_predicates(case)):
                g.add((s, p, copy))
            # FC-B asks whether the property is now missing; a case with two values of it keeps the other.
            still_there = any(p == gone_p for p, _ in facts if (p, _) != (gone_p, gone_o))
            copies[copy] = (case, gone_p, still_there)
    return copies


def check(b, fail_closed=True, only=None):
    base, _, _ = ds.run(b, fail_closed=fail_closed)
    raw = ds.load(b, derived=False)
    required = ds.required_inputs(ds.derive(ds.load(b, derived=False)))
    cases = [c for c in base if only is None or ds.short(c) in only]
    copies = mutate(raw, cases)
    graded, _, _ = ds.run(b, data=ds.derive(raw), fail_closed=fail_closed)
    problems = []
    for copy, (case, prop, still_there) in sorted(copies.items(), key=str):
        if graded[copy][0] != ds.DM.Allow:
            continue
        was = base[case][0]
        if was != ds.DM.Allow:
            problems.append(f"FC-A {ds.short(case)}: {ds.label(was)}, but Allow without {ds.short(prop)}")
        elif prop in required.get(case, ()) and not still_there:
            problems.append(f"FC-B {ds.short(case)}: Allow without {ds.short(prop)}, which is required")
    return len(cases), len(copies), problems


def main():
    if "--selftest" in args:
        # FC0 off, on cases each known to fail open without it (one per model).
        only = {"D30_FamilyVacation", "G01_LeadAnnuityClean", "G29_UnitrustMortgagedLand", "P25_FounderPayPlusBenefits"}
        _, n, problems = check("A", fail_closed=False, only=only)
        kinds = {p.split()[0] for p in problems}
        caught = {c for c in only if any(c in p for p in problems)}
        print(f"selftest, FC0 off: {n} copies, {len(problems)} fail-opens caught ({', '.join(sorted(kinds))})")
        for p in problems:
            print("  " + p)
        ok = caught == only and kinds == {"FC-A", "FC-B"}
        print("selftest " + ("passed: the test catches fail-opens in every model." if ok
                             else f"FAILED: missed {sorted(only - caught) or sorted({'FC-A', 'FC-B'} - kinds)}"))
        return 0 if ok else 1

    branches = [args[args.index("--branch") + 1].upper()] if "--branch" in args else ["A", "B"]
    bad = 0
    for b in branches:
        t = time.time()
        n, m, problems = check(b)
        print(f"Insider branch {b}: {n} cases, {m} copies each missing one fact, "
              f"{len(problems)} graded Allow when they must not be ({time.time() - t:.0f}s)")
        for p in problems:
            print("  " + p)
        bad += len(problems)
    print("Fail closed: " + ("no case is Allow on a missing fact." if not bad else f"{bad} problem(s)."))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
