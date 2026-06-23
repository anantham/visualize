# Euler's Formula — spiral & shadows

**Project 6.** Two perspectives on **e^iθ**: Taylor partial sums as a
right-angled spiral in the complex plane, and the same motion as a helix whose
projections are sine, cosine, and the unit circle.

## What it shows

- **Spiral view:** 1 + iθ + (iθ)²/2! + … walks Manhattan-style toward e^iθ on
  the unit circle; path length grows like e^θ while straight-line distance stays 1.
- **Helix view:** cos θ, θ, sin θ flattened to three 2D projections (links to
  [spinning phasors](../spinning-phasors/) for the continuous phasor picture).
- Zoom into the spiral's eye to see convergence.

## Structure — 7 stages

The unit circle → First step: 1 + iθ → The Manhattan spiral → Walked vs reached →
Helix — the circle view → Three shadows → **Playground**.

## Controls

θ slider, +1 term button, zoom slider, circle / sine / cosine projection toggles.
Back/Next navigate; `#0`–`#6` deep-link.

## Tech

Pure `<canvas>` 2D, zero dependencies, single file. Works offline. Helix is drawn
as 2D projections (not Three.js) to keep the file self-contained.

## Testing hook — `window.__viz`

| Method | Returns / effect |
|---|---|
| `state()` | `{ stage, taskDone, theta, terms, zoom, view }` |
| `setTheta(t)` | set θ directly |
| `stepTerm()` | add one Taylor term |
| `go(i)` | jump to stage `i` |

Invariants: θ > 0.8 completes stage 0; six terms completes the spiral stage;
visiting all three projection buttons completes the shadows stage.