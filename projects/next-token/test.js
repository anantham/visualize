// E2E for the next-token explorable.
//
// This page was migrated from the `pramana` research repo and has NO
// `window.__viz` hook (unlike the other gallery projects), so we drive it via
// the DOM, network, and console rather than a state API.
//
// SCOPE (read this before trusting a green run): this is a migration smoke +
// regression guard, NOT a correctness test. Its strongest assertions cover the
// things the migration actually changed (bundles load by relative path, SRV ->
// HF Space, /health reachable, no console errors) and the journey's DESIGN
// invariants (stages 3->4->5->6 advance in order; stage 4 is the residual-stream
// beat; the stream graphic renders during stage 4 — proven to go red if it
// doesn't). It does NOT verify the interpretability is correct — that the
// tokens/embeddings/residual values shown are the real model's outputs. That
// ground truth lives in pramana's precompute pipeline; visual/pedagogical
// correctness still needs a human eyeball.
//
// Run:
//   python3 -m http.server 4173      # from the repo root
//   node projects/next-token/test.js
// Override the base URL with BASE=... (use 127.0.0.1, not localhost — Python's
// http.server binds IPv4 only, so `localhost` may resolve to IPv6 ::1 and fail):
//   BASE=http://127.0.0.1:4173 node projects/next-token/test.js
//
// Requires playwright (`npm i -D playwright` in the repo, or run where it's
// installed). It also pings the live HF Space, so it needs network.
//
// STATUS: passing — runs green via Playwright's bundled Chromium against a local
// `python3 -m http.server` (prints "next-token: OK"). The Live check depends on
// the HF Space being awake; if it's cold-started the test warns but still passes.

const { chromium } = require('playwright');

const BASE = process.env.BASE || 'http://127.0.0.1:4173';
const PAGE_URL = BASE + '/projects/next-token/index.html';
const SPACE = 'https://everythingisrelative-pramana-gemma-live.hf.space';
const BUNDLES = ['pg_sent_kathmandu', 'pg_sent_keys', 'pg_sent_socrates', 'pg_sent_water'];

function assert(cond, msg) { if (!cond) throw new Error('ASSERT: ' + msg); }

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  // 1. Console hygiene — collect errors from the very start of the session.
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push('console.error: ' + m.text()); });

  // 7 MB page: wait for the load event, then let the inline script build the DOM.
  await page.goto(PAGE_URL, { waitUntil: 'load', timeout: 60000 });
  await page.waitForTimeout(2000);

  // 2. Structure — the page actually booted into the expected explorable.
  const title = await page.title();
  assert(/travel through a language model/i.test(title), `unexpected title: "${title}"`);

  const heads = await page.evaluate(() =>
    Array.from(document.querySelectorAll('h2')).map((h) => h.textContent.trim()));
  for (const p of ['Part 1', 'Part 2', 'Part 3', 'Part 4']) {
    assert(heads.some((t) => t.startsWith(p)), `deep-dive heading missing: ${p}`);
  }

  // Only the journey scaffold is present at load; the per-stage residual-stream
  // elements (#mlpStream/#jStreamRow/#wkStream/#vdHero) are created dynamically
  // during the scrub, so they're validated by the continuity sweep below.
  const haveScaffold = await page.evaluate(() =>
    ['#jMarkers', '#jContent', '#jLabel'].every((s) => !!document.querySelector(s)));
  assert(haveScaffold, 'journey scaffold (#jMarkers/#jContent/#jLabel) missing — page did not build');
  const markerCount = await page.evaluate(() => document.getElementById('jMarkers').children.length);
  assert(markerCount >= 4, `expected >=4 journey beats in #jMarkers, found ${markerCount}`);

  // 3. Lazy-loaded sentence bundles serve (by relative path) and parse as JSON.
  for (const b of BUNDLES) {
    const r = await page.evaluate(async (name) => {
      try {
        const res = await fetch('./' + name + '.json', { cache: 'no-store' });
        if (!res.ok) return { ok: false, status: res.status };
        const j = await res.json();
        return { ok: true, isObj: j !== null && typeof j === 'object' };
      } catch (e) { return { ok: false, err: String(e) }; }
    }, b);
    assert(r.ok && r.isObj, `bundle ${b}.json not served/parsed: ${JSON.stringify(r)}`);
  }

  // 4. Live mode — the page points SRV at the HF Space, and the Space answers.
  const usesSpace = (await page.content()).includes(SPACE);
  assert(usesSpace, 'page no longer references the HF Space (SRV mis-set?)');

  const health = await page.evaluate(async (space) => {
    try {
      const res = await fetch(space + '/health', { cache: 'no-store' });
      return { ok: res.ok, body: await res.json() };
    } catch (e) { return { ok: false, err: String(e) }; }
  }, SPACE);
  assert(health.ok && health.body && 'ok' in health.body,
    `Live backend /health unreachable or wrong shape: ${JSON.stringify(health)}`);
  if (!health.body.ok || !health.body.model_loaded) {
    console.warn('  [warn] HF Space reachable but not ready (likely cold-start): '
      + JSON.stringify(health.body));
  }

  // 5. Journey continuity — asserted against the journey's DESIGN, not a tuned
  // frame count. Scrubbing sp 2.85->5.5 must advance the pipeline through stages
  // 3->4->5->6 in order, stage 4 must be the residual-stream beat (this
  // explorable's titular concept), and the stream graphic must actually render
  // during stage 4. (The stream is only visible ~1/3 of the scrub — it fades
  // between stages — so "fraction of frames" is NOT a meaningful gate; the design
  // invariants below are.)
  const scan = await page.evaluate(() => {
    function spNow() { const mk = document.getElementById('jMarkers'); const kids = mk.children, line = innerHeight * 0.5; let sp = kids.length - 1, y = mk.getBoundingClientRect().top; for (let i = 0; i < kids.length; i++) { const h = kids[i].offsetHeight; if (line < y + h || i === kids.length - 1) { sp = i + Math.max(0, Math.min(0.9999, (line - y) / h)); break; } y += h; } return sp; }
    function yForSp(t) { let lo = 0, hi = document.body.scrollHeight; for (let k = 0; k < 44; k++) { const m = (lo + hi) / 2; scrollTo(0, m); if (spNow() < t) lo = m; else hi = m; } return (lo + hi) / 2; }
    const sel = ['#mlpStream', '#jStreamRow', '#wkStream', '#vdHero'];
    function streamVisible() { const c = document.getElementById('jContent'); if (!c) return null; for (const s of sel) { const el = document.querySelector('#jContent ' + s); if (el) { const o = +getComputedStyle(el).opacity; if (o > 0.3 && el.getBoundingClientRect().width > 4) return s; } } return null; }
    const y0 = yForSp(2.1), y1 = yForSp(5.5), STEPS = 120;   // start inside stage 3 (sp ~1.96-2.89) — 2.85 sat at its tail where the 3->4 dock masks the label
    const order = []; const srcs = {}; let streamInStage4 = false;
    for (let i = 0; i <= STEPS; i++) {
      scrollTo(0, y0 + (y1 - y0) * i / STEPS); if (typeof jScroll === 'function') jScroll();
      const label = ((document.getElementById('jLabel') || {}).textContent || '').trim();
      if (label && order[order.length - 1] !== label) order.push(label);
      const s = streamVisible(); if (s) { srcs[s] = (srcs[s] || 0) + 1; if (/^\s*4\b/.test(label)) streamInStage4 = true; }
    }
    scrollTo(0, 0);
    return { order, srcs, streamInStage4 };
  });
  console.log(`  journey labels: ${JSON.stringify(scan.order)}`);
  console.log(`  stream sightings: ${JSON.stringify(scan.srcs)}`);
  // (a) the scrub advances through stages 3,4,5,6 in order
  const nums = scan.order.map((l) => (l.match(/^\s*(\d+)/) || [])[1]).filter(Boolean).map(Number);
  for (const n of [3, 4, 5, 6]) assert(nums.includes(n), `stage ${n} never appeared during the 3->6 scrub (saw ${JSON.stringify(scan.order)})`);
  assert(nums.indexOf(3) < nums.indexOf(4) && nums.indexOf(4) < nums.indexOf(5) && nums.indexOf(5) < nums.indexOf(6),
    `stages did not advance in order: ${JSON.stringify(scan.order)}`);
  // (b) stage 4 is the residual-stream beat — the concept this explorable exists to teach
  const stage4 = scan.order.find((l) => /^\s*4\b/.test(l)) || '';
  assert(/residual/i.test(stage4), `stage 4 should name the residual stream, got "${stage4}"`);
  // (c) the residual-stream graphic actually renders during stage 4
  assert(scan.streamInStage4, 'no residual-stream element was visible during stage 4 — the stream graphic is not rendering');

  // 6. No console / page errors across load + all interactions above.
  assert(errors.length === 0, 'console/page errors:\n  ' + errors.join('\n  '));

  console.log('next-token: OK');
  await browser.close();
})().catch((e) => { console.error(e.message || e); process.exit(1); });
