# Lawyer-ready packet: the relay's finish line

[Back to the goal](GOAL.md) · grader: [tests/rehearsal/packet_scorecard.py](../../tests/rehearsal/packet_scorecard.py)

**SYNTHETIC.** Research for counsel review, not legal advice. The packet is built on the synthetic year; Dalaun gives a lawyer his real figures himself, outside this public repository.

## Why this is the finish line

The goal scorecard (`rehearsal/synthetic/SCORECARD.md`, SC1 to SC7) went 7 of 7 on 2026-11-24, but two of its passes hold only because the asset was sized at exact break-even, and every hard question was parked in the counsel queue as an assumption. Seven of seven proved the loop works. It did not produce anything a lawyer can act on.

The new finish line is a packet a lawyer can read in about an hour: each question researched against primary sources with a draft answer and an honest confidence label, the money case re-run at realistic sizes, and one plain memo of the structure. The relay runs until all six criteria below pass. The goal scorecard staying 7 of 7 is a floor.

Analogy: the goal scorecard was the dress rehearsal. This is the script you hand the director, with every line the actors weren't sure about marked in the margin.

## Who grades it

The grader is `tests/rehearsal/packet_scorecard.py`, in Dalaun's lane. The packet is in the agent lane, under `rehearsal/synthetic/packet/`. So the agents write the packet and cannot change how it is graded; a pull request that touches the grader or this file waits for Dalaun. Its own cases (a passing fixture, then one break per criterion) run inside the keystone check through `tests/rehearsal/pinned_checks.py`.

## The six criteria

| Id | Name | Passes when |
|---|---|---|
| PK1 | researched | Every question in `rehearsal/synthetic/counsel-queue.md` has `packet/research/Q<n>.md` with a draft answer of at least 25 words, a confidence label, and at least two primary cites, one of them a statute or regulation, each with its URL and `(read YYYY-MM-DD)`. |
| PK2 | framed | Every question labelled `likely` or `open` has a `Lawyer decides:` line saying exactly what the lawyer must decide. |
| PK3 | labelled | Every packet file carries the line `Research for counsel review, not legal advice.` |
| PK4 | sized | `asset_sized` and `asset_sized_pipeline` each have a family of at least three sizes in `scenarios.json` (the base plus scenarios with `"sensitivity_of": "<base>"`), spanning 0.75 times to 1.5 times the base income; every size ran in the engine; `packet/SENSITIVITY.md` has a row for each that matches the engine's output; and each family names a realistic case with a cited basis. |
| PK5 | memo | `packet/STRUCTURE-MEMO.md` has the four sections (The structure; Decisions only Dalaun makes; Risks; What a lawyer must decide), names the business trust, the Family Trust, the Foundation and the non-grantor design, lists every `likely` or `open` question by id under "What a lawyer must decide", and stays under 3,000 words. |
| PK6 | packet | `packet/LAWYER-PACKET.md` says the numbers are SYNTHETIC, links the memo, the sensitivity table and every research file, and the whole packet stays under 15,000 words (about an hour's reading). |

The grader prints `Packet: <n> of 6 pass; research <x> of <y> questions`. The research count is the relay's progress measure, so a run that researches questions without finishing PK1 still counts as movement.

## Packet rules for the runs

**Research files** (`rehearsal/synthetic/packet/research/Q<n>.md`), one per counsel-queue question, in this shape:

```
# Q<n>. <the queue's question title>

Research for counsel review, not legal advice.

- Question: <the question, in the queue's words>
- Draft answer: <what the primary sources say about this design, in plain words>
- Confidence: settled | likely | open
- Lawyer decides: <one sentence: the decision only a lawyer can make>
- What would change it: <the fact or authority that would flip the answer>
- Cites:
  - <IRC 674(c)>, https://www.law.cornell.edu/uscode/text/26/674 (read 2026-11-25)
  - <Treas. Reg. 1.674(d)-2>, https://www.ecfr.gov/current/title-26/section-1.674(d)-2 (read 2026-11-25)
```

- **Read it in this run.** Mark a cite `(read <date>)` only for a page fetched in the same run. Never cite from memory; a page that would not load is left out, not marked.
- **Primary sources.** Statute (law.cornell.edu/uscode, uscode.house.gov), regulation (ecfr.gov, law.cornell.edu/cfr), IRS rulings, notices, publications and instructions (irs.gov), Illinois statutes (ilga.gov), and agency pages such as sba.gov. Secondary sources may inform the answer but do not count toward the two.
- **Confidence, honestly.** `settled`: the text answers it on the design as written. `likely`: the text and IRS guidance point one way, but facts or state law could change it. `open`: the text does not settle it, authorities differ, or it turns on facts that do not exist yet. When in doubt, the lower label.
- **The most defensible reading, never the most favorable.** If the research shows a working assumption in the queue was wrong, rewrite that assumption with the new cite and say so in the research file; if that changes an engine input, it is an engine change (DAILY-RUN.md steps 3 and 4).
- **No advice.** Write what the sources say about this design. Never tell Dalaun to sign, form, fund or file anything.

**Sensitivity** (`rehearsal/synthetic/packet/SENSITIVITY.md`): a table with one row per sized scenario, `| <scenario id> | <version> | <asset net income> | <B minus A from the engine> |`, then one line per family: `- Realistic case (asset_sized): <scenario id>, <why this size is realistic, with a market or primary source URL and (read <date>)>`. The new scenarios go in `scenarios.json` with `"sensitivity_of"` set; sizes come from the stated span or the cited realistic basis, never from what makes arm B win.

**Memo** (`rehearsal/synthetic/packet/STRUCTURE-MEMO.md`): plain words, roles not names, synthetic figures only. The structure (business trust, Family Trust held non-grantor, Foundation), the decisions only Dalaun makes (including w, which the model holds at 0), the risks, and what a lawyer must decide, by question id.

**Packet** (`rehearsal/synthetic/packet/LAWYER-PACKET.md`): a one-page cover that says what the packet is, that the numbers are synthetic, and the order to read it in, with links to the memo, the sensitivity table and every research file.
