# You Rank It — preference tuning (DPO)

Beat 2 of the alignment series (after `projects/simulator/` and `projects/sft/`).
SFT can only imitate answers someone *wrote*. Preference tuning learns from something
far cheaper: a person looking at two answers and saying **which is better**. This beat
shows what that signal actually does — and what it doesn't.

Two real DPO runs on the Beat-1 SmolLM2-360M SFT checkpoint. Every bar is a measured
log-probability; nothing is simulated.

## Stages

1. **you rank it** — the mechanism. A held-out pair (one correct answer, one wrong,
   *deliberately similar length* so the comparison is length-fair). Scrub the training
   step and watch the model's likelihood of each. Two honest findings are built in:
   - the gap widens only **+0.396 → +0.464** per token (real, small), and **both**
     likelihoods rise — DPO controls the *difference*, not the goodness;
   - toggle to **summed** log-prob (what DPO's loss actually uses) and the gap stays
     **negative** (−2.97 → −1.39): the model still prefers the *wrong-but-shorter*
     answer. That's DPO's documented **length bias**, measured on our own run.
2. **the supervision** — the leverage point: one click between two answers. Counts
   (this run: 14 + 13 hand-made pairs; shipped SmolLM2-360M: **61,135** UltraFeedback
   pairs) and the disclosure map. Includes the honest twist: UltraFeedback's ratings
   were produced by **GPT-4**, not humans — in open models the "human" in RLHF is often
   another AI.
3. **watch it install** — the loop again, with a before/after toggle. "Prefer concise"
   installs in 150 steps on 13 pairs: **123.8 → 34.7 tokens (72% shorter)**, answers
   still complete.
4. **what it really did** — style installs cheaply; correctness barely moves. A widening
   gap is not a better model.

## Honest notes baked into the design

- Pairs are built by **instruction-steering** (chosen = "answer in one short sentence",
  rejected = "answer in thorough detail"), both **complete** answers, trained on the
  plain prompt. An earlier version built pairs by truncation (chosen = a cut-off prefix
  of rejected), which taught the model to stop mid-sentence and produced fake
  "over-optimization" deflections. Do not reintroduce that.
- The diversity metric (distinct-2) is **not** reported: it rises mechanically on
  shorter text, so it measures length, not diversity.

## Data

`stream.json`, from `bake_stream.py` (needs `~/.venv-align` and the SFT checkpoint in
`~/align_sft/ckpts/final`):

```bash
~/.venv-align/bin/python projects/preferences/bake_stream.py
```

## `window.__viz`

- `state()` → `{ready, stage, id, mstep, metric, state, step, stages}`
- `go(i)` · `mstep(i)` (training-step index) · `metric('pt'|'sum')`

## Verify

`node projects/preferences/test.js` (serve the repo root first) — asserts the bars are
artifact-derived, that scrubbing training grows the chosen bar, that the summed view is
negative while per-token is positive (the length bias), the supervision counts and the
GPT-4 disclosure, and the before/after install toggle.
