# CLAUDE.md — orientation for AI coding sessions

This repo builds **explorable explanations** (interactive teaching pages) and the
research/vision toward an authoring engine for them. Start with `README.md`, then
`vision.md` (thesis) and `ideas.md` (backlog). Per-project docs are in each
`projects/*/README.md`.

## Conventions — follow these when adding/editing a project

- **One self-contained `index.html` per project.** No build step, no bundler. CDN
  imports only (Three.js for 3D; everything else is hand-rolled `<canvas>` 2D).
  This dependency-light constraint is deliberate — see the "survives its toolchain"
  finding in `research/examples.md`. Don't introduce npm/build tooling.
- **The staged-document pattern** (projects 2–4): the explanation is a `STAGES`
  array of `{ title, copy, task, reveals, show, enter(), done() }`. Each stage
  reveals one control + one visual, one sentence, one task; the last is a
  playground. Progressive disclosure is the core UX principle — never show
  everything at once.
- **`done()` auto-detects** task completion from state (soft gating; Next glows,
  never locks). **Hash deep-links** (`#0`, `#1`, …) restore stage + preset.
- **Real-world anchors in copy** — tie quantities to lived/bodily experience, not
  bare numbers. The project-4 pivot: practical beats abstract.
- **Always expose a `window.__viz` hook** (`state()`, `go(i)`, setters) so the
  page is drivable headlessly.

## Verifying changes (important)

Every change was checked by **driving the real page with Playwright** and
asserting on `window.__viz.state()`, plus reviewing screenshots — not by eye
alone. Do the same: serve with `python3 -m http.server 4173`, write a short
Playwright script (template in `README.md`) that drives `__viz` and asserts
invariants, run it, and read a screenshot or two. The original test scripts lived
in `/tmp` and were lost on reboot; regenerate them into `projects/*/test.js` if
you touch a project. The `__viz` surface for each project is documented in its
README.

## Factual data → verify it

Anchor numbers (sizes, rainfall, etc.) are fact-checked, not guessed. When adding
factual anchors, verify them (web search, or a gather→verify→synthesize multi-agent
workflow as was done for the rainfall and zoom-ladder data). `data/personal-anchors.md`
is the source of truth for sense-of-scale.

## Don't

- Don't add a framework/build step.
- Don't dump all controls/visuals on one screen — stage them.
- Don't ship factual anchors you haven't checked.
- Don't claim something works without driving it; tests/screenshots over vibes.
