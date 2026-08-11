from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ABS_PATH = PUBLIC / "gomyway-3676-patch-ridge-recurrent-feature-gate-nested-cv-v1.json"
RANK_PATH = PUBLIC / "gomyway-3676-patch-ridge-relative-rank-calibration-nested-cv-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-ridge-calibration-selector-learnability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-ridge-calibration-selector-learnability-v1-manifest.json"
EXPECTED = (272, 595, 341)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing input: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def schemes(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        "normal": list(payload.get("normalCv") or []),
        "section": list(payload.get("sectionCv") or []),
        "shiftedWindow": list(payload.get("shiftedWindowCv") or []),
    }


def chosen_metrics(row: dict[str, Any]) -> tuple[float, float, float, float, float]:
    chosen = row.get("chosen") or {}
    inner_pass = float(chosen.get("innerPassCount") or 0.0)
    inner_folds = float(chosen.get("innerFoldCount") or 1.0)
    pass_rate = inner_pass / max(1.0, inner_folds)
    mean_lift = float(chosen.get("meanLift") or 0.0)
    true_total = float(chosen.get("innerTrue") or 0.0)
    false_total = float(chosen.get("innerFalse") or 0.0)
    balance = (true_total - false_total) / max(1.0, true_total + false_total)
    feature_count = float(chosen.get("featureCount") or len(row.get("featureGate") or []))
    q = float(row.get("tailQuantile") or chosen.get("tailQuantile") or 0.0)
    return pass_rate, mean_lift, balance, feature_count, q


def feature_vector(abs_row: dict[str, Any], rank_row: dict[str, Any]) -> np.ndarray:
    a = chosen_metrics(abs_row)
    r = chosen_metrics(rank_row)
    # Only training-derived quantities are permitted here. No held-out precision/lift/pass.
    return np.asarray([
        r[0] - a[0],
        r[1] - a[1],
        r[2] - a[2],
        r[3] - a[3],
        r[4] - a[4],
        a[0], r[0],
        a[1], r[1],
        a[3], r[3],
        a[4], r[4],
    ], dtype=np.float64)


def winner_label(abs_row: dict[str, Any], rank_row: dict[str, Any]) -> int:
    a = float(abs_row.get("heldoutPrecisionLift") or 0.0)
    r = float(rank_row.get("heldoutPrecisionLift") or 0.0)
    return 1 if r > a else 0


def standardize(train_x: np.ndarray, test_x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = np.mean(train_x, axis=0)
    scale = np.std(train_x, axis=0)
    scale = np.where(scale < 1e-8, 1.0, scale)
    return (train_x - mean) / scale, (test_x - mean) / scale


def centroid_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> int:
    zx, zt = standardize(train_x, test_x)
    if not np.any(train_y == 0) or not np.any(train_y == 1):
        return int(np.mean(train_y) >= 0.5)
    c0 = np.mean(zx[train_y == 0], axis=0)
    c1 = np.mean(zx[train_y == 1], axis=0)
    d0 = float(np.sum((zt - c0) ** 2))
    d1 = float(np.sum((zt - c1) ** 2))
    return 1 if d1 < d0 else 0


def main() -> None:
    abs_payload = load(ABS_PATH)
    rank_payload = load(RANK_PATH)
    if tuple(abs_payload.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Absolute strategy input not anchored to frozen champion")
    if tuple(rank_payload.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Rank strategy input not anchored to frozen champion")

    abs_schemes = schemes(abs_payload)
    rank_schemes = schemes(rank_payload)
    samples: list[dict[str, Any]] = []
    for scheme in ("normal", "section", "shiftedWindow"):
        aa = abs_schemes[scheme]
        rr = rank_schemes[scheme]
        if len(aa) != len(rr):
            raise RuntimeError(f"Fold count mismatch for {scheme}")
        for i, (a, r) in enumerate(zip(aa, rr)):
            samples.append({
                "scheme": scheme,
                "fold": i,
                "x": feature_vector(a, r),
                "y": winner_label(a, r),
                "absoluteHeldoutLift": float(a.get("heldoutPrecisionLift") or 0.0),
                "rankHeldoutLift": float(r.get("heldoutPrecisionLift") or 0.0),
            })

    x = np.vstack([s["x"] for s in samples])
    y = np.asarray([s["y"] for s in samples], dtype=np.int8)
    results: list[dict[str, Any]] = []
    correct = 0
    scheme_stats: dict[str, dict[str, int]] = {}
    for i, s in enumerate(samples):
        train = np.arange(len(samples)) != i
        pred = centroid_predict(x[train], y[train], x[i:i+1])
        ok = pred == int(y[i])
        correct += int(ok)
        st = scheme_stats.setdefault(str(s["scheme"]), {"correct": 0, "total": 0})
        st["correct"] += int(ok)
        st["total"] += 1
        row = {
            "scheme": s["scheme"],
            "fold": s["fold"],
            "predictedStrategy": "relativeRank" if pred else "absoluteThreshold",
            "actualWinner": "relativeRank" if int(y[i]) else "absoluteThreshold",
            "correct": ok,
            "absoluteHeldoutLift": round(float(s["absoluteHeldoutLift"]), 2),
            "rankHeldoutLift": round(float(s["rankHeldoutLift"]), 2),
        }
        results.append(row)
        print("SELECTOR", row)

    accuracy = 100.0 * correct / len(samples) if samples else 0.0
    for scheme, st in scheme_stats.items():
        st["accuracyPct"] = round(100.0 * st["correct"] / st["total"], 2) if st["total"] else 0.0

    # Exploratory gate only: 80% leave-one-fold-out accuracy and at least 60% in every scheme.
    learnable = accuracy >= 80.0 and all(float(st["accuracyPct"]) >= 60.0 for st in scheme_stats.values())

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-ridge-calibration-selector-learnability-diagnostic",
        "baselineMatchedMissingExtra": list(EXPECTED),
        "samples": len(samples),
        "leaveOneFoldOutAccuracyPct": round(accuracy, 2),
        "schemeStats": scheme_stats,
        "selectorLearnable": learnable,
        "results": results,
        "selectorFeaturePolicy": "training-derived inner-CV metadata only; held-out metrics used only to define/evaluate winner labels",
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "selectorLearnable": learnable,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
        "absoluteInputSha256": sha256(ABS_PATH),
        "rankInputSha256": sha256(RANK_PATH),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH RIDGE CALIBRATION SELECTOR LEARNABILITY V1 COMPLETE")
    print("Leave-one-fold-out accuracy:", round(accuracy, 2))
    print("Scheme stats:", scheme_stats)
    print("Calibration selector learnable:", learnable)
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
