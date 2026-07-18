# Pinning the Assistant — SFT

Beat 1 of the alignment series (continues `projects/simulator/`). Shows how
supervised fine-tuning turns the base *simulator* into an *assistant* — by
imitating demonstrations — using the same autoregressive-loop visual as Beat 0,
with a **training checkpoint** axis added.

Real greedy generations from one SmolLM2-360M run, the **same chat-formatted
prompt at every checkpoint**, so the only thing that changes is the weights.

## Stages

1. **watch it happen** — the hero: a checkpoint scrubber (base → SFT-50 →
   SFT-400) over the loop. Scrub it and the same prompt's output transforms from
   a garbled ramble (the base can't hold the assistant format) into a coherent
   answer. The assistant is essentially present by step 50.
2. **how: imitation** — the mechanism: real SmolTalk demonstrations, with the
   answer highlighted as the only thing SFT's loss lands on. Same next-token
   prediction as Beat 0, trained on curated replies.
3. **what changed** — gained a reliable assistant; spent the simulator's range.
   Bridge to preference tuning.

## Data

`stream.json`, from `bake_stream.py` (needs `~/.venv-align`, the base model
`HuggingFaceTB/SmolLM2-360M`, and the SFT checkpoints in `~/align_sft/ckpts/`):

```bash
~/.venv-align/bin/python projects/sft/bake_stream.py
```

Per prompt, it records token-by-token top-k next-token distributions + chosen
tokens at each checkpoint, plus a few real SmolTalk demonstrations.

## `window.__viz`

- `state()` → `{ready, stage, id, ckpt, prompt, step, stages}`
- `go(i)` — jump to stage
- `ckpt(name)` — set the training checkpoint ("base" | "sft_50" | "sft_400")

## Verify

`node projects/sft/test.js` (serve the repo root first) — drives the checkpoint
scrubber (asserts base reads broken, SFT-400 reads coherent), the demonstrations,
and checks for a painted distribution, no console errors, no mobile overflow.

## Before editing copy

Read [`../CLAIMS.md`](../CLAIMS.md) — the claims-provenance discipline for these pages. Every number a reader sees is checked by `npm run audit:provenance`; prose claims need a human adversarial read (the gate caught 0 of the 3 overclaims this series shipped).
