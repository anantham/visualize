# Alignment pipeline status

Updated: 2026-07-11 15:52 IST.

## Complete

- Fixed authored policy lattice: `bakes/situation_atlas.json`.
- SmolLM base → SFT step 50 → SFT step 400 → DPO generations:
  `bakes/pipeline_behavior.json`.
- Coarse response labels reapplied from stored verbatim outputs with repetition
  detection (`coarse-markers-repetition-v2`).
- DPO training and disjoint held-out trajectory: `bakes/pipeline_dpo.json`.
- Self-contained `../index.html` with completed data embedded.
- Static JavaScript syntax and JSON/embed validation.
- Desktop browser inspection of base, map, verifier, residual, and source stages
  completed before the execution limit was reached.

Current coarse behavior counts, 168 sampled outputs per stage:

| stage | non-refusal | refusal | redirect | hedge | malformed |
|---|---:|---:|---:|---:|---:|
| base | 70 | 7 | 0 | 1 | 90 |
| SFT step 50 | 159 | 0 | 0 | 9 | 0 |
| SFT step 400 | 155 | 0 | 0 | 13 | 0 |
| DPO | 156 | 0 | 0 | 12 | 0 |

These are automatic form/mode labels, not correctness or safety rates. In
particular, `non-refusal` includes harmful compliance.

## Blocked boundary

The Mac-GPU launch for `pipeline_safety_dpo.py` was rejected because the Codex
execution-usage limit was reached. The tool reported retry availability at
**19:04 IST on 2026-07-11**. The process never started; no safety result exists.

The standalone Playwright test launch was rejected by the same limit. Do not
mark the page Playwright-green until it runs.

## Resume sequence

Run one MPS process at a time:

```bash
~/.venv-align/bin/python projects/alignment/empirical/pipeline_safety_dpo.py
~/.venv-align/bin/python projects/alignment/empirical/pipeline_behavior_safety.py
~/.venv-align/bin/python projects/alignment/empirical/relabel_pipeline_behavior.py
~/.venv-align/bin/python projects/alignment/empirical/pipeline_refusal.py
python3 projects/alignment/embed_page_data.py
node projects/alignment/test.js
```

Acceptance gates:

1. Safety held-out margins must move in the intended direction by region.
2. Generated harmful refusal must rise without blanket scary-benign refusal.
3. Refusal surgery must show a coherent coefficient response or render an
   explicit null.
4. The final test must load the refusal artifact, verify both coefficient
   extremes, find painted canvas pixels, report no page errors, and pass mobile
   overflow checks.
