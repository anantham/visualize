# ADR-02 — SFT / Demonstrations as a tradeoff machine

**Status:** proposed (explorable beat design)
**One-liner:** `imitate ideal answers` → `format + helpfulness + instruction-following` → `capped at the demonstrator, style over judgment` → `confident, well-formatted, wrong outside the demonstrated shape`

## Signal source
Supervised demonstrations: pairs of `prompt → an ideal-looking completion`, written by a human or a stronger model. The training objective is pure imitation — maximize the likelihood of the demonstrated tokens. Nobody grades the model's own outputs; the demonstrator's judgment is baked into the answer text once, at authoring time, and never queried again. It's a teacher showing worked examples, not a teacher marking exams.

## What it buys
The single biggest usability jump in the whole pipeline: a raw next-token continuer becomes assistant-shaped. It answers instead of continuing the prompt, follows the demonstrated turn structure, adopts the register, and generalizes the *form* of instruction-following to instructions it never saw. It is also the cheap, stable floor every later method stands on — no reward model, no rollouts, one supervised pass.

## What it costs
The model is capped by its demonstrators — it can only imitate the ceiling of what it was shown, and it learns the *style* of good answers, not the *judgment* that produced them. So it will reproduce the surface shape of a demonstration even when the content is wrong: a correctly formatted citation to a paper that does not exist, a confident bullet list of falsehoods. It also narrows output distribution, collapsing toward the demonstrated register (measurable at 0.5B).

## Failure mode
Out-of-shape brittleness. Inside the demonstrated distribution it is competent; hand it a task type, format, or domain the demos never covered and it keeps wearing the costume of a good answer with nothing behind it — fluent, formatted, hollow. Because it optimizes "looks like the demo," it has no internal notion of better-vs-worse and no way to know it has left the region where imitation was safe. Style without judgment, delivered at full confidence.

## Dashboard delta

| Needle | Move | Why |
|---|---|---|
| usefulness | ↑↑ | The foundational jump: base continuer → instruction-following assistant. |
| diversity | ↓ | Collapses toward the demonstrated register; empirically real at 0.5B. |
| refusal/safety | ↑ | Only as much safety as the demos demonstrate — imitative, shallow refusals, not robust ones. |
| preference-margin | n/a | SFT optimizes likelihood, not a chosen>rejected gap; the preference-margin axis is absent. |
| OOD-generalization | ↓ | Generalizes format, not competence; confident-but-wrong once outside the demonstrated shape. |
| compute-cost | ↑ | The cheap floor of post-training: one pass over labeled pairs, no rollouts or reward model. |
| verifier-strength | n/a | No verifier in the loop — the demo author is the only judge, and only at write time. |

## The interaction ("make clear by")
A **demonstration bench** with a drag dial: **0 → 3 demos**. One fixed test prompt sits in the answer box. As the viewer drags the dial up, the box re-renders the *same prompt* answered by the model at each demo count — at 0 it rambles and continues the text (base-model behavior); by 3 it snaps into assistant shape, answering cleanly. Two shared needles move under their hand as they drag: **usefulness climbs ↑↑, diversity sinks ↓**.

Then the payoff toggle: **in-shape ⇄ out-of-shape prompt.** The demos all taught one narrow shape (say, short factual Q&A in a fixed format). Flip to an out-of-shape prompt the demos never covered and the model *still* emits the demonstrated shape — perfectly formatted, and wrong. A small **confidence-vs-correctness** twin bar shows confidence pinned high while correctness drops, and the **OOD needle** sits visibly low. The viewer feels the lesson with their hands: they trained a style, not a judge.

- **Measured endpoints:** a completed 400-step SmolLM2-360M run and paired base-vs-SFT generations now live in `../empirical/bakes/`. The base emits broken chat-template continuations while the SFT endpoint answers directly. The 24-output sample did **not** show diversity collapse (distinct-2 increased), so that cost must not be presented as measured by this bake.
- **Live-feeling but interpolated:** the intermediate 1/2 demo states on the dial stay illustrative unless we run the small ablation below — then they become real checkpoints.

## What we can demonstrate at our scale
**🟡 partial.** The base→assistant endpoint jump is measured. The OOD examples are real generations but remain a six-prompt teaching sample, not an average-case benchmark. The fine-grained per-demo dial (0/1/2/3) is illustrative until intermediate checkpoints are generated. SFT-specific diversity collapse is **not established by this bake**; adjacent base-vs-instruct evidence cannot be silently attributed to SFT alone. The preference-margin and verifier-strength needles read `n/a` because SFT structurally has neither.

## Build tasks
1. **Data/bake.** Done for base and step 400. Generate steps 50/100/200 if the smooth demo-count dial remains.
2. **Measure.** Expand beyond 24 outputs before making a diversity claim; add explicit hand labels or task checkers before drawing correctness bars.
3. **(Optional, upgrades 🟡→🟢).** Train quick SFT variants on 1 / 3 / all demos → real checkpoints for the demo-count dial instead of interpolation.
4. **Render.** Wire the 0→3 dial and the in-shape/out-of-shape toggle to the baked JSON; animate the shared dashboard needles (usefulness, diversity, OOD) on drag; add the confidence-vs-correctness twin bar to the out-of-shape state.
5. **Verify.** Have Aditya eyeball the generations and needle motion (verify-via-user, not headless screenshots); sanity-check the diversity numbers reproduce the established 0.5B collapse.

## Honest caveats
- **"3 demos makes an assistant" is a metaphor.** Real SFT uses thousands to millions of pairs; the smooth per-demo dial is illustrative unless we run the 0/1/3/all ablation. Three slots stands in for "demonstrations," not a literal count.
- **Our target SFT run is 360M.** The qualitative shape — format gain, diversity loss, OOD brittleness — is expected to transfer upward, but the magnitudes are our-scale, not frontier.
- **Shipped Instruct models are SFT+DPO, not SFT alone.** Isolating "what SFT contributes" needs our own completed SFT-only checkpoint, never a comparison against a released Instruct model.
- **The OOD break examples are curated to teach.** They demonstrate the failure mode exists and is easy to trigger, not an average OOD error rate.
- **The two `n/a` needles are load-bearing, not neutral.** SFT has no preference signal and no verifier by construction; that absence is exactly the gap the next beats fill.

## Links
- **Framework:** [`../README.md`](../README.md) — the shared grammar (signal → buys → costs → failure) and the 7-needle dashboard every beat moves.
- **Sibling — prior:** [`ADR-01-pretraining.md`](ADR-01-pretraining.md) — the base model SFT starts from; the prior-divergence "terrain" (which corpus each model saw) is the distribution SFT imitates *on top of*.
- **Sibling — next:** [`ADR-03-dpo.md`](ADR-03-dpo.md) — DPO/preference optimization; it fills the **preference-margin** needle SFT leaves flat and adds the notion of better-vs-worse that pure imitation lacks.
