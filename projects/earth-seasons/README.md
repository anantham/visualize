# Earth Seasons — sunlight & tilt

**Project 7.** A 3D globe with day/night terminator, **23.4° axial tilt**, and
scrubbable day-of-year — showing why seasons happen and what changes when tilt
vanishes.

## What it shows

- Sunlight on one hemisphere at a time; scrub time-of-day and the terminator sweeps.
- Tilt steers which latitude gets more direct rays across the year.
- Pin **Kochi** (9.9°N) and watch daylight hours shift from winter to summer.
- Toggle tilt to 0° — seasons flatten; every day becomes an equinox everywhere.

## Structure — 5 stages

Day and night → Axial tilt → Pin a city → Remove the tilt → **Playground**.

## Controls

Time-of-day slider (0–24 h), day-of-year slider (Jan–Dec), tilt on/off, pin
Kochi. Orbit the globe with drag; scroll to zoom. Back/Next navigate; `#0`–`#4`
deep-link.

Daylight hours use a standard approximate formula (declination from obliquity ×
sin of orbital phase; hour angle from latitude and declination). Good for
qualitative teaching, not ephemeris-grade precision.

## Tech

Three.js 0.160 via CDN + ES-module import map. Needs a network connection.
Single file.

## Testing hook — `window.__viz`

| Method | Returns / effect |
|---|---|
| `state()` | `{ stage, taskDone, dayH, yearD, tilt, city, daylight }` |
| `setDay(h)` / `setYear(d)` | set time of day / day of year |
| `setTilt(on)` | enable or disable axial tilt |
| `go(i)` | jump to stage `i` |

Invariants: extreme day hours complete stage 0; year ≈ 172 (June solstice)
completes stage 1; pinning Kochi and comparing winter vs summer year days
completes stage 2; `tilt === false` completes stage 3.