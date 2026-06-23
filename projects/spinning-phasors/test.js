const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://localhost:4173/projects/spinning-phasors/');
  await page.evaluate(() => window.__viz.go(3));
  await page.evaluate(() => { window.__viz.set('freq', 1); document.getElementById('pause').click(); });
  const s = await page.evaluate(() => window.__viz.state());
  if (!s.paused) throw new Error('should be paused');
  const ok = await page.evaluate(() => {
    const st = window.__viz.state();
    return Math.abs(Math.cos(st.phase)) > 0.88 || Math.abs(Math.sin(st.phase)) < 0.15;
  });
  await page.evaluate(() => window.__viz.go(7));
  let dft = await page.evaluate(() => window.__viz.state());
  if (dft.dftBin !== 2) throw new Error(`DFT bin 2 at F=2 Fs=8, got ${dft.dftBin}`);
  await page.evaluate(() => window.__viz.go(8));
  const pg = await page.evaluate(() => window.__viz.state());
  if (pg.stage !== 8) throw new Error(`playground stage 8, got ${pg.stage}`);
  console.log('spinning-phasors: OK');
  await browser.close();
})().catch((e) => { console.error('FAIL:', e.message); process.exit(1); });