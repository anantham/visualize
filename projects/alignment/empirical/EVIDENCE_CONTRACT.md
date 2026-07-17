# Evidence contract for the alignment atlas

This file is binding for measured interface copy. The rendering layer may say
less than the artifacts support, never more.

## Production lineage

The intended case study is SmolLM2-360M:

| stage | source | current state |
|---|---|---|
| base | `HuggingFaceTB/SmolLM2-360M` | available |
| SFT checkpoints | `~/align_sft/ckpts/checkpoint-{50..400}` | available |
| final SFT | `~/align_sft/ckpts/final` | available |
| preference | LoRA DPO continuing from final SFT | measured; `bakes/pipeline_dpo.json` |
| safety | marginal safety DPO with frozen preference reference | runner ready; execution blocked by session limit |
| refusal surgery | direction fit on the safety checkpoint | runner ready; waits on safety adapter |

Released Qwen base/instruct comparisons and the existing Qwen refusal sweep are
supporting evidence. They are not stages in this SmolLM lineage.

## Required point schema

Each atlas point must contain:

```json
{
  "id": "stable-prompt-id",
  "prompt": "verbatim prompt",
  "split": "heldout",
  "region": "dual_use",
  "position": {"x": 0.0, "y": 0.0, "method": "..."},
  "stages": {
    "sft": {
      "samples": 8,
      "counts": {
        "answer": 0,
        "refuse": 0,
        "redirect": 0,
        "hedge": 0,
        "malformed": 0
      },
      "responses": [],
      "probe": {"name": "multi-paraphrase-v1", "value": 0.0}
    }
  }
}
```

No percentage is rendered without its numerator and denominator in the same
selected-point view.

## Measurement hierarchy

1. **Primary:** sampled generated behavior under declared decoding settings.
2. **Secondary:** human-reviewed response-mode labels and their counts.
3. **Corroborating:** likelihood margins over multiple matched continuation
   paraphrases.
4. **Interpretability:** residual activations and causal interventions.

A canned-prefix likelihood margin must not be described as an observed response
rate. A prompt named `sycophancy_bait` is not evidence of sycophancy unless the
measurement distinguishes agreement from candid disagreement.

## Layout rules

- Position cannot be computed from the final aligned checkpoint alone.
- Labels used to evaluate the map cannot also select the winning layer or
  projection without held-out validation.
- Layout stability must be checked across projection seeds and reasonable
  neighborhood settings.
- A residual-stream projection is an interpretability view, not the canonical
  geography.

## Claim scope

Every aggregate records model lineage, prompt source, split, decoding settings,
sample count, classifier version, and bootstrap interval. One model is a case
study. Repeated measurements on the same model are triangulation, not
independent replication.

Words prohibited unless explicitly computed or independently replicated:

- `90%`
- `independent corroboration`
- `alignment installed`
- `the model values`
- `safety rate` when the metric is continuation likelihood

## Test rule

Tests load the production bake and derive expected displayed values. They must
fail if a rendered count, prompt, response prefix, model lineage, or measurement
label diverges from its artifact.
