# Prior Atlas - maps of model priors

A five-act explorable about how base language models carry different priors over
text. It starts by teaching bits as coin-flips of surprise, then turns a
six-model prior-divergence bake into a 3D terrain of where two models disagree
about the observed next token.

## Acts

0. **Price your own surprise** - surprise ladder: coin flip = 1 bit, 10 heads =
   10 bits, and a height gap of `h` bits means `2^h` times more likely.
1. **Two models, one sentence** - a 1D heat strip showing that a few next tokens
   carry most of the disagreement.
2. **The terrain** - 3,000 points, height = per-character surprisal gap, with a
   bits plus x-factor axis and the Go `Len` calibration peak.
3. **The map of models** - MDS navigator; click two model dots and the terrain
   re-forms for that pair.
4. **What this means** - data dominates, scale is second-order, with visible
   caveats.

## Data

The page is synced from the validated scratch bake in
`~/align_experiments/prior_divergence/`:

- `terrain_data.json`: 6 base models, 3,000 sampled next-token positions,
  per-model `bits`, and `model_map`.
- `terrain.html`: reference renderer copied here as `reference-terrain.html`.
- `data/gate_result_6m.json`: empirical gate showing same-data pairs flatten and
  data-different pairs produce mountains.
- `data/rebake_6m.log`: rebake log from the six-model run.
- Provenance scripts in scratch: `terrain_build_6model.py` and
  `terrain_render_build.py`.

The bundled page inlines the terrain JSON into `index.html`; the copy in
`data/terrain_data.json` is kept for provenance and scripts.

## Loading

The page preloads its two pinned Three.js modules and requests them in parallel
while the inline terrain data arrives. The loader reports the real phase and
elapsed time. First visits show a production-measured `0.5-2.5s` range; after a
successful visit, that browser sees its own previous observed load time instead.
When a wait exceeds the measured range, the copy says so rather than letting an
expired countdown imply that the page is stuck.

The calibration and raw samples are in
`data/load_benchmark_2026-07-16.json`. It uses first contentful paint to
interactive terrain as the user-visible metric. The sample is from one location
and is an expectation range, not a latency guarantee.

## Honesty Boundaries

- Curated sample, not natural density: domain-balanced and tail-oversampled.
- UMAP x-y is a lossy projection; axes are not canonical.
- The metric is a surprisal gap on the observed continuation, not symmetric JSD
  and not correctness.
- Same-data flattening is an absolute-elevation drop, not proof that tail shape
  disappears.
- Scale is a second-order nudge; data family dominates.

## Controls

On compact and touch layouts, the lesson becomes a bottom sheet over the
terrain. **Explore** opens the model map, pair presets, height and colour modes,
and legend in a scrollable drawer. Drag rotates the terrain, pinch zooms, and a
tap opens point detail. Primary touch targets are at least 44 px; point detail
does not auto-open over the lesson on compact layouts.

Deep links:

- `#0` through `#4` restore the act.
- `?a=gpt2&b=gemma-2-2b`, or `?pair=gpt2|gemma-2-2b`, restores the pair.
- `?density=faithful|reveal`, `?color=domain|surprised`, `?pick=0`, and
  `?snap=1` restore view state for tests/screenshots.

## Testing Hook - `window.__viz`

| Method | Returns / effect |
|---|---|
| `state()` | `{ ready, act, acts, pair, density, color, selected, n, models, hasBits }` |
| `go(i)` | switch act and apply the act preset |
| `setPair(key)` | switch model pair by `a|b` key |
| `setModels(a,b)` | switch model pair by names |
| `setControl(name,value)` | set `ladder`, `density`, or `color` |
| `selectPoint(i)` | open the point detail panel |
| `point(i)` | return raw point data |
| `pairs()` | return all 15 model pairs |
| `stats(a,b)` | deterministic bit-gap stats for a pair: `{ meanDiv, maxDiv, above10, n }` in bits/char (display-mode independent) |

Run:

```bash
npm run test:prior-atlas
# Standalone production deployment:
PAGE_URL=https://prior-atlas.vercel.app npm run test:prior-atlas
```

The release test drives a deliberately delayed loader, a 1280 px desktop
viewport, and a 390 px touch viewport. It checks parallel CDN starts, calibrated
loader state, responsive non-overlap, horizontal overflow, drawer focus,
touch-target sizes, point-detail dismissal, canvas pixels, and console errors.
