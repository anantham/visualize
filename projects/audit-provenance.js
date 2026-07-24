/**
 * Provenance gate for the measured-explorable series (simulator, sft, preferences).
 *
 * The evidence contract: "the rendering layer may say less than the artifacts support,
 * never more." This is the machine half of that — it drives every stage of every page,
 * scrapes the numbers a READER actually sees, and fails if any of them traces to
 * nothing. It caught zero of the three prose overclaims this series shipped (those need
 * a human adversarial read — see CLAIMS.md), but it permanently closes the number class.
 *
 * How a page declares its provenance (so this file never hard-codes rotting facts):
 *   - every numeric in the page's own bake (stream.json) is DERIVED and allowed;
 *   - anything else must be listed in the page's `<meta name="cited-number">` tags,
 *     e.g. <meta name="cited-number" content="61,135 | HF ultrafeedback_binarized card">.
 *     A number with no bake match and no cited-number meta is a VIOLATION.
 *
 * Run: node projects/audit-provenance.js   (serve the repo root on :4173 first)
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const BASE = process.env.AUDIT_URL || 'http://localhost:4173/projects';
const PAGES = [
  { id: 'simulator', stages: 6 },
  { id: 'sft', stages: 3 },
  { id: 'preferences', stages: 4 },
];

// trivially-ambiguous tokens that are never a provenance claim on their own
const TRIVIAL = new Set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '100']);

function bakeNumbers(obj, out = new Set()) {
  if (obj === null || obj === undefined) return out;
  if (typeof obj === 'number') {
    for (const s of [String(obj), obj.toFixed(0), obj.toFixed(1), obj.toFixed(2), obj.toFixed(3),
                     String(Math.round(obj)), String(Math.round(obj * 100)),
                     Math.abs(obj).toFixed(2), Math.abs(obj).toFixed(3)]) out.add(s);
    return out;
  }
  if (typeof obj === 'string') { const m = obj.match(/\d[\d,]*\.?\d*/g); if (m) m.forEach(x => { out.add(x); out.add(x.replace(/,/g, '')); }); return out; }
  if (Array.isArray(obj)) { obj.forEach(o => bakeNumbers(o, out)); return out; }
  Object.values(obj).forEach(o => bakeNumbers(o, out));
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const violations = [];

  for (const p of PAGES) {
    const bakePath = path.join(ROOT, p.id, 'stream.json');
    const nums = fs.existsSync(bakePath) ? bakeNumbers(JSON.parse(fs.readFileSync(bakePath, 'utf8'))) : new Set();
    const page = await browser.newPage({ viewport: { width: 1200, height: 1500 } });
    await page.goto(`${BASE}/${p.id}/#0`, { waitUntil: 'load' });
    await page.waitForFunction(() => window.__viz && window.__viz.state().ready === true, null, { timeout: 15000 });

    // cited numbers the page declares about itself
    const cited = await page.$$eval('meta[name="cited-number"]', els =>
      els.map(e => (e.getAttribute('content') || '').split('|')[0].trim()));
    const citedSet = new Set(cited.flatMap(c => [c, c.replace(/,/g, '')]));

    for (let s = 0; s < p.stages; s++) {
      await page.evaluate(i => window.__viz.go(i), s);
      await page.waitForTimeout(120);
      const id = await page.evaluate(() => window.__viz.state().id);
      const text = await page.locator('#app').innerText();   // the content region, not chrome
      const seen = [...new Set((text.match(/\d[\d,]*\.?\d*/g) || []))];
      for (const raw of seen) {
        const bare = raw.replace(/,/g, '');
        if (TRIVIAL.has(bare)) continue;
        const ok = nums.has(raw) || nums.has(bare) || nums.has(String(parseFloat(bare)))
          || nums.has(Math.abs(parseFloat(bare)).toFixed(2)) || nums.has(Math.abs(parseFloat(bare)).toFixed(3))
          || citedSet.has(raw) || citedSet.has(bare);
        if (!ok) violations.push({ beat: p.id, stage: id, value: raw });
      }
    }
    await page.close();
  }
  await browser.close();

  if (!violations.length) {
    console.log('provenance: OK — every number a reader sees is derived from a bake or a declared citation.');
  } else {
    console.error('provenance: FAIL — numbers on screen that trace to no artifact and no cited-number meta:');
    for (const v of violations) console.error(`  ${v.beat.padEnd(12)} ${String(v.stage).padEnd(10)} ${v.value}`);
    console.error(`\n${violations.length} untraceable. Either they are wrong, or the page must declare them:`);
    console.error('  <meta name="cited-number" content="VALUE | source you verified">');
    process.exit(1);
  }
})().catch(e => { console.error('AUDIT ERROR:', e.message || e); process.exit(1); });
