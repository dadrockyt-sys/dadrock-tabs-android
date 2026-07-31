from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CORRECTED_SIGNATURE_PATH = (
    REPO_ROOT / "public" / "gomyway-full-song-v8-corrected-intro-signature.json"
)
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-intro-orientation-lock.json"

EXPECTED_LAYER = "renderEvents"
EXPECTED_FIRST_MIDI = 40
EXPECTED_SECOND_MIDIS = {62, 67}
MIN_SECOND_SIGNATURE_COVERAGE = 0.5
MIN_SCORE_MARGIN = 0.5


def _safe_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def main() -> None:
    if not CORRECTED_SIGNATURE_PATH.exists():
        raise FileNotFoundError(
            f"Missing corrected signature report: {CORRECTED_SIGNATURE_PATH}"
        )

    source = json.loads(CORRECTED_SIGNATURE_PATH.read_text())
    selected_layer = source.get("selectedLayer")
    selected_offset = source.get("selectedOffset")
    layer_results = source.get("layerResults") or []

    selected_result = next(
        (
            item
            for item in layer_results
            if isinstance(item, dict) and item.get("layer") == selected_layer
        ),
        None,
    )
    if selected_result is None:
        raise ValueError("Selected event layer is missing from the corrected report")

    offset_results = [
        item
        for item in selected_result.get("offsetResults") or []
        if isinstance(item, dict)
    ]
    selected_offset_result = next(
        (
            item
            for item in offset_results
            if _safe_int(item.get("offsetSteps"), -999)
            == _safe_int(selected_offset, -998)
        ),
        None,
    )
    if selected_offset_result is None:
        raise ValueError("Selected offset details are missing from the corrected report")

    competing_scores = sorted(
        (
            _safe_float(item.get("orientationScore"))
            for item in offset_results
            if _safe_int(item.get("offsetSteps"), -999)
            != _safe_int(selected_offset, -998)
        ),
        reverse=True,
    )
    selected_score = _safe_float(selected_offset_result.get("orientationScore"))
    runner_up_score = competing_scores[0] if competing_scores else 0.0
    score_margin = selected_score - runner_up_score

    first = selected_offset_result.get("firstMeasure") or {}
    second = selected_offset_result.get("secondMeasure") or {}
    first_midis = {
        _safe_int(value)
        for value in first.get("exactDistinctMidis") or []
        if _safe_int(value) > 0
    }
    second_midis = {
        _safe_int(value)
        for value in second.get("exactDistinctMidis") or []
        if _safe_int(value) > 0
    }
    second_coverage = _safe_float(second.get("expectedCoverage"))

    checks = {
        "correctedSignaturePassed": source.get("passed") is True,
        "protectedBaselinesUnchanged": source.get("protectedBaselinesChanged") is False,
        "rendererUnchanged": source.get("rendererChanged") is False,
        "uniqueOrientationReported": source.get("uniqueOrientationFound") is True,
        "selectedLayerIsRenderEvents": selected_layer == EXPECTED_LAYER,
        "selectedOffsetIsInteger": isinstance(selected_offset, int),
        "openLowESignaturePresent": EXPECTED_FIRST_MIDI in first_midis,
        "professionalDoubleStopEvidencePresent": bool(
            second_midis & EXPECTED_SECOND_MIDIS
        ),
        "minimumDoubleStopCoverageMet": (
            second_coverage >= MIN_SECOND_SIGNATURE_COVERAGE
        ),
        "minimumScoreMarginMet": score_margin >= MIN_SCORE_MARGIN,
    }
    orientation_locked = all(checks.values())

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-intro-orientation-lock",
        "passed": orientation_locked,
        "orientationLocked": orientation_locked,
        "selectedLayer": selected_layer if orientation_locked else None,
        "selectedOffsetSteps": selected_offset if orientation_locked else None,
        "selectedScore": round(selected_score, 6),
        "runnerUpScore": round(runner_up_score, 6),
        "scoreMargin": round(score_margin, 6),
        "firstMeasureExactMidi": sorted(first_midis),
        "secondMeasureExactMidi": sorted(second_midis),
        "secondMeasureCoverage": round(second_coverage, 6),
        "checks": checks,
        "usesV7PitchEvidenceReadOnly": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "nextTrainingStage": (
            "Use the locked two-measure orientation only as a read-only alignment anchor "
            "for intro consensus evaluation. Do not synthesize notes, replace V7 pitch "
            "events, or change the PDF renderer."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Intro orientation lock pass:", report["passed"])
    print("Orientation locked:", report["orientationLocked"])
    print("Selected layer:", report["selectedLayer"])
    print("Selected offset steps:", report["selectedOffsetSteps"])
    print("Selected score:", report["selectedScore"])
    print("Runner-up score:", report["runnerUpScore"])
    print("Score margin:", report["scoreMargin"])
    print("First-measure exact MIDI:", report["firstMeasureExactMidi"])
    print("Second-measure exact MIDI:", report["secondMeasureExactMidi"])
    print("Second-measure coverage:", report["secondMeasureCoverage"])
    print("Checks:", report["checks"])
    print("Renderer changed:", report["rendererChanged"])
    print("Protected baselines changed:", report["protectedBaselinesChanged"])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
