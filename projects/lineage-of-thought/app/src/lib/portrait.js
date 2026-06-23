import { useState, useEffect } from 'react';

// Resolve a thinker's portrait: use the note's `portrait` if present, else fetch the
// thumbnail from Wikipedia's REST summary API (CORS-enabled) via the `wikipedia` URL.
const cache = new Map();

function wikiTitle(url) {
  try { const p = new URL(url).pathname; const i = p.indexOf('/wiki/'); return i >= 0 ? decodeURIComponent(p.slice(i + 6)) : null; }
  catch { return null; }
}

export async function fetchPortrait(t) {
  if (!t) return '';
  if (t.portrait) return t.portrait;
  if (cache.has(t.id)) return cache.get(t.id);
  const title = wikiTitle(t.wikipedia);
  if (!title) { cache.set(t.id, ''); return ''; }
  try {
    const r = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`);
    const j = await r.json();
    const src = (j.thumbnail && j.thumbnail.source) || (j.originalimage && j.originalimage.source) || '';
    cache.set(t.id, src); return src;
  } catch { cache.set(t.id, ''); return ''; }
}

export function usePortrait(t) {
  const [url, setUrl] = useState(t && t.portrait ? t.portrait : '');
  useEffect(() => {
    let ok = true;
    if (!t) { setUrl(''); return; }
    if (t.portrait) { setUrl(t.portrait); return; }
    setUrl(''); fetchPortrait(t).then((u) => { if (ok) setUrl(u); });
    return () => { ok = false; };
  }, [t && t.id]); // eslint-disable-line
  return url;
}
