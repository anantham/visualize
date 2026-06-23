export const EDGE_COLOR = {
  influence: '#5eead4', derivation: '#60a5fa', disagreement: '#f87171', revival: '#fbbf24',
};
export const EDGE_LABEL = {
  influence: 'influence', derivation: 'develops', disagreement: 'disagrees', revival: 'revives',
};
export const REGION_TINT = {
  Greece: [96, 165, 250], Rome: [129, 140, 248], India: [245, 158, 11], China: [239, 68, 68],
  'East Asia': [251, 113, 133], 'Islamic world': [52, 211, 153], Jewish: [45, 212, 191],
  Europe: [148, 163, 184], Americas: [167, 139, 250],
};
const TRADITION_COLOR = {
  Platonism: '#60a5fa', Aristotelianism: '#38bdf8', 'Classical Greek': '#818cf8',
  'Ionian (Pre-Socratic)': '#22d3ee', Eleatic: '#2dd4bf', Stoicism: '#34d399', Epicureanism: '#a3e635',
  Cynicism: '#84cc16', Neoplatonism: '#818cf8', Buddhism: '#f59e0b', 'Madhyamaka Buddhism': '#fbbf24',
  'Navayana Buddhism': '#fb923c', Jainism: '#f472b6', 'Advaita Vedanta': '#e879f9',
  Confucianism: '#ef4444', 'Neo-Confucianism': '#f87171', Mohism: '#fb7185', Daoism: '#c084fc',
  Legalism: '#fda4af', Empiricism: '#94a3b8', Existentialism: '#cbd5e1',
};
export function tradColor(t) {
  if (TRADITION_COLOR[t]) return TRADITION_COLOR[t];
  let h = 0; for (const c of (t || '')) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return `hsl(${h % 360}, 55%, 64%)`;
}
export const regionRGB = (r) => { const t = REGION_TINT[r] || [160, 170, 190]; return `rgb(${t[0]},${t[1]},${t[2]})`; };
export const fmtYear = (y) => { y = Math.round(y); return y < 0 ? `${-y} BCE` : `${y} CE`; };
