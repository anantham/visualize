# Next token — watch a sentence travel through a language model

**Type a sentence (or scrub the prebuilt one) and watch it become tokens, then
vectors, then a running residual-stream vector that each layer amends — until the
final vector is scored against the whole vocabulary to pick the next token.**

A single self-contained `index.html` (~7 MB — the model-derived data is embedded
inline). It teaches, end to end, how input text is transformed on the **residual
stream** of a transformer (`gemma-2-2b`, with `gpt2`/`pythia`/`neox`/`qwen` shown
for tokenizer contrast):

- **The journey** — a scroll-scrubbed overview of the whole pipeline.
- **The deep-dive**, four parts the journey links into:
  - **Part 1 · The sentence**
  - **Part 2 · Text → tokens** (the tokenizer — the five decisions, why *N* pieces)
  - **Part 3 · Tokens → vectors** (the embedding; a 2D PCA explorer)
  - **Part 4 · The machine** (layers amending a running vector → unembed → logits)

This project came over from the `pramana` research repo, where it's the public
explainer for the *isought_whitebox* experiment. It's **live at
[nexttoken.adityaarpitha.com](https://nexttoken.adityaarpitha.com)**.

## Run

No toolchain, but it **must be served** (the lazy-loaded sentence bundles and the
File/fetch paths need an `http://` origin):

```sh
python3 -m http.server 4173
# then open http://127.0.0.1:4173/projects/next-token/
```

Use **`127.0.0.1`**, not `localhost`, if your browser resolves `localhost` to IPv6
(`::1`) — Python's `http.server` binds IPv4 only, so `localhost` can show "site
can't be reached" while `127.0.0.1` works.

The page lazy-loads four sentence bundles (`pg_sent_kathmandu.json`,
`pg_sent_keys.json`, `pg_sent_socrates.json`, `pg_sent_water.json`) by relative
path, so they must sit next to `index.html` (they do).

## Live mode (the Hugging Face Space backend)

Beyond the prebuilt sentences, **Live mode lets you type your own sentence** and
runs it through the model on demand. That compute happens on a free Hugging Face
Docker Space, not in the page:

- **Endpoint:** `https://everythingisrelative-pramana-gemma-live.hf.space`
  (`gemma-2-2b` bf16, CPU-basic). Endpoints used: `/health`, `/tokenize`,
  `/tokenize_demo`, `/embed_query`, `/walkthrough`. CORS is open (`*`).
- **Source of the Space** lives in `pramana` at `isought_whitebox/hf_space/`
  (`app.py`, `Dockerfile`, `requirements.txt`) and is deployed separately to HF —
  it is **not** part of this repo. If Live mode breaks, check the Space is awake
  (`curl …hf.space/health` → `{"ok":true,"model_loaded":true,...}`); HF free-tier
  Spaces sleep when idle and take ~1–2 min to warm.
- **Graceful degradation:** if the Space is down, the static journey + prebuilt
  sentences still work; only the type-your-own path is unavailable.

The backend URL is set by a `SRV` constant near the top of the page's script.
This gallery copy points `SRV` at the Space **always**; pass `?backend=local` to
point it at a local dev backend (`127.0.0.1:8716`) instead. *(The pramana original
keyed off `location.hostname` — changed here so Live mode works when the gallery
is served from localhost.)*

## Provenance / regenerating

This is the **built artifact**, not the source. It's generated in `pramana` by
`isought_whitebox/views/build_playground.py` (which reads a precomputed
model-data pipeline that needs `torch` + the gemma weights). To refresh it: run
that generator in pramana, then copy the resulting `playground.html` →
`index.html` here and re-apply the two edits above (repoint `SRV`, neutralize the
private `experiment.html`/`atlas.html` links). The research pipeline stays in
pramana by design — this repo holds the explorable.

## Verifying changes

Unlike the other gallery projects, this page does **not** expose a `window.__viz`
hook (it predates that convention), so `test.js` drives it via the DOM, network,
and console instead of a state API.

```sh
python3 -m http.server 4173                 # from the repo root
node projects/next-token/test.js            # uses 127.0.0.1 by default
```

`test.js` requires playwright (`npm i -D playwright`) and network (it pings the
HF Space). It asserts: 0 console errors on load; the title + deep-dive Part 1–4
headings; all four `pg_sent_*.json` bundles serve (by relative path) and parse;
the page points `SRV` at the Space and `/health` answers; and — by *design
invariant*, not a tuned threshold — that scrubbing the journey advances through
stages 3→4→5→6 in order, that stage 4 is the residual-stream beat, and that the
stream graphic renders during stage 4 (a negative control confirms this goes red
if it doesn't). A clean run prints `next-token: OK`.

> **Scope:** this is a migration smoke + regression guard, not a correctness
> test. It does *not* verify the interpretability is right — that the tokens,
> embeddings, and residual values shown are the real model's outputs. That ground
> truth lives in pramana's precompute pipeline; visual/pedagogical correctness
> still needs a human eyeball, with nexttoken.adityaarpitha.com as the reference.
> The continuity sweep is adapted from pramana's `transition_scan.js`.
