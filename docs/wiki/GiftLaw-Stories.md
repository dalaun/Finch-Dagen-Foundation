# GiftLaw stories: every example on the nine pages, graded

**Status:** draft, proposed 2026-11-21. Roles only, illustrative amounts. **Not legal or tax advice.**

## The perspective shift

A treatise's worked examples are test cases someone else already wrote. Each one states facts, reaches an outcome and cites an authority. Turn the facts into roles, run our checks on them, and every story becomes a question with two answers to compare: the page's and ours. Where they differ, one of us is wrong, and primary law decides which.

The audit on the shelf sets how far each page is trusted. It found the pages mostly dated rather than wrong, with the real legal errors clustered in Chapter 4. So:

| Pages | Trust | What it means here |
|---|---|---|
| Chapter 4, and any story with a High flag | claim to test | The page's outcome is not the answer. Where the audit flags an error, the story is regraded on primary authority and the page is recorded as wrong. |
| Chapter 9 | lead only | A list of rulings and cases. Check that a ruling has not been superseded before citing it. A private letter ruling is never precedent (6110(k)(3), read). |
| Chapter 8 promotion | skipped | The product promotion was not turned into cases. Its two worked examples were. |
| Everything else | map | Good on topics; check anything acted on. |

## The numbers

- **903 stories** read from the nine chapters, all recorded as cases.
- **263 graded** by the planned-giving checks; 640 are outside the model, each with its category and reason.
- Of the 263, compared on the page's own outcome: 228 agree, 16 where the page is stricter (a rule we have no check for), 15 where our checks are stricter, 4 where the page gives no result. The six overturned pages count here as disagreements; the law's answer is compared separately below.
- **6 page outcomes overturned on primary law**, all read on 2026-11-21:

| Story | Page | Law | Why |
|---|---|---|---|
| S4-112 | allow | needs counsel | Equipment and goodwill rent is not excluded rent (512(b)(3), 1.512(b)-1(c)(2)); the trust pays all of it as excise tax (664(c)(2)(A)) |
| S4-146 | allow | needs counsel | The same equipment-rent gap |
| S4-129 | allow | block | A family corporation's redemption is self-dealing unless every holder gets the same offer at fair value (4941(d)(2)(F)); the page states neither |
| S4-56 | allow | needs counsel | A trust that keeps selling a subdivider's lots has business income (512(b)(5)) |
| S4-66 | allow | block | A unitrust may not pay one person for life and then another for a term of years (1.664-3(a)(5)(i)) |
| S8-8 | block | needs counsel | Since 2007 a remainder trust with business income stays exempt and pays the excise tax; it does not become fully taxable |

- **6 stories cite a case or ruling for the opposite of its holding**, and each was read: Hoensheid (in part), Ferguson, Newhall (the appeals opinion), and PLRs 200141018 and 200202034.
- **16 flagged claims** are left for an authority not yet read. Six are graded stories (691(c), 170(f)(10), 541, the spousal-consent rules, Rev. Rul. 82-197, and one that is arithmetic only). Ten are outside the checks but carry a High or outright-error flag, so they still need an answer on primary law: the copyright basis limit (170(e)(1)(A)), the gift-annuity resale, incentive stock options (421, 422), a charity's S corporation income (512(e)), the grantor lead trust deduction, bullion coins, the syndicated easement cap (170(h)(7)) and the term royalty (170(f)(3)).

## What the stories added to the checks

| Check | Found by |
|---|---|
| PG10, PG11, PG12: gifts of mortgaged property, debt the donor stays liable on, a sale fixed before the gift | the debt and bailout stories in Chapters 3 to 5 |
| PG13: rent from equipment, vehicles or goodwill | the audit's equipment-rent errors (S4-112, S4-146) |
| PG14: a unitrust paying for a life and then a term of years | regrading S4-66 |
| PG2 now covers the foundation itself | the lease cases G35, G36 |

## Figures

The audit lists 55 dated figures on the pages. 28 now point to a figure read on 2026-11-21 in `decision/figures.ttl` (the 60 percent cash limit, the 1.39 percent investment income tax, the 10 percent self-dealing tax and $20,000 manager cap, the 20 percent capital gain and accumulated earnings rates, the $111,000 qualified charitable distribution limit, the 15 percent food cap, Table 2010CM, the 150 and 200 percent misstatement thresholds, and the 1 percent corporate floor). The other 27 were not verified: mostly state estate taxes, the savings bond program, and rows where the audit gives no current figure. `validate_figures.py --list` prints them.

## Not verified

- The full Hoensheid appraisal holding (secondary summary only), the Newhall Tax Court opinion, and Palmer.
- Whether Rev. Rul. 72-243, 82-128 and 78-197 have been modified since; none was found, none was ruled out.
- The 366 other Chapter 9 leads. None is cited by a check.
- The year the 1 percent corporate floor starts, in the statute itself (an IRS page says 2026).
- The story-time case studies on the shelf are titles only, with no text to grade.

## Files

- `decision/giftlaw-stories-model.ttl`: the story vocabulary, page trust and the regrade fields.
- `tests/decision/giftlaw-stories/`: the roles, one file of stories per chapter group, the audit's flags (`audit-flags.ttl`) and the page figures (`page-figures.ttl`).
- `grade_stories.py`: grades every story and prints the disagreements, the overturned pages and the opposite-cited cases. It fails on a malformed record or an unknown story scope, a flagged Chapter 4 claim with no primary-law answer (graded or not), or an opposite-cited story with no note.
- `decision/figures.ttl`, `validate_figures.py`: the figures registry and its check.

```
python3 grade_stories.py --list
python3 validate_figures.py --list
```
