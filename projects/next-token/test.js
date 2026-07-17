#!/usr/bin/env node
/* Cross-model verification harness for the next-token explorable.
 *
 * Drives EVERY journey model (not just gemma) through the attention beat, the
 * A→B transition, the embedding grid, and the frame-fit invariant — asserting
 * the things that used to be gemma-only. Supersedes the old migration smoke test.
 *
 * Usage:  node projects/next-token/test.js [url]
 *   dev (generator output):  serve pramana/isought_whitebox/views on :4173, then
 *                            node projects/next-token/test.js
 *   deployed mirror:         serve the repo root on :4173, then
 *                            node projects/next-token/test.js http://127.0.0.1:4173/projects/next-token/index.html
 *   Default url = http://127.0.0.1:4173/playground.html
 *   (use 127.0.0.1, not localhost — Python's http.server binds IPv4 only.)
 *
 * Page hooks (globals): selectModel(key), jScrollToSp(sp), jForceContent(), jSp().
 * Beat A ≈ sp 3.40, A→B dock ≈ 3.46, embedding grid ≈ sp 2.6.
 * Requires playwright (installed in this repo's node_modules).
 */
const { chromium } = require('playwright');

const URL = process.argv[2] || process.env.BASE || 'http://127.0.0.1:4173/playground.html';
const VW = 1440, VH = 700;              // wide-short: the frame that must fit

// key -> {heads, kv}  (verified from the bakes; kv<heads => GQA)
const MODELS = {
  'gemma-2-2b':   { heads: 8,  kv: 4 },
  'gpt2':         { heads: 12, kv: 12 },
  'gpt2-xl':      { heads: 25, kv: 25 },
  'pythia-1.4b':  { heads: 16, kv: 16 },
  'qwen2.5-0.5b': { heads: 14, kv: 2 },
  'qwen2.5-7b':   { heads: 28, kv: 4 },
  'mistral-7b':   { heads: 32, kv: 8 },
  'gemma-2-9b':   { heads: 16, kv: 8 },
};

const sleep = ms => new Promise(r => setTimeout(r, ms));

// --- embedding mini-game reachability (the "caption crowded out" regression) ---
// The journey is a pinned 100vh frame; a tall grid (21 rows, or a long sentence) must
// NOT push the "Meaning enters here" mini-game link below the fold. Checked across a
// viewport matrix — laptop-short (1440x800) is exactly the case a mobile-only fix missed.
const FIT_VIEWPORTS = [
  { w: 1440, h: 900, name: 'desktop-tall',     mobile: false },
  { w: 1440, h: 800, name: 'laptop-short',     mobile: false },
  { w: 1280, h: 720, name: 'desktop-720',      mobile: false },
  { w: 390,  h: 844, name: 'mobile-portrait',  mobile: true  },
  { w: 844,  h: 390, name: 'mobile-landscape', mobile: true  },
];
// Deterministic: land on a stage via the page's OWN scroll hook, then measure whether a
// mini-game entry link is in-view AND hit-testable (not crowded below the pinned-frame fold).
// No y-scan → no flake. `reSrc` is a RegExp source string for the link text.
async function probeStageLink(page, reSrc, sps) {
  let best = null;
  for (const sp of sps) {
    const r = await page.evaluate(async (args) => {
      const [reSrc, sp] = args, re = new RegExp(reSrc, 'i');
      if (typeof jScrollToSp === 'function') jScrollToSp(sp);
      if (typeof jForceContent === 'function') jForceContent();
      await new Promise(res => setTimeout(res, 80));
      const link = [...document.querySelectorAll('a')].find(a => re.test(a.textContent));
      if (!link) return null;
      const rc = link.getBoundingClientRect(), vh = innerHeight, vw = innerWidth;
      const inView = rc.top >= 0 && rc.bottom <= vh && rc.left >= 0 && rc.right <= vw && rc.width > 0 && rc.height > 0;
      const cx = rc.left + rc.width / 2, cy = rc.top + rc.height / 2;
      let hitOk = false;
      if (cx >= 0 && cy >= 0 && cx <= vw && cy <= vh) { const el = document.elementFromPoint(cx, cy); hitOk = !!(el && (el === link || link.contains(el))); }
      return { sp, top: Math.round(rc.top), bottom: Math.round(rc.bottom), vh, inView, hitOk };
    }, [reSrc, sp]);
    if (r) { const s = (r.inView ? 2 : 0) + (r.hitOk ? 1 : 0); if (!best || s > best.score) best = { ...r, score: s }; if (r.inView && r.hitOk) break; }
  }
  return best;
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: VW, height: VH } });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));

  await page.goto(URL, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => typeof window.selectModel === 'function', { timeout: 15000 });

  const benign = t => /health|favicon|ERR_CONNECTION_REFUSED|hf\.space|status of 5\d\d/i.test(t);   // sleeping-Space 5xx / remote flakes aren't UI failures
  const results = {};

  for (const [key, exp] of Object.entries(MODELS)) {
    const before = errors.length;
    await page.evaluate(k => window.selectModel(k), key);
    // poll the beat-A board until its head count matches (detects the async bake load)
    let loaded = false;
    for (let i = 0; i < 60; i++) {
      const heads = await page.evaluate(() => {
        window.jScrollToSp(3.40); window.jForceContent && window.jForceContent();
        const jw = document.querySelector('#aHeadBoard .jwide');
        if (!jw) return -1;
        const axis = jw.children[1];                    // [rail, axis, cols]
        return axis ? axis.children.length - 1 : -1;    // minus the 'avg' row
      });
      if (heads === exp.heads) { loaded = true; break; }
      await sleep(200);
    }

    const r = await page.evaluate(() => {
      const rect = el => el ? el.getBoundingClientRect() : null;
      const out = {};
      window.jScrollToSp(3.40); window.jForceContent && window.jForceContent();
      const jw = document.querySelector('#aHeadBoard .jwide');
      out.heads = jw ? jw.children[1].children.length - 1 : -1;
      out.shelves = jw ? jw.children[0].children.length : -1;
      // frame fit: pin a head, whole frame within the fold
      const h = document.querySelector('#aHeadBoard [data-head="1"]');
      if (h) h.dispatchEvent(new MouseEvent('click', { bubbles: true }));
      const ex = document.getElementById('jBeatExplain');
      out.frameFits = ex ? rect(ex).bottom <= innerHeight : false;
      // A→B transition: nothing flies off-screen, breakdown held back
      window.jScrollToSp(3.46); window.jForceContent && window.jForceContent();
      const recede = document.getElementById('abRecede');
      const parts = recede ? [...recede.querySelectorAll('#aHeadBoard,#pinBox')] : [];
      out.transitionParts = parts.length;
      out.transitionOnscreen = parts.length ? parts.every(p => {
        const b = rect(p); return b.top >= -20 && b.bottom <= innerHeight + 40;
      }) : null;
      const arith = document.getElementById('jArith'), band = document.getElementById('mlpBand');
      const shown = el => el && +getComputedStyle(el).opacity > 0.15;
      out.breakdownHeldBack = !(shown(arith) || shown(band));
      // the stream must visibly move during the glide (nonzero transform, not identity)
      const stream = document.getElementById('mlpStream') || document.getElementById('jStreamRow');
      const tr = stream ? getComputedStyle(stream).transform : 'none';
      out.streamMoved = tr !== 'none' && !/matrix\(1,\s*0,\s*0,\s*1,\s*0,\s*0\)/.test(tr);
      // embedding grid legibility: heatmap must have contrast
      window.jScrollToSp(2.6); window.jForceContent && window.jForceContent();
      const cells = [...document.querySelectorAll('#jContent span')]
        .map(s => getComputedStyle(s).backgroundColor)
        .filter(c => c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent');
      out.embUniqueColors = new Set(cells).size;
      // attention walkthrough LAYER SWEEP: must ENTER at layer 1 (sink acknowledged in copy) and
      // ARRIVE at a mid showcase layer (>1) by the end — the old design teleported straight to the
      // showcase, which read as a bug ("why does attention start at 18?").
      const rdLayer = () => { const sl = document.getElementById('jStreamLabel') || document.querySelector('#wkStream .sub');
        const lm = sl ? sl.textContent.match(/layer\s+(\d+)\s+of/i) : null; return lm ? +lm[1] : null; };
      window.jScrollToSp(3.22); window.jForceContent && window.jForceContent();
      out.entryLayer = rdLayer();
      window.jScrollToSp(3.29); window.jForceContent && window.jForceContent();
      out.showcaseLayer = rdLayer();
      return out;
    });

    r.loaded = loaded;
    r.newErrors = errors.slice(before).filter(t => !benign(t));
    results[key] = r;
  }

  // --- embedding mini-game reachability across the viewport matrix ---
  const captionResults = [];
  for (const v of FIT_VIEWPORTS) {
    const p = await browser.newPage({ viewport: { width: v.w, height: v.h }, isMobile: v.mobile, hasTouch: v.mobile });
    try {
      await p.goto(URL, { waitUntil: 'domcontentloaded' });
      await p.waitForFunction(() => typeof window.jScroll === 'function', { timeout: 15000 });
      await sleep(400);
      const emb = await probeStageLink(p, 'Meaning enters', [2.6]);            // §3 embedding mini-game entry
      const tok = await probeStageLink(p, 'Guess the tokens', [1.4, 1.5, 1.6, 1.75, 1.9]); // §2 tokens entry (renders across a band)
      const opened = await p.evaluate(() => {
        if (typeof jScrollToSp === 'function') jScrollToSp(2.6);
        if (typeof jForceContent === 'function') jForceContent();
        const a = [...document.querySelectorAll('a')].find(x => /expand the grid/i.test(x.textContent));
        if (a) a.click();
        const m = document.getElementById('embView');
        return m ? getComputedStyle(m).display : null;
      });
      const embOk = !!(emb && emb.inView && emb.hitOk), tokOk = !!(tok && tok.inView && tok.hitOk);
      const ok = embOk && tokOk && opened === 'flex';
      captionResults.push({ name: v.name, wh: `${v.w}x${v.h}`, ok, emb, tok, opened });
    } catch (e) {
      captionResults.push({ name: v.name, wh: `${v.w}x${v.h}`, ok: false, err: e.message });
    } finally { await p.close(); }
  }

  await browser.close();

  const pass = b => b === true ? 'PASS' : b === false ? 'FAIL' : b == null ? ' -- ' : String(b);
  const pad = (s, n) => String(s).padEnd(n);
  console.log('\ncross-model verification @ ' + URL + '  (viewport ' + VW + '×' + VH + ')\n');
  console.log(pad('model', 15), pad('heads', 12), pad('shelves', 12), pad('frame', 6), pad('transit', 8), pad('held', 6), pad('moved', 6), pad('emb', 9), pad('showcase', 11), 'errors');
  let allGreen = true;
  for (const [key, r] of Object.entries(results)) {
    const exp = MODELS[key];
    const heads = r.heads === exp.heads ? `PASS(${r.heads})` : `FAIL(${r.heads}/${exp.heads})`;
    const shelves = r.shelves === exp.kv ? `PASS(${r.shelves})` : `FAIL(${r.shelves}/${exp.kv})`;
    const emb = (r.embUniqueColors >= 6) ? `PASS(${r.embUniqueColors})` : `FAIL(${r.embUniqueColors})`;
    const showcase = (r.entryLayer === 1 && r.showcaseLayer > 1) ? `PASS(L1→L${r.showcaseLayer})` : `FAIL(L${r.entryLayer}→L${r.showcaseLayer})`;
    const errN = r.newErrors.length ? `FAIL(${r.newErrors.length})` : 'PASS';
    const checks = [r.heads === exp.heads, r.shelves === exp.kv, r.frameFits, r.transitionOnscreen !== false, r.breakdownHeldBack !== false, r.streamMoved !== false, r.embUniqueColors >= 6, r.entryLayer === 1 && r.showcaseLayer > 1, r.newErrors.length === 0];
    if (!r.loaded || checks.some(x => x === false)) allGreen = false;
    console.log(
      pad(key, 15), pad(heads, 12), pad(shelves, 12),
      pad(pass(r.frameFits), 6), pad(pass(r.transitionOnscreen), 8),
      pad(pass(r.breakdownHeldBack), 6), pad(pass(r.streamMoved), 6), pad(emb, 9), pad(showcase, 11), errN,
      r.loaded ? '' : '[LOAD-FAILED]');
    if (r.newErrors.length) r.newErrors.slice(0, 2).forEach(e => console.log('      ↳', e.slice(0, 100)));
  }
  console.log('\n' + (allGreen ? 'cross-model: ALL GREEN ✓' : 'cross-model: FAILURES ABOVE ✗'));

  // mini-game reachability report — the "entry crowded out below the pinned-frame fold" guard
  console.log('\nmini-game entries reachable (tokens §2 + embedding §3, not crowded below the fold):');
  let capGreen = true;
  const rf = (x, label) => x ? `${label}(top=${x.top}/vh=${x.vh} in=${x.inView} hit=${x.hitOk})` : `${label}(MISSING)`;
  for (const c of captionResults) {
    if (!c.ok) capGreen = false;
    const detail = c.err ? c.err : `${rf(c.tok, 'tokens')} ${rf(c.emb, 'embed')} expandOpens=${c.opened === 'flex'}`;
    console.log('  ' + (c.ok ? 'PASS' : 'FAIL') + '  ' + pad(c.name, 18) + pad(c.wh, 9) + (c.ok ? '' : detail));
  }
  console.log('\n' + (allGreen && capGreen ? 'ALL GREEN ✓' : 'FAILURES ABOVE ✗') + '\n');
  process.exit(allGreen && capGreen ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
