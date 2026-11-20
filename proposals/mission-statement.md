# Proposal: the longer mission line (for the owner's wording, not decided)

Status: open decision, partly applied. On Nov 20, 2026 the owner asked that nothing sit outside the lens of the full mission, so the draft data now uses option 1 (his line, exactly) on `:FoundationMission`, and C4 is built. The wiki's quoted mission line (Home, Examples) is unchanged until he picks the wording below.

## Where the repo stands

Every place in the repo says: "Empowering lives through health, education, innovation, and opportunity".
That is `:FoundationMission :hasMissionStatement` in `trust-domain-ontology.ttl`, plus the wiki pages (Home, Authority-Cascade, Examples).

## The longer line

The mission the owner confirmed on Nov 19, 2026:

> Empowering lives through health, education, innovation, and opportunity in furtherance of long-term human and systemic capability.

Options to choose from:

1. **His line, exactly as above.** Closest to what he confirmed.
2. **Same meaning, split in two fields.** Keep the short line as `hasMissionStatement` and add the second half as its own statement of the end goal (for example `purposeDescription` or a new `hasTelos` text). Easier to quote; the two halves read as means and end.
3. **His line with a light edit**, for example "...and opportunity, in furtherance of long-term human and systemic capability." (adds a comma only).

## What the second half would change, if adopted

Read this way, the second half is the end goal: health, education, innovation and opportunity are the means, and long-term capability is the end. A program that helps today but builds nothing lasting passes the first half and fails the second.

To make it checkable, not just written, the graph needs one more link and one more check:

- Each authorized activity names the lasting capability it builds (for example "trained clinical researchers", "a tutoring program that keeps running").
- A cascade check, C4, fails an authorized activity that names none.

Now built in the draft as C4, with `:buildsCapability`, `:LongTermCapability` and `:capabilityTest`. It is a new rule on every program, so it stays the owner's call, and the wording of each capability test should come from him or counsel.

## Files that would change once he picks

- `trust-domain-ontology.ttl`: the `hasMissionStatement` literal on `:FoundationMission` (and the comment on `:ExampleFoundationTrust`).
- `docs/wiki/Home.md`, `Authority-Cascade.md`, `Examples.md`: the quoted mission line.
