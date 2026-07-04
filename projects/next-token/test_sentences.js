#!/usr/bin/env node
/* Cross-SENTENCE completeness test for the next-token explorable.
 * Cycles every built-in sentence (the stage-1 picker) and drives it through
 * each stage, asserting the DATA needed at that stage is present — so a sentence
 * can't silently be missing tour-swaps / embedding / showcase-head / value data.
 *
 * Usage:  node projects/next-token/test_sentences.js [url]
 *   serve pramana/isought_whitebox/views on :4173, then run.
 * Requires playwright (repo node_modules).
 */
const { chromium } = require('playwright');
const URL = process.argv[2] || process.env.BASE || 'http://127.0.0.1:4173/playground.html';
const SENTENCES = ['anchor', 'water', 'kathmandu', 'socrates', 'keys'];
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 820 } });
  const errors = [];
  p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  p.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
  await p.goto(URL, { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => typeof window.jPickSentence === 'function' && typeof window.jScrollToSp === 'function', { timeout: 15000 });
  const benign = t => /health|favicon|ERR_CONNECTION_REFUSED/i.test(t);

  const results = {};
  for (const id of SENTENCES) {
    const before = errors.length;
    // switch sentence, wait for the (lazy) bundle to load: poll until the tour reflects it
    await p.evaluate(sid => window.jPickSentence(sid), id);
    await sleep(1500);
    const r = await p.evaluate(() => {
      const at = (sp) => { window.jScrollToSp(sp); window.jForceContent && window.jForceContent(); };
      const txt = () => (document.getElementById('jContent') || {}).textContent || '';
      const out = {};
      // stage 2 — tokenizer tour: swap-words present, no fallback
      at(1.46);
      out.tourSwaps = document.querySelectorAll('[data-tourword]').length;
      out.tourFallback = /pick one to swap a word/.test(txt());
      // stage 3 — embedding grid renders
      at(2.6);
      out.embCells = document.querySelectorAll('#jContent .g23h, #jContent span[style*="background"]').length;
      // stage 4 — attention walkthrough: renders + uses the SHOWCASE layer (not the layer-0/1 fallback) + value step has cells
      at(3.25);
      const sl = document.getElementById('jStreamLabel') || document.querySelector('#wkStream .sub');
      const m = sl ? (sl.textContent.match(/layer\s+(\d+)\s+of/i)) : null;
      out.wkLayer = m ? +m[1] : null;                 // showcase => a mid layer; fallback => 1
      out.valueCells = (document.getElementById('wkValue') || document.createElement('div')).querySelectorAll('span[style*="background"]').length;
      // stage 4 — board renders
      at(3.40);
      const jw = document.querySelector('#aHeadBoard .jwide');
      out.boardHeads = jw ? jw.children[1].children.length - 1 : 0;
      // stage 6 — next-token distribution
      at(5.5);
      out.nextTokens = document.querySelectorAll('#jContent [data-tip], #jContent span').length;
      return out;
    });
    r.newErrors = errors.slice(before).filter(t => !benign(t));
    results[id] = r;
  }
  await b.close();

  const P = (ok) => ok ? 'PASS' : 'FAIL';
  const pad = (s, n) => String(s).padEnd(n);
  console.log('\ncross-sentence completeness @ ' + URL + '\n');
  console.log(pad('sentence', 12), pad('tour', 10), pad('embed', 7), pad('showcaseLayer', 15), pad('valueData', 11), pad('board', 7), 'errors');
  let green = true;
  for (const [id, r] of Object.entries(results)) {
    const tour = P(r.tourSwaps > 0 && !r.tourFallback) + (r.tourSwaps ? `(${r.tourSwaps})` : '');
    const emb = P(r.embCells > 20);
    const showcase = (r.wkLayer && r.wkLayer > 1) ? `PASS(L${r.wkLayer})` : `FAIL(L${r.wkLayer})`;   // >1 => real showcase head, not the layer-0 fallback
    const value = P(r.valueCells > 8);   // milk's-value (16) + stream/attn/mid — <=8 means v16 missing
    const board = P(r.boardHeads === 8);
    const errN = r.newErrors.length ? `FAIL(${r.newErrors.length})` : 'PASS';
    const ok = [r.tourSwaps > 0 && !r.tourFallback, r.embCells > 20, r.wkLayer > 1, r.valueCells > 8, r.boardHeads === 8, r.newErrors.length === 0];
    if (ok.some(x => !x)) green = false;
    console.log(pad(id, 12), pad(tour, 10), pad(emb, 7), pad(showcase, 15), pad(value, 11), pad(board, 7), errN);
  }
  console.log('\n' + (green ? 'ALL SENTENCES COMPLETE ✓' : 'INCOMPLETE SENTENCES ABOVE ✗') + '\n');
  process.exit(green ? 0 : 1);
})().catch(e => { console.error(e); process.exit(2); });
