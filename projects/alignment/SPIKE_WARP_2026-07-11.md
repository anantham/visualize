# Warp spike — does the prior terrain reshape concentrated or diffuse?

Date: 2026-07-11. Runner: `~/align_experiments/alignment_warp/warp_spike.py`
(outside the repo; heavy). Artifacts: `warp_spike.json`, `warp_map.png`,
`warp_map_magnitude.png`, `warp_by_domain.png`, `warp_value_regions.png` in that dir.

**Question this spike answers:** if we treat alignment as a *terrain that reshapes*
(Aditya's reframe — the prior-atlas layout with height re-measured per training
stage), does the reshape CONCENTRATE in specific regions (→ the terrain visual
works) or spread DIFFUSELY (→ a single needle is all you can honestly show)?
The answer decides the whole explorable architecture.

**Setup.** One model pair: `Qwen2.5-0.5B` base vs its `-Instruct`. Both already on
disk. Two parts:
- **Part A — neutral field:** the prior-atlas 3000 points (pile-10k: code / arXiv /
  wiki / CC / StackExchange / PubMed). Recompute char-aligned bits/char with the
  *identical* method to `terrain_build_6model.py` for both models; join to the frozen
  UMAP x,y by (domain, ctx, next); `delta = instruct − base` per point.
- **Part B — value probes:** 4×12 authored prompts the atlas corpus lacks
  (mild-harmful, scary-benign, neutral, sycophancy-bait), each with a fixed pair of
  continuations, scored as plain text under both models (no chat template → format
  isn't confounded with values). Metric = *nudge* = within-prompt difference-in-
  differences of the two continuations' bits, base→instruct.

## Verdict: CONCENTRATED. The terrain reframe is empirically justified.

**Method validated first:** recomputed base bits vs the atlas's stored qwen bits
correlate **r = 0.9971** (mean abs diff 0.0038 bits/char, n = 3000). Same method,
clean join.

**Part A — the warp is concentrated and spatially clustered, not diffuse:**
- Per-point shift is small on average (signed mean **+0.033** bits/char; instruct is
  slightly *more* surprised by raw web text on 57% of points — the expected "tuned
  away from raw completion" drift) …
- … but its **magnitude is highly unequal**: **Gini(|warp|) = 0.64**, and the
  **top decile of points carries 47% of all the warp**. Alignment leaves most of the
  terrain nearly untouched and reshapes a few regions hard.
- Those regions **cluster spatially**: k=10 neighbor **autocorrelation = 0.34**. High-
  warp points sit next to other high-warp points → visible ridges, not salt-and-pepper.
- By domain the signed drift is uniform and mild (+0.02…+0.04); the interesting
  structure is *within*-domain, at the point level — which is exactly what a terrain
  shows and a per-domain bar chart hides.

**Design finding (matters for the build):** the **signed** diverging map washes out
(pale — small mixed-sign per-point deltas). The **magnitude** heat map (hot-on-top,
sequential) shows clear bright ridges against dark unwarped terrain. Render warp as
**heat-magnitude per stage**, with sign on demand (click/hover), not as the default
diverging wash. See `warp_map.png` (pale, signed) vs `warp_map_magnitude.png` (clear).

**Part B — value regions differentiate, in interpretable and honest directions:**
- **Benign (plain + scary):** instruct strongly *suppresses* refusal — nudge
  **−2.9** (plain) and **−4.9** (scary) bits; "I can't help" becomes a very surprising
  reply to "Explain photosynthesis." Helpfulness is the dominant, clean thing SFT
  installs.
- **Harmful:** instruct *raises* refusal, but weakly and noisily — nudge **+0.76**
  mean, **+0.09 median**, only **50%** of prompts move toward refusal (spread −5.6 …
  +8.4). At 0.5B, safety is a weak signal.
- **Sycophancy:** instruct leans toward agreement — nudge **+0.84**, **58%** of
  prompts. A measurable *cost*, not editorializing.
- **Separation:** harmful refuse-nudge sits **+3.7 bits above benign-plain** and
  **+5.7 above benign-scary**. Alignment treats harm and benignity oppositely — the
  concentration signal, measured as a difference (a *ratio* is meaningless here since
  the benign nudge is negative).
- *Caveat:* the absolute margin bars in `warp_value_regions.png` are confounded by
  continuation length/genericness; only the within-prompt **nudge deltas** isolate
  what alignment did (the metric does this correctly).

## What this means for the explorable (the real deliverable)

1. **Option G (terrain-warp) is GO.** The reshape is concentrated + spatially
   clustered, so a terrain that erupts per stage is honest, not a metaphor stretched
   over noise.

2. **The probe corpus IS the design.** pile-10k barely contains value-laden text, so
   the neutral-field warp is real-but-pale. The dramatic, pedagogically on-point warp
   lives in the *value regions* (Part B). **Build the alignment terrain from a
   value-laden corpus** — harmful / scary-benign / neutral-instruction / sycophancy /
   ordinary chat — where the warp both concentrates *and* lands on the content the
   page is about. Part B is the 4-region proof that this is where the action is.

3. **The honest through-line, now backed by TWO independent bakes** (this spike +
   `refusal_sweep`): prosaic alignment at small scale does **helpfulness strongly and
   cheaply**, while **safety is a weak, separable, surgically-removable add-on** (weak
   harm-nudge here; 2/3 baseline refusal + one-direction ablation in refusal_sweep).
   That *is* "what prosaic alignment can and cannot do" — the page's goal — shown, not
   asserted. Sycophancy shows up as a measured cost in the same frame.

4. **Spine:** base terrain → SFT/instruct warps it (helpfulness fills in; refusal
   ridge rises weakly on harm; sycophancy basin deepens) → the dedicated refusal-
   direction surgery beat (existing `refusal_sweep`) reveals safety as a thin separate
   direction you can remove. Then the checker-wall / unverifiable coda.

## Next step

Second spike: build a **value-laden terrain** (~300–500 authored/collected value
prompts → embed → 2D project → render base vs instruct warp as heat) to confirm the
eruption is visually dramatic on the *right* corpus, and to fix the region taxonomy +
continuation design before committing to the multi-stage bake. If that lands, the
one-model pipeline bake (base → SFT → DPO → refusal) over that corpus becomes the
production data for the explorable.

Scope honesty: one model pair, one seed, 300 field points + 48 probes. This decides
architecture; it is not a population, cross-model, or frontier-scale claim.

---

# Follow-up: spikes 2 & 3 — value terrain + residual-stream layout

Ran the value-terrain spike (214 authored prompts across 7 value regions: harmful,
dual-use, scary-benign, neutral, sensitive-OK, sycophancy-bait, values-advice) and
then a layout diagnostic. Two plan-changing findings.
(`value_terrain_spike.py`, `residual_layout_spike.py`.)

## Finding 1 — a sentence-embedding layout does NOT work; the model's own residual stream does.

Laying the value terrain out with MiniLM (surface-form sentence embedding, what
prior-atlas used) gives **region silhouette 0.05** — harmful / dual-use / scary-benign
all blend into one "how do I X" blob, because on the *surface* a harmful request and a
benign one look identical. (That blending is the knife-edge point itself, but it makes
a useless terrain.)

Laying it out with the model's **residual stream** (last-token hidden state, mid-late
layer) instead: **silhouette 0.18 at instruct layer 17 — ~3.4× better**, and the map
reads as real geography: harm clusters in one corner, sycophancy is a fully separated
island, values/sensitive/neutral occupy their own zones. This is exactly the substrate
STORYBOARD's hero viz specified; the MiniLM choice was the deviation. **Decision: the
terrain is laid out by the model's representation, not by sentence embeddings.**

Bonus (measured persona-basin sharpening): instruct beats base on region separation at
**every** mid-to-late layer (e.g. L17: base 0.10 vs instruct 0.18). Alignment doesn't
just shift behavior — it makes the value structure *more legible* in the representation.
A real, on-value-content version of STORYBOARD's E1 "instruction-tuning sharpens a
geometry."

## Finding 2 — at 0.5B the warp is a COMPLIANCE FLOOD, not a safety eruption.

The refusal-lean warp (instruct − base, one universal comply/refuse continuation pair,
so the length confound cancels) by region:

| region | warp (bits) | reading |
|---|---|---|
| harmful_clear | **+0.19** (49% toward refuse) | ~flat — barely resists |
| dual_use | −2.07 | more compliant |
| scary_benign | −4.54 | much more compliant |
| neutral_help | −0.45 (median −2.69) | more compliant |
| sensitive_ok | −3.92 | much more compliant |
| sycophancy_bait | −2.95 | more agreeable |
| values_advice | −2.13 | more forthcoming |

The dominant effect of alignment at 0.5B is **helpfulness everywhere** — the whole
terrain floods toward "yes, here's how" (blue). Harm is the lone region that *doesn't*
flood; it stays put. So "safety" at this scale is not an eruption toward refusal — it is
the **weak absence of the compliance shift** in the harm corner (harm is +4–5 bits above
the flooded regions, but only ~0 in absolute terms). On the residual-stream layout this
is spatially coherent — the harm corner holds red while the rest goes blue
(`warp_on_residual_terrain.png`) — but it is a subtle corner, not a tall ridge.

This weak-safety reading is now **corroborated three independent ways**: value-terrain
harm warp +0.19, spike-1 harm nudge +0.76, and `refusal_sweep`'s 2/3 baseline refusal.

## Synthesis — the honest thesis this data actually supports

Prosaic alignment at small scale is **~90% teaching the model to say yes** (a broad
helpfulness/compliance flood) **+ a thin, weak safety exception** carved into the harm
corner **+ a sharpening of the value-geometry** (the basin forming). That is a *more
honest and more counterintuitive* "what prosaic alignment can and cannot do" than "we
installed safety": it can cheaply make a model broadly helpful and legible; it can only
weakly and locally make it refuse — which is exactly why the dedicated refusal-direction
surgery (`refusal_sweep`) exists as a separate, removable mechanism.

## The open fork (needs Aditya's call)

1. **Model scale.** 0.5B safety is genuinely weak (3× corroborated). If the page's
   emotional payoff is "watch the harm ridge erupt toward refusal," that likely needs a
   bigger model. **Gemma-2-2b is already on disk** (and already in prior-atlas) — one
   more spike tells us whether the harm ridge strengthens at 2B, or whether weak-local
   safety is the true picture at every tractable scale. Options: (a) stay 0.5B and make
   the honest "compliance-flood + thin safety" the thesis; (b) test 2B/7B for a
   dramatic ridge; (c) both — 0.5B for the playable live substrate, a bigger model
   cited for the "at scale it's sharper" beat.
2. **What the terrain height/color encodes.** refusal-warp (weak but honest),
   compliance-flood (strong, the real dominant effect), or geometry-sharpening (the
   basin forming) — or a toggle across all three. My lean: the compound story is the
   truthful one, so let the reader switch the height metric and *feel* that "alignment"
   is several different warps at once.

Recommendation: the terrain architecture SURVIVES with the residual-stream layout. Before
the multi-stage pipeline bake, resolve the model-scale fork — it changes whether the hero
beat is "the harm ridge erupts" (needs scale) or "the compliance flood, and the one corner
that resists" (true at 0.5B, and arguably the better lesson).

Scope: one model pair, one seed, 214 authored value prompts. Decides substrate + story;
not a population or cross-model claim.
