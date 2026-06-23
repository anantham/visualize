const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on('pageerror', (e) => { throw new Error(e.message); });

  await page.goto('http://localhost:4173/projects/pascals-paths/');

  await page.evaluate(() => window.__viz.selectCell(6, 2));
  let s = await page.evaluate(() => window.__viz.state());
  if (s.sel.count !== 15) throw new Error(`C(6,2)=15, got ${s.sel?.count}`);
  if (s.sel.viaL !== 5 || s.sel.viaR !== 10) throw new Error('split counts wrong');

  await page.evaluate(() => window.__viz.go(4));
  await page.evaluate(() => document.getElementById('race-btn').click());
  for (let i = 0; i < 300; i++) {
    s = await page.evaluate(() => window.__viz.state());
    if (s.race?.done) break;
    await page.waitForTimeout(50);
  }
  s = await page.evaluate(() => window.__viz.state());
  if (!s.race?.done) throw new Error('race did not finish');
  if (s.race.enumSteps !== 560) throw new Error(`enumSteps 560, got ${s.race.enumSteps}`);
  if (s.race.dpCells !== 45) throw new Error(`dpCells 45, got ${s.race.dpCells}`);

  await page.evaluate(() => window.__viz.go(3));
  await page.evaluate(() => window.__viz.selectCell(5, 2));
  await page.waitForTimeout(900);
  s = await page.evaluate(() => window.__viz.state());
  if (!s.taskDone) throw new Error('stage 3 split task should complete');

  console.log('pascals-paths: OK');
  await browser.close();
})().catch((e) => {
  console.error('FAIL:', e.message || e);
  process.exit(1);
});