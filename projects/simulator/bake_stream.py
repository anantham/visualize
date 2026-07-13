#!/usr/bin/env python
"""Bake the autoregressive LOOP for Beat 0: token-by-token generation on gemma-2-2b,
recording the real next-token distribution (top-k) and the chosen token at every step.
The UI animates: tokens in -> model -> distribution out -> pick -> feed the token back in.

Writes projects/simulator/stream.json:
  streams[]       : {label, group, promptPieces[], steps:[{topk:[{tok,p}], chosen}]}
                    groups: 'worlds' (same prompt, sampled -> different paths),
                            'framings' (different seed -> different document),
                            'register' (clean vs broken seed)
  fewshotSharpen  : the ANSWER-step distribution at 0 vs 2 shots (ICL = distribution sharpening)
"""
import json, time, gc
from pathlib import Path
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "google/gemma-2-2b"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
OUT = Path(__file__).resolve().parent / "stream.json"
TOPK = 8
N_STEPS = 26

SEEDS = [
    # group, label, prompt, sample?, seed
    ("worlds", "run 1", "How does a compass work?", True, 1),
    ("worlds", "run 2", "How does a compass work?", True, 2),
    ("worlds", "run 3", "How does a compass work?", True, 7),
    ("framings", "a Q&A page", "Q: How does a compass work?\nA:", False, 0),
    ("framings", "a forum thread", "Thread: How does a compass work?\n\nTop reply:", False, 0),
    ("framings", "a children's book", "From a picture book for young children:\n\nHow does a compass work? Well,", False, 0),
    ("register", "clean prose", "The printing press let ideas spread across Europe. Because books became cheap,", False, 0),
    ("register", "broken prose", "The printing press is let the idea spread in the Europe. Because the book is become cheap,", False, 0),
]

FEWSHOT = {
    # prose format avoids gemma's "glossary => HTML" habit, so the answer token itself
    # is what lights up in the distribution
    "task": "translate English → French",
    "shots": [("sea", "mer"), ("bread", "pain"), ("water", "eau"), ("house", "maison")],
    "queries": [("mountain", "montagne"), ("green", "vert"), ("friend", "ami"), ("dog", "chien")],
    "shotCounts": [0, 3],
}


def fewshot_context(n, q):
    shots = " ".join(f"In French, {a} is {b}." for a, b in FEWSHOT["shots"][:n])
    return (shots + " " if n else "") + f"In French, {q} is"


def piece(tok, tid):
    return tok.decode([tid])


SAMPLING_CONTEXTS = [
    "Once upon a time, there was a",
    "The best way to spend a rainy Saturday is to",
    "The weather today is",
]


@torch.no_grad()
def topk_logits(model, tok, prompt, k=30):
    ids = tok(prompt, return_tensors="pt").to(DEVICE)["input_ids"]
    logits = model(ids).logits[0, -1].float()
    top = logits.topk(k)
    return [{"tok": piece(tok, int(i)), "logit": round(float(l), 3)}
            for l, i in zip(top.values, top.indices)]


@torch.no_grad()
def stream(model, tok, prompt, sample, seed):
    ids = tok(prompt, return_tensors="pt").to(DEVICE)["input_ids"]
    prompt_pieces = [piece(tok, t) for t in ids[0].tolist()]
    if sample:
        torch.manual_seed(seed)
    steps = []
    for _ in range(N_STEPS):
        logits = model(ids).logits[0, -1]
        probs = F.softmax(logits.float(), -1)
        top_p, top_i = probs.topk(TOPK)
        if sample:
            nxt = torch.multinomial(probs, 1).item()
        else:
            nxt = int(top_i[0].item())
        steps.append({
            "topk": [{"tok": piece(tok, int(i)), "p": round(float(p), 4)} for p, i in zip(top_p, top_i)],
            "chosen": piece(tok, nxt),
            "chosenInTop": nxt in top_i.tolist(),
        })
        if nxt == (tok.eos_token_id or -1):
            break
        ids = torch.cat([ids, torch.tensor([[nxt]], device=DEVICE)], 1)
    return prompt_pieces, steps


@torch.no_grad()
def answer_dist(model, tok, prompt):
    ids = tok(prompt, return_tensors="pt").to(DEVICE)["input_ids"]
    probs = F.softmax(model(ids).logits[0, -1].float(), -1)
    top_p, top_i = probs.topk(TOPK)
    return [{"tok": piece(tok, int(i)), "p": round(float(p), 4)} for p, i in zip(top_p, top_i)]


def main():
    print(f"[{time.strftime('%H:%M:%S')}] loading {MODEL}", flush=True)
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(DEVICE).eval()

    data = {"model": MODEL, "topk": TOPK, "streams": [], "fewshotSharpen": None}
    for group, label, prompt, sample, seed in SEEDS:
        print(f"  stream: {group}/{label}", flush=True)
        pp, steps = stream(model, tok, prompt, sample, seed)
        data["streams"].append({"group": group, "label": label, "prompt": prompt,
                                "promptPieces": pp, "steps": steps})

    print("  fewshot sharpen...", flush=True)
    fs = {"task": FEWSHOT["task"], "shotCounts": FEWSHOT["shotCounts"], "queries": []}
    for q, exp in FEWSHOT["queries"]:
        by = {}
        for n in FEWSHOT["shotCounts"]:
            ctx = fewshot_context(n, q)
            by[str(n)] = {"context": ctx, "topk": answer_dist(model, tok, ctx)}
        fs["queries"].append({"q": q, "expected": exp, "byShot": by})
    data["fewshotSharpen"] = fs

    print("  sampling logits...", flush=True)
    data["sampling"] = [{"context": c, "tokens": topk_logits(model, tok, c, 30)} for c in SAMPLING_CONTEXTS]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"[{time.strftime('%H:%M:%S')}] WROTE {OUT}", flush=True)
    del model; gc.collect()
    if DEVICE == "mps":
        torch.mps.empty_cache()


if __name__ == "__main__":
    main()
