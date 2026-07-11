# Concepts to communicate — alignment explorable

**Legend:** 🟢 demonstrable at our scale (baked/live on 0.5B/360M) · 🟡 explain/mention (concept or supporting, softer evidence) · 🔵 cite as frontier result (NOT a live small-model demo).

## A. The setup — what we're aligning
- **Base model = simulator** — no fixed self; "anyone on demand" 🟢
- **The prior is a fingerprint of the corpus**, not a neutral average — the voice of whoever wrote the *most* 🟢 *(Act 1, tiny-pretrain demo)*
- **Next-token / autocomplete** — bridge from the prior explorable 🟢
- **Temperature / sampling** — how far the simulator wanders 🟢
- **Persona / simulacrum / the mask** — the character the simulator puts on 🟡

## B. How alignment is done — the methods (the "how")
- **Demonstrations → SFT** (supervised fine-tuning) 🟢
- **Preferences: rank-ordering** responses (A > B, C is fine) — the core signal 🟢 *(concept)*
- **RLHF** (RL from Human Feedback) = **reward model** + **PPO**; trained on human **rater** comparisons 🟡
- **DPO** (Direct Preference Optimization) — skips the reward model (our instruct models are SFT+DPO) 🟡
- **PPO vs DPO tradeoff** — 4 models vs 2; stability; diversity cost 🟡
- **Constitutional AI / RLAIF** — AI feedback instead of humans 🔵
- **Verifiable reward: RLVR / GRPO** — math/code checkers (the "fat straw") 🟡
- **The reward "thin straw"** — demonstrations → preferences → verifiable → the wall (no checker) 🟡
- **Diversity / mode collapse** — alignment homogenizes output 🟢 *(E6)*

## C. THE HERO — safety as a thin, separable direction (Act 2)
- **Refusal** — the behavior 🟢
- **Safety / harmlessness** vs **helpfulness** — two different things 🟢
- **The refusal direction** — ONE direction mediates refusal 🟢 *(E3)*
- **Ablation / activation steering** — remove or add a direction 🟢 *(E3/E7)*
- **Jailbreak** — remove the fence / adversarial prompt 🟢
- **Abliteration** — weight-orthogonalization jailbreak (bakes the ablation in) 🟡
- **Shallow safety** — the fence lives in the first few tokens 🟡 *(E4 / prefill)*
- **Prefill attack** 🟡
- **Over-refusal** — crank the fence too high, it refuses "capital of France" 🟢 *(E7)*
- **White-box vs black-box; open weights ⇒ the fence is removable** — the punch 🟢
- **Fence ≠ values** — ablate refusal and the helpful/coherent self SURVIVES 🟢 *(E4 — killed the "one object" claim)*
- **Instruction-tuning ≠ safety-tuning** — SmolLM2 is helpful but has no fence 🟢

## D. The lenses — how we see inside (interpretability)
- **Residual stream / activations** 🟢
- **Diff-of-means / linear directions** 🟢
- **Persona vectors / steering vectors** — the axes of character 🟢 *(E7)*
- **Rank of a behavior** — single direction vs a "concept cone" 🟡 *(E3 rank probe)*
- **Probing / linear separability** — the "basin" (soft at our scale) 🟢 *(E1)*
- **Logit lens** — bridge from the prior explorable 🟡
- **SAEs / features, attribution graphs / circuits** — cite; too big for 0.5B 🔵

## E. The deep end — the emergent self & inner alignment (Act 3, mostly cited)
- **Inner vs outer alignment** 🔵
- **Mesa-optimization / a mesa-objective** — the model's own goal ≠ the training goal 🔵
- **Deceptive alignment / alignment faking** — Claude 3 Opus defending its values 🔵
- **Goal-guarding; corrigibility** — a mind robust enough to resist correction (double edge) 🔵
- **Sleeper agents / backdoors** — persistence scales UP with size 🔵 *(optional labeled toy backdoor)*
- **Revealed preference vs stated** — what it does when it can act > what it says 🟡
- **Agency / tool use / stakes** 🟡

## F. The thesis threads (what it all means)
- **Is/ought entanglement** — truth & value co-arise, can't decouple (pramana) 🟡 *(E5 direction)*
- **Emergent misalignment** — narrow bad training → broad value shift 🟡 *(E5, weak-but-real via the linear direction, not the behavioral %)*
- **OOD generalization** — does a principle hold beyond its training family? (the honest depth probe) 🟢 *(E3 OOD)*
- **The attractor / persona basin / "well"** — framing metaphor (soft, not sharp) 🟡 *(E1)*
- **"Aligned to WHAT?"** — value pluralism; alignment is a *choice*, not one truth; the P1–P6 disunity (AOI) 🟡
- **Verify structure, not output** — the honest move when nothing is checkable 🟡

---

**Build order implied by the tags:** the 🟢 cluster in **C** (+ E1/E6/E7) is the demonstrable spine — build there. **B** and **F** are taught in prose/simple widgets around the demos. **E** is a cited coda, never a live 0.5B claim.
