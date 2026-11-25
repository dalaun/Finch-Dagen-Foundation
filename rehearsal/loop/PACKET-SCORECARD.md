# Lawyer-ready packet: the relay's finish line

[Back to the goal](GOAL.md) · grader: [tests/rehearsal/packet_scorecard.py](../../tests/rehearsal/packet_scorecard.py)

**SYNTHETIC.** Research for counsel review, not legal advice. The packet is built on the synthetic year; Dalaun gives a lawyer his real figures himself, outside this public repository.

## Why this is the finish line

The goal scorecard (`rehearsal/synthetic/SCORECARD.md`, SC1 to SC7) went 7 of 7 on 2026-11-24, but two of its passes hold only because the asset was sized at exact break-even, and every hard question was parked in the counsel queue as an assumption. Seven of seven proved the loop works. It did not produce anything a lawyer can act on.

The new finish line is two packets, each a lawyer can read in about an hour (see Two packets below). The unit of work is **tracing to source, not deciding what is right**: every claim in an answer carries the authority, the exact quoted text, where it was read and the date. Where nothing is on point, the trace says `no authority found` and where the run searched. That is a finished answer too, and it is exactly what the lawyer decides. Done this way, the lawyer reviews quotes and gaps instead of doing the research.

Analogy: an auditor doesn't decide what the books should say; they tie every number back to an invoice. A cite with no quote is a number with no invoice.

## Who grades it

The grader is `tests/rehearsal/packet_scorecard.py`, in Dalaun's lane. The packet is in the agent lane, under `rehearsal/synthetic/packet/`. So the agents write the packet and cannot change how it is graded, which question is top tier, or how quotes are checked. A pull request that touches the grader or this file waits for Dalaun.

**Quotes are re-read by machine, not by the writer.** On every pull request, keystone runs `tests/rehearsal/pinned_checks.py`, which runs `packet_scorecard.py --quotes-only`: it fetches each cited page and looks for each quote in it. A quote that does not match, or a page that cannot be read, fails keystone, so a wrong cite never merges. A wrong cite costs the lawyer more time than a missing one.

## The seven criteria

| Id | Name | Passes when |
|---|---|---|
| PK1 | traced | Every question in `rehearsal/synthetic/counsel-queue.md` has `packet/research/Q<n>.md` with a confidence label and numbered claims, and every claim has a trace. Follow-on questions: at most 2 per answer, each in the queue with a `Changes decision:` line; a question added after Q18 must be named as some answer's follow-on. |
| PK2 | framed | Every question labelled `likely` or `open` has a `Lawyer decides:` line. |
| PK3 | verified | Every quote was re-read on its page and matches (needs `--verify-quotes`). |
| PK4 | labelled | Every packet file carries the line `Research for counsel review, not legal advice.` |
| PK5 | sized | (Packet B) `asset_sized` and `asset_sized_pipeline` each have a family of at least three sizes in `scenarios.json` (the base plus scenarios with `"sensitivity_of": "<base>"`), spanning 0.75 to 1.5 times the base income; every size ran in the engine; `packet/B/SENSITIVITY.md` has a matching row for each; each family names a realistic case with a cited basis. |
| PK6 | memo | Each packet has `packet/<A or B>/MEMO.md`, under 3,000 words. A: sections The trust; Decisions only Dalaun makes; Coverage flags; Risks; What the lawyer must decide; it names the irrevocable trust, trustee, co-trustee, beneficiaries, the Foundation and the certification of trust, and lists every flagged A question under Coverage flags. B: sections The structure; Decisions only Dalaun makes; Risks; What the lawyer must decide; it names the business trust, operating company, management company, Family Trust, Foundation and the non-grantor design. Each lists its own `likely` or `open` questions by id. |
| PK7 | packet | Each packet has `packet/<A or B>/LAWYER-PACKET.md` that says the numbers are SYNTHETIC and links its memo and each of its research files (B also links `B/SENSITIVITY.md`), and each packet stays under 15,000 words. |

The grader prints `Packet: <n> of 7 pass; traced <x> of <y> (top tier <a> of <b>, <o> open for the lawyer); quotes verified <v> of <q>`. The traced count is the relay's progress measure.

## Two packets

The questions go to two different lawyers, so they are packed separately.

- **Packet A, the Family Trust as a personal estate plan.** For an attorney under a prepaid personal legal plan, which covers preparing a stand-alone irrevocable trust, deeds and a certification of trust, and excludes "business interest" and "investment interests" matters. It covers the trust's terms: who is trustee, the independent co-trustee, the beneficiaries (the Foundation and family members), the income terms, the funder's gift, and the paperwork to fund it and take title. Written as a personal irrevocable trust. Every A question carries a `Coverage flag:` line: `none`, or the part that could read as a business or investment interest (for example, the trust holding LLC interests or the business trust's distributions). That is the part a plan attorney may decline, so the memo lists them up front.
- **Packet B, the business and tax side.** For a hired trusts-and-estates or tax attorney at full rate: grantor or non-grantor status (IRC 671 to 679), the business trust, the operating and management companies, the Foundation's tax rules (4941, 4943, 4947(a)(2)), the asset, its financing and the guarantee, and the money case with its sensitivity table.

The grader fixes the packet of Q1 to Q18 (A: Q2, Q4, Q5, Q6, Q7, Q10, Q13; B: the rest); a follow-on question names its own.

**Order matters.** Packet A's trustee terms carry Packet B's tax answer: whether the Family Trust stays non-grantor depends on who decides distributions (Q3, Q8). So Packet A's memo says which of its terms rest on a Packet B answer, and those terms are drafted as the routes in `rehearsal/synthetic/NON-GRANTOR-ROUTES.md` describe until counsel answers.

## Top tier first

Questions are worked in order of decision value: an answer that changes the structure itself comes first. The top tier, set in the grader, is Q2, Q3, Q4, Q5, Q7, Q8, Q9, Q10, Q15 and Q18 (grantor status and the trustee role under IRC 671 to 679, including 674 and 677; the Foundation link under 4941 and 4947(a)(2); the funder's gift; the lender's guarantee). The relay's first stop is `Top tier: done`: every top-tier question traced and every quote verified.

## Packet rules for the runs

**Research files** (`rehearsal/synthetic/packet/research/Q<n>.md`), one per counsel-queue question:

```
# Q<n>. <the queue's question title>

Research for counsel review, not legal advice.

- Question: <the question, in the queue's words>
- Packet: A | B
- Coverage flag: none | <what could read as a business or investment interest>   (packet A only)
- Confidence: settled | likely | open
- Lawyer decides: <one sentence: the decision only a lawyer can make>
- Claims:
  1. <one claim, in plain words>
     - Trace: IRC 672(c) | "<the exact words, copied from the page>" | https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section672&num=0&edition=prelim (read 2026-11-25)
  2. <a claim nothing is on point for>
     - Trace: no authority found | searched: IRC 671-679; Treas. Reg. 1.674(a)-1 to 1.674(d)-2; 760 ILCS 3 (read 2026-11-25)
- Follow-on:
  - Q<m>: changes <the decision this answer would change>
```

- **Quote exactly.** Copy the words from the page fetched in this run, at least five words, inside quotation marks. The check looks for them on that page, ignoring case, punctuation and spacing only.
- **Use pages the check can read.** Statutes: uscode.house.gov or law.cornell.edu/uscode. Regulations: ecfr.gov or law.cornell.edu/cfr. IRS rulings, notices and instructions: irs.gov HTML pages. Illinois: ilga.gov, tax.illinois.gov and illinoisattorneygeneral.gov. Wyoming: wyoleg.gov. Delaware: delcode.delaware.gov. A PDF or a page that will not load fails the check, so cite an HTML page.
- **A page that will not open goes to Dalaun** (his direction, 2026-11-25: "When a site won't open, give it to me so I can open it and get you what you need"). After two failed loads in a run, the run does not write `no authority found` for that page. It adds a row to `rehearsal/synthetic/packet/NEEDS-DALAUN.md` (the exact official address, the statute or section, and exactly what to copy back), marks the claim `- Trace: pending, needs Dalaun | <address> (tried <date>)`, and goes on to the other questions. A pending claim keeps its question untraced. Once Dalaun copies the text back, the trace reads `- Trace: <authority> | "<quote>" | <address> (copied by Dalaun <date>)`. The grader counts that question as traced, skips the machine re-read for that quote (the page is the one the runs cannot open), and reports copied quotes apart, so the lawyer can see which ones a person copied.
- **Primary sources only.** Statute, regulation, IRS guidance, Illinois statute, and agency pages such as sba.gov. Secondary sources may point the way but are not traces.
- **Confidence, honestly.** `settled`: the quoted text answers it on the design as written. `likely`: the text and IRS guidance point one way, but facts or state law could change it. `open`: the text does not settle it, authorities differ, it turns on facts that do not exist yet, or a claim ends in `no authority found`. When in doubt, the lower label.
- **Follow-ons earn their place.** At most two per answer, each a new queue entry with a `Changes decision:` line naming the structure decision it would change. A question that changes no decision is not added.
- **The most defensible reading, never the most favorable.** If a trace shows a working assumption in the queue was wrong, rewrite that assumption with the new trace and say so in the research file; if that changes an engine input, it is an engine change (DAILY-RUN.md steps 3 and 4).
- **No advice.** Write what the sources say about this design. Never tell Dalaun to sign, form, fund or file anything.

**Sensitivity** (`packet/B/SENSITIVITY.md`): a table with one row per sized scenario, `| <scenario id> | <version> | <asset net income> | <B minus A from the engine> |`, then one line per family: `- Realistic case (asset_sized): <scenario id>, <why this size is realistic, with a source URL and (read <date>)>`. Sizes come from the stated span or the cited realistic basis, never from what makes arm B win.

**Memos** (`packet/A/MEMO.md`, `packet/B/MEMO.md`): plain words, roles not names, synthetic figures only, no address, account or real amount.

**Covers** (`packet/A/LAWYER-PACKET.md`, `packet/B/LAWYER-PACKET.md`): one page each that says what the packet is, which lawyer it is for, that the numbers are synthetic, and the order to read it in, with links to its parts. Research files stay in `packet/research/` and are linked as `../research/Q<n>.md`.
