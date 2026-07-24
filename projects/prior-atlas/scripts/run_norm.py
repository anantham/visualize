#!/usr/bin/env python
"""
Prior-divergence, NORMALIZED (kills the word-length confound) + a matched
same-data/different-scale pair to test the "flatten" knob.

Changes vs run.py:
  (1) NORMALIZED metric. The raw metric summed |Delta surprisal| per whitespace-word,
      so long strings (esp. long code tokens) scored high just for being long. Here we
      report divergence as BITS-PER-CHARACTER at each aligned word unit:
          div_norm(word) = |surp_A_word - surp_B_word| / n_chars(word)
      where n_chars = characters in the word's segment (the exact span the summed
      surprisal covers). Both models sum over the identical span, so this is an honest,
      symmetric, tokenizer-agnostic density. (Per-TOKEN is also emitted as a robustness
      check: |surp_A/ntok_A - surp_B/ntok_B|, each model's own token count in the span.)
  (2) MATCHED pair. Adds EleutherAI/pythia-410m alongside pythia-1.4b (identical Pile
      training data, only scale differs). Prediction: pythia-1.4b-vs-410m terrain is far
      FLATTER (no coverage/memorization mountains -- same data -> same coverage) than any
      cross-corpus pair (gpt2-vs-pythia). gpt2 + qwen2.5-0.5b kept.

Everything else (300-passage / 6-domain pile-10k sample, char-aligned surprisal) reused.
Outputs are _norm suffixed so the originals are untouched.
"""
import os, re, json, math, time, gc
import numpy as np
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM

OUT = "/Users/aditya/align_experiments/prior_divergence"
os.makedirs(OUT, exist_ok=True)
LN2 = math.log(2.0)
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
torch.manual_seed(0)

MODELS = {
    "gpt2":        "gpt2",
    "pythia-1.4b": "EleutherAI/pythia-1.4b",
    "pythia-410m": "EleutherAI/pythia-410m",   # NEW: matched same-data control
    "qwen2.5-0.5b":"Qwen/Qwen2.5-0.5B",
}
# matched pair first, then the cross-corpus (mismatched) pairs
PAIRS = [
    ("pythia-1.4b", "pythia-410m"),    # MATCHED  (same data, scale differs)
    ("gpt2",        "pythia-1.4b"),    # MISMATCHED (primary contrast)
    ("gpt2",        "qwen2.5-0.5b"),   # MISMATCHED
    ("pythia-1.4b", "qwen2.5-0.5b"),   # MISMATCHED
]
MATCHED_KEY   = "pythia-1.4b|pythia-410m"
MISMATCH_KEY  = "gpt2|pythia-1.4b"

PREF_DOMAINS = ["Github", "ArXiv", "Wikipedia (en)", "Pile-CC", "StackExchange", "PubMed Central"]
DOCS_PER_DOMAIN = 50
TRUNC_TOKENS = 256
MIN_CHARS_TAIL = 4   # min visible-word length for the "substantive" tail (avoid 1-char noise)

# ----------------------------------------------------------------------------
# 1. Build domain-labelled passages (identical sampling to run.py: same seeds)
# ----------------------------------------------------------------------------
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

# ----------------------------------------------------------------------------
# 2. Common word segmentation. Each word owns its leading whitespace; we also
#    record n_chars (segment span = the exact chars the summed surprisal covers)
#    and vis_len (visible word length) for tail filtering.
# ----------------------------------------------------------------------------
def word_segments(text):
    segs, prev = [], 0
    for m in re.finditer(r"\S+", text):
        segs.append((m.group(), prev, m.end(), m.start()))
        prev = m.end()
    return segs

for p in passages:
    p["words"] = word_segments(p["text"])

# ----------------------------------------------------------------------------
# 3. Per-model per-word surprisal (bits) + per-model token count per word
# ----------------------------------------------------------------------------
word_surp = {name: {} for name in MODELS}   # summed bits over the segment (NaN if uncovered)
word_ntok = {name: {} for name in MODELS}   # this model's #tokens landing in the segment

@torch.no_grad()
def run_model(name, hf_id):
    print(f"[{time.strftime('%H:%M:%S')}] loading {name} ({hf_id}) on {DEVICE}", flush=True)
    tok = AutoTokenizer.from_pretrained(hf_id, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(hf_id, torch_dtype=torch.float32)
    model.to(DEVICE).eval()
    t0 = time.time()
    for p in passages:
        text = p["text"]
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False,
                  return_tensors="pt", truncation=True, max_length=512)
        ids = enc["input_ids"]
        offsets = enc["offset_mapping"][0].tolist()
        N = ids.shape[1]
        if N < 2:
            word_surp[name][p["id"]] = np.full(len(p["words"]), np.nan)
            word_ntok[name][p["id"]] = np.zeros(len(p["words"]))
            continue
        logits = model(ids.to(DEVICE)).logits[0]
        logp = torch.log_softmax(logits.float(), dim=-1)
        tgt = ids[0, 1:].to(DEVICE)
        sl = (-logp[:-1].gather(1, tgt.unsqueeze(1)).squeeze(1) / LN2).cpu().numpy()
        L = len(text)
        csurp = np.full(L, np.nan)
        # token midpoint -> which char, for per-word token counts
        tok_mid = []      # (mid_char, has_prediction)
        for j in range(1, N):
            s, e = offsets[j]
            if e <= s:
                tok_mid.append((-1, False))
                continue
            csurp[s:e] = sl[j-1] / (e - s)
            tok_mid.append(((s + e) // 2, True))
        ws = np.full(len(p["words"]), np.nan)
        nt = np.zeros(len(p["words"]))
        for wi, (_, seg_start, seg_end, word_start) in enumerate(p["words"]):
            vis = csurp[word_start:seg_end]
            if vis.size == 0 or np.isnan(vis).any():
                continue
            ws[wi] = float(np.nansum(csurp[seg_start:seg_end]))
            # count this model's predicted tokens whose midpoint lands in [seg_start, seg_end)
            nt[wi] = sum(1 for mid, ok in tok_mid if ok and seg_start <= mid < seg_end)
        word_surp[name][p["id"]] = ws
        word_ntok[name][p["id"]] = nt
    print(f"    done {name} in {time.time()-t0:.1f}s", flush=True)
    del model
    gc.collect()
    if DEVICE == "mps":
        torch.mps.empty_cache()

for name, hf_id in MODELS.items():
    run_model(name, hf_id)

# ----------------------------------------------------------------------------
# 4. Divergences per pair: RAW (per-word bits) and NORMALIZED (bits/char, bits/token)
# ----------------------------------------------------------------------------
records = {f"{a}|{b}": [] for a, b in PAIRS}
for a, b in PAIRS:
    key = f"{a}|{b}"
    for p in passages:
        wa, wb = word_surp[a][p["id"]], word_surp[b][p["id"]]
        na, nb = word_ntok[a][p["id"]], word_ntok[b][p["id"]]
        words = p["words"]
        for wi in range(len(words)):
            sa, sb = wa[wi], wb[wi]
            if np.isnan(sa) or np.isnan(sb):
                continue
            wtext, seg_start, seg_end, wstart = words[wi]
            n_chars = seg_end - seg_start          # span the summed surprisal covers
            vis_len = seg_end - wstart             # visible word length
            if n_chars <= 0:
                continue
            div_raw = abs(sa - sb)
            div_char = div_raw / n_chars
            # per-token: each model's own bits/token, then |delta|
            bpt_a = sa / na[wi] if na[wi] > 0 else np.nan
            bpt_b = sb / nb[wi] if nb[wi] > 0 else np.nan
            div_tok = abs(bpt_a - bpt_b) if not (np.isnan(bpt_a) or np.isnan(bpt_b)) else np.nan
            records[key].append({
                "passage_id": p["id"], "domain": p["domain"], "word_idx": wi,
                "word": wtext, "wstart": wstart, "n_chars": int(n_chars), "vis_len": int(vis_len),
                "surp_a": float(sa), "surp_b": float(sb),
                "div_raw": float(div_raw), "div_char": float(div_char),
                "div_tok": float(div_tok) if not np.isnan(div_tok) else None,
                "bpc_a": float(sa / n_chars), "bpc_b": float(sb / n_chars),
            })

# ----------------------------------------------------------------------------
# 5. Outputs (NORMALIZED metric = bits/char is primary)
# ----------------------------------------------------------------------------
def pct(arr, qs):
    return {f"p{q}": float(np.percentile(arr, q)) for q in qs}

QS = [50, 75, 90, 95, 99, 99.9]
dist = {}
for a, b in PAIRS:
    key = f"{a}|{b}"
    dc   = np.array([r["div_char"] for r in records[key]])
    dr   = np.array([r["div_raw"]  for r in records[key]])
    dt   = np.array([r["div_tok"]  for r in records[key] if r["div_tok"] is not None])
    pc   = pct(dc, QS)
    pr   = pct(dr, QS)
    ptk  = pct(dt, QS)
    counts, edges = np.histogram(dc, bins=np.linspace(0, float(dc.max()), 61))
    dist[key] = {
        "pair": [a, b],
        "matched": key == MATCHED_KEY,
        "n_words": int(dc.size),
        "bits_per_char": {
            "mean": float(dc.mean()), "std": float(dc.std()), "max": float(dc.max()),
            "percentiles": pc,
            "p99_over_median": float(pc["p99"] / pc["p50"]) if pc["p50"] > 0 else None,
            "p99.9_over_median": float(pc["p99.9"] / pc["p50"]) if pc["p50"] > 0 else None,
            "frac_over_1bpc": float((dc > 1).mean()),
            "frac_over_3bpc": float((dc > 3).mean()),
        },
        "bits_per_token": {
            "mean": float(dt.mean()), "max": float(dt.max()), "percentiles": ptk,
            "p99_over_median": float(ptk["p99"] / ptk["p50"]) if ptk["p50"] > 0 else None,
        },
        "raw_bits_per_word_reference": {
            "mean": float(dr.mean()), "percentiles": pr,
            "p99_over_median": float(pr["p99"] / pr["p50"]) if pr["p50"] > 0 else None,
        },
        "histogram_bpc": {"bin_edges": edges.tolist(), "counts": counts.tolist()},
    }
with open(f"{OUT}/divergence_dist_norm.json", "w") as f:
    json.dump(dist, f, indent=2)

# by-domain (normalized)
by_domain = {}
for a, b in PAIRS:
    key = f"{a}|{b}"
    dom_map = {}
    for r in records[key]:
        dom_map.setdefault(r["domain"], []).append(r["div_char"])
    by_domain[key] = {
        dom: {"mean_bpc": float(np.mean(v)), "p90_bpc": float(np.percentile(v, 90)),
              "p99_bpc": float(np.percentile(v, 99)), "n": len(v)}
        for dom, v in sorted(dom_map.items(), key=lambda kv: -np.mean(kv[1]))
    }
with open(f"{OUT}/divergence_by_domain_norm.json", "w") as f:
    json.dump(by_domain, f, indent=2)

# tail examples (normalized): (a) top-30 unfiltered, (b) top-30 substantive (vis_len>=MIN)
ptext = {p["id"]: p["text"] for p in passages}
def make_ex(r, a, b):
    txt = ptext[r["passage_id"]]
    ctx = txt[max(0, r["wstart"] - 80):r["wstart"]].replace("\n", "\\n")
    surprised = a if r["surp_a"] > r["surp_b"] else b
    return {
        "domain": r["domain"], "context": "..." + ctx,
        "next_word": r["word"].replace("\n", "\\n"),
        "n_chars": r["n_chars"], "vis_len": r["vis_len"],
        f"bpc_{a}": round(r["bpc_a"], 2), f"bpc_{b}": round(r["bpc_b"], 2),
        "div_bits_per_char": round(r["div_char"], 2),
        "div_raw_bits_per_word": round(r["div_raw"], 1),
        "more_surprised": surprised,
    }
tail = {}
for a, b in PAIRS:
    key = f"{a}|{b}"
    recs = records[key]
    top_all = sorted(recs, key=lambda r: -r["div_char"])[:30]
    subs = [r for r in recs if r["vis_len"] >= MIN_CHARS_TAIL]
    top_sub = sorted(subs, key=lambda r: -r["div_char"])[:30]
    tail[key] = {
        "top30_unfiltered": [make_ex(r, a, b) for r in top_all],
        f"top30_substantive_vislen_ge_{MIN_CHARS_TAIL}": [make_ex(r, a, b) for r in top_sub],
        "unfiltered_median_vislen": float(np.median([r["vis_len"] for r in top_all])),
    }
with open(f"{OUT}/tail_examples_norm.json", "w") as f:
    json.dump(tail, f, indent=2)

# ----------------------------------------------------------------------------
# 6. Figure: MATCHED terrain vs MISMATCHED terrain, same axes (the flatten test)
# ----------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COL = {
    MATCHED_KEY:  "#2a9d8f",   # matched  (teal)
    MISMATCH_KEY: "#e4572e",   # mismatched (orange-red)
    "gpt2|qwen2.5-0.5b":       "#8a5a44",
    "pythia-1.4b|qwen2.5-0.5b":"#6a4c93",
}
dchar = {f"{a}|{b}": np.array([r["div_char"] for r in records[f"{a}|{b}"]]) for a, b in PAIRS}

fig, axes = plt.subplots(1, 3, figsize=(19, 5.6))

# -- Panel A: normalized divergence histogram, matched vs mismatched, SAME axes --
axA = axes[0]
xmax = float(np.percentile(dchar[MISMATCH_KEY], 99.9))
bins = np.linspace(0, xmax, 60)
for key in (MISMATCH_KEY, MATCHED_KEY):
    axA.hist(dchar[key], bins=bins, histtype="step", lw=2.2, color=COL[key],
             label=("MISMATCHED " if key == MISMATCH_KEY else "MATCHED ") + key)
axA.set_yscale("log")
axA.set_xlabel("divergence (bits / character)")
axA.set_ylabel("word count (log)")
axA.set_title("Normalized divergence: does the tail survive?")
axA.legend(fontsize=8)

# -- Panel B: "elevation profile" -- sorted divergence vs percentile rank (the terrain) --
axB = axes[1]
for key in (MISMATCH_KEY, MATCHED_KEY):
    v = np.sort(dchar[key])[::-1]
    rank_pct = 100.0 * np.arange(1, v.size + 1) / v.size
    axB.plot(rank_pct, v, lw=2.2, color=COL[key],
             label=("MISMATCHED " if key == MISMATCH_KEY else "MATCHED ") + key)
axB.set_xscale("log")
axB.set_xlabel("top X% of words (log)")
axB.set_ylabel("divergence (bits / char)")
axB.set_title("Terrain elevation profile: mountains vs flat")
axB.legend(fontsize=8)
axB.grid(alpha=0.25)

# -- Panel C: all pairs, p50 / p90 / p99 bits-per-char (flatten summary) --
axC = axes[2]
keys = [f"{a}|{b}" for a, b in PAIRS]
x = np.arange(len(keys))
w = 0.26
for i, q in enumerate(["p50", "p90", "p99"]):
    vals = [dist[k]["bits_per_char"]["percentiles"][q] for k in keys]
    axC.bar(x + (i - 1) * w, vals, w, label=q,
            color=["#bfc0c0", "#87a2c7", "#3d5a80"][i])
axC.set_xticks(x)
axC.set_xticklabels([k.replace("pythia-", "py").replace("qwen2.5-0.5b", "qwen")
                     for k in keys], rotation=18, ha="right", fontsize=8)
axC.set_ylabel("divergence (bits / char)")
axC.set_title("Per-pair p50/p90/p99 (matched pair = leftmost)")
axC.legend(fontsize=8)

plt.tight_layout()
plt.savefig(f"{OUT}/divergence_figure_norm.png", dpi=130)

# ----------------------------------------------------------------------------
# 7. Console summary
# ----------------------------------------------------------------------------
print("\n===== NORMALIZED SUMMARY (bits/char) =====", flush=True)
for a, b in PAIRS:
    key = f"{a}|{b}"
    s = dist[key]["bits_per_char"]
    r = dist[key]["raw_bits_per_word_reference"]
    tag = "MATCHED  " if dist[key]["matched"] else "mismatch "
    print(f"\n[{tag}{key}] n={dist[key]['n_words']}", flush=True)
    print(f"   bits/char : median={s['percentiles']['p50']:.3f}  p90={s['percentiles']['p90']:.3f}  "
          f"p99={s['percentiles']['p99']:.3f}  max={s['max']:.2f}  p99/med={s['p99_over_median']:.1f}", flush=True)
    print(f"   raw ref   : median={r['percentiles']['p50']:.2f}  p99={r['percentiles']['p99']:.2f}  "
          f"p99/med={r['p99_over_median']:.1f}   (for contrast)", flush=True)
    print("   by-domain bits/char (hot->cool):", flush=True)
    for dom, v in by_domain[key].items():
        print(f"     {dom:18s} mean={v['mean_bpc']:.3f}  p99={v['p99_bpc']:.3f}  n={v['n']}", flush=True)

print("\n--- FLATTEN TEST (matched vs mismatched, bits/char) ---", flush=True)
m  = dist[MATCHED_KEY]["bits_per_char"]
mm = dist[MISMATCH_KEY]["bits_per_char"]
print(f"   {'metric':16s} {'MATCHED(py1.4b-410m)':>22s} {'MISMATCH(gpt2-py1.4b)':>22s} {'ratio MM/M':>12s}", flush=True)
for q in ["p50", "p90", "p99", "p99.9"]:
    mv, mmv = m["percentiles"][q], mm["percentiles"][q]
    print(f"   {q:16s} {mv:22.3f} {mmv:22.3f} {mmv/mv:12.1f}", flush=True)
print(f"   {'mean':16s} {m['mean']:22.3f} {mm['mean']:22.3f} {mm['mean']/m['mean']:12.1f}", flush=True)
print(f"   {'p99/median':16s} {m['p99_over_median']:22.1f} {mm['p99_over_median']:22.1f}", flush=True)
print(f"\n[{time.strftime('%H:%M:%S')}] wrote *_norm outputs + divergence_figure_norm.png to {OUT}", flush=True)
