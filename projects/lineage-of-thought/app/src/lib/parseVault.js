// Parse Obsidian-style thinker notes (frontmatter + geo + typed [[links]] + cruxes + idea-travel).
const SECTION_MAP = {
  'influenced by': ['influence', 'in'], teacher: ['influence', 'in'], teachers: ['influence', 'in'],
  'studied under': ['influence', 'in'], 'influence on': ['influence', 'out'], students: ['influence', 'out'],
  develops: ['derivation', 'in'], 'derives from': ['derivation', 'in'], 'builds on': ['derivation', 'in'],
  systematizes: ['derivation', 'in'], extends: ['derivation', 'in'],
  'disagreed with': ['disagreement', 'sym'], critiques: ['disagreement', 'sym'], rejects: ['disagreement', 'sym'],
  opposes: ['disagreement', 'sym'], 'disagrees with': ['disagreement', 'sym'],
  revives: ['revival', 'in'], 'revival of': ['revival', 'in'], reinterprets: ['revival', 'in'],
};
function coerceNum(v) {
  if (typeof v === 'number') return v;
  if (typeof v !== 'string') return null;
  let m = v.match(/(-?\d+)\s*(bce|bc)\b/i); if (m) return -Math.abs(+m[1]);
  m = v.match(/(\d+)\s*(ce|ad)\b/i); if (m) return +m[1];
  m = v.match(/^-?\d+(\.\d+)?$/); return m ? parseFloat(v) : null;
}
function parseFrontmatter(text) {
  const fm = {}; let body = text;
  const m = text.match(/^﻿?---\s*\n([\s\S]*?)\n---\s*\n?/);
  if (m) {
    body = text.slice(m[0].length);
    for (const line of m[1].split('\n')) {
      const i = line.indexOf(':'); if (i < 0) continue;
      const k = line.slice(0, i).trim(); let v = line.slice(i + 1).trim();
      if (v === 'true') v = true; else if (v === 'false') v = false;
      else if (/^-?\d+(\.\d+)?$/.test(v)) v = parseFloat(v);
      fm[k] = v;
    }
  }
  return { fm, body };
}
function parseLinkLine(line) {
  const lm = line.match(/\[\[([^\]]+)\]\]/); if (!lm) return null;
  const target = lm[1].split('|')[0].trim();
  const rest = line.slice(line.indexOf(']]') + 2);
  let crux = null, note = null;
  const parts = rest.split(/\s[—–-]\s/); const head = parts[0];
  if (parts.length > 1) note = parts.slice(1).join(' - ').trim();
  if (head.includes('::')) crux = head.split('::')[1].trim();
  return { target, crux, note };
}
export function parseVault(files) {
  const thinkers = {}; const raw = [];
  for (const f of files) {
    const id = f.name.replace(/\.md$/i, '');
    const { fm, body } = parseFrontmatter(f.text);
    const lines = body.split('\n');
    let desc = '';
    for (const ln of lines) { const t = ln.trim(); if (t && !t.startsWith('#') && !t.startsWith('-') && !t.startsWith('*')) { desc = t; break; } }
    const aLat = coerceNum(fm.active_lat), aLon = coerceNum(fm.active_lon),
          bLat = coerceNum(fm.birth_lat), bLon = coerceNum(fm.birth_lon);
    const th = {
      id, name: fm.name || id, born: coerceNum(fm.born), died: coerceNum(fm.died), floruit: coerceNum(fm.floruit),
      region: fm.region || '—', tradition: fm.tradition || '—', uncertain: !!fm.uncertain,
      importance: (typeof fm.importance === 'number' ? fm.importance : null),
      portrait: fm.portrait || '', wikipedia: fm.wikipedia || '', thesis: fm.thesis || '', key_work: fm.key_work || '',
      lat: aLat != null ? aLat : bLat, lon: aLon != null ? aLon : bLon, birthLat: bLat, birthLon: bLon,
      place: (fm.active_place || fm.birth_place || '').toString(),
      verified_by: fm.verified_by || '', desc, cruxes: [], travel: [],
    };
    thinkers[id] = th;
    let sec = null;
    for (const ln of lines) {
      const h = ln.match(/^#{1,6}\s+(.*)$/); if (h) { sec = h[1].trim().toLowerCase(); continue; }
      const li = ln.match(/^\s*[-*]\s+(.*)$/); if (!li || !sec) continue;
      if (sec === 'cruxes' || sec === 'crux') { const p = parseLinkLine(li[1]); if (p) th.cruxes.push({ crux: p.target, stance: p.note || '' }); continue; }
      if (sec === 'idea travel') { const tm = li[1].match(/^\s*(-?\d{1,4})\s*[—–-]\s*(.*)$/); if (tm) th.travel.push({ year: +tm[1], text: tm[2].trim() }); continue; }
      const map = SECTION_MAP[sec]; if (!map) continue;
      const p = parseLinkLine(li[1]); if (!p) continue;
      raw.push({ owner: id, linked: p.target, type: map[0], dir: map[1], crux: p.crux, note: p.note });
    }
  }
  const byLower = {}; for (const id in thinkers) byLower[id.toLowerCase()] = id;
  const edges = []; const seen = new Set();
  for (const e of raw) {
    const lid = byLower[(e.linked || '').toLowerCase()]; if (!lid || !thinkers[e.owner]) continue;
    let s, t; if (e.dir === 'out') { s = e.owner; t = lid; } else { s = lid; t = e.owner; }
    const k = s + '→' + t + '·' + e.type; if (seen.has(k)) continue; seen.add(k);
    edges.push({ source: s, target: t, type: e.type, crux: e.crux || null, note: e.note || null, mutual: e.dir === 'sym' });
  }
  const deg = {}; for (const id in thinkers) deg[id] = 0;
  for (const e of edges) { deg[e.source]++; deg[e.target]++; }
  for (const id in thinkers) if (thinkers[id].importance == null) thinkers[id].importance = 1 + deg[id];
  const list = Object.values(thinkers).sort((a, b) => (a.born ?? 0) - (b.born ?? 0));
  return { thinkers: list, byId: thinkers, edges };
}
export async function loadVaultFromManifest(base = '/vault') {
  const manifest = await fetch(`${base}/manifest.json`).then((r) => { if (!r.ok) throw new Error('no manifest'); return r.json(); });
  const files = await Promise.all(manifest.map(async (name) => ({ name, text: await fetch(`${base}/${encodeURIComponent(name)}`).then((r) => r.text()) })));
  return parseVault(files);
}
