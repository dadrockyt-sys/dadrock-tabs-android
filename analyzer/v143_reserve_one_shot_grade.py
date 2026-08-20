#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"

REFERENCE_PATH = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
FREEZE_MANIFEST_PATH = CAL / "contextual-prune-freeze-manifest.json"
PREDICTION_MANIFEST_PATH = CAL / "reserve-97-113-contextual-prune-prediction-manifest.json"
BASE_PATH = CAL / "reserve-97-113-base027-frozen-events.json"
CANDIDATE_PATH = CAL / "reserve-97-113-contextual-prune-frozen-events.json"
REPORT_PATH = CAL / "reserve-97-113-contextual-prune-one-shot-grade.json"

TARGET_MEASURES = set(range(97, 114))


def load_json(path: Path) -> Any:
    if not path.exists() or path.stat().st_size <= 0:
        raise RuntimeError(f"Missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_prediction_events(payload: Any) -> set[tuple[int, int]]:
    found: set[tuple[int, int]] = set()
    events = payload.get("events", []) if isinstance(payload, dict) else []
    for event in events:
        if not isinstance(event, dict):
            continue
        measure = int(event.get("measure", 0))
        step = int(event.get("quantizedStep", event.get("step", -1)))
        if measure in TARGET_MEASURES and 0 <= step < 16:
            found.add((measure, step))
    return found


def extract_reference_events(payload: Any) -> set[tuple[int, int]]:
    if not isinstance(payload, dict):
        raise RuntimeError("Professional reference root is not an object")
    found: set[tuple[int, int]] = set()
    seen_measures: set[int] = set()
    for measure_payload in payload.get("measures", []) or []:
        if not isinstance(measure_payload, dict):
            continue
        measure = int(measure_payload.get("measureNumber", 0))
        if measure not in TARGET_MEASURES:
            continue
        seen_measures.add(measure)
        for event in measure_payload.get("events", []) or []:
            if not isinstance(event, dict):
                continue
            step = int(event.get("quantizedStep", -1))
            if not 0 <= step < 16:
                raise RuntimeError(f"Reference event has invalid step: measure={measure} step={step}")
            found.add((measure, step))
    if seen_measures != TARGET_MEASURES:
        missing = sorted(TARGET_MEASURES - seen_measures)
        raise RuntimeError(f"Reserve reference missing measures: {missing}")
    if not found:
        raise RuntimeError("Reserve reference contains zero events")
    return found


def metrics(pred: set[tuple[int, int]], ref: set[tuple[int, int]]) -> dict[str, Any]:
    tp = len(pred & ref)
    fp = len(pred - ref)
    fn = len(ref - pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "predicted": len(pred),
        "reference": len(ref),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def rounded(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, dict):
        return {key: rounded(val) for key, val in value.items()}
    if isinstance(value, list):
        return [rounded(val) for val in value]
    return value


def main() -> None:
    freeze_manifest = load_json(FREEZE_MANIFEST_PATH)
    prediction_manifest = load_json(PREDICTION_MANIFEST_PATH)
    base_payload = load_json(BASE_PATH)
    candidate_payload = load_json(CANDIDATE_PATH)

    if freeze_manifest.get("predictionsFrozenBeforeReserveGrading") is not True:
        raise RuntimeError("Development freeze is not sealed before reserve grading")
    for key in ("targetReserveReferenceOpened", "measures97To113Opened", "reservePayloadOpened"):
        if freeze_manifest.get(key) is not False:
            raise RuntimeError(f"Pre-grade freeze invariant changed: {key}={freeze_manifest.get(key)!r}")
    if freeze_manifest.get("productionModified") is not False:
        raise RuntimeError("Development freeze marks productionModified=true")

    invariants = prediction_manifest.get("invariants", {})
    required_true = (
        "developmentPredictionsFrozenBeforeReserveGrading",
        "section5BaseReplayMatchedHistoricalFreeze",
        "reserveCacheReferenceFree",
    )
    for key in required_true:
        if invariants.get(key) is not True:
            raise RuntimeError(f"Prediction manifest invariant changed: {key}={invariants.get(key)!r}")
    required_false = (
        "professionalReferenceUsedForPrediction",
        "targetReserveReferenceOpened",
        "reservePayloadOpened",
        "candidateAddsEvents",
        "candidateRelocatesEvents",
        "productionModified",
    )
    for key in required_false:
        if invariants.get(key) is not False:
            raise RuntimeError(f"Prediction manifest invariant changed: {key}={invariants.get(key)!r}")

    fingerprints = prediction_manifest.get("fingerprints", {})
    actual_base_sha = sha256(BASE_PATH)
    actual_candidate_sha = sha256(CANDIDATE_PATH)
    if actual_base_sha != fingerprints.get("frozenBaseReserveEventsSha256"):
        raise RuntimeError("Frozen reserve base fingerprint mismatch")
    if actual_candidate_sha != fingerprints.get("frozenContextualReserveEventsSha256"):
        raise RuntimeError("Frozen reserve candidate fingerprint mismatch")

    base = extract_prediction_events(base_payload)
    candidate = extract_prediction_events(candidate_payload)
    if len(base) != int(prediction_manifest.get("counts", {}).get("reserveBaseEvents", -1)):
        raise RuntimeError("Frozen reserve base event count mismatch")
    if len(candidate) != int(prediction_manifest.get("counts", {}).get("reserveContextualEvents", -1)):
        raise RuntimeError("Frozen reserve candidate event count mismatch")
    if not candidate.issubset(base):
        raise RuntimeError("Frozen reserve candidate is not a subset of frozen base")

    # ONE-SHOT OPEN: predictions and pass/fail rule are already frozen above.
    reference_payload = load_json(REFERENCE_PATH)
    reference = extract_reference_events(reference_payload)

    base_metrics = metrics(base, reference)
    candidate_metrics = metrics(candidate, reference)
    delta = {
        "predicted": candidate_metrics["predicted"] - base_metrics["predicted"],
        "tp": candidate_metrics["tp"] - base_metrics["tp"],
        "fp": candidate_metrics["fp"] - base_metrics["fp"],
        "fn": candidate_metrics["fn"] - base_metrics["fn"],
        "precision": candidate_metrics["precision"] - base_metrics["precision"],
        "recall": candidate_metrics["recall"] - base_metrics["recall"],
        "f1": candidate_metrics["f1"] - base_metrics["f1"],
    }

    removed = base - candidate
    removed_tp = len(removed & reference)
    removed_fp = len(removed - reference)

    per_measure = []
    for measure in sorted(TARGET_MEASURES):
        mset = {(m, s) for m, s in reference if m == measure}
        bset = {(m, s) for m, s in base if m == measure}
        cset = {(m, s) for m, s in candidate if m == measure}
        per_measure.append(
            {
                "measure": measure,
                "base": metrics(bset, mset),
                "candidate": metrics(cset, mset),
                "f1Delta": metrics(cset, mset)["f1"] - metrics(bset, mset)["f1"],
            }
        )

    # Predeclared reserve gate, frozen before the reference is opened:
    # 1) all prediction fingerprints/invariants above must match,
    # 2) candidate must remain a subset of base,
    # 3) precision must improve,
    # 4) F1 must improve.
    precision_positive = delta["precision"] > 0.0
    f1_positive = delta["f1"] > 0.0
    gate_passed = precision_positive and f1_positive and candidate.issubset(base)

    report = rounded(
        {
            "schemaVersion": 1,
            "grade": "v143-contextual-prune-reserve-one-shot",
            "reserveMeasures": "97-113",
            "predeclaredGate": {
                "candidateMustRemainSubsetOfBase": True,
                "precisionDeltaMustBePositive": True,
                "f1DeltaMustBePositive": True,
            },
            "reference": {
                "path": str(REFERENCE_PATH.relative_to(ROOT)),
                "eventCount": len(reference),
                "measureCount": len({m for m, _ in reference}),
                "openedOnlyAfterFrozenPredictionFingerprintVerification": True,
            },
            "frozenPredictionFingerprints": {
                "baseSha256": actual_base_sha,
                "candidateSha256": actual_candidate_sha,
            },
            "base": base_metrics,
            "candidate": candidate_metrics,
            "deltaVsBase": delta,
            "pruneAudit": {
                "removedEvents": len(removed),
                "removedTruePositives": removed_tp,
                "removedFalsePositives": removed_fp,
            },
            "perMeasure": per_measure,
            "gate": {
                "predictionFingerprintsMatched": True,
                "candidateSubsetOfBase": candidate.issubset(base),
                "precisionDeltaPositive": precision_positive,
                "f1DeltaPositive": f1_positive,
                "reserveGatePassed": gate_passed,
            },
            "invariants": {
                "predictionsFrozenBeforeReserveReferenceOpened": True,
                "professionalReferenceUsedForPrediction": False,
                "reserveReferenceOpenedForOneShotGrading": True,
                "predictionsModifiedAfterReferenceOpen": False,
                "productionModified": False,
            },
        }
    )
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("=== V143 RESERVE ONE-SHOT GRADE ===")
    print("REFERENCE_EVENTS", len(reference))
    print("BASE", rounded(base_metrics))
    print("CANDIDATE", rounded(candidate_metrics))
    print("DELTA", rounded(delta))
    print("REMOVED", {"total": len(removed), "tp": removed_tp, "fp": removed_fp})
    print("RESERVE_GATE_PASSED", gate_passed)
    print("PRODUCTION_MODIFIED", False)
    print(f"WROTE={REPORT_PATH}")


if __name__ == "__main__":
    main()
