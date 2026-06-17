# Triangle Inequality in 3D

**Project 1.** A page where you place two points in 3D space and watch the
triangle inequality hold — and see exactly when it becomes equality — by dragging.

> |AB| ≤ |AO| + |OB| — the straight path between two points is never longer than
> a detour through a third.

## The idea

`O` is fixed at the origin; `A` and `B` are draggable. The green **direct** path
|AB| is compared to the orange **detour** |AO| + |OB|. The detour can never be
shorter. Equality happens exactly when `O` lies on segment `AB` — the moment the
detour vanishes. The whole point is that this is something the reader's *hand*
discovers, not something asserted.

## Controls

- **Drag A or B** — moves the point in the plane facing the camera.
- **Drag the background** — orbit the camera; **scroll** — zoom.
- **Show equality** — animates B so O lands on segment AB (everything turns green,
  an equality banner appears).
- **Reset** — restores the starting positions.

Dashed drop-lines to the floor grid aid depth perception; live side lengths are
labelled in-scene, and the panel shows the inequality with live numbers plus a
two-bar detour-vs-direct comparison.

## Tech

Three.js 0.160 via CDN + ES-module import map. Needs a network connection. ~1 file.

## Testing hook — `window.__viz`

| Method | Returns / effect |
|---|---|
| `state()` | `{ A:[x,y,z], B:[x,y,z], AO, OB, AB, slack, equal }` |
| `screenPos(name)` | screen pixel `{x,y}` of point `'A'`, `'B'`, or `'O'` (for synthetic drags) |
| `setPoint(name, [x,y,z])` | move a point directly |

Invariants worth asserting: `slack === AO + OB − AB ≥ 0` always; after **Show
equality**, `slack → 0` and `equal === true`.
