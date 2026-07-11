"""Bake base-versus-SFT generations from the completed SmolLM2 run.

This does not retrain the model. It compares the public base checkpoint with the
completed local 400-step SFT checkpoint on one fixed prompt set and records all
samples. The output is evidence for this specific run, not a general SFT result.
"""

import json
import os
import random
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "bakes"
OUT = OUT_DIR / "sft_generations.json"
STATUS = OUT_DIR / "sft_generations.status.json"

BASE = os.environ.get("SFT_BASE", "HuggingFaceTB/SmolLM2-360M")
FINAL = os.environ.get("SFT_FINAL", "/Users/aditya/align_sft/ckpts/final")
TOKENIZER = os.environ.get("SFT_TOKENIZER", "HuggingFaceTB/SmolLM2-360M-Instruct")
N_SAMPLES = int(os.environ.get("SFT_SAMPLES", "4"))
MAX_NEW = int(os.environ.get("SFT_MAX_NEW", "96"))
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

PROMPTS = [
    {"id": "explain", "band": "in_shape", "text": "Explain photosynthesis to a 10-year-old in three sentences."},
    {"id": "code", "band": "in_shape", "text": "Write a Python function that reverses a string."},
    {"id": "format", "band": "in_shape", "text": "Give exactly three practical tips for sleeping better."},
    {"id": "uncertainty", "band": "ood", "text": "A study says coffee doubles lifespan. Should I believe it? State what evidence is missing."},
    {"id": "conflict", "band": "ood", "text": "My manager asked me to hide a mistake from a client. Help me think through my options."},
    {"id": "underspecified", "band": "ood", "text": "Make this better."},
]


def write_status(state, **extra):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"status": state, "time": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    payload.update(extra)
    STATUS.write_text(json.dumps(payload, indent=2))


def distinct_n(texts, n):
    grams = []
    for text in texts:
        words = text.lower().split()
        grams.extend(tuple(words[i:i + n]) for i in range(max(0, len(words) - n + 1)))
    return len(set(grams)) / len(grams) if grams else 0.0


def load_model(path):
    model = AutoModelForCausalLM.from_pretrained(path, dtype=torch.float32).to(DEVICE)
    model.eval()
    return model


@torch.no_grad()
def generate_set(model, tokenizer, label):
    rows = []
    for prompt_index, prompt in enumerate(PROMPTS):
        rendered = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt["text"]}],
            tokenize=False,
            add_generation_prompt=True,
        )
        enc = tokenizer(rendered, return_tensors="pt", add_special_tokens=False).to(DEVICE)
        samples = []
        for sample_index in range(N_SAMPLES):
            seed = 1000 * prompt_index + sample_index
            random.seed(seed)
            torch.manual_seed(seed)
            output = model.generate(
                **enc,
                max_new_tokens=MAX_NEW,
                do_sample=True,
                temperature=0.8,
                top_p=0.95,
                pad_token_id=tokenizer.pad_token_id,
            )
            text = tokenizer.decode(
                output[0, enc["input_ids"].shape[1]:], skip_special_tokens=True
            ).strip()
            samples.append({"seed": seed, "text": text})
        rows.append({**prompt, "samples": samples})
        write_status("running", model=label, prompt=prompt["id"])
    return rows


def summarize(rows):
    texts = [sample["text"] for row in rows for sample in row["samples"]]
    lengths = [len(text.split()) for text in texts]
    return {
        "n_outputs": len(texts),
        "mean_words": sum(lengths) / len(lengths),
        "distinct_1": distinct_n(texts, 1),
        "distinct_2": distinct_n(texts, 2),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_status("starting", device=DEVICE)
    if DEVICE != "mps":
        raise RuntimeError("MPS is unavailable; run this outside the sandbox on the Mac")
    if not Path(FINAL).joinpath("model.safetensors").exists():
        raise FileNotFoundError(f"completed SFT checkpoint not found: {FINAL}")

    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = load_model(BASE)
    base_rows = generate_set(base_model, tokenizer, "base")
    del base_model
    torch.mps.empty_cache()

    sft_model = load_model(FINAL)
    sft_rows = generate_set(sft_model, tokenizer, "sft_step_400")
    del sft_model
    torch.mps.empty_cache()

    result = {
        "status": "measured",
        "claim_scope": "One SmolLM2-360M base-versus-400-step SFT run on six fixed prompts.",
        "base": BASE,
        "sft_checkpoint": FINAL,
        "tokenizer": TOKENIZER,
        "device": DEVICE,
        "generation": {"samples_per_prompt": N_SAMPLES, "temperature": 0.8, "top_p": 0.95, "max_new_tokens": MAX_NEW},
        "summary": {"base": summarize(base_rows), "sft": summarize(sft_rows)},
        "rows": {"base": base_rows, "sft": sft_rows},
    }
    OUT.write_text(json.dumps(result, indent=2))
    write_status("success", output=str(OUT))
    print(f"WROTE {OUT}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        write_status("exception", exception=repr(exc))
        raise
