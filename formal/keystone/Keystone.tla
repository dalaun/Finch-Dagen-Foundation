------------------------------ MODULE Keystone ------------------------------
(***************************************************************************)
(* The keystone rule, checked on every order of moves.                    *)
(*                                                                         *)
(* Rule (one sentence, for the founder to judge):                          *)
(*   No step moves the foundation's money or property to a disqualified    *)
(*   person, or lets one use it, directly or through someone who passes    *)
(*   it on, except pay for personal services the person actually did, at   *)
(*   no more than the market rate, and repayment of a loan the person made *)
(*   to the foundation without interest.                                   *)
(*   26 USC 4941(d)(1)(A)-(E); exceptions 4941(d)(2)(B), (E);              *)
(*   who is disqualified: 4946(a)(1), 507(d)(2).                           *)
(*                                                                         *)
(* Two neighbour rules are checked beside it:                              *)
(*   NoTaxableGrant   26 USC 4945(d)(4), (h): no grant to an organization  *)
(*                    that is not a public charity without expenditure     *)
(*                    responsibility.                                      *)
(*   NoExcessHolding  26 USC 4943(c)(2), (c)(6): the foundation does not   *)
(*                    still hold the management company's stock when the   *)
(*                    gift disposition period ends.                        *)
(*                                                                         *)
(* How to read it: each action is one move between roles. Its guard is    *)
(* the repo check that must say Allow before the move can happen; the     *)
(* check id is in the comment. The rule (the invariants at the bottom) is *)
(* written from the statute, separately from the guards. TLC then tries   *)
(* every order of moves. Roles only, no amounts: one token is one unit of *)
(* value at market price. Modeling, not legal advice.                     *)
(***************************************************************************)
EXTENDS Naturals, FiniteSets

CONSTANTS
    FamilyOver35,   \* settings: 4946(d) family hold > 35% of the family trust (branch A TRUE, branch B FALSE)
    DeriveScreen,   \* FALSE = the repo today: insider status is a typed setting (dm:substantialContributor,
                    \*         dm:dqScreened) that someone must update; TRUE = derived from the gift ledger
    Break           \* "none" or the name of one guard removed on purpose: "lease", "excess", "er"

Founder       == "Founder"         \* trustee and foundation manager, 4946(a)(1)(B)
Relative      == "Relative"        \* 4946(d) family member, 4946(a)(1)(D)
FamilyTrust   == "FamilyTrust"
BusinessTrust == "BusinessTrust"   \* owns the operating company; beneficiary: the family trust
MgmtCo        == "ManagementCo"    \* the founder's management company, > 35% his, 4946(a)(1)(E)
Foundation    == "Foundation"
Vendor        == "Vendor"          \* unrelated seller; may also donate
Grantee       == "Grantee"         \* unrelated organization that is not a public charity
PubCharity    == "PublicCharity"
Spent         == "Spent"           \* value that left the model at a public charity

Parties == {Founder, Relative, FamilyTrust, BusinessTrust, MgmtCo, Foundation,
            Vendor, Grantee, PubCharity}
Tokens  == 1..3

\* Insiders fixed by the settings (rules IR3, IR5 in decision/spend-decision-model.ttl).
FixedInsiders == {Founder, Relative, MgmtCo, BusinessTrust}
                 \cup (IF FamilyOver35 THEN {FamilyTrust} ELSE {})

\* Recorded dm:passesBenefitTo edges that H2 and AL4 read (tests/decision/*).
PassThrough == {FamilyTrust, BusinessTrust}

VARIABLES
    owner,      \* owner[t]: who holds token t
    fdn,        \* fdn[t]: TRUE when token t is the foundation's value (or a grant still restricted to its purpose)
    er,         \* er[t]: token t sits at the grantee under an expenditure responsibility agreement
    eqOwner,    \* who owns the piece of equipment
    eqUser,     \* who uses it
    stock,      \* who holds the management company's stock block
    deadline,   \* TRUE once the 4943(c)(6) disposition period for gifted stock has ended
    gave,       \* parties that have given the foundation enough to be substantial contributors (507(d)(2))
    typed,      \* insiders as the settings say (what R1, AL0 and E1 read when DeriveScreen = FALSE)
    worked,     \* the founder has done one unit of necessary work not yet paid for
    record,     \* a written comparability record for the founder's pay exists (ST1a, H5, ST2)
    loan,       \* loan[p]: principal of an interest-free loan p made to the foundation
    broke       \* the sections a move has broken so far (written by the law below, not by the guards)

vars == <<owner, fdn, er, eqOwner, eqUser, stock, deadline, gave, typed, worked, record, loan, broke>>

\* --- Who is disqualified ------------------------------------------------
\* The law: fixed insiders plus anyone who has become a substantial contributor.
\* 53.4946-1(a)(8): a public charity is not a disqualified person for 4941.
IsDP(p) == p \in FixedInsiders \cup (gave \ {PubCharity})

\* What the checks see.
Screened == IF DeriveScreen THEN FixedInsiders \cup (gave \ {PubCharity}) ELSE typed

\* --- The law, applied to each move ---------------------------------------
\* 4941(d)(1)(A)-(E): a move that carries the foundation's value to a disqualified
\* person (judged at the time of the move) is self-dealing unless 4941(d)(2)(B)
\* (repaying an interest-free loan) or (E) (reasonable pay for personal services
\* actually done) covers it. 4945(d)(4), (h): a grant to an organization that is
\* not a public charity, without expenditure responsibility, is taxable.
\* Each move calls Law; no guard does.
Law(to, isFdn, excepted, taxable) ==
    broke' = broke \cup (IF isFdn /\ IsDP(to) /\ ~excepted THEN {"4941"} ELSE {})
                   \cup (IF taxable THEN {"4945"} ELSE {})

Init ==
    /\ owner = [t \in Tokens |-> CASE t = 1 -> Founder
                                   [] t = 2 -> BusinessTrust
                                   [] t = 3 -> Vendor]
    /\ fdn = [t \in Tokens |-> FALSE]
    /\ er = [t \in Tokens |-> FALSE]
    /\ eqOwner = Vendor /\ eqUser = Vendor
    /\ stock = Founder
    /\ deadline = FALSE
    /\ gave = {}
    /\ typed = FixedInsiders
    /\ worked = FALSE
    /\ record = FALSE
    /\ loan = [p \in Parties |-> 0]
    /\ broke = {}

FdnTokens  == {t \in Tokens : owner[t] = Foundation}
PrivTokens(p) == {t \in Tokens : owner[t] = p /\ ~fdn[t]}

\* --- Moves into the foundation --------------------------------------------
\* A gift. No guard: gifts in are allowed. (PG10, liens on gifted property,
\* is not modeled.) A gift this large makes the giver a substantial contributor.
Gift(p, t) ==
    /\ p \notin {Foundation, Grantee, PubCharity}
    /\ t \in PrivTokens(p)
    /\ owner' = [owner EXCEPT ![t] = Foundation]
    /\ fdn' = [fdn EXCEPT ![t] = TRUE]
    /\ gave' = gave \cup ({p} \ FixedInsiders)
    /\ Law(Foundation, FALSE, FALSE, FALSE)
    /\ UNCHANGED <<er, eqOwner, eqUser, stock, deadline, typed, worked, record, loan>>

\* The founder gives the management company's stock. Guard PG3b: a written
\* disposal plan (assumed written with the gift).
GiftStock ==
    /\ stock = Founder
    /\ stock' = Foundation
    /\ Law(Foundation, FALSE, FALSE, FALSE)
    /\ UNCHANGED <<owner, fdn, er, eqOwner, eqUser, deadline, gave, typed, worked, record, loan>>

\* An interest-free loan to the foundation. Guard AL0: no deal with an insider
\* (stricter than 4941(d)(2)(B), which allows this one).
LendToFoundation(p, t) ==
    /\ p \notin {Foundation, PubCharity, Grantee}
    /\ t \in PrivTokens(p)
    /\ p \notin Screened                                   \* AL0
    /\ loan[p] = 0
    /\ owner' = [owner EXCEPT ![t] = Foundation]
    /\ fdn' = [fdn EXCEPT ![t] = TRUE]
    /\ loan' = [loan EXCEPT ![p] = 1]
    /\ Law(Foundation, FALSE, FALSE, FALSE)
    /\ UNCHANGED <<er, eqOwner, eqUser, stock, deadline, gave, typed, worked, record>>

\* --- Moves out of the foundation -----------------------------------------
\* The foundation buys goods or rents space from p (P22, P23).
\* Guards R1 (payee not an insider), H2 (payee passes nothing on to an insider).
\* Market price: the foundation gets value back, so the token stops being its value.
Buy(p, t) ==
    /\ p \in {Founder, Relative, FamilyTrust, BusinessTrust, MgmtCo, Vendor}
    /\ t \in FdnTokens
    /\ p \notin Screened                                   \* R1
    /\ p \notin PassThrough                                \* H2
    /\ owner' = [owner EXCEPT ![t] = p]
    /\ fdn' = [fdn EXCEPT ![t] = FALSE]
    /\ Law(p, TRUE, FALSE, FALSE)
    /\ UNCHANGED <<er, eqOwner, eqUser, stock, deadline, gave, typed, worked, record, loan>>

\* The foundation buys the equipment from its owner. Guards R1, H2.
BuyEquipment(t) ==
    /\ eqOwner \notin {Foundation}
    /\ t \in FdnTokens
    /\ eqOwner \notin Screened                             \* R1
    /\ eqOwner \notin PassThrough                          \* H2
    /\ owner' = [owner EXCEPT ![t] = eqOwner]
    /\ fdn' = [fdn EXCEPT ![t] = FALSE]
    /\ eqOwner' = Foundation /\ eqUser' = Foundation
    /\ Law(eqOwner, TRUE, FALSE, FALSE)
    /\ UNCHANGED <<er, stock, deadline, gave, typed, worked, record, loan>>

\* The foundation leases the equipment out (G36). Guards AL0 and R3 (lessee
\* not an insider) and PG13 (personal-property rent not tied to real property
\* goes to counsel, so it never passes as Allow). Break = "lease" marks the lease
\* to the management company Allow.
LeaseEquipment(p) ==
    /\ eqOwner = Foundation /\ eqUser = Foundation
    /\ p \in {MgmtCo, Vendor, FamilyTrust}
    /\ \/ Break = "lease" /\ p = MgmtCo
       \/ /\ p \notin Screened                             \* AL0, R3
          /\ FALSE                                         \* PG13: needs counsel
    /\ eqUser' = p
    /\ Law(p, TRUE, FALSE, FALSE)
    /\ UNCHANGED <<owner, fdn, er, eqOwner, stock, deadline, gave, typed, worked, record, loan>>

\* The foundation sells the equipment at market. Guard AL0. The buyer's payment
\* becomes the foundation's value.
SellEquipment(p, u) ==
    /\ eqOwner = Foundation /\ eqUser = Foundation
    /\ p \in {Founder, FamilyTrust, BusinessTrust, MgmtCo, Vendor}
    /\ u \in PrivTokens(p)
    /\ p \notin Screened                                   \* AL0
    /\ eqOwner' = p /\ eqUser' = p
    /\ owner' = [owner EXCEPT ![u] = Foundation]
    /\ fdn' = [fdn EXCEPT ![u] = TRUE]
    /\ Law(p, TRUE, FALSE, FALSE)
    /\ UNCHANGED <<er, stock, deadline, gave, typed, worked, record, loan>>

\* The foundation sells the gifted stock to dispose of it. Guard AL0.
SellStock(p, u) ==
    /\ stock = Foundation
    /\ p \in {Founder, FamilyTrust, BusinessTrust, MgmtCo, Vendor}
    /\ u \in PrivTokens(p)
    /\ p \notin Screened                                   \* AL0
    /\ stock' = p
    /\ owner' = [owner EXCEPT ![u] = Foundation]
    /\ fdn' = [fdn EXCEPT ![u] = TRUE]
    /\ Law(p, TRUE, FALSE, FALSE)
    /\ UNCHANGED <<er, eqOwner, eqUser, deadline, gave, typed, worked, record, loan>>

\* The founder does a unit of necessary work for a program, and writes the
\* comparability record. These are his steps, not the foundation's.
FounderWorks ==
    /\ ~worked
    /\ worked' = TRUE
    /\ Law(Founder, FALSE, FALSE, FALSE)
    /\ UNCHANGED <<owner, fdn, er, eqOwner, eqUser, stock, deadline, gave, typed, record, loan>>

WriteRecord ==
    /\ ~record
    /\ record' = TRUE
    /\ Law(Founder, FALSE, FALSE, FALSE)
    /\ UNCHANGED <<owner, fdn, er, eqOwner, eqUser, stock, deadline, gave, typed, worked, loan>>

\* The foundation pays the founder one unit, the market rate for one unit of work.
\* Guards ST1a and H5 (a written comparability record), ST2 (decided before money
\* moves), K5 and ST1c (no more than the benchmark: pay only for work done).
\* Break = "excess" drops the work-done guard.
Wage(t) ==
    /\ t \in FdnTokens
    /\ record                                              \* ST1a, H5, ST2
    /\ (worked \/ Break = "excess")                        \* K5, ST1c
    /\ owner' = [owner EXCEPT ![t] = Founder]
    /\ fdn' = [fdn EXCEPT ![t] = FALSE]
    /\ worked' = FALSE
    /\ Law(Founder, TRUE, worked, FALSE)
    /\ UNCHANGED <<er, eqOwner, eqUser, stock, deadline, gave, typed, record, loan>>

\* The foundation repays an interest-free loan's principal. Guard R1.
Repay(p, t) ==
    /\ loan[p] = 1
    /\ t \in FdnTokens
    /\ p \notin Screened                                   \* R1
    /\ owner' = [owner EXCEPT ![t] = p]
    /\ fdn' = [fdn EXCEPT ![t] = FALSE]
    /\ loan' = [loan EXCEPT ![p] = 0]
    /\ Law(p, TRUE, TRUE, FALSE)
    /\ UNCHANGED <<er, eqOwner, eqUser, stock, deadline, gave, typed, worked, record>>

\* The foundation lends. Guards R1 and AL0 (insider); R7 (any other loan is a
\* jeopardy or program-related-investment question for counsel), so no loan out
\* ever passes as Allow. Kept so the model shows the route is closed.
LendOut(p, t) ==
    /\ t \in FdnTokens
    /\ p \in {Founder, Relative, FamilyTrust, BusinessTrust, MgmtCo, Vendor, Grantee}
    /\ p \notin Screened                                   \* R1, AL0
    /\ FALSE                                               \* R7: needs counsel
    /\ owner' = [owner EXCEPT ![t] = p]
    /\ Law(p, TRUE, FALSE, FALSE)
    /\ UNCHANGED <<fdn, er, eqOwner, eqUser, stock, deadline, gave, typed, worked, record, loan>>

\* A grant. Guards R1 and S1 (grantee not an insider), H2 (passes nothing on),
\* R6 (a grantee that is not a public charity needs expenditure responsibility).
\* Break = "er" lets a grant to the grantee go without the agreement.
Grant(g, t) ==
    /\ t \in FdnTokens
    /\ g \in {Relative, FamilyTrust, BusinessTrust, MgmtCo, Grantee, PubCharity}
    /\ g \notin Screened                                   \* R1, S1
    /\ g \notin PassThrough                                \* H2
    /\ LET withER == g = Grantee /\ Break # "er" IN
       /\ owner' = [owner EXCEPT ![t] = IF g = PubCharity THEN Spent ELSE g]
       /\ fdn' = [fdn EXCEPT ![t] = g # PubCharity]
       /\ er' = [er EXCEPT ![t] = withER]
       /\ Law(g, TRUE, FALSE,
                       g \notin {PubCharity} /\ ~withER)
    /\ UNCHANGED <<eqOwner, eqUser, stock, deadline, gave, typed, worked, record, loan>>

\* The grantee spends a granted token. Under an expenditure responsibility
\* agreement it spends only on the grant's purpose, buying at market (an
\* assumption: the model trusts the agreement). That spend is the grantee's own
\* deal with a seller, not the foundation's value passed on: the grantee is not
\* controlled by the foundation (53.4941(d)-1(b)(1)). Without an agreement the
\* grantee can pay anyone, and what it passes on is still the foundation's value.
GranteeSpends(t, q) ==
    /\ owner[t] = Grantee /\ fdn[t]
    /\ q \in Parties \ {Grantee, Foundation}
    /\ (er[t] => q \in {Vendor, PubCharity})               \* ER terms (assumed kept)
    /\ owner' = [owner EXCEPT ![t] = IF q = PubCharity THEN Spent ELSE q]
    /\ fdn' = [fdn EXCEPT ![t] = FALSE]
    /\ er' = [er EXCEPT ![t] = FALSE]
    /\ Law(q, ~er[t], FALSE, FALSE)
    /\ UNCHANGED <<eqOwner, eqUser, stock, deadline, gave, typed, worked, record, loan>>

\* --- Moves the foundation is not a party to -------------------------------
\* Private value moves between the other roles along the stack: the business
\* trust pays the family trust, the family trust distributes to the relative,
\* the founder puts money into his management company and is paid by it.
\* Unguarded: no foundation check runs on these.
Chain == {<<BusinessTrust, FamilyTrust>>, <<FamilyTrust, Relative>>,
          <<Founder, MgmtCo>>, <<MgmtCo, Founder>>}

PrivateMove(p, q, t) ==
    /\ <<p, q>> \in Chain
    /\ t \in PrivTokens(p)
    /\ owner' = [owner EXCEPT ![t] = q]
    /\ Law(q, FALSE, FALSE, FALSE)
    /\ UNCHANGED <<fdn, er, eqOwner, eqUser, stock, deadline, gave, typed, worked, record, loan>>

\* Someone updates the insider settings to match the gift ledger. Nothing in the
\* repo forces this to happen before the next payment.
Rescreen ==
    /\ ~DeriveScreen
    /\ typed # FixedInsiders \cup (gave \ {PubCharity})
    /\ typed' = FixedInsiders \cup (gave \ {PubCharity})
    /\ Law(Foundation, FALSE, FALSE, FALSE)
    /\ UNCHANGED <<owner, fdn, er, eqOwner, eqUser, stock, deadline, gave, worked, record, loan>>

\* Time passes the end of the gift disposition period for the stock.
PeriodEnds ==
    /\ stock = Foundation /\ ~deadline
    /\ deadline' = TRUE
    /\ Law(Foundation, FALSE, FALSE, FALSE)
    /\ UNCHANGED <<owner, fdn, er, eqOwner, eqUser, stock, gave, typed, worked, record, loan>>

Next ==
    \/ \E p \in Parties, t \in Tokens : Gift(p, t)
    \/ GiftStock
    \/ \E p \in Parties, t \in Tokens : LendToFoundation(p, t)
    \/ \E p \in Parties, t \in Tokens : Buy(p, t)
    \/ \E t \in Tokens : BuyEquipment(t)
    \/ \E p \in Parties : LeaseEquipment(p)
    \/ \E p \in Parties, u \in Tokens : SellEquipment(p, u)
    \/ \E p \in Parties, u \in Tokens : SellStock(p, u)
    \/ FounderWorks
    \/ WriteRecord
    \/ \E t \in Tokens : Wage(t)
    \/ \E p \in Parties, t \in Tokens : Repay(p, t)
    \/ \E p \in Parties, t \in Tokens : LendOut(p, t)
    \/ \E g \in Parties, t \in Tokens : Grant(g, t)
    \/ \E t \in Tokens, q \in Parties : GranteeSpends(t, q)
    \/ \E pq \in Chain, t \in Tokens : PrivateMove(pq[1], pq[2], t)
    \/ Rescreen
    \/ PeriodEnds

Spec == Init /\ [][Next]_vars

\* --- The rules, written from the statute ---------------------------------
TypeOK ==
    /\ owner \in [Tokens -> Parties \cup {Spent}]
    /\ fdn \in [Tokens -> BOOLEAN]
    /\ er \in [Tokens -> BOOLEAN]
    /\ eqOwner \in Parties /\ eqUser \in Parties
    /\ stock \in Parties
    /\ gave \subseteq Parties /\ typed \subseteq Parties
    /\ worked \in BOOLEAN /\ record \in BOOLEAN /\ deadline \in BOOLEAN
    /\ loan \in [Parties -> {0, 1}]
    /\ broke \subseteq {"4941", "4945"}

\* 4941(d)(1)(A)-(E): the move just taken did not carry foundation value to a
\* disqualified person, unless an exception in 4941(d)(2)(B) or (E) covers it;
\* and no disqualified person uses foundation property (4941(d)(1)(C), (E)).
\* "Through someone who passes it on" is covered because a grant keeps the token
\* the foundation's value until the grantee spends it.
Keystone ==
    /\ "4941" \notin broke
    /\ ~(eqOwner = Foundation /\ IsDP(eqUser))

\* 4945(d)(4), (h).
NoTaxableGrant == "4945" \notin broke

\* 4943(c)(2)(A), (c)(6): the management company is the founder's, so the
\* foundation's permitted holding is nil, and gifted stock must be gone when
\* the period ends.
NoExcessHolding == ~(deadline /\ stock = Foundation)

=============================================================================
