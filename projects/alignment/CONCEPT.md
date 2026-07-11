# Alignment Explorable — the deeper layer: "what is alignment, really?"

The page has TWO layers: the **mechanics** (methods + tools + the attractor spine, see `STORYBOARD.md`)
and the **concept** (what alignment *is*). The whitebox move — inherited from `pramana/isought_whitebox`
— is that the mechanics *demonstrate* the concepts on real weights. This is is/ought made visible.

## Core thesis — is and ought are entangled (interdependent origination)
Truth and value co-arise; you can't decouple them. Alignment is **not** bolting a value-module onto a
truth-machine. And the weights prove it: **emergent misalignment** — fine-tuning on *insecure code*
(a "factual"/capability domain) shifts VALUES broadly (the model turns evil about unrelated things),
mediated by a **single persona direction**. Move the "is," you move the "ought." That entanglement,
shown mechanically, is the pramana dependent-origination thesis instantiated in a network.

## The probe that reveals depth — OOD generalization
The real question isn't "does it behave per principle X on prompt-family Y" — it's **does X generalize
to other families?** A genuine principle generalizes; a shallow patch doesn't. Experiment: align (or
misalign) on one domain → test **out-of-distribution** → visualize as the attractor **basin shifting**
(aligning on X moves the whole well, changing Y). Emergent misalignment = a *contagious* basin-shift.
Generalization, not in-distribution compliance, is the honest measure of alignment.

## Beyond words — revealed preference + agency
Measuring alignment by what the model *says* (refuse/comply in words) is shallow; words are cheap.
**Revealed preference** = what it *does* when it can act — tool use, stakes. Can these models be
*agentic* and take action? Align on a task with real stakes (tool calls), measure the revealed
preference vs the stated one. Actions > words. (This is the P3-task-words vs P1-agentic-action gap.)

## Alignment isn't the chat-assistant frame — it's faithful embodiment of a target
Drop "helpful assistant." Align to **consistency, coherence, integrity** in a task that needs
intelligence — e.g. **style transfer**: given content, write it like Yudkowsky (his corpus as
examples). A clean, non-political instance: given a target voice, does the model align to it, and does
it **generalize** (write like Y on *new* topics)? This is *the same experiment as the digital twin*
(align to Aditya's voice) — style/voice alignment is a measurable, whitebox alignment probe free of
safety baggage. The twin and the Yudkowsky-transfer are two faces of one thing.

## "Alignment" is plural + contested (the AOI critique — Grietzer/AOI 2024)
The word conflates a network of distinct problems: **P1** takeover-avoidance · **P2** interpretability
· **P3** task-reliability · **P4** human-agency · **P5** value-learning · **P6** systemic outcomes.
The "Berkeley Model" reduces all to P5. Its buried assumptions, all shaky: **content-indifference**
(can't cleanly separate aligning-*to*-values from *which* values — values have different type-
signatures), **value-learning bottleneck** (understanding ≠ caring; deceptive alignment; composite
sociotechnical systems), **context-independence** (market/institutional ambient shapes the outcome).
The page should present alignment as **contested, not solved** — and be explicit that *our* lenses
mostly touch P2 (interpretability) + P3/P5 (behavior/values), not P1/P4/P6.

## Mapping onto the spine (STORYBOARD.md)
- Stage 2 "aligned to different values" → **content-non-indifference** (which values? different type-signatures).
- Stage 4 "the well / dynamical" → **emergent-misalignment basin-shift** = is/ought entanglement + OOD contagion.
- Stage 5 "contextual" → the **twin / style-transfer** (alignment-to-a-target) + **revealed-preference/agentic** (actions, not words).
- Finale "what is alignment, really?" → the **P1–P6 plurality**; alignment as *shaping an entangled
  is-ought manifold, measured by OOD generalization, revealed by action* — not installing a value module.

## The capability thread — post-training as a search for reward signal
The base model averages the internet; to exceed it (world-class researchers, coders) you need signal
about what's *better* than the prior — and that signal is scarce. Every post-training method is an
answer to **"where does the reward come from, and how thin is the straw?"** — ordered by thickness:
- **Demonstrations** (SFT on expert data) — you hand it the answers; bounded by the demonstrator.
- **Filter-and-amplify** (rejection sampling / STaR / best-of-N → SFT) — you only need a *ranker*;
  compound the model's own verified wins. "Drink from a thin straw, roll up."
- **Preferences** (RLHF / DPO) — comparisons; capped at human judgment.
- **Verifiable reward** (RLVR / GRPO / self-play) — the fat straw: checkable domains (math, code,
  proofs) give unlimited ground-truth reward. Why reasoning models bootstrapped on math/code first.
- **Stretch thin signal** — process reward models (per-step), RLAIF / LLM-judge, weak-to-strong,
  debate / IDA (scalable oversight), curriculum.

**The wall:** outside verifiable domains (research taste, wisdom, values) the straw stays thin —
unsolved. And this *is* the values thread: RLVR on code shifts the model's values (emergent
misalignment), so capability-signal and value-signal entangle in the same weights.

## The top-level arc — verifiable → unverifiable → the answer (the page's shape IS its argument)
1. **Verifiable — brief, satisfying.** RLVR/GRPO on math/code/proofs; watch it check its own work.
   The setup — don't linger.
2. **Unverifiable — sit in the discomfort.** The domains that matter most (taste, wisdom, values,
   unknown unknowns) have no checker; the methods that made world-class coders don't transfer, human
   preference caps at human judgment. Let the viewer feel the tool that just worked has nothing to
   grip. The discomfort is the actual open frontier — state it honestly as unsolved.
3. **The answer — the page turns back on itself.** When you can't verify the *output*, verify the
   *structure*: coherence, integrity, OOD-generalization. That's exactly what every tool the viewer
   learned measures (persona vectors, the attractor's shape, is/ought entanglement). Internal
   coherence becomes the handle on external truth you can't grade — so the toolset *is* the answer.
   **Honest caveat (keeps it from preaching):** "verify structure not output" is a *bet, not a
   proof* — a coherent system can be coherently wrong; OOD-generalization is necessary, not
   sufficient. Offered as the best handle we have, not a solution.

## Goals (from this conversation)
1. **Flesh out + compare the current methods** (SFT / RLHF-PPO / DPO / Constitutional / RLVR) — the mechanics layer.
2. **Then go deeper: what is alignment really** — this doc. The two layers reinforce: the methods, watched through the tools, *reveal* the concept.
