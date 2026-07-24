const { chromium } = require('playwright');
const zlib = require('zlib');

const BASE = process.env.BASE_URL || 'http://localhost:4173';
const PAGE = (process.env.PAGE_URL || `${BASE}/projects/prior-atlas/`).replace(/\/?$/, '/');

function paeth(a, b, c) {
  const p = a + b - c;
  const pa = Math.abs(p - a);
  const pb = Math.abs(p - b);
  const pc = Math.abs(p - c);
  if (pa <= pb && pa <= pc) return a;
  return pb <= pc ? b : c;
}

function pngStats(buf) {
  let off = 8;
  let width = 0;
  let height = 0;
  let colorType = 0;
  let bitDepth = 0;
  const idat = [];

  while (off < buf.length) {
    const len = buf.readUInt32BE(off);
    const type = buf.toString('ascii', off + 4, off + 8);
    const data = buf.subarray(off + 8, off + 8 + len);
    if (type === 'IHDR') {
      width = data.readUInt32BE(0);
      height = data.readUInt32BE(4);
      bitDepth = data[8];
      colorType = data[9];
    } else if (type === 'IDAT') {
      idat.push(data);
    } else if (type === 'IEND') {
      break;
    }
    off += len + 12;
  }

  if (bitDepth !== 8 || ![2, 6].includes(colorType)) {
    throw new Error(`expected 8-bit RGB/RGBA PNG, got bitDepth=${bitDepth} colorType=${colorType}`);
  }

  const raw = zlib.inflateSync(Buffer.concat(idat));
  const bpp = colorType === 6 ? 4 : 3;
  const stride = width * bpp;
  let pos = 0;
  let prev = Buffer.alloc(stride);
  const unique = new Set();
  let n = 0;
  let mean = 0;
  let m2 = 0;
  const yStep = Math.max(1, Math.floor(height / 40));
  const xStep = Math.max(1, Math.floor(width / 40));

  for (let y = 0; y < height; y++) {
    const filter = raw[pos++];
    const row = raw.subarray(pos, pos + stride);
    pos += stride;
    const recon = Buffer.alloc(stride);

    for (let x = 0; x < stride; x++) {
      const left = x >= bpp ? recon[x - bpp] : 0;
      const up = prev[x];
      const upLeft = x >= bpp ? prev[x - bpp] : 0;
      let value;
      if (filter === 0) value = row[x];
      else if (filter === 1) value = row[x] + left;
      else if (filter === 2) value = row[x] + up;
      else if (filter === 3) value = row[x] + Math.floor((left + up) / 2);
      else if (filter === 4) value = row[x] + paeth(left, up, upLeft);
      else throw new Error(`unsupported PNG filter ${filter}`);
      recon[x] = value & 255;
    }

    if (y % yStep === 0) {
      for (let x = 0; x < width; x += xStep) {
        const p = x * bpp;
        const r = recon[p];
        const g = recon[p + 1];
        const b = recon[p + 2];
        unique.add(`${r},${g},${b}`);
        const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
        n += 1;
        const delta = lum - mean;
        mean += delta / n;
        m2 += delta * (lum - mean);
      }
    }
    prev = recon;
  }

  return { width, height, unique: unique.size, variance: n > 1 ? m2 / (n - 1) : 0 };
}

(async () => {
  const browser = await chromium.launch();
  const loaderPage = await browser.newPage({ viewport: { width: 960, height: 640 } });
  const loaderErrors = [];
  const preloadStarts = [];
  const releasePreloads = [];
  loaderPage.on('pageerror', (e) => loaderErrors.push(e.message));
  loaderPage.on('console', (msg) => {
    if (msg.type() === 'error') loaderErrors.push(msg.text());
  });
  await loaderPage.route('https://unpkg.com/three@0.160.0/**', async (route) => {
    preloadStarts.push({ url: route.request().url(), at: Date.now() });
    await new Promise((resolve) => releasePreloads.push(resolve));
    await route.continue();
  });

  try {
    await loaderPage.goto(`${PAGE}?loader-check=${Date.now()}#0`, { waitUntil: 'commit' });
    await loaderPage.waitForFunction(() => window.__atlasLoader?.state().status === 'loading', null, { timeout: 30000 });
    const preloadDeadline = Date.now() + 5000;
    while (new Set(preloadStarts.map((item) => item.url)).size < 2 && Date.now() < preloadDeadline) {
      await loaderPage.waitForTimeout(25);
    }
    await loaderPage.waitForTimeout(350);
    const loading = await loaderPage.evaluate(() => ({
      state: window.__atlasLoader.state(),
      heading: document.getElementById('msg-h').textContent,
      copy: document.getElementById('msg-p').textContent,
      visibility: getComputedStyle(document.getElementById('msg')).visibility,
    }));
    if (loading.visibility !== 'visible') throw new Error('loader is not visible while 3D modules are pending');
    if (!loading.heading.trim()) throw new Error('loader phase heading is empty while 3D modules are pending');
    if (!loading.copy.includes('measured first visits:') || !loading.copy.includes('elapsed')) {
      throw new Error(`loader is missing its measured range or elapsed time: ${loading.copy}`);
    }
    if (loading.state.elapsedMs < 250 || loading.state.estimateSource !== 'benchmark') {
      throw new Error(`loader timing state is not advancing from the benchmark: ${JSON.stringify(loading.state)}`);
    }
    if (loading.state.benchmark.lowMs !== 500 || loading.state.benchmark.highMs !== 2500 || loading.state.benchmark.coldSamples !== 12) {
      throw new Error(`loader benchmark is not the production-calibrated range: ${JSON.stringify(loading.state.benchmark)}`);
    }
    await loaderPage.waitForTimeout(100);
    if ((await loaderPage.evaluate(() => window.__atlasLoader.state().status)) !== 'loading') {
      throw new Error('loader settled before the delayed-state screenshot');
    }
    await loaderPage.screenshot({ path: '/tmp/prior-atlas-loader-check.png' });

    await loaderPage.waitForFunction(() => window.__atlasLoader.state().elapsedMs > 2600);
    await loaderPage.waitForFunction(() => document.getElementById('msg-estimate').textContent.includes('taking longer than most measured loads'));
    const slowCopy = await loaderPage.locator('#msg-p').textContent();
    if (!slowCopy.includes('taking longer than most measured loads')) {
      throw new Error(`loader did not acknowledge exceeding the measured range: ${slowCopy}`);
    }
    releasePreloads.splice(0).forEach((release) => release());

    await loaderPage.waitForFunction(() => window.__viz?.state().ready, null, { timeout: 30000 });
    const loaded = await loaderPage.evaluate(() => window.__atlasLoader.state());
    if (loaded.status !== 'ready' || loaded.elapsedMs < 1000) {
      throw new Error(`loader did not record the delayed load: ${JSON.stringify(loaded)}`);
    }
    const uniquePreloads = preloadStarts.filter((item, i, all) =>
      all.findIndex((other) => other.url === item.url) === i);
    if (uniquePreloads.length < 2) throw new Error(`expected both Three.js modules to preload, saw ${uniquePreloads.length}`);
    const preloadSpread = Math.max(...uniquePreloads.map((item) => item.at)) - Math.min(...uniquePreloads.map((item) => item.at));
    if (preloadSpread > 500) throw new Error(`Three.js module requests started ${preloadSpread}ms apart instead of in parallel`);
    await loaderPage.waitForFunction(() => getComputedStyle(document.getElementById('msg')).visibility === 'hidden');
    if (loaderErrors.length) throw new Error(loaderErrors.join('; '));
  } finally {
    releasePreloads.splice(0).forEach((release) => release());
    await loaderPage.close();
  }

  const page = await browser.newPage({
    viewport: { width: 1280, height: 820 },
    deviceScaleFactor: 1,
  });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  try {
    await page.goto(`${PAGE}?snap=1#0`);
    await page.waitForFunction(() => window.__viz?.state().ready, null, { timeout: 30000 });

    let state = await page.evaluate(() => window.__viz.state());
    if (state.n !== 3000) throw new Error(`expected 3000 points, got ${state.n}`);
    if (state.models !== 6) throw new Error(`expected 6 models, got ${state.models}`);
    if (state.acts < 5) throw new Error(`expected at least 5 acts, got ${state.acts}`);
    if (state.pair !== 'gpt2|gemma-2-2b') throw new Error(`unexpected default pair ${state.pair}`);
    if (state.density !== 'reveal') throw new Error(`unexpected density ${state.density}`);

    await page.evaluate(() => window.__viz.setControl('ladder', 1));
    const ladder = await page.locator('#surprise-ladder').textContent();
    if (!ladder.includes('coin lands heads') || !ladder.includes('1 bit')) {
      throw new Error('surprise ladder missing coin-flip = 1 bit rung');
    }

    const pairs = await page.evaluate(() => window.__viz.pairs());
    if (pairs.length !== 15) throw new Error(`expected all 15 model pairs, got ${pairs.length}`);
    if (!pairs.some((p) => p.key === 'pythia-1.4b|pythia-410m' && p.matched)) {
      throw new Error('missing matched pythia same-data control pair');
    }

    const first = await page.evaluate(() => window.__viz.point(0));
    if (!first.bits?.gpt2 || !first.bits?.['gemma-2-2b']) throw new Error('point 0 missing per-model bits');

    const shape = await page.evaluate(() => ({
      same: window.__viz.stats('pythia-1.4b', 'pythia-410m'),
      diff: window.__viz.stats('gpt2', 'gemma-2-2b'),
    }));
    if (!(shape.same.meanDiv < shape.diff.meanDiv)) {
      throw new Error(`same-data pair should be flatter: ${shape.same.meanDiv} !< ${shape.diff.meanDiv}`);
    }
    if (!(shape.same.maxDiv < shape.diff.maxDiv)) {
      throw new Error(`same-data max should be lower: ${shape.same.maxDiv} !< ${shape.diff.maxDiv}`);
    }

    await page.evaluate(() => window.__viz.go(2));
    await page.waitForFunction(() => window.__viz.state().act === 2 && window.__viz.state().selected === 0);
    const axis = await page.locator('#axis').textContent();
    const calibration = await page.locator('#calibration').textContent();
    if (!axis.includes('20 bits') || !axis.includes('million×')) throw new Error('axis missing bits + x-factor scale');
    if (!calibration.includes('million×') || !calibration.includes('coverage')) {
      throw new Error('calibration peak copy missing x-factor + coverage framing');
    }

    let panel = await page.locator('#info').evaluate((el) => ({
      shown: el.classList.contains('show'),
      hidden: el.getAttribute('aria-hidden'),
      text: el.textContent,
    }));
    if (!panel.shown || panel.hidden !== 'false') throw new Error('detail panel did not open on terrain act');
    if (!panel.text.includes('bits / char')) throw new Error('detail panel missing divergence unit');
    if (!panel.text.includes('million×') || !panel.text.includes('coverage')) {
      throw new Error('detail panel missing x-factor or coverage line');
    }

    await page.evaluate(() => window.__viz.go(3));
    await page.locator('#modelmap [data-name="gpt2"]').click();
    await page.locator('#modelmap [data-name="gpt2-xl"]').click();
    await page.waitForFunction(() => window.__viz.state().pair === 'gpt2|gpt2-xl');
    state = await page.evaluate(() => window.__viz.state());
    if (state.pair !== 'gpt2|gpt2-xl' || !state.matched) throw new Error(`map dots did not select same-data pair: ${state.pair}`);

    await page.evaluate(() => window.__viz.go(4));
    const caveats = await page.locator('.act[data-act="4"]').textContent();
    for (const phrase of ['Curated sample', 'UMAP is lossy', 'not correctness', 'tail shape', 'Scale looks second-order']) {
      if (!caveats.includes(phrase)) throw new Error(`missing caveat phrase: ${phrase}`);
    }

    await page.waitForFunction(() => getComputedStyle(document.getElementById('msg')).visibility === 'hidden');
    await page.screenshot({ path: '/tmp/prior-atlas-check.png' });
    const canvasPng = await page.locator('#stage canvas').screenshot();
    const stats = pngStats(canvasPng);
    if (stats.width < 500 || stats.height < 400) throw new Error(`canvas too small: ${stats.width}x${stats.height}`);
    if (stats.unique < 10 || stats.variance < 1) {
      throw new Error(`canvas looks blank: unique=${stats.unique} variance=${stats.variance.toFixed(3)}`);
    }
    const loaderVisibility = await page.locator('#msg').evaluate((el) => getComputedStyle(el).visibility);
    if (loaderVisibility !== 'hidden') throw new Error(`settled loader remains paintable: ${loaderVisibility}`);

    const mobile = await browser.newPage({
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 1,
      isMobile: true,
      hasTouch: true,
    });
    mobile.on('pageerror', (e) => errors.push(`mobile: ${e.message}`));
    mobile.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(`mobile: ${msg.text()}`);
    });

    try {
      await mobile.goto(`${PAGE}?snap=1#2`);
      await mobile.waitForFunction(() => window.__viz?.state().ready, null, { timeout: 30000 });

      const mobileState = await mobile.evaluate(() => window.__viz.state());
      if (mobileState.selected !== -1) throw new Error('mobile terrain act should not auto-open point detail');

      const layout = await mobile.evaluate(() => {
        const rect = (id) => {
          const el = document.getElementById(id);
          const r = el.getBoundingClientRect();
          return { x: r.x, y: r.y, width: r.width, height: r.height, display: getComputedStyle(el).display };
        };
        return {
          viewportMeta: document.querySelector('meta[name="viewport"]').content,
          overflow: document.documentElement.scrollWidth - innerWidth,
          story: rect('story'),
          rail: rect('rail'),
          axis: rect('axis'),
          calibration: rect('calibration'),
          mobilebar: rect('mobilebar'),
          targets: ['mobile-explore', 'story-back', 'story-next'].map((id) => {
            const r = document.getElementById(id).getBoundingClientRect();
            return { id, width: r.width, height: r.height };
          }).concat([...document.querySelectorAll('.story-dot')].map((el) => {
            const r = el.getBoundingClientRect();
            return { id: `act-${el.dataset.act}`, width: r.width, height: r.height };
          })),
        };
      });
      if (layout.viewportMeta.includes('maximum-scale')) throw new Error('mobile viewport disables user zoom');
      if (layout.overflow > 0) throw new Error(`mobile page overflows horizontally by ${layout.overflow}px`);
      if (layout.rail.display !== 'none') throw new Error('desktop rail should be collapsed on mobile');
      if (layout.calibration.display !== 'none') throw new Error('calibration card should not cover mobile lesson');
      if (layout.mobilebar.y + layout.mobilebar.height > layout.axis.y) throw new Error('mobile bar overlaps height scale');
      if (layout.axis.y + layout.axis.height > layout.story.y) throw new Error('height scale overlaps mobile lesson');
      if (layout.story.y + layout.story.height > 845) throw new Error('mobile lesson extends below viewport');
      for (const target of layout.targets) {
        if (target.width < 44 || target.height < 44) {
          throw new Error(`mobile touch target ${target.id} is ${target.width}x${target.height}`);
        }
      }

      await mobile.locator('#mobile-explore').click();
      await mobile.waitForFunction(() => document.body.classList.contains('mobile-controls-open'));
      await mobile.waitForFunction(() => document.activeElement?.id === 'mobile-controls-close');
      const drawer = await mobile.evaluate(() => {
        const rail = document.getElementById('rail').getBoundingClientRect();
        const close = document.getElementById('mobile-controls-close').getBoundingClientRect();
        const pair = document.querySelector('.pair').getBoundingClientRect();
        return {
          expanded: document.getElementById('mobile-explore').getAttribute('aria-expanded'),
          focused: document.activeElement?.id,
          rail: { x: rail.x, y: rail.y, width: rail.width, height: rail.height },
          close: { width: close.width, height: close.height },
          pair: { width: pair.width, height: pair.height },
        };
      });
      if (drawer.expanded !== 'true' || drawer.focused !== 'mobile-controls-close') {
        throw new Error('Explore drawer did not open with focus on its close control');
      }
      if (drawer.rail.x < 0 || drawer.rail.y < 0 || drawer.rail.x + drawer.rail.width > 390 || drawer.rail.y + drawer.rail.height > 844) {
        throw new Error('Explore drawer extends outside mobile viewport');
      }
      if (drawer.close.width < 44 || drawer.close.height < 44 || drawer.pair.height < 44) {
        throw new Error('Explore drawer has undersized touch targets');
      }

      await mobile.locator('.pair[data-key="gpt2|gpt2-xl"]').click();
      await mobile.waitForFunction(() => window.__viz.state().pair === 'gpt2|gpt2-xl');
      if (await mobile.locator('body').evaluate((el) => el.classList.contains('mobile-controls-open'))) {
        throw new Error('pair selection should return mobile users to the terrain');
      }

      await mobile.evaluate(() => { window.__viz.go(2); window.__viz.selectPoint(0); });
      await mobile.waitForFunction(() => document.getElementById('info').classList.contains('show'));
      await mobile.waitForTimeout(350);
      const closeHeight = await mobile.locator('#i-close').evaluate((el) => el.getBoundingClientRect().height);
      if (closeHeight < 43.5) throw new Error(`mobile detail close target is only ${closeHeight}px tall`);
      await mobile.locator('#i-close').click();
      if ((await mobile.evaluate(() => window.__viz.state().selected)) !== -1) {
        throw new Error('mobile point detail did not close');
      }

      await mobile.evaluate(() => window.__viz.go(4));
      await mobile.waitForTimeout(350);
      const finalNav = await mobile.evaluate(() => {
        const story = document.getElementById('story').getBoundingClientRect();
        const next = document.getElementById('story-next').getBoundingClientRect();
        return { storyTop: story.top, storyBottom: story.bottom, nextTop: next.top, nextBottom: next.bottom };
      });
      if (finalNav.nextTop < finalNav.storyTop || finalNav.nextBottom > finalNav.storyBottom) {
        throw new Error('mobile story navigation is not kept visible in the final act');
      }

      await mobile.screenshot({ path: '/tmp/prior-atlas-mobile-check.png' });
      const mobileCanvas = pngStats(await mobile.locator('#stage canvas').screenshot());
      if (mobileCanvas.unique < 10 || mobileCanvas.variance < 1) {
        throw new Error(`mobile canvas looks blank: unique=${mobileCanvas.unique} variance=${mobileCanvas.variance.toFixed(3)}`);
      }
    } finally {
      await mobile.close();
    }

    if (errors.length) throw new Error(errors.join('; '));
    console.log('prior-atlas: OK');
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error('FAIL:', e.message || e);
  process.exit(1);
});
