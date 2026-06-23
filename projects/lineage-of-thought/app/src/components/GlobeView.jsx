import React, { useRef, useEffect, useState, useMemo } from 'react';
import Globe from 'react-globe.gl';
import * as THREE from 'three';
import { EDGE_COLOR, tradColor } from '../lib/colors.js';

const TEX = 'https://cdn.jsdelivr.net/npm/three-globe/example/img/';

const DIM_POINT = 'rgba(120,140,180,0.16)';
const DIM_ARC = 'rgba(120,140,180,0.05)';
const activeAt = (t, year) => { const s = t.born ?? t.floruit ?? t.died; return s != null && s <= year; };
function hexA(hex, a) { const c = (hex || '#ffffff').replace('#', ''); const r = parseInt(c.slice(0, 2), 16), g = parseInt(c.slice(2, 4), 16), b = parseInt(c.slice(4, 6), 16); return `rgba(${r},${g},${b},${a})`; }
function angDist(la1, lo1, la2, lo2) { const R = Math.PI / 180; const dLa = (la2 - la1) * R, dLo = (lo2 - lo1) * R; const a = Math.sin(dLa / 2) ** 2 + Math.cos(la1 * R) * Math.cos(la2 * R) * Math.sin(dLo / 2) ** 2; return 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)) / R; }
const shortPlace = (p) => (p || '').split(/[,/(]/)[0].trim();

let GLOW_TEX = null;
function glowTexture() {
  if (GLOW_TEX) return GLOW_TEX;
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const x = c.getContext('2d'); const g = x.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.22, 'rgba(255,255,255,0.85)');
  g.addColorStop(0.55, 'rgba(255,255,255,0.25)'); g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g; x.fillRect(0, 0, 64, 64);
  GLOW_TEX = new THREE.CanvasTexture(c); return GLOW_TEX;
}

export default function GlobeView({ data, year, filters, selectedId, hoveredId, cog, centers, thread, pinned, onSelect, onHover, onScrub }) {
  const globeEl = useRef();
  const containerRef = useRef();
  const ballRef = useRef(null);
  const cloudsRef = useRef(null);
  const spritesRef = useRef({});
  const yearRef = useRef(0); const focusRef = useRef(null); const egoRef = useRef(null); const threadRef = useRef(null);
  const [countries, setCountries] = useState({ features: [] });
  const [size, setSize] = useState({ w: window.innerWidth, h: window.innerHeight });
  const [labelSz, setLabelSz] = useState(0.42); // driven by camera altitude so labels stay readable at any zoom
  const inThread = !!thread;

  useEffect(() => {
    fetch('/countries.geojson').then((r) => r.json()).then(setCountries).catch(() => {});
    const onResize = () => setSize({ w: window.innerWidth, h: window.innerHeight });
    window.addEventListener('resize', onResize); return () => window.removeEventListener('resize', onResize);
  }, []);

  useEffect(() => {
    if (!globeEl.current) return;
    const c = globeEl.current.controls();
    c.autoRotate = false; c.enableDamping = true; c.enableZoom = true; c.enablePan = false; c.rotateSpeed = 0.55;
    c.zoomSpeed = 1.1; c.minDistance = 108; c.maxDistance = 580; // native trackpad pinch + scroll zoom, with limits
    globeEl.current.pointOfView({ lat: 20, lng: 60, altitude: 2.4 }, 0);
    window.__globePOV = () => globeEl.current && globeEl.current.pointOfView();
  }, []);
  // while tracing an idea, scroll advances the thread → disable native zoom so the wheel handler owns it
  useEffect(() => { const g = globeEl.current; if (!g || typeof g.controls !== 'function') return; const c = g.controls(); if (c) c.enableZoom = !inThread; }, [inThread]);
  // keep labels a roughly constant on-screen size across zoom levels (label geo-size ∝ altitude)
  useEffect(() => {
    const g = globeEl.current; if (!g || typeof g.controls !== 'function') return; const c = g.controls(); if (!c) return;
    let t = 0; const onChange = () => { if (t) return; t = setTimeout(() => { t = 0; const alt = (g.pointOfView() || {}).altitude || 2.4; setLabelSz(Math.max(0.16, Math.min(0.85, alt * 0.2))); }, 100); };
    c.addEventListener('change', onChange); onChange();
    return () => { c.removeEventListener('change', onChange); if (t) clearTimeout(t); };
  }, []);

  // realistic earth: specular ocean + drifting clouds + a sun for relief shading.
  // All best-effort & guarded — the Blue Marble + bump map already apply via props.
  useEffect(() => {
    const G = globeEl.current; if (!G) return;
    let raf = 0, scene, clouds, sun, amb;
    const apply = () => {
      try {
        const loader = new THREE.TextureLoader();
        if (typeof G.globeMaterial === 'function' && G.globeMaterial()) {
          const mat = G.globeMaterial(); mat.bumpScale = 8;
          loader.load(TEX + 'earth-water.png', (tex) => { mat.specularMap = tex; mat.specular = new THREE.Color('#1b3a57'); mat.shininess = 16; mat.needsUpdate = true; });
        }
        if (typeof G.scene === 'function') {
          scene = G.scene();
          // dramatic 3D terminator: dim the ambient, strengthen + angle the sun
          let hasDir = false;
          scene.traverse((o) => { if (o.isAmbientLight) o.intensity = 0.42; if (o.isDirectionalLight) { o.intensity = 1.7; o.position.set(-0.5, 0.35, 1); hasDir = true; } });
          if (!hasDir) { const sun = new THREE.DirectionalLight(0xffffff, 1.7); sun.position.set(-0.5, 0.35, 1); scene.add(sun); }
          const R = (typeof G.getGlobeRadius === 'function') ? G.getGlobeRadius() : 100;
          clouds = new THREE.Mesh(new THREE.SphereGeometry(R * 1.012, 72, 54),
            new THREE.MeshPhongMaterial({ transparent: true, opacity: 0.4, depthWrite: false }));
          loader.load('https://cdn.jsdelivr.net/gh/vasturiano/react-globe.gl@master/example/clouds/clouds.png', (tex) => { clouds.material.map = tex; clouds.material.needsUpdate = true; });
          scene.add(clouds); cloudsRef.current = clouds;
          const spin = () => { raf = requestAnimationFrame(spin); if (cloudsRef.current) cloudsRef.current.rotation.y += 0.0004; };
          raf = requestAnimationFrame(spin);
        }
      } catch (e) { /* niceties are optional */ }
    };
    const t = setTimeout(apply, 80); // let the globe init its material first
    return () => { clearTimeout(t); if (raf) cancelAnimationFrame(raf); if (scene) { if (clouds) scene.remove(clouds); if (sun) scene.remove(sun); if (amb) scene.remove(amb); } };
  }, []);

  // FREE mode: the globe's own controls handle zoom (trackpad pinch + two-finger scroll + wheel).
  // THREAD mode: scroll passes the idea along; pinch/⌘ still zooms.
  useEffect(() => {
    const el = containerRef.current; if (!el) return;
    let accum = 0, raf = 0;
    const onWheel = (e) => {
      if (!threadRef.current) return; // free exploration → leave the wheel to native zoom
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        if (globeEl.current) { const pov = globeEl.current.pointOfView(); globeEl.current.pointOfView({ altitude: Math.max(0.18, Math.min(4.5, pov.altitude * (1 + e.deltaY * 0.0016))) }, 80); }
        return;
      }
      e.preventDefault();
      accum += e.deltaY;
      if (!raf) raf = requestAnimationFrame(() => { if (onScrub) onScrub(accum); accum = 0; raf = 0; });
    };
    el.addEventListener('wheel', onWheel, { passive: false });
    return () => { el.removeEventListener('wheel', onWheel); if (raf) cancelAnimationFrame(raf); };
  }, [onScrub]);

  const focus = hoveredId || selectedId;
  const egoSet = useMemo(() => {
    if (!focus) return null; const s = new Set([focus]);
    for (const e of data.edges) { if (!filters[e.type]) continue; if (e.source === focus) s.add(e.target); if (e.target === focus) s.add(e.source); }
    return s;
  }, [focus, data, filters]);
  yearRef.current = year; focusRef.current = focus; egoRef.current = egoSet; threadRef.current = thread;

  // soft glowing light-points instead of cylinders — camera-facing sprites, occluded by the globe
  const makeSprite = (d) => {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTexture(), color: new THREE.Color(tradColor(d.tradition)), transparent: true, opacity: 0.85, depthWrite: false, blending: THREE.AdditiveBlending }));
    const b = 1.7 + Math.min(2.6, (d.importance || 1) * 0.55); s.scale.set(b, b, 1); s.__t = d; s.__base = b;
    spritesRef.current[d.id] = s; return s;
  };
  const updateSprite = (obj, d) => { const g = globeEl.current; if (!g || typeof g.getCoords !== 'function') return; const c = g.getCoords(d.lat, d.lon, 0.012); obj.position.set(c.x, c.y, c.z); };
  useEffect(() => {
    window.__nodeStats = () => { let v = 0, n = 0; for (const id in spritesRef.current) { n++; if (spritesRef.current[id].visible) v++; } return { visible: v, total: n }; };
    let raf; const loop = () => { raf = requestAnimationFrame(loop);
      const yr = yearRef.current, foc = focusRef.current, eg = egoRef.current, th = threadRef.current, sprs = spritesRef.current;
      const g = globeEl.current;
      if (th) {
        for (const id in sprs) { const s = sprs[id];
          const i = th.steps.findIndex((x) => x.t.id === id);
          if (i < 0) { s.visible = false; continue; }
          s.visible = true; const cur = i === th.index;
          s.scale.setScalar(cur ? s.__base * 2.4 : (i <= th.index ? s.__base * 1.3 : s.__base));
          s.material.color.set(cur ? '#ffffff' : th.color); s.material.opacity = i <= th.index ? 1 : 0.4;
        }
        return;
      }
      // FREE mode: style active nodes, then merge on-screen-near ones (cluster zoomed out → split zoomed in)
      const cam = (g && typeof g.camera === 'function') ? g.camera() : null;
      const vis = [];
      for (const id in sprs) { const s = sprs[id], t = s.__t;
        if (!activeAt(t, yr)) { s.visible = false; continue; }
        const inEgo = !eg || eg.has(id), isFoc = id === foc;
        s.visible = true; s.material.color.set(tradColor(t.tradition));
        s.material.opacity = inEgo ? (isFoc ? 1 : 0.8) : 0.16; s.scale.setScalar(isFoc ? s.__base * 2 : s.__base);
        const front = cam ? s.position.dot(cam.position) > 0 : true; // only near-hemisphere nodes cluster
        let sx = 0, sy = 0, ok = false;
        if (front && g && typeof g.getScreenCoords === 'function') { const c = g.getScreenCoords(t.lat, t.lon); if (c) { sx = c.x; sy = c.y; ok = true; } }
        vis.push({ id, s, sx, sy, ok, isFoc, imp: t.importance || 1 });
      }
      const R = 24; vis.sort((a, b) => b.imp - a.imp); const taken = new Set();
      for (const a of vis) { if (!a.ok || taken.has(a.id) || a.isFoc) continue; let count = 1;
        for (const b of vis) { if (b === a || !b.ok || taken.has(b.id) || b.isFoc) continue;
          const dx = a.sx - b.sx, dy = a.sy - b.sy; if (dx * dx + dy * dy < R * R) { taken.add(b.id); b.s.visible = false; count++; }
        }
        if (count > 1) a.s.scale.setScalar(a.s.__base * (1.2 + Math.min(1.1, count * 0.13))); // cluster grows with how many it holds
      }
    };
    raf = requestAnimationFrame(loop); return () => cancelAnimationFrame(raf);
  }, []);

  // STABLE arrays (independent of year) so react-globe.gl never rebuilds geometry mid-scrub.
  const allPoints = useMemo(() => data.thinkers.filter((t) => t.lat != null && t.lon != null), [data]);
  const allArcs = useMemo(() => data.edges
    .filter((e) => { const a = data.byId[e.source], b = data.byId[e.target]; return a && b && a.lat != null && b.lat != null; })
    .map((e) => ({ ...e, sa: data.byId[e.source], sb: data.byId[e.target] })), [data]);

  // thread mode: path arcs between consecutive steps; the "ball" ring at the current step
  const threadArcs = useMemo(() => inThread ? thread.steps.slice(0, -1).map((s, i) => ({ sa: s.t, sb: thread.steps[i + 1].t, i, type: 'thread' })) : [], [thread, inThread]);
  const threadStepIndexOf = (id) => inThread ? thread.steps.findIndex((s) => s.t.id === id) : -1;

  const points = inThread ? thread.steps.map((s) => s.t) : allPoints;
  const arcs = inThread ? threadArcs : allArcs;
  // the "ball": glides continuously along the path between the current node and the next as the year advances
  const ball = useMemo(() => {
    if (!inThread || !thread.steps.length) return null;
    const i = Math.max(0, thread.index);
    const cur = thread.steps[i], nxt = thread.steps[i + 1];
    if (thread.index < 0 || !nxt) return { lat: cur.t.lat, lon: cur.t.lon }; // rest on the first node before the idea is picked up
    const span = nxt.year - cur.year; const f = span > 0 ? Math.max(0, Math.min(1, (year - cur.year) / span)) : 0;
    return { lat: cur.t.lat + (nxt.t.lat - cur.t.lat) * f, lon: cur.t.lon + (nxt.t.lon - cur.t.lon) * f };
  }, [thread, year, inThread]);
  ballRef.current = ball;
  // active world-centres (multipolar) as amber labels + gentle halos, plus the thread ball + thinker labels
  const centerLabels = (centers || []).map((c) => ({ lat: c.lat, lng: c.lon, text: c.place, kind: 'center' }));
  const threadLabels = inThread ? thread.steps.map((s) => ({ lat: s.t.lat, lng: s.t.lon, text: `${s.t.name}${s.t.place ? ', ' + shortPlace(s.t.place) : ''}`, kind: 'thinker' })) : [];
  const labels = [...centerLabels, ...threadLabels];
  // ripples ONLY while following an idea (the gliding ball) — no resting-state pulses on the globe
  const rings = (inThread && ball && thread.index >= 0) ? [{ lat: ball.lat, lon: ball.lon, kind: 'ball' }] : [];

  // camera: thread ball > selection > centre-of-gravity drift
  const cogKey = cog ? `${Math.round(cog.lat / 3)}_${Math.round(cog.lon / 3)}` : '';
  useEffect(() => {
    if (!globeEl.current || !cog || selectedId || inThread) return;
    const pov = globeEl.current.pointOfView();
    globeEl.current.pointOfView({ lat: cog.lat, lng: cog.lon, altitude: pov.altitude || 2.2 }, 900);
  }, [cogKey, selectedId, inThread]); // eslint-disable-line
  useEffect(() => {
    if (!globeEl.current || inThread || !selectedId) return; const t = data.byId[selectedId];
    if (t && t.lat != null) { const pov = globeEl.current.pointOfView(); globeEl.current.pointOfView({ lat: t.lat, lng: t.lon, altitude: Math.min(pov.altitude || 2.2, 1.9) }, 1000); }
  }, [selectedId, inThread]); // eslint-disable-line
  // follow the ball ONLY while time is actively changing (scroll / arrow / autoplay) or when pinned;
  // otherwise the camera is FREE — drag & zoom however you like. Zoom adapts to the hop distance.
  const lastChangeRef = useRef(0);
  useEffect(() => { lastChangeRef.current = performance.now(); }, [year]);
  useEffect(() => {
    if (!inThread) return; let raf;
    const loop = () => {
      raf = requestAnimationFrame(loop);
      const g = globeEl.current, t = ballRef.current; if (!g || !t) return;
      if (!pinned && (performance.now() - lastChangeRef.current) > 650) return; // idle → leave camera to the user
      const a = thread.steps[Math.max(0, thread.index)]?.t, b = thread.steps[thread.index + 1]?.t || a;
      const hop = (a && b) ? angDist(a.lat, a.lon, b.lat, b.lon) : 0;
      const tAlt = Math.max(0.75, Math.min(2.6, 0.85 + (hop / 180) * 1.9)); // short hop → zoom in, long → out
      const pov = g.pointOfView();
      const dlng = ((t.lon - pov.lng + 540) % 360) - 180, dlat = t.lat - pov.lat, dAlt = tAlt - pov.altitude;
      if (Math.abs(dlat) < 0.05 && Math.abs(dlng) < 0.05 && Math.abs(dAlt) < 0.02) return;
      g.pointOfView({ lat: pov.lat + dlat * 0.14, lng: pov.lng + dlng * 0.14, altitude: pov.altitude + dAlt * 0.08 }, 0);
    };
    raf = requestAnimationFrame(loop); return () => cancelAnimationFrame(raf);
  }, [inThread, pinned]);

  const pointRadius = (d) => {
    if (inThread) { const i = threadStepIndexOf(d.id); if (i < 0) return 0; return i === thread.index ? 0.85 : (i < thread.index ? 0.42 : 0.26); }
    return !activeAt(d, year) ? 0 : (d.id === focus ? 0.7 : 0.24 + Math.min(0.42, (d.importance || 1) * 0.1));
  };
  const pointColor = (d) => {
    if (inThread) { const i = threadStepIndexOf(d.id); if (i === thread.index) return '#ffffff'; if (i < thread.index) return thread.color; if (i > thread.index) return hexA(thread.color, 0.4); return DIM_POINT; }
    return (!egoSet || egoSet.has(d.id)) ? tradColor(d.tradition) : DIM_POINT;
  };
  const arcColor = (e) => {
    if (inThread) return e.i < thread.index ? thread.color : (e.i === thread.index ? hexA(thread.color, 0.6) : hexA(thread.color, 0.2));
    if (!filters[e.type] || !activeAt(e.sa, year) || !activeAt(e.sb, year)) return 'rgba(0,0,0,0)';
    if (!focus) return hexA(EDGE_COLOR[e.type], 0.14); // faint resting web — barely there
    return (e.source === focus || e.target === focus) ? hexA(EDGE_COLOR[e.type], 0.9) : 'rgba(0,0,0,0)'; // only the focused node's threads light up
  };

  const zoomBy = (factor) => { const g = globeEl.current; if (!g) return; const pov = g.pointOfView(); g.pointOfView({ altitude: Math.max(0.18, Math.min(4.5, pov.altitude * factor)) }, 300); };

  return (
    <div ref={containerRef} style={{ position: 'fixed', inset: 0 }}>
      <div className="zoomctl">
        <button onClick={() => zoomBy(0.65)} title="Zoom in">＋</button>
        <button onClick={() => zoomBy(1.5)} title="Zoom out">－</button>
      </div>
      <Globe ref={globeEl} width={size.w} height={size.h} backgroundColor="#070b12"
        globeImageUrl={TEX + 'earth-blue-marble.jpg'} bumpImageUrl={TEX + 'earth-topology.png'}
        showAtmosphere atmosphereColor="#86b8ff" atmosphereAltitude={0.25}
        customLayerData={allPoints} customThreeObject={makeSprite} customThreeObjectUpdate={updateSprite}
        pointsData={allPoints} pointLat={(d) => d.lat} pointLng={(d) => d.lon}
        pointColor={() => 'rgba(0,0,0,0)'} pointAltitude={0.004} pointResolution={2} pointRadius={pointRadius}
        pointLabel={(d) => `<div style="font:600 13px ui-sans-serif;color:#fff">${d.name}</div><div style="font:11px ui-sans-serif;color:#9fb2cf">${d.tradition}</div>`}
        onPointClick={(d) => onSelect(d.id)} onPointHover={(d) => onHover(d ? d.id : null)}
        arcsData={arcs} arcStartLat={(e) => e.sa.lat} arcStartLng={(e) => e.sa.lon}
        arcEndLat={(e) => e.sb.lat} arcEndLng={(e) => e.sb.lon} arcColor={arcColor}
        arcStroke={(e) => (inThread ? (e.i < thread.index ? 0.6 : 0.35) : ((focus && (e.source === focus || e.target === focus)) ? 0.4 : 0.12))} arcAltitudeAutoScale={inThread ? 0.5 : 0.22}
        arcDashLength={inThread ? 0.5 : 1} arcDashGap={inThread ? 0.25 : 0} arcDashAnimateTime={inThread ? 2200 : 0}
        arcsTransitionDuration={0}
        ringsData={rings} ringLat={(d) => d.lat} ringLng={(d) => d.lon}
        ringColor={(d) => d.kind === 'center' ? ((tt) => hexA('#ffce8a', 0.5 * (1 - tt))) : ((tt) => hexA(thread ? thread.color : '#ffffff', 1 - tt))}
        ringMaxRadius={(d) => d.kind === 'center' ? 2.2 : 5} ringPropagationSpeed={(d) => d.kind === 'center' ? 0.9 : 2.2} ringRepeatPeriod={(d) => d.kind === 'center' ? 2200 : 900}
        labelsData={labels} labelLat={(d) => d.lat} labelLng={(d) => d.lng} labelText={(d) => d.text}
        labelSize={(d) => d.kind === 'center' ? labelSz * 1.7 : labelSz} labelDotRadius={(d) => d.kind === 'center' ? labelSz * 0.62 : labelSz * 0.32}
        labelColor={(d) => d.kind === 'center' ? 'rgba(255,216,150,1)' : 'rgba(215,224,240,0.85)'} labelResolution={2}
        labelAltitude={(d) => d.kind === 'center' ? 0.07 : 0.02}
      />
    </div>
  );
}
