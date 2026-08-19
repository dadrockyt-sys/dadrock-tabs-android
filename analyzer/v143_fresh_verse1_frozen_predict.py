from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import v143_intro_consensus_alignment_refinement as consensus
from v143_intro_repetition_recovery_event_selector import _score_measures
from v143_intro_learned_grid_event_selector import _predict_pitch_sets_for_assignments


REPO_ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_DIR = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
)

CACHE_PATH = CALIBRATION_DIR / "fresh-verse1-reference-free-cache.json"
BASE_SELECTOR_MODEL_PATH = CALIBRATION_DIR / "intro-learned-grid-event-selector-model.json"
SEQUENCE_MODEL_PATH = CALIBRATION_DIR / "intro-sequence-event-model.json"
ONSET_MODEL_PATH = CALIBRATION_DIR / "intro-onset-group-sequence-model.json"
CONSTRAINED_MODEL_PATH = CALIBRATION_DIR / "intro-constrained-count-reranker-model.json"
PITCH_MODEL_PATH = CALIBRATION_DIR / "intro-learned-onset-spectral-set-model.json"

OUTPUT_PATH = CALIBRATION_DIR / "fresh-verse1-frozen-predictions.json"

FIRST_MEASURE = 17
LAST_MEASURE = 32
MEASURES = set(range(FIRST_MEASURE, LAST_MEASURE + 1))

# Deliberately no professional-reference path exists in this file. This stage
# must save frozen predictions before any Verse 1 human labels are opened.


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required frozen artifact: {path}")
    return json.loads(path.read_text())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rows_by_measure(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = {}
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        measure = int(raw.get("measure") or 0)
        if measure not in MEASURES:
            continue
        row = dict(raw)
        out.setdefault(measure, []).append(row)
    for values in out.values():
        values.sort(
            key=lambda row: (
                float(row.get("onsetTime") or 0.0),
                int(row.get("onsetGroupId") or 0),
            )
        )
    return out


def _grid_lookup(cache: dict[str, Any]) -> dict[tuple[int, int], float]:
    grid: dict[tuple[int, int], float] = {}
    for raw in cache.get("grid", []) or []:
        if not isinstance(raw, dict):
            continue
        measure = int(raw.get("measure") or 0)
        step = int(raw.get("step") or 0)
        if measure in MEASURES and 0 <= step < 16:
            grid[(measure, step)] = float(raw.get("timeSeconds") or 0.0)
    return grid


def _baseline_active(
    keys: list[tuple[int, int]],
    scores: dict[tuple[int, int], float],
    evidence: dict[tuple[int, int], bool],
    threshold: float,
) -> set[tuple[int, int]]:
    return {
        key
        for key in keys
        if evidence.get(key, False)
        and float(scores.get(key, 0.0)) >= float(threshold)
    }


def _scaled_count(count: int, multiplier: float, eligible_count: int) -> int:
    if count <= 0 or eligible_count <= 0:
        return 0
    target = int(round(float(count) * float(multiplier)))
    return max(1, min(target, eligible_count))


def _select_ranked(
    ds: dict[str, Any],
    scores: np.ndarray,
    baseline_active: set[tuple[int, int]],
    policy: str,
    multiplier: float,
) -> set[tuple[int, int]]:
    eligible = [
        (key, float(score))
        for key, score, has_evidence in zip(ds["keys"], scores, ds["evidence"])
        if bool(has_evidence)
    ]
    if not eligible:
        return set()

    if policy == "block":
        k = _scaled_count(len(baseline_active), multiplier, len(eligible))
        ranked = sorted(eligible, key=lambda item: (-item[1], item[0]))
        return {key for key, _ in ranked[:k]}

    if policy == "per-measure":
        selected: set[tuple[int, int]] = set()
        for measure in sorted(MEASURES):
            candidates = [(key, score) for key, score in eligible if key[0] == measure]
            baseline_count = sum(1 for key in baseline_active if key[0] == measure)
            k = _scaled_count(baseline_count, multiplier, len(candidates))
            ranked = sorted(candidates, key=lambda item: (-item[1], item[0]))
            selected.update(key for key, _ in ranked[:k])
        return selected

    raise RuntimeError(f"Unknown frozen count policy: {policy}")


def main() -> None:
    cache = _load_json(CACHE_PATH)
    base_selector_model = _load_json(BASE_SELECTOR_MODEL_PATH)
    sequence_model = _load_json(SEQUENCE_MODEL_PATH)
    onset_model = _load_json(ONSET_MODEL_PATH)
    constrained_model = _load_json(CONSTRAINED_MODEL_PATH)
    pitch_model = _load_json(PITCH_MODEL_PATH)

    scope = str(cache.get("scope") or "")
    if scope != "fresh-verse1-measures-17-32-reference-free":
        raise RuntimeError(f"Unexpected fresh-cache scope: {scope!r}")
    if cache.get("professionalReferenceUsedByAnalyzer") is not False:
        raise RuntimeError("Fresh capture does not assert professionalReferenceUsedByAnalyzer=False")
    if cache.get("professionalReferenceRequiredAtRuntime") is not False:
        raise RuntimeError("Fresh capture does not assert professionalReferenceRequiredAtRuntime=False")

    rows = [dict(row) for row in (cache.get("rows") or []) if isinstance(row, dict)]
    rows_by_measure = _rows_by_measure(rows)
    grid = _grid_lookup(cache)
    expected_grid_count = len(MEASURES) * 16
    if len(grid) != expected_grid_count:
        raise RuntimeError(
            f"Fresh Verse 1 grid incomplete: expected {expected_grid_count}, got {len(grid)}"
        )

    spectrum_min = int(cache.get("spectrumMidiMin") or 28)
    spectrum_max = int(cache.get("spectrumMidiMax") or 112)
    spectrum_len = spectrum_max - spectrum_min + 1

    print("=== V143 FRESH VERSE 1 FROZEN PREDICTION ===")
    print("Measure range: 17..32")
    print("Frozen models only: True")
    print("Professional reference opened by predictor: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    # 1) Frozen intro-trained base grid selector.
    base_scores, base_evidence = _score_measures(
        rows_by_measure,
        grid,
        MEASURES,
        base_selector_model,
    )
    base_threshold = float(base_selector_model["threshold"])

    # 2) Frozen intro-trained multiscale sequence scorer. Passing an empty
    # reference is intentional: labels are only needed to construct Y, never X.
    seq_scores, seq_evidence = consensus._sequence_scores_for_measures(
        rows_by_measure,
        grid,
        {},
        MEASURES,
        MEASURES,
        base_scores,
        base_evidence,
        base_threshold,
        sequence_model,
    )

    # 3) Frozen physical-onset scorer.
    _, onset_scores = consensus._onset_scores_for_measures(
        rows_by_measure,
        grid,
        MEASURES,
        MEASURES,
        spectrum_len,
        onset_model,
    )

    # 4) Build the same label-free consensus features used during intro
    # calibration, then apply the frozen constrained reranker weights.
    ds = consensus._meta_dataset(
        {},
        MEASURES,
        MEASURES,
        rows_by_measure,
        grid,
        seq_scores,
        seq_evidence,
        onset_scores,
        float(sequence_model["threshold"]),
    )
    mean = np.asarray(constrained_model["featureMean"], dtype=np.float64)
    std = np.asarray(constrained_model["featureStd"], dtype=np.float64)
    weights = np.asarray(constrained_model["weights"], dtype=np.float64)
    rerank_scores = consensus._design(ds["X"], mean, std) @ weights

    sequence_baseline = _baseline_active(
        ds["keys"],
        seq_scores,
        seq_evidence,
        float(sequence_model["threshold"]),
    )
    active = _select_ranked(
        ds,
        rerank_scores,
        sequence_baseline,
        str(constrained_model["countPolicy"]),
        float(constrained_model["countMultiplier"]),
    )

    # 5) One-to-one physical-onset assignment using frozen onset confidence.
    assignments = consensus._assign_active_slots(
        active,
        rows_by_measure,
        grid,
        onset_scores,
        int(constrained_model["assignWindowMs"]),
        float(constrained_model["residualPenalty"]),
    )

    # 6) Frozen learned spectral pitch-set decoder.
    pitch_sets = _predict_pitch_sets_for_assignments(assignments, grid, pitch_model)

    predictions: list[dict[str, Any]] = []
    for key in sorted(active):
        measure, step = key
        assigned = assignments.get(key)
        predictions.append(
            {
                "measure": int(measure),
                "step": int(step),
                "gridTimeSeconds": round(float(grid[key]), 9),
                "assigned": assigned is not None,
                "onsetGroupId": int(assigned.get("onsetGroupId") or 0) if assigned else None,
                "onsetTimeSeconds": round(float(assigned.get("onsetTime") or 0.0), 9) if assigned else None,
                "signedResidualMs": round(
                    1000.0 * (float(assigned.get("onsetTime") or 0.0) - float(grid[key])),
                    3,
                ) if assigned else None,
                "midiPitches": sorted(int(value) for value in pitch_sets.get(key, set())),
                "candidateMidis": sorted(int(value) for value in (assigned.get("candidateMidis") or [])) if assigned else [],
            }
        )

    per_measure_counts = {
        str(measure): sum(1 for row in predictions if int(row["measure"]) == measure)
        for measure in range(FIRST_MEASURE, LAST_MEASURE + 1)
    }
    assigned_count = sum(bool(row["assigned"]) for row in predictions)
    predicted_pitch_event_count = sum(len(row["midiPitches"]) for row in predictions)

    model_paths = {
        "baseSelector": BASE_SELECTOR_MODEL_PATH,
        "sequence": SEQUENCE_MODEL_PATH,
        "onset": ONSET_MODEL_PATH,
        "constrainedReranker": CONSTRAINED_MODEL_PATH,
        "spectralPitchSet": PITCH_MODEL_PATH,
    }
    model_fingerprints = {
        name: {
            "path": str(path.relative_to(REPO_ROOT)),
            "sha256": _sha256(path),
        }
        for name, path in model_paths.items()
    }

    payload = {
        "schemaVersion": 1,
        "scope": "fresh-verse1-frozen-reference-free-predictions",
        "section": {"name": "Verse 1", "startMeasure": FIRST_MEASURE, "endMeasure": LAST_MEASURE},
        "sourceCache": str(CACHE_PATH.relative_to(REPO_ROOT)),
        "sourceCacheSha256": _sha256(CACHE_PATH),
        "modelFingerprints": model_fingerprints,
        "frozenConfiguration": {
            "baseSelectorThreshold": float(base_threshold),
            "sequenceThreshold": float(sequence_model["threshold"]),
            "countPolicy": str(constrained_model["countPolicy"]),
            "countMultiplier": float(constrained_model["countMultiplier"]),
            "assignWindowMs": int(constrained_model["assignWindowMs"]),
            "residualPenalty": float(constrained_model["residualPenalty"]),
            "pitchWindowMs": int(pitch_model["windowMs"]),
            "candidatePriorWeight": float(pitch_model["candidatePriorWeight"]),
            "polyphonyGapZ": float(pitch_model["polyphonyGapZ"]),
        },
        "sequenceBaselineEventCount": len(sequence_baseline),
        "selectedGridEventCount": len(active),
        "assignedOnsetEventCount": assigned_count,
        "predictedPitchEventCount": predicted_pitch_event_count,
        "perMeasureEventCounts": per_measure_counts,
        "predictions": predictions,
        "professionalReferenceOpenedByPredictor": False,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "predictionsFrozenBeforeGrading": True,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")

    print("\n=== FRESH VERSE 1 FROZEN PREDICTIONS SAVED ===")
    print("sequenceBaselineEventCount:", len(sequence_baseline))
    print("selectedGridEventCount:", len(active))
    print("assignedOnsetEventCount:", assigned_count)
    print("predictedPitchEventCount:", predicted_pitch_event_count)
    print("perMeasureEventCounts:", json.dumps(per_measure_counts, sort_keys=True))
    print("Professional reference opened by predictor: False")
    print("Predictions frozen before grading: True")
    print("Production modified: False")
    print("READY FOR FIRST REFERENCE OPEN / GRADING: True")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
