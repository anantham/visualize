const { chromium } = require('playwright');
const zlib = require('zlib');

const BASE = process.env.BASE_URL || 'http://localhost:4173';

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
    await page.goto(`${BASE}/projects/prior-atlas/?snap=1#0`);
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
    if (!(shape.same.meanH < shape.diff.meanH)) {
      throw new Error(`same-data pair should be flatter: ${shape.same.meanH} !< ${shape.diff.meanH}`);
    }
    if (!(shape.same.maxH < shape.diff.maxH)) {
      throw new Error(`same-data max should be lower: ${shape.same.maxH} !< ${shape.diff.maxH}`);
    }

    await page.evaluate(() => window.__viz.go(2));
    await page.waitForFunction(() => window.__viz.state().act === 2 && window.__viz.state().selected === 0);
    const axis = await page.locator('#axis').textContent();
    const calibration = await page.locator('#calibration').textContent();
    if (!axis.includes('20 bits') || !axis.includes('million×')) throw new Error('axis missing bits + x-factor scale');
    if (!calibration.includes('33 million×') || !calibration.includes('memorization')) {
      throw new Error('calibration peak copy missing 25-bit x-factor framing');
    }

    let panel = await page.locator('#info').evaluate((el) => ({
      shown: el.classList.contains('show'),
      hidden: el.getAttribute('aria-hidden'),
      text: el.textContent,
    }));
    if (!panel.shown || panel.hidden !== 'false') throw new Error('detail panel did not open on terrain act');
    if (!panel.text.includes('bits / char')) throw new Error('detail panel missing divergence unit');
    if (!panel.text.includes('million×') || !panel.text.includes('coverage / memorization')) {
      throw new Error('detail panel missing x-factor or coverage/memorization line');
    }

    await page.evaluate(() => window.__viz.go(3));
    await page.locator('#modelmap [data-name="gpt2"]').click();
    await page.locator('#modelmap [data-name="gpt2-xl"]').click();
    await page.waitForFunction(() => window.__viz.state().pair === 'gpt2|gpt2-xl');
    state = await page.evaluate(() => window.__viz.state());
    if (state.pair !== 'gpt2|gpt2-xl' || !state.matched) throw new Error(`map dots did not select same-data pair: ${state.pair}`);

    await page.evaluate(() => window.__viz.go(4));
    const caveats = await page.locator('.act[data-act="4"]').textContent();
    for (const phrase of ['Curated sample', 'UMAP is lossy', 'not correctness', 'tail shape', 'Scale is second-order']) {
      if (!caveats.includes(phrase)) throw new Error(`missing caveat phrase: ${phrase}`);
    }

    const canvasPng = await page.locator('#stage canvas').screenshot();
    const stats = pngStats(canvasPng);
    if (stats.width < 500 || stats.height < 400) throw new Error(`canvas too small: ${stats.width}x${stats.height}`);
    if (stats.unique < 10 || stats.variance < 1) {
      throw new Error(`canvas looks blank: unique=${stats.unique} variance=${stats.variance.toFixed(3)}`);
    }

    if (errors.length) throw new Error(errors.join('; '));
    await page.screenshot({ path: '/tmp/prior-atlas-check.png' });
    console.log('prior-atlas: OK');
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error('FAIL:', e.message || e);
  process.exit(1);
});
