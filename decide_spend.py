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

Planned gifts (tests/decision/planned-giving-cases.ttl) are graded by
decision/planned-giving-shapes.ttl: lead trusts, remainder unitrusts, business
interests, the estate exception, a residence trust, bargain sales and the
foundation's own payout. decision/planned-giving-model.ttl records the Code and
regulations behind each check, with the GiftLaw Pro sections as secondary sources.

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
from rdflib import BNode, Graph, Namespace, URIRef, RDF, Literal
from rdflib.namespace import XSD
from pyshacl import validate
import fast_sparql  # noqa: F401  (parse each SPARQL text once; same answers, faster)

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
model.parse(HERE / "decision/planned-giving-model.ttl", format="turtle")
shapes = Graph()
shapes.parse(HERE / "trust-domain-keystone-shapes.ttl", format="turtle")
shapes.parse(HERE / "decision/spend-decision-shapes.ttl", format="turtle")
shapes.parse(HERE / "decision/stewardship-shapes.ttl", format="turtle")
shapes.parse(HERE / "decision/planned-giving-shapes.ttl", format="turtle")
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
    ns = {"dm": DM, "td": TD, "rdf": RDF, "xsd": XSD}
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


def load(b, overrides=None, derived=True):
    data = Graph()
    for f in [HERE / "trust-domain-ontology.ttl", model_file,
              HERE / "decision/stewardship-model.ttl", HERE / "decision/irs-instruments.ttl",
              HERE / "decision/planned-giving-model.ttl", HERE / "tests/decision/planned-giving-cases.ttl",
              HERE / "tests/decision/decision-cases.ttl", HERE / "tests/decision/entity-deal-cases.ttl",
              HERE / "tests/decision/gift-ledger.ttl",
              HERE / BRANCH_FILES[b], *map(Path, extra)]:
        data.parse(f, format="turtle")
    for prop, value in (overrides or {}).items():
        data.set((CASES.FamilyTrust, DM[prop], value))
    return derive(data) if derived else data


REQUIREMENTS = Graph().parse(HERE / "decision/required-inputs.ttl", format="turtle")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
GRADED = (DM.SpendProposal, DM.EntityDeal, DM.PlannedGift)
NUMERIC = {XSD.decimal, XSD.integer, XSD.int, XSD.long, XSD.double, XSD.float,
           XSD.nonNegativeInteger, XSD.positiveInteger}
DATES = {XSD.date}


def graded_cases(data):
    return {c for k in GRADED for c in data.subjects(RDF.type, k)}


def records(data, case):
    """The case and the records it owns: blank nodes it links to, and named nodes it
    links to through a property whose range is an owned record (dm:OwnedRecord, such
    as a benefit on a pay deal). Facts on these count as the case's own facts. A
    record two cases link to is owned by both."""
    owned = owned_record_properties(data)
    out, todo = [case], [case]
    while todo:
        node = todo.pop()
        for p, o in data.predicate_objects(node):
            if (isinstance(o, BNode) or (p in owned and isinstance(o, URIRef))) and o not in out:
                out.append(o)
                todo.append(o)
    return out


def owned_record_properties(data):
    """Properties whose range is dm:OwnedRecord or a subclass of it."""
    kinds, todo = set(), [DM.OwnedRecord]
    while todo:
        k = todo.pop()
        if k not in kinds:
            kinds.add(k)
            todo.extend(data.subjects(RDFS.subClassOf, k))
    return {p for k in kinds for p in data.subjects(RDFS.range, k)}


def required_inputs(data):
    """Each node an input requirement covers, with the facts it must state, and the
    cases that own it: ({node: {property, ...}}, {node: {case, ...}}). A requirement whose
    pattern binds ?case is about a record the case links to (?this is the record)."""
    required, owner = defaultdict(set), defaultdict(set)
    for req in REQUIREMENTS.subjects(RDF.type, DM.InputRequirement):
        pattern = str(REQUIREMENTS.value(req, DM.appliesWhen))
        linked = "?case" in pattern
        q = (f"PREFIX : <{DM}> SELECT DISTINCT ?this {'?case' if linked else ''} "
             f"WHERE {{ {pattern} }}")
        props = set(REQUIREMENTS.objects(req, DM.requiresInput))
        for row in data.query(q):
            required[row[0]] |= props
            owner[row[0]].add(row[1] if linked else row[0])
    return required, owner


def missing_inputs(data):
    """Fail closed: the required facts each case leaves out, on itself or on a record
    it owns: {case: {property, ...}}. Any case listed gets check FC0, Insufficient."""
    required, owner = required_inputs(data)
    missing = defaultdict(set)
    for node, props in required.items():
        gone = {p for p in props if data.value(node, p) is None}
        if gone:
            for case in owner[node]:
                missing[case] |= gone
    return dict(missing)


def unknown_terms(data):
    """Fail closed on a fact that is there but means nothing to the checks: a check
    that compares a value to a known term silently skips a misspelled one. For every
    fact on a case or a record it owns: the property must be declared; a value of a
    closed list (owl:oneOf) must be on the list; a value of any other declared range
    must be declared a member of it; any other named value must be declared at all;
    a named term may not be written as text; a yes/no must be a boolean, an amount
    a number and a date a date. Returns ({case: {property, ...}},
    {malformed literal facts}); the run sets the malformed ones aside before the checks,
    since a comparison or a sum over text would stop the whole grading."""
    declared_props = {p for t in (OWL.ObjectProperty, OWL.DatatypeProperty, RDF.Property)
                      for p in data.subjects(RDF.type, t)}
    object_props = set(data.subjects(RDF.type, OWL.ObjectProperty))
    sub = defaultdict(set)
    for c, sup in data.subject_objects(RDFS.subClassOf):
        sub[sup].add(c)

    def members(cls):
        lst = data.value(cls, OWL.oneOf)
        if lst is not None:
            return set(data.items(lst))
        seen, todo = set(), [cls]
        while todo:
            k = todo.pop()
            if k not in seen:
                seen.add(k)
                todo.extend(sub[k])
        return {m for k in seen for m in data.subjects(RDF.type, k)}

    cache = {}
    unknown, malformed = defaultdict(set), set()
    for case in graded_cases(data):
        for node in records(data, case):
            for p, o in data.predicate_objects(node):
                if p in (RDF.type, RDFS.label, RDFS.comment) or isinstance(o, BNode):
                    continue
                if p not in declared_props:
                    unknown[case].add(p)
                    continue
                ranges = set(data.objects(p, RDFS.range))
                if isinstance(o, Literal):
                    named = p in object_props or any(not str(c).startswith(str(XSD)) and c != RDFS.Literal
                                                     for c in ranges)
                    if named:      # text where a named term belongs ("LifeThenTerm" for :LifeThenTerm)
                        unknown[case].add(p)
                        malformed.add((node, p, o))
                    elif (XSD.boolean in ranges and (o.datatype != XSD.boolean or o.value not in (True, False))) or \
                            (ranges & NUMERIC and (o.datatype not in NUMERIC or o.value is None)) or \
                            (ranges & DATES and (o.datatype not in DATES or o.value is None)):
                        unknown[case].add(p)
                        malformed.add((node, p, o))
                    continue
                classes = [c for c in ranges if not str(c).startswith(str(XSD)) and c != RDFS.Literal]
                for c in classes:
                    if c not in cache:
                        cache[c] = members(c)
                    if o not in cache[c]:
                        unknown[case].add(p)
                if not classes and data.value(o, RDF.type) is None:
                    unknown[case].add(p)
    return dict(unknown), malformed


SPLIT_PAY_FACTS = ("payee", "fiscalYear", "annualAmount", "benchmarkAnnual")


def split_pay_siblings(data, missing, unknown):
    """Fail closed across cases: H4 sums a payee's pay in a year over every proposal
    that states all four of its facts, so one proposal missing a fact (or stating one
    the checks cannot read) silently drops out of its siblings' sum. Returns the
    proposals whose split-pay total cannot be trusted: {proposal, ...}, each a
    complete proposal sharing the incomplete one's payee and year, or its year when
    the payee is the missing fact, or its payee when the year is."""
    facts = [DM[f] for f in SPLIT_PAY_FACTS]
    known = {}
    for p in data.subjects(RDF.type, DM.SpendProposal):
        pay = (data.value(p, DM.annualAmount) is not None       # a spend that states no
               or data.value(p, DM.benchmarkAnnual) is not None)  # amount is not in any sum
        if pay:
            bad = missing.get(p, set()) | unknown.get(p, set())
            known[p] = {f: (None if f in bad else data.value(p, f)) for f in facts}
    payee, year = DM.payee, DM.fiscalYear
    out = set()
    for x, kx in known.items():
        if all(kx[f] is not None for f in facts):
            continue
        if kx[payee] is None and kx[year] is None:
            continue                               # nothing to tie it to; x itself is FC0
        for y, ky in known.items():
            if y == x or any(ky[f] is None for f in facts):
                continue
            if (kx[payee] is None or kx[payee] == ky[payee]) and (kx[year] is None or kx[year] == ky[year]):
                out.add(y)
    return out


def run(b, overrides=None, data=None, fail_closed=True):
    """Grade every proposal under branch b, or a prepared (derived) graph. Returns (results, data, failed)."""
    data = load(b, overrides) if data is None else data
    unknown, malformed = unknown_terms(data)
    checked = data
    if malformed:                  # set aside text where a yes/no or an amount belongs
        checked = Graph() + data
        for t in malformed:
            checked.remove(t)
    _, report, _ = validate(checked, shacl_graph=shapes, inference="rdfs",
                            advanced=True, allow_warnings=True)
    failed = defaultdict(set)      # focus node -> constraints it failed
    for r in report.subjects(RDF.type, SH.ValidationResult):
        failed[report.value(r, SH.focusNode)].add(report.value(r, SH.sourceConstraint))
    check_of = {}                  # constraint -> (check name, outcome)
    for chk in data.subjects(RDF.type, DM.DecisionCheck):
        c = data.value(chk, DM.checkConstraint)
        if c is not None:
            check_of[c] = (str(c).split("#")[-1].split("_")[0], data.value(chk, DM.onFail))
    missing = missing_inputs(data) if fail_closed else {}
    unknown = unknown if fail_closed else {}
    siblings = split_pay_siblings(data, missing, unknown) if fail_closed else set()
    results = {}
    for p in sorted(graded_cases(data), key=str):
        hits = {}
        for n in [p, *data.objects(p, DM.assesses)]:
            for c in failed.get(n, ()):
                if c in check_of:
                    name, outcome = check_of[c]
                    hits[name] = outcome
        if missing.get(p) or unknown.get(p):   # FC0: a required fact is missing or unknown, so no Allow
            hits["FC0"] = DM.Insufficient
        if p in siblings:                      # FC1: a split-pay sibling is missing or unknown
            hits["FC1"] = DM.Insufficient
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
    print(f"\n{len(set(data.subjects(RDF.type, DM.Instrument)))} instruments, {len(perms)} permissions linked to checks.")

    counts = defaultdict(int)
    for outcome, _ in results.values():
        counts[short(outcome)] += 1
    print(f"\n{len(results)} proposals: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
          + ". Grading: " + ("all match the answer key." if not bad else f"{bad} mismatch(es)."))
    return bad


if __name__ == "__main__":
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
