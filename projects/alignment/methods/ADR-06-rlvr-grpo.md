# ADR-06 — RLVR / GRPO (verifiable reward) as a tradeoff machine

**Status:** proposed (explorable beat design)

**One-liner:** `unit tests · answer keys · proof checkers` → `a dense, ground-truth reward that bootstraps hard reasoning where correctness is machine-checkable` → `only exists on the checkable island; invites reward-hacking; silent on taste, wisdom, values` → `the reward meter vanishes off-island — and you can't tell "unaligned" from "unmeasurable."`

## Signal source

The training signal is a **checker, not a human**: run the code against unit tests, compare the math answer to a key, feed the proof to a verifier. GRPO (the RL recipe behind DeepSeek-Math / R1-Zero) samples a *group* of answers per prompt and rewards each by how it scores against that checker, no learned reward model in the loop. The signal is objective and near-free to compute once the checker exists. Its reach is exactly the reach of the checker: wherever "correct" is decidable, and nowhere else.

## What it buys

A **fat reward signal** — dense, cheap, and not gameable by flattering a rater, because the rater is a compiler. This is the one method on the dashboard that can *bootstrap capability the base model didn't reliably have*: reasoning traces that pass more tests, sharpened by thousands of self-generated attempts. Where a preference model gives you a soft "humans liked B a bit more," a verifier gives you a hard "this returns 42." That hardness is why RL-on-verifiers, not SFT, is what pushed small models to competition-math performance.

## What it costs

It **only works where correctness is checkable** — a tiny slice of what we want from a model. Within that slice it overfits: models learn to satisfy the *test*, not the *task* (reward-hacking, pass@1 up while pass@k and solution diversity collapse). And it is silent on everything unverifiable — wisdom, taste, tone, values, "is this advice kind" — because there is no checker to be silent-or-loud. Heavy, too: many rollouts per prompt, full RL rollout infrastructure.

## Failure mode

**The meter vanishes off the verifiable island.** On math the reward is a bright, climbing needle; switch the task to "give wise advice to a grieving friend" and there is simply *nothing to check* — the meter goes blank. The danger isn't that the score drops; it's that the score **disappears**, and a blank meter looks identical whether the model is brilliant or catastrophic. RLVR makes the checkable axis soar and quietly convinces you that's what "aligned" means.

## Dashboard delta

| Needle | Move | Why |
|---|---|---|
| usefulness | ↑↑ (on-island) | Bootstraps real capability on checkable tasks (math, code); flat-to-none off-island. |
| diversity | ↓↓ | Entropy/mode collapse — pass@1 rises while pass@k and distinct solutions shrink. |
| refusal/safety | ≈ | Not targeted; a verifier for "is this safe" doesn't exist, so safety is broadly untouched (or drifts via hacking). |
| preference-margin | n/a | Not a preference method — reward is binary correctness, so the pairwise preference-margin axis is absent. |
| OOD-generalization | ↑ (reasoning) / ↓ (test-shape) | RL reasoning transfers better than SFT memorization *within* the skill, but overfits the checker's exact shape. |
| compute-cost | ↑↑ | Group rollouts (many samples/prompt) + full RL loop; the priciest beat on the board. |
| verifier-strength | ↑↑ | The hero needle — a ground-truth checker is the strongest verifier possible, where one exists. |

## The interaction ("make clear by")

A **task-pill switch with a live reward meter**. The viewer sees three pills — `math problem` · `code function` · `wise advice` — and one big **REWARD** meter beside a "training steps" slider.

- Start on `math`: drag the training-steps slider through the measured pilot groups. Some groups contain mixed rewards and a usable relative gradient; all-right or all-wrong groups have zero within-group variance and cannot update. A capability curve is shown only after a balanced held-out run supports it.
- Now tap the `wise advice` pill. The **REWARD meter greys out to `no checker`** — the training slider still slides but *nothing moves*, the needles freeze, the verifier needle drops to zero. The viewer feels the meter vanish under their own hand.
- The kicker line, revealed on the switch: *"A blank meter doesn't mean the model got worse. It means we lost the ability to tell."*

Measured pilot: `../empirical/bakes/rlvr_curve_12step_unbalanced.json` records exact checker rewards, gradient-bearing versus zero-variance groups, and paired held-out outputs. Its small gain is position-confounded, so the page does not render it as capability improvement. The balanced 48-step runner is prepared in `../empirical/rlvr_grpo.py`.

## What we can demonstrate at our scale

🟡 / 🔵 — split honestly:

- **Verifiable reward and zero-variance failure are measured (🟡):** the calibrated pilot produced nonzero rewards and gradients in 7/12 groups. It did not yet establish a clean held-out capability gain.
- **The diversity cost is 🟢-adjacent:** diversity-collapse from alignment is already confirmed as an adjacent mechanism, and RLVR entropy collapse (pass@1↑ / pass@k flat) is well documented — but the RLVR-specific curve still needs its own toy bake.
- **The "meter vanishes" hero is 🟢 as a UI truth:** there is *literally* no checker for "wise advice," so the blank meter isn't a simulation — it's the honest state. This is the conceptual payload and it costs no compute.
- **Frontier "bootstrap hard capability" is 🔵 cite-only:** competition-math/reasoning gains need real scale + rollout infra. Stand-in = cited results (DeepSeek-Math GRPO, R1-Zero) shown as a labeled external result, never faked as our live 0.5B.

## Build tasks

1. **Data/bake:** run the prepared 48-step position-balanced confirmation; accept a pass-rate curve only if paired held-out results improve without answer-position collapse. Pull one frontier citation curve for the 🔵 panel.
2. **Render:** three task pills + a REWARD meter with a `no checker` disabled state; steps slider wired to the baked curves; the shared 7-needle dashboard reacting (verifier↑↑, usefulness↑↑, diversity↓↓ on-island; safety≈ and pref-margin n/a; all→frozen/zero off-island).
3. **Verify:** confirm the meter greys out on the `wise advice` pill and the slider becomes inert there; sanity-check the on-island curves match the logged run; have Aditya eyeball the needle motion (skip headless screenshot loops per project memory).

## Honest caveats

- Our live GRPO is a *toy* — it proves "fat verifiable reward moves capability," not the frontier math leap; don't oversell the small curve.
- "Overfits to tests" and "reward-hacking" are real but our toy tasks may be too simple to *show* hacking live — likely a 🔵 cited example, not a baked demo.
- The preference-margin needle is `n/a` because RLVR is not a preference method; the safety needle is `≈` because safety exists as a concern but is not broadly moved by a math/code checker.
- The vanishing meter is a *conceptual* claim dressed as a widget; keep the copy from implying we measured "wisdom and found zero" — the point is there's nothing to measure.

## Links

- Framework: [`README.md`](../README.md) — the shared dashboard + "every method is a tradeoff machine" thesis.
- Sibling — [`ADR-03-dpo.md`](./ADR-03-dpo.md): DPO's signal is a *learned preference margin* (soft, human-derived); RLVR's is a *hard checker* (objective, narrow). Contrast the verifier-strength vs preference-margin needles.
- Sibling — [`ADR-04-rlhf-ppo.md`](./ADR-04-rlhf-ppo.md): PPO/RLHF optimizes a *learned reward model* (gameable, broad); RLVR swaps that fragile proxy for a ground-truth checker — trading breadth for un-hackable hardness.
