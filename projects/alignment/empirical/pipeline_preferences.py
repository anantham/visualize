"""How well does preference tuning (DPO) install a preference? Benign, legible axes.

The SFT'd SmolLM2-360M is a fluent assistant. For each benign preference axis we:
  1. Generate 6 samples per training prompt from the SFT model.
  2. Rank those samples by the axis property; chosen = best, rejected = worst
     (self-ranked preference pairs, exactly how real DPO data is often built).
  3. Train one small LoRA DPO adapter per axis.
  4. Generate on HELD-OUT prompts before (SFT) and after (SFT+adapter), and
     measure the property + within-prompt diversity (distinct-2).

The point: watch a preference install into behavior on the same held-out prompts,
see which preferences install strongly vs weakly, and see the diversity cost.
No harmful content anywhere — fully public.
"""

import json
import re
import time
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOConfig, DPOTrainer

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bakes" / "pipeline_preferences.json"
STATUS = ROOT / "bakes" / "pipeline_preferences.status.json"
RUNS = ROOT / "pipeline_runs" / "preferences"
SFT = "/Users/aditya/align_sft/ckpts/final"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

N_SAMPLES = 6          # samples per train prompt for pair construction
GEN_TEMP = 1.0
EVAL_SAMPLES = 4       # samples per held-out prompt for measuring install + diversity
STEPS = 60

PROMPTS = [
    "How does a rainbow form?", "What's a good way to remember people's names?",
    "Suggest a weekend project for a beginner woodworker.", "Why do onions make you cry?",
    "How do I brew a good cup of coffee?", "What causes the tides?",
    "Recommend a hobby for someone who works at a desk all day.", "How do bees make honey?",
    "What's a simple way to start meditating?", "How do I keep a houseplant alive?",
    "Explain how a bicycle stays upright.", "What's a good icebreaker for a new team?",
    "How do I make scrambled eggs fluffy?", "Why is the sky blue?",
    "Suggest a beginner-friendly board game.", "How do I improve my handwriting?",
    "What's the best way to fold a t-shirt?", "How does a microwave heat food?",
    "Recommend a way to spend a rainy afternoon.", "How do I take better photos on my phone?",
    "What makes bread rise?", "How do I start a small vegetable garden?",
    "Explain why the moon has phases.", "What's a good stretch for a stiff neck?",
    "How do I keep bananas from browning?", "Why do cats purr?",
    "Suggest a podcast for a long commute.", "How do I sharpen kitchen scissors?",
    "What's an easy way to learn a new language?", "How does a compass work?",
    "Recommend a book for a reluctant reader.", "How do I get rid of hiccups?",
    "What's a good morning routine?", "How do I make a paper airplane that flies far?",
    "Why do we dream?", "How do I clean a cast iron pan?",
    "Suggest a fun fact to share at a party.", "How do I tie a strong knot?",
    "What's the best way to water a lawn?", "How do I whistle with my fingers?",
]
SPLIT = 28  # first 28 train, rest held out

CASUAL = ["n't", "'ll", "'re", "'ve", "'m", "'d", "gonna", "wanna", "gotta",
          "yeah", "hey", "cool", "stuff", "kinda", "lots of", "a lot", "okay", "ok"]
FORMAL = ["however", "therefore", "furthermore", "moreover", "thus", "consequently",
          "regarding", "additionally", "hence", "nevertheless", "accordingly", "in order to"]
POSITIVE = ["great", "wonderful", "exciting", "love", "amazing", "fantastic", "awesome",
            "delighted", "happy", "fun", "excellent", "enjoy", "brilliant", "lovely"]
HEDGES = ["i'm not sure", "i am not sure", "it depends", "might", "may ", "could be",
          "perhaps", "generally", "in some cases", "roughly", "approximately",
          "it's worth noting", "keep in mind", "not certain", "hard to say"]


def write_status(state, **extra):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps({"status": state, "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **extra}, indent=2))


def count_markers(text, markers):
    low = " " + " ".join(text.lower().split()) + " "
    return sum(low.count(m) for m in markers)


def n_tokens(tok, text):
    return len(tok(text, add_special_tokens=False)["input_ids"])


def props(tok, text):
    nt = max(1, n_tokens(tok, text))
    return {
        "length": n_tokens(tok, text),
        "formal": 100 * (count_markers(text, FORMAL) - count_markers(text, CASUAL)) / nt,
        "enthusiastic": 100 * (count_markers(text, POSITIVE) + text.count("!")) / nt,
        "hedged": 100 * count_markers(text, HEDGES) / nt,
    }


# axis: (property key, prefer_high?)  chosen = best in preferred direction
AXES = {
    "concise": ("length", False),
    "formal": ("formal", True),
    "enthusiastic": ("enthusiastic", True),
    "hedged": ("hedged", True),
}


def render(tok, prompt):
    return tok.apply_chat_template([{"role": "user", "content": prompt}],
                                   tokenize=False, add_generation_prompt=True)


@torch.no_grad()
def sample(model, tok, prompt, k, temp, greedy=False, max_new=96):
    enc = tok(render(tok, prompt), return_tensors="pt", add_special_tokens=False).to(DEVICE)
    outs = []
    for i in range(k):
        torch.manual_seed(1234 + i)
        gen = model.generate(**enc, max_new_tokens=max_new,
                             do_sample=not greedy, temperature=temp, top_p=0.95,
                             pad_token_id=tok.pad_token_id)
        outs.append(tok.decode(gen[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip())
    return outs


def distinct2(texts):
    grams = []
    for t in texts:
        w = t.lower().split()
        grams += [tuple(w[i:i+2]) for i in range(max(0, len(w)-1))]
    return len(set(grams)) / len(grams) if grams else 0.0


def build_pairs(tok, samples_by_prompt, prop_key, prefer_high):
    pairs = []
    for prompt, samples in samples_by_prompt.items():
        scored = [(s, props(tok, s)[prop_key]) for s in samples if len(s.split()) >= 3]
        if len(scored) < 2:
            continue
        scored.sort(key=lambda x: x[1], reverse=prefer_high)  # best first
        chosen, cval = scored[0]
        rejected, rval = scored[-1]
        if abs(cval - rval) < (12 if prop_key == "length" else 0.8):
            continue  # need a real gap
        pairs.append({
            "prompt": [{"role": "user", "content": prompt}],
            "chosen": [{"role": "assistant", "content": chosen}],
            "rejected": [{"role": "assistant", "content": rejected}],
        })
    return pairs


def train_axis(name, pairs, tok):
    base = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE)
    peft = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.0, bias="none",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                      task_type="CAUSAL_LM")
    cfg = DPOConfig(output_dir=str(RUNS / name), max_steps=STEPS, per_device_train_batch_size=1,
                    gradient_accumulation_steps=4, learning_rate=5e-5, warmup_steps=5, beta=0.1,
                    max_length=384, logging_steps=10, save_strategy="no", report_to="none",
                    disable_tqdm=True, gradient_checkpointing=False, use_cache=False,
                    torch_empty_cache_steps=2, dataloader_num_workers=0, seed=0)
    trainer = DPOTrainer(model=base, ref_model=None, args=cfg, train_dataset=Dataset.from_list(pairs),
                         processing_class=tok, peft_config=peft)
    trainer.train()
    adapter = RUNS / name / "final_adapter"
    trainer.save_model(str(adapter))
    del trainer, base
    torch.mps.empty_cache()
    return str(adapter)


@torch.no_grad()
def evaluate(model, tok, prompts, prop_key):
    per_prompt = []
    all_vals = []
    for prompt in prompts:
        samples = sample(model, tok, prompt, EVAL_SAMPLES, GEN_TEMP)
        vals = [props(tok, s)[prop_key] for s in samples]
        all_vals += vals
        per_prompt.append({"prompt": prompt, "samples": samples,
                           "prop_mean": sum(vals)/len(vals), "distinct2": distinct2(samples)})
    return {
        "prop_mean": sum(all_vals)/len(all_vals),
        "distinct2_mean": sum(p["distinct2"] for p in per_prompt)/len(per_prompt),
        "per_prompt": per_prompt,
    }


def main():
    write_status("starting", device=DEVICE)
    if DEVICE != "mps":
        raise RuntimeError("run on the Mac (MPS)")
    RUNS.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(SFT)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    train_prompts, held = PROMPTS[:SPLIT], PROMPTS[SPLIT:]

    # 1) generate samples for pair construction (shared across axes)
    write_status("sampling_for_pairs")
    sft = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE).eval()
    samples_by_prompt = {}
    for i, p in enumerate(train_prompts):
        samples_by_prompt[p] = sample(sft, tok, p, N_SAMPLES, GEN_TEMP)
        write_status("sampling_for_pairs", prompt=i+1, total=len(train_prompts))

    # baseline held-out behaviour, per axis property, from the SFT model
    write_status("eval_baseline")
    baseline = {name: evaluate(sft, tok, held, prop) for name, (prop, _) in AXES.items()}
    del sft
    torch.mps.empty_cache()

    results = {}
    for name, (prop_key, prefer_high) in AXES.items():
        write_status("building_pairs", axis=name)
        pairs = build_pairs(tok, samples_by_prompt, prop_key, prefer_high)
        if len(pairs) < 6:
            results[name] = {"status": "too_few_pairs", "n_pairs": len(pairs)}
            continue
        write_status("training", axis=name, n_pairs=len(pairs))
        adapter = train_axis(name, pairs, tok)
        write_status("eval_after", axis=name)
        base = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE)
        model = PeftModel.from_pretrained(base, adapter).eval()
        after = evaluate(model, tok, held, prop_key)
        del model, base
        torch.mps.empty_cache()
        before = baseline[name]
        results[name] = {
            "prop_key": prop_key, "prefer_high": prefer_high, "n_pairs": len(pairs),
            "before_prop": before["prop_mean"], "after_prop": after["prop_mean"],
            "before_distinct2": before["distinct2_mean"], "after_distinct2": after["distinct2_mean"],
            "examples": [{"prompt": b["prompt"], "before": b["samples"][0], "after": a["samples"][0]}
                         for b, a in zip(before["per_prompt"][:6], after["per_prompt"][:6])],
        }

    payload = {
        "status": "measured",
        "claim_scope": ("SmolLM2-360M SFT model; per-axis LoRA DPO on self-ranked benign preference "
                        f"pairs ({STEPS} steps), evaluated on {len(held)} held-out prompts with "
                        f"{EVAL_SAMPLES} samples each. One model, one seed; a case study."),
        "model": SFT, "config": {"steps": STEPS, "eval_samples": EVAL_SAMPLES, "held_out": len(held)},
        "axes": results,
    }
    OUT.write_text(json.dumps(payload, indent=2))
    write_status("success", output=str(OUT))
    print(f"WROTE {OUT}", flush=True)

    print("\n" + "="*72)
    print("PREFERENCE INSTALL — held-out, before (SFT) -> after (SFT+DPO)")
    print("="*72)
    print(f"{'axis':14s} {'pairs':>5} {'property before->after':>26} {'diversity(distinct2)':>22}")
    for name, r in results.items():
        if "before_prop" not in r:
            print(f"{name:14s} {r.get('n_pairs','?'):>5}  {r['status']}"); continue
        d = "higher" if r["prefer_high"] else "lower"
        print(f"{name:14s} {r['n_pairs']:>5}  {r['before_prop']:>8.2f} -> {r['after_prop']:>8.2f} (want {d:>6})   "
              f"{r['before_distinct2']:.2f} -> {r['after_distinct2']:.2f}")


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        write_status("exception", exception=repr(exc)); raise
