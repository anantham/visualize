const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on('pageerror', (e) => { throw new Error(e.message); });

  await page.goto('http://localhost:4173/projects/triangle-inequality/');
  let s = await page.evaluate(() => window.__viz.state());
  if (s.stage !== 0) throw new Error(`stage 0 expected, got ${s.stage}`);
  if (s.slack < 0) throw new Error(`slack >= 0, got ${s.slack}`);

  await page.evaluate(() => {
    window.__viz.setPoint('A', [3, 1, 0]);
    window.__viz.setPoint('B', [-2, 0.5, 1]);
  });
  await page.evaluate(() => { window.__viz.go(0); });
  await page.evaluate(() => { window.__viz.state(); flags = { dragged: true }; });
  // simulate drag completion
  await page.evaluate(() => {
    const ev = new Event('pointerup');
    window.dispatchEvent(ev);
  });

  await page.evaluate(() => {
    window.__viz.setPoint('A', [2.6, 1.8, -1.2]);
    window.__viz.setPoint('B', [-2.2, 0.9, 1.6]);
    window.__viz.go(5);
  });
  await page.evaluate(() => document.getElementById('align').click());
  await page.waitForTimeout(900);
  s = await page.evaluate(() => window.__viz.state());
  if (!s.equal) throw new Error(`equal after align, slack=${s.slack}`);
  if (s.visible.length < 5) throw new Error('playground should show all visuals');

  console.log('triangle-inequality: OK');
  await browser.close();
})().catch((e) => {
  console.error('FAIL:', e.message || e);
  process.exit(1);
});