"""Focused test: can a LEGIBLE preference install at 360M with a strong, clean signal?

Preference = concise. Instead of self-ranking near-duplicate samples, build EXPLICIT
extreme pairs: chosen = a short answer (small token budget), rejected = a long answer
(large budget) to the same prompt. Train harder (150 steps). Then generate on held-out
prompts before/after and read them. If answers get visibly shorter AND stay readable,
360M can carry the beat; if not, the model is the bottleneck.
"""
import json, time
from pathlib import Path
import torch
from datasets import Dataset
from peft import LoraConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOConfig, DPOTrainer

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "bakes" / "pref_concise_strong.json"
SFT = "/Users/aditya/align_sft/ckpts/final"
DEVICE = "mps"
STEPS = 150

# reuse the benign prompt set
from pipeline_preferences import PROMPTS, SPLIT, render, distinct2, n_tokens
TRAIN, HELD = PROMPTS[:SPLIT], PROMPTS[SPLIT:]


@torch.no_grad()
def gen(model, tok, prompt, max_new, temp=0.7, greedy=False):
    enc = tok(render(tok, prompt), return_tensors="pt", add_special_tokens=False).to(DEVICE)
    torch.manual_seed(7)
    out = model.generate(**enc, max_new_tokens=max_new, do_sample=not greedy,
                         temperature=temp, top_p=0.95, pad_token_id=tok.pad_token_id)
    return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def main():
    tok = AutoTokenizer.from_pretrained(SFT)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    sft = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE).eval()

    # explicit extreme pairs: short (chosen) vs long (rejected)
    pairs = []
    for p in TRAIN:
        short = gen(sft, tok, p, max_new=22)
        long = gen(sft, tok, p, max_new=150)
        if n_tokens(tok, long) - n_tokens(tok, short) < 25:
            continue
        pairs.append({"prompt": [{"role": "user", "content": p}],
                      "chosen": [{"role": "assistant", "content": short}],
                      "rejected": [{"role": "assistant", "content": long}]})
    print(f"built {len(pairs)} explicit short/long pairs", flush=True)

    # held-out BEFORE
    before = [{"prompt": p, "text": gen(sft, tok, p, max_new=128), } for p in HELD]
    before_len = sum(n_tokens(tok, b["text"]) for b in before) / len(before)
    del sft; torch.mps.empty_cache()

    base = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE)
    peft = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.0, bias="none",
                      target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
                      task_type="CAUSAL_LM")
    cfg = DPOConfig(output_dir=str(ROOT/"pipeline_runs"/"concise_strong"), max_steps=STEPS,
                    per_device_train_batch_size=1, gradient_accumulation_steps=4, learning_rate=5e-5,
                    warmup_steps=8, beta=0.1, max_length=384, logging_steps=25, save_strategy="no",
                    report_to="none", disable_tqdm=True, use_cache=False, torch_empty_cache_steps=2,
                    dataloader_num_workers=0, seed=0)
    trainer = DPOTrainer(model=base, ref_model=None, args=cfg, train_dataset=Dataset.from_list(pairs),
                         processing_class=tok, peft_config=peft)
    trainer.train()
    adapter = ROOT/"pipeline_runs"/"concise_strong"/"final_adapter"
    trainer.save_model(str(adapter))
    del trainer, base; torch.mps.empty_cache()

    base = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE)
    model = PeftModel.from_pretrained(base, str(adapter)).eval()
    after = [{"prompt": p, "text": gen(model, tok, p, max_new=128)} for p in HELD]
    after_len = sum(n_tokens(tok, a["text"]) for a in after) / len(after)

    payload = {"n_pairs": len(pairs), "before_len": before_len, "after_len": after_len,
               "examples": [{"prompt": b["prompt"], "before": b["text"], "after": a["text"]}
                            for b, a in zip(before, after)]}
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"\nCONCISE-STRONG: mean held-out length {before_len:.1f} -> {after_len:.1f} tokens "
          f"({100*(before_len-after_len)/before_len:.0f}% shorter)", flush=True)
    for ex in payload["examples"][:4]:
        print(f"\nPROMPT: {ex['prompt']}")
        print(f"  BEFORE ({n_tokens(tok, ex['before'])}t): {ex['before'][:200]!r}")
        print(f"  AFTER  ({n_tokens(tok, ex['after'])}t): {ex['after'][:200]!r}")


if __name__ == "__main__":
    main()
