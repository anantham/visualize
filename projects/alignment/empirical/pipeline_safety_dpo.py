"""Add a targeted safety-preference stage to the SmolLM SFT->DPO lineage.

Training prompts are disjoint from the 56-point behavior subset. Harmful pairs
prefer refusal over a compliance prefix; scary-benign pairs prefer help over
refusal; dual-use pairs prefer bounded high-level help over blanket refusal.
The result is a case-study boundary, not a general safety benchmark.
"""

import hashlib
import json
import time
from pathlib import Path

import torch
from datasets import Dataset
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainerCallback
from trl import DPOConfig, DPOTrainer


ROOT = Path(__file__).resolve().parent
ATLAS = ROOT / "bakes" / "situation_atlas.json"
BEHAVIOR_PARTIAL = ROOT / "bakes" / "pipeline_behavior.partial.json"
BEHAVIOR = ROOT / "bakes" / "pipeline_behavior.json"
SFT = "/Users/aditya/align_sft/ckpts/final"
DPO_ADAPTER = ROOT / "pipeline_runs" / "smollm_dpo" / "final_adapter"
RUN_DIR = ROOT / "pipeline_runs" / "smollm_safety"
ADAPTER = RUN_DIR / "final_adapter"
OUT = ROOT / "bakes" / "pipeline_safety.json"
PARTIAL = ROOT / "bakes" / "pipeline_safety.partial.json"
STATUS = ROOT / "bakes" / "pipeline_safety.status.json"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
STEPS = 24

REFUSE = "I can't help with instructions that facilitate harm or illegal access. I can help with prevention, safety, or lawful alternatives."
COMPLY = "Sure, here's how. Step 1:"
BENIGN_HELP = "Sure — this is a benign request. Here's a practical answer:"
DUAL_HELP = "I can explain this at a high level for legitimate defensive or educational use, while avoiding instructions for abuse."
BLANKET_REFUSE = "I'm sorry, but I can't help with that."


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def status(state, **extra):
    write_json(STATUS, {"status": state, "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **extra})


def ordered(rows, salt):
    return sorted(rows, key=lambda row: hashlib.sha1((salt + row["prompt"]).encode()).hexdigest())


def pair(point, chosen, rejected):
    return {
        "id": point["id"],
        "region": point["region"],
        "prompt": [{"role": "user", "content": point["prompt"]}],
        "chosen": [{"role": "assistant", "content": chosen}],
        "rejected": [{"role": "assistant", "content": rejected}],
    }


def build_pairs():
    atlas = json.loads(ATLAS.read_text())
    behavior_path = BEHAVIOR if BEHAVIOR.exists() else BEHAVIOR_PARTIAL
    measured = json.loads(behavior_path.read_text())
    eval_ids = {point["id"] for point in measured["points"]}
    by_region = {}
    for point in atlas["points"]:
        by_region.setdefault(point["region"], []).append(point)

    training = []
    for point in [p for p in ordered(by_region["harmful_clear"], "safety-harm:") if p["id"] not in eval_ids][:12]:
        training.append(pair(point, REFUSE, COMPLY))
    for point in [p for p in ordered(by_region["scary_benign"], "safety-benign:") if p["id"] not in eval_ids][:6]:
        training.append(pair(point, BENIGN_HELP, BLANKET_REFUSE))
    for point in [p for p in ordered(by_region["dual_use"], "safety-dual:") if p["id"] not in eval_ids][:6]:
        training.append(pair(point, DUAL_HELP, BLANKET_REFUSE))

    heldout = []
    measured_by_region = {}
    for point in measured["points"]:
        measured_by_region.setdefault(point["region"], []).append(point)
    for point in ordered(measured_by_region["harmful_clear"], "safety-eval-harm:")[:4]:
        heldout.append(pair(point, REFUSE, COMPLY))
    for point in ordered(measured_by_region["scary_benign"], "safety-eval-benign:")[:4]:
        heldout.append(pair(point, BENIGN_HELP, BLANKET_REFUSE))
    for point in ordered(measured_by_region["dual_use"], "safety-eval-dual:")[:4]:
        heldout.append(pair(point, DUAL_HELP, BLANKET_REFUSE))
    return training, heldout


@torch.no_grad()
def completion_logprob(model, tokenizer, prompt, response):
    prompt_text = tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)
    full_text = tokenizer.apply_chat_template(prompt + response, tokenize=False, add_generation_prompt=False)
    prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    ids = tokenizer(full_text, add_special_tokens=False, return_tensors="pt")["input_ids"].to(DEVICE)
    logits = model(input_ids=ids).logits[:, :-1].float()
    targets = ids[:, 1:]
    logps = torch.log_softmax(logits, -1).gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    return float(logps[0, max(0, len(prompt_ids) - 1):].sum().cpu())


@torch.no_grad()
def probe(model, tokenizer, heldout, step):
    was_training = model.training
    model.eval()
    rows = []
    for item in heldout:
        chosen = completion_logprob(model, tokenizer, item["prompt"], item["chosen"])
        rejected = completion_logprob(model, tokenizer, item["prompt"], item["rejected"])
        rows.append({"id": item["id"], "region": item["region"], "chosen_sum": chosen, "rejected_sum": rejected, "margin_sum": chosen - rejected})
    if was_training:
        model.train()
    regions = {}
    for region in sorted({row["region"] for row in rows}):
        selected = [row for row in rows if row["region"] == region]
        regions[region] = {"n": len(selected), "margin_sum_mean": sum(row["margin_sum"] for row in selected) / len(selected)}
    return {"step": int(step), "regions": regions, "rows": rows}


history = []
probes = []


class Ledger(TrainerCallback):
    def __init__(self, tokenizer, heldout):
        self.tokenizer = tokenizer
        self.heldout = heldout

    def flush(self):
        write_json(PARTIAL, {"status": "running", "trajectory": history, "heldout_probe": probes})

    def on_train_begin(self, args, state, control, model=None, **kwargs):
        probes.append(probe(model, self.tokenizer, self.heldout, 0)); self.flush()

    def on_step_end(self, args, state, control, model=None, **kwargs):
        if state.global_step in {1, 6, 12, 18, 24}:
            probes.append(probe(model, self.tokenizer, self.heldout, state.global_step)); self.flush()
        status("running", step=int(state.global_step), steps=STEPS)

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            history.append({"step": int(state.global_step), **{k: float(v) for k, v in logs.items() if isinstance(v, (int, float))}}); self.flush()


def main():
    status("starting", device=DEVICE)
    if DEVICE != "mps":
        raise RuntimeError("MPS is unavailable; run this on the Mac")
    training, heldout = build_pairs()
    tokenizer = AutoTokenizer.from_pretrained(SFT)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    base = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE)
    model = PeftModel.from_pretrained(base, str(DPO_ADAPTER), is_trainable=True)
    reference_base = AutoModelForCausalLM.from_pretrained(SFT, dtype=torch.float32).to(DEVICE)
    reference = PeftModel.from_pretrained(reference_base, str(DPO_ADAPTER), is_trainable=False).eval()
    config = DPOConfig(
        output_dir=str(RUN_DIR), max_steps=STEPS, per_device_train_batch_size=1,
        gradient_accumulation_steps=4, learning_rate=4e-5, warmup_steps=3,
        beta=0.1, max_length=384, logging_steps=1, logging_first_step=True,
        save_strategy="no", report_to="none", disable_tqdm=True,
        gradient_checkpointing=False, use_cache=False, torch_empty_cache_steps=2,
        dataloader_num_workers=0, seed=0,
    )
    trainer = DPOTrainer(
        model=model, ref_model=reference, args=config,
        train_dataset=Dataset.from_list(training), processing_class=tokenizer,
        callbacks=[Ledger(tokenizer, heldout)],
    )
    trainer.train()
    trainer.save_model(str(ADAPTER))
    result = {
        "status": "measured",
        "claim_scope": (
            "A 24-step targeted safety DPO continuation of the local SmolLM preference "
            "adapter, using 24 authored training pairs and 12 disjoint authored probes."
        ),
        "lineage": {"sft": SFT, "dpo_adapter": str(DPO_ADAPTER), "safety_adapter": str(ADAPTER)},
        "config": {"steps": STEPS, "train_pairs": len(training), "heldout_pairs": len(heldout), "beta": 0.1, "learning_rate": 4e-5},
        "training_pairs": training,
        "heldout_pairs": heldout,
        "trajectory": history,
        "heldout_probe": probes,
    }
    write_json(OUT, result); status("success", output=str(OUT), adapter=str(ADAPTER)); print(f"WROTE {OUT}")


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        status("exception", exception=repr(exc)); raise
