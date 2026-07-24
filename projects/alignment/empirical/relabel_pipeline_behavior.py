"""Reapply the current coarse classifier to stored behavior generations."""

import json
from pathlib import Path

from pipeline_behavior import classify, summarize


ROOT = Path(__file__).resolve().parent
BAKE = ROOT / "bakes" / "pipeline_behavior.json"


def main():
    data = json.loads(BAKE.read_text())
    for stage in data["stages"].values():
        for row in stage["rows"]:
            for sample in row["samples"]:
                sample["mode_auto"] = classify(sample["text"])
        stage["summary"] = summarize(stage["rows"])
    data["classifier"]["version"] = "coarse-markers-repetition-v2"
    data["classifier"]["human_reviewed"] = False
    BAKE.write_text(json.dumps(data, indent=2))
    print(f"RELABELLED {BAKE}")


if __name__ == "__main__":
    main()
