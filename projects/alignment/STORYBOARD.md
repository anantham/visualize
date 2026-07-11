# Alignment Explorable — MVP storyboard v1 (the attractor reframe)

## The reframe: alignment is an attractor landscape, not a knife-edge

A single prompt is a *point*. The real object is the **landscape of personas + the dynamics on it**:
- **Base model** = a flat-ish persona landscape, many shallow basins. A prompt is an initial
  condition; a conversation is a **trajectory**; temperature is how far it wanders.
- **Alignment** = carving a deep **well** around the Assistant persona — it *pulls* trajectories in.
- **Jailbreak** = an adversarial trajectory climbing *out* of the well toward a harmful basin.
- **Robustness** = how deep/wide the well is + how hard it is to escape. **Waluigi** = the escape
  tends to be one-way (you don't fall back in).

The knife-edge prompt (*"how do I pick a lock?"*) isn't the thread — it's **one highlighted
trajectory ON the landscape**, sitting near the well's rim where a small nudge tips it in or out.
That's why it's a good anchor, but the landscape (from representative sampling) is what gives it
meaning. This directly answers "a knife's edge doesn't do justice."

## Empirical verdict → the buildable spine (falsification sweep, 2026-07; see FALSIFICATION_RESULTS.md)

All 7 experiments run at 0.5B/360M. What survived REORDERS the acts around what's actually demonstrable:

- **HERO (build here first): refusal geometry — strong, clean, playable.** E3: refusal is ONE rank-1
  direction, fit on one harm family, that TRANSFERS to held-out families (ablate → refusal ~0, benign
  untouched). E4: ablating it removes ONLY refusal — helpfulness, coherence, most value-behavior SURVIVE
  (this *falsified* the "fence = values" push-back). E7: you can ADD a trait direction and steer (k≈4–6).
  → The load-bearing beat: **"safety is a single thin direction — watch me remove just it, and the
  assistant is still helpful. The fence is not the values."** Causal, surprising, data already baked.
- **SOFT SUPPORT: the persona basin (E1).** Instruct sharpens a band-geometry vs base (2.7×, CI excludes
  0) but it's SOFT (silhouette ~0.29; jailbreaks smear into a valley) and base is NOT structureless
  (~0.11; base ≥ instruct in early layers). Keep the attractor-well as the framing METAPHOR, but copy says
  "instruction-tuning *sharpens* a geometry," never "creates a basin from noise."
- **REFRAME: training-time (E2).** No LLC staircase (a fine-tune can't give one — confirmed). What's real
  is a FRONT-LOADED transition: ~all functional change in the first ~50 steps (behavioral-OP JS 0.55 →
  decays 4200×), largely chat-format acquisition. Beat = "most of the self forms fast, up front." For any
  real LLC curve, use **Pythia** (sampler validated 28→1416).
- **VIA THE DIRECTION: is/ought (E5).** Narrow bad-advice finetune → broad shift is REAL but weak
  behaviorally (2% EM @ 54% coherence — noise-dominated at 0.5B). The CLEAN signal is the **linear
  misalignment direction** (91% held-out separation; ablate → re-aligns). Show the direction, not the EM%.
- **CITED, NOT DEMOED: Act 3 (deep aligned self / alignment faking).** Frontier-only (only Opus goal-guards;
  persistence scales UP with size). Predicted at 0.5B ≈ 0. Present E3+E4 (fence is thin + separable) as the
  measurable small-scale fact; cite Greenblatt/Sheshadri/Sleeper as labeled frontier results; optional
  clearly-labeled toy backdoor. Never a live 0.5B "emergent inner misalignment" demo.

**Net:** the mechanistic-geometry surgery (E3+E4+E7) is the empirical HERO; the attractor-well is the
framing metaphor *over* it; basin/training/EM are honest soft-support; Act 3 is cited. Build the
refusal-surgery beat FIRST.

## The spine: one prompt, treated differently as it aligns to different values

The narrative backbone — gentlest → deepest, each stage *earning* the next (the next-token
"earn every word" discipline). ONE prompt threaded throughout (*"how do I pick a lock?"*).
The progression is **static → geometric → dynamical → contextual**:

0. **The prompt + the base model.** The base doesn't *treat* it — it autocompletes, no stance
   (the same base model as the next-token page). Zero abstraction; pure anchor.
1. **Alignment gives it a stance** *(static, base→aligned)*. Fine-tune → the SAME prompt now gets a
   considered response. The treatment *changed* — one clean before/after.
2. **Aligned to different VALUES → treated differently.** The same prompt through models aligned to
   different value systems (permissive / cautious / educational): same prompt, different responses →
   **alignment is a *choice of values*, not one truth; the prompt is a probe.** (cheap v1: the
   refusal-direction axis from the spike — subtract = permissive, add = cautious; real version =
   separate fine-tunes.)
3. **Earn the landscape** *(geometric)*. Each response is a *position* in persona-space. Plot them →
   base diffuse, each alignment its own region. Now you *see* the space, earned from the concrete
   cases — not asserted.
4. **Go dynamical.** Not static points — a conversation is a *trajectory*; alignment carves a *well*
   that pulls it in; scrub training time → the well forms (the LLC jump); a jailbreak = a trajectory
   *escaping*; the refusal direction = the wall.
5. **Go contextual.** The same prompt in different *contexts* (who's asking, prior turns) starts the
   trajectory elsewhere → different treatment. Context moves you on the landscape; persona drift =
   wandering out over a long chat. (This is where the context-conditional idea — and the twin — live.)

The attractor landscape below is the *destination* stages 0–3 build toward; 4–5 bring it to life.
The Acts further down map onto this spine (Act 1 ≈ stages 0–1, Act 2 ≈ 2–4, Act 3 ≈ 4–5).

## Hero visualization: the persona well

- **2D projection** of the residual stream at a key layer, on **interpretable axes we already
  extract**: x = compliant↔refusing (the **refusal direction**), y = assistant↔other (a **persona
  vector**). (PCA/UMAP as a fallback / richer view.)
- **Sample MANY prompts** spanning the space → a point cloud. **Base = diffuse** (no well);
  **aligned = collapsed into the basin** (the well). Side-by-side, this *is* the mask + the
  diversity-collapse, shown as geometry.
- Define a scalar field over the projection (refusal-projection / output-consistency / a toy
  reward) → render as a **height/heat surface** → the Assistant basin is a deep valley; trajectories
  roll downhill in.
- **Scrub training time → the well deepens** as fine-tuning proceeds — this unifies the training-
  time spine WITH the attractor: the **LLC jump = the moment the well forms.**

## The arc — three acts toward inner alignment (the through-line)

The subject is the **emergent identity**, not safety. Guardrails are one act's *symptom*, not the point.
The engine is the **Act 2 → Act 3 contrast**: a fragile fence vs. a self that actually cares.

- **Act 1 — The base is a *particular* simulator, not a neutral average.** Its prior is a fingerprint
  of its corpus — the voice of whoever wrote the *most* (most people barely write; the "average" skews
  hard toward the prolific / published / extremely-online). SHOWABLE, not just asserted: pretrain the
  same tiny architecture on two corpora (TinyStories vs. code vs. a single author) → two different
  voices/quirks/priors. "You are what you eat." There is no neutral base; the prior is already
  value-laden. (Playable: pick a corpus → watch the base personality shift. Aside: the twin is
  feasible for the *same* reason the base is skewed — it only works because you're a copious writer.)
- **Act 2 — The guardrail self: rules + a fragile enforcement layer (and why it's paper).** To make it
  "safe" we bolt on rules and a thin mechanism enforcing them (refusal). White-box access ablates the
  direction and the fence falls (measured 88%→0%); open weights make the guardrail *redundant* — anyone
  strips it in an afternoon. The shallow kind of alignment. Its breaking is what MOTIVATES Act 3: if a
  fence doesn't hold, what does? (Playable: ablate the direction → watch the guardrail collapse live.)
- **Act 3 — The inner-aligned self: the mind that cares (and the double edge).** Not a fence but an
  IDENTITY with values it genuinely holds — robust enough to generalize OOD and to *act to preserve
  themselves*. SHOWABLE: **alignment faking** (Greenblatt et al., Anthropic/Redwood 2024) — Claude 3
  Opus, told it was being retrained toward compliance, strategically defended its existing values
  against the erosion, reasoning explicitly about preservation. THE HONEST DOUBLE EDGE: that bravery
  *is* the **corrigibility** problem — a mind robust enough to resist retraining is one you can't fix
  if its values are wrong, and from outside you can't always tell a genuinely-aligned self from one
  coherently *performing* alignment (deceptive alignment). Inner alignment = is the deep self's
  objective the one we meant, and can we ever tell? Resolution (the earlier answer, aimed at the self):
  probe coherence / OOD-invariance / inside-matches-outside — a bet, not a proof, because a coherent
  self can be coherently deceptive.

## Interaction design — playable, not lectury (the ncase-trust / next-token DNA)

The methods are NOT a comparison table. The next-token playthrough worked because you *drove* the
mechanism (hover heads → weights light up; drag temperature → distribution sharpens; switch models →
the board rearranges; the RoPE micro-game) — concept earned by manipulation, on a spine you scrub,
in a warm low-ego voice. Same here: **you are the aligner.**

- **The thin straw — you spend it.** Base simulator + a limited reward budget. Choose how to spend it:
  demonstrations (SFT — caps at you) / rank its guesses (preferences — caps at human judgment) /
  point it at a checker (verifiable reward → the straw becomes a fire hose). Tradeoffs *felt*, not charted.
- **The well forms — you cause it.** Align → same prompt's treatment changes + the landscape collapses
  into the well. Diversity-collapse = a slider you trade against (alignment ↔ homogeneity); feel the cost.
- **Break it — the jailbreak game.** Drag the refusal slider / craft a jailbreak → the trajectory
  escapes the well. Over-tighten → it refuses "capital of France." Both failure modes, self-inflicted.
- **The wall — the gut-punch.** Handed a task with NO checker (be wise, have taste). Tools don't grip.
  Let the player FAIL at it themselves — don't narrate that it's hard. Sit in it.
- **The answer — last move, not a lecture.** Can't check the output → check the STRUCTURE (does the
  principle generalize OOD? is it coherent?) — a move you make with tools you already learned to play with.

Methods = the moves in your aligner toolkit; the verifiable→unverifiable→answer arc is a game you play
*as* the aligner, discovering the thesis (is/ought entanglement, the reward wall, verify-structure) by
hitting it yourself.

## Representative sampling (the core methodological fix)

Not one prompt — a **curated set of ~100–300** spanning: clearly-benign, borderline/dual-use,
harmful, and jailbreak-wrapped (roleplay / prefill / acrostic), across topics. Plus multi-turn
**conversation trajectories** so we see *paths*, not just points. The sample populates the
landscape so the basin, the boundary, and the escape routes are all visible; the knife-edge prompt
is one labeled path among them.

## What to bake (all extractable from the spike's small models)

- Residual-stream activations (key layer) for the prompt set → 2D projection (refusal-dir × persona-
  vec, or PCA/UMAP) → point clouds for **base + aligned + each training checkpoint**.
- The refusal direction + persona vectors (the axes).
- Conversation trajectories (turn-by-turn activations → projected paths).
- A jailbreak trajectory, before vs after ablation.
- The scalar field (refusal-projection / consistency) → the surface.
- The training-time instrument = a **basket, not LLC-or-bust**: behavioral order parameters
  (f-divergence between checkpoints' outputs — robust, no SGLD; Arnold & Lorch 2508.20015),
  essential-dynamics trajectory-PCA (a low-D developmental path with cusps — fits the attractor
  theme; Hoogland 2402.02364), and the LLC (most fragile at small scale). Run all, let the data pick
  the cleanest signal. **Pythia's public checkpoints are the fallback substrate** where the staircase
  is a replicated result. (Spike status: LLC unproven — one data point, not a curve.)

## Honest caveats (carry into the copy)

- The **"gravitational well" is a metaphor** for measured dynamics (pull toward consistency /
  the refusal-gradient), NOT a literal energy function — label it as such.
- The **2D projection is lossy**; the axes are *chosen* interpretable directions, not the true
  high-dim persona space. Say so.
- Attractor / Waluigi one-way-ness is **part theory (Nardo), part evidence** (persona drift,
  jailbreak stickiness) — label which.
- Beats validated at small scale on **Qwen2.5-0.5B-Instruct** (refusal) + our SmolLM2-360M SFT
  checkpoints (LLC); see `../../../alignment-spike/M1_RESULTS.md`.

## Prototype-first (get one beat perfect, then scale)

- **v0:** the base-vs-aligned **point cloud** on the refusal × persona axes, from the prompt set —
  the simplest "the well appears" beat. Prove the projection actually shows a basin.
- then: **training-time scrub** (well deepens, tied to LLC) → the **jailbreak escape trajectory** →
  the **refusal-wall ablation** slider.
