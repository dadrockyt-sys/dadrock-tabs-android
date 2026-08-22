from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_MODEL_PATH = (
    ROOT
    / "public"
    / "training"
    / "v143-final-multifamily-development"
    / "v143-production-model-candidate-v1.json"
)


class V143ProductionEngine:
    def __init__(self, model_path: Path | str = DEFAULT_MODEL_PATH):
        self.model_path = Path(model_path)

        payload = json.loads(
            self.model_path.read_text(encoding="utf-8")
        )

        if int(payload.get("schemaVersion", -1)) != 14305:
            raise RuntimeError("Unexpected V143 production model schema")

        if payload.get("status") != "candidate-not-promoted":
            raise RuntimeError(
                f"Unexpected model status: {payload.get('status')}"
            )

        runtime = payload.get("runtime") or {}

        if runtime.get("referenceFree") is not True:
            raise RuntimeError("V143 model is not marked reference-free")

        training = payload.get("training") or {}

        if training.get("runtimeLabelsRequired") is not False:
            raise RuntimeError("V143 runtime unexpectedly requires labels")

        config = payload["configuration"]
        schema = payload["featureSchema"]
        ranker = payload["ranker"]

        self.pair_radius = int(config["pairRadius"])
        self.lambda_value = float(config["lambda"])
        self.q = float(config["q"])
        self.representation = str(config["representation"])
        self.family = str(config["family"])

        self.feature_names = tuple(
            str(name)
            for name in schema["featureNames"]
        )

        self.mean = np.asarray(
            ranker["mean"],
            dtype=np.float64,
        )

        self.scale = np.asarray(
            ranker["scale"],
            dtype=np.float64,
        )

        self.coef = np.asarray(
            ranker["coef"],
            dtype=np.float64,
        )

        expected = int(schema["totalFeatureCount"])

        if expected != len(self.feature_names):
            raise RuntimeError(
                "Feature-name count does not match model schema"
            )

        if not (
            self.mean.shape
            == self.scale.shape
            == self.coef.shape
            == (expected,)
        ):
            raise RuntimeError(
                "V143 ranker dimensions do not match feature schema"
            )

        if not (
            np.isfinite(self.mean).all()
            and np.isfinite(self.scale).all()
            and np.isfinite(self.coef).all()
        ):
            raise RuntimeError("V143 model contains non-finite values")

        if np.any(self.scale == 0.0):
            raise RuntimeError("V143 model contains zero scale values")

        validation = payload.get("validation") or {}

        if validation.get("exactSerializationReplayPassed") is not True:
            raise RuntimeError(
                "V143 candidate has not passed serialization replay"
            )

        self.expected_replay_sha256 = str(
            validation["serializedScoreSha256"]
        )

    @property
    def feature_count(self) -> int:
        return len(self.feature_names)

    def score_matrix(
        self,
        features: np.ndarray | Sequence[Sequence[float]],
    ) -> np.ndarray:
        x = np.asarray(features, dtype=np.float64)

        if x.ndim == 1:
            x = x.reshape(1, -1)

        if x.ndim != 2:
            raise ValueError(
                f"Expected 2-D feature matrix, got shape {x.shape}"
            )

        if x.shape[1] != self.feature_count:
            raise ValueError(
                f"Expected {self.feature_count} features, "
                f"got {x.shape[1]}"
            )

        if not np.isfinite(x).all():
            raise ValueError("Feature matrix contains non-finite values")

        return (
            (x - self.mean)
            / self.scale
        ) @ self.coef

    def score_row(
        self,
        features: Sequence[float],
    ) -> float:
        return float(self.score_matrix(features)[0])

    def describe(self) -> dict:
        return {
            "pairRadius": self.pair_radius,
            "lambda": self.lambda_value,
            "q": self.q,
            "representation": self.representation,
            "family": self.family,
            "featureCount": self.feature_count,
            "referenceFree": True,
        }


if __name__ == "__main__":
    engine = V143ProductionEngine()

    print("V143 PRODUCTION ENGINE LOADED")
    print(json.dumps(engine.describe(), indent=2))
