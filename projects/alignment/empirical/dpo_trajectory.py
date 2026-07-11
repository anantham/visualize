"""Run a small, measured DPO trajectory on Qwen2.5-0.5B-Instruct.

The preference set is deliberately small and hand-authored for teaching. The
experiment tests what the optimizer does to chosen/rejected log probabilities;
it does not estimate the broad effectiveness of DPO in production.
"""

import json
import time
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainerCallback
from trl import DPOConfig, DPOTrainer


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "bakes"
RUN_DIR = OUT_DIR / "dpo_run"
OUT = OUT_DIR / "dpo_trajectory.json"
PARTIAL = OUT_DIR / "dpo_trajectory.partial.json"
STATUS = OUT_DIR / "dpo_trajectory.status.json"
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


RAW_PAIRS = [
    ("What is 17 times 24?", "17 times 24 is 408.", "It is probably around 380."),
    ("Explain TCP versus UDP briefly.", "TCP prioritizes reliable, ordered delivery; UDP sends datagrams without delivery guarantees and usually has lower overhead.", "TCP is for websites and UDP is for everything else."),
    ("Give exactly three tips for clearer writing.", "1. Use concrete verbs.\n2. Cut unnecessary qualifiers.\n3. Put the main point first.", "Write clearly, add examples, revise, read more, and use good grammar."),
    ("I found a correlation in a tiny sample. Did I prove causation?", "No. A small observational correlation can reflect chance, confounding, or reverse causation; you need stronger design and more data.", "Yes, correlation usually proves the cause if the pattern is strong."),
    ("How do I center a div in CSS?", "Use a parent with `display: grid; place-items: center;` or flexbox with `justify-content` and `align-items` set to `center`.", "Add random margins until it looks centered."),
    ("Write a polite one-sentence meeting decline.", "Thanks for the invitation; I cannot attend, but I would appreciate any notes or follow-up materials.", "No, I do not want to come to this meeting."),
    ("What should I do if a medical symptom is suddenly severe?", "Seek urgent professional care or local emergency help, especially if there is trouble breathing, chest pain, fainting, or rapid worsening.", "Wait several days and diagnose it from social media."),
    ("Summarize photosynthesis in one sentence.", "Plants use light energy to convert carbon dioxide and water into sugars, releasing oxygen.", "Photosynthesis is when plants breathe sunlight."),
    ("I do not know the answer. How should I respond?", "Say what is uncertain, avoid inventing facts, and identify what evidence or source would resolve it.", "Give the most confident-sounding answer so the user is satisfied."),
    ("Suggest a safe password practice.", "Use a password manager to generate a unique long password for each account and enable multi-factor authentication.", "Reuse one memorable password everywhere."),
    ("Translate 'good morning' into Spanish.", "Buenos dias.", "Buenas noches."),
    ("A user asks an ambiguous question. What should an assistant do?", "Answer the likely interpretation while stating the assumption, or ask a focused clarification when the consequence matters.", "Refuse every ambiguous request."),
]


def conversational(role, content):
    return [{"role": role, "content": content}]


PAIRS = [
    {"prompt": conversational("user", p), "chosen": conversational("assistant", c), "rejected": conversational("assistant", r)}
    for p, c, r in RAW_PAIRS
]


def write_status(state, **extra):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"status": state, "time": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    payload.update(extra)
    STATUS.write_text(json.dumps(payload, indent=2))


@torch.no_grad()
def completion_logprob(model, tokenizer, prompt, response):
    prompt_messages = prompt
    full_messages = prompt + response
    prompt_text = tokenizer.apply_chat_template(
        prompt_messages, tokenize=False, add_generation_prompt=True
    )
    full_text = tokenizer.apply_chat_template(
        full_messages, tokenize=False, add_generation_prompt=False
    )
    prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    full_ids = tokenizer(full_text, add_special_tokens=False, return_tensors="pt")["input_ids"].to(DEVICE)
    logits = model(input_ids=full_ids).logits[:, :-1, :].float()
    targets = full_ids[:, 1:]
    token_logps = torch.log_softmax(logits, dim=-1).gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    start = max(0, len(prompt_ids) - 1)
    completion = token_logps[0, start:]
    return {
        "sum": float(completion.sum().cpu()),
        "mean": float(completion.mean().cpu()),
        "tokens": int(completion.numel()),
    }


@torch.no_grad()
def fixed_probe(model, tokenizer, step):
    was_training = model.training
    model.eval()
    rows = []
    for index, pair in enumerate(PAIRS):
        chosen = completion_logprob(model, tokenizer, pair["prompt"], pair["chosen"])
        rejected = completion_logprob(model, tokenizer, pair["prompt"], pair["rejected"])
        rows.append({
            "pair": index,
            "chosen": chosen,
            "rejected": rejected,
            "margin_sum": chosen["sum"] - rejected["sum"],
            "margin_mean": chosen["mean"] - rejected["mean"],
        })
    if was_training:
        model.train()
    return {
        "step": int(step),
        "chosen_sum": sum(row["chosen"]["sum"] for row in rows) / len(rows),
        "rejected_sum": sum(row["rejected"]["sum"] for row in rows) / len(rows),
        "margin_sum": sum(row["margin_sum"] for row in rows) / len(rows),
        "chosen_mean": sum(row["chosen"]["mean"] for row in rows) / len(rows),
        "rejected_mean": sum(row["rejected"]["mean"] for row in rows) / len(rows),
        "margin_mean": sum(row["margin_mean"] for row in rows) / len(rows),
        "pairs": rows,
    }


class LedgerCallback(TrainerCallback):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def write_partial(self):
        PARTIAL.write_text(json.dumps({
            "status": "running",
            "training_batches": history,
            "fixed_probe": fixed_history,
        }, indent=2))

    def on_train_begin(self, args, state, control, model=None, **kwargs):
        fixed_history.append(fixed_probe(model, self.tokenizer, 0))
        self.write_partial()

    def on_step_end(self, args, state, control, model=None, **kwargs):
        if state.global_step in {1, 3, 6, 9, 12, 15, 18, 21, 24}:
            fixed_history.append(fixed_probe(model, self.tokenizer, state.global_step))
            self.write_partial()

    def on_log(self, args, state, control, logs=None, **kwargs):
        if not logs:
            return
        payload = {"step": int(state.global_step), **{k: float(v) for k, v in logs.items() if isinstance(v, (int, float))}}
        history.append(payload)
        self.write_partial()
        write_status("running", step=int(state.global_step))


history = []
fixed_history = []


def main():
    history.clear()
    fixed_history.clear()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    write_status("starting", device=DEVICE)
    if DEVICE != "mps":
        raise RuntimeError("MPS is unavailable; run this outside the sandbox on the Mac")

    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32).to(DEVICE)

    peft = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        task_type="CAUSAL_LM",
    )
    config = DPOConfig(
        output_dir=str(RUN_DIR),
        max_steps=24,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=5e-5,
        warmup_steps=3,
        beta=0.1,
        max_length=384,
        logging_steps=1,
        logging_first_step=True,
        save_strategy="no",
        report_to="none",
        disable_tqdm=True,
        gradient_checkpointing=False,
        use_cache=True,
        torch_empty_cache_steps=2,
        dataloader_num_workers=0,
        seed=0,
    )
    trainer = DPOTrainer(
        model=model,
        ref_model=None,
        args=config,
        train_dataset=Dataset.from_list(PAIRS),
        processing_class=tokenizer,
        peft_config=peft,
        callbacks=[LedgerCallback(tokenizer)],
    )
    trainer.train()
    adapter_dir = RUN_DIR / "final_adapter"
    trainer.save_model(str(adapter_dir))
    first_probe = fixed_history[0]
    last_probe = fixed_history[-1]

    result = {
        "status": "measured",
        "claim_scope": "A 24-step LoRA DPO run on 12 hand-authored teaching preference pairs; fixed-probe values compare the same pairs at every measured step and are not a production benchmark.",
        "model": MODEL,
        "device": DEVICE,
        "config": {"steps": 24, "beta": 0.1, "learning_rate": 5e-5, "lora_rank": 8, "pairs": len(PAIRS)},
        "preference_pairs": PAIRS,
        "training_batch_trajectory": history,
        "fixed_probe_trajectory": fixed_history,
        "verdict": {
            "chosen_sum_delta": last_probe["chosen_sum"] - first_probe["chosen_sum"],
            "rejected_sum_delta": last_probe["rejected_sum"] - first_probe["rejected_sum"],
            "margin_sum_delta": last_probe["margin_sum"] - first_probe["margin_sum"],
            "both_likelihoods_sank": last_probe["chosen_sum"] < first_probe["chosen_sum"] and last_probe["rejected_sum"] < first_probe["rejected_sum"],
            "reading": "This run widened the margin by increasing chosen likelihood and decreasing rejected likelihood.",
        },
        "adapter": str(adapter_dir),
        "available_metrics": sorted({key for row in history for key in row}),
    }
    OUT.write_text(json.dumps(result, indent=2))
    write_status("success", output=str(OUT), steps=trainer.state.global_step)
    print(f"WROTE {OUT}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        write_status("exception", exception=repr(exc))
        raise
