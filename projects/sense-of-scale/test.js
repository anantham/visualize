const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));

  await page.goto('http://localhost:4173/projects/sense-of-scale/');
  let s = await page.evaluate(() => window.__viz.state());
  if (s.stage !== 9) throw new Error(`default stage 9, got ${s.stage}`);
  if (s.view !== 'index') throw new Error(`default view index, got ${s.view}`);

  await page.evaluate(() => window.__viz.go(6));
  await page.evaluate(() => window.__viz.pourThing(1));
  s = await page.evaluate(() => window.__viz.state());
  if (Math.abs(s.pour.n - 0.4) >= 0.05) throw new Error(`good cry teaspoons ~0.4, got ${s.pour.n}`);

  await page.evaluate(() => window.__viz.go(7));
  await page.evaluate(() => {
    window.__viz.setRainRate(60);
    window.__viz.setRainDepth(950);
  });
  s = await page.evaluate(() => window.__viz.state());
  if (s.rain.depth < 944) throw new Error(`rain depth >= 944, got ${s.rain.depth}`);

  await page.evaluate(() => window.__viz.go(1));
  await page.evaluate(() => window.__viz.setZ(-10));
  s = await page.evaluate(() => window.__viz.state());
  if (!s.sawAtom) throw new Error('sawAtom after zoom in');

  await page.evaluate(() => window.__viz.setZ(5.8));
  s = await page.evaluate(() => window.__viz.state());
  if (!s.sawKerala) throw new Error('sawKerala after zoom out');

  await page.evaluate(() => window.__viz.go(8));
  await page.evaluate(() => {
    const lock = () => document.getElementById('lock').click();
    const next = () => document.getElementById('game-next').click();
    window.__viz.setGuess(1.4);
    lock(); next();
    window.__viz.setGuess(1.62);
    lock(); next();
    window.__viz.setGuess(0.43);
    lock();
  });
  s = await page.evaluate(() => window.__viz.state());
  if (s.game.hits < 2) throw new Error(`calibration hits >= 2, got ${s.game.hits}`);

  if (errors.length) throw new Error(errors.join('; '));
  console.log('sense-of-scale: OK');
  await page.screenshot({ path: '/tmp/sense-of-scale-check.png' });
  await browser.close();
})().catch((e) => {
  console.error('FAIL:', e.message || e);
  process.exit(1);
});