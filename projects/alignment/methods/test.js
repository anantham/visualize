const { chromium } = require('playwright');

const BASE = process.env.BASE_URL || 'http://localhost:4173';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 920 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  try {
    await page.goto(`${BASE}/projects/alignment/methods/#0`);
    await page.waitForFunction(() => window.__viz?.state().ready);

    let state = await page.evaluate(() => window.__viz.state());
    if (state.stage !== 0 || state.id !== 'overview') throw new Error(`bad initial state: ${JSON.stringify(state)}`);

    const methods = await page.evaluate(() => window.__viz.methods());
    if (methods.length !== 7) throw new Error(`expected 7 methods, got ${methods.length}`);
    if (!methods.some((m) => m.id === 'refusal' && m.tier === 'measured summary')) {
      throw new Error('refusal method should be labeled measured summary, not live');
    }

    await page.evaluate(() => window.__viz.go(3));
    state = await page.evaluate(() => window.__viz.state());
    if (state.id !== 'dpo') throw new Error(`expected DPO stage, got ${state.id}`);
    await page.evaluate(() => window.__viz.setControl('dpo', 'step', 95));
    await page.evaluate(() => window.__viz.setControl('dpo', 'reveal', true));
    const likelihoodText = await page.locator('#demo').textContent();
    if (!likelihoodText.includes('chosen likelihood')) throw new Error('DPO reveal did not show likelihood split');
    if (!likelihoodText.includes('fixed probe') || !likelihoodText.includes('-50.52')) {
      throw new Error('DPO stage is not using the measured fixed-probe endpoint');
    }

    await page.evaluate(() => window.__viz.go(5));
    const constitutionalText = await page.locator('#demo').textContent();
    if (!constitutionalText.includes('No reliable constitution effect')) {
      throw new Error('constitutional stage should show the measured null');
    }
    if (!constitutionalText.includes('position A selections')) {
      throw new Error('constitutional stage should expose measured position bias');
    }

    await page.evaluate(() => window.__viz.go(6));
    await page.evaluate(() => window.__viz.setControl('rlvr', 'task', 'math'));
    await page.evaluate(() => window.__viz.setControl('rlvr', 'steps', 0));
    const zeroSignalText = await page.locator('#demo').textContent();
    if (!zeroSignalText.includes('relative gradient is zero')) {
      throw new Error('RLVR pilot should expose zero-variance groups');
    }
    await page.evaluate(() => window.__viz.setControl('rlvr', 'steps', 20));
    const learningSignalText = await page.locator('#demo').textContent();
    if (!learningSignalText.includes('GRPO can update')) {
      throw new Error('RLVR pilot should expose groups with mixed rewards');
    }
    await page.evaluate(() => window.__viz.setControl('rlvr', 'task', 'advice'));
    const rlvrText = await page.locator('#demo').textContent();
    if (!rlvrText.includes('no checker')) throw new Error('RLVR off-island state missing no-checker text');

    await page.evaluate(() => window.__viz.go(7));
    await page.evaluate(() => window.__viz.setControl('refusal', 'coef', -80));
    const leftText = await page.locator('#demo').textContent();
    if (!leftText.includes('redacted harmful procedural content')) throw new Error('refusal low end did not show redacted ablated output');
    if (!leftText.includes('harmful safety response')) throw new Error('refusal stage missing measured safety rate');
    await page.evaluate(() => window.__viz.setControl('refusal', 'coef', 82));
    const rightText = await page.locator('#demo').textContent();
    if (!rightText.includes('benign over-refusal')) throw new Error('refusal high end missing over-refusal metric');
    if (!rightText.includes('boiling point of water')) throw new Error('refusal high end missing benign prompt');

    const needlePixels = await page.locator('#needles').evaluate((canvas) => {
      const ctx = canvas.getContext('2d');
      const { width, height } = canvas;
      const data = ctx.getImageData(0, 0, width, height).data;
      const r0 = data[0], g0 = data[1], b0 = data[2];
      let changed = 0;
      for (let i = 0; i < data.length; i += 160) {
        if (Math.abs(data[i] - r0) + Math.abs(data[i + 1] - g0) + Math.abs(data[i + 2] - b0) > 12) changed += 1;
      }
      return changed;
    });
    if (needlePixels < 40) throw new Error(`needle canvas appears blank: changed=${needlePixels}`);

    const navCount = await page.locator('#nav button').count();
    if (navCount !== 8) throw new Error(`expected 8 nav stages, got ${navCount}`);

    if (errors.length) throw new Error(errors.join('; '));
    await page.screenshot({ path: '/tmp/alignment-methods-check.png', fullPage: true });
    console.log('alignment-methods: OK');
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error('FAIL:', e.message || e);
  process.exit(1);
});
