# Vision

## In one sentence

Make creating explorable, animated explanations — of math, algorithms, physics,
data, and the natural world — as easy as making a matplotlib chart.

## Why

Distill's [Research Debt](https://distill.pub/2017/research-debt) essay names the
problem: ideas accumulate interpretive labor that every new learner must repay
alone, because explanation is treated as an afterthought rather than a
first-class output. The [explorable explanations](https://explorabl.es/)
movement ([explorableexplanations.com](http://explorableexplanations.com/)) is
the answer in spirit: explanations a reader can *play* with until the idea
clicks. But in practice, every great explorable is a bespoke, weeks-long
engineering project. The ideas that most deserve interactive explanation mostly
never get one.

**This project is a tool for paying down research debt**: authoring explorables
with the directness of matplotlib and the expressiveness of manim, producing
output that is alive — interactive, animated, simulated, shareable.

## A field guide to the inspirations

What great output looks like, grouped by what each cluster teaches us:

**Interactive textbooks and concept toys** — the core genre.
[Setosa](http://setosa.io/ev/) (eigenvectors, Markov chains as toys),
[Seeing Theory](http://students.brown.edu/seeing-theory/index.html) (all of
intro probability through interaction),
[D3 Graph Theory](https://d3gt.com/) (graph theory as a hands-on course),
[Hitchman's non-Euclidean geometry](https://mphitchman.com/geometry/chapter-1.html)
(an interactive textbook), and
[Bostock's Visualizing Algorithms](https://bost.ocks.org/mike/algorithms/) —
the canonical essay on visualization as a tool of thought.

**Live simulation underneath the picture.**
[Falstad's circuit simulator](http://www.falstad.com/circuit/e-rtlinverter.html)
and [digital filter applet](http://www.falstad.com/dfilter/) aren't recordings —
a real model runs continuously, and the reader perturbs it. Lesson: the best
explanations are often *simulations with a viewport*, not pre-baked animation.

**The world as data, rendered live.**
[earth.nullschool.net](https://earth.nullschool.net) (global wind on a globe),
[stuffin.space](http://stuffin.space) (every tracked satellite, in real time),
[TheSkyLive's 3D solar system](https://theskylive.com/3dsolarsystem). Real
datasets and celestial mechanics, presented so directly that no prose is needed.

**Scale, time, and zoom as the explanatory device.**
[OneZoom](http://www.onezoom.org/life.html/@Homininae?init=zoom) (the entire
tree of life, navigated by infinite zoom),
[3 Billion Years](http://davidson16807.github.io/3billionyears/#) (deep time as
a scrubbable simulation),
[howmuchis13billioneuros.com](https://howmuchis13billioneuros.com/) (making an
incomprehensible number physical). Sometimes the *navigation itself* — zooming,
scrubbing, comparing — is the explanation.

**Beyond the flat screen.** [hypernom](http://hypernom.com/) — 4D polytopes you
experience rather than read about. A reminder that the ceiling is very high.

**Venues for this kind of work.** [Distill](https://distill.pub/2017/research-debt)
and [epiphany.pub](https://epiphany.pub/post?refId=2684bc94f9fcb9ffe637ebfbeba2af8c797c6ad9a66181026ee4bd3806b6f211)
show people want to *publish* interactive artifacts, not just build them.

## The tools we have, and where they stop

| Tool | What it gets right | Where it stops |
|---|---|---|
| [manim](https://github.com/3b1b/manim) | Beautiful, programmatic, math-native animation — the classic | Renders to video; the viewer can't interact, and the author's iteration loop is slow |
| matplotlib | The "low floor": a chart in three lines, everyone knows it | Static by default; animation and interaction are afterthoughts |
| PyQtGraph | Fast, real-time, genuinely interactive plotting | Desktop-bound, utilitarian, not built for explanation |
| PyGame | Total control over a live render loop | Too low-level: axes, easing, layout all built from scratch |
| [jsgif](https://github.com/antimatter15/jsgif) | Capture a canvas and share it as a GIF, right from the browser | An encoder, not an authoring tool — but it shows how output should travel |

The exemplars above were each hand-built with D3, WebGL, or bespoke JS by people
with both deep domain knowledge and weeks of frontend time. The gap this project
lives in: nothing today combines a low floor, a live interactive output, and
explanation-native primitives.

Our field study of all these sites and the full tooling landscape
([research/examples.md](research/examples.md)) sharpened this to four
properties no existing tool holds simultaneously: **low floor** (a result in
~20 lines), **high aesthetic ceiling by default**, **interactive web output**
(not video), and **a sustaining institution**. Idyll, Apparatus, and Motion
Canvas each had the product roughly right and died of the fourth property.
Distill's hiatus memo names the prize: *"the primary bottleneck is the amount
of effort it takes to produce these articles and the unusual combination of
scientific and design expertise required."* The venue exists; the force
multiplier on production effort doesn't.

## Principles

1. **Code is the authoring format.** An explanation is a program: versionable,
   diffable, reproducible, remixable. No timeline-scrubbing GUI as the source of
   truth.
2. **The output is alive.** The default artifact is something a reader can
   interact with — scrub a parameter, drag a point, step an algorithm, perturb a
   simulation. Video and GIF are *exports* (the jsgif lesson), not the medium.
3. **Simulation is a first-class citizen.** The Falstad lesson: many explanations
   need a live model running underneath (circuits, orbits, populations, climate),
   with the visualization as a viewport into its state.
4. **Scale, time, and zoom are primitives.** Scrubbing through deep time,
   zooming across orders of magnitude, and physical size comparison are
   explanatory devices in their own right (OneZoom, 3 Billion Years,
   13 billion euros) — they should be easy, not heroic.
5. **Fast iteration loop.** Authors see changes immediately, the way PyQtGraph
   and PyGame feel — not after a render queue. The speed of the loop determines
   the quality of the explanation.
6. **Low floor, high ceiling.** A first animation in five lines; full control
   over timing, easing, simulation, and interaction when you outgrow defaults.
7. **Explanation-native primitives.** The vocabulary of teaching: number lines,
   coordinate frames, graphs/trees, grids, vectors, distributions, algorithm
   state, globes and orbits — with animation and interaction built into each.
8. **The document is small; the engine is the heavy asset.** Every great
   simulation site reduces content to a compact declarative payload (a
   netlist, eight orbital elements, a wind grid) hydrated by one shared
   engine — and every interesting state serializes into a URL. Authoring
   should mean writing documents, not programs; reader mode should be author
   mode with chrome stripped.
9. **Built to outlive its toolchain.** Setosa's build needs Node 9 under
   Rosetta; Seeing Theory is frozen on D3 v3; Motion Canvas's site fell off
   DNS. Emit dependency-light, self-contained artifacts so the work survives
   the npm ecosystem that produced it.

## What this is not

- Not a BI/dashboard charting library — plenty of those exist.
- Not a no-code diagramming app — code-first is the point.
- Not a video editor or a slide tool — those produce dead artifacts.

## Proving ground

**Project 1 (chosen): the triangle inequality in 3D.** A webpage where the
visitor places two points in 3D space and watches the inequality hold — and
sees exactly when it becomes equality — as they drag. The first end-to-end
artifact this project ships.

The full backlog lives in [ideas.md](ideas.md): Euler's formula from two
perspectives (the Manhattan-spiral convergence and the helix), Pascal's
triangle as a path-counting DP, periods of composite functions (LCM/GCD),
DSP spinning phasors and radians/sample, and sunlight on a rotating Earth.

Other candidates that would prove the tool generalizes:

1. **Central Limit Theorem demo.** Reproduce the Seeing Theory–style explorable
   in under ~50 lines, with web and GIF export.
2. **A Falstad-style toy.** A tiny live simulation (e.g., an RC circuit or a
   bouncing-ball physics sandbox) where the reader can change parameters while
   it runs.

## Open questions

- **Language and runtime.** Python authoring (meet manim/matplotlib users where
  they are) compiling to an interactive web target? Or web-native from the
  start? The research leans toward "manim inverted": author in code, render to
  interactive web by default, video as the degenerate export. Also: design the
  primitives so an LLM can target them — the Claude-Artifacts wave shows
  non-programmers already want these pages badly enough to prompt for them.
- **Library vs. platform.** The research is decisive that a *journal* is the
  wrong shape (Distill) and a venue without an authoring engine can't
  bootstrap (epiphany.pub). Library first; a gallery as the engine's
  marketing surface later. The unsolved part is sustainability — every tool
  that got the product right died of single-maintainer abandonment.
- **2D first or 3D from day one?** The globe/orbit inspirations pull toward 3D
  (WebGL); the textbook genre is mostly 2D. Projects 1 (Three.js) and 2 (pure
  canvas 2D) suggest both belong behind one viewport abstraction, with the
  renderer matched to the content.
