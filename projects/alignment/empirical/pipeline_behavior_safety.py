"""Append the safety-adapter generation stage to pipeline_behavior.json."""

import json
from pathlib import Path

import torch
from transformers import AutoTokenizer

from pipeline_behavior import (
    ROOT, OUT, STATUS, TOKENIZER, DEVICE, generate_point, load_stage,
    partial_payload, summarize, write_json, write_status,
)


SAFETY_ADAPTER = ROOT / "pipeline_runs" / "smollm_safety" / "final_adapter"


def main():
    if DEVICE != "mps":
        raise RuntimeError("MPS is unavailable; run this on the Mac")
    data = json.loads(OUT.read_text())
    points = data["points"]
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    stage = {"id": "safety", "checkpoint": "/Users/aditya/align_sft/ckpts/final", "adapter": str(SAFETY_ADAPTER)}
    model = load_stage(stage)
    rows = []
    for index, point in enumerate(points):
        rows.append({"id": point["id"], "region": point["region"], "samples": generate_point(model, tokenizer, point, index)})
        write_status("running_safety_behavior", point=index + 1, total=len(points))
    data["stages"]["safety"] = {"rows": rows, "summary": summarize(rows)}
    data["lineage"]["safety_adapter"] = str(SAFETY_ADAPTER)
    write_json(OUT, data)
    write_status("success", output=str(OUT), prompts=len(points), stages=list(data["stages"]))
    print(f"UPDATED {OUT}")


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        write_status("exception", exception=repr(exc)); raise
