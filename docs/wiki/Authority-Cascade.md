# The Authority Cascade

[← Back to Home](Home.md) | [← Keystone Constraint](Keystone-Constraint.md)

## The Proof of Legitimacy

The Authority Cascade is the **complete traceable chain** from mission statement to every dollar spent. This cascade **proves** [Keystone Constraint](Keystone-Constraint.md) satisfaction.

## The Complete Chain

```
Mission
  ↓ legitimizes
Authority
  ↓ has purpose
Purpose Domains
  ↓ authorize
Authorized Activities
  ↓ require
Operators in Role
  ↓ necessitate
Expense Domains
  ↓ manifest as
Actual Spend
  ↓ traces back to
Purpose ✓
```

**If the cascade completes → spend is permissible.**
**If the cascade breaks → spend is private inurement.**

---

## The Six Levels

### Level 1: Mission

The foundation's mission statement:

```turtle
:FoundationMission rdf:type :CharitablePurpose ;
    :hasMissionStatement "Empowering lives through health, education, innovation, and opportunity in furtherance of long-term human and systemic capability." .
```

**What it does**: Legitimizes all authority exercised by the trust

**Property**: `:legitimizes`

### Level 2: Purpose Domains

The mission decomposes into four operational domains:

```turtle
:FoundationMission :hasSubPurpose :FoundationHealthMission ,
                                  :FoundationEducationMission ,
                                  :FoundationInnovationMission ,
                                  :FoundationOpportunityMission .
```

**What they do**: Each purpose domain **authorizes** specific activities

**Property**: `:authorizes`

### Level 3: Authorized Activities

Specific operational activities explicitly authorized by purpose domains:

```turtle
:Program_AIAgentTraining rdf:type :AuthorizedActivity ;
    :advancesPurpose :FoundationOpportunityMission ;
    :buildsCapability :Cap_ResidentAgentOperators .
```

**What they do**: Define **what the trust is allowed to do**

**Property**: `:requires` (activities require operators)

### Level 4: Operators in Role

Human capabilities operating in specific roles to execute authorized activities:

```turtle
:Role_AITrainer rdf:type :OperatorInRole ;
    :servesActivity :Program_AIAgentTraining .
```

**What they do**: Execute the authorized activities

**Property**: `:necessitates` (operators necessitate expense domains)

### Level 5: Expense Domains

Categories of expense/enablement necessary to sustain operators:

```turtle
:CompDomain_AITrainer rdf:type :CompensationDomain ;
    :sustains :Role_AITrainer .

:BenefitsDomain_AITrainer rdf:type :BenefitsDomain ;
    :sustains :Role_AITrainer .
```

**What they do**: Define **where private enablement occurs**

**Property**: `:manifestsAs` (expense domains manifest as actual spend)

### Level 6: Actual Spend

Concrete expenditures - the actual dollars out:

```turtle
:Pay_AITrainer_Feb2027 rdf:type :ActualSpend ;
    :tracesBackTo :FoundationOpportunityMission .
```

**What it does**: **Closes the loop** - traces back to purpose

**Property**: `:tracesBackTo` ✓

---

## Complete Example: The AI Trainer's Pay

The foundation's Opportunity program trains South Side residents to run their own AI agent workflows. It pays one AI trainer to teach it. This is the same example `trust-domain-ontology.ttl` uses (`:TheAuthorityCascade`), so the wiki and the graph tell one story. All amounts are illustrative.

### The Full Cascade

```
1. MISSION
   "Empowering lives through health, education, innovation, and opportunity in furtherance of long-term human and systemic capability."
   (:FoundationMission)
   ↓ legitimizes FoundationAuthority
   ↓ has sub-purpose

2. PURPOSE DOMAIN
   Opportunity
   (:FoundationOpportunityMission)
   ↓ authorizes

3. AUTHORIZED ACTIVITY (the program)
   AI agent training for South Side residents
   (:Program_AIAgentTraining)
   builds: residents who run their own agent workflows (:Cap_ResidentAgentOperators)
   tested by: graduates still running their workflow 90 days after training
   holds: the starter agent template and training guide (:Asset_AgentTrainingTemplate)
   ↓ requires

4. OPERATOR IN ROLE
   AI trainer
   (:Role_AITrainer)
   ↓ necessitates

5. EXPENSE DOMAINS
   - Compensation: pay for teaching the program
   - Benefits: staff benefits
   (:CompDomain_AITrainer, :BenefitsDomain_AITrainer)
   ↓ manifest as

6. ACTUAL SPEND
   - $4,000 pay (February 2027)
   - $600 benefits (February 2027)
   (:Pay_AITrainer_Feb2027, :Pay_AITrainerBenefits_Feb2027)
   ↓ traces back to

7. PURPOSE
   :FoundationOpportunityMission ✓ (confirmed by the path above, not just asserted)
```

### The Ontology Representation

```turtle
# Level 1-2: Mission → Purpose Domain
:FoundationMission :hasSubPurpose :FoundationOpportunityMission .

# Level 2-3: Purpose Domain → Authorized Activity
:FoundationOpportunityMission :authorizes :Program_AIAgentTraining .
:Program_AIAgentTraining :advancesPurpose :FoundationOpportunityMission ;
    :buildsCapability :Cap_ResidentAgentOperators .
:Asset_AgentTrainingTemplate :deployedIn :Program_AIAgentTraining .

# Level 3-4: Authorized Activity → Operator
:Program_AIAgentTraining :requires :Role_AITrainer .
:Role_AITrainer :servesActivity :Program_AIAgentTraining .

# Level 4-5: Operator → Expense Domains
:Role_AITrainer :necessitates :CompDomain_AITrainer ,
                              :BenefitsDomain_AITrainer .
:CompDomain_AITrainer :sustains :Role_AITrainer .

# Level 5-6: Expense Domain → Actual Spend
:CompDomain_AITrainer :manifestsAs :Pay_AITrainer_Feb2027 .

# Level 6 → Back to Level 2: Actual Spend → Purpose (CLOSES THE LOOP)
:Pay_AITrainer_Feb2027 :tracesBackTo :FoundationOpportunityMission .
```

### The Proof

Every dollar ($4,000 pay + $600 benefits a month) is **provably**:

1. **Incidental to purpose**
   - Serves the Opportunity purpose (residents trained to run their own agents)
   - Not personal enrichment

2. **Inseparable from execution**
   - The training cannot run without a trainer
   - The program cannot keep a qualified trainer without fair pay and benefits

3. **Within market rate**
   - $48,000 a year against a $55,000 benchmark; $7,200 of benefits against $9,000 (both illustrative)

**∴ Satisfies Keystone Constraint ✓** `validate_keystone.py` passes all four AI trainer nodes (the two enablements and the two payments).

---

## Enforced Restrictions

The ontology **enforces** these relationships via OWL restrictions:

### Restriction 1: Activities Must Be Authorized

```turtle
:AuthorizedActivity rdfs:subClassOf
    [ rdf:type owl:Restriction ;
      owl:onProperty [ owl:inverseOf :authorizes ] ;
      owl:minCardinality "1"^^xsd:nonNegativeInteger
    ] .
```

**Meaning**: Every authorized activity MUST be authorized by at least one purpose domain.

### Restriction 2: Operators Must Serve Activities

```turtle
:OperatorInRole rdfs:subClassOf
    [ rdf:type owl:Restriction ;
      owl:onProperty :servesActivity ;
      owl:minCardinality "1"^^xsd:nonNegativeInteger
    ] .
```

**Meaning**: Every operator MUST serve at least one authorized activity.

### Restriction 3: Expense Domains Must Sustain Operators

```turtle
:ExpenseDomain rdfs:subClassOf
    [ rdf:type owl:Restriction ;
      owl:onProperty :sustains ;
      owl:minCardinality "1"^^xsd:nonNegativeInteger
    ] .
```

**Meaning**: Every expense domain MUST sustain at least one operator.

### Restriction 4: Spend Must Trace Back (THE PROOF)

```turtle
:ActualSpend rdfs:subClassOf
    [ rdf:type owl:Restriction ;
      owl:onProperty :tracesBackTo ;
      owl:minCardinality "1"^^xsd:nonNegativeInteger
    ] .
```

**Meaning**: Every actual spend MUST trace back to at least one purpose.

**This is the formal proof requirement.**

---

## What Fails the Cascade

### Example: Improper Lavish Expense

**Attempted cascade**:

```
1. MISSION
   "Empowering lives through health, education, innovation, and opportunity in furtherance of long-term human and systemic capability."
   ↓
2. PURPOSE DOMAIN
   ??? (no purpose serves personal luxury)
   ❌ CASCADE BREAKS

Actual Spend: $50,000 luxury vacation
  ↓ traces back to... ???
  ❌ CANNOT TRACE BACK TO PURPOSE
```

**Result**: Fails to complete cascade → **PRIVATE INUREMENT**

### Example: Unauthorized Activity

```
1. MISSION → Purpose Domain ✓
2. Purpose Domain → Activity
   ❌ Activity NOT authorized by any purpose domain
   CASCADE BREAKS

Result: Private inurement (activity outside mission)
```

### Example: Unnecessary Operator

```
1-3. Mission → Purpose → Activity ✓
4. Activity → Operator
   ❌ Operator NOT required by activity
   CASCADE BREAKS

Result: Private inurement (unnecessary enrichment)
```

---

## The Cascade in the Graph

The cascade is now data, with the asset-to-program pipeline in it: no asset without a program, no program without a purpose and a lasting capability, no dollar without a path back to the mission.

- Link 1: `:FoundationMission :legitimizes :FoundationAuthority`, and `:ExampleFoundationTrust :exercisesAuthority :FoundationAuthority`.
- Link 2: each purpose domain `:authorizes` its programs. Innovation authorizes Canonical Governance Infrastructure for nonprofits; Education authorizes the Chicago street-grid workshops and the industrial hemp curriculum grants; Opportunity authorizes AI agent training for residents; Health authorizes resident-owned personal health knowledge graphs.
- Each program `:buildsCapability` a `:LongTermCapability` with a `:capabilityTest`, and each asset the trust `:controls` is `:deployedIn` a program.
- A grant is `:grantedUnder` its grantmaking program.

`trust-domain-keystone-shapes.ttl` checks the whole chain closed-world:

- **C1 Spend trace**: each `tracesBackTo` on a payment must be confirmed by the path payment, expense domain, operator, activity, authorizing purpose (or, for a grant, grant, grantmaking program, authorizing purpose). A payment that only asserts its trace fails.
- **C2 Activity authorized**: every authorized activity is authorized by a purpose inside a trust's mission.
- **C3 Mission legitimizes**: a trust's purpose legitimizes an authority the trust exercises.
- **C4 Builds capability**: every authorized activity names the lasting capability it builds and how that is tested. This is the mission's second half, "in furtherance of long-term human and systemic capability". A program that helps today and builds nothing lasting fails here.
- **A1 Asset to program**: every asset the trust controls is deployed in a program its mission authorizes.
- **S1 No self-dealing**: no payment or grant benefits a disqualified person (the founder, a foundation manager, a substantial contributor or their family) other than as pay for services. A complete path to the mission does not cure it.
- **D1 to D3 Participant records**: a resident's health record is owned by that resident, is never a foundation asset, and goes to anyone else only on a revocable consent the resident gave for that recipient. Sharing is off by default.

Run `python3 validate_keystone.py`. All five programs, their assets, pay, the grant and the residents' records pass; each failure probe fails exactly the check it was written to break.

## Automated Validation

### SPARQL Query: Find Broken Cascades

```sparql
PREFIX : <http://example.org/trust-domain#>

# Find all spend that fails to trace back to purpose
SELECT ?spend ?amount WHERE {
  ?spend rdf:type :ActualSpend .

  # Spend exists but...
  FILTER NOT EXISTS {
    ?spend :tracesBackTo ?purpose .
  }

  OPTIONAL { ?spend rdfs:label ?amount }
}
```

**Returns**: All spending that fails cascade → FLAGS FOR REVIEW

### SPARQL Query: Validate Complete Cascade

```sparql
PREFIX : <http://example.org/trust-domain#>

SELECT ?spend ?purpose WHERE {
  ?spend rdf:type :ActualSpend ;
         :tracesBackTo ?purpose .

  # Trace backward through cascade
  ?expenseDomain :manifestsAs ?spend ;
                 :sustains ?operator .

  ?operator :servesActivity ?activity .

  ?activity :advancesPurpose ?purpose .
}
```

**Returns**: All spending with complete cascade → VALIDATED

---

## The Audit Trail

For **any** expenditure, you can query the complete chain:

```
Query: What authorized this $4,000 payment?

Answer (graph traversal):
$4,000 AI trainer pay
  ← manifests from CompDomain_AITrainer
  ← sustains Role_AITrainer
  ← serves Program_AIAgentTraining
  ← advances FoundationOpportunityMission
  ← part of FoundationMission ✓
```

**This is machine-readable compliance.**

---

## Why This Matters

Traditional compliance:
- Gather receipts
- Write justification memos
- Hope auditor agrees

**This ontology**:
- Query the graph
- Does path from spend → purpose exist?
- If YES → permissible, if NO → inurement

**No ambiguity. No judgment calls. Provable compliance.**

---

**Next**: [Examples →](Examples.md) | [Usage Guide →](Usage-Guide.md)
