# Spinning Phasors — frequency as radians per sample

**Project 2.** A pure tone isn't really a sine or a cosine — it's a phasor
`e^{jωt}` spinning on the unit circle, and sine & cosine are its two shadows.
Sample it, and frequency becomes an angle step: **radians per sample**.

## What it shows

- A phasor spinning on the unit circle (counter-clockwise for positive F,
  clockwise for negative).
- Its **sine** shadow scrolling right and **cosine** shadow scrolling down.
- **Sampling**: a strobe captures the phasor every 1/Fs s — pink dots on the
  circle, stems on the waveforms, and a Δθ arc showing the constant per-sample
  angle. The panel shows `Δθ = 2πF/Fs` in radians and in units of π, on a −π…+π
  gauge with Nyquist at the edges.
- **Aliasing**: push F past Fs/2 and a red impostor phasor threads the same
  samples at the wrapped frequency — the **wagon-wheel effect**.
- **DFT bank**: a row of bin phasors, each spinning at k·Fs/N — the detector
  that lights up when your tone matches bin k.

## Structure — 9 stages

Something spinning → The other way (negative F) → The first shadow (sine) → The
second shadow + the name (cosine, e^{jωt}) → Strobe it (sampling) → Frequency as
an angle step (rad/sample) → Break it (aliasing) → **A bank of detectors** (DFT
bins) → Playground (log slider to ±20 kHz, strobe view, DFT bank).

Real-world anchors update live under the sliders (heartbeat, vinyl LP, hummingbird
≈ 50 Hz mains hum, A440…) so the abstract Hz value is always grounded.

## Controls

Frequency slider (linear ±8 Hz in the lessons, logarithmic to ±20 kHz in
playground), "sample it" toggle, strobe-rate slider, "strobe view" (hide the
continuous phasor), time-speed slider, pause. Back/Next navigate stages; `#0`–`#8`
deep-link.

## Tech

Pure `<canvas>` 2D, zero dependencies, single file. Works offline.

## Testing hook — `window.__viz`

| Method | Returns / effect |
|---|---|
| `state()` | `{ stage, taskDone, wide, F, Fs, sampling, strobe, paused, t, phase, radPerSample, wrapped, apparentF, aliased, samples, history, dftBin, visible[] }` |
| `set(id, value)` | set a control by DOM id (`'freq'`, `'fs'`, `'sampling'`, `'strobe'`, `'speed'`) |
| `setF(hz)` / `setFs(v)` | set frequency / sample rate directly |
| `go(i)` | jump to stage `i` |

Invariants: at F=2, Fs=8 → `radPerSample === π/2`, not aliased; at F=7, Fs=8 →
`aliased`, `apparentF === −1`, `wrapped === −π/4`; pause freezes `t`; at F=2,
Fs=8 with sampling → `dftBin === 2`.