# Model coverage — next-token

The model dropdown (and the persistent top-right switcher) flips the journey to
each model's **real** precomputed data, or runs it **live** for the small ones.
Coverage is **not uniform** — this documents what each model has and the gaps.

## What each model has

| model | journey data | attention heads (`qk`) | SAE features | live mode |
|---|---|---|---|---|
| **gemma-2-2b** | embedded (default) | ✅ | ✅ Gemma Scope | ✅ |
| **gemma-2-2b-it** | baked | ✅ | ❌ | ✅ |
| **gemma-2-9b** | baked | ✅ | ❌ | — (precomputed) |
| **gemma-2-27b** | ❌ **metadata only** | ❌ | ❌ | — |
| gpt2 / gpt2-xl | baked | ✅ | ❌ | ✅ (gpt2) |
| pythia-1.4b | baked | ✅ | ❌ | ✅ |
| pythia-12b | ❌ metadata only | ❌ | ❌ | — |
| qwen2.5-0.5b / 7b | baked | ✅ | ❌ | ✅ (0.5b) |
| mistral-7b | baked | ✅ | ❌ | — |

- **SAE features** (the "what it now means" panel) are **gemma-2-2b only** — they come
  from Gemma Scope via `precompute_sae.py` (res-16k) + `precompute_mlp.py` (mlp-16k)
  with Neuronpedia labels. Other models show *"(features available for gemma-2-2b)"*.
- **Live mode** (type your own sentence) runs the ≤2B models on the HF Space; larger
  models are precomputed-only and the Static/Live toggle greys out.
- **Journey bakes** come from `pramana/.../views/bake_model_walk.py` → `walk_<key>.json`.

## Parked / addable

- **gemma-2-27b — PARKED: needs a bigger box.** 27B in bf16 is ~54 GB resident **plus**
  a ~54 GB download; it does not fit the 64 GB dev box (worse with the activation
  cache + overhead). Bake on a larger/cloud machine: `bake_model_walk.py gemma-2-27b
  gemma-2-27b bf16`, then copy `walk_gemma-2-27b.json` into this folder. Until then it
  stays in the dropdown as **metadata-only** (the architecture diagrams reflect 27B;
  selecting it does not load a journey).
- **9b SAE features — DONE.** `precompute_sae_model.py` ran Gemma Scope 9b res-16k SAEs
  across all 42 layers (3528 Neuronpedia-labelled features) → patched into
  `walk_gemma-2-9b.json`. The IT model could still reuse the 2b SAEs (approximate).
- **pythia-12b — metadata-only**, held with the deeper attention pedagogy.

## Instruction-tuned model (gemma-2-2b-it)

Architecturally **identical** to gemma-2-2b — same layers, dims, vocab, heads. Only
the weights were post-trained: **SFT** (fine-tuning on example chats) then
**preference optimization**. The journey is mechanically unchanged; the prediction
beat adds a **base↔IT comparison** that shows the tuning's fingerprint — markdown
(`**`) and ellipsis tokens climbing into the IT's runner-ups while the base's stay
plain words.
