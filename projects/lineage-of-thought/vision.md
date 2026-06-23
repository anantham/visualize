# Lineage of Thought — vision

**Point this at a vault of notes on thinkers and schools of thought, and watch
ideas light up the world: where they were born, who they reached, and how the
center of human thought drifted across the globe over three thousand years.**

It is a *reader* for an Obsidian vault and an *atlas* of intellectual history at
once. You write the notes (one per thinker, Obsidian-style `[[links]]` for
influence, disagreement, revival); the tool turns that web into something you
can fly through in space and scrub through in time.

---

## The hero view is a globe, not a chart

Most history-of-ideas visualizations are timelines — flat, Eurocentric ribbons.
The thing that's missing from a ribbon is **place**. Ideas don't happen on a
number line; they happen *somewhere*, and their whole drama is how they *move* —
Buddhism walking from the Gangetic plain to Gandhara to Chang'an; Aristotle
traveling Athens → Baghdad → Córdoba → Paris over a thousand years; Vedanta
crossing to Chicago in 1893.

So the default view is a **3D globe**.

- **Scrub time, and ideas move in space.** A time playhead (scroll or drag)
  sweeps forward. As it passes a thinker, their marker ignites at their location;
  as their idea is taken up elsewhere, a **great-circle arc** grows from teacher
  to student, from source to revival. You are watching thought propagate across
  the map, in order, at the speed you choose.
- **The globe re-centers on the era's center of gravity.** At any moment in time
  there is a *center of mass* of intellectual activity. In −400 it sits between
  Athens, the Gangetic plain, and the state of Lu. By 800 CE it is Baghdad. By
  1650, Western Europe. By 1900, the North Atlantic. The camera drifts to follow
  it, so the view is always centered on "where the action is" — and you *feel*
  hegemony arrive and pass.
- **Zoom sets temporal granularity.** Far out, you see only the giants and the
  millennium. Zoom in and the century fills in around a thinker — their
  contemporaries surface, the minor figures appear, the dense local arguments
  resolve. (This is the level-of-detail idea from the timeline view, mapped onto
  the globe.)

The flat **timeline ribbon** (already built — see the MVP) doesn't go away: it
becomes the globe's twin. Same data, same selection, same clock. The ribbon is
for reading the *order and overlap* of lives; the globe is for feeling their
*place and spread*. Selecting a thinker in one highlights them in the other.

---

## The center-of-gravity layer

A deliberate, separate meta-layer answers a question the per-thinker notes can't:
**where was the center of culture, and when?** New York now; San Francisco rising;
London before that; Baghdad, Chang'an, Athens, Alexandria, Florence, Vienna,
Paris before *that*. Some eras have one dominant center; some are genuinely
multipolar (the Axial Age: Greece, India, China all igniting at once). That
ebb between **hegemony and diversity** is itself one of the most interesting
stories in the data.

This lives in its own file — a `centers-of-gravity.md` timeline of
`era → place(s) → lat/lon → why` — authored and fact-checked like any other
anchor data in this repo. The globe reads it to know where to point the camera
over time, and renders the dominant center as a soft halo whose size tracks how
concentrated (vs. distributed) thought was in that era.

---

## Selecting a thinker: the card

Click any marker (on globe or ribbon) and it opens into a **card**: a portrait,
their dates and place, their one-line thesis, and the full rendered content of
their note — with the `[[links]]` clickable so you can walk the lineage by hand.
The card is the bridge back to the vault: what you see is what you wrote.

---

## What makes it more than a map of dots

The edges. Every line on the globe carries meaning, colored by kind:

- **influence / develops** — a tradition flowing forward in time and across space.
- **disagreement** — colored differently, tagged with the *crux* of the dispute
  (`Are universals real?`, `Is the self real?`, `Is human nature good?`).
- **revival** — the dramatic one: a thinker reaching *back* across centuries to
  retrieve a forgotten figure (Ambedkar → the Buddha, ~2400 years; Nietzsche →
  Heraclitus; Zhu Xi → Confucius). On a globe these are long arcs that leap both
  distance and time.
- **idea-travel routes** — per-idea waypoints (place + year) tracing the physical
  spread of a school, so the animation isn't guessed from birthplaces but
  follows the actual transmission path.

And the **cruxes** are first-class: filter to one question and watch a single
debate light up across civilizations and millennia — *Is the self real?* drawn
between the Buddha (no), Mahāvīra (yes), Śaṅkara (yes), and Hume (no), across
India and Europe and 2,400 years.

---

## Data model

Everything is plain Markdown in a vault, parsed live (File System Access API):

- **Per-thinker note** — frontmatter (`born`, `died`, `birth_lat/lon`,
  `active_lat/lon`, `region`, `tradition`, `portrait`, `thesis`, `key_work`) +
  typed sections (`## Influenced by`, `## Develops`, `## Disagreed with` with
  `::` cruxes, `## Revives`, `## Cruxes`, `## Idea travel`). The geography is the
  new, globe-critical part.
- **Cruxes** emerge from the notes (shared `[[Question?]]` links), no separate file.
- **`centers-of-gravity.md`** — the era→place hegemony timeline.

The seed vault (`vault-sample/`) is being enriched by a cross-verified
multi-model **Deep Research** pass (ChatGPT / Grok / Gemini driven headlessly in
their logged-in web UIs — see `research/`), producing geography + idea-travel
routes for a canonical ~50-thinker core.

---

## Tech & reuse (no build step, ever)

- **Globe** — hand-rolled **Three.js from a CDN** (the same way `triangle-inequality`
  and `earth-seasons` already do it in this repo). A sphere with an Earth texture
  (or a hex-polygon coastline mesh), `lat/lon → 3D` placement, animated
  great-circle arcs, and `pointOfView({lat, lon, altitude})`-style camera drift.
- **Borrowed math** — the portfolio's `src/lib/journey.ts` is a pure-JS,
  React-free state machine: `buildTimeline(events)`, `getState(progress) →
  {lat, lng, traveling, activeEvent}`, longitude-wrap interpolation, and the
  camera altitude/zoom choreography (`JourneyExperience.tsx` ~L388–444) and arc
  growth (~L279–350). We port that logic; we do **not** pull in
  react-globe.gl / Cesium / Next.js (build-bound, incompatible with this repo).
- **Same conventions** as the rest of `visualize`: one self-contained `index.html`,
  CDN-only, a `window.__viz` hook, verified by driving the real page with
  Playwright.

---

## Staged plan

1. **Timeline ribbon** *(built)* — swimlanes by region, lifespan ribbons, typed
   colored edges, span-scaled revival arcs, hover ego-network, click-to-card,
   vault loader, `window.__viz`. The data spine.
2. **Globe view** — Three.js sphere, markers from `active_lat/lon`, great-circle
   influence/revival arcs, a shared time playhead with the ribbon.
3. **Center of gravity** — `centers-of-gravity.md`, camera drift, the hegemony
   halo, the multipolar-vs-dominant read.
4. **Cards** — portrait + full note + walkable `[[links]]`.
5. **Idea-travel animation** — arcs follow real transmission waypoints, not just
   birthplaces; play/scrub propagation.
6. **Polish** — crux filter across time, search, deep-links, presets.

---

## Open questions

- **Center of gravity — measured or authored?** Hand-author the era→place
  timeline (curated, defensible), or compute it from the density of active
  thinkers' coordinates per time-slice (emergent, but only as good/representative
  as the vault)? Probably author first, then show the computed version as a check.
- **Birthplace vs. active place vs. the idea's path.** A marker has to sit
  *somewhere*; the truest answer is that ideas move, so the long-term right model
  is the `## Idea travel` route, with birthplace as the t=0 fallback.
- **The Eurocentrism trap.** Coverage is a function of what's in the vault. The
  globe makes gaps visible (an empty continent is an honest signal) — but we
  should seed deliberately broadly (the cross-verified research pass is scoped to
  do exactly this) and never let the *tool* imply the *map* is complete.
- **Time is not uniform.** Antiquity is sparse and fuzzy-dated; the last 200 years
  are dense. Linear time crushes the modern era into a smear. Log-time? A
  warpable axis? (The ribbon already fades uncertain dates; the globe needs an
  answer too.)
