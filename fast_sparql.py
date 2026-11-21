"""
Parse each SPARQL text once.

pyshacl runs every SPARQL check once per case, and rdflib parses the query text
again on every run. On the decision model that parsing was about four fifths of
the time a grading took. Importing this module makes rdflib keep the parsed form
of each text and reuse it. The query, the data and the answers are the same; only
the repeated parsing goes away. Every grading still has to match its answer key,
so a difference would fail CI.

Only plain SPARQL text queries are cached, with no options beyond initBindings and
initNs. Anything else, or a text that does not parse on its own, goes to rdflib
unchanged.
"""
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

_query = Graph.query
_parsed = {}


def _query_once(self, query_object, processor="sparql", result="sparql", initNs=None,  # noqa: N803
                initBindings=None, use_store_provided=True, **kwargs):  # noqa: N803
    if (not isinstance(query_object, str) or processor != "sparql" or result != "sparql"
            or kwargs):
        return _query(self, query_object, processor, result, initNs, initBindings,
                      use_store_provided, **kwargs)
    ns = dict(initNs) if initNs else dict(self.namespaces())
    key = (query_object, frozenset((k, str(v)) for k, v in ns.items()))
    if key not in _parsed:
        try:
            _parsed[key] = prepareQuery(query_object, initNs=ns)
        except Exception:
            _parsed[key] = None
    if _parsed[key] is None:
        return _query(self, query_object, processor, result, ns, initBindings, use_store_provided)
    return _query(self, _parsed[key], processor, result, None, initBindings, use_store_provided)


Graph.query = _query_once
