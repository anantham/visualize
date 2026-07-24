"""Embed measured JSON artifacts into the self-contained alignment page."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
BAKES = ROOT / "empirical" / "bakes"
SOURCES = {
    "atlas": BAKES / "situation_atlas.json",
    "behavior": BAKES / "pipeline_behavior.json",
    "dpo": BAKES / "pipeline_dpo.json",
    "refusal": BAKES / "pipeline_refusal.json",
    "rlvr": BAKES / "rlvr_curve_12step_unbalanced.json",
    "residual": Path("/Users/aditya/align_experiments/alignment_warp/residual_layout.json"),
}
FALLBACKS = {
    "behavior": BAKES / "pipeline_behavior.partial.json",
    "refusal": BAKES / "pipeline_refusal.partial.json",
}


def main():
    data = {}
    missing = []
    for key, path in SOURCES.items():
        if path.exists():
            data[key] = json.loads(path.read_text())
        elif key in FALLBACKS and FALLBACKS[key].exists():
            data[key] = json.loads(FALLBACKS[key].read_text())
            data[key]["embedded_from_partial"] = True
        else:
            data[key] = None
            missing.append(key)
    text = INDEX.read_text()
    compact = json.dumps(data, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")
    replacement = f"/*__DATA_START__*/{compact}/*__DATA_END__*/"
    replaced, count = re.subn(
        r"/\*__DATA_START__\*/.*?/\*__DATA_END__\*/",
        lambda _match: replacement,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("data markers missing or duplicated")
    INDEX.write_text(replaced)
    print(f"embedded {', '.join(key for key in SOURCES if key not in missing)}")
    if missing:
        print(f"pending: {', '.join(missing)}")


if __name__ == "__main__":
    main()
