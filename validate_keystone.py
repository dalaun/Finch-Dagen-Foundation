#!/usr/bin/env python3
"""
Run the keystone and authority-cascade checks and grade them.

  python3 validate_keystone.py            core ontology + probe cases, graded
  python3 validate_keystone.py FILE.ttl   also check your own data file(s)

Each private enablement, payment, authorized activity, asset, grant, participant record and trust is checked
by trust-domain-keystone-shapes.ttl (SHACL). A node passes when it has no
violation. Verdicts are derived from linked evidence; nothing passes by
category or label. tests/keystone/expected.ttl is the answer key: any node
that fails differently from it, or that is checked but has no expectation,
makes the run fail (exit code 1).
Needs: pip install rdflib pyshacl
"""
import sys
from collections import defaultdict
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, RDF
from pyshacl import validate
import fast_sparql  # noqa: F401  (parse each SPARQL text once; same answers, faster)

HERE = Path(__file__).resolve().parent
TD = Namespace("http://example.org/trust-domain#")
T = Namespace("http://example.org/trust-domain/tests#")
SH = Namespace("http://www.w3.org/ns/shacl#")

data = Graph()
for f in [HERE / "trust-domain-ontology.ttl", HERE / "tests/keystone/keystone-probes.ttl", *map(Path, sys.argv[1:])]:
    data.parse(f, format="turtle")
shapes = Graph().parse(HERE / "trust-domain-keystone-shapes.ttl", format="turtle")
expected_g = Graph().parse(HERE / "tests/keystone/expected.ttl", format="turtle")

conforms, report, _ = validate(data, shacl_graph=shapes, inference="rdfs",
                               advanced=True, allow_warnings=True)

failed = defaultdict(set)
for r in report.subjects(RDF.type, SH.ValidationResult):
    failed[report.value(r, SH.focusNode)].add(report.value(r, SH.sourceConstraint))

# Every node any shape targets, so passes are listed too (same inference as the run)
from pyshacl.rdfutil import clone_graph
import owlrl
closed = clone_graph(data)
owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(closed)
checked = set(closed.query("""
  PREFIX td: <http://example.org/trust-domain#>
  SELECT ?n WHERE {
    { ?n a td:PrivateEnablement FILTER NOT EXISTS { ?n a td:ExpenseDomain } }
    UNION { ?n a td:ActualSpend } UNION { ?n a td:AuthorizedActivity } UNION { ?n a td:Asset } UNION { ?n a td:Grant } UNION { ?n a td:ParticipantRecord }
    UNION { ?n td:hasPurpose ?p } }"""))
checked = {row[0] for row in checked if isinstance(row[0], URIRef)} | set(failed)

expected = defaultdict(set)
for n, _, c in expected_g.triples((None, T.expectFail, None)):
    if c != T.none:
        expected[n].add(c)
known = set(expected_g.subjects(T.expectFail, None))

short = lambda u: str(u).split("#")[-1]
bad = 0
print(f"{'node':40} {'verdict':8} failed checks")
for n in sorted(checked, key=str):
    got = failed.get(n, set())
    verdict = "PASS" if not got else "FAIL"
    note = ""
    if n not in known:
        note, bad = "  <-- no expectation in tests/keystone/expected.ttl", bad + 1
    elif got != expected[n]:
        note, bad = f"  <-- expected {sorted(map(short, expected[n])) or 'pass'}", bad + 1
    print(f"{short(n):40} {verdict:8} {' '.join(sorted(short(c).split('_')[0] for c in got))}{note}")
missing = known - checked
for n in sorted(missing, key=str):
    print(f"{short(n):40} MISSING  in answer key but not checked"); bad += 1

print(f"\n{len(checked)} nodes checked, {sum(1 for n in checked if not failed.get(n))} pass, "
      f"{sum(1 for n in checked if failed.get(n))} fail. Grading: "
      + ("all match the answer key." if not bad else f"{bad} mismatch(es)."))
sys.exit(1 if bad else 0)
