const { chromium } = require('playwright');

const TAU = Math.PI * 2;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));

  await page.goto('http://localhost:4173/projects/composite-periods/');
  let s = await page.evaluate(() => window.__viz.state());
  if (s.section !== 0) throw new Error(`default section 0, got ${s.section}`);
  if (Math.abs(s.period - TAU) > 0.01) throw new Error(`sin(x) period 2π, got ${s.period}`);

  await page.evaluate(() => window.__viz.go(1));
  await page.evaluate(() => window.__viz.setK(2));
  s = await page.evaluate(() => window.__viz.state());
  if (s.k !== 2) throw new Error(`k=2, got ${s.k}`);
  if (Math.abs(s.period - Math.PI) > 0.01) throw new Error(`sin(2x) period π, got ${s.period}`);
  if (!s.done[1]) throw new Error('section 1 should complete at k=2');

  await page.evaluate(() => window.__viz.go(2));
  await page.evaluate(() => window.__viz.setPhi(1.2));
  s = await page.evaluate(() => window.__viz.state());
  if (Math.abs(s.period - Math.PI) > 0.01) throw new Error('phase shift must not change period');
  if (!s.done[2]) throw new Error('section 2 should complete after phi move');

  await page.evaluate(() => window.__viz.go(3));
  await page.evaluate(() => window.__viz.setK2(3));
  s = await page.evaluate(() => window.__viz.state());
  if (!s.addSecond) throw new Error('second wave should be on');
  if (Math.abs(s.period - TAU) > 0.02) throw new Error(`LCM period 2π, got ${s.period}`);

  await page.evaluate(() => window.__viz.go(4));
  await page.evaluate(() => window.__viz.revealGuess(true));
  s = await page.evaluate(() => window.__viz.state());
  if (!s.revealGuess) throw new Error('guess reveal should work');
  if (s.xMax < TAU) throw new Error('xMax should fit long periods');

  await page.evaluate(() => window.__viz.go(5));
  s = await page.evaluate(() => window.__viz.state());
  if (s.section !== 5) throw new Error('playground section 5');

  if (errors.length) throw new Error(errors.join('; '));
  console.log('composite-periods: OK');
  await page.screenshot({ path: '/tmp/composite-periods-check.png', fullPage: true });
  await browser.close();
})().catch((e) => {
  console.error('FAIL:', e.message || e);
  process.exit(1);
});