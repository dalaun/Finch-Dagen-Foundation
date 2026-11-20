# The Keystone Constraint

[← Back to Home](Home.md) | [← Architecture](Architecture.md)

## The Fundamental Rule

> **Private enablement is permissible when and only when it is BOTH:**
> 1. **Incidental to** purpose-driven execution (not the primary purpose), AND
> 2. **Inseparable from** purpose-driven execution (necessarily coupled with mission advancement)

This constraint is the **fundamental boundary** between legitimate operations and private inurement.

## What is Private Enablement?

**Private enablement** = any benefit, compensation, or resource provided to private individuals:
- Employee salaries
- Contractor payments
- Health insurance and benefits
- Professional development
- Distributions to beneficiaries
- Any expenditure benefiting a private person

---

## The Two-Part Test

### Test 1: Incidentality

**Question**: Is the private enablement **incidental to** the purpose?

**Meaning**: The enablement serves the mission, not the person.

#### ✅ Passes Incidentality Test:
- Researcher salary to conduct health research
- Teacher salary to provide education
- Program director compensation to manage charitable programs
- **The purpose is the mission; compensation is how you achieve it**

#### ❌ Fails Incidentality Test:
- Luxury vacation unrelated to mission
- Personal expenses with no mission nexus
- Enrichment disguised as compensation
- **The enablement IS the purpose (enrichment)**

### Test 2: Inseparability

**Question**: Is the private enablement **inseparable from** execution?

**Meaning**: You cannot achieve the mission without this enablement.

#### ✅ Passes Inseparability Test:
- Researcher salary - cannot do research without researcher
- Health insurance - cannot retain qualified staff without benefits
- Professional development - cannot maintain expertise without training
- **Remove the enablement → execution stops**

#### ❌ Fails Inseparability Test:
- Excessive compensation - can achieve same result with reasonable compensation
- Lavish benefits - can retain staff with standard benefits
- Personal enrichment - separable from mission entirely
- **Remove the enablement → execution continues**

---

## The Formal Logic

```
PermissiblePrivateEnablement ⟺ (incidental ∧ inseparable)

Where:
  incidental = enablement serves purpose, not person
  inseparable = mission cannot be achieved without enablement
```

In OWL:

```turtle
:PermissiblePrivateEnablement rdf:type owl:Class ;
    rdfs:subClassOf :PrivateEnablement ,
        [ rdf:type owl:Restriction ;
          owl:onProperty :isIncidentalTo ;
          owl:minCardinality "1"^^xsd:nonNegativeInteger
        ] ,
        [ rdf:type owl:Restriction ;
          owl:onProperty :isInseparableFrom ;
          owl:minCardinality "1"^^xsd:nonNegativeInteger
        ] .
```

**Translation**: To be permissible, enablement MUST be incidental to at least one purpose AND inseparable from at least one operational activity.

---

## Examples

### ✅ Example 1: AI Trainer Pay

**Scenario**: The foundation's Opportunity program, AI agent training for South Side residents, pays its AI trainer $4,000/month (illustrative).

**Test 1 - Incidental?**
- Purpose: Opportunity (residents who can run their own AI agent workflows)
- Enablement: the trainer's pay
- **Result**: ✅ Pay is incidental to the Opportunity purpose (serves the program, not enrichment)

**Test 2 - Inseparable?**
- Activity: AI agent training
- Enablement: a qualified trainer
- **Result**: ✅ The training cannot run without a trainer

**Conclusion**: **PERMISSIBLE** - satisfies both tests, and $48,000 a year sits under the $55,000 benchmark (illustrative)

```turtle
:Enable_AITrainerPay rdf:type :EmployeeCompensationEnablement ;
    :isIncidentalTo :FoundationOpportunityMission ;
    :isInseparableFrom :Program_AIAgentTraining ;
    :hasMarketBenchmark :Benchmark_AITrainer .
```

### ✅ Example 2: Staff Benefits

**Scenario**: The same program provides the trainer $600/month of benefits (illustrative).

**Test 1 - Incidental?**
- Purpose: Opportunity
- Enablement: benefits for program staff
- **Result**: ✅ Benefits enable the program, not personal enrichment

**Test 2 - Inseparable?**
- Activity: keeping a qualified trainer on the program
- Enablement: a fair benefits package
- **Result**: ✅ The program cannot keep its trainer without benefits

**Conclusion**: **PERMISSIBLE** - satisfies both tests, and $7,200 a year sits under the $9,000 benchmark (illustrative)

```turtle
:Enable_AITrainerBenefits rdf:type :OperationalBenefitEnablement ;
    :isIncidentalTo :FoundationOpportunityMission ;
    :isInseparableFrom :Program_AIAgentTraining ;
    :hasMarketBenchmark :Benchmark_StaffBenefits .
```

The verdict comes from the checks in `trust-domain-keystone-shapes.ttl`, which read these links; run `python3 validate_keystone.py`.

### ❌ Example 3: Trustee Luxury Vacation

**Scenario**: Trust pays $50,000 for trustee's luxury vacation unrelated to trust activities.

**Test 1 - Incidental?**
- Purpose: Charitable mission
- Enablement: Personal luxury vacation
- **Result**: ❌ Serves personal enjoyment, NOT mission

**Test 2 - Inseparable?**
- Activity: None - vacation unrelated to trust activities
- Enablement: Personal enrichment
- **Result**: ❌ Completely separable from any mission activity

**Conclusion**: **IMPROPER** - fails both tests → **PRIVATE INUREMENT**

```turtle
:ExampleImproperLavishExpense rdf:type :ImproperPrivateEnablement ;
    :violatesKeystoneConstraint :TheKeystoneConstraint .

:ImproperPrivateEnablement rdfs:subClassOf :PrivateInurement .
```

### ❌ Example 4: Excessive Compensation

**Scenario**: Foundation pays employee $500,000 for work with market rate of $150,000.

**Analysis**:
- Base compensation ($150,000): ✅ Incidental + inseparable = PERMISSIBLE
- Excess portion ($350,000):
  - Test 1: ❌ NOT incidental (serves enrichment)
  - Test 2: ❌ Separable (can achieve same result with market rate)

**Conclusion**: **EXCESS IS IMPROPER** - the separable portion violates keystone constraint

---

## The Disjoint Classes

**Critical axiom**:

```turtle
:PermissiblePrivateEnablement owl:disjointWith :ImproperPrivateEnablement .
```

**Meaning**: Private enablement is EITHER permissible OR improper - never both.

If it passes both tests → permissible
If it fails either test → improper → private inurement

---

## Connection to Authority Cascade

The keystone constraint is **proven** by the [Authority Cascade](Authority-Cascade.md):

```
If spend can trace:
  Actual Spend → Expense Domain → Operator in Role →
  Authorized Activity → Purpose

Then:
  - Incidental to purpose (traces back to mission)
  - Inseparable from execution (required for activity)

∴ Satisfies keystone constraint
```

**The cascade IS the proof mechanism for the keystone constraint.**

---

## How the Graph Runs This Test

The OWL classes above say what the keystone **means**. OWL reasons open-world: a missing link is "unknown", so on its own it can never fail a payment. Before this check existed, a salary with no links at all was classified permissible just by being "compensation", and the failing examples were labelled by hand.

The test itself now lives in `trust-domain-keystone-shapes.ttl` (SHACL) and reads only linked evidence. Every private enablement is graded on five checks:

| Check | Passes when |
|---|---|
| K1 Incidental claim | it names a purpose inside a trust's mission (`isIncidentalTo`) |
| K2 Incidental backing | an expense domain pays it, sustains an operator, and an activity that purpose `authorizes` requires that operator |
| K3 Inseparable | the activity it is `isInseparableFrom` is the one that requires the operator it sustains |
| K4 Amount evidence | it has paid amounts and a market benchmark (`hasMarketBenchmark`) |
| K5 Within market rate | no payment, annualized, exceeds the benchmark |

Nothing is permissible by category or label: the verdict is the check's output. Amounts use the gist money pattern (`gist:Magnitude`, `gist:numericValue`, `gist:hasUnitOfMeasure`) with `:hasPaymentPeriod` (`:PerMonth`, `:PerYear`, `:OneTime`).

One judgment call remains: the market benchmark. The check can only be as good as the benchmark's source, so each benchmark carries `dcterms:source`. The example benchmarks are illustrative, not a market survey.

Run it:

```
pip install rdflib pyshacl
python3 validate_keystone.py
```

It checks the foundation model in `trust-domain-ontology.ttl` plus the failure probes in `tests/keystone/`, and grades the results against the answer key in `tests/keystone/expected.ttl`. The model's examples come from the foundation's own programs, and every amount is illustrative:

- The ontology steward's $6,000 a month, against a $78,000 a year benchmark, passes all five checks. The same role paid $8,000 a month fails K5 only: $96,000 a year is over the benchmark, so the excess is separable.
- The founder's personal travel, claimed as incidental to Opportunity, fail K2, K3 and K4: no program requires them and no expense domain pays an operator.
- Staff pay for the founder's own for-profit venture fails K2 and K4: no purpose authorizes the venture.

The older narrative examples on this page and on [Examples](Examples.md) are the original illustration and have not been rebuilt yet.

## Automated Validation

### SPARQL Query: Find Improper Enablement

```sparql
PREFIX : <http://example.org/trust-domain#>

SELECT ?enablement ?description WHERE {
  ?enablement rdf:type :PrivateEnablement .

  # Check if it's missing incidentality
  FILTER NOT EXISTS {
    ?enablement :isIncidentalTo ?purpose
  }

  OPTIONAL { ?enablement rdfs:comment ?description }
}
```

### SPARQL Query: Validate Permissibility

```sparql
PREFIX : <http://example.org/trust-domain#>

ASK {
  ?enablement rdf:type :PermissiblePrivateEnablement ;
              :isIncidentalTo ?purpose ;
              :isInseparableFrom ?activity .
}
```

Returns `true` if enablement satisfies both tests.

---

## Why This Matters

Traditional compliance question: "Is this expense reasonable?"

**This ontology asks**:
1. Does it serve purpose? (incidental)
2. Is it necessary for execution? (inseparable)

If YES to both → permissible
If NO to either → private inurement

**No ambiguity. No judgment calls. Testable constraint.**

---

**Next**: [The Authority Cascade →](Authority-Cascade.md)
