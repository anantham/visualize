const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));

  await page.goto('http://localhost:4173/projects/eulers-formula/');
  let s = await page.evaluate(() => window.__viz.state());
  if (s.stage !== 0) throw new Error(`default stage 0, got ${s.stage}`);

  await page.evaluate(() => window.__viz.setTheta(1.5));
  s = await page.evaluate(() => window.__viz.state());
  if (!s.taskDone) throw new Error('stage 0 task should complete after θ > 0.8');

  await page.evaluate(() => window.__viz.go(2));
  for (let i = 0; i < 5; i++) await page.evaluate(() => window.__viz.stepTerm());
  s = await page.evaluate(() => window.__viz.state());
  if (s.terms < 6) throw new Error(`terms >= 6, got ${s.terms}`);
  if (!s.taskDone) throw new Error('stage 2 spiral task should complete');

  await page.evaluate(() => window.__viz.go(5));
  await page.evaluate(() => document.getElementById('v-sine').click());
  await page.evaluate(() => document.getElementById('v-cos').click());
  s = await page.evaluate(() => window.__viz.state());
  if (!s.taskDone) throw new Error('stage 5 should complete after all three views');

  await page.evaluate(() => window.__viz.go(6));
  s = await page.evaluate(() => window.__viz.state());
  if (s.stage !== 6) throw new Error('playground stage 6');

  if (errors.length) throw new Error(errors.join('; '));
  console.log('eulers-formula: OK');
  await page.screenshot({ path: '/tmp/eulers-formula-check.png' });
  await browser.close();
})().catch((e) => {
  console.error('FAIL:', e.message || e);
  process.exit(1);
});