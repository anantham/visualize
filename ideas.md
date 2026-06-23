# Ideas backlog

Concrete visualizations to build. Each entry: the concept, the visual, what the
visitor can play with. (Items marked *interpretation* are my reading of the
original note — confirm or correct.)

## 1. Triangle inequality in 3D — **PROJECT 1** ✅ built: [projects/triangle-inequality/](projects/triangle-inequality/index.html)

> You choose 2 points in 3D and see how the inequality is maintained.

The first end-to-end build: a webpage that lets a visitor *really play with*
the triangle inequality.

- **The visual:** two draggable points in 3D space (plus the origin, or a third
  draggable point), with the three sides drawn and their lengths labeled live.
  Show |a| + |b| vs |a + b| (or the three pairwise distances) updating as you
  drag.
- **Interactions:** drag points in 3D (orbit camera to disambiguate depth);
  watch the inequality readout; try to break it. Snap-to-degenerate: when the
  points become collinear, equality — highlight that moment.
- **The aha:** the inequality is never violated, and equality happens exactly
  when the detour vanishes — "the straight line is shortest" made tactile.

## 2. Euler's formula e^iθ — two perspectives — **PROJECT 6** ✅ built: [projects/eulers-formula/](projects/eulers-formula/index.html)

**Perspective 1 — reached via Manhattan distance, with zoom.**

> e^iθ is reached via the Manhattan distance. Allow zooming in to see the
> convergence.

*Interpretation:* the Taylor partial sums 1 + iθ + (iθ)²/2! + … Each successive
term is rotated 90° from the last (powers of i cycle), so the partial-sum path
is a right-angled spiral — Manhattan-style movement alternating between real
and imaginary directions — that wraps into the point e^iθ on the unit circle.
A pleasing corollary: the total path length walked is Σ θᵏ/k! = e^θ, while the
straight-line distance reached is 1. Zooming into the spiral's eye shows the
convergence visually.

- **Interactions:** scrub θ; step through terms one at a time; infinite zoom
  into the limit point; toggle the unit circle.

**Perspective 2 — the helix.**

> X axis is the real line. Along Y axis θ varies, Z axis is imaginary. This
> causes a sin curve to appear parallel to the YZ plane and a cos curve
> parallel to the XY plane. e^iθ can now be seen as a helix moving along the
> Y axis.

- **The visual:** a 3D helix (cos θ, θ, sin θ). Project onto the XY plane →
  cosine; onto the YZ plane → sine; look down the θ-axis → the unit circle.
- **Interactions:** orbit the camera between the three canonical views (circle
  end-on, sine side-on, cosine top-down); scrub θ with a point riding the
  helix and its two shadow points riding the projections.
- **The aha:** sine, cosine, and the unit circle are three shadows of one
  object.

## 3. Pascal's triangle as paths — nCk — **PROJECT 3** ✅ built: [projects/pascals-paths/](projects/pascals-paths/index.html)

> You need to move n levels deep into Pascal's triangle and only take k right
> turns (thus n−k left turns). How many such paths are possible? That's nCk and
> it's a dynamic problem, since … ????

The open "since…" is the heart of the visualization: every cell can only be
entered from the two cells above it, so paths-to-here = paths-to-upper-left +
paths-to-upper-right — Pascal's identity C(n,k) = C(n−1,k−1) + C(n−1,k) *is*
the DP recurrence, and the triangle *is* the memo table.

- **Interactions:** click a cell to flood-light all paths to it; watch counts
  fill level by level; toggle between "enumerate paths" (exponential, slow,
  visibly wasteful) and "DP fill" (each cell computed once) to feel why
  overlapping subproblems matter.

## 4. Periods and fundamental periods of composite functions — **PROJECT 5** ✅ built: [projects/composite-periods/](projects/composite-periods/index.html)

> Visualise how to find periods and fundamental periods of composite functions.
> Note how phase shift creates a new wrapped-up function with the same phase
> [period], how scaling does not affect roots, how LCM appears in the period of
> functions of functions, while GCD is needed for frequency.

- **The visual:** build a function as a pipeline (e.g. sin(x) → sin(2x) →
  sin(2x + φ) → sin(2x+φ) + cos(3x)) and at each stage show the waveform with
  its fundamental period bracketed.
- **Interactions:** sliders for frequency multipliers and phase shifts; combine
  two periodic functions and watch the combined period emerge as the LCM of the
  parts (equivalently, the combined frequency as a GCD); markers on roots
  showing which transformations move them and which don't.
- **The aha:** period arithmetic (LCM/GCD) stops being a memorized rule — you
  see the two waves "lining up again" exactly at the LCM.

## 5. DSP — radians/sample via spinning phasors — **PROJECT 2** ✅ built: [projects/spinning-phasors/](projects/spinning-phasors/index.html)

> Get away from viewing individual frequency tones as sines and/or cosines and
> instead view them as spinning phasors (e^jωt = 1∠ωt) … Each point in a DFT
> is an individual frequency tone represented as a single rotating phasor in
> time. … Once sampled, the rotation will be at the same rate but in discrete
> samples where each sample is a constant angle in radians — thus frequency can
> be quantified as radians/sample.

- **The visual:** a unit-circle phasor spinning at F Hz (counter-clockwise for
  positive frequency, clockwise for negative), with its real projection tracing
  a cosine and imaginary projection tracing a sine off to the side — the helix
  idea (#2) in disguise.
- **Interactions:** frequency slider (through zero into negative — watch it
  reverse); a "sample" button/slider that strobes the continuous rotation into
  discrete dots a constant angle apart, making radians/sample literal; push the
  sample rate down until aliasing appears as the phasor seeming to spin the
  wrong way.
- **Extension:** a row of phasors, one per DFT bin, each spinning at its bin
  frequency — the DFT as a bank of spinning detectors. ✅ added in stage 8
  (`#7`) and playground.

## 6. Sense of Scale — a personal scope-insensitivity trainer — **PROJECT 4** ✅ built: [projects/sense-of-scale/](projects/sense-of-scale/index.html)

*Design pivot during build: not one log-ladder for everything, but view engines
keyed by quantity kind — Race (rates), Zoom (extents), Count (crowds, with the
repetition→smear→nested-tens arc), Ring (cycles), plus the ladder demoted to an
index/map.*

*Second pivot (user steer): **practical/bodily/lived anchors beat abstract ones.**
A quantity only means something as a thing you've handled. Two new view engines
in that spirit: **Pour** (volume as real containers — a good cry = 0.4 teaspoons,
a car = 9 scooty tanks, daily water = 2.7 bottles) and **Rain** (rainfall as a
depth on your own body + runoff off your roof in tankers; gauge auto-rescales so
the human shrinks at Mawsynram's annual). The cosmic zoom is now the least-aligned
view and is the candidate to re-anchor next. Rainfall anchor numbers were
adversarially fact-checked via a verification workflow. Deferred to v2:
arbitrary-value probe, drawn money pallets, persistent calibration, custom anchors,
practical re-anchoring of energy/power/pressure.*

Scope insensitivity: humans can't feel large (or tiny) numbers because the
numbers lose reference. The cure is a personal collection of *anchors* —
(quantity, value, story) triples like "30 ml = a kashayam dose" or "80 W = one
resting human" — pinned onto explorable scales. Seed data:
[data/personal-anchors.md](../data/personal-anchors.md) (18 categories,
~30 orders of magnitude).

- **Primitive 1 — the Ladder:** a zoomable log₁₀ axis per quantity
  (power, money, speed, length…), anchors pinned at their decades. Type or
  drag a value → it lands between anchors with live ratios ("1,500 W = one AC
  = 18.75 resting humans"). Click any anchor to *rebase* the whole ladder in
  that unit (everything in Vespa tanks).
- **Primitive 2 — the Ring:** cyclic dual-label mappings (24h ↔ 12h train
  clock, Malayalam ↔ English weekdays, month numbers ↔ names) — same data
  shape, circular scale.
- **Dual notation rails:** the lakh/crore ↔ million/billion ladder is one
  log axis with two label systems — a Ladder with two rails.
- **The repetition→smear moment:** show ratios as literal repeated icons
  (18 humans = 1 AC); past ~10³–10⁴ the icons become an indistinct smear —
  that breakdown IS scope insensitivity, made visible; switch to nested
  areas / volumes (the 13-billion-euros lesson).
- **Estimation game:** "place the cheetah" — drag a marker to where you think
  a value lives, get calibration feedback. Training, not just reference.
- Anchors are a user-editable JSON document (add your own, localStorage +
  export) — the document/engine pattern again.

## 7. Sunlight on a rotating Earth — **PROJECT 7** ✅ built: [projects/earth-seasons/](projects/earth-seasons/index.html)

A 3D globe with a day/night terminator, axial tilt, and a scrubbable
time-of-year — showing *why* seasons happen. (Inspiration:
[TheSkyLive 3D solar system](https://theskylive.com/3dsolarsystem),
[earth.nullschool.net](https://earth.nullschool.net).)

- **Interactions:** scrub the day and the year independently; tilt toggle
  (set axial tilt to 0° and watch seasons vanish); pin a city and watch its
  daylight hours change across the year.
