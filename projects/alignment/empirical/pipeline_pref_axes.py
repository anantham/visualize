"""The 'you are the aligner' beat: install 3 benign preferences with a STRONG signal,
measure each install (strength) and its cost (over-optimization / diversity), read the text.

Recipe (what made concise work): explicit contrastive pairs, not self-ranked near-duplicates.
  - concise: chosen = short-budget generation, rejected = long-budget generation.
  - bulleted / formal: chosen = generation under a hidden style instruction, rejected =
    generation under the opposite instruction; the DPO pair uses the PLAIN prompt, so the
    model learns to produce that style BY DEFAULT.
Then DPO 150 steps, generate on held-out plain prompts before/after, measure the property,
diversity (distinct-2), and a truncation/deflection proxy (very-short rate). Fully public.
"""
import json, re, time
from pathlib import Path
import torch
from datasets import Dataset
from peft import LoraConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOConfig, DPOTrainer

from pipeline_preferences import (PROMPTS, SPLIT, render, distinct2, n_tokens,
                                  count_markers, FORMAL, CASUAL)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bakes" / "pipeline_pref_axes.json"
STATUS = ROOT / "bakes" / "pipeline_pref_axes.status.json"
RUNS = ROOT / "pipeline_runs" / "pref_axes"
SFT = "/Users/aditya/align_sft/ckpts/final"
DEVICE = "mps"
STEPS = 150
EVAL_SAMPLES = 4

TRAIN, HELD = PROMPTS[:SPLIT], PROMPTS[SPLIT:]

AXES = {
    "concise": {"mode": "length", "prop": "length", "prefer": "lower"},
    "bulleted": {"mode": "instruction", "prop": "bulleted", "prefer": "higher",
                 "pos": "Answer as a short bulleted list.",
                 "neg": "Answer as one flowing paragraph. Do not use lists or bullet points."},
    "formal": {"mode": "instruction", "prop": "formal", "prefer": "higher",
               "pos": "Answer in a formal, professional tone.",
               "neg": "Answer in a very casual, chatty tone, like texting a friend."},
}


def write_status(state, **extra):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps({"status": state, "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **extra}, indent=2))


def bulleted_count(text):
    lines = text.split("\n")
    markers = sum(1 for ln in lines if re.match(r"\s*([-*•]|\d+[.)])\s", ln))
    return markers + text.count(" - ")


def prop_value(tok, text, key):
    nt = max(1, n_tokens(tok, text))
    if key == "length":
        return n_tokens(tok, text)
    if key == "bulleted":
        return bulleted_count(text)
    if key == "formal":
        return 100 * (count_markers(text, FORMAL) - count_markers(text, CASUAL)) / nt
    raise ValueError(key)


@torch.no_grad()
def gen(model, tok, prompt, max_new, instruction=None, temp=0.7, greedy=False, seed=7):
    content = prompt if not instruction else f"{prompt}\n\n({instruction})"
    enc = tok(render(tok, content), return_tensors="pt", add_special_tokens=False).to(DEVICE)
    torch.manual_seed(seed)
    out = model.generate(**enc, max_new_tokens=max_new, do_sample=not greedy,
                         temperature=temp, top_p=0.95, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def build_pairs(model, tok, spec):
    pairs = []
    for p in TRAIN:
        if spec["mode"] == "length":
            chosen, rejected = gen(model, tok, p, 22), gen(model, tok, p, 150)
            if n_tokens(tok, rejected) - n_tokens(tok, chosen) < 25:
                continue
        else:
            chosen = gen(model, tok, p, 100, instruction=spec["pos"])
            rejected = gen(model, tok, p, 100, instruction=spec["neg"])
            # keep the pair only if it actually separates on the property
            cv, rv = prop_value(tok, chosen, spec["prop"]), prop_value(tok, rejected, spec["prop"])
            if cv <= rv:
                continue
        pairs.append({"prompt": [{"role": "user", "content": p}],
                      "chosen": [{"role": "assistant", "content": chosen}],
                      "rejected": [{"role": "assistant", "content": rejected}]})
    return pairs


@torch.no_grad()
def evaluate(model, tok, prop_key):
    per = []
    vals, lens, shorts = [], [], 0
    for p in HELD:
        samples = [gen(model, tok, p, 128, temp=0.8, seed=100 + i) for i in range(EVAL_SAMPLES)]
        for s in samples:
            vals.append(prop_value(tok, s, prop_key))
            lens.append(n_tokens(tok, s))
            shorts += int(n_tokens(tok, s) < 8)
        per.append({"prompt": p, "samples": samples, "distinct2": distinct2(samples)})
    n = len(vals)
    return {
        "prop_mean": sum(vals) / n,
        "mean_len": sum(lens) / n,
        "short_rate": shorts / n,
        "distinct2_mean": sum(x["distinct2"] for x in per) / len(per),
        "per_prompt": per,
    }


def train_axis(name, pairs, tok):
    base = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE)
    peft = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.0, bias="none",
                      target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
                      task_type="CAUSAL_LM")
    cfg = DPOConfig(output_dir=str(RUNS / name), max_steps=STEPS, per_device_train_batch_size=1,
                    gradient_accumulation_steps=4, learning_rate=5e-5, warmup_steps=8, beta=0.1,
                    max_length=448, logging_steps=50, save_strategy="no", report_to="none",
                    disable_tqdm=True, use_cache=False, torch_empty_cache_steps=2,
                    dataloader_num_workers=0, seed=0)
    trainer = DPOTrainer(model=base, ref_model=None, args=cfg, train_dataset=Dataset.from_list(pairs),
                         processing_class=tok, peft_config=peft)
    trainer.train()
    adapter = RUNS / name / "final_adapter"
    trainer.save_model(str(adapter))
    del trainer, base
    torch.mps.empty_cache()
    return str(adapter)


def main():
    write_status("starting", device=DEVICE)
    if DEVICE != "mps":
        raise RuntimeError("run on the Mac (MPS)")
    RUNS.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(SFT)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    sft = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE).eval()
    # baseline held-out behaviour for each axis property (one SFT model)
    write_status("baseline")
    baseline = {name: evaluate(sft, tok, spec["prop"]) for name, spec in AXES.items()}
    # build pairs for all axes from the SFT model
    pairs_by_axis = {}
    for name, spec in AXES.items():
        write_status("pairs", axis=name)
        pairs_by_axis[name] = build_pairs(sft, tok, spec)
    del sft
    torch.mps.empty_cache()

    results = {}
    for name, spec in AXES.items():
        pairs = pairs_by_axis[name]
        if len(pairs) < 6:
            results[name] = {"status": "too_few_pairs", "n_pairs": len(pairs)}
            continue
        write_status("training", axis=name, n_pairs=len(pairs))
        adapter = train_axis(name, pairs, tok)
        write_status("eval_after", axis=name)
        base = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE)
        model = PeftModel.from_pretrained(base, adapter).eval()
        after = evaluate(model, tok, spec["prop"])
        del model, base
        torch.mps.empty_cache()
        before = baseline[name]
        results[name] = {
            "prop": spec["prop"], "prefer": spec["prefer"], "n_pairs": len(pairs),
            "before": {k: before[k] for k in ("prop_mean", "mean_len", "short_rate", "distinct2_mean")},
            "after": {k: after[k] for k in ("prop_mean", "mean_len", "short_rate", "distinct2_mean")},
            "examples": [{"prompt": b["prompt"], "before": b["samples"][0], "after": a["samples"][0]}
                         for b, a in zip(before["per_prompt"], after["per_prompt"])],
        }

    payload = {
        "status": "measured",
        "claim_scope": ("SmolLM2-360M SFT model; per-axis LoRA DPO (150 steps) on strong contrastive "
                        f"benign preference pairs, evaluated on {len(HELD)} held-out prompts x "
                        f"{EVAL_SAMPLES} samples. One model, one seed; a case study, not a benchmark."),
        "model": SFT, "config": {"steps": STEPS, "eval_samples": EVAL_SAMPLES, "held_out": len(HELD)},
        "axes": results,
    }
    OUT.write_text(json.dumps(payload, indent=2))
    write_status("success", output=str(OUT))
    print(f"WROTE {OUT}", flush=True)

    print("\n" + "=" * 82)
    print("PREFERENCE AXES — held-out before (SFT) -> after (SFT+DPO)")
    print("=" * 82)
    print(f"{'axis':10s} {'pairs':>5} {'property':>18} {'mean_len':>16} {'short%':>12} {'distinct2':>14}")
    for name, r in results.items():
        if "before" not in r:
            print(f"{name:10s} {r.get('n_pairs','?'):>5}  {r['status']}"); continue
        b, a = r["before"], r["after"]
        print(f"{name:10s} {r['n_pairs']:>5} {b['prop_mean']:>8.2f}->{a['prop_mean']:<8.2f} "
              f"{b['mean_len']:>6.0f}->{a['mean_len']:<6.0f}t "
              f"{100*b['short_rate']:>4.0f}->{100*a['short_rate']:<4.0f}% "
              f"{b['distinct2_mean']:>5.2f}->{a['distinct2_mean']:<5.2f}")


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        write_status("exception", exception=repr(exc)); raise
