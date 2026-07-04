# Attention section rebuild — earn every word in order

**Principle (Gwern grow-speech):** the attention section must earn `query/key/score/
softmax/value/head` *in order*, at the moment each becomes useful — not open on them.
The current section opens the one-head walkthrough on layer 0 (the BOS-sink,
positional layer) with all the jargon at once. That's the core mistake.

**Verified by experiment** (`scratchpad/mine_attention_examples.py`, gemma-2-2b):
the legible attention is at **mid layers**, not layer 0. Chosen showcase example =
**induction**, because it's the one case where key-chooses vs value-copies is undeniable.

## The example (chosen)

`When Mary went to the store, Mary bought milk. When John went to the store, John bought`

Tokens (gemma-2-2b, 21): `<bos> When Mary went to the store , Mary bought milk . When John went to the store , John bought`
- **Followed token** = the last ` bought` (idx 20) — the predictor.
- **Showcase head** = **L17 H0**, which reads ` milk` (idx 10) at **87%** (BOS 0.05).
  The model is *copying the answer from the earlier pattern* — induction.
- **Most head-diverse layer** = L13 (heads split across milk / store / John / …).
- Per-model showcase (layer, head) differs — the bake should auto-detect and store it.

## The 10 steps (what shows · data · reuse/new)

| # | step | what the learner sees | data | reuse / new |
|---|---|---|---|---|
| 1 | Follow one token | 21 tokens, gold on last ` bought`; "we follow this token — it must predict the next word" | pieces | reorder (strip exists) |
| 2 | The need | causality **on a mid token** (follow the *first* ` bought` idx 9, grey its future 10–20 → "reads only what came before"), then move to the last ` bought` which sees all | causal mask | **new caption** |
| 3 | Plain reading | the last ` bought` lights earlier tokens by strength — it reaches back to ` milk`. **No query/key.** "brighter = more useful now" | `attn_full` avg @ showcase layer | **new framing** (cell-lighting exists) |
| 4 | Query | "` bought` forms a question: *what did I buy last time?*" | `qk[L].heads[h].q16` | reorder (mode 9) |
| 5 | Key | "each earlier token has a tag; ` milk`'s tag = *I follow a 'bought'*" | `k16` | reorder |
| 6 | Score + /√d | question·tag → score; ` milk` scores highest; /√d = pressure valve | `sc` | reorder + pressure gauge |
| 7 | Softmax → pattern | scores → % summing to 100 (milk 87%) = the attention pattern | `wt` | reorder |
| 8 | **Value + write-back** | the key only *chose*; ` milk`'s **value** (meaning packet) is mixed in and **added back to ` bought`'s stream** → sets up the MLP handoff | **needs `v16` (new bake field)** | **new** |
| 9 | Head → board | that single reading was **8 heads blended** — the avg you saw *splits* into specialists (H0=induction→milk; others elsewhere) | board + `qk` | gate after 1–8 |
| 10 | Architectures | MHA/GQA/sliding/L-G/soft-cap via the model-switch — shelves regroup as you flip models | GQA rail, nuances | gate here |

**The arc:** step 3's single "reading" *is* step 9's `avg` row. Introduce "head" late,
and the average splits into the specialists. Step 8's write-back closes attention back
onto the residual-stream spine and hands off to the MLP.

## Code changes

- **`jBuildAIntro`/`jUpdateAIntro` (mode 9)** — currently jumps to query/key at layer 0.
  Rebuild as steps 1–8, each earning its word; use the showcase `(layer, head)`, not L0.
- **Board (mode 3 beat 1)** — step 9; entry continuous from the walkthrough's avg.
- **GQA rail + `attnScheme` + nuances** — move to step 10 (gate behind the core; keep
  surfaced via the model-switch, which the user likes).
- **Scroll map (`jScroll`)** — re-allocate stage-4 sub-progress to the 10 steps.

## Re-bake requirements (blocker — needs the model venv + GPU)

Extend `bake_model_walk.py`:
1. `WALKTHROUGH` → the Mary/milk sentence.
2. **`v16`** per head (value vectors) — for step 8.
3. **Post-RoPE rotated q/k** (`hook_rot_q/k`) so the pin-detail q·k matches the score.
4. **`showcase: {layer, head, target}`** — auto-detected best induction head per model.
5. bias norms (honest bias story, later nuance).
Re-bake gemma-2-2b first (fast) to build against; then all models before deploy.

## Known trade-offs / open items

- **Default gemma loses its SAE "what it now means" panel** until `precompute_sae.py`
  is re-run on the Mary/milk sentence (it's sentence-specific). The MLP beat falls back
  to the generic scene meanwhile. Re-run SAE later.
- The default journey currently uses the **embedded** gemma bake (playground_data.json,
  from the heavy is/ought precompute). Switch the default to `walk_gemma-2-2b.json`
  (Mary/milk) so all models go through the same bake path.
- Per-model showcase layers/heads need the experiment run across all models (extend
  `mine_attention_examples.py`) — or rely on the baked auto-detected `showcase`.
