const { chromium } = require('playwright');
const BASE = process.env.SIM_URL || 'http://localhost:4173/projects/simulator/';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });

  await page.goto(`${BASE}#0`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__viz && window.__viz.state().ready === true, null, { timeout: 15000 });
  const st = await page.evaluate(() => window.__viz.state());
  if (st.stages !== 6) throw new Error(`expected 6 stages, got ${st.stages}`);

  // stage 0 — the loop: stepping one token advances the stream + grows the sentence
  const before = await page.evaluate(() => window.__viz.state().step);
  await page.click('[data-eng="step"]');
  const after = await page.evaluate(() => window.__viz.state().step);
  if (after !== before + 1) throw new Error(`step did not advance (${before}->${after})`);
  const genTokens = await page.locator('.tok.gen').count();
  if (genTokens < 1) throw new Error('no generated token appeared after stepping');
  await page.click('[data-eng="step"]');
  await page.click('[data-eng="step"]');
  const dist = await page.locator('.dist .drow').count();
  if (dist < 4) throw new Error(`expected a next-token distribution, got ${dist} rows`);
  const pick = await page.locator('.dist .drow.pick').count();
  if (pick < 1) throw new Error('no chosen token highlighted in the distribution');
  await page.screenshot({ path: '/tmp/sim-loop.png' });

  // stage 1 — sampling: temperature reshapes bars, sampling records picks
  await page.evaluate(() => window.__viz.go(1));
  // temperature reshapes the lower bars (top bar is normalized to 100%)
  await page.$eval('[data-srange="temp"]', el => { el.value = 0.3; el.dispatchEvent(new Event('input', { bubbles: true })); });
  const low = await page.locator('#samdist .drow .bar i').nth(2).evaluate(el => parseFloat(el.style.width));
  await page.$eval('[data-srange="temp"]', el => { el.value = 2; el.dispatchEvent(new Event('input', { bubbles: true })); });
  const high = await page.locator('#samdist .drow .bar i').nth(2).evaluate(el => parseFloat(el.style.width));
  if (!(high > low)) throw new Error(`temperature did not flatten the distribution (bar#3: ${low}% -> ${high}%)`);
  await page.click('[data-smp="many"]');
  const picks = await page.locator('#sampicks .tok').count();
  if (picks < 1) throw new Error('sampling did not record any picks');
  await page.screenshot({ path: '/tmp/sim-sample.png' });

  // stage 2 — seeding: switching the seed changes the stream
  await page.evaluate(() => window.__viz.go(2));
  await page.click('[data-idx="2"]'); // children's book
  const gp = await page.evaluate(() => window.__viz.state());
  if (gp.group !== 'framings' || gp.idx !== 2) throw new Error(`seed switch failed: ${JSON.stringify(gp)}`);
  await page.screenshot({ path: '/tmp/sim-seed.png' });

  // stage 3 — few-shot: toggling examples changes the distribution
  await page.evaluate(() => window.__viz.go(3));
  const d0 = await page.locator('.dist').innerText();
  const shotBtns = await page.locator('[data-shot]').count();
  if (shotBtns < 2) throw new Error('few-shot toggle buttons missing');
  await page.locator('[data-shot]').last().click();
  const d1 = await page.locator('.dist').innerText();
  if (d0 === d1) throw new Error('adding examples did not change the distribution');
  await page.screenshot({ path: '/tmp/sim-shots.png' });

  // stage 4 — register: flipping clean->broken changes the continuation, and the page
  // must report the HONEST per-topic split (it mirrors on some topics, corrects on others)
  await page.evaluate(() => window.__viz.go(4));
  await page.click('[data-rk="clean"]');
  const clean = await page.locator('.sent').innerText();
  await page.click('[data-rk="broken"]');
  const broken = await page.locator('.sent').innerText();
  if (clean === broken) throw new Error('clean/broken seed toggle did not change the continuation');
  const regText = await page.locator('#app').innerText();
  if (/matches the register it/i.test(regText)) {
    throw new Error('register stage is overclaiming a general law (it only mirrors on some topics)');
  }
  if (!/mirrored/i.test(regText)) throw new Error('register stage should report whether this topic mirrored');
  // the topic that corrects must actually say so
  await page.click('[data-rt="1"]');
  const corrected = await page.locator('#app').innerText();
  if (!/corrected/i.test(corrected)) throw new Error('a non-mirroring topic must be labelled corrected');
  await page.click('[data-rt="0"]');
  await page.screenshot({ path: '/tmp/sim-register.png' });

  // stage 5
  await page.evaluate(() => window.__viz.go(5));
  await page.screenshot({ path: '/tmp/sim-end.png' });

  // mobile
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${BASE}#0`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__viz && window.__viz.state().ready === true);
  const ov = await page.evaluate(() => ({ w: innerWidth, sw: document.documentElement.scrollWidth }));
  if (ov.sw > ov.w + 1) throw new Error(`mobile overflow ${ov.sw} > ${ov.w}`);
  await page.screenshot({ path: '/tmp/sim-mobile.png' });

  if (errors.length) throw new Error('page errors:\n' + errors.join('\n'));
  console.log('simulator: OK');
  await browser.close();
})().catch(e => { console.error('FAIL:', e.message || e); process.exit(1); });
