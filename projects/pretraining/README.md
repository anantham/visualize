# Pretraining - the model's first world

An explorable bridge between `next-token` and the alignment pages. It teaches that
before a model can be post-trained or aligned, it first learns a base prior from a
specific data mixture.

The page is a single self-contained `index.html`: no build step, no framework, no
external runtime. It uses a sticky canvas and scroll-controlled acts rather than a
large control dashboard.

## Acts

1. **Disclosure** - pick a model and see whether the corpus recipe is inspectable.
2. **Corpus** - category treemap of the disclosed training mixture, or an explicit
   "not disclosed" panel.
3. **Tokenization** - a sentence becomes token IDs.
4. **Training loop** - context -> prediction -> loss -> gradient -> weights.
5. **Compute** - rough dense-transformer FLOPs and H100-equivalent estimate.
6. **Instability** - checkpoints, loss wiggles, run monitoring.
7. **Base model** - the resulting simulator is capable, but not yet an assistant.

## Data Boundaries

The treemaps are category-level teaching views, not exact dataloader
reconstructions. For models with public corpora, categories are rolled up from the
published recipes. For partial/closed models, the page marks uncertainty directly
instead of inventing a detailed corpus.

Initial model set:

- GPT-2 and GPT-2 XL - weights open, WebText described, exact corpus not
  released.
- Pythia 1.4B - Pythia paper plus The Pile.
- Pythia 12B - same Pythia/Pile setup at larger scale.
- OLMo 7B - OLMo paper plus Dolma.
- SmolLM2 1.7B - SmolLM2 technical report.
- Qwen2.5 0.5B and Qwen2.5 7B - weights open, broad scale disclosed, exact
  corpus not public.
- Mistral 7B - weights open, exact pretraining corpus not public.
- Gemma 2 2B, 2B IT, 9B, and 27B - weights open, broad categories disclosed,
  exact mix not public. The IT entry is marked as a post-trained sibling of the
  same base family.
- Llama 3 8B - public token scale with partial corpus disclosure.
- GPT-4o, Claude 3.5 Sonnet, and Gemini 1.5 Pro - specific named opaque API
  models, no weights or full corpus recipe.

Compute estimates use the rough dense transformer rule:

```text
training FLOPs ~= 6 * parameters * tokens
```

The H100-equivalent number assumes a rough sustained 400 TFLOP/s per H100. It is
a scale anchor, not a claim about actual wall-clock training time.

## Testing Hook - `window.__viz`

| Method | Returns / effect |
|---|---|
| `state()` | `{ ready, project, step, mode, model, openness, hasCorpus }` |
| `go(i)` | switch the scroll act |
| `setModel(id)` | select a model |
| `models()` | model metadata shown by the dropdown |
| `corpus()` | current model's displayed corpus categories |
| `estimate()` | current rough FLOPs and H100-year estimate |

Run:

```bash
python3 -m http.server 4173
npm run test:pretraining
```
