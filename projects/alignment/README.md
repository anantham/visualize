# Alignment explorable

A scroll-controlled sequel to `projects/next-token/`. The page follows one
SmolLM2-360M lineage while a fixed, model-independent map of situations keeps
its positions and measured response fields change over it.

Open `index.html` directly or serve the repo:

```bash
python3 -m http.server 4173
```

The page is self-contained after embedding its compact bakes:

```bash
python3 projects/alignment/embed_page_data.py
```

## Journey

1. Base continuation
2. SFT step 50
3. SFT step 400
4. DPO preference stage
5. Targeted safety preferences
6. Refusal-direction intervention
7. RLVR verifier boundary (separate Qwen pilot, explicitly labelled)
8. Residual-stream lens (separate Qwen endpoint diagnostic)
9. Sources of the objective

The seven-method workbench remains at `methods/index.html` as the comparison
appendix.

## Evidence

`STORYBOARD_V2.md` defines the journey and visual semantics.
`empirical/EVIDENCE_CONTRACT.md` defines what rendered measurements may claim.

| artifact | role |
|---|---|
| `empirical/bakes/situation_atlas.json` | fixed authored policy lattice and rejected-UMAP diagnostics |
| `empirical/bakes/pipeline_behavior.json` | verbatim sampled behavior across the SmolLM lineage |
| `empirical/bakes/pipeline_dpo.json` | disjoint-pair DPO trajectory |
| `empirical/bakes/pipeline_safety.json` | targeted same-lineage safety preferences; pending |
| `empirical/bakes/pipeline_refusal.json` | same-lineage refusal-direction sweep; pending |
| `empirical/bakes/rlvr_curve_12step_unbalanced.json` | separate, confounded verifier pilot |

Heavy adapters and checkpoints remain under the gitignored
`empirical/pipeline_runs/`. The page never reads those at runtime.

## Test hook

```js
window.__viz.state()
window.__viz.go(3)
window.__viz.select(promptId)
window.__viz.setAlpha(0)
window.__viz.stages()
```

Run browser verification while the repo server is active:

```bash
node projects/alignment/test.js
```

The test loads the JSON artifacts independently, checks displayed DPO and
refusal values against them, asserts the canvas painted, checks mobile overflow,
and fails on page or console errors.

See `empirical/PIPELINE_STATUS.md` for the exact current boundary and resume
sequence. Pending stages render as pending; the page does not borrow Qwen's
refusal result to fill the SmolLM gap.
