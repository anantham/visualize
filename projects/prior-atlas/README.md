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

## Honesty Boundaries

- Curated sample, not natural density: domain-balanced and tail-oversampled.
- UMAP x-y is a lossy projection; axes are not canonical.
- The metric is a surprisal gap on the observed continuation, not symmetric JSD
  and not correctness.
- Same-data flattening is an absolute-elevation drop, not proof that tail shape
  disappears.
- Scale is a second-order nudge; data family dominates.

## Controls

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
| `stats(a,b)` | return deterministic terrain-height stats for a pair |

Run:

```bash
npm run test:prior-atlas
```
