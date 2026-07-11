# Methods Data Status

This tracks what the interactive methods workbench can honestly wire today.

| Method | Current widget | Real artifact found | Status |
|---|---|---|---|
| Pretraining | illustrative corpus switcher | Prior Atlas / prior-divergence terrain exists, but no corpus-conditioned generation JSON | Needs bake; do not imply from-scratch corpus training |
| SFT | illustrative demo-count dial | completed 400-step SmolLM2-360M run; `../empirical/bakes/sft_generations.json` and `sft_behavioral_op.json` | Endpoints measured; intermediate dial still illustrative |
| DPO | measured fixed-probe trajectory | `../empirical/bakes/dpo_trajectory.json` | Measured narrow run: margin widened via chosen up + rejected down; both-sink failure not observed |
| RLHF / PPO | simulated overoptimization curve | no PPO run expected | Keep simulated/cited unless deliberately building toy PPO |
| Constitutional AI / RLAIF | measured judge-failure matrix | `../empirical/bakes/constitutional_matrix.json` plus preserved pilot | 0.5B judge chose position A 201/240; zero constitution-majority flips. Use as judge-bias failure, not successful CAI |
| RLVR / GRPO | measured 12-step pilot plus real no-checker UI truth | `../empirical/bakes/rlvr_curve_12step_unbalanced.json`; balanced runner in `../empirical/rlvr_grpo.py` | Mixed rewards produced gradients, but small held-out gain was position-confounded; balanced 48-step confirmation pending |
| Safety / Refusal Direction | measured seven-coefficient sweep | `../empirical/bakes/refusal_sweep.json` | Seven coefficients on 3 harmful + 3 benign prompts; UI currently compresses to three states |

## Next Bakes

1. `pretraining_corpus_generations.json`: prompt x corpus completions and optional token distributions.
2. SFT intermediate checkpoints: generate at steps 50/100/200/400 if the demo-count dial remains.
3. DPO diversity: measure samples separately; do not infer diversity from the fixed log-probability probe.
4. Constitutional AI: a stronger/cited judge is required to demonstrate constitution-sensitive choices; the 0.5B result is a null.
5. RLVR: run the prepared 48-step position-balanced confirmation and accept a capability gain only if paired held-out results survive.
6. Refusal: add more harmful, benign, and scary-benign prompts before treating six prompts as a rate estimate.
