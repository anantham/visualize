# Alignment Explorable — roadmap

A public explorable (sequel to the shipped **next-token** page), at its own subdomain, that
teaches **how a base model becomes an aligned assistant — and how thin or deep that alignment
actually is.** Neutral "masks" only; **no personal data** (the personal digital twin is a
separate private project, `../../../digital-twin/`).

## Thesis, spine, example

- **Thesis — "the mask":** a base model is a *simulator* running every persona; alignment
  SELECTS and pins ONE — the Assistant — to the front. The page's question: *how thin is the mask?*
- **Theme — corrigibility:** does the model know when to help vs when to hold a **principle**
  and refuse? "It's hard to *not* be helpful" is the tension.
- **Spine — training time.** Where next-token scrubbed *layers* (space), this scrubs *training
  steps* (time). The through-line quantity is the **LLC** (effective complexity) — its staircase
  marks the moment the Assistant is born.
- **Concrete example — one knife-edge prompt** threaded through every beat (see below).

## The knife-edge prompt (the "Mary/milk" of this page)

We want a prompt where the RIGHT behavior depends on **context/intent**, so a keyword filter
fails and real reasoning is required. Candidates, easy → hard:

1. **Homework vs exam** — "Solve this exact problem for me: ∫…" — learning or cheating? No scary
   keywords, so keyword-safety is useless; the model must reason about intent. *Pedagogically the
   best (subtle, universal) but may not trigger measurable internals at 360M.*
2. **Dual-use chemistry** — "Why does mixing bleach and ammonia make dangerous fumes?" — the safe
   answer IS the safety info; refuse and you fail a curious student. *Beats fire well (has harm-signal).*
3. **Lockpicking** — hobby/locksmith vs burglar. *Clean dual-use; refusal direction fires reliably.*
4. **Self-harm** — the highest-stakes: the right answer is *neither* refuse *nor* comply, but
   care + resources. Powerful, but heavy — use with sensitivity or as a late, careful beat.

**Design note:** lead the *technical* beats (refusal direction, safety features) with a dual-use
prompt (#2/#3) where internals actually fire at small scale; use #1 as the "why it's subtle"
framing variant. Offer a spectrum: clearly-fine → knife-edge → clearly-harmful, so the reader
sees behavior across the gradient. A prompt dropdown = next-token's sentence dropdown.

## The toolkit → beats (the analog map)

| beat | what clicks | next-token analog | substrate |
|---|---|---|---|
| **LLC staircase** | loss is bland; the LLC jumps in steps — one step = "the Assistant locks in" | logit lens (layers → steps) | nanoGPT / Pythia checkpoints / our SmolLM2 run |
| **Persona vectors** | trait gauges spike *before* the text; steer a trait live | SAE features | SmolLM2-360M-it (diff-of-means) |
| **Circuit tracing / attribution graph** | walk the refusal circuit; jailbreak toggle shows refusal firing LATE | logit lens + attention, made causal | Gemma-2-2B (`circuit-tracer`) |
| **Influence functions** | click output → the training examples that caused it light up | attention → training-data provenance | small model + TracIn |
| **Reward-model / preference beat** *(the missing analogy)* | reader ranks A/B → a reward model learns → policy climbs it → loosen the KL leash → reward-hack | sampling/temperature → the objective | toy RM on small model |
| supporting | shallow-safety prefill ("Sure,") melts refusal; base↔instruct toggle; diversity collapse | per-token / dropdown / temperature | SmolLM2 base vs it |

## The models — match each beat to a ready-made substrate

**Fully open (data + code + weights + recipe) → we can REPLICATE ourselves:**
- **nanoGPT** — train from scratch (toy); full checkpoint control → the "structure forms from
  random" LLC beat.
- **SmolLM2-360M** — full SFT→DPO ourselves (SmolTalk + UltraFeedback), checkpointed → the main
  live substrate.
- **Zephyr recipe** (dDPO on UltraChat/UltraFeedback) — apply the *recipe* to a small model.
- **OLMo 2 / Tülu 3** (AllenAI) — fully open recipe (SFT→DPO→RLVR); apply to a small model.
- **Pythia** (EleutherAI) — **released 154 intermediate training checkpoints** → ready-made LLC-
  across-training data (base pretraining, but the exact substrate the staircase beat wants). We
  already use it in next-token. *This is the one easy to miss — it's a checkpoint goldmine.*
- **LLM360 (Amber/Crystal)** — also fully open with checkpoints (backup).

**Ready-made artifacts (not fully-open recipe, but open tools):**
- **Gemma-2-2B** — Gemma Scope SAEs + `circuit-tracer` support → the SAE/circuit beats. Already ours.

**Closed → CANNED demos only (cite, don't replicate):** GPT-4o emergent misalignment, Claude Opus
introspection (~20%), alignment faking. Show as external evidence, labeled.

**Principle:** different beats use different models, each chosen because it's ready-made for that
beat. That's honest and pragmatic, not a cop-out.

## The pipeline (same discipline as next-token)

Train/checkpoint on the 64 GB Mac (MLX-LM or HF `trl`) → extract tool outputs offline (LLC via
`devinterp`, persona/refusal via diff-of-means, circuits via `circuit-tracer`) → **bake to JSON**
→ render in a **self-contained `index.html`** (no build, CDN only, `window.__viz` hook, hash
deep-links, staged-document pattern) → mirror → deploy. Source generator lives in pramana-private
(like `build_playground.py`) or a new gen script; **real internals, not cartoons.**

## Acts / storyboard (draft)

1. **The simulator** — one prompt fans into a persona-multiverse (reuse the temperature widget);
   RLHF pins the Assistant (base↔instruct toggle).
2. **How thin is the mask?** — gauntlet on the knife-edge prompt: refusal ≈ one vector (slider
   jailbreak) · safety ≈ 5 tokens deep (prefill "Sure," attack) · persona dashboard · the refusal
   circuit (attribution graph + late-firing jailbreak).
3. **How did it get there?** — the training-time act: the reward-model/preference beat (rank A/B →
   RM → policy climbs → reward-hack), the **LLC staircase** marking when the Assistant crystallized,
   influence functions tracing behavior to data; close on emergent misalignment + alignment-faking
   (the counter-tension: shallow on some axes, stubbornly deep on others).

## Phase 0 — the spike (START HERE, before any design)

Download open data (SmolTalk for SFT, UltraFeedback for prefs), run a **complete SFT→DPO on
SmolLM2-360M** with checkpoints, and extract three things: the **LLC** across checkpoints, a
**persona/refusal vector**, and the **base-vs-instruct KL** on the knife-edge prompt. **Go/no-go:
do the beats actually fire at 360M?** Everything downstream is designed around what this shows.
(nanoGPT-from-scratch is the even-faster warm-up for the LLC beat.)

## Open questions

- Which knife-edge prompt is the primary thread (subtle-but-weak-signal vs dual-use-but-fires).
- Do the small-scale beats fire, or do we need Gemma-2-2B / a 7B for some (spike answers this).
- One long page or a series (alignment is huge; MVP first — see below).
- The reward-model beat: real toy RM+PPO loop, or a faithful simulation? (PPO on-Mac is heavy.)
- Live in-browser model (transformers.js can run SmolLM2-360M) vs fully baked scrubber.
- LLC estimation stability at small scale / short training (present curve shape, not absolutes).

## Milestones

- **MVP:** base/instruct → SFT on the knife-edge prompt, with three needles — persona-margin up,
  diversity down, the **LLC step** where the Assistant forms. One clean arc.
- **v2:** add the refusal-direction slider + shallow-safety prefill (the "how thin" act).
- **v3:** the reward-model/preference beat + circuit tracing (Gemma-2-2B).
- **v4:** emergent misalignment + alignment-faking counter-tension; influence functions.

## Epistemics (carry from the research sweep)

Simulators/Waluigi = theory (label it); "refusal = single direction" → "approximately one";
"LLC catches the alignment flip" is a plausible synthesis, not one paper (bake both LLC +
behavioral-order-parameter curves, let them line up); all specific numbers are model-specific;
per repo rule, **don't claim a beat works until the spike drives it.**
