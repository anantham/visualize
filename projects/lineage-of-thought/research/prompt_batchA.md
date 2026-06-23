You are compiling a rigorously fact-checked dataset for a history-of-ideas visualization (a globe + timeline showing how schools of thought influenced each other and spread across the world). Do NOT ask me any clarifying questions — make reasonable scholarly assumptions and proceed. Use web research and cite sources. Where scholars disagree on a date, give the mainstream consensus and set `uncertain: true`.

# Your task

For EACH of the thinkers listed in the ROSTER below, produce one structured Markdown "note" in the EXACT format shown in the EXAMPLE. Separate consecutive notes with a line containing only:

===FILE: <Name>.md===

Output ONLY the notes (each preceded by its `===FILE:` marker). No preamble, no closing summary, no commentary between notes.

# Field rules

- `born` / `died`: integer years. **Negative = BCE** (e.g. Plato `born: -428`). Use best scholarly consensus.
- `uncertain`: `true` if the dates are legendary or strongly contested (e.g. Laozi, the Buddha's traditional vs. revised dating), else `false`.
- `birth_lat` / `birth_lon` and `active_lat` / `active_lon`: decimal degrees of the **birthplace** and of the **place they mainly taught/worked** (these differ often — Aristotle born in Stagira, taught in Athens). This geography is critical: it's where each thinker sits on the globe.
- `region`: one broad band — one of: `Greece`, `Rome`, `India`, `China`, `East Asia`, `Islamic world`, `Jewish`, `Europe`, `Americas`.
- `tradition`: the school (e.g. `Platonism`, `Stoicism`, `Madhyamaka Buddhism`, `Legalism`).
- `wikipedia`: the full URL of their English Wikipedia article (used to fetch a portrait later).
- `portrait`: a direct image URL (Wikimedia Commons) of a portrait/bust if you are confident it is correct, else leave empty `""`.
- `thesis`: one sentence capturing their central claim.
- `key_work`: their most important work (title), or `""`.
- `sources`: 1–3 URLs backing the dates/biography.

# Edge rules (this is what draws the influence lines)

Use Obsidian-style `[[Name]]` wikilinks that reference OTHER thinkers by the SAME name as their note. Put each link under the section that types the relationship:

- `## Influenced by` — people who shaped them (teachers, predecessors they drew on).
- `## Develops` — a tradition/figure they systematically extended (e.g. Mencius develops [[Confucius]]).
- `## Disagreed with` — opponents. Use `::` to name the CRUX of disagreement, then `—` for a note. E.g. `- [[Aristotle]] :: Are universals real? — Forms are immanent, not transcendent`.
- `## Revives` — ONLY for retrieving/reinterpreting a figure from **more than ~150 years earlier** (a deliberate look back across time, not a continuous lineage).
- `## Cruxes` — the big questions they took a position on, as `- [[Question?]] — their stance`. Reuse the SAME crux wording across thinkers who addressed it, so debates link up (e.g. `[[Is the self real?]]`, `[[Are universals real?]]`, `[[Is human nature good?]]`).

You MAY link to thinkers not in this batch if the influence is real (they'll resolve later) — use the person's common English name.

# Idea travel (for the globe animation)

Add a `## Idea travel` section: 2–5 bullet waypoints tracing how their key idea spread in space and time, each as `- <year> — <place>: <what happened>`. Years may be BCE (negative or "300 BCE"). Example for Buddhism: founding in the Gangetic plain, spread to Gandhara, transmission to China, etc.

# EXAMPLE (follow this format EXACTLY)

===FILE: Plato.md===
---
name: Plato
born: -428
died: -348
uncertain: false
birth_place: Athens, Greece
birth_lat: 37.98
birth_lon: 23.73
active_place: Athens, Greece
active_lat: 37.98
active_lon: 23.73
region: Greece
tradition: Platonism
wikipedia: https://en.wikipedia.org/wiki/Plato
portrait: https://upload.wikimedia.org/wikipedia/commons/5/5a/Plato_Silanion_Musei_Capitolini_MC1377.jpg
key_work: The Republic
thesis: The changing world of the senses is a shadow of eternal, unchanging Forms.
sources:
  - https://plato.stanford.edu/entries/plato/
  - https://en.wikipedia.org/wiki/Plato
---

# Plato

Founded the Academy in Athens. Recast Socrates' ethical questioning into a sweeping metaphysics in which true reality consists of eternal Forms, knowable by reason, of which the physical world is only a copy.

## Influenced by
- [[Socrates]] — his teacher; the dialectic and the priority of the soul
- [[Parmenides]] :: Is change real? — unchanging Being behind appearances
- [[Pythagoras]] — number, harmony, and the immortal soul

## Disagreed with
- [[Heraclitus]] :: Is change real? — flux applies only to the sensible world, not the Forms

## Cruxes
- [[Are universals real?]] — yes; the Forms exist independently of particulars

## Idea travel
- -387 — Athens: founds the Academy
- 250 — Rome/Alexandria: Platonism feeds Neoplatonism (Plotinus)
- 529 — Athens: Justinian closes the Academy; Platonist texts carried east into the Syriac/Islamic world
- 1462 — Florence: Ficino's Platonic Academy revives Plato in Renaissance Europe

# ROSTER (Batch A — antiquity)

Greece / Rome: Pythagoras, Heraclitus, Parmenides, Socrates, Plato, Aristotle, Epicurus, Zeno of Citium, Diogenes of Sinope, Plotinus
India: Mahavira, the Buddha (Siddhartha Gautama), Nagarjuna, Patanjali
China: Laozi, Confucius, Mozi, Mencius, Zhuangzi, Xunzi, Han Feizi

Produce all 21 notes now, each preceded by its `===FILE: <Name>.md===` marker, in the exact format above.
