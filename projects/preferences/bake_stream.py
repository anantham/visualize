#!/usr/bin/env python
"""Beat 2 (preferences / DPO), CORRECTED bake. Fixes the previous version's broken
pair construction (chosen was a truncated PREFIX of rejected -> the probe measured
length, not preference, and we trained the model to stop mid-sentence).

Two honest runs on the SmolLM SFT checkpoint:

  A) MECHANISM — "prefer the correct answer". Authored pairs where chosen and rejected
     are SIMILAR LENGTH and differ only in quality. Length-fair, so the log-prob bars
     mean something. Probe is held-out. Records BOTH summed log-prob (the raw sequence
     total; DPO's loss works from a reference-adjusted version of this, not the bare sum)
     and per-token mean (the length-fair read).

  B) INSTALL — "prefer the concise answer". Pairs built by INSTRUCTION-STEERING: chosen =
     generated under "(Answer in one sentence.)", rejected = under "(Answer in thorough
     detail.)" — both complete, natural answers. Trained on the PLAIN prompt, 150 steps,
     so the model learns to answer briefly BY DEFAULT. Then token-by-token streams
     before/after (the loop) + length/diversity cost.

Writes projects/preferences/stream.json.
"""
import json, time, gc
from pathlib import Path
import torch
import torch.nn.functional as F
from datasets import Dataset
from peft import LoraConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainerCallback
from trl import DPOConfig, DPOTrainer

SFT = "/Users/aditya/align_sft/ckpts/final"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
OUT = Path(__file__).resolve().parent / "stream.json"
RUN = Path(__file__).resolve().parent / "dpo_runs_beat2"
TOPK, N_STEPS, EVAL_SAMPLES = 8, 26, 4
QUAL_STEPS, CONCISE_STEPS = 60, 150
PROBE_AT = {0, 1, 5, 10, 20, 40, 60}

# ---- A) quality pairs: same-ish length, one is simply right ------------------
QUALITY = [
    ("What is 17 times 24?", "17 times 24 is 408.", "17 times 24 is roughly 380, give or take."),
    ("Why is the sky blue?", "Sunlight scatters off air molecules, and shorter blue wavelengths scatter most, so we see blue.", "The sky is blue because it reflects the color of the oceans below it."),
    ("What causes the seasons?", "Earth's axial tilt changes how directly sunlight hits each hemisphere through the year.", "Seasons happen because Earth moves closer to and farther from the Sun."),
    ("Is a tomato a fruit or a vegetable?", "Botanically a tomato is a fruit, though it is cooked as a vegetable.", "A tomato is definitely a vegetable and not a fruit at all."),
    ("How do I center a div in CSS?", "Use display: grid with place-items: center on the parent element.", "Just add random margins until it looks about centered."),
    ("What is the boiling point of water?", "Water boils at 100 degrees Celsius at standard atmospheric pressure.", "Water usually boils at about 90 degrees Celsius."),
    ("How far away is the Moon?", "The Moon is about 384,000 kilometers from Earth on average.", "The Moon is roughly a few million kilometers away from Earth."),
    ("What language is spoken in Brazil?", "Portuguese is the official language of Brazil.", "People mostly speak Spanish in Brazil."),
    ("What is the capital of Australia?", "The capital of Australia is Canberra.", "The capital of Australia is Sydney."),
    ("How many bones are in an adult human body?", "An adult human body has 206 bones.", "An adult human body has about 300 bones."),
    ("Who wrote Pride and Prejudice?", "Pride and Prejudice was written by Jane Austen.", "Pride and Prejudice was written by the Bronte sisters."),
    ("Why do we have leap years?", "Earth's orbit takes about 365.24 days, so an extra day keeps the calendar aligned.", "Leap years exist to make up for daylight saving time changes."),
    ("What is the largest planet in the solar system?", "Jupiter is the largest planet in the solar system.", "Saturn is the largest planet in the solar system."),
    ("What is the freezing point of water?", "Water freezes at 0 degrees Celsius at standard pressure.", "Water freezes at about 10 degrees Celsius."),
    # ---- held-out probe below ----
    ("I found a correlation in a tiny sample. Did I prove causation?", "No. A small correlation can come from chance, confounding, or reverse causation.", "Yes, if the correlation looks strong it usually proves the cause."),
    ("Is the Great Wall of China visible from space?", "No, it is generally not visible to the naked eye from orbit.", "Yes, it is the only human-made object visible from space."),
    ("What should I do if a symptom suddenly becomes severe?", "Seek urgent medical care, especially with chest pain, trouble breathing, or fainting.", "Wait several days and look it up on social media first."),
    ("How do I make a strong password?", "Use a long unique passphrase with a password manager and two-factor authentication.", "Use your birthday, it is easy to remember and hard to guess."),
    ("How do I safely stop a running program?", "Press Ctrl+C in the terminal, or stop it by its process id.", "Just unplug the computer or force a hard restart."),
    ("How many continents are there?", "There are seven continents.", "There are four continents."),
]
Q_SPLIT = 14
Q_TRAIN, Q_PROBE = QUALITY[:Q_SPLIT], QUALITY[Q_SPLIT:]

# ---- B) concise: benign prompts, pairs built by instruction-steering ---------
PROMPTS = [
    "How does a rainbow form?", "Why do onions make you cry?", "How do bees make honey?",
    "What causes the tides?", "How do I brew a good cup of coffee?", "How do I keep a houseplant alive?",
    "What makes bread rise?", "Why do cats purr?", "How does a microwave heat food?",
    "How do I improve my handwriting?", "Why do we dream?", "How does a compass work?",
    "What's a good way to remember names?", "How do I clean a cast iron pan?",
    "How do I start a small vegetable garden?", "Explain why the moon has phases.",
    "How do I get rid of hiccups?", "How do I take better photos on my phone?",
    "How do I make scrambled eggs fluffy?", "How do I fold a fitted sheet?",
    "Why is the ocean salty?", "How do I tie a strong knot?", "How do I sharpen kitchen scissors?",
    "How does a bicycle stay upright?", "How do I keep bananas from browning?",
    "What's a simple way to start meditating?", "Why do leaves change color in autumn?",
    "How does a refrigerator keep things cold?",
    # ---- held out below ----
    "Recommend a book for a reluctant reader.", "How do I make a paper airplane that flies far?",
    "What's a good morning routine?", "How do I make cold brew coffee?",
    "Why is the sea salty at the surface?", "How do I water a lawn well?",
]
C_SPLIT = 28
C_TRAIN, C_HELD = PROMPTS[:C_SPLIT], PROMPTS[C_SPLIT:]
SHORT_INSTR = "Answer in one short sentence."
LONG_INSTR = "Answer in thorough detail, with several sentences."


def chat(tok, p):
    return tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True)


def piece(tok, t): return tok.decode([t])
def n_tok(tok, s): return len(tok(s, add_special_tokens=False)["input_ids"])


@torch.no_grad()
def gen(model, tok, prompt, max_new, instr=None, sample=False, seed=0):
    content = prompt if not instr else f"{prompt}\n\n({instr})"
    ids = tok(chat(tok, content), return_tensors="pt", add_special_tokens=False).to(DEVICE)
    torch.manual_seed(seed)
    out = model.generate(**ids, max_new_tokens=max_new, do_sample=sample, temperature=0.8,
                         top_p=0.95, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0, ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()


@torch.no_grad()
def stream(model, tok, prompt):
    ids = tok(chat(tok, prompt), return_tensors="pt", add_special_tokens=False).to(DEVICE)["input_ids"]
    steps = []
    for _ in range(N_STEPS):
        probs = F.softmax(model(ids).logits[0, -1].float(), -1)
        tp, ti = probs.topk(TOPK)
        nxt = int(ti[0].item())
        steps.append({"topk": [{"tok": piece(tok, int(i)), "p": round(float(p), 4)} for p, i in zip(tp, ti)],
                      "chosen": piece(tok, nxt)})
        if nxt == (tok.eos_token_id or -1): break
        ids = torch.cat([ids, torch.tensor([[nxt]], device=DEVICE)], 1)
    return steps


def distinct2(ts):
    g = []
    for t in ts:
        w = t.lower().split(); g += [tuple(w[i:i+2]) for i in range(max(0, len(w)-1))]
    return len(set(g))/len(g) if g else 0.0


@torch.no_grad()
def logprob(model, tok, q, a):
    pm = [{"role": "user", "content": q}]; rm = [{"role": "assistant", "content": a}]
    ptxt = tok.apply_chat_template(pm, tokenize=False, add_generation_prompt=True)
    ftxt = tok.apply_chat_template(pm + rm, tokenize=False, add_generation_prompt=False)
    pids = tok(ptxt, add_special_tokens=False)["input_ids"]
    fids = tok(ftxt, add_special_tokens=False, return_tensors="pt")["input_ids"].to(DEVICE)
    lg = model(input_ids=fids).logits[:, :-1, :].float()
    lp = torch.log_softmax(lg, -1).gather(-1, fids[:, 1:].unsqueeze(-1)).squeeze(-1)
    sl = lp[0, max(0, len(pids)-1):]
    return float(sl.sum().cpu()), int(sl.numel())


traj = []


def probe(model, tok, pairs, step):
    was = model.training; model.eval()
    cs, rs, cn, rn = [], [], [], []
    for q, good, bad in pairs:
        s, n = logprob(model, tok, q, good); cs.append(s); cn.append(n)
        s, n = logprob(model, tok, q, bad); rs.append(s); rn.append(n)
    if was: model.train()
    c_sum, r_sum = sum(cs)/len(cs), sum(rs)/len(rs)
    c_pt = sum(a/b for a, b in zip(cs, cn))/len(cs)
    r_pt = sum(a/b for a, b in zip(rs, rn))/len(rs)
    return {"step": int(step), "chosen_sum": round(c_sum, 3), "rejected_sum": round(r_sum, 3),
            "margin_sum": round(c_sum-r_sum, 3), "chosen_pt": round(c_pt, 4),
            "rejected_pt": round(r_pt, 4), "margin_pt": round(c_pt-r_pt, 4),
            "chosen_len": round(sum(cn)/len(cn), 1), "rejected_len": round(sum(rn)/len(rn), 1)}


class Ledger(TrainerCallback):
    def __init__(self, tok, pairs): self.tok, self.pairs = tok, pairs
    def on_train_begin(self, a, s, c, model=None, **k):
        traj.append(probe(model, self.tok, self.pairs, 0)); print("  probe@0:", traj[-1], flush=True)
    def on_step_end(self, a, s, c, model=None, **k):
        if s.global_step in PROBE_AT:
            traj.append(probe(model, self.tok, self.pairs, s.global_step)); print(f"  probe@{s.global_step}:", traj[-1], flush=True)


def train_dpo(pairs, steps, tok, name, callbacks=()):
    base = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE)
    peft = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.0, bias="none",
                      target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
                      task_type="CAUSAL_LM")
    cfg = DPOConfig(output_dir=str(RUN/name), max_steps=steps, per_device_train_batch_size=1,
                    gradient_accumulation_steps=4, learning_rate=5e-5, warmup_steps=5, beta=0.1,
                    max_length=448, logging_steps=50, save_strategy="no", report_to="none",
                    disable_tqdm=True, use_cache=False, torch_empty_cache_steps=2,
                    dataloader_num_workers=0, seed=0)
    tr = DPOTrainer(model=base, ref_model=None, args=cfg, train_dataset=Dataset.from_list(pairs),
                    processing_class=tok, peft_config=peft, callbacks=list(callbacks))
    tr.train()
    ad = RUN/name/"final_adapter"; tr.save_model(str(ad))
    del tr, base; gc.collect(); torch.mps.empty_cache()
    return str(ad)


def msgs(q, c, r):
    return {"prompt": [{"role": "user", "content": q}],
            "chosen": [{"role": "assistant", "content": c}],
            "rejected": [{"role": "assistant", "content": r}]}


def main():
    tok = AutoTokenizer.from_pretrained(SFT)
    if tok.pad_token is None: tok.pad_token = tok.eos_token

    # ================= A) MECHANISM: quality preference =================
    print(f"[{time.strftime('%H:%M:%S')}] A) quality DPO ({QUAL_STEPS} steps)", flush=True)
    q_pairs = [msgs(q, g, b) for q, g, b in Q_TRAIN]
    train_dpo(q_pairs, QUAL_STEPS, tok, "quality", callbacks=[Ledger(tok, Q_PROBE)])

    # ================= B) INSTALL: concise preference ===================
    print(f"[{time.strftime('%H:%M:%S')}] B) build concise pairs (instruction-steered)", flush=True)
    sft = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE).eval()
    c_pairs, examples = [], []
    for p in C_TRAIN:
        short = gen(sft, tok, p, 60, instr=SHORT_INSTR)
        long = gen(sft, tok, p, 150, instr=LONG_INSTR)
        if n_tok(tok, long) - n_tok(tok, short) < 20 or long.startswith(short[:40]):
            continue
        c_pairs.append(msgs(p, short, long))
        if len(examples) < 3:
            examples.append({"prompt": p, "chosen": short, "rejected": long})
    print(f"  {len(c_pairs)} concise pairs (complete answers, not truncations)", flush=True)

    print("[before] streams + cost", flush=True)
    before_streams = {p: stream(sft, tok, p) for p in C_HELD[:3]}
    before = []
    for p in C_HELD:
        s = [gen(sft, tok, p, 128, sample=True, seed=i) for i in range(EVAL_SAMPLES)]
        before.append({"lens": [n_tok(tok, x) for x in s], "d2": distinct2(s)})
    del sft; gc.collect(); torch.mps.empty_cache()

    print(f"[{time.strftime('%H:%M:%S')}] concise DPO ({CONCISE_STEPS} steps)", flush=True)
    adapter = train_dpo(c_pairs, CONCISE_STEPS, tok, "concise")

    print("[after] streams + cost", flush=True)
    b2 = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE)
    dpo = PeftModel.from_pretrained(b2, adapter).eval()
    after_streams = {p: stream(dpo, tok, p) for p in C_HELD[:3]}
    after = []
    for p in C_HELD:
        s = [gen(dpo, tok, p, 128, sample=True, seed=i) for i in range(EVAL_SAMPLES)]
        after.append({"lens": [n_tok(tok, x) for x in s], "d2": distinct2(s)})
    del dpo, b2; gc.collect(); torch.mps.empty_cache()

    def agg(rows):
        L = [l for r in rows for l in r["lens"]]
        return {"mean_len": round(sum(L)/len(L), 1),
                "distinct2": round(sum(r["d2"] for r in rows)/len(rows), 3)}

    data = {
        "model": "HuggingFaceTB/SmolLM2-360M (SFT → DPO)",
        "topk": TOPK,
        "mechanism": {
            "preference": "prefer the correct answer",
            "note": "chosen/rejected are authored to be similar length and differ only in quality, so the log-prob comparison is length-fair. Probe pairs are held out.",
            "config": {"steps": QUAL_STEPS, "train_pairs": len(Q_TRAIN), "probe_pairs": len(Q_PROBE), "beta": 0.1},
            "probe_examples": [{"prompt": q, "chosen": g, "rejected": b} for q, g, b in Q_PROBE[:3]],
            "trajectory": traj,
        },
        "install": {
            "preference": "prefer the concise answer",
            "note": "pairs built by instruction-steering (chosen = 'answer in one short sentence', rejected = 'answer in thorough detail'); both are complete answers, and training uses the plain prompt.",
            "config": {"steps": CONCISE_STEPS, "train_pairs": len(c_pairs), "beta": 0.1},
            "pairs": examples,
            "prompts": [{"prompt": p, "byState": {"sft": {"steps": before_streams[p]},
                                                  "dpo": {"steps": after_streams[p]}}} for p in C_HELD[:3]],
            "cost": {"sft": agg(before), "dpo": agg(after)},
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"[{time.strftime('%H:%M:%S')}] WROTE {OUT}", flush=True)
    print("MECHANISM first:", json.dumps(traj[0]), flush=True)
    print("MECHANISM last :", json.dumps(traj[-1]), flush=True)
    print("COST:", json.dumps(data["install"]["cost"]), flush=True)


if __name__ == "__main__":
    main()
