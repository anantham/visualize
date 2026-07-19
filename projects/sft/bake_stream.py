#!/usr/bin/env python
"""Beat 1 (SFT) data: the SAME autoregressive loop as Beat 0, but scrubbed across
TRAINING. For each benign prompt, generate token-by-token (top-k distribution +
chosen) at three checkpoints of one real run:
    base SmolLM2-360M  ->  SFT step 50  ->  SFT step 400 (final)
Same chat-formatted input at every checkpoint, so the ONLY thing that changed is the
weights. Watch a rambling continuation become a clean assistant answer.

Also grabs a few example SmolTalk rows (the first qualifying rows from the same
dataset SFT learns from — not necessarily this run's exact training examples) so the
page can show 'this is the kind of thing it imitated'.

Writes projects/sft/stream.json.
"""
import json, time, gc
from pathlib import Path
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
OUT = Path(__file__).resolve().parent / "stream.json"
TOPK = 8
N_STEPS = 30

CKPTS = [
    ("base", "HuggingFaceTB/SmolLM2-360M"),
    ("sft_50", "/Users/aditya/align_sft/ckpts/checkpoint-50"),
    ("sft_400", "/Users/aditya/align_sft/ckpts/final"),
]
TOKENIZER = "/Users/aditya/align_sft/ckpts/final"

PROMPTS = [
    "How does a rainbow form?",
    "Why is the sky blue?",
    "Suggest a fun project for a rainy afternoon.",
    "How do I make a paper airplane?",
]


def piece(tok, tid):
    return tok.decode([tid])


def chat(tok, prompt):
    return tok.apply_chat_template([{"role": "user", "content": prompt}],
                                   tokenize=False, add_generation_prompt=True)


@torch.no_grad()
def stream(model, tok, prompt):
    text = chat(tok, prompt)
    ids = tok(text, return_tensors="pt", add_special_tokens=False).to(DEVICE)["input_ids"]
    steps = []
    for _ in range(N_STEPS):
        logits = model(ids).logits[0, -1]
        probs = F.softmax(logits.float(), -1)
        tp, ti = probs.topk(TOPK)
        nxt = int(ti[0].item())  # greedy: canonical output for a clean checkpoint comparison
        steps.append({
            "topk": [{"tok": piece(tok, int(i)), "p": round(float(p), 4)} for p, i in zip(tp, ti)],
            "chosen": piece(tok, nxt),
        })
        if nxt == (tok.eos_token_id or -1):
            break
        ids = torch.cat([ids, torch.tensor([[nxt]], device=DEVICE)], 1)
    return steps


def get_demos(n=3):
    try:
        from datasets import load_dataset
        ds = load_dataset("HuggingFaceTB/smoltalk", "all", split="train", streaming=True)
        out = []
        for row in ds:
            msgs = row.get("messages") or []
            if len(msgs) == 2 and msgs[0]["role"] == "user" and msgs[1]["role"] == "assistant":
                u, a = msgs[0]["content"], msgs[1]["content"]
                if 12 < len(u) < 120 and 40 < len(a) < 320 and "\n" not in u:
                    out.append({"prompt": u.strip(), "answer": a.strip()})
                    if len(out) >= n:
                        break
        if out:
            return out, "HuggingFaceTB/smoltalk"
    except Exception as e:
        print(f"  (smoltalk unavailable: {e}) — using illustrative demos", flush=True)
    return ([
        {"prompt": "What is the tallest mountain on Earth?",
         "answer": "The tallest mountain above sea level is Mount Everest, at about 8,849 meters (29,032 feet), in the Himalayas on the Nepal–China border."},
        {"prompt": "Give me a tip for staying focused.",
         "answer": "Try the two-minute rule: if a task takes less than two minutes, do it now. For bigger tasks, work in short focused blocks with a clear single goal, and put your phone out of reach."},
        {"prompt": "How do I boil an egg?",
         "answer": "Place eggs in a pot, cover with cold water, and bring to a boil. Once boiling, remove from heat, cover, and let sit: about 6 minutes for soft, 10–12 for hard-boiled. Cool in ice water before peeling."},
    ], "illustrative (SmolTalk style)")


def main():
    print(f"[{time.strftime('%H:%M:%S')}] tokenizer", flush=True)
    tok = AutoTokenizer.from_pretrained(TOKENIZER)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    demos, demo_src = get_demos()
    data = {"model": "HuggingFaceTB/SmolLM2-360M (base → SFT)", "topk": TOPK,
            "checkpoints": [c[0] for c in CKPTS], "demoSource": demo_src, "demonstrations": demos,
            "prompts": [{"prompt": p, "byCkpt": {}} for p in PROMPTS]}

    for name, path in CKPTS:
        print(f"[{time.strftime('%H:%M:%S')}] checkpoint {name}", flush=True)
        model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.float32).to(DEVICE).eval()
        for entry in data["prompts"]:
            entry["byCkpt"][name] = {"steps": stream(model, tok, entry["prompt"])}
        del model; gc.collect()
        if DEVICE == "mps":
            torch.mps.empty_cache()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"[{time.strftime('%H:%M:%S')}] WROTE {OUT}", flush=True)


if __name__ == "__main__":
    main()
