#!/usr/bin/env python
"""
Build terrain_data.json: a navigable point cloud of prior-divergence positions.

Reuses run_norm.py's machinery verbatim (same NeelNanda/pile-10k 300-passage /
6-domain sample, same seeds, same char-aligned per-word surprisal in bits/char).
Adds:
  * one record PER word-position carrying all 4 models' bits/char + the preceding
    ~120-char context + the next word + the Pile domain,
  * stratified sampling (~500 high-divergence tail + ~2500 domain-spanning bulk),
  * a 2D layout: MiniLM sentence-embedding of each context -> UMAP (fallback PCA),
  * per-pair |delta bits/char| for the 4 informative pairs.

Outputs ONLY terrain_data.json (existing files untouched). A surprisal cache
(terrain_surp_cache.pkl) is written so the layout/export step can be re-run cheaply.
"""
import os, re, json, math, time, gc, pickle
import numpy as np
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT = "/Users/aditya/align_experiments/prior_divergence"
CACHE = f"{OUT}/terrain_surp_cache.pkl"
LN2 = math.log(2.0)
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
torch.manual_seed(0)

MODELS = {
    "gpt2":        "gpt2",
    "pythia-1.4b": "EleutherAI/pythia-1.4b",
    "pythia-410m": "EleutherAI/pythia-410m",
    "qwen2.5-0.5b":"Qwen/Qwen2.5-0.5B",
}
MODEL_ORDER = ["gpt2", "pythia-1.4b", "pythia-410m", "qwen2.5-0.5b"]
# (a, b, matched)  -- mismatched cross-corpus first, matched same-data last
PAIRS = [
    ("gpt2",        "pythia-1.4b",  False),   # dramatic / mismatched (primary)
    ("gpt2",        "qwen2.5-0.5b", False),
    ("pythia-1.4b", "qwen2.5-0.5b", False),
    ("pythia-1.4b", "pythia-410m",  True),    # matched (same Pile data, scale only)
]

PREF_DOMAINS = ["Github", "ArXiv", "Wikipedia (en)", "Pile-CC", "StackExchange", "PubMed Central"]
DOCS_PER_DOMAIN = 50
TRUNC_TOKENS = 256

N_TAIL   = 500       # top-divergence positions (mountains)
N_BULK   = 2500      # domain-spanning bulk (plains)
CTX_CHARS = 120      # preceding context window (chars)
MIN_VIS  = 2         # drop pure single-char noise positions
RNG = np.random.default_rng(0)

# ---------------------------------------------------------------- passages (identical to run_norm)
print(f"[{time.strftime('%H:%M:%S')}] loading pile-10k ...", flush=True)
ds = load_dataset("NeelNanda/pile-10k", split="train")
by_dom = {}
for i, m in enumerate(ds["meta"]):
    by_dom.setdefault(m["pile_set_name"], []).append(i)
avail = {d: len(v) for d, v in by_dom.items()}
domains = [d for d in PREF_DOMAINS if avail.get(d, 0) >= DOCS_PER_DOMAIN]
print("USING domains:", domains, flush=True)

ref_tok = AutoTokenizer.from_pretrained(MODELS["gpt2"], use_fast=True)
passages = []
rng = np.random.default_rng(0)
for dom in domains:
    idxs = by_dom[dom]
    rng.shuffle(idxs)
    taken = 0
    for di in idxs:
        if taken >= DOCS_PER_DOMAIN:
            break
        raw = ds[di]["text"]
        if not raw or len(raw.strip()) < 200:
            continue
        ids = ref_tok(raw, add_special_tokens=False)["input_ids"][:TRUNC_TOKENS]
        if len(ids) < 32:
            continue
        text = ref_tok.decode(ids)
        if len(text.strip()) < 64:
            continue
        passages.append({"id": len(passages), "domain": dom, "text": text})
        taken += 1
print(f"built {len(passages)} passages across {len(domains)} domains", flush=True)

def word_segments(text):
    segs, prev = [], 0
    for m in re.finditer(r"\S+", text):
        segs.append((m.group(), prev, m.end(), m.start()))
        prev = m.end()
    return segs
for p in passages:
    p["words"] = word_segments(p["text"])

# ---------------------------------------------------------------- per-model surprisal (from run_norm)
def compute_surprisal():
    word_surp = {name: {} for name in MODELS}
    word_ntok = {name: {} for name in MODELS}

    @torch.no_grad()
    def run_model(name, hf_id):
        print(f"[{time.strftime('%H:%M:%S')}] {name} ({hf_id}) on {DEVICE}", flush=True)
        tok = AutoTokenizer.from_pretrained(hf_id, use_fast=True)
        model = AutoModelForCausalLM.from_pretrained(hf_id, torch_dtype=torch.float32).to(DEVICE).eval()
        t0 = time.time()
        for p in passages:
            text = p["text"]
            enc = tok(text, return_offsets_mapping=True, add_special_tokens=False,
                      return_tensors="pt", truncation=True, max_length=512)
            ids = enc["input_ids"]; offsets = enc["offset_mapping"][0].tolist(); N = ids.shape[1]
            if N < 2:
                word_surp[name][p["id"]] = np.full(len(p["words"]), np.nan)
                word_ntok[name][p["id"]] = np.zeros(len(p["words"])); continue
            logits = model(ids.to(DEVICE)).logits[0]
            logp = torch.log_softmax(logits.float(), dim=-1)
            tgt = ids[0, 1:].to(DEVICE)
            sl = (-logp[:-1].gather(1, tgt.unsqueeze(1)).squeeze(1) / LN2).cpu().numpy()
            L = len(text); csurp = np.full(L, np.nan); tok_mid = []
            for j in range(1, N):
                s, e = offsets[j]
                if e <= s:
                    tok_mid.append((-1, False)); continue
                csurp[s:e] = sl[j-1] / (e - s); tok_mid.append(((s + e) // 2, True))
            ws = np.full(len(p["words"]), np.nan); nt = np.zeros(len(p["words"]))
            for wi, (_, seg_start, seg_end, word_start) in enumerate(p["words"]):
                vis = csurp[word_start:seg_end]
                if vis.size == 0 or np.isnan(vis).any():
                    continue
                ws[wi] = float(np.nansum(csurp[seg_start:seg_end]))
                nt[wi] = sum(1 for mid, ok in tok_mid if ok and seg_start <= mid < seg_end)
            word_surp[name][p["id"]] = ws; word_ntok[name][p["id"]] = nt
        print(f"    done {name} in {time.time()-t0:.1f}s", flush=True)
        del model; gc.collect()
        if DEVICE == "mps": torch.mps.empty_cache()

    for name, hf_id in MODELS.items():
        run_model(name, hf_id)
    return word_surp, word_ntok

if os.path.exists(CACHE):
    print(f"[{time.strftime('%H:%M:%S')}] loading cached surprisal {CACHE}", flush=True)
    with open(CACHE, "rb") as f:
        blob = pickle.load(f)
    word_surp, word_ntok = blob["surp"], blob["ntok"]
else:
    word_surp, word_ntok = compute_surprisal()
    with open(CACHE, "wb") as f:
        pickle.dump({"surp": word_surp, "ntok": word_ntok}, f)
    print(f"[{time.strftime('%H:%M:%S')}] cached surprisal -> {CACHE}", flush=True)

# ---------------------------------------------------------------- per-position records (all 4 models valid)
records = []   # each: dict with bpc per model, context, next, domain, div per pair
for p in passages:
    txt = p["text"]
    surps = {m: word_surp[m][p["id"]] for m in MODELS}
    for wi, (wtext, seg_start, seg_end, wstart) in enumerate(p["words"]):
        n_chars = seg_end - seg_start
        vis_len = seg_end - wstart
        if n_chars <= 0 or vis_len < MIN_VIS:
            continue
        sv = {m: surps[m][wi] for m in MODELS}
        if any(np.isnan(v) for v in sv.values()):
            continue
        bpc = {m: sv[m] / n_chars for m in MODELS}
        div = {}; surprised = {}
        maxdiv_mismatch = 0.0
        for a, b, matched in PAIRS:
            key = f"{a}|{b}"
            d = abs(bpc[a] - bpc[b])
            div[key] = d
            surprised[key] = a if sv[a] > sv[b] else b
            if not matched:
                maxdiv_mismatch = max(maxdiv_mismatch, d)
        ctx = txt[max(0, wstart - CTX_CHARS):wstart]
        records.append({
            "domain": p["domain"], "ctx": ctx, "next": wtext,
            "bits": bpc,
            "div": div, "surprised": surprised, "maxdiv": maxdiv_mismatch,
        })
print(f"[{time.strftime('%H:%M:%S')}] valid positions (all 4 models): {len(records)}", flush=True)

# ---------------------------------------------------------------- stratified sampling
order = np.argsort([-r["maxdiv"] for r in records])          # by peak mismatched divergence
tail_idx = list(order[:N_TAIL])
tail_set = set(tail_idx)

remaining_by_dom = {}
for i, r in enumerate(records):
    if i in tail_set:
        continue
    remaining_by_dom.setdefault(r["domain"], []).append(i)

bulk_idx = []
per_dom = N_BULK // len(domains)
for dom in domains:
    pool = remaining_by_dom.get(dom, [])
    take = min(per_dom, len(pool))
    bulk_idx.extend(RNG.choice(pool, size=take, replace=False).tolist())
# top up to N_BULK from whatever is left, spanning all domains
leftover = [i for dom in domains for i in remaining_by_dom.get(dom, []) if i not in set(bulk_idx)]
need = N_BULK - len(bulk_idx)
if need > 0 and leftover:
    bulk_idx.extend(RNG.choice(leftover, size=min(need, len(leftover)), replace=False).tolist())

sample_idx = list(tail_idx) + list(bulk_idx)
sample = [records[i] for i in sample_idx]
is_tail = np.array([True] * len(tail_idx) + [False] * len(bulk_idx))
print(f"[{time.strftime('%H:%M:%S')}] sampled {len(sample)} (tail {len(tail_idx)} + bulk {len(bulk_idx)})", flush=True)

# ---------------------------------------------------------------- layout: MiniLM embed -> UMAP (fallback PCA)
ctxs = [r["ctx"] if r["ctx"].strip() else " " for r in sample]
print(f"[{time.strftime('%H:%M:%S')}] embedding {len(ctxs)} contexts (all-MiniLM-L6-v2) ...", flush=True)
from sentence_transformers import SentenceTransformer
emb_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=DEVICE)
emb = emb_model.encode(ctxs, batch_size=128, normalize_embeddings=True,
                       show_progress_bar=False, convert_to_numpy=True)

layout_method = "umap"
try:
    import umap
    reducer = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1,
                        metric="cosine", random_state=42)
    xy = reducer.fit_transform(emb)
except Exception as e:
    print(f"[WARN] UMAP failed ({e}); falling back to PCA-2D", flush=True)
    from sklearn.decomposition import PCA
    xy = PCA(n_components=2, random_state=42).fit_transform(emb)
    layout_method = "pca"

# normalize to [-1,1], shared scale (preserve aspect ratio of the layout)
xy = xy.astype(float)
mid = (xy.max(0) + xy.min(0)) / 2.0
half = (xy.max(0) - xy.min(0)).max() / 2.0
xy = (xy - mid) / half
print(f"[{time.strftime('%H:%M:%S')}] layout={layout_method}; x[{xy[:,0].min():.2f},{xy[:,0].max():.2f}] y[{xy[:,1].min():.2f},{xy[:,1].max():.2f}]", flush=True)

# ---------------------------------------------------------------- export
def r3(x):
    return round(float(x), 3)

points = []
for i, r in enumerate(sample):
    points.append({
        "x": r3(xy[i, 0]), "y": r3(xy[i, 1]),
        "ctx": r["ctx"][:CTX_CHARS], "next": r["next"], "domain": r["domain"],
        "bits": {m: r3(v) for m, v in r["bits"].items()},
        "div": {k: r3(v) for k, v in r["div"].items()},
        "surprised": r["surprised"],
    })

out = {
    "models": MODEL_ORDER,
    "pairs": [{"key": f"{a}|{b}", "a": a, "b": b, "matched": matched} for a, b, matched in PAIRS],
    "domains": domains,
    "layout": layout_method,
    "points": points,
}
outpath = f"{OUT}/terrain_data.json"
with open(outpath, "w") as f:
    json.dump(out, f, separators=(",", ":"), ensure_ascii=False)
sz = os.path.getsize(outpath)
print(f"[{time.strftime('%H:%M:%S')}] wrote {outpath}  ({len(points)} pts, {sz/1e6:.2f} MB)", flush=True)

# ---------------------------------------------------------------- sanity checks
from sklearn.metrics import silhouette_score
labels = np.array([domains.index(r["domain"]) for r in sample])
sil = silhouette_score(xy, labels, metric="euclidean")

# per-domain centroid spread (Github should be compact)
print("\n===== SANITY =====", flush=True)
print(f"layout method: {layout_method}", flush=True)
print(f"domain silhouette on 2D (>0 => domains cluster spatially): {sil:.3f}", flush=True)

# Github cluster compactness vs overall
gh = xy[labels == domains.index("Github")]
gh_c = gh.mean(0)
gh_rms = np.sqrt(((gh - gh_c) ** 2).sum(1)).mean()
all_rms = np.sqrt(((xy - xy.mean(0)) ** 2).sum(1)).mean()
print(f"Github points: {len(gh)}  mean-dist-to-own-centroid={gh_rms:.3f}  vs all-points-to-global={all_rms:.3f}", flush=True)

# where do the mismatched mountains live?
mm_key = "gpt2|pythia-1.4b"
divs_mm = np.array([r["div"][mm_key] for r in sample])
top_mask = divs_mm >= np.percentile(divs_mm, 95)   # top 5% divergence points
top_doms = {}
for r, t in zip(sample, top_mask):
    if t: top_doms[r["domain"]] = top_doms.get(r["domain"], 0) + 1
print(f"\nTop-5%-divergence points ({mm_key}) by domain:", flush=True)
for d, c in sorted(top_doms.items(), key=lambda kv: -kv[1]):
    print(f"   {d:16s} {c}", flush=True)
# spatial concentration of the top-divergence points: mean pairwise dist vs random
top_xy = xy[top_mask]
def mean_pairwise(a):
    if len(a) < 2: return float("nan")
    from scipy.spatial.distance import pdist
    return float(pdist(a).mean())
try:
    rand_xy = xy[RNG.choice(len(xy), size=len(top_xy), replace=False)]
    print(f"top-divergence spatial spread (mean pairwise dist): {mean_pairwise(top_xy):.3f}  "
          f"vs random-same-n: {mean_pairwise(rand_xy):.3f}", flush=True)
except Exception as e:
    print(f"(pairwise dist skipped: {e})", flush=True)

# flatten knob: matched vs mismatched divergence on the SAMPLED points
print("\n--- FLATTEN KNOB (sampled points, bits/char) ---", flush=True)
for a, b, matched in PAIRS:
    key = f"{a}|{b}"
    v = np.array([r["div"][key] for r in sample])
    tag = "MATCHED " if matched else "mismatch"
    print(f"   [{tag}] {key:26s} median={np.median(v):.3f}  p90={np.percentile(v,90):.3f}  "
          f"p99={np.percentile(v,99):.3f}  max={v.max():.2f}", flush=True)
mmv = np.array([r["div"][mm_key] for r in sample])
mtv = np.array([r["div"]["pythia-1.4b|pythia-410m"] for r in sample])
print(f"\n   mismatched/matched median ratio: {np.median(mmv)/max(np.median(mtv),1e-9):.1f}x", flush=True)
print(f"   mismatched/matched p99 ratio:    {np.percentile(mmv,99)/max(np.percentile(mtv,99),1e-9):.1f}x", flush=True)
print(f"[{time.strftime('%H:%M:%S')}] DONE", flush=True)
