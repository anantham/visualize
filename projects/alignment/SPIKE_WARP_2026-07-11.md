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
