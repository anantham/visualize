# Lineage of Thought

**Point it at a vault of notes on thinkers and schools of thought, and see who
shaped whom — across time and (soon) across the globe.**

A self-contained `index.html` (canvas-2D, Three.js to come, no build step) that
parses an Obsidian-style vault of one-note-per-thinker and renders the influence
web as a zoomable **timeline**: civilization swimlanes, lifespan ribbons, typed
colored edges, and dramatic span-scaled **revival arcs** (Ambedkar → the Buddha,
~2,400 years). See [`vision.md`](vision.md) for where this is going (a globe where
ideas physically travel as you scrub time, re-centering on each era's cultural
center of gravity).

## Run

No toolchain. Serve the repo and open the page (the File System Access API and
the bundled seed both need an `http://` origin):

```sh
python3 -m http.server 4173
# then open http://localhost:4173/projects/lineage-of-thought/
```

It loads the bundled **seed vault** (`vault-sample/`) on start. Click **Open
vault…** to point it at your own Obsidian folder (Chromium browsers — Chrome,
Edge, Brave), or drag a folder onto the page.

## Controls

- **drag** — pan · **scroll** — zoom the time axis · **hover** — focus a thinker
  (dims others, lights up their influences + contemporaries) · **click** — open
  the side card · **Fit** / **+ / –** — zoom · **search** — jump to a thinker ·
  legend edge-types are **click-to-filter**.

## The vault note convention

One Markdown file per thinker. **Frontmatter** carries the facts; **section
headers type the links**; `[[wikilinks]]` connect thinkers; `::` names a crux.

```markdown
---
name: Plato
born: -428            # year; negative = BCE
died: -348
uncertain: false     # true for legendary/contested dates → faded ribbon ends
birth_lat: 37.98     # geography (for the globe): birthplace …
birth_lon: 23.73
active_lat: 37.98    # … and where they mainly taught/worked
active_lon: 23.73
region: Greece       # → swimlane
tradition: Platonism # → node color
portrait: https://…  # optional, for the card
thesis: The sensible world is a shadow of eternal Forms.
---

# Plato

Founded the Academy. …

## Influenced by
- [[Socrates]] — the dialectic
- [[Parmenides]] :: Is change real? — unchanging Being behind appearances

## Disagreed with
- [[Sophists]] :: Is truth relative? — no

## Develops          # systematic extension of a tradition
- [[Pythagoras]] — number and the immortal soul

## Revives           # retrieval of a figure >150 years earlier (long arc)
- (e.g. on an Ambedkar note: [[Buddha]])

## Cruxes            # positions on shared questions; reuse wording to link debates
- [[Are universals real?]] — yes; Forms exist apart from particulars

## Idea travel       # waypoints for the globe animation
- -387 — Athens: founds the Academy
- 1462 — Florence: Ficino's Platonic Academy revives him
```

**Edge types** (color-coded, filterable): `influence` (Influenced by / Teacher),
`derivation` (Develops / Derives from / Builds on), `disagreement` (Disagreed
with / Critiques / Rejects / Opposes), `revival` (Revives / Reinterprets).
Direction: under these headers the *linked* thinker is the source and the *note
owner* is the target, except `Influence on` / `Students` which reverse it.

## `window.__viz` (test/automation hook)

```js
__viz.state()              // {loaded, source, thinkers, edges, regions, selected, hovered, filters, view}
__viz.data()               // {thinkers:[{id,born,died,region,tradition,importance,…}], edges:[{source,target,type,crux,gap}]}
__viz.get(id)              // full parsed thinker record
__viz.select(id)           // open the card for a thinker
__viz.go(id)               // select + center the view on them
__viz.hover(id)            // trigger the ego-network highlight
__viz.contemporariesOf(id) // ids whose lifespans overlap
__viz.fit() / setZoom(px) / centerYear(y) / setFilter(type,on) / openVault()
```

Verify changes by serving the page and driving `__viz` with Playwright (see
[`test.js`](test.js)); assert on parsed dates/edges/contemporaries and screenshot.

## Data: seed + multi-model research

`vault-sample/` is a hand-curated, fact-checked seed (21 thinkers across Greece /
India / China / Europe). It's being enriched by a **cross-verified Deep Research
pass** that drives ChatGPT / Gemini / Grok in their logged-in web UIs (see
`~/Documents/Ongoing Local/AFFORDANCES.md`), all researching the same roster so
dates and coordinates can be merged and disagreements flagged:

```
research/
  prompt_batchA.md     the research prompt (emits notes in this repo's convention)
  deep_research.py     drive one provider's Deep Research headless → out/<provider>_batchA.md
  gemini_login.py      one-time helper to sign a Gemini account into the browser profile
  inspect_ui.py        dump a chat UI's controls (used to find the Deep Research selectors)
  merge_research.py    parse all provider outputs → clean cross-verified notes + a conflicts report
  out/                 raw provider outputs + logs
→ vault-research/      merged, cross-verified notes (+ _conflicts.md)
```

Run a provider: `uv run --with playwright research/deep_research.py --provider
chatgpt --prompt-file research/prompt_batchA.md --output research/out/chatgpt_batchA.md
--mode deep`. Then merge: `uv run research/merge_research.py`.

> Note: the web UIs render Markdown to HTML, so extracted text loses the literal
> `---`/`#`/`-` syntax — `merge_research.py` is tolerant of that (the `===FILE:`
> markers, `key: value` fields, `[[links]]` and `::` cruxes all survive) and
> rebuilds clean notes.

## Status

Built: the timeline view (this `index.html`), the seed vault, and the research
pipeline. Next (see `vision.md`): the **globe** view — a Three.js sphere where
markers sit at each thinker's coordinates, influence/revival arcs are
great-circles, and a shared time playhead drifts the camera to the era's center
of gravity.
