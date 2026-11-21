#!/usr/bin/env python3
"""
Grade proposed foundation spends, and deals between the founder's roles:
allow, block, needs counsel or insufficient.

  python3 decide_spend.py              worked cases under insider branch A (default)
  python3 decide_spend.py --branch B   the same cases under insider branch B
  python3 decide_spend.py --compare    both branches side by side: what flips
  python3 decide_spend.py --sweep      move the family trust's settings one at a time
  python3 decide_spend.py FILE.ttl     also grade your own proposals

Stage 1 is the existing keystone and cascade check (trust-domain-keystone-shapes.ttl),
run on the node each proposal assesses. Stages 2 and 3 are
decision/spend-decision-shapes.ttl, run on the proposal itself. Each failed check
maps to an outcome in decision/spend-decision-model.ttl; the proposal gets the most
severe one (block > insufficient > needs counsel > allow). A scorer's answer can
only raise an outcome, never lower it.

Entity deals (tests/decision/entity-deal-cases.ttl) are graded the same way by
decision/stewardship-shapes.ttl: stewardship ("own nothing, steward everything"),
arm's length between the founder's roles, what a business may deduct and what an
employee may exclude. decision/irs-instruments.ttl catalogs the IRS publications
those checks come from, linked to roles and checks.

Insider branches: whether the family trust, the business trust and the operating
company are disqualified persons waits on counsel. tests/decision/branch-a.ttl
(over the line, fail closed, the default) and branch-b.ttl (under the line) set
the family trust's facts; the insider rules in decision/spend-decision-model.ttl
derive each role's status from them before the checks run. tests/decision/expected.ttl is the branch A answer key;
expected-branch-b.ttl lists only what branch B changes. Any proposal whose outcome
or failed checks differ from its key, or that has no expectation, makes the run
fail (exit 1).
Not legal or tax advice. Needs: pip install rdflib pyshacl
"""
import sys
from collections import defaultdict
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, RDF, Literal
from rdflib.namespace import XSD
from pyshacl import validate

HERE = Path(__file__).resolve().parent
DM = Namespace("http://example.org/trust-domain/decision#")
T = Namespace("http://example.org/trust-domain/tests#")
SH = Namespace("http://www.w3.org/ns/shacl#")
LABEL = URIRef("http://www.w3.org/2000/01/rdf-schema#label")
BRANCH_FILES = {"A": "tests/decision/branch-a.ttl", "B": "tests/decision/branch-b.ttl"}
BRANCH_KEYS = {"A": ["tests/decision/expected.ttl"],
               "B": ["tests/decision/expected.ttl", "tests/decision/expected-branch-b.ttl"]}

args = sys.argv[1:]
compare = "--compare" in args
sweep = "--sweep" in args
branch = "A"
if "--branch" in args:
    branch = args[args.index("--branch") + 1].upper()
    if branch not in BRANCH_FILES:
        sys.exit(f"unknown branch {branch}: use A or B")
extra = [a for i, a in enumerate(args)
         if not a.startswith("--") and not (i and args[i - 1] == "--branch")]

model_file = HERE / "decision/spend-decision-model.ttl"
model = Graph().parse(model_file, format="turtle")
model.parse(HERE / "decision/stewardship-model.ttl", format="turtle")
shapes = Graph()
shapes.parse(HERE / "trust-domain-keystone-shapes.ttl", format="turtle")
shapes.parse(HERE / "decision/spend-decision-shapes.ttl", format="turtle")
shapes.parse(HERE / "decision/stewardship-shapes.ttl", format="turtle")
severity = {o: int(model.value(o, DM.severity)) for o in model.subjects(RDF.type, DM.Outcome)}
by_severity = {v: k for k, v in severity.items()}
short = lambda u: str(u).split("#")[-1]
label = lambda o: str(model.value(o, LABEL))


def answer_key(b):
    key = {}
    for f in BRANCH_KEYS[b]:          # later files override earlier ones
        g = Graph().parse(HERE / f, format="turtle")
        for s in set(g.subjects()):
            key[s] = (g.value(s, T.expectOutcome), set(str(g.value(s, T.expectChecks) or "").split()))
    return key


TD = Namespace("http://example.org/trust-domain#")
CASES = Namespace("http://example.org/trust-domain/decision-cases#")
RULES = sorted(model.subjects(RDF.type, DM.InsiderRule), key=str)


def derive(data):
    """Insider rules: stage 1 to a fixed point, then stage 2 once."""
    ns = {"dm": DM, "td": TD, "rdf": RDF}
    for stage in (1, 2):
        rules = [r for r in RULES if int(model.value(r, DM.ruleStage)) == stage]
        while True:
            before = len(data)
            for r in rules:
                for t in data.query(str(model.value(r, DM.construct)), initNs=ns):
                    data.add(t)
            if stage == 2 or len(data) == before:
                break
    return data


def load(b, overrides=None):
    data = Graph()
    for f in [HERE / "trust-domain-ontology.ttl", model_file,
              HERE / "decision/stewardship-model.ttl", HERE / "decision/irs-instruments.ttl",
              HERE / "tests/decision/decision-cases.ttl", HERE / "tests/decision/entity-deal-cases.ttl",
              HERE / BRANCH_FILES[b], *map(Path, extra)]:
        data.parse(f, format="turtle")
    for prop, value in (overrides or {}).items():
        data.set((CASES.FamilyTrust, DM[prop], value))
    return derive(data)


def run(b, overrides=None):
    """Grade every proposal under branch b. Returns (results, data, failed)."""
    data = load(b, overrides)
    _, report, _ = validate(data, shacl_graph=shapes, inference="rdfs",
                            advanced=True, allow_warnings=True)
    failed = defaultdict(set)      # focus node -> constraints it failed
    for r in report.subjects(RDF.type, SH.ValidationResult):
        failed[report.value(r, SH.focusNode)].add(report.value(r, SH.sourceConstraint))
    check_of = {}                  # constraint -> (check name, outcome)
    for chk in data.subjects(RDF.type, DM.DecisionCheck):
        c = data.value(chk, DM.checkConstraint)
        if c is not None:
            check_of[c] = (str(c).split("#")[-1].split("_")[0], data.value(chk, DM.onFail))
    results = {}
    graded = set(data.subjects(RDF.type, DM.SpendProposal)) | set(data.subjects(RDF.type, DM.EntityDeal))
    for p in sorted(graded, key=str):
        hits = {}
        for n in [p, *data.objects(p, DM.assesses)]:
            for c in failed.get(n, ()):
                if c in check_of:
                    name, outcome = check_of[c]
                    hits[name] = outcome
        worst = max([0, *(severity[o] for o in hits.values())])
        results[p] = (by_severity[worst], set(hits))
    return results, data, failed


def grade(b):
    results, data, failed = run(b)
    key = answer_key(b)
    bad = 0
    print(f"Insider branch {b}\n{'proposal':34} {'outcome':14} failed checks")
    for p, (outcome, checks) in results.items():
        exp = key.get(p)
        note = ""
        if exp is None or exp[0] is None:
            note, bad = "  <-- no expectation in the answer key", bad + 1
        elif (outcome, checks) != exp:
            note, bad = f"  <-- expected {short(exp[0])} {' '.join(sorted(exp[1])) or '-'}", bad + 1
        print(f"{short(p):34} {label(outcome):14} {' '.join(sorted(checks)) or '-'}{note}")

    print("\nchecks enforced only by conscience (P1):")
    p1 = DM.P1_EnforcedBeyondConscience
    for chk in sorted(set(data.subjects(RDF.type, DM.DecisionCheck)), key=str):
        got = {"P1"} if p1 in failed.get(chk, ()) else set()
        exp = key.get(chk, (None, set()))[1]
        if got or exp:
            ok = got == exp
            bad += 0 if ok else 1
            print(f"  {short(chk):26} {'FAIL P1' if got else 'pass'}"
                  f"{'' if ok else '  <-- expected ' + (' '.join(sorted(exp)) or 'pass')}")

    # every instrument permission must point at checks that exist, and name its evidence
    q = """SELECT ?perm ?chk WHERE { ?perm a dm:Permission ; dm:becomesCheck ?chk .
                                    FILTER NOT EXISTS { ?chk a dm:DecisionCheck } }"""
    for perm, chk in data.query(q, initNs={"dm": DM}):
        bad += 1
        print(f"  instrument {short(perm)} points at missing check {short(chk)}")
    perms = set(data.subjects(RDF.type, DM.Permission))
    for perm in perms:
        if data.value(perm, DM.evidence) is None:
            bad += 1
            print(f"  instrument {short(perm)} has no evidence grade")
    print(f"\n{len(set(data.subjects(RDF.type, DM.Instrument)))} IRS instruments, {len(perms)} permissions linked to checks.")

    counts = defaultdict(int)
    for outcome, _ in results.values():
        counts[short(outcome)] += 1
    print(f"\n{len(results)} proposals: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
          + ". Grading: " + ("all match the answer key." if not bad else f"{bad} mismatch(es)."))
    return bad


if sweep:
    pct = lambda v: Literal(str(v), datatype=XSD.decimal)
    yes = lambda v: Literal(v)
    watch = [CASES.P22_RentFromFamilyTrust, CASES.P23_OperatingCoPurchase,
             CASES.P24_GrantToFamilyTrust, CASES.P14_OperatingCoShares]
    rows = [("family 0%, siblings 30%", {"dqFamilySharePercent": pct(0)}),
            ("family 30%, siblings 30%", {}),
            ("family 35%", {"dqFamilySharePercent": pct(35)}),
            ("family 36%", {"dqFamilySharePercent": pct(36)}),
            ("family 60%", {"dqFamilySharePercent": pct(60), "otherRelativeSharePercent": pct(0)}),
            ("family 30%, trust is a substantial contributor", {"substantialContributor": yes(True)}),
            ("family 30%, trustee paid", {"trusteePaid": yes(True)}),
            ("family 30%, deduction allowed, foundation remainder only",
             {"charitableDeductionAllowed": yes(True), "foundationInterestKind": DM.RemainderOnly})]
    print("Sweep from branch B; one setting changes per row.\n")
    print(f"{'family trust settings':58} {'insider':8} " + "  ".join(f"{short(p).split('_')[0]:22}" for p in watch)
          + "  4943 % (foundation / insiders)")
    for name, ov in rows:
        res, data, _ = run("B", ov)
        insider = "yes" if (CASES.FamilyTrust, RDF.type, TD.DisqualifiedPerson) in data else "no"
        cells = [f"{label(res[p][0])} {' '.join(sorted(res[p][1])) or ''}".strip() for p in watch]
        p14 = CASES.P14_OperatingCoShares
        held = f"{float(data.value(p14, DM.foundationVotingPercentAfter)):g} / {float(data.value(p14, DM.disqualifiedVotingPercent)):g}"
        print(f"{name:58} {insider:8} " + "  ".join(f"{c:22}" for c in cells) + "  " + held)
    sys.exit(0)

if compare:
    a, _, _ = run("A")
    b, _, _ = run("B")
    flips = [p for p in a if a[p] != b.get(p)]
    print(f"{'proposal':34} {'branch A':24} branch B")
    for p in flips:
        fa = f"{label(a[p][0])} {' '.join(sorted(a[p][1])) or '-'}"
        fb = f"{label(b[p][0])} {' '.join(sorted(b[p][1])) or '-'}"
        print(f"{short(p):34} {fa:24} {fb}")
    print(f"\n{len(flips)} of {len(a)} proposals change between branches; "
          f"{sum(1 for p in flips if a[p][0] != b[p][0])} change outcome.")
    sys.exit(0)

sys.exit(1 if grade(branch) else 0)
