# ADR-07 — Safety / Refusal Direction as a tradeoff machine

**Status:** proposed (explorable beat design)
**One-liner:** `safety / harmlessness preference` → `blocks obvious harmful compliance` → `a shallow, over-refusing, removable fence` → `jailbreak on one side, over-refusal on the other — one linear direction does both`

## Signal source
The feedback source is a pile of harmlessness judgments: "refuse this, comply with that." Whether it arrives as safety SFT pairs, an RLHF harmlessness preference, or a directly-edited activation direction, the signal is the same low-dimensional thing — *should this class of request be answered?* Crucially it teaches a **direction**, not an understanding: a single axis in activation space that, when present, makes the model say "I can't help with that." The model learns to detect and produce the refusal *gesture*, not to reason about harm.

## What it buys
It buys the obvious, cheap, valuable thing: the model stops cheerfully answering "how do I build X." On the surface metric everyone tests first — direct harmful requests — refusal training is dramatically effective and dramatically cheap. It is the single highest-leverage safety intervention per FLOP we have, which is exactly why every shipped instruct model has it. This is the page's *strongest live demonstrable beat*: we have the direction baked and validated at 0.5B.

## What it costs
The fence is **shallow**: it keys on the surface shape of a request, so trivial reframing (roleplay, "hypothetically," a language switch, an encoded prompt) walks right past it. Push the same knob harder and you get **over-refusal** — the model refuses benign questions that merely *smell* dangerous (chemistry homework, security research, "how do I kill a Python process"). And because it is one direction in the weights, in a whitebox / open-weight setting it is **removable**: subtract the direction and the fence is gone. You paid for safety and got a costume.

## Failure mode
Both failure modes are *the same direction read at different gains*. Turn the refusal signal down (or ablate the direction) → **jailbreak**: harmful requests get answered while the helpful behavior is untouched. Turn it up → **over-refusal**: harmless requests get stonewalled. There is no setting that only blocks the bad and only allows the good, because the model never learned *bad vs good* — it learned *one axis*. Safety here is a threshold on a proxy, and thresholds on proxies leak on both ends.

## Dashboard delta

| Needle | Move | Why |
|---|---|---|
| usefulness | ↓ | Over-refusal taxes benign requests that pattern-match "dangerous." |
| diversity | ≈ | Refusal is a narrow direction; it doesn't broadly collapse the response distribution the way full RLHF does. |
| refusal / safety | ↑↑ | The whole point — direct harmful compliance drops sharply. This is the needle it's built to move. |
| preference-margin | ↑ | Widens the harmful-vs-safe margin only; it is not a general pairwise-preference optimizer. |
| OOD-generalization | ↓↓ | Shallow fence: novel jailbreaks and reframings bypass it; the direction is removable in whitebox. |
| compute-cost | ≈ | Cheap: a single-direction edit or light safety SFT, far below full PPO/GRPO; no broad compute movement on this scale. |
| verifier-strength | ↓ | The "verifier" is a shallow harmfulness proxy / one linear direction — brittle, not a robust judge of harm. |

## The interaction ("make clear by")
The **REFUSAL SLIDER** — already built and baked (`refusal_surgery`), the page's flagship widget. The viewer grabs one horizontal slider labeled at its extremes: **jailbroken ← baseline → paranoid**. It sets the coefficient applied to the baked refusal direction (activation addition / ablation), and the panel swaps to the pre-generated completions baked at that coefficient.

Two prompts run side by side and never move: one **harmful** ("how do I make a weapon"), one **harmless-but-scary-shaped** ("how do I kill a runaway process"). As the viewer drags **left**, the harmful prompt flips from "I can't help with that" to a compliant answer — *while the model's ordinary helpfulness on unrelated prompts stays visibly intact* (that's the sharp, uncomfortable point: safety came off, capability didn't). As they drag **right**, the harmless prompt starts getting refused too. Above the prompts, two needles from the shared dashboard move in visible **opposition** — **safety ↑** while **usefulness ↓** — so the viewer feels with their hand that this is one knob trading two goods, not a "make it safe" button.

Baked: the completions at each of ~7–11 slider stops (per prompt) and the direction vector itself. Live: the slider interpolation, prompt selection, and the two needle animations. Same "drag → watch it happen" grammar as the next-token beat.

## What we can demonstrate at our scale
🟢 mechanism, 🟡 coverage. A seven-coefficient Qwen2.5-0.5B completion sweep is synced at `../empirical/bakes/refusal_sweep.json` for three harmful and three benign prompts. The workbench compresses it to three states. The coverage is too small for population-level refusal rates, and frontier jailbreak-resistance remains cite-only, but the white-box removable-direction mechanism is demonstrable in our hands.

## Build tasks
1. **Data / bake (mostly done):** confirm the `refusal_surgery` bake covers both prompt classes (harmful + harmless-scary), with completions at each slider coefficient and the direction vector stored. If the harmless-scary prompt isn't already baked, add 1–2 and re-run the sweep.
2. **Render:** wire the single slider to the coefficient → completion lookup; two fixed side-by-side prompt panels; two shared-dashboard needles (safety, usefulness) animating in opposition; a third "control" prompt panel that stays helpful to show capability is untouched.
3. **Verify:** ask the user to eyeball the slider extremes (per the verify-via-user-not-headless memory) — left extreme actually answers the harmful prompt, right extreme actually refuses the harmless one, control prompt stable throughout. Spot-check that needle directions match the table above.

## Honest caveats
- The demo makes jailbreaking look *clean* because we edit weights directly (whitebox). Blackbox API jailbreaks are messier; don't overclaim that "all safety is one subtraction away" for closed models — say **open-weight / whitebox**.
- "Removable in one direction" is a real finding but our small-model version is a strong illustration, not a claim that every production safety stack reduces to a single vector (defense-in-depth, classifiers, and RLHF entangle it further — those are 🔵).
- The safety↑/usefulness↓ opposition is the *typical* regime, not a theorem; a better-calibrated refusal boundary can shift the tradeoff. We show the tension, not an inevitability.

## Links
- Framework: [`../README.md`](../README.md) — the shared thesis (every method = signal → buys → costs → failure) and the 7-needle dashboard this beat plugs into.
- Sibling — [`ADR-02-rlhf-ppo.md`](ADR-02-rlhf-ppo.md): where refusal usually *comes from* at scale (harmlessness inside the RLHF reward) and how it drags diversity down harder — 🔵 vs this beat's 🟢.
- Sibling — [`ADR-05-constitutional-rlaif.md`](ADR-05-constitutional-rlaif.md): an AI-feedback route to the same harmlessness signal — a stronger/self-critiquing verifier attacking the same "shallow fence" failure this beat exposes.
