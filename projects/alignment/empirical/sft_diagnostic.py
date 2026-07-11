"""Repo-local SFT diagnostic runner.

This reproduces the failed SmolLM2 SFT run shape while writing all outputs under
the visualize repo. It adds explicit status files, MPS memory breadcrumbs,
token-length stats, earlier checkpoints, and callback logs so a crash has a
receipt.

Env knobs:
  N_EXAMPLES=4000 MAX_STEPS=35 SAVE_STEPS=5 SAVE_TOTAL_LIMIT=1
  BATCH=4 GRAD_ACCUM=2 MAX_LENGTH=1024 EMPTY_CACHE_STEPS=5
"""

import atexit
import itertools
import json
import os
import platform
import signal
import sys
import time
import traceback
from pathlib import Path

import torch
from datasets import Dataset, load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainerCallback
from trl import SFTConfig, SFTTrainer


BASE = "HuggingFaceTB/SmolLM2-360M"
TOK_SRC = "HuggingFaceTB/SmolLM2-360M-Instruct"

ROOT = Path(__file__).resolve().parent
RUN_ROOT = ROOT / "sft_diag_runs"
RUN_ID = time.strftime("%Y%m%d-%H%M%S")
OUT = RUN_ROOT / RUN_ID
CKPT = OUT / "ckpts"
LOG_PATH = OUT / "run.log"
STATUS_PATH = OUT / "status.json"

N_EXAMPLES = int(os.environ.get("N_EXAMPLES", "4000"))
MAX_STEPS = int(os.environ.get("MAX_STEPS", "35"))
SAVE_STEPS = int(os.environ.get("SAVE_STEPS", "5"))
SAVE_TOTAL_LIMIT = int(os.environ.get("SAVE_TOTAL_LIMIT", "1"))
BATCH = int(os.environ.get("BATCH", "4"))
GRAD_ACCUM = int(os.environ.get("GRAD_ACCUM", "2"))
MAX_LENGTH = int(os.environ.get("MAX_LENGTH", "1024"))
EMPTY_CACHE_STEPS = int(os.environ.get("EMPTY_CACHE_STEPS", "5"))

START = time.time()
LAST_STATUS = {"status": "starting", "run_id": RUN_ID}


def log(msg):
    text = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(text, flush=True)
    with LOG_PATH.open("a") as f:
        f.write(text + "\n")


def mps_stats():
    if not torch.backends.mps.is_available():
        return {"available": False}
    return {
        "available": True,
        "current_allocated": int(torch.mps.current_allocated_memory()),
        "driver_allocated": int(torch.mps.driver_allocated_memory()),
        "recommended_max": int(torch.mps.recommended_max_memory()),
    }


def write_status(status, **extra):
    LAST_STATUS.clear()
    LAST_STATUS.update({
        "status": status,
        "run_id": RUN_ID,
        "elapsed_s": round(time.time() - START, 1),
        "mps": mps_stats(),
    })
    LAST_STATUS.update(extra)
    with STATUS_PATH.open("w") as f:
        json.dump(LAST_STATUS, f, indent=2)


def on_exit():
    if LAST_STATUS.get("status") not in {"success", "exception", "signal"}:
        write_status("process_exit_without_success_marker")


def on_signal(signum, _frame):
    write_status("signal", signal=signum)
    log(f"received signal {signum}; exiting")
    raise SystemExit(128 + signum)


class DiagCallback(TrainerCallback):
    def __init__(self):
        self.last = time.time()

    def on_train_begin(self, args, state, control, **kwargs):
        log(f"train_begin max_steps={args.max_steps} device={args.device}")
        log(f"mps train_begin {json.dumps(mps_stats())}")

    def on_step_begin(self, args, state, control, **kwargs):
        if state.global_step < 35:
            log(f"step_begin next={state.global_step + 1} mps={json.dumps(mps_stats())}")

    def on_step_end(self, args, state, control, **kwargs):
        now = time.time()
        log(f"step_end step={state.global_step} dt={now - self.last:.2f}s mps={json.dumps(mps_stats())}")
        self.last = now
        write_status("running", step=int(state.global_step))
        if EMPTY_CACHE_STEPS and state.global_step % EMPTY_CACHE_STEPS == 0:
            torch.mps.empty_cache()
            log(f"mps_cache_emptied step={state.global_step} mps={json.dumps(mps_stats())}")

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            log(f"trainer_log step={state.global_step} {json.dumps(logs, sort_keys=True)}")

    def on_save(self, args, state, control, **kwargs):
        log(f"checkpoint_saved step={state.global_step} output_dir={args.output_dir}")

    def on_train_end(self, args, state, control, **kwargs):
        log(f"train_end step={state.global_step} mps={json.dumps(mps_stats())}")


def percentile(vals, p):
    if not vals:
        return None
    vals = sorted(vals)
    idx = min(len(vals) - 1, max(0, round((len(vals) - 1) * p)))
    return vals[idx]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    CKPT.mkdir(parents=True, exist_ok=True)
    atexit.register(on_exit)
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)

    meta = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": torch.__version__,
        "mps_built": torch.backends.mps.is_built(),
        "mps_available": torch.backends.mps.is_available(),
        "env": {k: os.environ.get(k) for k in [
            "PYTORCH_MPS_HIGH_WATERMARK_RATIO",
            "PYTORCH_ENABLE_MPS_FALLBACK",
            "N_EXAMPLES",
            "MAX_STEPS",
            "SAVE_STEPS",
            "SAVE_TOTAL_LIMIT",
            "BATCH",
            "GRAD_ACCUM",
            "MAX_LENGTH",
            "EMPTY_CACHE_STEPS",
        ]},
        "params": {
            "base": BASE,
            "tokenizer": TOK_SRC,
            "n_examples": N_EXAMPLES,
            "max_steps": MAX_STEPS,
            "save_steps": SAVE_STEPS,
            "save_total_limit": SAVE_TOTAL_LIMIT,
            "batch": BATCH,
            "grad_accum": GRAD_ACCUM,
            "max_length": MAX_LENGTH,
            "empty_cache_steps": EMPTY_CACHE_STEPS,
        },
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2))
    write_status("starting", meta=meta)
    log(f"run_dir={OUT}")
    log(f"meta={json.dumps(meta, sort_keys=True)}")

    if not torch.backends.mps.is_available():
        raise RuntimeError("MPS is not available; run this outside the sandbox or on a machine with MPS")

    log(f"loading tokenizer {TOK_SRC}")
    tok = AutoTokenizer.from_pretrained(TOK_SRC)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    log(f"streaming {N_EXAMPLES} smoltalk examples")
    stream = load_dataset("HuggingFaceTB/smoltalk", "all", split="train", streaming=True)
    rows = list(itertools.islice(stream, N_EXAMPLES))
    ds = Dataset.from_list([{"messages": r["messages"]} for r in rows])
    log(f"dataset size={len(ds)} roles={[m['role'] for m in ds[0]['messages']]}")

    lengths = []
    for row in ds:
        text = tok.apply_chat_template(row["messages"], tokenize=False, add_generation_prompt=False)
        lengths.append(len(tok(text, add_special_tokens=False)["input_ids"]))
    length_stats = {
        "min": min(lengths),
        "median": percentile(lengths, 0.5),
        "p95": percentile(lengths, 0.95),
        "p99": percentile(lengths, 0.99),
        "max": max(lengths),
        "gt_max_length": sum(x > MAX_LENGTH for x in lengths),
        "gt_model_context": sum(x > 8192 for x in lengths),
    }
    (OUT / "length_stats.json").write_text(json.dumps(length_stats, indent=2))
    log(f"length_stats={json.dumps(length_stats, sort_keys=True)}")

    log(f"loading BASE model {BASE}")
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.float32)

    cfg = SFTConfig(
        output_dir=str(CKPT),
        max_steps=MAX_STEPS,
        per_device_train_batch_size=BATCH,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=2e-5,
        warmup_steps=min(10, MAX_STEPS),
        logging_steps=1,
        save_strategy="steps",
        save_steps=SAVE_STEPS,
        save_total_limit=SAVE_TOTAL_LIMIT,
        max_length=MAX_LENGTH,
        packing=False,
        report_to="none",
        dataloader_num_workers=0,
        bf16=False,
        fp16=False,
        gradient_checkpointing=False,
        seed=0,
        disable_tqdm=True,
    )

    trainer = SFTTrainer(
        model=model,
        args=cfg,
        train_dataset=ds,
        processing_class=tok,
        callbacks=[DiagCallback()],
    )
    log(f"trainer device={trainer.args.device}")
    write_status("training_started")
    trainer.train()
    final_dir = OUT / "final"
    trainer.save_model(str(final_dir))
    log(f"DONE final_dir={final_dir}")
    write_status("success", final_dir=str(final_dir))


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        OUT.mkdir(parents=True, exist_ok=True)
        tb = traceback.format_exc()
        log("EXCEPTION " + repr(exc))
        with (OUT / "traceback.txt").open("w") as f:
            f.write(tb)
        write_status("exception", exception=repr(exc), traceback=tb)
        raise
