# 04. Ontology sketch and answer key

[Back to the rehearsal overview](README.md)

Files: [rehearsal-ontology.ttl](rehearsal-ontology.ttl) (terms) and [answer-key-cases.ttl](answer-key-cases.ttl) (the eval). Both parse as Turtle. Neither is loaded by the keystone check yet, so they cannot break CI.

## The shape, in one line

A **ledger line** (something that happened) is sorted into an **expense domain**, gets candidate **routes** (layer + paying entity + instrument + evidence), each route is checked by **gates**, and a **rehearsal run** records which route won, or that there was **no route yet** and what would be needed.

## Reuse before invention

| Need | Term used | Source |
|---|---|---|
| Expense domain | `td:ExpenseDomain` | Trust-domain core |
| Instrument, IRC section | `td:Instrument`, `td:IRCSection` | Trust-domain core |
| Evidence | `td:Evidence` | Trust-domain core |
| Insider | `td:DisqualifiedPerson` | Trust-domain core |
| Asset | `td:Asset`, new `rh:HeldAsset` adds who holds it | Trust-domain core + new |
| Line, run, step, gate result, professional decision | new, each `rdfs:subClassOf gist:Event` | gist |
| Entity | new `rh:Entity`, `rdfs:subClassOf gist:Organization` | gist |
| Layer, arm, verdict, tax classification, step outcome | new, each a `gist:Category` | gist |
| Route | new, `gist:Content` (a claim to test) | gist |
| Evidence requirement, gate | new, `gist:Specification` | gist |

## Northstar alignment (proposed, unverified)

Northstar's primitives are Actor, Event and Asset. The core file that defines them lives in another repository and was not read for this sketch. The intended mapping: entities and people are Actors; ledger lines, runs, steps and gate results are Events; held assets are Assets. A later pull request can import the Northstar core and replace these comments with real subclass links.

## The answer key

Each case is a synthetic line with a proposed layer, an expected verdict (pass, amber, fail, or no route yet) and the citation that settles it. The twin is graded on exact agreement. Two grades matter over time:

1. **Evidence now:** did the twin reach the verdict the law gives, from the evidence linked?
2. **Outcome later:** when a real return is filed or a professional answers, did the twin's verdict hold? Each professional decision is recorded as an event, so the history itself becomes the grader.

Section citations are kept as text, not as links to the section classes, so the sketch does not repeat the core's open issue of using classes as values.
