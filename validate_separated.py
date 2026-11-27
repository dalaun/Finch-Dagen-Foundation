#!/usr/bin/env python3
"""
Validate separated ontologies (vocabulary + compliance)
"""

from rdflib import Graph

print("=" * 80)
print("VALIDATING SEPARATED ONTOLOGIES")
print("=" * 80)

# 1. Validate vocabulary ontology
print("\n1. Validating trust-domain-vocabulary.ttl (SEMANTIC LAYER)...")
vocab = Graph()
try:
    vocab.parse("trust-domain-vocabulary.ttl", format="turtle")
    print(f"   ✓ Valid Turtle syntax")
    print(f"   ✓ Total triples: {len(vocab)}")

    # Check no authority axioms leaked in
    from rdflib import OWL
    functional_count = len(list(vocab.triples((None, None, OWL.FunctionalProperty))))
    disjoint_count = len(list(vocab.triples((None, OWL.disjointWith, None))))

    print(f"   - Functional properties: {functional_count} (should be 0)")
    print(f"   - Disjointness axioms: {disjoint_count} (should be 0)")

    if functional_count > 0 or disjoint_count > 0:
        print("   ✗ FAILED: Authority axioms found in vocabulary layer!")
        exit(1)
    else:
        print("   ✓ Clean semantic layer (no authority axioms)")

except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

# 2. Validate compliance ontology
print("\n2. Validating trust-domain-compliance.ttl (AUTHORITY LAYER)...")
compliance = Graph()
try:
    compliance.parse("trust-domain-compliance.ttl", format="turtle")
    print(f"   ✓ Valid Turtle syntax")
    print(f"   ✓ Total triples: {len(compliance)}")

    # Check it has authority axioms
    from rdflib import OWL, RDFS
    functional_count = len(list(compliance.triples((None, None, OWL.FunctionalProperty))))
    disjoint_count = len(list(compliance.triples((None, OWL.disjointWith, None))))

    print(f"   - Functional properties: {functional_count}")
    print(f"   - Disjointness axioms: {disjoint_count}")

    if functional_count == 0 and disjoint_count == 0:
        print("   ✗ FAILED: No authority axioms found!")
        exit(1)
    else:
        print("   ✓ Contains authority axioms")

except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

# 3. Test importing compliance into vocabulary
print("\n3. Testing compliance imports vocabulary...")
combined = Graph()
try:
    # Load vocabulary first
    combined.parse("trust-domain-vocabulary.ttl", format="turtle")
    vocab_triples = len(combined)

    # Load compliance (which should import vocabulary)
    combined.parse("trust-domain-compliance.ttl", format="turtle")
    total_triples = len(combined)

    print(f"   ✓ Combined successfully")
    print(f"   - Vocabulary: {vocab_triples} triples")
    print(f"   - Total after compliance: {total_triples} triples")
    print(f"   - Compliance adds: {total_triples - vocab_triples} triples")

except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

# 4. Compare with original
print("\n4. Comparing with original ontology...")
original = Graph()
try:
    original.parse("trust-domain-estate-planning.ttl", format="turtle")
    original_count = len(original)

    print(f"   - Original: {original_count} triples")
    print(f"   - Combined (vocab + compliance): {total_triples} triples")
    print(f"   - Difference: {abs(total_triples - original_count)} triples")

    # A count can hide lost content (the v3 split lost 8 property-chain
    # triples and still looked close). Compare content instead: expand every
    # blank node (lists, restrictions) into its full structure, skip the
    # ontology header, and ignore explicit "a owl:Class" on anonymous classes.
    from rdflib import BNode, RDF, OWL

    def expand(node, g, seen=()):
        if not isinstance(node, BNode) or node in seen:
            return node
        return tuple(sorted(
            (str(p), str(expand(o, g, seen + (node,))))
            for p, o in g.predicate_objects(node)
            if not (p == RDF.type and o == OWL.Class)))

    def content(g):
        headers = set(g.subjects(RDF.type, OWL.Ontology))
        return {(s, p, expand(o, g)) for s, p, o in g
                if not isinstance(s, BNode) and s not in headers}

    combined_g = Graph()
    combined_g.parse("trust-domain-vocabulary.ttl", format="turtle")
    combined_g.parse("trust-domain-compliance.ttl", format="turtle")
    lost = content(original) - content(combined_g)
    added = content(combined_g) - content(original)
    print(f"   - Statements in original but not in split: {len(lost)}")
    print(f"   - Statements in split but not in original: {len(added)}")
    for s, p, o in sorted(lost, key=str)[:10]:
        print(f"     lost:  {s.split('#')[-1]} {p.split('#')[-1]}")
    for s, p, o in sorted(added, key=str)[:10]:
        print(f"     added: {s.split('#')[-1]} {p.split('#')[-1]}")
    if lost or added:
        print("   ✗ Split does not carry the same content as the original")
        exit(1)
    print("   ✓ Same content as the original (header and anonymous-class typing aside)")

except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

print("\n" + "=" * 80)
print("VALIDATION COMPLETE ✓")
print("=" * 80)
print("\nSummary:")
print(f"  • Vocabulary (semantic): {vocab_triples} triples")
print(f"  • Compliance (authority): {total_triples - vocab_triples} triples")
print(f"  • Total when combined: {total_triples} triples")
print(f"  • Original ontology: {original_count} triples")
print("\nThe ontology has been successfully separated into:")
print("  1. trust-domain-vocabulary.ttl (data-centric - what things mean)")
print("  2. trust-domain-compliance.ttl (operational - what is allowed)")
