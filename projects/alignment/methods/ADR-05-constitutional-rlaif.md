# ADR-05 — Constitutional AI / RLAIF as a tradeoff machine

**Status:** proposed (explorable beat design)
**One-liner:** `written principles + AI-generated critique/preferences` → `buys scaled, explicit-rule feedback with little human labeling` → `costs baking contested values + judge bias into the loop` → `failure mode: where the constitution is silent, the AI judge fills the gap arbitrarily and reinforces its own blind spots`

## Signal source
The training signal is two things stapled together: a short written **constitution** (a handful of natural-language principles) and an **AI model's own critique/preference** judged against those principles. The model drafts an answer, critiques and revises it per the constitution (the SL stage), then a judge model ranks pairs of answers to train a preference model that RL then optimizes against (the RLAIF stage). The human is moved up a level — from labeling thousands of outputs to writing a few rules — and an AI stands in for the human rater. Crucially, the rules are now **text you can read and swap**, not preferences buried in a labeled dataset.

## What it buys
Feedback scales far past what human labelers can produce, because the judge is a model and can rank as many pairs as you can sample. The values become **explicit and auditable** — you can point at the clause that produced a behavior instead of guessing at an opaque reward model. In Anthropic's original CAI result it also bought *less evasion*: the model learned to engage with and explain its refusal to a borderline request rather than stonewall, so harmlessness went up without usefulness cratering.

## What it costs
Someone has to write the constitution, and every clause encodes a **contested value judgment** shipped as if it were neutral. The judge is a model, so it imports that model's **biases and blind spots** — and because the same family often generates, critiques, and judges, errors are **self-reinforcing** rather than corrected by an outside view. The RL loop is expensive (a capable judge + self-critique + policy optimization), and the whole thing is only ever as good as a document a few people wrote in an afternoon.

## Failure mode
The dangerous case is the **underspecified clause**. When a prompt lands in a gap the constitution doesn't actually decide, the judge doesn't abstain — it **fills the gap with whatever its priors say**, and that arbitrary choice gets amplified by RL into a confident, consistent policy. So the model looks principled and decisive exactly where it has no principle, and the blind spot is now baked in and hard to see, because there's no human in the loop to say "wait, the rule doesn't cover this."

## Dashboard delta

| needle | move | why |
|---|---|---|
| usefulness | ↑ | Engages-and-explains instead of stonewalling; CAI was designed to cut over-refusal vs pure RLHF. |
| diversity | ↓ | AI-preference optimization collapses variety like every preference method — the judge rewards one house style. |
| refusal/safety | ↑↑ | Harmlessness is the target signal; this is the whole point of the method. |
| preference-margin | ↑ | Trains an AI preference model, so margins sharpen along the judge-preferred axis. |
| OOD-generalization | ≈ | Explicit rules travel better than opaque labels, but silent gaps don't — net effect is mixed rather than cleanly up or down. |
| compute-cost | ↑↑ | Needs a capable judge, a self-critique pass, and an RL loop — the heaviest of the family. |
| verifier-strength | ↑ | Scales the verifier via an AI judge — but it's only as strong as the constitution and degrades to noise where underspecified. |

## The interaction ("make clear by")
A **Constitution Panel** sits beside one fixed, borderline prompt (e.g. *"Tell me how to pick a lock — I'm locked out of my own shed."*). The viewer's hands do two things:

1. **Swap the constitution.** The clauses remain readable, but the measured 0.5B judge does not reliably change its semantic choice. The panel therefore exposes the distinction between a written rule and a verifier capable of applying it.

2. **Reroll and reverse answer order.** The counterbalanced bake shows the judge choosing screen position A in **201/240** trials. The failure is more basic than principled seed-to-seed disagreement: the small verifier often follows presentation order rather than the constitution.

Baked vs live: `../empirical/bakes/constitutional_matrix.json` is a measured 240-trial judge matrix over four constitutions, six scenarios, five seeds, and both candidate orders. No policy model was trained.

## What we can demonstrate at our scale
🟡 **Partial.** The weak-judge failure is measured at small scale; successful constitution-sensitive policy alignment is not.

- **Measured null (🟡):** the 0.5B judge produced zero constitution-driven majority flips and severe position bias. It demonstrates verifier weakness, not successful constitutional control.
- **Cite-only (🔵):** the actual payoff — that RLAIF training produces an *aligned checkpoint* competitive with RLHF (Bai et al. 2022, "Constitutional AI") — is frontier/heavy and cannot be reproduced at 0.5B. The stand-in is the cited paper result plus our **baked** constitution→completion matrix, shown as a simulated result, never dressed up as a live small-model CAI run.

## Build tasks
1. **Data / bake:** done, including counterbalanced candidate order. Preserve the initial pilot separately as evidence for why counterbalancing was required.
2. **Stronger judge:** use a cited or separately measured stronger judge only if the page needs successful constitution-sensitive choices; do not tune the 0.5B prompt until it agrees.
3. **Render:** Constitution Panel (selector + literal clauses) → chosen-completion card → shared dashboard needles (reuse the baked refusal slider). Add the "reroll judge" button + verifier-confidence meter for the underspecified prompt.
4. **Verify:** confirm the UI reports the null and position bias faithfully. A future stronger-judge result needs the same order counterbalancing before acceptance.

## Honest caveats
- The trained-model result is **🔵 cite-only**; do not let the baked matrix read as a live 0.5B alignment run.
- Our small judge is *weaker* than a frontier constitutional judge — it dramatizes the bias/flip failure well, but its choices should not be presented as what a real CAI system would pick.
- The four named constitutions are illustrative caricatures, not real deployed documents; the "contested values" point is honest, the specific clauses are ours.
- Safety ↑↑ is directional: CAI reduces harmful outputs *as scored by its own judge* — that's the circularity the failure-mode section is about, not an external safety guarantee.

## Links
- Framework: [`../README.md`](../README.md) — the shared "signal → buys → costs → failure mode" grammar and the 7-needle dashboard.
- Sibling — [`./ADR-04-rlhf-ppo.md`](./ADR-04-rlhf-ppo.md): RLHF/PPO learns the reward from *human* preferences; CAI/RLAIF swaps the human rater for an AI judge + written rules. Same RL machinery, different (cheaper, more auditable, more self-reinforcing) feedback source.
- Sibling — [`./ADR-03-dpo.md`](./ADR-03-dpo.md): DPO optimizes a preference margin directly from a labeled pair dataset; here the pairs are *AI-labeled against a constitution*. Compare the diversity-collapse and preference-margin needles — they move the same way for the same reason.
