import React from 'react';
import { EDGE_COLOR, tradColor, fmtYear } from '../lib/colors.js';
import { usePortrait } from '../lib/portrait.js';

const span = (t) => t.born != null ? `${fmtYear(t.born)}${t.died != null ? ' – ' + fmtYear(t.died) : ''}${t.uncertain ? ' (approx.)' : ''}` : (t.floruit != null ? 'fl. ' + fmtYear(t.floruit) : '');

export default function Card({ data, id, onClose, onSelect, obsidianVault, vaultPath }) {
  const t = id ? data.byId[id] : null;
  const portrait = usePortrait(t);
  const E = data.edges;
  const rows = t ? {
    inflBy: E.filter((e) => e.target === id && e.type === 'influence'),
    dev: E.filter((e) => e.target === id && e.type === 'derivation'),
    rev: E.filter((e) => e.target === id && e.type === 'revival'),
    revBy: E.filter((e) => e.source === id && e.type === 'revival'),
    dis: E.filter((e) => e.type === 'disagreement' && (e.source === id || e.target === id)),
  } : null;
  const other = (e) => (e.source === id ? e.target : e.source);
  const Row = ({ tid, sub }) => { const x = data.byId[tid]; if (!x) return null;
    return <a onClick={() => onSelect(tid)}>{x.name} <span className="yr">{x.born != null ? fmtYear(x.born) : ''}</span>{sub ? <><br /><span className="sub" dangerouslySetInnerHTML={{ __html: sub }} /></> : null}</a>; };
  const Block = ({ title, color, items }) => items && items.length
    ? <div className="rel"><h5><span className="b" style={{ background: color }} />{title}</h5>{items}</div> : null;

  return (
    <aside className={'card' + (t ? ' open' : '')}>
      <div className="x" onClick={onClose}>×</div>
      {t && <>
        {portrait ? <img className="portrait" src={portrait} alt="" onError={(e) => { e.target.style.display = 'none'; }} /> : null}
        <div className="cb">
          <h2>{t.name}</h2>
          <div className="meta">{span(t)}{t.verified_by ? <> · <span style={{ color: '#5eead4' }}>✓ {t.verified_by}</span></> : null}</div>
          <span className="chip">{t.region}</span>
          <span className="chip" style={{ borderColor: tradColor(t.tradition) + '66', color: tradColor(t.tradition) }}>{t.tradition}</span>
          {t.thesis && <div className="thesis">{t.thesis}</div>}
          {t.desc && <div className="desc">{t.desc}</div>}
          <Block title="Influenced by" color={EDGE_COLOR.influence} items={rows.inflBy.map((e) => <Row key={'i' + e.source} tid={e.source} sub={e.note} />)} />
          <Block title="Develops" color={EDGE_COLOR.derivation} items={rows.dev.map((e) => <Row key={'d' + e.source} tid={e.source} sub={e.note} />)} />
          <Block title="Revives" color={EDGE_COLOR.revival} items={rows.rev.map((e) => <Row key={'r' + e.source} tid={e.source} sub={e.note} />)} />
          <Block title="Revived by" color={EDGE_COLOR.revival} items={rows.revBy.map((e) => <Row key={'rb' + e.target} tid={e.target} sub={e.note} />)} />
          <Block title="Disagrees with" color={EDGE_COLOR.disagreement} items={rows.dis.map((e, i) => <Row key={'x' + i} tid={other(e)} sub={(e.crux ? `on <em>${e.crux}</em>` : '') + (e.note ? ': ' + e.note : '')} />)} />
          {t.cruxes.length ? <div className="rel"><h5>Cruxes</h5>{t.cruxes.map((c, i) => <a key={i}><strong>{c.crux}</strong>{c.stance ? <><br /><span className="sub">{c.stance}</span></> : null}</a>)}</div> : null}
          {t.travel.length ? <div className="rel"><h5>Idea travel</h5>{t.travel.map((x, i) => <a key={i}><span className="yr">{fmtYear(x.year)}</span> {x.text}</a>)}</div> : null}
          <div className="rel links">
            {obsidianVault ? <a href={`obsidian://open?vault=${encodeURIComponent(obsidianVault)}&file=${encodeURIComponent(t.id)}`} style={{ color: '#c084fc' }}>Obsidian ✎</a> : null}
            {vaultPath ? <a href={`subl://open?url=${encodeURIComponent('file://' + vaultPath + '/' + t.id + '.md')}`} style={{ color: '#f5a97f' }}>Sublime ↗</a> : null}
            {vaultPath ? <a href={`vscode://file/${vaultPath}/${t.id}.md`} style={{ color: '#5eead4' }}>VS Code ↗</a> : null}
            {t.wikipedia ? <a href={t.wikipedia} target="_blank" rel="noreferrer" style={{ color: '#60a5fa' }}>Wikipedia ↗</a> : null}
          </div>
        </div>
      </>}
    </aside>
  );
}
