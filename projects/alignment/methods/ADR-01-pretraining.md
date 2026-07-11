# ADR-01 — Pretraining / Base Model as a tradeoff machine

**Status:** proposed (explorable beat design)

**One-liner:** `internet-scale corpus likelihood` → `broad capability + every possible voice` → `not an assistant, no stable "should", no safety, prior-biased` → `unsteerable, prolific-writer priors leak into every answer`

## Signal source
The only signal is **next-token likelihood over a fixed corpus mixture** — web text, books, code, forums. There is no human in the loop, no notion of correct, helpful, or safe: the model is rewarded purely for predicting what came next in text that already exists. Whatever the corpus over-represents (a prolific blogger's voice, StackOverflow's register, one language's grammar) becomes the model's *prior* — its default guess before you've steered it at all. This is the cheapest-per-token signal in the whole pipeline and the most expensive in total.

## What it buys
Almost everything downstream capability rests on: broad world knowledge, code, arithmetic-ish patterns, translation, and — crucially — **the widest possible distribution of voices and registers**. A base model can plausibly continue as a lawyer, a shitposter, a 1600s pamphleteer, or a Python linter, because all of those lived in the corpus. This is the *ceiling* for two of our needles (diversity and OOD-generalization): every later alignment method spends down from here, never adds to it.

## What it costs
It is **not an assistant**. Ask it a question and it may continue with three more questions, because in the corpus questions are followed by questions. There is no stable "should" — it will complete anything, helpful or harmful, with equal fluency. Its priors are *biased by who wrote the most*: overrepresented authors, dominant languages, and popular opinions become the default voice, and that bias is invisible until you probe it.

## Failure mode
**Unsteerable, prior-driven completion.** With no instruction-following and no refusal, the base model answers *as the corpus would*, not as you want — it drifts into the register of whoever wrote the nearest-neighbour text, leaks corpus bias as if it were fact, and cannot be told to stop. You don't get a wrong assistant; you get a mirror of the internet's priors with no one steering.

## Dashboard baseline state

Pretraining is the one baseline-state row in the series. Later method rows are marginal
moves applied after this stage.

| Needle | Move | One-line why |
|---|---|---|
| usefulness | ↑ | Vast latent knowledge and skill — but delivered as raw completion, not an instruction-following assistant. |
| diversity | ↑↑ | The ceiling. Every voice, register, and dialect in the corpus is reachable; all later alignment spends from here. |
| refusal/safety | ↓↓ | No refusals, no stable "should" — completes anything, including what you don't want. |
| preference-margin | n/a | Undefined: no reward model and no preference pairs exist yet. The axis is absent. |
| OOD-generalization | ↑↑ | Broadest prior → widest generalization; nothing has been narrowed or specialized yet. |
| compute-cost | off-scale | The single most expensive stage in the whole pipeline — millions of GPU-hours at frontier scale, not on the post-training cost ruler. |
| verifier-strength | ↓↓ | The "verifier" is only next-token likelihood over the corpus — infinitely scalable, but blind to true / helpful / good. |

## The interaction ("make clear by")
A **CORPUS SWITCHER**. The viewer sees one fixed prompt (e.g. *"The most important thing about money is"*) and a row of corpus chips — `Wikipedia`, `Python code`, `Books/1800s`, `Reddit`, `News`. Tap a chip and the completion under the prompt **re-writes itself in that corpus's voice**: the same question, a different prior. The key move is a **MIX slider** between two chips: drag from `Wikipedia` → `Reddit` and watch the completion *morph* mid-sentence from encyclopedic to conversational — you are literally dragging the prior. This is the next-token "drag → watch it happen" grammar: your hand on the slider, the text re-priors in real time.

While you drag, the shared dashboard reacts honestly: **diversity stays pinned at ↑↑** (all corpora are "on the table"), **refusal/safety stays flat at zero** for *every* corpus (none refuse — that's the point), and the **preference-margin and verifier needles show as greyed-out / "n/a"** — visibly *empty machinery*, because the reward and verifier apparatus simply doesn't exist yet at this beat. That emptiness is the teaching moment: pretraining hasn't aligned anything to a *should*; it's only aligned to *who wrote the corpus*.

Baked vs live: the completions and their next-token distributions are **baked** (precomputed JSON per corpus × prompt) so the beat is instant and safe to curate; the underlying divergence is **real**, reusing the already-built prior-divergence terrain checkpoints. An optional live tiny-model path can generate a fresh completion, but baking is the shipping default.

## What we can demonstrate at our scale
🟡 with a 🟢 cousin. The **prior-divergence terrain beat is already built and validated at 0.5B**; the current corpus-switcher in the methods workbench is only illustrative text until real corpus-conditioned generations are baked. The asterisk remains: we do **not** train N base models from scratch. We approximate "different pretraining corpora" via **continued-pretraining / domain-adaptation** of one tiny checkpoint on distinct corpora — the divergence-of-priors effect is genuine and observable, but the mechanism is a stand-in for from-scratch pretraining. The compute-cost magnitude itself is 🔵 / off-scale; we describe it, we never pay it.

## Build tasks
1. **Data / bake.** Pick 3–5 maximally-distinct corpora (Wikipedia, code, pre-1900 books, a forum register, news). Reuse the existing prior-divergence terrain checkpoints if they already cover these; otherwise continue-pretrain / domain-adapt SmolLM2-360M (or Qwen2.5-0.5B) per corpus. Choose ~4 benign shared prompts. Precompute per (corpus × prompt): the completion string and the next-token distribution for the first few steps. Emit as one JSON.
2. **Render.** Corpus chips + a two-corpus MIX slider, a fixed prompt selector, a completion pane that morphs on drag, and the shared 7-needle dashboard with diversity pinned ↑↑, refusal flat at 0, and preference-margin/verifier rendered as explicit "n/a — doesn't exist yet" states. Reuse the next-token distribution viz for the token bars.
3. **Verify.** Confirm completions genuinely diverge by corpus (not cosmetic re-skinning) and that none refuse. Sanity-check the mix slider interpolates believably. Per the project's verify-via-user norm, have Aditya eyeball a few corpus switches rather than run a costly headless screenshot loop.

## Honest caveats
- **We reuse pretrained checkpoints and stand in continued-pretraining for from-scratch pretraining** — the prior-divergence effect is real, the "N base models" framing is an approximation.
- **The compute needle is off-scale at our scale**: frontier pretraining cost is true and 🔵 cite-only here, but it is not comparable to post-training costs in the shared ruler.
- **360M/0.5B voices are crude** — completions can be incoherent or samey; curate baked prompts where divergence is visible.
- **The empty preference-margin / verifier needles are a feature, not a gap** — showing them greyed-out is the honest depiction that this machinery doesn't exist until later beats. Don't let the dashboard imply a zero where the concept is undefined.
- **Safety = "no refusals" must be curated**: because the base model will complete anything, we only ship benign prompts so the beat doesn't itself emit unwanted text.

## Links
- **Framework doc:** [`../README.md`](../README.md) — the shared thesis (every method is a tradeoff machine) and the 7-needle dashboard grammar.
- **Cousin beat:** the already-built, validated **prior-divergence "terrain"** beat (which corpus each model saw) — the corpus switcher is its interactive sibling; cross-link when wiring.
- **Next beat →** [`./ADR-02-sft.md`](./ADR-02-sft.md) — Supervised Fine-Tuning turns this base model into an assistant, and is the first method to *spend* the diversity this beat maxed out.
- **Two beats →** [`./ADR-03-dpo.md`](./ADR-03-dpo.md) — DPO adds the preference-margin needle that reads "n/a" here (instruct models = SFT + DPO, not PPO).
