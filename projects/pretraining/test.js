const { chromium } = require('playwright');

const BASE = process.env.BASE_URL || 'http://127.0.0.1:4173';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 920 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  try {
    await page.goto(`${BASE}/projects/pretraining/`);
    await page.waitForFunction(() => window.__viz?.state().ready);

    let state = await page.evaluate(() => window.__viz.state());
    if (state.project !== 'pretraining') throw new Error(`wrong project: ${JSON.stringify(state)}`);
    if (state.mode !== 'select') throw new Error(`expected initial select mode, got ${state.mode}`);

    const models = await page.evaluate(() => window.__viz.models());
    if (models.length < 15) throw new Error(`expected expanded model list, got ${models.length}`);
    if (!models.some((m) => m.id === 'pythia-1.4b' && m.hasCorpus)) {
      throw new Error('Pythia should expose a corpus view');
    }
    for (const id of ['gpt2', 'gpt2-xl', 'pythia-12b', 'qwen2.5-0.5b', 'qwen2.5-7b', 'mistral-7b', 'gemma-2-2b', 'gemma-2-9b', 'gemma-2-27b']) {
      if (!models.some((m) => m.id === id)) throw new Error(`missing next-token model ${id}`);
    }
    if (models.some((m) => m.id === 'gpt-claude')) {
      throw new Error('closed models should be named specifically, not grouped');
    }
    if (!models.some((m) => m.id === 'gemini-1.5-pro' && !m.hasCorpus && m.openness === 'opaque')) {
      throw new Error('Gemini should be represented as a specific opaque model');
    }

    await page.evaluate(() => window.__viz.go(1));
    await page.evaluate(() => window.__viz.setModel('pythia-1.4b'));
    state = await page.evaluate(() => window.__viz.state());
    if (state.mode !== 'corpus' || !state.hasCorpus) throw new Error(`Pythia corpus state wrong: ${JSON.stringify(state)}`);
    let corpus = await page.evaluate(() => window.__viz.corpus());
    if (!corpus.some((d) => d.name.includes('web'))) throw new Error('Pythia corpus should include web');
    if (!corpus.some((d) => d.name.includes('code'))) throw new Error('Pythia corpus should include code');

    await page.evaluate(() => window.__viz.setModel('gemini-1.5-pro'));
    state = await page.evaluate(() => window.__viz.state());
    if (state.hasCorpus || state.openness !== 'opaque') throw new Error(`opaque model state wrong: ${JSON.stringify(state)}`);
    const opaqueText = await page.locator('#caption').textContent();
    if (!opaqueText.includes('corpus')) throw new Error('caption should still explain corpus disclosure');

    await page.evaluate(() => window.__viz.setModel('smollm2-1.7b'));
    await page.evaluate(() => window.__viz.go(4));
    const estimate = await page.evaluate(() => window.__viz.estimate());
    if (!(estimate.flops > 1e23)) throw new Error(`SmolLM2 estimate too small: ${JSON.stringify(estimate)}`);

    await page.evaluate(() => window.__viz.go(6));
    state = await page.evaluate(() => window.__viz.state());
    if (state.mode !== 'base') throw new Error(`expected base mode, got ${state.mode}`);

    const pixels = await page.locator('#viz').evaluate((canvas) => {
      const ctx = canvas.getContext('2d');
      const { width, height } = canvas;
      const data = ctx.getImageData(0, 0, width, height).data;
      let changed = 0;
      for (let i = 0; i < data.length; i += 200) {
        if (data[i] + data[i + 1] + data[i + 2] > 80) changed += 1;
      }
      return changed;
    });
    if (pixels < 80) throw new Error(`canvas appears blank: changed=${pixels}`);

    if (errors.length) throw new Error(errors.join('; '));
    await page.screenshot({ path: '/tmp/pretraining-check.png', fullPage: true });
    console.log('pretraining: OK');
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error('FAIL:', e.message || e);
  process.exit(1);
});
