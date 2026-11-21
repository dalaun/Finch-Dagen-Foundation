# Examples

[← Back to Home](Home.md)

This page shows concrete individuals from the ontology demonstrating permissible vs improper private enablement.

## Complete Authority Cascade Example

### The AI Trainer's Pay (Opportunity program)

**The Scenario**: The foundation's Opportunity program trains South Side residents to run their own AI agent workflows. It employs an AI trainer to teach it. This is the same example `trust-domain-ontology.ttl` carries, so you can run it.

**Compensation**: $4,000/month pay + $600/month benefits (illustrative)

#### The Complete Traceable Chain

```turtle
# 1. MISSION
:FoundationMission rdf:type :CharitablePurpose ;
    :hasMissionStatement "Empowering lives through health, education, innovation, and opportunity in furtherance of long-term human and systemic capability." ;
    :hasSubPurpose :FoundationOpportunityMission .

# 2. PURPOSE DOMAIN
:FoundationOpportunityMission rdf:type :OpportunityPurpose ;
    :authorizes :Program_AIAgentTraining .

# 3. AUTHORIZED ACTIVITY (the program, with its lasting capability and its asset)
:Program_AIAgentTraining rdf:type :AuthorizedActivity ;
    :advancesPurpose :FoundationOpportunityMission ;
    :requires :Role_AITrainer ;
    :buildsCapability :Cap_ResidentAgentOperators .

:Cap_ResidentAgentOperators rdf:type :LongTermCapability ;
    :capabilityTest "Graduates are still running their own agent workflow 90 days after training." .

:Asset_AgentTrainingTemplate rdf:type :IntangibleAsset ;
    :deployedIn :Program_AIAgentTraining .

# 4. OPERATOR IN ROLE
:Role_AITrainer rdf:type :OperatorInRole ;
    :servesActivity :Program_AIAgentTraining ;
    :necessitates :CompDomain_AITrainer ,
                  :BenefitsDomain_AITrainer .

# 5. EXPENSE DOMAINS
:CompDomain_AITrainer rdf:type :CompensationDomain ;
    :sustains :Role_AITrainer ;
    :manifestsAs :Pay_AITrainer_Feb2027 ;
    :enablesPrivately :Enable_AITrainerPay .

:BenefitsDomain_AITrainer rdf:type :BenefitsDomain ;
    :sustains :Role_AITrainer ;
    :manifestsAs :Pay_AITrainerBenefits_Feb2027 ;
    :enablesPrivately :Enable_AITrainerBenefits .

# 6. ACTUAL SPEND
:Pay_AITrainer_Feb2027 rdf:type :ActualSpend ;
    :tracesBackTo :FoundationOpportunityMission ;
    rdfs:label "AI trainer pay, February 2027: $4,000 (illustrative)" .

:Pay_AITrainerBenefits_Feb2027 rdf:type :ActualSpend ;
    :tracesBackTo :FoundationOpportunityMission ;
    rdfs:label "AI trainer benefits, February 2027: $600 (illustrative)" .
```

#### Keystone Constraint Satisfaction

```turtle
# PAY ENABLEMENT
:Enable_AITrainerPay rdf:type :EmployeeCompensationEnablement ;
    :isIncidentalTo :FoundationOpportunityMission ;      # TEST 1
    :isInseparableFrom :Program_AIAgentTraining ;        # TEST 2
    :hasMarketBenchmark :Benchmark_AITrainer .           # $55,000/yr (illustrative)

# BENEFITS ENABLEMENT
:Enable_AITrainerBenefits rdf:type :OperationalBenefitEnablement ;
    :isIncidentalTo :FoundationOpportunityMission ;      # TEST 1
    :isInseparableFrom :Program_AIAgentTraining ;        # TEST 2
    :hasMarketBenchmark :Benchmark_StaffBenefits .       # $9,000/yr (illustrative)
```

Writing "satisfies the keystone" on a node proves nothing by itself. The checks in `trust-domain-keystone-shapes.ttl` (K1 to K5) read the links above and decide; run `python3 validate_keystone.py`.

#### Why It's Permissible

**Test 1 - Incidental to Purpose**:
- ✅ The purpose is Opportunity: residents who can run their own AI agent workflows
- ✅ The pay serves that program, not personal enrichment
- ✅ The expense domain pays an operator the program requires (K2)

**Test 2 - Inseparable from Execution**:
- ✅ The training cannot run without a trainer
- ✅ The program cannot keep a qualified trainer without fair pay and benefits
- ✅ The activity it is inseparable from is the one that requires the trainer (K3)

**Within market rate** (K4, K5):
- ✅ $48,000 a year against $55,000; $7,200 of benefits against $9,000

**Result**: ✅ **PERMISSIBLE** - all checks pass

---

## Example: Improper Lavish Expense

### Trustee's Luxury Vacation

**The Scenario**: Trust pays $50,000 for trustee's luxury Caribbean vacation unrelated to trust activities.

```turtle
:ExampleImproperLavishExpense rdf:type :ImproperPrivateEnablement ;
    :violatesKeystoneConstraint :TheKeystoneConstraint ;
    rdfs:label "Example: Improper Lavish Personal Expense" ;
    rdfs:comment "Luxury vacation for trustee unrelated to mission activities." .
```

#### Why It's Improper

**Test 1 - Incidental to Purpose**:
- ❌ NO mission purpose served by personal vacation
- ❌ Serves personal enjoyment, not charitable purpose
- **FAILS TEST 1**

**Test 2 - Inseparable from Execution**:
- ❌ Vacation is completely separable from trust operations
- ❌ Can be removed without affecting mission execution
- **FAILS TEST 2**

**Result**: ❌ **IMPROPER** - Fails both tests → **PRIVATE INUREMENT**

#### The Failed Cascade

```
Attempted cascade:
1. Mission: "Empowering lives through health, education, innovation, and opportunity in furtherance of long-term human and systemic capability."
   ↓
2. Purpose Domain: ???
   ❌ NO PURPOSE SERVES PERSONAL LUXURY
   CASCADE BREAKS

:ExampleImproperLavishExpense
  :tracesBackTo ???
  ❌ CANNOT TRACE BACK TO PURPOSE
```

---

## Example: Excessive Compensation

### Above-Market Salary

**The Scenario**: Foundation pays employee $500,000 for work with market rate of $150,000.

```turtle
:ExampleImproperExcessCompensation rdf:type :ImproperPrivateEnablement ;
    :violatesKeystoneConstraint :TheKeystoneConstraint ;
    rdfs:label "Example: Improper Excessive Compensation" ;
    rdfs:comment "Compensation far exceeding market rate - the EXCESS portion
                  is separable and violates keystone constraint." .
```

#### Analysis

**Base Compensation ($150,000)**:
- ✅ Incidental to purpose (work advances mission)
- ✅ Inseparable from execution (need qualified employee)
- **Result**: PERMISSIBLE

**Excess Portion ($350,000)**:
- ❌ NOT incidental to purpose (serves enrichment)
- ❌ Separable from execution (same work achievable at market rate)
- **Result**: IMPROPER → PRIVATE BENEFIT

**Conclusion**: Excess above market rate violates keystone constraint.

---

## Foundation Trust Example

### Complete Trust Structure

```turtle
:ExampleFoundationTrust rdf:type :ForeignPrivateIrrevocableNonGrantorTrust ;
    # Classification
    :isRevocable "false"^^xsd:boolean ;
    :isGrantorTrust "false"^^xsd:boolean ;
    :isForeign "true"^^xsd:boolean ;
    :isDomestic "false"^^xsd:boolean ;

    # Jurisdiction
    :jurisdiction "Nevis" ;
    :hasCourtJurisdiction "Nevis High Court" ;
    :hasControlLocation "Nevis" ;

    # Identification
    :establishedDate "2024-01-15"^^xsd:date ;
    :hasEIN "98-7654321" ;

    # Structure
    :hasTrustee :FoundationTrustee ;
    :hasPurpose :FoundationMission ;

    rdfs:label "Example Foundation Trust" ;
    rdfs:comment "Foreign private irrevocable non-grantor trust operating as
                  a private foundation. Purpose legitimizes authority, which
                  enables deployment of instruments." .
```

**Key Features**:
- Crossed IRC §§671-679 gateway (no retained control)
- Operates under IRC §§641-685 (autonomous accounting)
- Classified under IRC §7701 (foreign jurisdiction)
- Mission-driven purpose (charitable)
- EIN system identifier (98-series for foreign trust)

---

## DNI and Distribution Example

```turtle
# Compute DNI for 2024
:ExampleDNI_2024 rdf:type :DistributableNetIncome ;
    :dniAmount "150000.00"^^xsd:decimal ;
    rdfs:label "2024 DNI" .

# Income distribution to beneficiary
:ExampleIncomeDistribution rdf:type :IncomeDistribution ;
    :flowsCharacterThrough :ExampleCharacterFlow .

# Character flows through to beneficiary
:ExampleCharacterFlow rdf:type :CharacterFlowThrough ;
    rdfs:label "Income character (ordinary, capital gain, etc.) flowing through" .
```

---

## The Four Sub-Purposes

```turtle
# HEALTH
:FoundationHealthMission rdf:type :HealthPurpose ;
    :purposeDescription "Advancing health and wellness through medical research
                        grants, healthcare access programs, and public health initiatives" .

# EDUCATION
:FoundationEducationMission rdf:type :EducationalPurpose ;
    :purposeDescription "Advancing education through scholarship programs,
                        educational technology, curriculum development, and teacher training" .

# INNOVATION
:FoundationInnovationMission rdf:type :InnovationPurpose ;
    :purposeDescription "Advancing innovation through scientific research grants,
                        technology development, and breakthrough discoveries" .

# OPPORTUNITY
:FoundationOpportunityMission rdf:type :OpportunityPurpose ;
    :purposeDescription "Advancing economic opportunity through workforce development,
                        entrepreneurship programs, and access to capital for underserved populations" .
```

---

## Temporal Tracking Example (v4.0)

### Fiscal Year 2024 with Expenditures

```turtle
# Fiscal year with minimum distribution requirements
:FiscalYear2024 rdf:type :FiscalYear ;
    :fiscalYearStart "2024-01-01"^^xsd:date ;
    :fiscalYearEnd "2024-12-31"^^xsd:date ;
    :yearNumber "2024"^^xsd:integer ;
    :minimumDistributionRequired "500000.00"^^xsd:decimal ;
    :qualifyingDistributionsMade "625000.00"^^xsd:decimal ;
    rdfs:label "Fiscal Year 2024" .

# DNI computed for fiscal year
:DNI_2024 rdf:type :DistributableNetIncome ;
    :computedFor :FiscalYear2024 ;
    :dniAmount "750000.00"^^xsd:decimal ;
    rdfs:label "2024 DNI - $750,000" .

# Expenditure occurring during fiscal year
:Pay_AITrainer_Jan2024 rdf:type :ActualSpend ;
    :occursDuring :FiscalYear2024 ;
    :expenditureDate "2024-01-31"^^xsd:date ;
    :tracesBackTo :FoundationOpportunityMission ;
    rdfs:label "AI trainer pay - January 2024 - $4,000 (illustrative)" .

# Activity spanning fiscal year
:Program_AIAgentTraining :hasTemporalExtent :FiscalYear2024 .
```

**Key Features**:
- Fiscal year tracks minimum distribution requirement ($500K) vs actual ($625K) ✅
- DNI computed annually for tax compliance
- Expenditures linked to temporal periods via `occursDuring`
- Activities span fiscal years via `hasTemporalExtent`
- Enables time-series compliance queries

---

## Grantmaking Example (v4.0)

### Grant for an Industrial Hemp Curriculum (Education program)

This is the grant `trust-domain-ontology.ttl` carries. The grantee is a public charity, left unnamed; the amount is illustrative.

```turtle
# Public charity grantee (receivesGrant runs grantee -> grant)
:Grantee_CommunityCollege rdf:type :PublicCharity ;
    :receivesGrant :Grant_HempCurriculum ;
    rdfs:label "Community college (public charity, unnamed)" .

# Grant to advance the education purpose
:Grant_HempCurriculum rdf:type :Grant ;
    :grantAmount "40000.00"^^xsd:decimal ;
    :grantedUnder :Program_HempCurriculumGrants ;
    :tracesBackTo :FoundationEducationMission ;
    :satisfiesQualifyingDistribution :QD_HempCurriculumGrant ;
    rdfs:label "Hemp curriculum grant: $40,000 (illustrative)" .

# Qualifying distribution for IRC §4942
:QD_HempCurriculumGrant rdf:type :QualifyingDistribution ;
    rdfs:comment "A grant to a public charity counts toward the IRC §4942 minimum distribution." .

# Grantmaking activity (distinct from operations), with the capability it builds
:Program_HempCurriculumGrants rdf:type :GrantmakingActivity ;
    :advancesPurpose :FoundationEducationMission ;
    :buildsCapability :Cap_HempWorkforce .

```

**Why Grantmaking is Distinct from Operations**:
- `GrantmakingActivity` is separate class from operational activities
- Grants to IRC §509(a) public charities automatically qualify
- Non-exempt grantees require expenditure responsibility
- Enables tracking qualifying distributions vs minimum requirements

---

## IRC §§4941-4945 Safeguard Examples (v4.0)

### Example: IRC §4941 Self-Dealing Violation

```turtle
# Disqualified person (substantial contributor)
:ExampleTrusteeAsDisqualifiedPerson rdf:type :SubstantialContributor ,
                                              :DisqualifiedPerson ;
    rdfs:label "Foundation Trustee (Disqualified Person)" .

# Self-dealing transaction
:ExampleSelfDealing rdf:type :SelfDealingTransaction ;
    :involvesDisqualifiedPerson :ExampleTrusteeAsDisqualifiedPerson ;
    :transactionAmount "100000.00"^^xsd:decimal ;
    rdfs:label "VIOLATION: Self-Dealing Transaction" ;
    rdfs:comment "Sale of property to disqualified person - IRC §4941 violation" .
```

**Result**: ❌ **VIOLATION** - Transaction with disqualified person triggers IRC §4941 self-dealing prohibition

### Example: IRC §4943 Excess Business Holding

```turtle
# Excess business holding (>20% ownership)
:ExampleExcessHolding rdf:type :ExcessBusinessHolding ;
    :hasOwnershipPercentage "35.0"^^xsd:decimal ;
    :excessHoldingPercentage "15.0"^^xsd:decimal ;
    rdfs:label "VIOLATION: Excess Business Holding (35%)" ;
    rdfs:comment "Ownership exceeds 20% limit - IRC §4943 violation" .
```

**Result**: ❌ **VIOLATION** - Holdings >20% violate IRC §4943 excess business holding limits

### Example: IRC §4944 Jeopardizing Investment

```turtle
# Jeopardizing investment
:ExampleJeopardizingInvestment rdf:type :JeopardizingInvestment ;
    :jeopardizesMission :FoundationHealthMission ;
    rdfs:label "VIOLATION: Jeopardizing Investment" ;
    rdfs:comment "Speculative investment endangering mission - IRC §4944 violation" .
```

**Result**: ❌ **VIOLATION** - Investment jeopardizes mission, prohibited by IRC §4944

### Example: IRC §4945 Taxable Expenditure

```turtle
# Lobbying expenditure
:ExampleLobbyingExpenditure rdf:type :LobbyingExpenditure ,
                                     :TaxableExpenditure ;
    :transactionAmount "50000.00"^^xsd:decimal ;
    rdfs:label "VIOLATION: Lobbying Expenditure" ;
    rdfs:comment "Expenditure for lobbying - IRC §4945 taxable expenditure" .

# Political expenditure
:ExamplePoliticalExpenditure rdf:type :PoliticalExpenditure ,
                                      :TaxableExpenditure ;
    :transactionAmount "25000.00"^^xsd:decimal ;
    rdfs:label "VIOLATION: Political Expenditure" ;
    rdfs:comment "Expenditure for political campaign - IRC §4945 taxable expenditure" .
```

**Result**: ❌ **VIOLATION** - Both are taxable expenditures prohibited by IRC §4945

**All violations are subclasses of `AuthorityCollapse`** and can be detected via disjoint class axioms.

---

## Doctrinal Source Examples

```turtle
# THE GATEWAY
:IRC_671_679 rdf:type :IRCSection ;
    rdfs:label "IRC §§671-679" ;
    rdfs:comment "Control-of-income boundary - determines who is the economic operator,
                  the gateway to non-grantor status" .

# THE OPERATING SYSTEM
:IRC_641_685 rdf:type :IRCSection ;
    rdfs:label "IRC §§641-685" ;
    rdfs:comment "Trust as autonomous accounting system - enables trust to retain income,
                  deploy expenses, distribute outputs with DNI and character flow-through" .

# THE JURISDICTION
:IRC_7701 rdf:type :IRCSection ;
    rdfs:label "IRC §7701" ;
    rdfs:comment "Jurisdictional identity - assigns which sovereign's rules apply
                  via court test and control test" .
```

---

**See Also**:
- [Authority Cascade](Authority-Cascade.md) - Understanding the traceable chain
- [Keystone Constraint](Keystone-Constraint.md) - The permissibility test
- [Usage Guide](Usage-Guide.md) - Querying these examples
