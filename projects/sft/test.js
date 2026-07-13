const { chromium } = require('playwright');
const BASE = process.env.SFT_URL || 'http://localhost:4173/projects/sft/';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });

  await page.goto(`${BASE}#0`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__viz && window.__viz.state().ready === true, null, { timeout: 15000 });
  const st = await page.evaluate(() => window.__viz.state());
  if (st.stages !== 3) throw new Error(`expected 3 stages, got ${st.stages}`);

  // stage 0 — checkpoint scrubber transforms the same prompt's answer
  await page.click('[data-ckpt="sft_400"]');
  const trained = await page.locator('.sent').innerText();
  await page.click('[data-ckpt="base"]');
  const raw = await page.locator('.sent').innerText();
  if (trained === raw) throw new Error('scrubbing base vs SFT-400 did not change the answer');
  // base should read as broken, SFT-400 as coherent (verdict class flips)
  const rawVerdict = await page.locator('.verdict').getAttribute('class');
  await page.click('[data-ckpt="sft_400"]');
  const trainedVerdict = await page.locator('.verdict').getAttribute('class');
  if (!rawVerdict.includes('bad')) throw new Error('base checkpoint should show the "just continues" verdict');
  if (!trainedVerdict.includes('ok')) throw new Error('SFT-400 should show the coherent-answer verdict');
  // the loop still steps
  const dist = await page.locator('.dist .drow').count();
  if (dist < 4) throw new Error('missing next-token distribution');
  await page.screenshot({ path: '/tmp/sft-train.png' });

  // stage 1 — demonstrations
  await page.evaluate(() => window.__viz.go(1));
  const demos = await page.locator('.demo').count();
  if (demos < 1) throw new Error('no demonstrations rendered');
  await page.screenshot({ path: '/tmp/sft-how.png' });

  // stage 2
  await page.evaluate(() => window.__viz.go(2));
  await page.screenshot({ path: '/tmp/sft-end.png' });

  // mobile
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${BASE}#0`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__viz && window.__viz.state().ready === true);
  const ov = await page.evaluate(() => ({ w: innerWidth, sw: document.documentElement.scrollWidth }));
  if (ov.sw > ov.w + 1) throw new Error(`mobile overflow ${ov.sw} > ${ov.w}`);
  await page.screenshot({ path: '/tmp/sft-mobile.png' });

  if (errors.length) throw new Error('page errors:\n' + errors.join('\n'));
  console.log('sft: OK');
  await browser.close();
})().catch(e => { console.error('FAIL:', e.message || e); process.exit(1); });
