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
:ClinicalTrialsActivity rdf:type :AuthorizedActivity ;
    :advancesPurpose :FoundationHealthMission .
```

**What they do**: Define **what the trust is allowed to do**

**Property**: `:requires` (activities require operators)

### Level 4: Operators in Role

Human capabilities operating in specific roles to execute authorized activities:

```turtle
:ResearchScientistDrSmith rdf:type :OperatorInRole ;
    :servesActivity :ClinicalTrialsActivity .
```

**What they do**: Execute the authorized activities

**Property**: `:necessitates` (operators necessitate expense domains)

### Level 5: Expense Domains

Categories of expense/enablement necessary to sustain operators:

```turtle
:CompensationDomain_DrSmith rdf:type :CompensationDomain ;
    :sustains :ResearchScientistDrSmith .

:BenefitsDomain_DrSmith rdf:type :BenefitsDomain ;
    :sustains :ResearchScientistDrSmith .
```

**What they do**: Define **where private enablement occurs**

**Property**: `:manifestsAs` (expense domains manifest as actual spend)

### Level 6: Actual Spend

Concrete expenditures - the actual dollars out:

```turtle
:SalaryPayment_DrSmith_January2024 rdf:type :ActualSpend ;
    :tracesBackTo :FoundationHealthMission .
```

**What it does**: **Closes the loop** - traces back to purpose

**Property**: `:tracesBackTo` ✓

---

## Complete Example: Dr. Smith's Salary

### The Full Cascade

```
1. MISSION
   "Empowering lives through health, education, innovation, and opportunity in furtherance of long-term human and systemic capability."
   (:FoundationMission)
   ↓ legitimizes FiduciaryAuthority
   ↓ has sub-purpose

2. PURPOSE DOMAIN
   Health mission - advancing health and wellness
   (:FoundationHealthMission)
   ↓ authorizes

3. AUTHORIZED ACTIVITY
   Conducting clinical trials for novel cancer treatments
   (:ClinicalTrialsActivity)
   ↓ requires

4. OPERATOR IN ROLE
   Research scientist Dr. Smith
   (:ResearchScientistDrSmith)
   ↓ necessitates

5. EXPENSE DOMAINS
   - Compensation: Salary for research work
   - Benefits: Health insurance, retirement
   (:CompensationDomain_DrSmith, :BenefitsDomain_DrSmith)
   ↓ manifest as

6. ACTUAL SPEND
   - $12,500 salary payment (January 2024)
   - $850 health insurance premium
   (:SalaryPayment_DrSmith_January2024, :HealthInsurance_DrSmith_January2024)
   ↓ traces back to

7. PURPOSE
   :FoundationHealthMission ✓
```

### The Ontology Representation

```turtle
# Level 1-2: Mission → Purpose Domain
:FoundationMission :hasSubPurpose :FoundationHealthMission .

# Level 2-3: Purpose Domain → Authorized Activity
:FoundationHealthMission :authorizes :ClinicalTrialsActivity .
:ClinicalTrialsActivity :advancesPurpose :FoundationHealthMission .

# Level 3-4: Authorized Activity → Operator
:ClinicalTrialsActivity :requires :ResearchScientistDrSmith .
:ResearchScientistDrSmith :servesActivity :ClinicalTrialsActivity .

# Level 4-5: Operator → Expense Domains
:ResearchScientistDrSmith :necessitates :CompensationDomain_DrSmith ,
                                        :BenefitsDomain_DrSmith .
:CompensationDomain_DrSmith :sustains :ResearchScientistDrSmith .

# Level 5-6: Expense Domain → Actual Spend
:CompensationDomain_DrSmith :manifestsAs :SalaryPayment_DrSmith_January2024 .

# Level 6 → Back to Level 2: Actual Spend → Purpose (CLOSES THE LOOP)
:SalaryPayment_DrSmith_January2024 :tracesBackTo :FoundationHealthMission .
```

### The Proof

Every dollar ($12,500 salary + $850 insurance) is **provably**:

1. **Incidental to purpose**
   - Serves health mission (cancer research)
   - Not personal enrichment

2. **Inseparable from execution**
   - Clinical trials cannot occur without qualified researcher
   - Cannot retain researcher without competitive compensation/benefits

**∴ Satisfies Keystone Constraint ✓**

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
Query: What authorized this $12,500 spend?

Answer (graph traversal):
$12,500 Salary
  ← manifests from CompensationDomain_DrSmith
  ← sustains ResearchScientistDrSmith
  ← serves ClinicalTrialsActivity
  ← advances FoundationHealthMission
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
