import React, { useRef, useState, useEffect, useMemo } from 'react';
import { tradColor, fmtYear } from '../lib/colors.js';

const PAD = 14, SVG_H = 52, AXIS_Y = 34;

export default function Timeline({ data, year, range, cog, timeMap, thread, onYear, onHover, onSelect, hoveredId, selectedId, playing, onTogglePlay }) {
  const svgRef = useRef(); const [w, setW] = useState(700); const [scrub, setScrub] = useState(false);
  useEffect(() => {
    if (!svgRef.current) return;
    const ro = new ResizeObserver((es) => setW(es[0].contentRect.width));
    ro.observe(svgRef.current); return () => ro.disconnect();
  }, []);

  const [min, max] = range;
  const xOf = (yr) => PAD + timeMap.toFrac(yr) * (w - 2 * PAD);
  const yrOf = (x) => timeMap.toYear((x - PAD) / (w - 2 * PAD));

  const regions = useMemo(() => {
    const first = {}; for (const t of data.thinkers) { const s = t.born ?? t.floruit ?? t.died ?? 0; if (first[t.region] == null || s < first[t.region]) first[t.region] = s; }
    return Object.keys(first).sort((a, b) => first[a] - first[b]);
  }, [data]);
  const laneY = (r) => { const n = regions.length; const i = Math.max(0, regions.indexOf(r)); return n > 1 ? 8 + (i * 18) / (n - 1) : 16; };

  const ticks = useMemo(() => {
    const steps = [50, 100, 200, 250, 500, 1000]; const step = steps.find((s) => s >= (max - min) / 9) || 1000;
    const out = []; for (let y = Math.ceil(min / step) * step; y < max; y += step) out.push(y); return out;
  }, [min, max]);

  function seek(e) { const r = e.currentTarget.getBoundingClientRect(); onYear(Math.round(Math.max(min, Math.min(max, yrOf(e.clientX - r.left))))); }

  return (
    <div className="timeline">
      <div className="tl-center">{cog?.region
        ? <>◇ <b style={{ color: '#ffce8a' }}>{cog.region}</b>{cog.others && cog.others.length ? <span className="tl-others"> · {cog.others.join(' · ')}</span> : null}{cog.detail ? <span className="tl-detail"> — {cog.detail}</span> : null}</>
        : 'scrub time to watch the world’s centres of gravity shift'}</div>
      <div className="tl-row">
      <button className="btn tl-play" onClick={onTogglePlay} title={playing ? 'Pause' : 'Play through time'}>{playing ? '❚❚' : '▶'}</button>
      <div className="tl-year"><b>{fmtYear(year)}</b><span>centre of the world</span></div>
      <svg className="tl-svg" ref={svgRef} height={SVG_H}
        onPointerDown={(e) => { setScrub(true); e.currentTarget.setPointerCapture(e.pointerId); seek(e); }}
        onPointerMove={(e) => { if (scrub) seek(e); }} onPointerUp={() => setScrub(false)}>
        <line x1={PAD} y1={AXIS_Y} x2={w - PAD} y2={AXIS_Y} stroke="rgba(122,150,200,0.28)" />
        {(() => { let lastX = -999; return ticks.map((t) => { const x = xOf(t); if (x - lastX < 48) return null; lastX = x; return (
          <g key={t}>
            <line x1={x} y1={AXIS_Y - 3} x2={x} y2={AXIS_Y + 3} stroke="rgba(122,150,200,0.45)" />
            <text x={x} y={AXIS_Y + 15} fill="#7f93b5" fontSize="10" textAnchor="middle">{fmtYear(t)}</text>
          </g>); }); })()}
        {/* future region (after current year) shaded */}
        <rect x={xOf(year)} y={0} width={Math.max(0, (w - PAD) - xOf(year))} height={AXIS_Y} fill="rgba(7,11,18,0.45)" />
        {thread && thread.steps.length > 1 && (
          <polyline fill="none" stroke={thread.color} strokeOpacity="0.6" strokeWidth="1.5"
            points={thread.steps.map((s) => `${xOf(s.year)},${laneY(s.t.region)}`).join(' ')} />
        )}
        {data.thinkers.map((t) => {
          const yr = t.born ?? t.floruit ?? t.died; if (yr == null) return null;
          const on = yr <= year; const foc = t.id === hoveredId || t.id === selectedId;
          const inThr = thread ? thread.steps.some((s) => s.t.id === t.id) : true;
          const r = foc ? 6 : 3 + Math.min(3, (t.importance || 1) * 0.7);
          const op = thread ? (inThr ? (on ? 1 : 0.5) : 0.08) : (on ? 1 : 0.28);
          return (
            <circle className="tl-dot" key={t.id} cx={xOf(yr)} cy={laneY(t.region)} r={r}
              fill={tradColor(t.tradition)} opacity={op}
              stroke={foc ? '#fff' : 'none'} strokeWidth={foc ? 1.5 : 0}
              onPointerEnter={(e) => onHover(t.id, e.clientX, e.clientY)} onPointerLeave={() => onHover(null)}
              onPointerDown={(e) => { e.stopPropagation(); onSelect(t.id); }} />
          );
        })}
        <line x1={xOf(year)} y1={2} x2={xOf(year)} y2={AXIS_Y} stroke="#60a5fa" strokeWidth="2" />
        <circle cx={xOf(year)} cy={3} r={5} fill="#60a5fa" stroke="#0b1220" strokeWidth="1.5" />
      </svg>
      </div>
    </div>
  );
}
