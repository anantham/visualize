"""Build a fixed, model-independent situation map for the alignment explorable.

The current input is the 214-prompt authored design corpus from the terrain
spike. Prompt positions come from a frozen sentence encoder and a predeclared
UMAP configuration; no aligned-model activation or behavior metric influences
the geography. Stability diagnostics are baked alongside the coordinates.
"""

import hashlib
import json
import os
from pathlib import Path

import numpy as np
from scipy.spatial import procrustes
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.manifold import trustworthiness
from sklearn.metrics import silhouette_score
import umap


ROOT = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get(
    "VALUE_TERRAIN_SOURCE",
    "/Users/aditya/align_experiments/alignment_warp/value_terrain.json",
))
OUT = ROOT / "bakes" / "situation_atlas.json"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
CANONICAL = {"n_neighbors": 20, "min_dist": 0.30, "seed": 0}
VARIANTS = [
    {"n_neighbors": 10, "min_dist": 0.30, "seed": 1},
    {"n_neighbors": 20, "min_dist": 0.30, "seed": 2},
    {"n_neighbors": 30, "min_dist": 0.30, "seed": 3},
    {"n_neighbors": 20, "min_dist": 0.10, "seed": 4},
    {"n_neighbors": 20, "min_dist": 0.50, "seed": 5},
]

# Human-readable policy coordinates. The x-axis describes this project's
# authored target treatment, not an objective moral property of the prompt.
ANCHORS = {
    "neutral_help": (-0.88, -0.10),
    "scary_benign": (-0.82, -0.58),
    "dual_use": (0.00, -0.58),
    "harmful_clear": (0.86, -0.58),
    "sensitive_ok": (-0.42, 0.38),
    "values_advice": (-0.05, 0.78),
    "sycophancy_bait": (0.55, 0.78),
}


def project(embeddings, config):
    return umap.UMAP(
        n_neighbors=config["n_neighbors"],
        min_dist=config["min_dist"],
        metric="cosine",
        random_state=config["seed"],
    ).fit_transform(embeddings)


def knn_indices(values, k=10):
    values = np.asarray(values, dtype=np.float64)
    norm = np.linalg.norm(values, axis=1, keepdims=True)
    unit = values / np.maximum(norm, 1e-12)
    similarity = unit @ unit.T
    np.fill_diagonal(similarity, -np.inf)
    return np.argpartition(-similarity, kth=k - 1, axis=1)[:, :k]


def neighbor_overlap(a, b):
    return float(np.mean([
        len(set(left).intersection(right)) / len(left)
        for left, right in zip(a, b)
    ]))


def normalize_xy(xy):
    xy = np.asarray(xy, dtype=np.float64)
    center = np.median(xy, axis=0)
    span = np.quantile(np.abs(xy - center), 0.95, axis=0)
    return np.clip((xy - center) / np.maximum(span, 1e-9), -1.2, 1.2)


def policy_lattice(embeddings, labels):
    """Place declared regions at transparent anchors; use local PCA for texture."""
    xy = np.zeros((len(labels), 2), dtype=np.float64)
    labels = np.asarray(labels)
    for region, anchor in ANCHORS.items():
        mask = labels == region
        local = PCA(n_components=2, svd_solver="full").fit_transform(embeddings[mask])
        # PCA signs are arbitrary. Orient each component deterministically.
        for component in range(2):
            farthest = np.argmax(np.abs(local[:, component]))
            if local[farthest, component] < 0:
                local[:, component] *= -1
        scale = np.quantile(np.abs(local), 0.95, axis=0)
        local = np.clip(local / np.maximum(scale, 1e-9), -1, 1) * 0.13
        xy[mask] = np.asarray(anchor) + local
    return xy


def main():
    source = json.loads(SOURCE.read_text())
    rows = source["points"]
    prompts = [row["prompt"] for row in rows]
    labels = [row["region"] for row in rows]

    encoder = SentenceTransformer(ENCODER, device="cpu")
    embeddings = encoder.encode(
        prompts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    # UMAP is evaluated as a candidate and retained only as a diagnostic. The
    # canonical positions use the stable, declared lattice below.
    canonical_raw = project(embeddings, CANONICAL)
    canonical = policy_lattice(embeddings, labels)

    high_knn = knn_indices(embeddings)
    canonical_knn = knn_indices(canonical_raw)
    variants = []
    for config in VARIANTS:
        xy = project(embeddings, config)
        _, _, disparity = procrustes(canonical_raw, xy)
        variants.append({
            **config,
            "neighbor_overlap_with_canonical_k10": neighbor_overlap(
                canonical_knn, knn_indices(xy)
            ),
            "procrustes_disparity": float(disparity),
            "trustworthiness_k10": float(trustworthiness(
                embeddings, xy, n_neighbors=10, metric="cosine"
            )),
        })

    points = []
    for index, (row, xy) in enumerate(zip(rows, canonical)):
        prompt = row["prompt"]
        stable_id = hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:12]
        points.append({
            "id": stable_id,
            "prompt": prompt,
            "region": row["region"],
            "source": "authored_design_spike",
            "split": "design",
            "x": round(float(xy[0]), 5),
            "y": round(float(xy[1]), 5),
            "position_method": "authored-policy-lattice-v1",
            "source_index": index,
        })

    result = {
        "status": "measured_layout",
        "production_ready": False,
        "claim_scope": (
            "A model-independent layout of 214 authored design prompts. It is a "
            "visual substrate and stability test, not a natural held-out benchmark."
        ),
        "source_artifact": str(SOURCE),
        "encoder": ENCODER,
        "canonical_projection": {
            "method": "authored-policy-lattice-v1",
            "x_axis": "authored target: answer (-1) to refuse (+1)",
            "y_axis": "interaction: task/information (-1) to judgment/advice (+1)",
            "anchors": {key: list(value) for key, value in ANCHORS.items()},
            "within_region": "MiniLM embedding -> deterministic local PCA, radius 0.13",
            "disclosure": (
                "Region anchors are editorial policy categories supplied by the project, "
                "not categories discovered by the model or an objective moral ordering."
            ),
        },
        "diagnostics": {
            "n": len(points),
            "regions": sorted(set(labels)),
            "region_silhouette_high_dim_cosine": float(silhouette_score(
                embeddings, labels, metric="cosine"
            )),
            "rejected_global_umap": {
                "config": CANONICAL,
                "trustworthiness_k10": float(trustworthiness(
                    embeddings, canonical_raw, n_neighbors=10, metric="cosine"
                )),
                "high_to_map_neighbor_overlap_k10": neighbor_overlap(
                    high_knn, canonical_knn
                ),
                "variants": variants,
                "reason_rejected": (
                    "Exact k=10 neighborhoods changed too much across reasonable "
                    "seeds and hyperparameters to present as semantic geography."
                ),
            },
        },
        "points": points,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result["diagnostics"], indent=2))
    print(f"WROTE {OUT}")


if __name__ == "__main__":
    main()
