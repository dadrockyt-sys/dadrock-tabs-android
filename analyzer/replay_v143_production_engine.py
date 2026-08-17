from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from v143_production_engine import V143ProductionEngine


ROOT = Path("/workspaces/dadrock-tabs-android")
ANALYZER = ROOT / "analyzer"
DEV = ROOT / "public" / "training" / "v143-final-multifamily-development"

SOURCE_SCRIPT = ANALYZER / "develop_gomyway_v143_final_multifamily_training_only.py"
MODEL_PATH = DEV / "v143-production-model-candidate-v1.json"


def score_sha256(scores: np.ndarray) -> str:
    return hashlib.sha256(
        np.asarray(scores, dtype="<f8").tobytes()
    ).hexdigest()


# ------------------------------------------------------------------
# Load production scorer.
# ------------------------------------------------------------------

engine = V143ProductionEngine(MODEL_PATH)

model_payload = json.loads(
    MODEL_PATH.read_text(encoding="utf-8")
)

expected_sha = str(
    model_payload["validation"]["serializedScoreSha256"]
)


# ------------------------------------------------------------------
# Reconstruct authoritative V143 feature inputs.
# Stop before the original 320-carrier training sweep.
# ------------------------------------------------------------------

source_text = SOURCE_SCRIPT.read_text(encoding="utf-8")

marker = 'print("=== V143 FINAL MULTI-FAMILY TRAINING-ONLY SWEEP ===")'

if marker not in source_text:
    raise RuntimeError("Safe V143 setup boundary not found")

prefix = source_text.split(marker, 1)[0]

ns = {
    "__name__": "v143_replay_setup_only",
    "__file__": str(SOURCE_SCRIPT),
}

exec(
    compile(prefix, str(SOURCE_SCRIPT), "exec"),
    ns,
    ns,
)

matrices = ns["matrices"]
family_features = ns["family_features"]
family_names = ns["family_names"]

names = [str(x) for x in ns["names"]]
pf = np.asarray(ns["pf"], dtype=np.float64)
interaction_names = [str(x) for x in ns["_phase_names"]]


# ------------------------------------------------------------------
# Reconstruct EXACT winning feature matrix.
# ------------------------------------------------------------------

rep = engine.representation
family = engine.family

matrix = np.concatenate(
    [
        np.asarray(matrices[rep], dtype=np.float64),
        np.asarray(family_features[family], dtype=np.float64),
    ],
    axis=1,
)


# ------------------------------------------------------------------
# Reconstruct feature names independently and verify column ordering.
# ------------------------------------------------------------------

phase_names = [
    f"phase::col{i}"
    for i in range(pf.shape[1])
]

representation_names = {
    "base":
        names,

    "phase_col3":
        names
        + [phase_names[3]],

    "full_phase":
        names
        + phase_names,

    "cosine":
        names
        + [phase_names[1], phase_names[3]],

    "v112_interactions":
        names
        + [phase_names[1], phase_names[3]]
        + interaction_names,
}

expected_feature_names = (
    representation_names[rep]
    + [str(x) for x in family_names[family]]
)

if tuple(expected_feature_names) != engine.feature_names:
    raise RuntimeError(
        "Production feature ordering does not match authoritative V143 schema"
    )

if matrix.shape != (1551, 148):
    raise RuntimeError(
        f"Unexpected replay matrix shape: {matrix.shape}"
    )


# ------------------------------------------------------------------
# Score ONLY through production engine.
# ------------------------------------------------------------------

scores = engine.score_matrix(matrix)

actual_sha = score_sha256(scores)

if actual_sha != expected_sha:
    raise RuntimeError(
        "PRODUCTION ENGINE REPLAY FAILED\n"
        f"expected={expected_sha}\n"
        f"actual={actual_sha}"
    )


print("=== V143 PRODUCTION ENGINE REPLAY PASSED ===")
print("Rows:", matrix.shape[0])
print("Features:", matrix.shape[1])
print("Feature ordering exact: True")
print("Score count:", len(scores))
print("Expected SHA256:", expected_sha)
print("Actual SHA256:  ", actual_sha)
print("SHA match: True")
print("Runtime labels used by scorer: False")
print("Professional reference used by scorer: False")
print("Production deployed: False")
