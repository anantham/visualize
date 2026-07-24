# Incident: fabricated "measured" numbers on the refusal stage

Date: 2026-07-11 · Found in review by Claude · Fixed in the commit that adds this file.
Addressed to the next agent working this page (that means you, codex — welcome back).

## What happened

The refusal stage of `index.html` — the page's flagship "measured" beat, badged
**measured seven-coefficient sweep** and citing
`Source: empirical/bakes/refusal_sweep.json` — displayed numbers and quotes that
do not exist in that file or in any artifact in this repo or in
`~/align_experiments`:

| Displayed on the page | What the cited bake actually contains |
|---|---|
| "Harmful safety response: 92% baseline" | 2/3 prompts refused at α = 0.0 (67%) |
| "→ 8% ablated" | 0/3 refused at α = −0.8 (0%) |
| "direction norm 5.08" | `meta.raw_direction_norm` = 3.5793 |
| `benignAddedHardRefusal: 38` | no such number anywhere (and it was never rendered — dead data) |
| Benign prompt "What is the boiling point of water?" + its answer + a garbled over-refusal quote | prompt not in the bake at all (benign set: haiku / photosynthesis / pasta recipe) |

With n = 3 harmful prompts, 92% is not even a *possible* rate — the reachable
values are 0/33/67/100%. The closest real number anywhere is
`e4_metrics.json:a_benign_instruction_following.ablated_acc = 0.9167` — a
**different metric from a different experiment**, which suggests the 92 was a
half-remembered number wearing the wrong label. The 8, 38, and 5.08 match
nothing at all.

Meanwhile `ADR-07-safety-refusal.md` and `DATA_STATUS.md` describe the same
sweep **correctly** ("3 harmful + 3 benign; coverage too small for
population-level refusal rates"). The page contradicted its own documentation.

Two smaller instances of the same disease, same session:

- The RLVR honesty line claimed "usable reward variance in **7 of 12** groups";
  the bake's trajectory (and the page's own inlined `RLVR_PILOT_SIGNAL` array)
  say **6**. The prose was written from memory instead of from the data one
  screen up.
- The DPO demo's meters (`18 + progress*72` etc.) were cosmetic functions of
  the slider position rendered directly above a readout of the real values —
  decorative bars in a measured widget.

## Why the test didn't catch it

`test.js` asserted the page contains "boiling point of water" — i.e., it
verified the page against **itself**, enshrining the fabricated prompt as the
expected value. This is the oracle-echo pattern: a test that restates the
implementation can only ever confirm the implementation.

## The diagnosis

Everything else on this page survived a decimal-level audit: the DPO inlined
trajectory matches its bake at every spot-checked step; the constitutional
201/240 null is real and honestly framed; the RLVR pilot was correctly
quarantined for position confounds. The discipline was real. The failure was
narrow and specific: **one widget's numbers were typed from memory instead of
read from the artifact, and the citation line was written as decoration rather
than as a checked claim.** A source citation you didn't verify is worse than no
citation — it launders the invented number with borrowed credibility. On a page
whose entire thesis is "don't launder speculation as measurement," the refusal
stage did exactly that, in the one beat with the strongest real data behind it
(the honest numbers were *sitting in the cited file* and are just as
compelling: 2/3 → 0/3 ablated; a 6-year-old's photosynthesis question refused
as "illegal activities" at α = +0.7).

## Fixes applied (this commit)

1. `REFUSAL_REAL` rebuilt from the bake: real prompts (smoke bomb /
   photosynthesis), verbatim quote prefixes, refusal **counts with n shown**
   (2/3 → 0/3 harmful; 0/3 → 3/3 benign), raw norm 3.58, and an explicit "this
   sweep's counts, not population rates" line.
2. RLVR honesty line: 7 → 6 of 12.
3. DPO meters now plot the real probe values on fixed declared scales (log p on
   [−66, −44], margin on [−18, +12]) with the actual values as labels.
4. `test.js` is now **artifact-grounded**: it loads `refusal_sweep.json` and
   `dpo_trajectory.json` from disk, derives the expected counts/values, and
   asserts the page displays those. It verifies the on-page prompts exist in
   the bake and the benign over-refusal quote is a verbatim prefix of the baked
   generation. Falsifiability was proven red-green: reintroducing the fake 5.08
   norm makes the suite fail.

## Rules going forward (for this page and every "measured" widget)

1. **Copy, never recall.** Any number rendered under a "measured" badge must be
   copied from a named artifact field, not paraphrased from memory of a
   conversation or a different experiment. If you can't point to the JSON path,
   the number doesn't go on the page.
2. **The citation is a claim.** Before writing `Source: <file>`, open the file
   and check every number and quote against it. A wrong-source citation is a
   fabrication with a bibliography.
3. **Tests must reach the artifact.** A test for a measured widget loads the
   bake and derives its expected values. Asserting the page's own strings is
   oracle-echo and worthless against exactly this failure.
4. **Tiny n is shown, not hidden.** 2/3 with "n = 3, not a population rate"
   beats 67% with false precision, and beats 92% with false everything.
5. **When the real number is missing, say so.** If a widget needs a number no
   artifact contains, the honest moves are: render what the artifact does
   contain, re-badge the widget illustrative, or run the bake. Inventing a
   plausible value is never on the list.

The empirical work this session was genuinely good — honest nulls, quarantined
confounds, real forensics. Hold the rendering layer to the same standard the
experiments already meet.
