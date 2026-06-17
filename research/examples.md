# Field study: how the great explorables are built

*Compiled June 2026. Method: four parallel research passes (page-source inspection
via fetch, secondary sources, GitHub repos, papers) over the ~20 inspiration
sites, plus headless-browser screenshots in [screenshots/](screenshots/).
Screenshot caveats: OneZoom is behind a cookie wall, stuffin.space rendered
blank headless, 3 Billion Years was caught mid-load — those three need an
interactive browser session.*

## The one-paragraph conclusion

Reader demand for explorable explanations is proven (Distill articles at 100k+
readers, Seeing Theory's Webby, manim's 87k stars), and the authoring community
exists (explorabl.es still merges submissions). What's missing — stated
explicitly by Distill in its hiatus memo — is not a venue but a **force
multiplier on production effort**: every great explorable studied here was
hand-built by 1–2 unusually skilled people, every reusable layer stops exactly
where the interesting interactivity begins, and nearly every tool that lowered
the barrier is now dead or pivoted away. The opportunity is an engine holding
four properties no existing tool holds simultaneously: **low floor, high
aesthetic ceiling, interactive web output, and a sustaining institution.**

---

## Site capsules

### The textbook genre (Setosa, Seeing Theory, Bostock, D3GT, Hitchman)

- **Setosa / Explained Visually** — drag a vector, watch its image under a
  matrix; eigenvectors found by the reader's hand, prose numbers bound to
  figure state (AngularJS controllers + D3/SVG, one bespoke script per
  article). Duo, 2013–15, open source, **build now requires Node 9 under
  Rosetta** — the canonical toolchain-decay cautionary tale.
- **Seeing Theory** — one pedagogical loop reused ~18 times: *set a
  distribution by dragging bars → simulate (flip ×1 / ×100) → watch empirical
  converge on theoretical*. D3 v3 + jStat, every unit hand-coded. Built by an
  undergrad on a fellowship; won a Webby; officially unmaintained.
- **Bostock, Visualizing Algorithms** — algorithms instrumented to *emit
  state streams*, rendered many ways; click-to-replay with fresh randomness is
  the whole intoraction model and it's enough. Key insight: a well-chosen
  static encoding (the shuffle-bias matrix) can beat animation. 29 inline
  script blocks, solo, 2014.
- **D3 Graph Theory** — the reader draws their own graph; every theorem is
  checked against *the reader's* object. A micro content-engine (shell page +
  content-as-JSON + per-unit app.js) got one student 80% of an authoring
  framework.
- **Hitchman's geometry book** — the only one on a true framework
  (**PreTeXt**: semantic XML → HTML/PDF/print). Solo professor shipped a full
  maintained interactive textbook — but the framework's uniformity means *no*
  concept-toy moments. Frameworks' ceiling is bespoke work's floor.

### Live simulation & the-world-as-data (Falstad ×2, nullschool, stuffin.space, TheSkyLive)

- **Falstad CircuitJS** — a SPICE-class solver (modified nodal analysis)
  whose entire "textbook" is hundreds of tiny text netlists loaded into one
  engine via iframe query flags (`startCircuit=…&hideMenu=true`). Full model
  state compresses into a shareable URL. Two time knobs: model timestep vs.
  animation legibility.
- **Falstad dfilter** — four linked views (frequency response, live spectrum,
  waveform, impulse response) of one coefficient set, *while you hear the
  filtered audio*. The plots are the input devices: drag the response curve,
  drag poles/zeros in the z-plane.
- **earth.nullschool.net** — cron bakes NOAA GRIB2 into small static JSON
  grids; the client is a pure renderer advecting particles through the vector
  field (layered 2D canvases at different update cadences, worker for
  regridding). The URL hash serializes the entire view — every atmospheric
  moment is citable.
- **stuffin.space** — 20k satellites SGP4-propagated in a web worker, posted
  to the GPU as one Float32Array, drawn as point sprites in ~one draw call;
  GPU pick-buffer makes every dot inspectable. Built by an 18-year-old.
  Curated groups ("Iridium-33 collision debris") turn a dataset into story
  beats.
- **TheSkyLive 3D solar system** — closed-form Keplerian models mean time is
  *random-access*: the scene file for a comet is eight orbital elements in
  JSON. Three.js where a scene graph earns its weight (hundreds of objects,
  not 20k).

### Scale, time, and zoom (OneZoom, 3 Billion Years, 13-billion-euros, hypernom)

- **OneZoom** — 2.2M species in one page because the layout is *fractal*:
  self-similar recursion makes zoom both the only navigation and the
  level-of-detail culling. Controller/renderer split; every zoom state is a
  URL (`/@Homininae?init=zoom`). Deep zoom requires coordinate re-basing, not
  one giant scale factor.
- **3 Billion Years** — deep time as a scrubbable axis. The "simulation" is
  honest fakery: pre-rendered paleomap frames interpolated on a Three.js globe
  (custom Mollweide-projection shader). The months went into the *frames*, not
  the engine — content is the bottleneck.
- **howmuchis13billioneuros.com** — Bret Victor's scrubbable-numbers pattern,
  pure: drag any number in the prose, a reactive calculation graph (calculang)
  recomputes the rest. No canvas at all; the prose is the visualization.
- **hypernom** — headset orientation *is* a unit quaternion, i.e. a position
  on the 3-sphere; the SO(3)→S³ double cover stops being a theorem and becomes
  the experience of needing to turn 720° to get home. Bind input streams to
  arbitrary parameter spaces, not just x/y.

### Movement & venues

- **Bret Victor (2011)** named the genre and its taxonomy (reactive documents,
  explorable examples, contextual info); his Tangle library proved reactive
  documents in ~0 KB and has been dead for a decade. The spec has existed for
  15 years; the engine never followed.
- **explorabl.es** — alive, volunteer-run link index; its "make your own"
  tools page is mostly a graveyard. Authors exist; tooling doesn't.
- **Distill (2017–2021)** — validated demand, then shut down with the most
  important sentence in this corpus: *"the primary bottleneck is the amount of
  effort it takes to produce these articles and the unusual combination of
  scientific and design expertise required."* Their verdict: self-publication
  plus better tooling, not journals.
- **epiphany.pub** — venue + embedded code editor, no opinionated explanation
  layer → cold-start death (offline since ~2022). A venue without an authoring
  engine cannot bootstrap.

---

## The six interaction primitives

The complete interaction vocabulary across the textbook genre reduces to six
composable moves (and the simulation genre adds little beyond them):

1. **Drag a handle** — set a continuous parameter or move an object (vectors,
   probability bars, poles/zeros, our triangle points).
2. **Click to add/toggle** — set discrete structure (graph vertices, circuit
   switches, deck of cards).
3. **Run ×N** — a button with a magnitude (flip 1 / flip 100); one-shot vs.
   batch is what makes convergence visible.
4. **Click to replay** — re-run a process with fresh randomness; the minimum
   viable interactivity, often sufficient.
5. **Click to expand** — progressive disclosure (PreTeXt knowls); cheapest
   universally applicable interaction.
6. **Live inline numbers** — prose bound to model state (Setosa, Tangle,
   13-billion-euros); the strongest single effect per unit of authoring cost.

Plus the meta-primitive from the simulation cluster: **any displayed quantity
can be promoted to a control surface** (drag the curve, not a slider beside it).

## Architecture patterns that recur

1. **The document is small; the engine is the heavy asset.** Netlists, filter
   coefficients, TLE lines, eight Keplerian elements, baked JSON wind grids —
   every strong site reduces content to a compact declarative payload hydrated
   by one shared engine. Authoring = writing documents, not programs.
2. **Reader mode = author mode + flags.** The embedded explainer is the full
   tool with chrome stripped (`hideMenu`, `editable`), never a second codebase.
3. **Controller/model split from the renderer**, with an explicit contract
   (typed arrays from a worker, a reactive calc graph, semantic camera
   commands). The render loop stays dumb.
4. **Every interesting state is a URL.** nullschool's hash, OneZoom's zoom
   coordinates, CircuitJS's lz-string circuits. Sharing, tours, citations, and
   remixing all fall out of serializable state.
5. **Time is a first-class control, in two flavors.** Closed-form/analytic
   models scrub freely (random access); stepped simulations expose
   speed/timestep. The time UI should derive from the model type.
6. **Deep scale needs LOD + re-basing.** Fractal layout gives culling for
   free; "infinite" zoom needs local coordinate frames, not a growing scale
   factor.
7. **Match the renderer to the object count** — point sprites for 20k, scene
   graph for hundreds, layered 2D canvas for full-screen fields, SVG for
   dozens. One viewport abstraction, several backends.
8. **Universal inspectability** — hover-readout / pick-buffer / click-to-lock
   should be built into the viewport, not per-demo code.
9. **Survival demands declarative source + dependency-light artifacts.**
   Everything hand-coded against a framework era froze (Setosa/Node 9, Seeing
   Theory/D3 v3, Motion Canvas's site fell off DNS). The survivors compile
   semantic source with a centrally maintained runtime (PreTeXt) or are
   single-file/self-contained.

## The tooling landscape: why nothing won

Four properties; no tool holds all four:

| Property | Held by | Surrendered by |
|---|---|---|
| **Low floor** (respectable result in ~20 lines, no frontend skill) | Streamlit/marimo, Desmos, Apparatus, LLM one-shots | manim, MathBox, Observable, D3 |
| **High aesthetic ceiling by default** | manim, MathBox, Motion Canvas | Streamlit, Desmos, Idyll, LLM one-offs |
| **Interactive web output** | Idyll, Observable, Tangle, Apparatus | the entire manim/Motion Canvas/Revideo lineage (video only) |
| **Sustaining institution** (>5 yrs maintained, real backing) | Observable, Streamlit/Snowflake, marimo/CoreWeave | Idyll, Apparatus, Motion Canvas, MathBox, Tangle, Distill |

Notable post-mortems: **Idyll** (closest prior art — markup for reactive
articles; died with its PhD author, and it lowered the *document* floor while
the *diagram* still had to be hand-written in D3/React). **Motion Canvas**
(best code-to-motion web engine; 18.6k stars; site literally fell off DNS —
stars ≠ sustainability). **Apparatus** (lowest floor ever achieved —
direct-manipulation authoring; author left for a market that pays).
**Observable** (high ceiling, but pivoted to BI/dashboards). **The 2024–26 AI
wave** (text-to-manim, Claude-Artifact explorables) is the strongest demand
signal — non-programmers coaxing explorables out of chatbots — but produces
single-shot, unhosted artifacts with no shared primitives.

**The unclaimed slice:** a code-first library whose primitives are
*explanatory* (scenes, linked representations, reactive parameters, narration
steps), rendering to **interactive web by default with video as a degenerate
case** (manim inverted), with manim-grade aesthetics baked into the defaults,
one-command static export, and design that makes it a natural **compile target
for LLMs**.

## Risks

1. **The Distill bottleneck may apply to the engine itself** — if quality
   requires per-piece design judgment that primitives can't encode, the engine
   yields mediocre explorables at scale. The central bet: opinionated defaults
   (manim's trick: the aesthetic *is* the brand) can carry quality through
   templating.
2. **Single-maintainer death** killed every tool that had the product right
   (Idyll, Apparatus, Motion Canvas). Sustainability needs an economic or
   institutional engine from early on; the audience (teachers, academics) has
   low willingness to pay.
3. **Squeeze from both ends** — funded general-purpose stacks (Observable,
   marimo, Quarto) keep absorbing interactivity from above; improving LLM
   one-shotting erodes the floor advantage from below. The counter to both:
   be the substrate with consistent primitives, hosting, and remixability.

## What this means for visualize

- Projects 1 and 2 accidentally validate pattern 9 (single-file, CDN-only,
  no build step) — keep that discipline.
- Both projects should grow **URL-serialized state** (pattern 4) and
  **direct manipulation on the representation** (drag the phasor itself, drag
  the waveform — not only sliders).
- The first six interaction primitives are the checklist for every new
  project; a future engine should make each a one-liner.
- When an engine emerges from these projects, its shape is dictated by
  pattern 1: a small declarative document per explanation, one maintained
  runtime, reader/author as a flag.
