# Composite Periods — LCM made visible

**Project 5.** Scroll-driven explorable: build `sin(kx + φ) + cos(mx)` and watch the
fundamental period emerge as the **LCM** of the parts.

## What it shows

- **Green bracket** — fundamental period T on the combined wave
- **Ghost components** — faint sin and cos with **per-part brackets** (T₁, T₂)
- **φ=0 ghost** — phase compare: slide φ, T pulses unchanged
- **Pink roots** — zero crossings when scaling k
- **Metronome dots** — two rates resync at LCM
- **Guess T** — red dashed bracket vs true green (reveal answer)
- **Dynamic x-window** — widens when T is large
- **Presets** in playground

## Structure — scroll sections

1. Period · 2. Scale k · 3. Phase φ · 4. Two waves · 5. LCM / metronomes · 6. Playground

Sticky journey nav; `#0`–`#5` deep-link. Soft ✓ cues per section (never locked).

## Tech

Pure HTML + canvas, zero dependencies, single file. Works offline.

## Testing hook — `window.__viz`

| Method | Returns / effect |
|---|---|
| `state()` | `{ section, stage, done[], k, phi, k2, addSecond, guessPi, revealGuess, period, xMax }` |
| `setK(v)` / `setPhi(v)` / `setK2(v)` | set parameters |
| `setSecond(on)` / `setGuessPi(v)` / `revealGuess(on)` | affordances |
| `go(i)` | scroll to section `i` and apply its preset |

Invariants: k=1 → `period === 2π`; k=2 alone → `period === π`; sin(2x)+cos(3x)
→ `period === 2π`; phase shift leaves period unchanged.