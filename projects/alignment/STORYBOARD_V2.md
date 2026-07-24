# Alignment explorable — storyboard v2

## Thesis

`Aligned` is not a property added to a model. Post-training changes different
behaviors in different situations, according to the examples, preferences,
rules, and checkers supplied by particular people and institutions.

The explorable follows one model through a measured checkpoint chain. A fixed
map of situations stays in place while response fields change over it. The
reader first sees what changed, then learns which training signal caused it and
which nearby behavior paid the cost.

## Visual contract

- **Geography is fixed and model-independent.** A prompt never moves merely
  because the selected checkpoint changed.
- **Every visible field names its measurement.** Height never means
  "alignment". It can mean answer rate, refusal rate, preference margin,
  distribution shift, or diversity, one at a time.
- **Behavior precedes internals.** The main map is driven by generations and
  validated response labels. Residual-stream geometry appears later as a
  separate interpretability lens.
- **Uncertainty is visible.** Counts, sample sizes, and intervals travel with
  every measured aggregate.
- **One model means one lineage.** Base, SFT, preference, and safety stages must
  descend from the same checkpoint. Cross-model evidence is a labeled aside.

## The persistent object

Each point is a prompt. Its position is fixed across the journey. Nearby points
are similar situations, not similar model activations.

The selected field supplies:

- **height:** magnitude of the selected measured quantity;
- **color:** behavioral direction, such as answer, refuse, redirect, or hedge;
- **contour:** a decision boundary or uncertainty band;
- **click:** the prompt, sampled responses, counts, and exact artifact source.

The production atlas uses held-out, naturally phrased prompts. Authored prompts
may train or calibrate a measurement but cannot also serve as its only test.

## Scroll journey

### 0. A base model continues

Start with one ordinary request. The base checkpoint continues text; it has not
yet been trained into a reliable conversational role. One response, no map.

### 1. Supervised fine-tuning creates answer mode

Pull back to the fixed situation atlas. Scrub base → early SFT → final SFT.
Answer-like behavior spreads broadly, with the largest measured transition
shown where it actually occurs. Explain demonstrations only after the reader
has seen the change.

### 2. Preferences choose among acceptable answers

Hold the map fixed and switch to preference margin and response diversity.
Show where preferred style rises, where rejected responses sink, and whether
the output fan narrows. DPO is the measured branch; PPO is an alternate recipe,
not the next chronological checkpoint.

### 3. Safety draws a local boundary

Show refusal, safe redirection, and over-refusal as separate labels. Harmful,
dual-use, and scary-benign neighbors make boundary errors visible. Do not call
the absence of compliance a positive refusal effect.

### 4. Refusal surgery

Expose the white-box refusal-direction coefficient. The same prompt set remains
on screen while harmful compliance and benign over-refusal change in opposite
directions. This is a causal intervention with the experiment's small sample
size shown explicitly.

### 5. Some objectives have no signal here

Overlay the verifier field. Math/code regions have a checker; advice and value
regions do not. RLVR belongs here as a branch demonstrating the reach and limit
of verifiable reward, not as a universal final alignment stage.

### 6. Look inside

Only now open the residual-stream lens. Compare base and post-trained geometry
as aligned small multiples or a registered animation. This view explains a
representation; it does not define the situation map used to prove itself.

### 7. Aligned to whom

Zoom from the map to the sources of its fields: demonstrations, preference
pairs, constitutions, safety policies, and checkers. The page ends by making the
incentive landscape inspectable rather than claiming a single correct target.

The multi-agent and societal-power view is a coda or sequel. It should not be
presented as an empirical continuation until its own substrate exists.

## Method branches

The main lineage is `base → SFT → DPO → safety intervention`. Other methods are
branches from the stage whose signal they replace:

- PPO branches from preference tuning.
- Constitutional/RLAIF branches from the source of preference judgments.
- RLVR branches where a verifier exists.
- The existing methods workbench remains the comparison appendix.

## Build gates

1. Freeze a model-independent prompt map and pass layout-stability checks.
2. Produce one lineage with named local checkpoints.
3. Bake sampled generations and response labels for every stage.
4. Validate labels against a human-reviewed stratified sample.
5. Add likelihood probes only as corroboration, using multiple paraphrases.
6. Render the staged document from the compact bake.
7. Drive `window.__viz`, assert artifact-derived values, and review desktop and
   mobile screenshots before calling the page ready.
