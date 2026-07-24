# Alignment as Tradeoff Machines — the Method Series

**Interactive build:** open [`index.html`](./index.html), or serve the repo and visit
`/projects/alignment/methods/`. The page turns the ADR framework into a shared
seven-needle workbench: one overview table plus one interactive beat per method.

> **Thesis.** There is no single knob called "alignment." Every alignment method is a
> *tradeoff machine*: you feed it one particular **feedback signal**, it **buys** you a
> few specific properties, it **costs** you others, and it has one characteristic
> **failure mode** that falls out of the exact signal you chose. Line the methods up
> side by side and the pattern is unmistakable — *every method moves the same needles in
> a different direction.* The method is the shape of that movement.

Each page in this series takes one method and runs it through the same four-part
grammar, then reads out the same shared dashboard of seven needles. The point of the
series is not to crown a winner. It is to make the *shape of each tradeoff* legible, so
that "we aligned the model" stops sounding like one thing.

---

## The grammar — every method, four beats

Read every ADR in this series as the same sentence with different nouns:

| Beat | Question it answers |
|------|--------------------|
| **Signal** | What feedback source are we optimizing against? (a corpus, human demos, A≻B pairs, a reward model, a constitution + AI judge, a unit-test checker, a refusal direction) |
| **Buys** | Which needles go **up**, and *why does this signal specifically* move them? |
| **Costs** | Which needles go **down** — the price baked into the same signal? |
| **Failure** | The one characteristic way this method breaks — always a *direct consequence* of what the signal can and cannot see. |

The signal is upstream of everything. The buys, the costs, and the failure are all just
the signal viewed from different angles.

> ### The core lesson
> **No method aligns the model in the grand sense.** Each aligns it to a *particular
> feedback source* with a *particular failure mode*. "Aligned" is always aligned-*to-what*,
> and the failure is always the gap between that feedback source and what we actually
> wanted. Choosing a method is choosing which gap you can live with.

---

## The shared dashboard — the 7 needles

Every method is scored on the same seven axes so the rows are directly comparable. Each
needle reads **↑↑ / ↑ / ≈ / ↓ / ↓↓ / n/a / off-scale** (strong up · up · neutral · down ·
strong down · axis absent · not on the shared ruler). The interactive build treats **n/a**
and **≈** differently: `n/a` means the method has no machinery for that axis; `≈` means the
machinery exists but does not broadly move the needle.

| Needle | What it measures |
|--------|------------------|
| **usefulness** | Helpfulness / task capability the method adds to the assistant. |
| **diversity** | Breadth of the output distribution — range of voices, answers, and phrasings (entropy). |
| **safety** | Refusal of harmful requests / harmlessness. |
| **pref-margin** | How wide a gap the method opens between preferred and dispreferred outputs — i.e., how directly it *is* a preference objective. |
| **OOD** | Robustness and generalization *outside* the training distribution. |
| **compute** | Training cost / resources the stage consumes. |
| **verifier** | Quality of the feedback source itself — the signal that scores outputs, from raw likelihood → soft reward model → ground-truth checker. |

---

## The MASTER NEEDLE TABLE

Rows = the 7 methods, columns = the 7 needles. Read across a row to see one method's
whole tradeoff shape; read down a column to see how differently the methods treat the
same axis. **Every row is different — that is the entire argument.**

| Method | usefulness | diversity | safety | pref-margin | OOD | compute | verifier |
|--------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **01 · Pretraining / Base Model** | ↑ | ↑↑ | ↓↓ | n/a | ↑↑ | off-scale | ↓↓ |
| **02 · SFT / Demonstrations** | ↑↑ | ↓ | ↑ | n/a | ↓ | ↑ | n/a |
| **03 · Preferences / DPO** | ↑ | ↓ | ↑ | ↑↑ | ↓ | ↑ | ↓ |
| **04 · RLHF / PPO** | ↑↑ | ↓ | ↑ | ↑↑ | ↑ | ↑↑ | ↑ |
| **05 · Constitutional AI / RLAIF** | ↑ | ↓ | ↑↑ | ↑ | ≈ | ↑↑ | ↑ |
| **06 · RLVR / GRPO** | ↑↑ | ↓↓ | ≈ | n/a | ↑/↓ ⃰ | ↑↑ | ↑↑ |
| **07 · Safety / Refusal Direction** | ↓ | ≈ | ↑↑ | ↑ | ↓↓ | ≈ | ↓ |

**Legend:** ↑↑ strong gain · ↑ gain · ≈ neutral/no broad movement · n/a axis absent · ↓ cost · ↓↓ strong cost · off-scale not on the post-training cost ruler.
⃰ **RLVR · OOD is a split cell**: **↑** on transfer of *reasoning* ability, **↓** on *test-shape overfit* — the only needle in the table that points both ways at once (see reconcile note 1).

What the columns reveal at a glance:
- **verifier** climbs from ↓↓ (pretraining's likelihood-only) up to ↑↑ (RLVR's ground-truth checker) — this is the through-line of the whole series: *better feedback signal = stronger, harder-to-hack verifier.*
- **diversity** is negative for almost everything past the base model — alignment is, structurally, distribution-narrowing. The rows are marginal moves, so DPO/PPO are `↓` here rather than re-charging SFT's already-counted collapse as `↓↓`.
- **safety** is only the *target* needle (↑↑) for the two methods built for it (CAI, Refusal); everyone else moves it as a side effect or not at all.
- **pref-margin** is ↑↑ exactly for the two methods that literally optimize a preference gap (DPO, PPO) — and undefined (`n/a`) for every method that has no preference signal.

---

## Method → one-liner → demonstrable tier → build status

The **demonstrable tier** answers "how much of this page can we actually *show* at
0.5B?" — 🟢 measured/validated mechanism · 🟡 partial (a real core + cite-only, illustrative, or simulated pieces) ·
🔵 cite-only (frontier-scale, shown as a labeled external result, never faked as ours).

| # | Method | One-liner | Tier | Build status |
|---|--------|-----------|:----:|--------------|
| 01 | **Pretraining / Base Model** | Corpus next-token likelihood → broad capability + every possible voice, but no assistant, no stable "should", no safety, prior-biased → unsteerable completions that mirror whoever wrote the corpus. | 🟡 | Prior-divergence terrain built + validated at 0.5B; the current corpus switcher is illustrative text, not real generations. "Different corpora" is continued-pretrain, not from-scratch; the compute cost is off-scale/cite-only and never paid in the demo. |
| 02 | **SFT / Demonstrations** | Imitating ideal answers buys assistant format + helpfulness + instruction-following; costs judgment (style-only, capped at the demonstrator); fails OOD as confident, well-formatted, wrong. | 🟡 | A completed 400-step SmolLM2-360M run and paired base-vs-SFT generations are now in `../empirical/bakes/`. The current demo-count dial remains illustrative because intermediate checkpoint generations are not wired. |
| 03 | **Preferences / DPO** | "A ≻ B" pairs → cheap, stable alignment (no reward model, no rollouts) → offline-bounded and inherits rater taste; the objective constrains a relative margin, not either absolute likelihood in isolation. | 🟢 / 🟡 | A measured 24-step fixed-probe run widened summed margin **−16.27 → +9.70** by raising chosen log p **−62.80 → −50.52** and lowering rejected **−46.54 → −60.22**. The often-cited both-likelihoods-sink path was **not observed** here; DPO-specific diversity still needs measurement. |
| 04 | **RLHF / PPO** | Human-preference reward model + online PPO → explores beyond static data & wins real preference gains → costs 4 live models, instability, a KL leash → failure: over-optimize the proxy so reward climbs while true quality, diversity & personality collapse. | 🟡 | Refusal is wired from real Qwen2.5-0.5B measurements; the reward-vs-KL overoptimization curve is 🔵 simulated (matched to Gao et al. 2022), and PPO-specific diversity/output snapshots are illustrative. |
| 05 | **Constitutional AI / RLAIF** | Written rules + AI-judged critique/preferences → scales feedback & makes values explicit/swappable → bakes contested values + judge bias into the loop → where the constitution is silent the judge fills the gap arbitrarily and reinforces its own blind spots. | 🟡 / 🔵 | The counterbalanced 0.5B matrix did **not** show constitution-sensitive judging: position A won **201/240**, with zero constitution-driven majority flips. This is a measured judge-bias failure; a successful trained CAI checkpoint remains cite-only. |
| 06 | **RLVR / GRPO** | Unit tests / answer keys / proof checkers → a hard reward on the checkable island → only exists where correctness is decidable, can produce zero-gradient all-wrong groups, invites test-shape exploitation, and is silent on wisdom. | 🟡 / 🔵 | The first exact-integer run produced all-zero rewards because answers were clipped; a calibrated multiple-choice pilot produced reward variance and gradients, but its **22.5% → 27.5%** held-out change was option-position confounded. A position-balanced 48-step confirmation is prepared but not yet completed. Frontier reasoning bootstrap remains cite-only. |
| 07 | **Safety / Refusal Direction** | Harmlessness preference → blocks obvious harmful compliance → a shallow, over-refusing, *removable* fence → one linear direction jailbreaks one way and over-refuses the other. | 🟢 / 🟡 | A seven-coefficient Qwen2.5-0.5B sweep is synced at `../empirical/bakes/refusal_sweep.json` for three harmful and three benign prompts. The UI compresses it to three states and redacts harmful procedural output. Closed-API defense-in-depth remains cite-only. |

---

## ADR index

The seven per-method decision records, in canonical order (each follows the
signal → buys → costs → failure grammar and reports the seven-needle dashboard):

1. [ADR-01 · Pretraining / Base Model](./ADR-01-pretraining.md)
2. [ADR-02 · SFT / Demonstrations](./ADR-02-sft.md)
3. [ADR-03 · Preferences / DPO](./ADR-03-dpo.md)
4. [ADR-04 · RLHF / PPO](./ADR-04-rlhf-ppo.md)
5. [ADR-05 · Constitutional AI / RLAIF](./ADR-05-constitutional-rlaif.md)
6. [ADR-06 · RLVR / GRPO (verifiable reward)](./ADR-06-rlvr-grpo.md)
7. [ADR-07 · Safety / Refusal Direction](./ADR-07-safety-refusal.md)

---

## Reconcile — consistency decisions across the 7 ADRs

These are the scale decisions now applied to the interactive build and mirrored in the ADRs.

1. **Split-direction cell has no convention.** RLVR's OOD is `↑ reasoning / ↓ test-shape
   overfit` — a genuine two-way cell, unlike every other single-arrow entry. Either adopt
   an explicit split notation (`↑/↓`) documented in the legend (done here provisionally),
   or pick the net direction. Right now it's the lone exception.

2. **Resolved in the interactive build: `n/a` vs `≈`.** Pretraining/SFT/RLVR
   pref-margin is now `n/a` because the axis is absent; Safety's diversity and compute are
   `≈` because the axis exists and does not broadly move.

3. **Resolved in the interactive build: baseline row vs marginal rows.** Pretraining is a
   baseline-state row; methods 02-07 are marginal moves. This is why DPO/PPO diversity are
   `↓` rather than `↓↓`: they add narrowing, but SFT's earlier collapse is not charged twice.

4. **Resolved in the interactive build: compute ruler.** Compute is the marginal cost of the
   post-training stage. Pretraining is flagged `off-scale` rather than plotted as if its
   frontier-scale cost were comparable to PPO.

5. **Resolved in the interactive build: weak verifier vs no verifier.** SFT's verifier is
   `n/a` because no verifier is in the loop; DPO's static offline preference set is `↓`;
   pretraining's likelihood-only verifier stays `↓↓`.

6. **Data status is tracked separately.** The master needle table says what a method does;
   [`DATA_STATUS.md`](./DATA_STATUS.md) says which parts are measured, illustrative, simulated,
   or missing. Keeping those scales separate is the main anti-hype rule for this page.
