#!/usr/bin/env python3
"""
OWL lint: catches three modeling mistakes a reasoner will quietly accept.

  L1  owl:hasValue points at a class. hasValue names one individual, so
      "governed by hasValue :Pub_15" reads as "governed by a single thing
      named Pub_15", not "governed by some Pub 15 rule". Use
      owl:someValuesFrom for a class.
  L2  A restriction is placed on rdf:type. rdf:type is OWL's own vocabulary
      and is not allowed as a restriction property in OWL 2 DL. Use the
      class itself as the filler instead.
  L3  One restriction carries more than one owl:onProperty. That is a
      malformed restriction; split it into one restriction per property.

Usage: python3 validate_owl_lint.py [file.ttl ...]
With no arguments it checks every .ttl file in the repo root.
Exits 1 if any problem is found, so CI can block the merge.
"""

import glob
import sys

from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS


def is_class(g, node):
    return (node, RDF.type, OWL.Class) in g or (node, RDF.type, RDFS.Class) in g


def lint(path):
    g = Graph()
    g.parse(path, format="turtle")
    problems = []

    for restriction, value in g.subject_objects(OWL.hasValue):
        if isinstance(value, URIRef) and is_class(g, value):
            prop = g.value(restriction, OWL.onProperty)
            problems.append(
                f"L1 hasValue points at class {g.qname(value)}"
                f" (on {g.qname(prop) if prop else '?'}); use owl:someValuesFrom"
            )

    for restriction in g.subjects(OWL.onProperty, RDF.type):
        problems.append("L2 restriction on rdf:type; use the class itself as the filler")

    for restriction in set(g.subjects(OWL.onProperty, None)):
        props = list(g.objects(restriction, OWL.onProperty))
        if len(props) > 1:
            names = ", ".join(g.qname(p) if isinstance(p, URIRef) else "[inverse]" for p in props)
            problems.append(f"L3 one restriction has {len(props)} onProperty values ({names}); split it")

    return problems


def main(argv):
    files = argv[1:] or sorted(glob.glob("*.ttl"))
    total = 0
    for path in files:
        problems = lint(path)
        total += len(problems)
        status = "ok" if not problems else f"{len(problems)} problem(s)"
        print(f"{path}: {status}")
        for p in problems:
            print(f"  {p}")
    print(f"\nOWL lint: {len(files)} file(s), {total} problem(s).")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
