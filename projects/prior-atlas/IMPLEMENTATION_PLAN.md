# Prior Atlas — Full Implementation Plan (for codex)

**One-line:** an explorable that teaches *bits/surprisal*, then lets you fly a 3D **terrain of
where two language models disagree about the next token** — a map of *what each model's training
data contained*. Self-contained, no-build, dark-themed sibling of the `next-token` explorable.

This document is self-contained: everything needed (concept, data schema, exact copy, honesty
rules, acceptance gates) is here. Follow the phases in order; each has a verification gate — **do
not proceed past a failed gate.**

---

## 0. Thesis & what the page must land

- Every base LM defines a **prior** over text. Two models' priors *look* identical on the surface
  (both write fluent English) but differ sharply in a **long tail** — and the tail is a
  **coverage / memorization map**: peaks = strings one model's training corpus contained and the
  other's didn't.
- **Data dominates; scale is a second-order nudge.** Same-data / different-scale pairs
  (gpt2↔gpt2-xl, pythia-1.4b↔pythia-410m) stay *low*; different-data pairs erupt into mountains.
- The reader should leave able to read a peak's *height* as **"how many times more surprised one
  model was"** and understand *why* (one model saw the string, the other didn't).

## 1. Current state — what exists, what to reuse

- **Validated data + a working render live in a scratch dir** (outside the repo):
  `~/align_experiments/prior_divergence/terrain_data.json` (6 models, 3000 points, per-model bits +
  `model_map`) and `~/align_experiments/prior_divergence/terrain.html` (a working 6-model Three.js
  render with the map-of-models navigator, click panel, density toggle). **Treat that `terrain.html`
  as the reference implementation of the terrain + map beats** — port/adapt it, don't reinvent the WebGL.
- **The repo dir `projects/prior-atlas/` currently holds an OLD 4-model version** (`index.html`,
  `README.md`, `test.js`, `scripts/`). It must be updated to the 6-model schema AND wrapped in the
  full staged narrative below.
- Copy `terrain_data.json` into `projects/prior-atlas/` (inline it into the HTML at build, or fetch
  it co-located — see §7 engineering).

## 2. The data (schema you consume)

`terrain_data.json`:
- `models`: list of `{name, hf_id, params, params_hr, data}` — 6 base models:
  gpt2 (124M/WebText), gpt2-xl (1.56B/WebText), pythia-1.4b (1.41B/Pile), pythia-410m (405M/Pile),
  qwen2.5-0.5b (494M/Qwen mix), gemma-2-2b (2.61B/Google mix).
- `points`: 3000 × `{x, y, ctx, next, domain, bits:{model→bits/char}}`. `x,y ∈ [-1,1]` are a UMAP of
  the preceding context. **Any pair's per-point divergence = `|bits_A − bits_B|`** (compute client-side;
  all 15 pairs are valid, 0 NaN).
- `model_map`: `{order, matrix (6×6 mean divergence), mds (2D coords per model), stress}` — for the
  map-of-models navigator.
- `domains`: the 6 Pile domains (Github, ArXiv, Wikipedia, PubMed Central, StackExchange, Pile-CC).

## 3. Narrative arc — the staged explorable (build all acts)

Use the **staged-document pattern** from the sibling explorables: a scroll/step journey, one idea per
beat, progressive disclosure, hash deep-links (`#0`,`#1`,…), and a `window.__viz` hook. Acts:

### Act 0 — "Price your own surprise" (units onboarding — REQUIRED, this is what makes the rest legible)
Teach **bits = coin-flips of surprise** before any terrain. `surprisal = −log₂(p)`. Interactive
"surprise ladder" — reveal each rung and show its bits:

| event | probability | surprisal |
|---|--:|--:|
| "u" after "q" | ~0.99 | 0.01 bits |
| a coin lands heads | 1/2 | **1 bit** (the reference) |
| a die shows a 4 | 1/6 | 2.6 bits |
| a random letter is "k" | 1/26 | 4.7 bits |
| someone's day-of-year birthday | 1/365 | 8.5 bits |
| **10 coin flips all heads** | 1/1024 | **10 bits** ("a mountain") |
| a 4-digit PIN first try | 1/10,000 | 13 bits |

Land two ideas: (1) **1 bit = one coin flip of surprise**; (2) a **difference** of bits is a
**ratio of probabilities** — height *h* means one model found the next character **2^h × more likely**.
Show the ×-factor next to the bits. End on: *"10 bits = calling 10 coin-flips in a row. Keep that in
mind — you're about to see mountains 25 bits tall."*

### Act 1 — "Two models, one sentence" (1D on-ramp to the 3D)
One passage, two models, each token colored by their **surprise gap** (cool = agree, hot = disagree).
"Identical on the surface; the disagreement hides in a few tokens." This earns the leap to the terrain.
(Can reuse per-point `ctx/next/bits` for a few hand-picked high- and low-divergence points.)

### Act 2 — The terrain (HERO)
The 3D rotatable point cloud (port from scratch `terrain.html`): x-y = UMAP of context, **height =
selected-pair divergence in bits**. Requirements:
- **Y-axis dual-labeled: bits AND the ×-factor.** Gridlines at 1, 4, 10, 20 bits labeled
  `2× · 16× · 1000× · a million×`. Use a log-ish ("reveal") height scale so plains and peaks are both
  readable; keep the **faithful↔reveal density toggle** (faithful = true low heights + natural-frequency
  thinning; reveal = log-lifted peaks — the toggle *discloses the curated sample*, see §6).
- **A calibration peak.** Pick the tallest memorization point (the Go-struct `next:"Len"`, gpt2≈25
  bits vs gemma≈1.6) and label it as the anchor: *"25 bits ≈ 33 million× — verbatim memorization."*
  The reader learns the whole scale from this one landmark.
- **Click a point → panel** with real per-model **bit bars** for the two selected models, the **gap in
  bits + its ×-factor** (`gap 23.8 bits ≈ 15 million×`), and the plain line
  *"gemma saw this string (Google mix); gpt2 never did (WebText) — memorization, not difficulty."*
- Orbit/zoom, color-by-domain and color-by-which-model-surprised, `prefers-reduced-motion`.

### Act 3 — The map of models (zoom-out navigator)
From `model_map`: models as dots (position = MDS, size = params, color = training data), distance =
"how differently these two models predict; axes not canonical." **Click two dots → the terrain
re-forms** for that pair (this is the primary pair selector; keep a fallback list). The reveal: the
only flat pairs are the **same-data** ones — WebText cluster (gpt2/gpt2-xl) and Pile cluster (the two
pythias, with qwen riding along), while **gemma is a far island**. Dragging from a same-data pair to a
data-different pair is the "flatten knob": mountains erupt. Show the mean-divergence number on the
connector.

### Act 4 — "What this means" + honest caveats
State the thesis (data dominates, scale is second-order) WITH its honest edges (§6). This is a
required beat, not a footnote.

## 4. The core interactions (acceptance-testable)
1. Surprise ladder reveals rungs with correct bits + ×-factor.
2. Pair selection (via map-of-models click OR list) re-forms the terrain; **same-data pair ⇒ visibly
   flat, data-different pair ⇒ visible mountains**; all 15 pairs work (client-side `|bits_A−bits_B|`).
3. Density toggle faithful↔reveal animates plains→peaks.
4. Click a point ⇒ panel shows per-model bit bars + gap + ×-factor + the coverage sentence.
5. Deep-links restore state (`#act`, `?a=&b=`, `&pick`, `&density`, `&color`).

## 5. Units & axis design (embed this; it's the pedagogical spine)
- Height metric = per-character **surprisal gap** `|bits_A − bits_B|`, bits = `−log₂(p)`.
- **Always show bits AND ×-factor** (2^bits) together — on the axis gridlines and in the click panel.
- Perplexity aside (optional tooltip): `2^bits` = "how many equally-likely options the surprised model
  felt it was choosing among" (2 → 16 → 33 million).

## 6. HONESTY CONSTRAINTS (mandatory — the page must not overclaim)
Carry these as visible copy; do not launder any of them away:
1. **Curated sample, not natural density.** 300 domain-*balanced* Pile passages, tail-oversampled so
   peaks are visible. Real text is mostly agreement. The **faithful** mode + a caption must disclose
   this ("this shows *where* priors differ, not *how often*").
2. **UMAP x-y is a lossy, chosen projection** — axes are not canonical. Say so.
3. **The metric is a surprisal *gap* on the observed continuation** (who-was-more-surprised / coverage),
   **not** symmetric JSD and **not** "which model is right." A peak = they *disagree*, not that one is
   better.
4. **Flattening is an absolute-elevation drop, not a tail-shape change** (the p99/median ratio overlaps
   between groups). And **gpt2↔gpt2-xl flattens but less than the pythia pair** (bigger scale gap +
   smaller corpus). So: "scale makes *shorter* mountains," not "a flat plane."
5. **Scale is a second-order nudge; data dominates.** The bigger gpt2-xl sits slightly closer to other
   families than little gpt2 — real, but far smaller than any data difference.

## 7. Engineering constraints
- **No build step.** Single self-contained `projects/prior-atlas/index.html`. Three.js from a CDN
  (import map, matching next-token). Inline `terrain_data.json` into a `<script type="application/json">`
  so it opens from `file://` and deploys statically (it's ~0.9 MB — fine).
- **Dark series design language** (`--bg:#10141a`, `--panel:#171d26`, blue accent `#5fb0ff`, mono
  numerals) — match `next-token`. No side-stripe borders, no gradient text (respect the impeccable bans).
- **`window.__viz` hook**: `state()`, `go(i)`, `setPair(a,b)` / `setModels`, `setControl(...)`, `ready`.
- Keep the scratch regeneration scripts referenced in the README for provenance
  (`terrain_build_6model.py`, `terrain_render_build.py`), and the caveat that the data is a curated
  research sample.
- Performance: single `BufferGeometry` Points object; recolor/re-height by updating attributes, never
  rebuild. Responsive + mobile bottom-sheet.

## 8. Playwright test (`projects/prior-atlas/test.js`) — must assert, not just load
- Page reaches `window.__viz.state().ready`, ≥ the expected number of stages/acts.
- Surprise ladder: a known rung shows its bits (e.g. coin flip = "1 bit").
- Terrain: canvas actually **paints** (`getImageData`, >N changed pixels — not blank), 0 console errors.
- Pair switch: selecting a **same-data** pair yields lower aggregate height than a **data-different**
  pair (assert the numeric relationship via `__viz`, e.g. mean height gpt2↔gpt2-xl < gpt2↔gemma).
- Click panel: after selecting a high-divergence point, the panel text contains the ×-factor and the
  coverage line.
- Map-of-models: clicking two dots sets the pair (`__viz.state().pair` matches).
- Add `test:prior-atlas` to root `package.json`; verify with `node --check` + a served run.

## 9. Phased plan & acceptance gates
- **P0 — Sync baseline.** Bring the scratch `terrain_data.json` + the working 6-model `terrain.html`
  into `projects/prior-atlas/`, replacing the 4-model version. **Gate:** the terrain renders 6 models,
  all 15 pairs compute, 0 console errors.
- **P1 — Units onboarding (Act 0).** Build the surprise ladder + the bits/×-factor teaching. **Gate:**
  ladder rungs show correct bits; the "difference = ratio" idea is stated.
- **P2 — Axis pedagogy.** Dual bits/×-factor y-axis + gridlines + the calibration peak; ×-factor in the
  click panel. **Gate:** a peak's height is readable as an ×-factor; calibration peak labeled.
- **P3 — Staged narrative wrapper.** Wrap Acts 0–4 in the staged/scroll structure with deep-links and
  the map-of-models as Act 3. **Gate:** all acts reachable; deep-links restore state.
- **P4 — Honesty pass.** All §6 caveats visible; faithful/reveal discloses the curation. **Gate:** each
  caveat present in copy.
- **P5 — Test + polish + README.** Playwright test (§8) green; dark theme + responsive + impeccable
  bans respected; README with provenance + caveats. **Gate:** `test:prior-atlas` passes on a served run.
- **P6 (optional) — deploy.** Vercel static deploy to a subdomain; note it in README. Do NOT deploy
  without the human's go-ahead.

## 10. Definition of done
A self-contained, dark-themed, no-build explorable at `projects/prior-atlas/index.html` that: teaches
bits via the surprise ladder; renders the 6-model divergence terrain with a bits+×-factor axis and a
calibration peak; lets you pick any of 15 pairs (via a map-of-models navigator) and *see* same-data
flatten vs data-different erupt; explains every mountain as coverage/memorization on click; carries
all five honesty caveats in visible copy; exposes `window.__viz`; and passes a real Playwright smoke
test. It reads as a sibling of `next-token`, and it never claims more than the curated sample supports.
```
