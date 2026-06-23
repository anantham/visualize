// Drive the real page through window.__viz and assert on parsed state.
// Run:  python3 -m http.server 4173   (from repo root)
//       npm i -D playwright && npx playwright install chromium
//       node projects/lineage-of-thought/test.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on('pageerror', (e) => { throw new Error('PAGE ERROR: ' + e.message); });
  await page.goto('http://localhost:4173/projects/lineage-of-thought/');

  // wait for the seed vault to parse
  await page.waitForFunction(() => window.__viz && window.__viz.state().loaded, null, { timeout: 10000 });

  const s = await page.evaluate(() => window.__viz.state());
  if (s.source !== 'seed') throw new Error(`expected seed source, got ${s.source}`);
  if (s.thinkers < 20) throw new Error(`expected >=20 thinkers, got ${s.thinkers}`);
  if (s.edges < 20) throw new Error(`expected >=20 edges, got ${s.edges}`);

  // dates parsed (BCE = negative)
  const plato = await page.evaluate(() => window.__viz.get('Plato'));
  if (plato.born !== -428 || plato.died !== -348) throw new Error(`Plato dates: ${plato.born}/${plato.died}`);
  if (plato.region !== 'Greece') throw new Error(`Plato region: ${plato.region}`);

  const data = await page.evaluate(() => window.__viz.data());
  const has = (src, tgt, type) => data.edges.some(e => e.source === src && e.target === tgt && e.type === type);

  // typed edges
  if (!has('Socrates', 'Plato', 'influence')) throw new Error('missing Socrates→Plato influence');
  const rev = data.edges.find(e => e.source === 'Buddha' && e.target === 'Ambedkar' && e.type === 'revival');
  if (!rev) throw new Error('missing Buddha→Ambedkar revival');
  if (rev.gap < 2000) throw new Error(`revival arc should span >2000y, got ${rev.gap}`);

  // crux parsed off a disagreement
  const dis = data.edges.find(e => e.type === 'disagreement' &&
    [e.source, e.target].includes('Aristotle') && [e.source, e.target].includes('Plato'));
  if (!dis || !/universals/i.test(dis.crux || '')) throw new Error(`Aristotle↔Plato crux: ${dis && dis.crux}`);

  // contemporaries by lifespan overlap
  const contemp = await page.evaluate(() => window.__viz.contemporariesOf('Confucius'));
  for (const who of ['Laozi', 'Buddha']) if (!contemp.includes(who)) throw new Error(`Confucius should be contemporary of ${who}`);

  // selection opens the card
  await page.evaluate(() => window.__viz.select('Nietzsche'));
  const sel = await page.evaluate(() => window.__viz.state().selected);
  if (sel !== 'Nietzsche') throw new Error(`select failed: ${sel}`);
  if (!(await page.evaluate(() => document.getElementById('side').classList.contains('open'))))
    throw new Error('card panel did not open on select');

  // edge filter toggles
  await page.evaluate(() => window.__viz.setFilter('disagreement', false));
  if (await page.evaluate(() => window.__viz.state().filters.disagreement)) throw new Error('filter did not toggle off');
  await page.evaluate(() => window.__viz.setFilter('disagreement', true));

  await page.evaluate(() => window.__viz.fit());
  await page.screenshot({ path: 'projects/lineage-of-thought/out.png' });

  console.log(`lineage-of-thought: OK (${s.thinkers} thinkers, ${s.edges} edges)`);
  await browser.close();
})().catch((e) => { console.error('FAIL:', e.message || e); process.exit(1); });
