# Alignment empirical bakes

Repo-local scripts and JSON artifacts for the alignment-method explorable. A
result is only called measured when the corresponding JSON exists under
`bakes/`. Small-model results establish the behavior of that run, not a general
frontier-model claim.

## Current run status

| Beat | Runner / source | Artifact | Status |
|---|---|---|---|
| SFT endpoints | `sft_generations.py` using the completed 400-step SmolLM2 run | `bakes/sft_generations.json` | measured; base and final only |
| SFT training transition | synced from the completed checkpoint sweep | `bakes/sft_behavioral_op.json` | measured; front-loaded base-to-step-50 change |
| DPO margin | `dpo_trajectory.py` | `bakes/dpo_trajectory.json` | measured on a fixed 12-pair probe |
| Constitutional judge | `constitutional_matrix.py` | `bakes/constitutional_matrix.json` | measured null: 201/240 position-A choices, zero constitution-majority flips |
| RLVR / GRPO | `rlvr_grpo.py` | `bakes/rlvr_curve_12step_unbalanced.json` | measured pilot, position-confounded; confirmation pending |
| Refusal direction | synced seven-alpha white-box sweep | `bakes/refusal_sweep.json` | measured on 3 harmful + 3 benign prompts |
| Diversity | synced base-vs-instruct experiment | `bakes/diversity_metrics.json` | measured adjacent effect; not DPO-specific |

## DPO verdict

The fixed probe scores the same preference pairs at every shown optimizer step.
From step 0 to 24:

- chosen summed log probability: `-62.80 -> -50.52`
- rejected summed log probability: `-46.54 -> -60.22`
- chosen-minus-rejected margin: `-16.27 -> +9.70`

This run widened the gap by raising chosen likelihood and lowering rejected
likelihood. It does not support using "both likelihoods sink" as the live demo.

## Constitutional verdict

The pilot exposed answer-position bias. The rerun therefore judged each pair in
both candidate orders across four constitutions and five seeds. Position A was
selected 201 of 240 times; semantic choices were nearly tied and no scenario's
majority changed across constitutions. The honest 0.5B demo is weak-judge bias,
not successful constitution swapping.

## RLVR calibration history

1. Exact-integer arithmetic with 24-token completions: all rewards were zero
   because every completion was clipped before its answer. Gradient was zero.
2. Multiple-choice arithmetic: calibration reached 22.5% sample accuracy and
   40% pass@4, with mixed rewards inside several four-sample groups.
3. Twelve GRPO steps produced nonzero gradients. Paired held-out accuracy moved
   22.5% to 27.5% and pass@4 40% to 50%, but answer positions were unbalanced and
   the policy shifted toward A. This is not accepted as a reasoning gain.
4. The runner now balances correct positions exactly across 32 train and 40
   held-out tasks and defaults to 48 steps. That confirmation remains pending.

Run the pending confirmation only when other MPS workloads are unloaded:

```bash
~/.venv-align/bin/python projects/alignment/empirical/rlvr_grpo.py
```

The runner writes status and partial trajectory files throughout the run.

## Resource guardrails

- Run one MPS experiment at a time.
- Unload Ollama models first; two pinned models previously occupied about 33 GB
  of unified memory.
- Keep checkpoint retention bounded. `sft_diagnostic.py` defaults to one retained
  checkpoint and empties the MPS cache every five steps.
- Do not delete the older 20 GB diagnostic directory or 34 GB scratch SFT run
  without explicit approval; they contain reproducibility artifacts.
