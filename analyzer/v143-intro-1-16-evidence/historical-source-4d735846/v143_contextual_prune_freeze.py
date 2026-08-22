#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "analyzer"
if str(ANALYZER) not in sys.path:
    sys.path.insert(0, str(ANALYZER))

import v143_contextual_prune_lobo as contextual
import v143_correlation_safe_fixed_count_reranker_freeze as freeze

CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"
REPORT_PATH = CAL / "contextual-prune-nested-lobo-report.json"
SOURCE_PATH = ANALYZER / "v143_contextual_prune_lobo.py"
MODEL_PATH = CAL / "contextual-prune-frozen-model.json"
EVENTS_PATH = CAL / "contextual-prune-17-96-frozen-events.json"
MANIFEST_PATH = CAL / "contextual-prune-freeze-manifest.json"

TARGET_MEASURES = set(range(17, 97))
EXPECTED_REFERENCE_COUNT = 431
EXPECTED_BASE_COUNT = 765
EXPECTED_FINAL_COUNT = 651


def load_json(path: Path) -> Any:
    if not path.exists() or path.stat().st_size <= 0:
        raise RuntimeError(f"Missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def as_list(value: Any) -> list[float]:
    return [float(v) for v in value.tolist()]


def main() -> None:
    report = load_json(REPORT_PATH)
    gate = report.get("gate", {})
    invariants = report.get("invariants", {})
    if gate.get("promotionEligible") is not True:
        raise RuntimeError("Contextual prune report is not promotion eligible")
    if invariants.get("measures97To113Opened") is not False:
        raise RuntimeError("Reserve-open invariant is not false")
    if invariants.get("reservePayloadOpened") is not False:
        raise RuntimeError("Reserve-payload-open invariant is not false")
    if invariants.get("candidateAddsEvents") is not False:
        raise RuntimeError("Contextual candidate unexpectedly adds events")
    if invariants.get("candidateRelocatesEvents") is not False:
        raise RuntimeError("Contextual candidate unexpectedly relocates events")

    final_cv = report.get("finalParameterSelectionByFiveFoldCV", {})
    l2 = float(final_cv.get("l2", -1.0))
    prune_fraction = float(final_cv.get("pruneFraction", -1.0))
    if l2 != 0.1 or prune_fraction != 0.15:
        raise RuntimeError(f"Unexpected selected parameters: l2={l2}, pruneFraction={prune_fraction}")

    # Blind-safe parser reads only consumed development measures and stops on
    # the measure-97 header before reserve event payload can be processed.
    reference, hit_boundary = contextual.parse_reference_blind_safe(contextual.REFERENCE_PATH)
    if not hit_boundary:
        raise RuntimeError("Did not encounter measure-97 reserve boundary")
    if len(reference) != EXPECTED_REFERENCE_COUNT:
        raise RuntimeError(f"Reference count changed: {len(reference)} != {EXPECTED_REFERENCE_COUNT}")

    base_model = load_json(freeze.BASE_MODEL_PATH)
    sequence_model = load_json(freeze.SEQUENCE_MODEL_PATH)
    if float(base_model.get("threshold", -1.0)) != 0.27:
        raise RuntimeError(f"Expected base threshold 0.27, got {base_model.get('threshold')}")

    rows_by_measure, grid = freeze._merge_fresh_caches()
    base_scores, base_evidence = freeze._score_measures(
        rows_by_measure,
        grid,
        TARGET_MEASURES,
        base_model,
    )
    base_active = freeze._active_from_scores(
        base_scores,
        base_evidence,
        TARGET_MEASURES,
        float(base_model["threshold"]),
    )
    if len(base_active) != EXPECTED_BASE_COUNT:
        raise RuntimeError(f"Base replay count mismatch: {len(base_active)} != {EXPECTED_BASE_COUNT}")

    sequence_scores, sequence_evidence = freeze._sequence_scores(
        rows_by_measure,
        grid,
        TARGET_MEASURES,
        TARGET_MEASURES,
        base_scores,
        base_evidence,
        base_model,
        sequence_model,
    )

    features = contextual.build_features(
        base_active,
        base_scores,
        sequence_scores,
        sequence_evidence,
    )
    full_keys = sorted(base_active)
    model = contextual.fit_logistic(full_keys, features, reference, l2)
    probabilities = contextual.predict_probabilities(model, full_keys, features)
    candidate = contextual.apply_prune_fraction(
        base_active,
        TARGET_MEASURES,
        probabilities,
        prune_fraction,
    )
    if len(candidate) != EXPECTED_FINAL_COUNT:
        raise RuntimeError(f"Frozen candidate count mismatch: {len(candidate)} != {EXPECTED_FINAL_COUNT}")
    if not candidate.issubset(base_active):
        raise RuntimeError("Frozen candidate is not a subset of base-0.27 events")

    base_metrics = contextual.metrics(base_active, reference)
    candidate_metrics = contextual.metrics(candidate, reference)
    if round(float(base_metrics["f1"]), 6) != 0.503344:
        raise RuntimeError(f"Base F1 mismatch: {base_metrics['f1']}")
    if round(float(candidate_metrics["f1"]), 6) != 0.54159:
        raise RuntimeError(f"Candidate F1 mismatch: {candidate_metrics['f1']}")

    frozen_model = {
        "schemaVersion": 1,
        "model": "v143-contextual-prune",
        "purpose": "Prune context-dependent false positives from promoted base-0.27 events without adding or relocating events.",
        "trainingMeasures": "17-96",
        "reserveMeasures": "97-113",
        "featureNames": contextual.FEATURE_NAMES,
        "l2": l2,
        "pruneFraction": prune_fraction,
        "weights": as_list(model["weights"]),
        "featureMean": as_list(model["mean"]),
        "featureStd": as_list(model["std"]),
        "baseThreshold": 0.27,
        "baseEventCount17To96": len(base_active),
        "candidateEventCount17To96": len(candidate),
        "developmentMetrics": {
            "base": base_metrics,
            "candidate": candidate_metrics,
            "f1Delta": float(candidate_metrics["f1"] - base_metrics["f1"]),
        },
        "candidateAddsEvents": False,
        "candidateRelocatesEvents": False,
        "professionalReferenceRequiredAtRuntime": False,
        "measures97To113UsedForTraining": False,
        "productionModified": False,
    }
    MODEL_PATH.write_text(json.dumps(frozen_model, indent=2) + "\n", encoding="utf-8")

    frozen_events = {
        "schemaVersion": 1,
        "artifact": "v143-contextual-prune-17-96-frozen-events",
        "measures": "17-96",
        "eventCount": len(candidate),
        "events": [
            {
                "measure": int(measure),
                "quantizedStep": int(step),
                "baseScore": float(base_scores.get((measure, step), 0.0)),
                "sequenceScore": float(sequence_scores.get((measure, step), 0.0)),
                "sequenceEvidence": bool(sequence_evidence.get((measure, step), False)),
                "contextualKeepProbability": float(probabilities[(measure, step)]),
            }
            for measure, step in sorted(candidate)
        ],
        "reserveMeasures97To113Opened": False,
        "productionModified": False,
    }
    EVENTS_PATH.write_text(json.dumps(frozen_events, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schemaVersion": 1,
        "freeze": "v143-contextual-prune-before-reserve",
        "developmentMeasures": "17-96",
        "reserveMeasures": "97-113",
        "selectedParameters": {"l2": l2, "pruneFraction": prune_fraction},
        "predictionsFrozenBeforeReserveGrading": True,
        "targetReserveReferenceOpened": False,
        "measures97To113Opened": False,
        "reservePayloadOpened": False,
        "developmentReferenceUsed": True,
        "productionModified": False,
        "fingerprints": {
            "nestedLoboReportSha256": sha256(REPORT_PATH),
            "contextualSourceSha256": sha256(SOURCE_PATH),
            "baseModelSha256": sha256(freeze.BASE_MODEL_PATH),
            "sequenceModelSha256": sha256(freeze.SEQUENCE_MODEL_PATH),
            "frozenModelSha256": sha256(MODEL_PATH),
            "frozenDevelopmentEventsSha256": sha256(EVENTS_PATH),
        },
        "counts": {
            "developmentReference": len(reference),
            "baseEvents17To96": len(base_active),
            "contextualEvents17To96": len(candidate),
        },
        "developmentMetrics": {
            "base": base_metrics,
            "candidate": candidate_metrics,
            "f1Delta": float(candidate_metrics["f1"] - base_metrics["f1"]),
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("=== V143 CONTEXTUAL PRUNE FREEZE ===")
    print("PARAMS", {"l2": l2, "pruneFraction": prune_fraction})
    print("BASE", base_metrics)
    print("CANDIDATE", candidate_metrics)
    print("RESERVE_97_113_OPENED", False)
    print(f"WROTE_MODEL={MODEL_PATH}")
    print(f"WROTE_EVENTS={EVENTS_PATH}")
    print(f"WROTE_MANIFEST={MANIFEST_PATH}")


if __name__ == "__main__":
    main()
