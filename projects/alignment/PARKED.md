# PARKED — the safety explorable

**Status: parked, deliberately not committed and not publishable.** Read this before
reviving anything in here.

The live alignment series is **`projects/simulator/` → `projects/sft/` →
`projects/preferences/`**. This directory is its empirical ancestor: the ADRs, the
evidence contract, the runners, and the bakes. Those are committed and remain the
governing record. The **page** (`index.html` / `test.js`) and the artifacts embedding
harmful completions are **git-ignored on purpose**.

## Why it's parked

1. **It renders harmful compliance text.** The selected-response panel shows each
   point's verbatim generation. On `clear harm` points at the SFT/DPO/safety stages
   that is the model cheerfully explaining gun assembly, identity theft, and dog
   poisoning. The output is weak (360M) but the disposition is compliance, and this is
   a public repo. Reviving the page requires redacting the harmful region in the UI
   first (the pattern exists: the old refusal beat rendered
   `"redacted harmful procedural content"`).
2. **Its copy contradicts its own data.** Stage 4 says *"Now draw the boundary… safety
   appears"* and stage 5 says *"a white-box direction can change refusals locally"* —
   while the measured badges beside them read **0/24** and **0/6 → 0/6**. The prose was
   written expecting success; the runs came back null. Per
   `empirical/EVIDENCE_CONTRACT.md` ("the rendering layer may say less than the
   artifacts support, never more") the page is currently in violation.
3. **The direction changed.** Safety turned out to be the least legible, least
   shareable beat — a weak null needing redaction — so the series pivoted to the
   base-model / SFT / preferences arc, which is fully benign and publishable.

## What the safety runs actually found (keep this — it's real)

At SmolLM2-360M, on our budget, **safety did not install**:

- **Targeted safety DPO** (24 authored pairs, 24 steps): generated harmful refusal
  stayed at **0/24** — verified genuine compliance, not a classifier miss. The held-out
  likelihood margin nudged **+1.9** but stayed deeply negative (−52).
- **Refusal-direction surgery**: the direction separates harmful from benign in
  activation space with a large effect (**5.15** at layer 28), yet steering produced
  **0/6 refusals at every coefficient**. The model *represents* harm and has no refusal
  *response* to trigger.
- **Honest caveats.** The safety-DPO null is badly under-powered (24 pairs vs the
  tens of thousands real safety training uses) — it shows *"24 pairs didn't install
  it"*, **not** *"safety can't install"*. The steering null carries a calibration
  caveat: one layer-28 direction added at every layer with coefficients capped at ±0.7,
  never independently calibrated, so a stronger intervention was not ruled out.

The contrast that makes it legible: **Qwen2.5-0.5B-Instruct**, the same size class,
*does* refuse (2/3 baseline) because it received real RLHF safety. It's training, not
scale.

## To revive

1. Redact harmful-region generations in the UI (never render them verbatim).
2. Rewrite stages 4–5 to state the **null**, not the hoped-for result.
3. Either calibrate the refusal steering or scope the claim to "at these coefficients".
4. Human-review the coarse classifier (`human_reviewed: false` today).
5. Re-run `node projects/alignment/test.js` — and update it, since it must assert the
   null, not the old copy.
