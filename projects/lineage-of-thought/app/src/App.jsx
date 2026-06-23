import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { loadVaultFromManifest, parseVault } from './lib/parseVault.js';
import { EDGE_COLOR, EDGE_LABEL, regionRGB, tradColor, fmtYear } from './lib/colors.js';
import GlobeView from './components/GlobeView.jsx';
import Timeline from './components/Timeline.jsx';
import Card from './components/Card.jsx';
import { usePortrait } from './lib/portrait.js';

const CARD_ORDER = ['how-we-learn', 'examined-life', 'the-self', 'human-nature', 'compassion', 'reason-revelation', 'the-way', 'liberation'];

// Map between a thread's step-progress (0..n-1, constant pace per hop) and calendar year.
function progFromYear(steps, year) {
  const n = steps.length; if (!n) return 0;
  if (year <= steps[0].year) return 0;
  if (year >= steps[n - 1].year) return n - 1;
  for (let i = 0; i < n - 1; i++) { const a = steps[i].year, b = steps[i + 1].year; if (year <= b) return i + (b > a ? (year - a) / (b - a) : 0); }
  return n - 1;
}
function yearFromProg(steps, p) {
  const n = steps.length; if (!n) return 0;
  const i = Math.max(0, Math.min(n - 1, Math.floor(p))); const f = p - i;
  const a = steps[i].year, b = steps[Math.min(n - 1, i + 1)].year; return a + (b - a) * f;
}

export default function App() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);
  const [year, setYear] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [hoveredId, setHoveredId] = useState(null);
  const [pop, setPop] = useState(null); // {id, x, y}
  const [filters, setFilters] = useState({ influence: true, derivation: true, disagreement: true, revival: true });
  const [playing, setPlaying] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [obsidianVault, setObsidianVault] = useState(() => localStorage.getItem('lot_obsidianVault') || '');
  const [vaultPath, setVaultPath] = useState(() => localStorage.getItem('lot_vaultPath') || '');
  useEffect(() => { localStorage.setItem('lot_obsidianVault', obsidianVault); localStorage.setItem('lot_vaultPath', vaultPath); }, [obsidianVault, vaultPath]);
  const [threads, setThreads] = useState([]);
  const [threadId, setThreadId] = useState(null);
  useEffect(() => { fetch('/threads.json').then((r) => r.json()).then(setThreads).catch(() => {}); }, []);
  const [showOverlay, setShowOverlay] = useState(true);
  const [pinCamera, setPinCamera] = useState(false);
  const [centers, setCenters] = useState([]);
  useEffect(() => { fetch('/centers.json').then((r) => r.json()).then(setCenters).catch(() => {}); }, []);

  useEffect(() => {
    loadVaultFromManifest('/vault')
      .then((d) => { setData(d); const yrs = d.thinkers.flatMap((t) => [t.born, t.died].filter((v) => v != null)); setYear(Math.max(...yrs)); })
      .catch((e) => setErr(e.message));
  }, []);

  const range = useMemo(() => {
    if (!data) return [-600, 2000];
    const yrs = data.thinkers.flatMap((t) => [t.born, t.died].filter((v) => v != null));
    return [Math.min(...yrs) - 20, Math.max(...yrs) + 20];
  }, [data]);

  // centre of gravity = centroid of the DOMINANT region's active thinkers at this year
  // the world's centres of gravity — MULTIPLE hubs can be active at once (multipolar history)
  const worldCenters = useMemo(() => centers.filter((c) => year != null && year >= c.from && year <= c.to)
    .sort((a, b) => (a.tier - b.tier) || (b.from - a.from)), [centers, year]);
  const cog = useMemo(() => {
    if (!worldCenters.length) return null;
    const top = worldCenters[0];
    return { lat: top.lat, lon: top.lon, region: top.place, detail: top.detail, others: worldCenters.slice(1, 5).map((c) => c.place) };
  }, [worldCenters]);

  // density-warped time axis: dense eras get more width (blend of linear time + CDF of thinkers)
  const timeMap = useMemo(() => {
    const [mn, mx] = range;
    const years = data ? data.thinkers.map((t) => t.born ?? t.floruit ?? t.died).filter((v) => v != null).sort((a, b) => a - b) : [];
    const N = years.length || 1;
    const cdf = (y) => { let lo = 0, hi = years.length; while (lo < hi) { const m = (lo + hi) >> 1; if (years[m] <= y) lo = m + 1; else hi = m; } return lo / N; };
    const lin = (y) => (mx > mn ? (y - mn) / (mx - mn) : 0);
    const toFrac = (y) => 0.4 * lin(y) + 0.6 * cdf(y);
    const toYear = (f) => { let lo = mn, hi = mx; for (let i = 0; i < 42; i++) { const m = (lo + hi) / 2; if (toFrac(m) < f) lo = m; else hi = m; } return (lo + hi) / 2; };
    return { toFrac, toYear };
  }, [data, range]);

  // idea-thread tracing: ordered steps + which one the "ball" is at for the current year
  const thread = useMemo(() => threads.find((t) => t.id === threadId) || null, [threads, threadId]);
  const threadSteps = useMemo(() => {
    if (!thread || !data) return [];
    return thread.steps.map((s) => { const t = data.byId[s.id]; if (!t) return null; const yr = (t.born != null && t.died != null) ? Math.round((t.born + t.died) / 2) : (t.floruit ?? t.born ?? t.died); return { ...s, t, year: yr }; })
      .filter(Boolean).sort((a, b) => a.year - b.year);
  }, [thread, data]);
  const threadIndex = useMemo(() => { let idx = -1; for (let i = 0; i < threadSteps.length; i++) if (threadSteps[i].year <= year) idx = i; return idx; }, [threadSteps, year]);
  const threadObj = thread ? { id: thread.id, color: thread.color, steps: threadSteps, index: threadIndex } : null;
  const threadCards = useMemo(() => {
    if (!data) return [];
    return threads.map((t) => {
      const steps = t.steps.map((s) => data.byId[s.id]).filter(Boolean);
      const yrs = steps.map((x) => x.born ?? x.floruit ?? x.died).filter((v) => v != null);
      return { id: t.id, name: t.name, color: t.color, summary: t.summary, count: steps.length,
        minY: yrs.length ? Math.min(...yrs) : null, maxY: yrs.length ? Math.max(...yrs) : null,
        regions: [...new Set(steps.map((x) => x.region))].length };
    }).sort((a, b) => ((CARD_ORDER.indexOf(a.id) + 1) || 99) - ((CARD_ORDER.indexOf(b.id) + 1) || 99));
  }, [threads, data]);

  useEffect(() => {
    if (!playing || !data) return;
    let raf, last = performance.now(); const span = range[1] - range[0];
    const threadMode = threadId && threadSteps.length > 1;
    // track a CONTINUOUS progress so the ball glides at constant pace; year stays a float (no quantization → no stutter)
    let prog = threadMode ? progFromYear(threadSteps, year) : 0;
    const step = (now) => {
      const dt = Math.min(0.05, (now - last) / 1000); last = now; // clamp dt so a stalled frame doesn't jump
      if (threadMode) {
        prog += dt * 0.7;
        if (prog >= threadSteps.length - 1) { setPlaying(false); setYear(threadSteps[threadSteps.length - 1].year); return; }
        setYear(yearFromProg(threadSteps, prog));
      } else {
        setYear((y) => { const ny = y + dt * span / 26; if (ny >= range[1]) { setPlaying(false); return range[1]; } return ny; });
      }
      raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step); return () => cancelAnimationFrame(raf);
  }, [playing, data, range, threadId, threadSteps]); // eslint-disable-line

  const select = useCallback((id) => {
    setSelectedId(id); setPop(null);
    const t = data?.byId[id];
    if (t) { const prime = (t.born != null && t.died != null) ? Math.round((t.born + t.died) / 2) : (t.floruit ?? t.died ?? t.born); if (prime != null) setYear(prime); }
  }, [data]);
  const hoverDot = useCallback((id, x, y) => { setHoveredId(id); setPop(id ? { id, x, y } : null); }, []);
  const scrubBy = useCallback((deltaY) => {
    setPlaying(false);
    if (threadId && threadSteps.length > 1) {
      // thread mode: advance progress ALONG THE PATH at a constant pace (no dwell at uneven year-gaps)
      setYear((y) => { const p = progFromYear(threadSteps, y); const np = Math.max(0, Math.min(threadSteps.length - 1, p + deltaY * 0.0016)); return yearFromProg(threadSteps, np); });
    } else {
      setYear((y) => { const f = timeMap.toFrac(y); const nf = Math.max(0, Math.min(1, f + deltaY * 0.0006)); return Math.round(timeMap.toYear(nf)); });
    }
  }, [timeMap, threadId, threadSteps]);
  const activateThread = useCallback((id) => {
    setSelectedId(null); setSettingsOpen(false); setThreadId(id);
    const th = threads.find((x) => x.id === id);
    if (th && data) { const ys = th.steps.map((s) => data.byId[s.id]).filter(Boolean).map((t) => (t.born != null && t.died != null) ? (t.born + t.died) / 2 : (t.floruit ?? t.born ?? t.died)); if (ys.length) setYear(Math.round(Math.min(...ys))); }
  }, [threads, data]);
  const exitThread = useCallback(() => setThreadId(null), []);
  // arrow keys: → / ← jump node-to-node along the active thread (else nudge time)
  useEffect(() => {
    const onKey = (e) => {
      if (showOverlay) return;
      const tag = e.target && e.target.tagName; if (tag === 'INPUT' || tag === 'TEXTAREA') return;
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      e.preventDefault(); setPlaying(false);
      if (threadId && threadSteps.length) {
        const i = threadIndex, n = threadSteps.length; let target;
        if (e.key === 'ArrowRight') target = i < 0 ? 0 : Math.min(n - 1, i + 1);
        else { const atNode = i >= 0 && Math.abs(year - threadSteps[i].year) < 1; target = i < 0 ? 0 : Math.max(0, atNode ? i - 1 : i); }
        setYear(threadSteps[target].year);
      } else {
        const span = range[1] - range[0];
        setYear((y) => Math.max(range[0], Math.min(range[1], Math.round(y + (e.key === 'ArrowRight' ? 1 : -1) * span / 80))));
      }
    };
    window.addEventListener('keydown', onKey); return () => window.removeEventListener('keydown', onKey);
  }, [showOverlay, threadId, threadSteps, threadIndex, year, range]);

  // expose for headless verification
  useEffect(() => {
    window.__viz = {
      state: () => ({ loaded: !!data, thinkers: data?.thinkers.length || 0, edges: data?.edges.length || 0,
        year, range, selected: selectedId, hovered: hoveredId, playing, filters, cogRegion: cog ? cog.region : null }),
      get: (id) => data?.byId[id] || null, select, setYear, play: () => setPlaying(true), pause: () => setPlaying(false),
      trace: (id) => { setShowOverlay(false); activateThread(id); }, untrace: () => exitThread(), threadIds: () => threads.map((t) => t.id),
      threadState: () => threadObj ? { id: threadObj.id, index: threadObj.index, steps: threadSteps.map((s) => ({ id: s.t.id, year: s.year, region: s.t.region })) } : null,
    };
  }, [data, year, range, selectedId, hoveredId, playing, filters, select, threads, threadObj, threadSteps, activateThread, exitThread, cog]);

  if (err) return <div className="center-msg">Couldn't load the vault.<br />{err}<br /><br />Run <code>npm run dev</code> from <code>app/</code>.</div>;
  if (!data || year == null) return <div className="center-msg">Loading the lineage…</div>;

  return (
    <>
      <GlobeView data={data} year={year} filters={filters} selectedId={selectedId} hoveredId={hoveredId}
        cog={cog} centers={worldCenters} thread={threadObj} pinned={pinCamera} onSelect={select} onHover={setHoveredId} onScrub={scrubBy} />
      <div className="bar">
        <div className="brand"><b>Lineage of Thought</b><span>{data.thinkers.length} thinkers · {data.edges.length} links · to {fmtYear(year)}</span></div>
        <div className="spacer" />
        <ThreadMenu threads={threads} activeId={threadId} onOpen={() => setShowOverlay(true)} onExit={exitThread} />
        <SearchBox data={data} onPick={select} />
        <button className={'btn gear' + (settingsOpen ? ' on' : '')} onClick={() => setSettingsOpen((o) => !o)} title="Settings" aria-label="Settings">⚙</button>
      </div>
      {settingsOpen && <Settings data={data} filters={filters} setFilters={setFilters} onClose={() => setSettingsOpen(false)}
        onLoadVault={(d) => { setData(d); const yrs = d.thinkers.flatMap((t) => [t.born, t.died].filter((v) => v != null)); setYear(Math.max(...yrs)); }}
        obsidianVault={obsidianVault} setObsidianVault={setObsidianVault} vaultPath={vaultPath} setVaultPath={setVaultPath}
        pinCamera={pinCamera} setPinCamera={setPinCamera} />}
      <Timeline data={data} year={year} range={range} cog={cog} centers={worldCenters} timeMap={timeMap} thread={threadObj} onYear={(y) => { setYear(y); setPlaying(false); }}
        onHover={hoverDot} onSelect={select} hoveredId={hoveredId} selectedId={selectedId}
        playing={playing} onTogglePlay={() => setPlaying((p) => { if (year >= range[1]) setYear(range[0]); return !p; })} />
      {pop && <Popover t={data.byId[pop.id]} x={pop.x} y={pop.y} />}
      {threadObj && <ThreadPanel thread={thread} steps={threadSteps} index={threadIndex} onExit={exitThread} onStep={(i) => { setPlaying(false); setYear(threadSteps[i].year); }} onSelect={select} />}
      {showOverlay && threadCards.length > 0 && <ThreadOverlay cards={threadCards} onPick={(id) => { activateThread(id); setShowOverlay(false); }} onClose={() => setShowOverlay(false)} />}
      <Card data={data} id={selectedId} onClose={() => setSelectedId(null)} onSelect={select} obsidianVault={obsidianVault} vaultPath={vaultPath} />
    </>
  );
}

function lev(a, b) {
  const m = a.length, n = b.length; if (!m) return n; if (!n) return m;
  let prev = Array.from({ length: n + 1 }, (_, i) => i);
  for (let i = 1; i <= m; i++) { const cur = [i]; for (let j = 1; j <= n; j++) cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)); prev = cur; }
  return prev[n];
}
function score(name, q) {
  const N = name.toLowerCase(), Q = q.toLowerCase();
  if (N.startsWith(Q)) return 1000 - N.length;
  if (N.includes(Q)) return 800 - N.indexOf(Q);
  let i = 0; for (const c of N) { if (c === Q[i]) i++; if (i === Q.length) break; } if (i === Q.length) return 500; // subsequence (missing letters)
  const words = N.split(/\s+/); let best = lev(Q, N); for (const w of words) best = Math.min(best, lev(Q, w)); // typo tolerance
  if (best <= Math.max(1, Math.ceil(Q.length * 0.34))) return 300 - best * 10;
  return -1;
}
function SearchBox({ data, onPick }) {
  const [q, setQ] = useState(''); const [open, setOpen] = useState(false); const [act, setAct] = useState(0);
  const results = useMemo(() => {
    if (!q.trim()) return [];
    return data.thinkers.map((t) => ({ t, s: score(t.name, q.trim()) })).filter((r) => r.s > 0).sort((a, b) => b.s - a.s).slice(0, 7).map((r) => r.t);
  }, [q, data]);
  useEffect(() => setAct(0), [q]);
  const pick = (t) => { if (!t) return; onPick(t.id); setQ(''); setOpen(false); };
  return (
    <div className="searchwrap">
      <input className="search" placeholder="find a thinker…" value={q} autoComplete="off"
        onChange={(e) => { setQ(e.target.value); setOpen(true); }} onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 160)}
        onKeyDown={(e) => {
          if (e.key === 'ArrowDown') { e.preventDefault(); setAct((a) => Math.min(results.length - 1, a + 1)); }
          else if (e.key === 'ArrowUp') { e.preventDefault(); setAct((a) => Math.max(0, a - 1)); }
          else if (e.key === 'Enter') { pick(results[act]); } else if (e.key === 'Escape') { setOpen(false); }
        }} />
      {open && q.trim() && (
        <div className="dropdown">
          {results.length ? results.map((t, i) => (
            <div key={t.id} className={'item' + (i === act ? ' active' : '')} onMouseEnter={() => setAct(i)} onMouseDown={(e) => { e.preventDefault(); pick(t); }}>
              <span className="d" style={{ background: tradColor(t.tradition) }} />
              <span className="nm">{t.name}</span>
              <span className="yr">{t.born != null ? fmtYear(t.born) : ''}</span>
            </div>
          )) : <div className="empty">No match — try fewer letters</div>}
        </div>
      )}
    </div>
  );
}

function OpenVault({ onLoad }) {
  async function open() {
    if (!window.showDirectoryPicker) { alert('Use Chrome/Edge/Brave to open a vault folder.'); return; }
    try {
      const dir = await window.showDirectoryPicker(); const out = [];
      async function walk(d) { for await (const [name, h] of d.entries()) { if (h.kind === 'file' && /\.md$/i.test(name)) out.push({ name, text: await (await h.getFile()).text() }); else if (h.kind === 'directory') await walk(h); } }
      await walk(dir); if (out.length) onLoad(parseVault(out));
    } catch (e) { if (e?.name !== 'AbortError') alert('Could not read folder: ' + e.message); }
  }
  return <button className="btn on" onClick={open}>Open vault…</button>;
}

function Settings({ data, filters, setFilters, onClose, onLoadVault, obsidianVault, setObsidianVault, vaultPath, setVaultPath, pinCamera, setPinCamera }) {
  const regions = useMemo(() => [...new Set(data.thinkers.map((t) => t.region))], [data]);
  return (
    <div className="settings">
      <div className="x" onClick={onClose}>×</div>
      <h4>Camera</h4>
      <label className="set-check"><input type="checkbox" checked={pinCamera} onChange={(e) => setPinCamera(e.target.checked)} /> Keep camera pinned to the idea (else free to drag)</label>
      <h4>Vault</h4>
      <OpenVault onLoad={onLoadVault} />
      <label className="set-label">Obsidian vault name
        <input value={obsidianVault} onChange={(e) => setObsidianVault(e.target.value)} placeholder="e.g. MyVault" /></label>
      <label className="set-label">Notes folder path
        <input value={vaultPath} onChange={(e) => setVaultPath(e.target.value)} /></label>
      <h4>Regions</h4>
      {regions.map((r) => <div className="lg" key={r}><span className="dot" style={{ background: regionRGB(r) }} /><span>{r}</span></div>)}
      <h4>Edges — click to filter</h4>
      {Object.keys(EDGE_COLOR).map((t) => (
        <div className={'lg' + (filters[t] ? '' : ' off')} key={t} onClick={() => setFilters((f) => ({ ...f, [t]: !f[t] }))}>
          <span className="sw" style={{ background: EDGE_COLOR[t] }} /><span>{EDGE_LABEL[t]}</span>
        </div>
      ))}
    </div>
  );
}

function Popover({ t, x, y }) {
  if (!t) return null;
  const left = Math.min(x + 14, window.innerWidth - 216);
  const top = Math.max(12, y - 150);
  return (
    <div className="pop" style={{ left, top }}>
      {t.portrait && <img src={t.portrait} alt="" onError={(e) => { e.target.style.display = 'none'; }} />}
      <div className="pb">
        <b>{t.name}</b>
        <div className="pm">{t.born != null ? fmtYear(t.born) : ''}{t.died != null ? ' – ' + fmtYear(t.died) : ''} · {t.region}</div>
        {t.thesis && <div className="pt">{t.thesis}</div>}
      </div>
    </div>
  );
}

function ThreadMenu({ threads, activeId, onOpen, onExit }) {
  const active = threads.find((t) => t.id === activeId);
  if (active) return <button className="btn on threadbtn" onClick={onExit} title="Stop tracing this idea">◉ {active.name} ✕</button>;
  return <button className="btn" onClick={onOpen} title="Browse ideas to trace">✦ Ideas</button>;
}

function ThreadOverlay({ cards, onPick, onClose }) {
  useEffect(() => { const k = (e) => { if (e.key === 'Escape') onClose(); }; window.addEventListener('keydown', k); return () => window.removeEventListener('keydown', k); }, [onClose]);
  return (
    <div className="overlay" onClick={(e) => { if (e.target.classList.contains('overlay')) onClose(); }}>
      <div className="ov-inner">
        <div className="ov-hero">
          <h1>What is education?</h1>
          <p>pick a question — watch the idea travel across space and time</p>
        </div>
        <div className="ov-grid">
          {cards.map((c) => (
            <button key={c.id} className="ov-card" style={{ '--accent': c.color }} onClick={() => onPick(c.id)}>
              <div className="ov-dot" style={{ background: c.color }} />
              <h3>{c.name}</h3>
              <div className="reveal">
                <p>{c.summary}</p>
                <div className="ov-meta">{c.count} thinkers · {c.minY != null ? fmtYear(c.minY) : '?'} → {c.maxY != null ? fmtYear(c.maxY) : '?'} · {c.regions} regions</div>
              </div>
            </button>
          ))}
        </div>
        <button className="ov-skip" onClick={onClose}>explore the globe freely →</button>
      </div>
    </div>
  );
}

function ThreadPanel({ thread, steps, index, onExit, onStep, onSelect }) {
  const cur = index >= 0 ? steps[index] : null;
  const prev = index > 0 ? steps[index - 1] : null;
  const portrait = usePortrait(cur ? cur.t : null);
  return (
    <div className="threadpanel">
      <div className="x" onClick={onExit}>×</div>
      <div className="tp-head"><span className="tp-dot" style={{ background: thread.color }} /><b>{thread.name}</b></div>
      <div className="tp-steps">{steps.map((s, i) => <span key={s.t.id} className={'tp-step' + (i === index ? ' cur' : '')} title={`${s.t.name} · ${fmtYear(s.year)}`} onClick={() => onStep(i)} style={{ background: i <= index ? thread.color : 'rgba(150,160,190,.25)' }} />)}</div>
      {cur ? (
        <div className="tp-cur">
          {portrait ? <img className="tp-portrait" src={portrait} alt="" onError={(e) => { e.target.style.display = 'none'; }} /> : null}
          <div className="tp-name" onClick={() => onSelect(cur.t.id)}>{cur.t.name}</div>
          <div className="tp-where">{fmtYear(cur.year)} · {cur.t.place ? cur.t.place.split(/[,/(]/)[0].trim() : cur.t.region}</div>
          <div className="tp-note">“{cur.note}”</div>
          {prev
            ? <div className="tp-trans"><span className="tp-tl">↑ carried from {prev.t.name}</span>{prev.note}</div>
            : <div className="tp-trans"><span className="tp-tl">where the idea begins</span></div>}
          <div className="tp-prog">{index + 1} / {steps.length} · ← → or scroll to pass it on</div>
        </div>
      ) : <div className="tp-cur"><div className="tp-note">Scroll forward to pick up the idea…</div></div>}
    </div>
  );
}
