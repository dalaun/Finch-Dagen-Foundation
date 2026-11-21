#!/usr/bin/env python3
"""
Grade proposed foundation spends: allow, block, needs counsel or insufficient.

  python3 decide_spend.py            worked cases, graded against the answer key
  python3 decide_spend.py FILE.ttl   also grade your own proposals

Stage 1 is the existing keystone and cascade check (trust-domain-keystone-shapes.ttl),
run on the node each proposal assesses. Stages 2 and 3 are
decision/spend-decision-shapes.ttl, run on the proposal itself. Each failed check
maps to an outcome in decision/spend-decision-model.ttl; the proposal gets the most
severe one (block > insufficient > needs counsel > allow). A scorer's answer can
only raise an outcome, never lower it.

tests/decision/expected.ttl is the answer key. Any proposal whose outcome or failed
checks differ from it, or that has no expectation, makes the run fail (exit 1).
Not legal or tax advice. Needs: pip install rdflib pyshacl
"""
import sys
from collections import defaultdict
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, RDF
from pyshacl import validate

HERE = Path(__file__).resolve().parent
DM = Namespace("http://example.org/trust-domain/decision#")
T = Namespace("http://example.org/trust-domain/tests#")
SH = Namespace("http://www.w3.org/ns/shacl#")

model_file = HERE / "decision/spend-decision-model.ttl"
data = Graph()
for f in [HERE / "trust-domain-ontology.ttl", model_file,
          HERE / "tests/decision/decision-cases.ttl", *map(Path, sys.argv[1:])]:
    data.parse(f, format="turtle")
shapes = Graph()
shapes.parse(HERE / "trust-domain-keystone-shapes.ttl", format="turtle")
shapes.parse(HERE / "decision/spend-decision-shapes.ttl", format="turtle")
model = Graph().parse(model_file, format="turtle")
expected_g = Graph().parse(HERE / "tests/decision/expected.ttl", format="turtle")

conforms, report, _ = validate(data, shacl_graph=shapes, inference="rdfs",
                               advanced=True, allow_warnings=True)

failed = defaultdict(set)      # focus node -> constraints it failed
for r in report.subjects(RDF.type, SH.ValidationResult):
    failed[report.value(r, SH.focusNode)].add(report.value(r, SH.sourceConstraint))

# constraint -> (check name, outcome); outcome -> severity
check_of = {}
for chk in data.subjects(RDF.type, DM.DecisionCheck):
    c = data.value(chk, DM.checkConstraint)
    if c is not None:
        check_of[c] = (str(c).split("#")[-1].split("_")[0], data.value(chk, DM.onFail))
severity = {o: int(model.value(o, DM.severity)) for o in model.subjects(RDF.type, DM.Outcome)}
by_severity = {v: k for k, v in severity.items()}
short = lambda u: str(u).split("#")[-1]

def decide(p):
    nodes = [p, *data.objects(p, DM.assesses)]
    hits = {}
    for n in nodes:
        for c in failed.get(n, ()):
            if c in check_of:
                name, outcome = check_of[c]
                hits[name] = outcome
    worst = max([0, *(severity[o] for o in hits.values())])
    return by_severity[worst], set(hits)

bad = 0
print(f"{'proposal':28} {'outcome':14} failed checks")
proposals = sorted(set(data.subjects(RDF.type, DM.SpendProposal)), key=str)
for p in proposals:
    outcome, checks = decide(p)
    exp_o = expected_g.value(p, T.expectOutcome)
    exp_c = set(str(expected_g.value(p, T.expectChecks) or "").split())
    note = ""
    if exp_o is None:
        note, bad = "  <-- no expectation in tests/decision/expected.ttl", bad + 1
    elif outcome != exp_o or checks != exp_c:
        note, bad = f"  <-- expected {short(exp_o)} {' '.join(sorted(exp_c)) or '-'}", bad + 1
    print(f"{short(p):28} {model.value(outcome, URIRef('http://www.w3.org/2000/01/rdf-schema#label')):14} "
          f"{' '.join(sorted(checks)) or '-'}{note}")

# Checks on the checks (P1: every check enforced by more than conscience)
print("\nchecks enforced only by conscience (P1):")
p1 = DM.P1_EnforcedBeyondConscience
for chk in sorted(set(data.subjects(RDF.type, DM.DecisionCheck)), key=str):
    got = {"P1"} if p1 in failed.get(chk, ()) else set()
    exp = set(str(expected_g.value(chk, T.expectChecks) or "").split())
    if got or exp:
        mark = "" if got == exp else f"  <-- expected {' '.join(sorted(exp)) or 'pass'}"
        bad += 0 if got == exp else 1
        print(f"  {short(chk):26} {'FAIL P1' if got else 'pass'}{mark}")

counts = defaultdict(int)
for p in proposals:
    counts[short(decide(p)[0])] += 1
print(f"\n{len(proposals)} proposals: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
      + ". Grading: " + ("all match the answer key." if not bad else f"{bad} mismatch(es)."))
sys.exit(1 if bad else 0)
