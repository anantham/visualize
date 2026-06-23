# Pascal's Paths — nCk as a walk

**Project 3.** You descend `n` levels into Pascal's triangle, choosing left or
right at each step. Take exactly `k` right turns and you land at cell (n, k) — and
the number of distinct paths there is **C(n, k)**. It's a dynamic-programming
problem because the only way into a cell is through the two cells above it:

> paths(n, k) = paths(n−1, k−1) + paths(n−1, k)   — Pascal's identity *is* the
> DP recurrence, and the triangle *is* the memo table.

## Structure — 7 stages

1. **Walk the triangle** — left/right buttons (or arrow keys) grow a path.
2. **Order doesn't matter** — reach the same cell two different ways.
3. **Count every route** — click any cell; every route into it lights up; counts
   appear and stay (you memoize the triangle by exploring it).
4. **Two doors in** — clicked cells split their route-bundles by parent (amber =
   via upper-left, blue = via upper-right) with the `15 = 5 + 10` identity drawn
   at the cell. Toggle **enumerate routes** vs **DP fill** on the same triangle —
   counts appear level by level with a step counter vs route-walking cost.
5. **Re-walking vs remembering** — a race: the left triangle walks all routes
   (shared prefixes glow hotter — overlapping subproblems made visible); the
   right fills each cell once. Step counters end ~560 vs 45.
6. **Let chance choose** — a Galton board: drop balls, watch the binomial /
   bell curve assemble from coin-flip left/rights, with the expected shape ticked.
7. **Playground** — depth slider (4–12 rows) + all interactions at once.

## Controls

Left/right/start-over (walk), click cells (select & split), Race!, drop 1 / drop
50 / clear (Galton), depth slider. Back/Next navigate; `#0`–`#6` deep-link.

## Tech

Pure `<canvas>` 2D, zero dependencies, single file. Works offline.

## Testing hook — `window.__viz`

| Method | Returns / effect |
|---|---|
| `state()` | `{ stage, taskDone, N, walk:{depth,rights}, sel:{r,i,count,viaL,viaR}, race:{done,enumSteps,dpCells}, galton:{landed,pending}, visible[] }` |
| `cellPos(r, i)` | screen `{x,y}` of cell (row r, index i) for synthetic clicks |
| `selectCell(r, i)` | select/split a cell directly |
| `setMode('enum' \| 'dp')` | enumerate routes or level-by-level DP fill |
| `go(i)` | jump to stage `i` |

Invariants: clicking cell (6,2) → `count 15`, `viaL 5`, `viaR 10`; the race ends
`enumSteps 560`, `dpCells 45`; depth N=10 center cell (10,5) → `252 = 126 + 126`.
