# Sense of Scale — numbers too big to feel

**Project 4.** A trainer for **scope insensitivity** — the human inability to feel
very large or very small numbers. The cure is a personal collection of *anchors*
(quantity, value, story) shown in whatever form fits the quantity. The data lives
in [`../../data/personal-anchors.md`](../../data/personal-anchors.md).

## The key design decision: views keyed by quantity *kind*

Not one log-ladder for everything. Different quantities want different forms, so
there are **six view engines**, plus a ladder demoted to an index/map:

| View | For | What it does |
|---|---|---|
| **Race** | rates (speed) | seven lanes cross a 100 m track at true speed; the crossing counters *are* the ratios |
| **Zoom** | extents (length) | continuous travel from a proton to the observable universe; concentric circles, true-scale area rectangles, captioned physical voids; **something at every zoom level** |
| **Count** | amounts (population, money, power, time, pressure, area, energy) | how many of a unit fit, degrading honestly: countable icons → dot field → "a smear, counting has died", with a nested-tens rescue |
| **Ring** | cycles | the 24h↔12h train clock and the Malayalam↔English week, one rotating hand |
| **Pour** | volume | real amounts in real containers — *a good cry = 0.4 teaspoons*, *a car = 9 scooty tanks*, *daily water = 2.7 bottles* |
| **Rain** | rainfall | a depth on your own body + roof runoff in tankers; the gauge rescales so the human shrinks at Mawsynram's annual |
| **Index** | everything | one strip per quantity; click any dot to open it in its natural view |

The guiding philosophy (a mid-project pivot): **practical / bodily / lived anchors
beat abstract ones.** A quantity only means something as a thing you've handled.
Pour and Rain are the purest expression; the cosmic Zoom is the holdout still to
be re-anchored.

## Structure — 10 stages

Speed→race · Length→zoom · Counts→crowds (population smear) · the demonetization
number (₹15.41 lakh crore) · Cycles→rings · Appliances in humans · **Volume→pour**
· **Rain→a depth you can stand in** · Calibrate yourself (an estimation game) ·
The index. `#0`–`#9` deep-link; the index is the playground.

## Data provenance

The rainfall and zoom-ladder anchors were **adversarially fact-checked** by
multi-agent verification workflows (gather per band → verify each claim against
sources → synthesize). That caught real errors (body-depth landmarks, Mumbai's
944 mm confirmed, Mawsynram annual, etc.) and mapped the genuine physical voids.

## Tech

Pure `<canvas>` 2D, zero dependencies, single file. Works offline.

## Testing hook — `window.__viz`

| Method | Returns / effect |
|---|---|
| `state()` | `{ stage, taskDone, view, simT, cam, snailCross, z, sawAtom, sawGalaxy, count, flags, ring, hand, day, pour:{thing,unit,n}, poured, rain:{depth,rate,raining,roof,stormH}, game, visible[] }` |
| `go(i)` | jump to stage `i` |
| `setCam(log)` / `setZ(z)` | race time-speed (log) / zoom view-width exponent |
| `zoomCheck(z)` | `{ present, sized, inVoid }` — occupancy at a zoom level (used to prove no accidental gaps) |
| `setUnit(i)` | pick a Count unit |
| `setHand(h)` / `setRing(r)` | ring hand position / `'clock'`\|`'week'` |
| `pourThing(i)` / `pourUnit(i)` | select a Pour amount / vessel |
| `setRainDepth(mm)` / `setRainRate(hr)` / `toggleRain()` | drive the Rain gauge |
| `setGuess(decades)` | the calibration game slider |
| `openIndex(catName, anchorLabel)` | open an index anchor in its natural view |

Invariants: zoom `present ≥ 1` at every non-void level across the full sweep;
pour "a good cry" → `0.4 teaspoons`, "filling a car" → `9 scooty tanks`; rain
past 944 mm marks the Mumbai task done; index "volume" opens the **pour** view,
"rainfall" opens **rain**.
