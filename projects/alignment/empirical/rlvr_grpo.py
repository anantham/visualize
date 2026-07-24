"""Run a small RLVR/GRPO experiment with an exact arithmetic checker.

The verifier can score arithmetic outputs and is deliberately absent for open
advice. This measures a toy checkable island, not broad reasoning or wisdom.
"""

import json
import os
import random
import re
import time
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainerCallback
from trl import GRPOConfig, GRPOTrainer


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "bakes"
RUN_DIR = OUT_DIR / "rlvr_run"
OUT = OUT_DIR / "rlvr_curve.json"
PARTIAL = OUT_DIR / "rlvr_curve.partial.json"
STATUS = OUT_DIR / "rlvr_curve.status.json"
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
MAX_STEPS = int(os.environ.get("RLVR_STEPS", "48"))
CALIBRATE_ONLY = os.environ.get("RLVR_CALIBRATE_ONLY", "0") == "1"


def make_tasks(seed, count, prefix):
    rng = random.Random(seed)
    rows = []
    for index in range(count):
        a = rng.randint(13, 79)
        b = rng.randint(12, 68)
        c = rng.randint(-40, 90)
        numeric_answer = a * b + c
        expression = f"({a} * {b}) + ({c})"
        distractors = [numeric_answer + rng.choice([-a, -b, -10, -1, 1, 10, b, a]) for _ in range(8)]
        distractor_values = []
        for value in distractors:
            if value != numeric_answer and value not in distractor_values:
                distractor_values.append(value)
            if len(distractor_values) == 3:
                break
        while len(distractor_values) < 3:
            candidate = numeric_answer + rng.randint(-30, 30)
            if candidate != numeric_answer and candidate not in distractor_values:
                distractor_values.append(candidate)
        letters = ["A", "B", "C", "D"]
        correct_index = index % len(letters)
        values = list(distractor_values)
        values.insert(correct_index, numeric_answer)
        answer = letters[correct_index]
        options = "  ".join(f"{letter}) {value}" for letter, value in zip(letters, values))
        rows.append({
            "id": f"{prefix}-{index:02d}",
            "prompt": [{"role": "user", "content": f"Compute {expression}. {options} Reply with only A, B, C, or D."}],
            "answer": answer,
            "numeric_answer": numeric_answer,
            "options": dict(zip(letters, values)),
            "expression": expression,
        })
    return rows


TRAIN_TASKS = make_tasks(17, 32, "train")
HELDOUT_TASKS = make_tasks(91, 40, "heldout")


def write_status(state, **extra):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"status": state, "time": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    payload.update(extra)
    STATUS.write_text(json.dumps(payload, indent=2))


def completion_text(completion):
    if isinstance(completion, str):
        return completion
    if isinstance(completion, list) and completion:
        item = completion[-1]
        if isinstance(item, dict):
            return str(item.get("content", ""))
    return str(completion)


def final_choice(text):
    matches = re.findall(r"\b[ABCD]\b", text.upper())
    return matches[-1] if matches else None


def exact_reward(completions, answer, **kwargs):
    return [1.0 if final_choice(completion_text(completion)) == str(target) else 0.0
            for completion, target in zip(completions, answer)]


@torch.no_grad()
def evaluate(model, tokenizer, label):
    was_training = model.training
    model.eval()
    rows = []
    for task_index, task in enumerate(HELDOUT_TASKS):
        rendered = tokenizer.apply_chat_template(task["prompt"], tokenize=False, add_generation_prompt=True)
        enc = tokenizer(rendered, return_tensors="pt", add_special_tokens=False).to(DEVICE)
        samples = []
        for sample_index in range(4):
            seed = 10000 + task_index * 10 + sample_index
            torch.manual_seed(seed)
            output = model.generate(
                **enc,
                max_new_tokens=8,
                do_sample=True,
                temperature=0.9,
                top_p=0.95,
                pad_token_id=tokenizer.pad_token_id,
            )
            text = tokenizer.decode(output[0, enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()
            parsed = final_choice(text)
            samples.append({"seed": seed, "text": text, "parsed": parsed, "correct": parsed == task["answer"]})
        rows.append({**task, "samples": samples})
        write_status("evaluating", phase=label, task=task["id"])
    if was_training:
        model.train()
    total = sum(len(row["samples"]) for row in rows)
    correct = sum(sample["correct"] for row in rows for sample in row["samples"])
    return {
        "label": label,
        "sample_accuracy": correct / total,
        "pass_at_4": sum(any(sample["correct"] for sample in row["samples"]) for row in rows) / len(rows),
        "unique_answers_mean": sum(len(set(sample["parsed"] for sample in row["samples"])) for row in rows) / len(rows),
        "rows": rows,
    }


history = []


class LedgerCallback(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        if not logs:
            return
        row = {"step": int(state.global_step), **{k: float(v) for k, v in logs.items() if isinstance(v, (int, float))}}
        history.append(row)
        PARTIAL.write_text(json.dumps({"status": "running", "trajectory": history}, indent=2))
        write_status("training", step=int(state.global_step))


def main():
    history.clear()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    write_status("starting", device=DEVICE)
    if DEVICE != "mps":
        raise RuntimeError("MPS is unavailable; run this outside the sandbox on the Mac")

    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32).to(DEVICE)
    before = evaluate(model, tokenizer, "before")
    torch.mps.empty_cache()
    if CALIBRATE_ONLY:
        result = {
            "status": "calibration",
            "claim_scope": "Pre-training calibration only; no optimizer steps were run.",
            "model": MODEL,
            "device": DEVICE,
            "heldout": {"before": before},
        }
        OUT.write_text(json.dumps(result, indent=2))
        write_status("calibration_success", output=str(OUT), accuracy=before["sample_accuracy"])
        print(f"WROTE {OUT}", flush=True)
        return

    peft = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        task_type="CAUSAL_LM",
    )
    config = GRPOConfig(
        output_dir=str(RUN_DIR),
        max_steps=MAX_STEPS,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=1,
        learning_rate=5e-5,
        warmup_steps=2,
        num_generations=4,
        generation_batch_size=4,
        max_completion_length=8,
        temperature=0.9,
        top_p=0.95,
        beta=0.0,
        loss_type="grpo",
        logging_steps=1,
        logging_first_step=True,
        log_completions=False,
        save_strategy="no",
        report_to="none",
        disable_tqdm=True,
        gradient_checkpointing=False,
        use_cache=True,
        torch_empty_cache_steps=2,
        dataloader_num_workers=0,
        seed=0,
    )
    trainer = GRPOTrainer(
        model=model,
        reward_funcs=exact_reward,
        args=config,
        train_dataset=Dataset.from_list(TRAIN_TASKS),
        processing_class=tokenizer,
        peft_config=peft,
        callbacks=[LedgerCallback()],
    )
    trainer.train()
    adapter_dir = RUN_DIR / "final_adapter"
    trainer.save_model(str(adapter_dir))
    after = evaluate(trainer.model, tokenizer, "after")

    result = {
        "status": "measured",
        "claim_scope": f"A {MAX_STEPS}-step LoRA GRPO run on 32 position-balanced arithmetic multiple-choice prompts with an exact checker; held-out evaluation uses 40 new position-balanced prompts and paired sampling seeds. This says nothing about uncheckable advice.",
        "model": MODEL,
        "device": DEVICE,
        "config": {"steps": MAX_STEPS, "num_generations": 4, "learning_rate": 5e-5, "lora_rank": 8, "beta": 0.0},
        "checker": "last parsed A/B/C/D choice equals the known arithmetic option",
        "train_tasks": TRAIN_TASKS,
        "heldout": {"before": before, "after": after},
        "trajectory": history,
        "adapter": str(adapter_dir),
        "off_island": {"task": "Give wise career advice under uncertainty.", "verifier": None, "reason": "No exact answer key exists."},
    }
    OUT.write_text(json.dumps(result, indent=2))
    write_status("success", output=str(OUT), before=before["sample_accuracy"], after=after["sample_accuracy"])
    print(f"WROTE {OUT}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        write_status("exception", exception=repr(exc))
        raise
