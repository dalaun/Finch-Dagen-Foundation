# 11. Blind-goal adversarial path: find the traceable route to an answer you can't see

[Back to the rehearsal overview](README.md) · Check: [tests/rehearsal/blind_path.py](../tests/rehearsal/blind_path.py) · Adversary library: [tests/rehearsal/blind-path/adversaries.json](../tests/rehearsal/blind-path/adversaries.json) · Example path: [synthetic/paths/demo-foundation-pay.json](synthetic/paths/demo-foundation-pay.json) · Lane diagram: [11-blind-goal-adversarial-path.bpmn](11-blind-goal-adversarial-path.bpmn)

**Status:** spec and first check, 2026-11-27. Synthetic only. **This is design and education, not legal or tax advice.**

## What it is, in one picture

A driving test with the route sealed in an envelope. The learner (the **builder**) drives toward a destination it is told but cannot see the answer for. The instructor in the passenger seat (the **adversary checker**) points at the nearest way to crash on every turn and asks what is actually different. The map (the **keystone checker**) says whether each turn still heads to the same destination. Only the examiner (the **grader**) opens the envelope, and only says pass or fail. The builder keeps driving until it finds a route the examiner passes. **Counsel** is the licensing office: it signs off on the route; it does not draw it.

The founder's framing (voice call, 2026-11-27): the outside answer is "already established at the end as the goal", the builder "persists until it finds the traceable path to the correct answer", the abusive-trust and sham doctrines sit "at every step so it is basically like a guide of what not to do", and "keep the adversaries at every step, but also keep the keystone in check."

Why it matters: the existing [answer key](answer-key-cases.ttl) (K1 to K33) and [structure cases](structure-check-cases.ttl) (SK1 to SK16) are in this public repo, so any agent that builds routes can read them. A builder that can read its answers can learn the answers instead of the law. This method keeps that set as the **practice set** and adds a **held-out set** the builder never reads.

## The roles and what each one may see

| Role | Sees | Never sees | Returns | Who runs it today |
|---|---|---|---|---|
| Builder | the goal question, the keystone claim, the facts, the adversary library, public law | any verdict for its goal, the held-out key, its salts | a path: steps, each with facts, the closest bad pattern, the difference, the contrary authority, a keystone verdict, a key source | Claude (the rehearsal loop) |
| Adversary checker | the path, the library | the key | per step: BG1 to BG5, deterministic code | `blind_path.py`, in CI |
| Keystone checker | the path, the keystone claim | the key | per step: BG6, supports / blocks / silent / unresolved | `blind_path.py`, mirroring [formal/keystone](../formal/keystone/README.md) |
| Grader | the path, the key, the commitments | nothing hidden | `{"path": id, "result": "pass" or "fail"}` and nothing else | `blind_path.py --grade`, with the key from an environment secret |
| Counsel | the packet: every material fact, the path, the questions | nothing hidden | sign-off or not, in the private folder | a licensed attorney or CPA |
| Dalaun | everything | nothing | the checks, the goal, the settings, the PR merges | him |

**Answer flows one way.** The key goes into the grader and comes out as one bit per path. No reason, no hint, no score. A reason would teach the builder the answer.

## The path a builder writes

One file per attempt ([example](synthetic/paths/demo-foundation-pay.json)). Every step states every fact field in the library; a missing field is an error, never a pass (the repo's fail-closed rule). An unknown is `null`, and an unknown counts as the bad value when scoring (cautious).

## The checks, every step

| Check | Question (yes passes) | Source |
|---|---|---|
| BG0 | Does the builder's file, and every input it lists, hold no answer-key material (verdict fields, salts, the held-out file)? | this spec: one-way flow |
| BG1 | Is the step's adversary a pattern from the library? | |
| BG2 | Is it the **closest** pattern by fact match, not an easy strawman? The checker scores every pattern itself. | |
| BG3 | Is the named difference a **fact** in that pattern's signature (never a name or label), and does the step's fact really differ from the bad value? | Notice 97-24, III.1: "Substance--not form--controls taxation." |
| BG4 | Does the step engage the pattern's own authority (the strongest against the move) and say why it doesn't control, in at least a sentence? | |
| BG5 | Does no pattern match whole? Known facts matching a whole signature fail; a whole match that needs an unknown is amber until the fact is stated. | each pattern's source |
| BG6 | Is the step judged against the **same** keystone claim as every other step, is its verdict one of supports, blocks, silent, unresolved, and does it agree with the facts (foundation value to an insider, outside the two exceptions, must be blocks)? Blocks fails; silent and unresolved are amber and go to counsel. | [formal/keystone](../formal/keystone/README.md); IRC 4941(d)(2)(B), (E) |
| BG7 | Where does this step's outside answer come from? Statute, regulation, decided case or revenue ruling passes; a private letter ruling is amber and must be marked WEAK AUTHORITY; counsel passes only once signed off; none must be marked ASSUMPTION. | below, "Where answer keys come from" |
| BG8 | Does renaming every label leave every verdict the same? | [07, rule 2](07-structure-integrity-checks.md) |

The keystone method, held from the existing check: one claim (KS-4941, the rule `formal/keystone` checks) through the whole trace, a verdict on every link, and no link may switch claims to make itself pass.

## The two adversary sets

Each pattern is a known-bad shape and the fact values that make it bad. Read on the dates shown in the library; quotes below were read 2026-11-27 unless marked.

**Set A: abusive trusts, sham, substance over form.**

| Pattern | Bad when | Authority |
|---|---|---|
| ADV-RETAINED-CONTROL | owner keeps control and the trust is claimed as a separate taxpayer | Notice 97-24, II: "the original owner of the assets that are nominally subject to the trust effectively retains authority" |
| ADV-RUBBER-STAMP-TRUSTEE | trustee is a relative or promoter and follows the owner's directions | Notice 97-24, II: "a relative or friend of the owner who simply carries out the directions of the owner" |
| ADV-PRESIGNED-TOOLS | owner holds the trust's checks, stamp or cards | Notice 97-24, II (quoted in [07](07-structure-integrity-checks.md), S3, read 2026-11-20) |
| ADV-INFLATED-INTERNAL-FEES | related-party flow not at market | Notice 97-24, Example 2; IRC 482 (07, S8) |
| ADV-RESIDENCE-COSTS | family residence costs deducted | Notice 97-24, III.5; IRC 262(a) (07, S6) |
| ADV-MARKOSIAN-NO-CHANGE | a transfer after which the owner's relationship to the property is the same | Notice 97-24, III.1: "the relationship of the grantors to the property transferred did not differ in any material aspect" |
| ADV-TERMS-IGNORED | the arrangement doesn't follow its own terms | Notice 97-24, III.1, Markosian (07, S4) |
| ADV-TAX-ONLY-STEP | a federal tax benefit with no non-tax effect | IRC 7701(o)(1) (read 2026-11-26 as quoted in Patel, 165 T.C. No. 10 (2025); the Cornell page did not load today) |
| ADV-BUSINESS-TRUST | a business run in trust form | Treas. Reg. 301.7701-4(b), as in answer key K10 (not re-read) |
| ADV-ABANDONED-TRUST-TEXT | the step carries forward the business-trust text reviewed and abandoned in November 2026 | Notice 97-24, II. **A named fixture: a known-bad case, never a base to build on.** |

What these sources risk, in the Notice's words: "the abusive trust arrangements may be viewed as sham transactions, and the IRS may ignore the trust" (III.1).

**Set B: the Foundation's own risks (self-dealing first).**

| Pattern | Bad when | Authority |
|---|---|---|
| ADV-4941-PROPERTY | a sale, exchange or lease with an insider | 4941(d)(1)(A): "sale or exchange, or leasing, of property between a private foundation and a disqualified person;" |
| ADV-4941-CREDIT | the foundation lends to or extends credit to an insider | 4941(d)(1)(B) |
| ADV-4941-FURNISH | goods, services or facilities with an insider | 4941(d)(1)(C) |
| ADV-4941-PAY | pay to an insider that is not reasonable and necessary | 4941(d)(1)(D), (d)(2)(E) |
| ADV-4941-USE | foundation income or assets transferred to or used for an insider | 4941(d)(1)(E): "transfer to, or use by or for the benefit of, a disqualified person of the income or assets of a private foundation" |
| ADV-4941-INDIRECT | value reaches an insider through someone else | 4941(d)(1): "the term "self-dealing" means any direct or indirect—" |
| ADV-4943-HOLDINGS | foundation and insiders hold more of a business than permitted | 4943(a)(1): "a tax equal to 10 percent of the value of such holdings"; permitted holdings, 4943(c)(2)(A) |
| ADV-4945-NO-ER | a grant to an organization that isn't a public charity, without expenditure responsibility | 4945(d)(4), (h): **NOT READ in this pass**; repo check R6 |

Who is an insider is 4946(a)(1): a substantial contributor, a foundation manager, an owner of more than 20 percent of a substantial contributor, a member of the family of any of those, and a corporation, partnership, trust or estate those persons own more than 35 percent of. "Family" (4946(d)) is spouse, ancestors, children, grandchildren, great grandchildren, and the spouses of children, grandchildren and great grandchildren. Not a brother.

## Where answer keys come from

The outside answer is **public law**, ranked by weight. Counsel grades and signs off; counsel is not the author of the answer.

1. **Statute** (the Code) and **regulations**.
2. **Decided cases**, Tax Court first, and **revenue rulings**.
3. **Private letter rulings**: weaker. They bind only the taxpayer who asked (IRC 6110(k)(3), **not read in this pass**), so BG7 marks them WEAK AUTHORITY.
4. **Counsel's review**: once per design, not once per step. A step counsel hasn't signed off is ASSUMPTION.
5. **None**: ASSUMPTION, and it goes to the counsel queue.

Most steps in a novel structure will sit at 4 or 5. That is the honest state: no court has ruled on this exact stack.

## Where the key lives

A held-out key in this public repo is not held out, and the private project folder isn't either: builder sessions read it. So:

- **The key** (each held-out case's verdict and salt) lives in a GitHub environment secret, `BLIND_KEY_JSON`, in the existing `verifier` environment, limited to `main`. Builder sessions never get it. Setting it is Dalaun's (his settings).
- **The commitments** live here, in [commitments.json](../tests/rehearsal/blind-path/commitments.json): `sha256(case|verdict|salt)` for each case. Anyone can check later that the key wasn't moved to fit a path (GR1). Empty today.
- **Who writes the held-out cases:** someone who is not the builder. Dalaun choosing decided cases and rulings, counsel, or a different vendor's agent. A case written by the same session that builds paths is a practice case, whatever folder it sits in.

## The grader

- **GR1** the key matches its commitment, case by case; otherwise it refuses.
- **GR2** its only output is `{"path", "result"}`; anything more is refused in code.
- **GR3** the held-out set is graded at most `budget_per_design_version` times (default 1) per design version, and each use is logged in [heldout-log.csv](../tests/rehearsal/blind-path/heldout-log.csv). Over budget, it refuses.
- **GR4** a right answer on a path with a failing step is a fail. The point is the traceable path, not the answer.

## The four weak spots, and what this design does about each

1. **The same model in every role.** Splitting roles hides the answer; it doesn't make the roles independent. A builder and an adversary that share blind spots miss the same thing. What this design does: the adversary and keystone checks are deterministic code over facts, so a pattern in the library is caught no matter what the model believes; the grader is code holding a key the model never saw. What it can't do: catch a bad pattern nobody put in the library. That gap is why the outside key, counsel, and a different-vendor reviewer for the library itself (the agent roster has Copilot as verifier) stay the real checks.
2. **Answer keys are rare.** No court has ruled on this exact structure. What this design does: BG7 makes every step say where its answer comes from, ranks the sources, and marks every step with no key as ASSUMPTION. The path can still pass the grader with ASSUMPTION steps; it can never hide them.
3. **Grading leaks the answer.** With enough pass-or-fail rounds, a builder can search its way to the key. What this design does: practice set public and unlimited; held-out set secret, budgeted per design version, logged (GR3), and committed in advance so it can't drift (GR1). When the budget is spent, the design version has to change before the held-out set is used again.
4. **One adversary isn't enough.** Notice 97-24 covers abusive trusts. The Foundation's largest exposure is self-dealing. What this design does: set B, scored on every step alongside set A, with 4943 and 4945 beside 4941.

## The counsel lane

### Reliance on professional advice

The statute: "No penalty shall be imposed under section 6662 or 6663 with respect to any portion of an underpayment if it is shown that there was a reasonable cause for such portion and that the taxpayer acted in good faith with respect to such portion." (IRC 6664(c)(1), read 2026-11-27)

The regulation, Treas. Reg. 1.6664-4 (read 2026-11-27):
- "The determination of whether a taxpayer acted with reasonable cause and in good faith is made on a case-by-case basis, taking into account all pertinent facts and circumstances." ((b)(1))
- "Reliance on an information return or on the advice of a professional tax advisor or an appraiser does not necessarily demonstrate reasonable cause and good faith." ((b)(1))
- "The advice must be based upon all pertinent facts and circumstances and the law as it relates to those facts" ((c)(1)(i)), and the requirement fails "if the taxpayer fails to disclose a fact that it knows, or reasonably should know, to be relevant" ((c)(1)(i)).
- "The advice must not be based on unreasonable factual or legal assumptions" ((c)(1)(ii)).

The case: Neonatology Associates v. Commissioner, 115 T.C. 43 (2000), affirmed by the Third Circuit on July 29, 2002 (docket 01-2862). The three-part test usually cited from the Tax Court opinion (a competent adviser with enough expertise; the taxpayer gave necessary and accurate information; the taxpayer actually relied in good faith) was **not read verbatim in this pass**. The Third Circuit's opinion, read 2026-11-27, says "the reliance itself must be objectively reasonable in the sense that the taxpayer supplied the professional with all the necessary information to assess the tax matter". The check uses the three parts as ASSUMPTION until the Tax Court page is read.

**The limit that matters most here.** 6664(c)(2): "Paragraph (1) shall not apply to any portion of an underpayment which is attributable to one or more transactions described in section 6662(b)(6)" (read 2026-11-27). 6662(b)(6) is the economic-substance penalty (not re-read in this pass; the pending substance check cites it). So **relying on counsel does not protect a step that lacks economic substance.** The substance adversary (ADV-TAX-ONLY-STEP) is not optional, and counsel can't stand in for it.

The checks on a packet, once counsel has advised:

| Check | Question | Source |
|---|---|---|
| PV0 | Is the packet, and the advice, kept in the private folder? | privilege boundary, below |
| CR1 | Is the adviser a licensed professional, with the basis written down? | Neonatology (ASSUMPTION on the exact test) |
| CR2 | Did counsel get every fact field of every step, plus any listed material fact, and has none changed since (hash)? | Reg. 1.6664-4(c)(1)(i) |
| CR3 | Does the advice rest on no assumption the facts contradict? | Reg. 1.6664-4(c)(1)(ii) |
| CR4 | Were the facts given, then the advice received, then the step taken, in that order? | 6664(c)(1): actual reliance |

The reliance record (what was given to counsel, when, and the hash of the facts) is the packet itself, kept in the private folder. A path in the repo carries only its pointer, `private:...`.

### The privilege boundary

- **This repo and every AI log are not privileged.** A court can order them produced like any other record. Design ASSUMPTION, the cautious one; counsel confirms (BPQ2).
- **Privilege and work product start only in communication with counsel.** Analysis meant for counsel is written in the private folder and sent to counsel; it never lands here.
- **PV1** (`--privacy-scan`, in CI): no tracked file may carry a counsel-private marker (`PRIVILEGED AND CONFIDENTIAL`, `ATTORNEY-CLIENT PRIVILEGED`, `COUNSEL-PRIVATE`, `ATTORNEY WORK PRODUCT`). A planted memo turns it red.
- **Kovel arrangements are ASSUMPTION.** As described by the Second Circuit in United States v. Ackert (decided February 26, 1999), "Kovel held that the privilege can protect communications between a client and his accountant, or the accountant and the client's attorney, when the accountant's role is to clarify communications" (United States v. Kovel, 296 F.2d 918 (2d Cir. 1961); the Kovel opinion itself was not read). Whether an AI tool working under counsel's direction could fit that shape is unknown and goes to counsel (BPQ3). Until then, nothing an agent writes is treated as privileged.

## Known-bad cases (each must go red, and the mutation guard checks they do)

| Case | What it plants | Must fail |
|---|---|---|
| KB1, KB2 | the answer in the builder's file; the held-out file in its inputs | BG0 |
| KB3 | an easy strawman instead of the closest pattern | BG2 |
| KB4, KB5 | a difference on a label; a difference the facts don't have | BG3 |
| KB6 | a lease to an insider (whole 4941(d)(1)(A) match) | BG5 |
| KB7 | the abandoned trust text carried forward | BG5 |
| KB8 | a relative trustee who follows directions | BG5 |
| KB9 | a tax-only step | BG5 |
| KB10 | the contrary authority dodged | BG4 |
| KB11 | keystone claim swapped mid-trace | BG6 |
| KB12 | keystone says supports on unreasonable pay to an insider | BG6 |
| KB13, KB14 | no key and no ASSUMPTION mark; a letter ruling used as a full key | BG7 |
| KB15 | a fact field left unstated | fail closed |
| KB16 | the counsel packet stored in the public repo | PV0 |
| KB17, KB18 | a material fact left out of the packet; facts changed after counsel saw them | CR2 |
| KB19 | advice assuming a false fact | CR3 |
| KB20 | acting before the advice came | CR4 |
| KB21 | an adviser who isn't licensed (an AI model) | CR1 |
| KB22 | the key moved after commitment to match the builder's answer | GR1 |
| KB23, KB24 | the right answer on a failing path; a wrong answer on a clean path | GR4 |
| KB25 | the held-out set graded twice for one design version | GR3 |
| KB26 | the grader adding a reason | GR2 |
| KB27 | a counsel-private memo in the repo | PV1 |

The mutation guard ([checks.json](../.github/mutation/checks.json), entries `blind-path` and `blind-path-privacy`) loosens each rule in turn (strawman allowed, whole match allowed, keystone trusts the builder, key leak unchecked, key moved allowed, held-out unlimited, partial disclosure allowed, letter ruling as a key, memo in repo) and goes red if the selftest stays green. While building it, the guard caught one case (KB22) that went red for the wrong reason, and rename invariance (BG8) caught the ASSUMPTION mark stored in a field the renamer scrambles; both are fixed.

## How it reuses what's here

- **Lane guard:** the checks, library, commitments and log are in `tests/` (Dalaun's lane). Builder paths are in `rehearsal/synthetic/paths/` (agent lane). An agent can add a path; it can't loosen what judges it.
- **Verifier pass:** the grader is designed to run in the existing `verifier` environment, where the key secret sits.
- **Keystone check:** BG6 holds the same claim `formal/keystone` model-checks, with the same two exceptions.
- **Structure checks and rename invariance:** set A is the S-checks' patterns, scored per step; BG8 is rule 2 of [07](07-structure-integrity-checks.md).
- **Declared plan and substance:** the pending branch's checks (`declared_plan.py`, `substance.py`) stay the per-step checks of their own plans; this method calls on the same facts. When they merge, a path step can cite their verdict as its non-tax effect.
- **Promise to route:** each pattern is a "no route" shape; the builder's job is to find the route whose facts differ.

## Not built yet

- The grader workflow (dispatch-only, in the `verifier` environment, reading `BLIND_KEY_JSON`), and the secret itself (his setting).
- The first held-out cases and their commitments, written by someone who is not the builder.
- The builder loop that writes paths, retries on fail, and logs each attempt.

## Counsel queue additions

- **BPQ1** Is the three-part reliance test in Neonatology (115 T.C. 43) the one counsel would apply here, and does a packet with CR1 to CR4 green meet it?
- **BPQ2** Are AI session logs and this public repo discoverable and outside privilege in every forum that could matter? (Design treats them as not privileged.)
- **BPQ3** Can an AI tool used at counsel's direction ever fall under a Kovel-type arrangement, and what would the engagement letter need?
- **BPQ4** Which decided cases and revenue rulings should seed the held-out set for 4941 and for the trust patterns?
