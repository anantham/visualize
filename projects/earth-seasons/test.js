const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));

  await page.goto('http://localhost:4173/projects/earth-seasons/');
  await page.waitForFunction(() => window.__viz?.state);
  let s = await page.evaluate(() => window.__viz.state());
  if (s.stage !== 0) throw new Error(`default stage 0, got ${s.stage}`);

  await page.evaluate(() => window.__viz.setDay(22));
  await page.waitForTimeout(100);
  s = await page.evaluate(() => window.__viz.state());
  if (!s.taskDone) throw new Error('stage 0 day spin task should complete');

  await page.evaluate(() => window.__viz.go(1));
  await page.evaluate(() => window.__viz.setYear(172));
  s = await page.evaluate(() => window.__viz.state());
  if (!s.taskDone) throw new Error('stage 1 solstice task should complete near day 172');

  await page.evaluate(() => window.__viz.go(2));
  await page.evaluate(() => document.getElementById('pin-city').click());
  await page.evaluate(() => window.__viz.setYear(80));
  await page.evaluate(() => window.__viz.setYear(172));
  await page.waitForTimeout(100);
  s = await page.evaluate(() => window.__viz.state());
  if (!s.city) throw new Error('Kochi should be pinned');
  if (s.daylight == null || s.daylight < 10) throw new Error(`daylight hours plausible, got ${s.daylight}`);
  if (!s.taskDone) throw new Error('stage 2 compare task should complete');

  await page.evaluate(() => window.__viz.go(3));
  await page.evaluate(() => window.__viz.setTilt(false));
  await page.waitForTimeout(100);
  s = await page.evaluate(() => window.__viz.state());
  if (s.tilt) throw new Error('tilt should be off');
  if (!s.taskDone) throw new Error('stage 3 tilt-off task should complete');

  if (errors.length) throw new Error(errors.join('; '));
  console.log('earth-seasons: OK');
  await page.screenshot({ path: '/tmp/earth-seasons-check.png' });
  await browser.close();
})().catch((e) => {
  console.error('FAIL:', e.message || e);
  process.exit(1);
});