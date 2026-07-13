# The Simulator — a base model, one token at a time

Beat 0 of the alignment series. Teaches what a **base model** actually is *before*
any alignment: not a broken assistant, but a **simulator** that predicts the next
token and feeds it back — and whose output is steered entirely by what you feed in.
Everything shown is real, unedited **gemma-2-2b** (base, no instruction tuning).

## Stages

1. **the loop** — the autoregressive mechanism: context tokens in → the model's real
   top-8 next-token distribution → a token is picked → it feeds back → the sentence
   builds itself. `run 1/2/3` are three real sampled paths from the same prompt.
2. **how it picks** — sampling made interactive: a temperature slider reshapes the
   real distribution live (softmax over baked logits, recomputed in-browser), top-p
   trims the tail, and repeated sampling shows the choice wander. Answers greedy vs.
   temperature vs. top-k vs. top-p.
3. **you seed it** — same weights, different framing (Q&A / forum / children's book)
   → a different kind of document is simulated.
4. **show, don't train** — few-shot in-context learning as distribution-sharpening:
   0 examples → lost; a few examples → the distribution snaps onto the answer.
5. **it mirrors you** — clean vs. broken context → the generated tokens match the
   register they're given.
6. **so far** — the takeaway and the bridge to SFT.

## Data

`stream.json` is the only data file, produced by `bake_stream.py` (needs the
`~/.venv-align` environment and `google/gemma-2-2b`; runs on the Mac's MPS):

```bash
~/.venv-align/bin/python projects/simulator/bake_stream.py
```

It records, per stream, the real per-step top-k next-token distribution and chosen
token; per few-shot query, the answer-step distribution at 0 vs N examples; and the
top-30 logits per sampling context (so the sampling stage recomputes softmax exactly).

## `window.__viz`

- `state()` → `{ready, stage, id, group, idx, step, playing, stages}`
- `go(i)` — jump to stage `i`
- `step()` — advance the loop by one token
- `pick(i)` — select stream `i` within the current engine group

## Verify

`node projects/simulator/test.js` (serve the repo root first, e.g.
`python3 -m http.server 4173`) — drives all six stages, the loop stepping, the
temperature reshaping, few-shot toggle, seed/register switches, and checks for a
painted distribution, no console errors, and no mobile overflow.
