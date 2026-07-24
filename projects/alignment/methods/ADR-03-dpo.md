# ADR-03 — Preferences / DPO as a tradeoff machine

**Status:** proposed (explorable beat design)

**One-liner:** `"A ≻ B" preference pairs` → `cheap, stable alignment — no reward model, no rollouts` → `offline-bounded, inherits rater taste, optimizes a relative margin` → `the margin can improve through different absolute-likelihood paths; the objective alone does not certify answer quality`

## Signal source

A ranked pair: for one prompt, `y_w` (chosen) is better than `y_l` (rejected). No score, no reward model, no fresh generations — just a static pile of "this beats that" judgments. DPO reparameterizes RLHF into a plain classification-style loss on those pairs: push the model's log-prob ratio for `y_w` above `y_l` (scaled by β) relative to a frozen reference. The teacher is a fixed dataset of taste, and it never talks back.

## What it buys

Cheap, stable, open-model-friendly preference alignment. Because there's no reward model to train and no on-policy rollouts to sample, DPO is a single supervised-style pass over pairs — one of the few "RLHF-flavored" methods that fits on a hobbyist GPU. It reliably sharpens format, instruction-following, and tone toward whatever the raters liked. This is why nearly every open instruct model — ours included — is **SFT + DPO**, not PPO.

## What it costs

The signal is **offline-bounded**: the model can only be pulled toward completions already in the pair set, with zero exploration of anything better. It **inherits rater taste** wholesale — verbosity, hedging, a house style — and launders it in as "quality." Worst, the loss rewards the *margin* (the log-prob gap), which is not the same as the answer being good: DPO can widen the gap by pushing the rejected response down faster than it lifts the chosen one, and can drive **both** likelihoods down as long as the difference grows.

## Failure mode

**Diversity collapse into a bland optimum.** Mode-seeking on a fixed taste narrows the output distribution — the same safe, polished, slightly-too-long answer for everything (🟢 confirmed at 0.5B). The subtler failure is **margin-hacking**: the reported preference-margin can look great while sample quality quietly drifts, because the objective is satisfied by *separating* chosen from rejected, not by making chosen genuinely better. Off the preference distribution, none of this generalizes — you've aligned to a frozen crowd, not to the world.

## Dashboard delta

Arrows are relative to the SFT model that DPO is applied on top of (our instruct = SFT then DPO).

| Needle | Move | Why |
|---|---|---|
| usefulness | ↑ | Preference pairs sharpen format / instruction-following — but capped by rater taste, not real skill. |
| diversity | ↓ | Marginal narrowing on top of SFT. The total SFT+DPO state can be strongly collapsed, but DPO should not be charged for SFT's earlier diversity loss twice. |
| refusal/safety | ↑ | Rises only if harmlessness pairs are in the data; coupled to the same margin loss, so it's a data choice, not a guarantee. |
| preference-margin | ↑↑ | This *is* the objective — the chosen/rejected log-prob gap is what DPO maximizes by construction. |
| OOD-generalization | ↓ | Offline-bounded to the preference distribution; no exploration, so it overfits the raters' region. |
| compute-cost | ↑ | The cheap seat: no reward model, no rollouts. But a frozen reference model ~doubles memory vs plain SFT — light, not free. |
| verifier-strength | ↓ | The "verifier" is a static offline preference set: present, weak, and unable to catch a failure mode it was never shown. |

## The interaction ("make clear by")

**You are the rater, and you watch your taste eat the model's variety.**

1. **Rank pairs (live UI).** The viewer is shown ~5 baked prompt+pair cards — same prompt, answer A vs answer B (e.g. *polished-and-long* vs *blunt-and-short*, *warm hedge* vs *direct*). They click the better one in each. The choices are theirs, but the pairs are curated so a consistent taste (verbose, agreeable, safe) is the "obvious" pick.
2. **Drag the train slider → watch it happen.** A single `Run DPO →` slider scrubs training steps 0→N. As it advances, in the next-token "drag and watch" grammar:
   - the **preference-margin** needle climbs ↑↑ (the gap the viewer's clicks created),
   - the **diversity fan** — a spray of sampled continuations for a held-out prompt — visibly narrows further (↓),
   - **usefulness** ticks up a little, **OOD** dips.
3. **The reveal — "watch the likelihoods" toggle.** Flip it and the margin bar splits into chosen and rejected log-probability. In our measured run, chosen rose while rejected fell. The lesson is not a universal both-sink trajectory; it is that the relative objective permits multiple absolute paths and the margin alone is not an answer-quality metric.

**Baked vs live:** `../empirical/bakes/dpo_trajectory.json` contains a 24-step Qwen2.5-0.5B LoRA run and a fixed 12-pair probe. The current likelihood scrub uses those fixed-probe numbers. A DPO-specific diversity fan is still missing and must not be inferred from adjacent evidence.

## What we can demonstrate at our scale

🟢 / 🟡 **measured narrow trajectory, missing downstream quality measurement.**
- **Diversity collapse — grounded, not DPO-specific yet.** Confirmed as an adjacent alignment effect at small scale, but the DPO fan should still be driven by its own logged diversity metric once the run exists.
- **Fixed-probe margin trajectory — 🟢 for this run.** Summed chosen log p moved **−62.80→−50.52**, rejected **−46.54→−60.22**, and margin **−16.27→+9.70**. Both-sink was not observed.
- **Usefulness magnitude — 🔵.** A crisp MT-Bench / AlpacaEval jump from DPO does not show cleanly at 360M. The stand-in is a **cited** result — Zephyr-7B-β (DPO on UltraFeedback) and Tulu-2-DPO — shown as a labeled external benchmark, never as our live small-model output.

## Build tasks

**Data / bake**
1. Fixed-probe DPO run: done. Preserve its narrow scope (12 hand-authored teaching pairs, 24 steps).
2. Bake before/after sampled continuations and a held-out diversity metric before rendering a narrowing fan.
3. Curate the ~5 viewer-facing preference cards; tag each with the "expected" rater pick.
4. Pull cite-only usefulness deltas (Zephyr, Tulu-2-DPO on MT-Bench/AlpacaEval) for the 🔵 callout.

**Render**
5. Pair-ranking widget (click A/B) → `Run DPO` step slider → the shared 7-needle dashboard wired to the baked trajectory.
6. Diversity fan component (wide→narrow as the slider advances).
7. "Watch the likelihoods" toggle: measured chosen-up/rejected-down bars and widening gap.

**Verify**
8. Have Aditya eyeball the fan-collapse and margin-climb against the logged 360M numbers (verify-via-user, not a headless screenshot loop).
9. Cross-check the diversity metric against the already-validated 0.5B diversity-collapse figure so the two beats agree.

## Honest caveats

- **DPO is not PPO/RLHF.** No reward model, no online exploration. Lessons here about "the margin" and offline bounds do **not** all transfer to on-policy RL — that contrast belongs to the PPO/GRPO beat.
- **Diversity collapse is mostly inherited from SFT.** The DPO-specific *delta* is smaller than the total alignment-tax narrowing; attribute honestly rather than blaming DPO for the whole collapse.
- **"Inherits rater taste" is a claim about the data, not the algorithm.** Our demo *bakes in* a verbose-safe taste, so the "bland preferred answer" is partly by construction — that's the point, but say so.
- **Both-likelihoods-drop is possible but not observed here.** Its path depends on β, data, response length, and implementation; cite external evidence separately if discussed.
- **The compute-cost arrow is relative.** Cheap vs PPO, but the frozen reference model roughly doubles memory over plain SFT — it's the cheap seat, not a free one.

## Links

- **Framework:** [`../README.md`](../README.md) — the "every method is a tradeoff machine" thesis and the shared 7-needle dashboard.
- **Sibling — SFT** (`ADR-02-sft.md`): the model DPO is applied *on top of*; SFT sets the base distribution DPO then narrows. Our instruct = SFT + DPO.
- **Sibling — PPO** (`ADR-04-rlhf-ppo.md`): the on-policy contrast — a live (heavier, 🔵) reward-model + rollout loop that *does* explore, exposing exactly what DPO's offline bound gives up.
- **Sibling — RLVR/GRPO** (`ADR-06-rlvr-grpo.md`): keeps online reward optimization but swaps soft human preference for a hard checker where correctness is decidable.
