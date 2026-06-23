# visualize

**Making explorable, interactive explanations as easy to author as a matplotlib
chart — with the expressiveness of manim and output that's alive.**

This repo is part design notebook, part working gallery. It holds a small set of
self-contained interactive explainers ("explorables") plus the research and
vision behind a longer-term goal: an authoring engine for this kind of work. See
[`vision.md`](vision.md) for the full thesis and [`ideas.md`](ideas.md) for the
backlog.

## The explorables

Seven are built. Each is a **single self-contained `index.html`** — no build step,
no install. Three use pure `<canvas>` 2D; one uses Three.js from a CDN. Open any
of them directly in a browser, or serve the repo (below) and visit the path.

| Project | Teaches | Tech |
|---|---|---|
| [`projects/triangle-inequality/`](projects/triangle-inequality/) | the triangle inequality \|AB\| ≤ \|AO\| + \|OB\|, by dragging points in 3D | Three.js (CDN) |
| [`projects/spinning-phasors/`](projects/spinning-phasors/) | frequency as **radians/sample** — a tone is a spinning phasor, sine & cosine are its shadows, aliasing is the wagon-wheel effect | canvas 2D |
| [`projects/pascals-paths/`](projects/pascals-paths/) | nCk as path-counting in Pascal's triangle, and why it's a dynamic-programming problem | canvas 2D |
| [`projects/sense-of-scale/`](projects/sense-of-scale/) | scope insensitivity — big/small numbers made felt via race, zoom, crowds, rings, pour & rain views | canvas 2D |
| [`projects/composite-periods/`](projects/composite-periods/) | periods & LCM/GCD of composite functions — waves lining up again | canvas 2D |
| [`projects/eulers-formula/`](projects/eulers-formula/) | e^iθ via Manhattan spiral + helix shadows | canvas 2D |
| [`projects/earth-seasons/`](projects/earth-seasons/) | sunlight, axial tilt, seasons on a 3D globe | Three.js (CDN) |

Each project folder has its own `README.md` with the concept, controls, stage
list, and testing-hook API.

## Running

No toolchain. Two options:

1. **Open the file** — double-click any `projects/*/index.html`. (Three.js and
   ES-module import maps load from a CDN, so the triangle project needs a network
   connection; the canvas projects work fully offline.)
2. **Serve the repo** (needed if a browser blocks `file://` module imports):
   ```sh
   python3 -m http.server 4173
   ```
   then visit e.g. `http://localhost:4173/projects/sense-of-scale/`.

## The shared pattern (read this before extending)

Projects 2–4 (`spinning-phasors`, `pascals-paths`, `sense-of-scale`) converged on
one architecture — the seed of the eventual "engine". If you build a fifth, copy
it:

- **A staged declarative document.** The explanation is a `STAGES` array of
  plain objects: `{ title, copy, task, reveals, show, enter(), done() }`. Each
  stage reveals **one new control** and **one new visual element**, has **one
  sentence** of copy and **one task**. The last stage is a free "playground". This
  is progressive disclosure — the antidote to dumping everything on screen at once.
- **Soft task gating.** `done()` auto-detects completion from state; the Next
  button glows but is never locked.
- **Hash deep-links.** `#0`, `#1`, … restore a stage (and its preset). Every
  interesting state should be a URL.
- **Real-world anchors.** Copy ties abstract quantities to lived experience
  (a heartbeat, a scooty tank, a flood) rather than bare numbers.
- **A `window.__viz` test hook.** Every project exposes a small imperative API
  (`state()`, `go(i)`, setters) so a headless browser can drive it and assert on
  state. See each project's README for its surface.
- **Single file, CDN-only, no build.** Deliberate: our [research](research/examples.md)
  found that every great explorable that depended on a build/framework rotted
  (Setosa needs Node 9 under Rosetta; Seeing Theory is frozen on D3 v3). Staying
  dependency-light is how the work survives.

## Verifying changes

Each explorable was developed against a Playwright script that loads the page,
drives it through `window.__viz`, and asserts on `state()` (e.g. "dragging A
keeps slack ≥ 0", "F=7, Fs=8 aliases to −1 Hz", "something is on screen at all 171
zoom levels"). **Those scripts lived in `/tmp` and were lost when the machine
rebooted.** The hooks they used are still in place and documented per project, so
the suites can be regenerated. A good home for them would be `projects/*/test.js`.

Minimal shape of such a script:

```js
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on('pageerror', (e) => console.log('PAGE ERROR:', e.message));
  await page.goto('http://localhost:4173/projects/spinning-phasors/');
  await page.evaluate(() => window.__viz.set('freq', 2));      // drive it
  const s = await page.evaluate(() => window.__viz.state());    // read state
  console.assert(Math.abs(s.radPerSample - Math.PI / 2) < 1e-3);
  await page.screenshot({ path: 'out.png' });
  await browser.close();
})();
```

## Repository map

```
vision.md                  the thesis: the gap, the principles, open questions
ideas.md                   the backlog (7 ideas; 4 built) with design notes
README.md                  you are here
CLAUDE.md                  orientation for AI coding sessions
data/
  personal-anchors.md      the sense-of-scale anchor collection (fact-checked)
research/
  examples.md              field study of ~20 exemplar sites + the tooling landscape
  screenshots/             16 reference captures of the inspiration sites
projects/
  triangle-inequality/     project 1 (Three.js)
  spinning-phasors/        project 2 (canvas)
  pascals-paths/           project 3 (canvas)
  sense-of-scale/          project 4 (canvas) — six view engines
```

## Status & next

Built: projects 1–7 (see table). Backlog highlights in `ideas.md`: sense-of-scale
v2 (custom anchors, mileage, annual rainfall strip), phasors DFT bank extension,
and re-anchoring abstract sense-of-scale categories in the bodily style of pour & rain.
