const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const BASE = process.env.PREF_URL || 'http://localhost:4173/projects/preferences/';
const DATA = JSON.parse(fs.readFileSync(path.join(__dirname, 'stream.json'), 'utf8'));

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 1000 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });

  await page.goto(`${BASE}#0`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__viz && window.__viz.state().ready === true, null, { timeout: 15000 });
  const st = await page.evaluate(() => window.__viz.state());
  if (st.stages !== 4) throw new Error(`expected 4 stages, got ${st.stages}`);

  // stage 0 — mechanism: scrubbing training moves the bars; the numbers come from the bake
  const traj = DATA.mechanism.trajectory;
  await page.evaluate(() => window.__viz.mstep(0));
  const w0 = await page.locator('.lp.c .track i').evaluate(el => parseFloat(el.style.width));
  await page.evaluate(n => window.__viz.mstep(n), traj.length - 1);
  const w1 = await page.locator('.lp.c .track i').evaluate(el => parseFloat(el.style.width));
  if (!(w1 > w0)) throw new Error(`chosen bar did not grow across training (${w0} -> ${w1})`);
  const shown = await page.locator('.lp.c .v').innerText();
  if (!shown.includes(traj[traj.length - 1].chosen_pt.toFixed(3))) {
    throw new Error(`per-token value not artifact-derived (saw ${shown})`);
  }
  // the summed view must expose the negative (length-bias) gap
  await page.evaluate(() => window.__viz.metric('sum'));
  const gapCls = await page.locator('.gap').getAttribute('class');
  if (!gapCls.includes('neg')) throw new Error('summed gap should be negative (length bias)');
  await page.evaluate(() => window.__viz.metric('pt'));
  const gapCls2 = await page.locator('.gap').getAttribute('class');
  if (!gapCls2.includes('pos')) throw new Error('per-token gap should be positive');
  await page.screenshot({ path: '/tmp/pref-mech.png', fullPage: true });

  // stage 1 — supervision
  await page.evaluate(() => window.__viz.go(1));
  const rows = await page.locator('.disc .drow2').count();
  if (rows !== 6) throw new Error(`expected 6 disclosure rows, got ${rows}`);
  const sup = await page.locator('#app').innerText();
  if (!sup.includes('61,135')) throw new Error('missing UltraFeedback count');
  if (!/GPT-4/.test(sup)) throw new Error('missing the synthetic-feedback disclosure');
  await page.screenshot({ path: '/tmp/pref-sup.png', fullPage: true });

  // stage 2 — install: toggling the preference changes the answer
  await page.evaluate(() => window.__viz.go(2));
  await page.click('[data-state="sft"]');
  const before = await page.locator('.sent').innerText();
  await page.click('[data-state="dpo"]');
  const after = await page.locator('.sent').innerText();
  if (before === after) throw new Error('toggling the preference did not change the answer');
  const dist = await page.locator('.dist .drow').count();
  if (dist < 4) throw new Error('missing next-token distribution');
  await page.screenshot({ path: '/tmp/pref-install.png', fullPage: true });

  // stage 3
  await page.evaluate(() => window.__viz.go(3));
  await page.screenshot({ path: '/tmp/pref-end.png', fullPage: true });

  // mobile
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${BASE}#0`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__viz && window.__viz.state().ready === true);
  const ov = await page.evaluate(() => ({ w: innerWidth, sw: document.documentElement.scrollWidth }));
  if (ov.sw > ov.w + 1) throw new Error(`mobile overflow ${ov.sw} > ${ov.w}`);

  if (errors.length) throw new Error('page errors:\n' + errors.join('\n'));
  console.log('preferences: OK');
  await browser.close();
})().catch(e => { console.error('FAIL:', e.message || e); process.exit(1); });
