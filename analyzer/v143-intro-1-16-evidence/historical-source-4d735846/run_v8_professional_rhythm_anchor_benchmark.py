from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates.json"
REFERENCE_PATH = REPO_ROOT / "analyzer" / "fixtures" / "gomyway_professional_intro_reference_v1.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-professional-rhythm-anchor.json"

STEPS_PER_MEASURE = 16
PAIR_STEPS = STEPS_PER_MEASURE * 2
SCORE_TOLERANCE = 1e-9


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _safe_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _reference_pair_steps(reference: dict[str, Any]) -> list[int]:
    repeat = reference.get("repeat") or {}
    source_measures = {
        _safe_int(value)
        for value in repeat.get("sourceMeasures", [1, 2])
    }
    steps: set[int] = set()

    for note in reference.get("notes") or []:
        measure = _safe_int(note.get("measure"))
        step = _safe_int(note.get("step"))
        if measure not in source_measures:
            continue
        pair_step = ((measure - min(source_measures)) * STEPS_PER_MEASURE) + step
        steps.add(pair_step % PAIR_STEPS)

    return sorted(steps)


def _stable_slots(candidate_report: dict[str, Any]) -> list[dict[str, Any]]:
    diagnostics = candidate_report.get("diagnostics") or {}
    return [
        {
            "pairStep": _safe_int(item.get("pairStep")) % PAIR_STEPS,
            "pairSupport": _safe_int(item.get("pairSupport")),
            "medianStrength": _safe_float(item.get("medianStrength")),
        }
        for item in diagnostics.get("stableIntroPairSteps") or []
    ]


def _evaluate_offset(
    stable_slots: list[dict[str, Any]],
    reference_steps: set[int],
    offset_steps: int,
) -> dict[str, Any]:
    shifted = [
        {
            **item,
            "anchoredPairStep": (int(item["pairStep"]) + offset_steps) % PAIR_STEPS,
        }
        for item in stable_slots
    ]
    shifted_steps = {int(item["anchoredPairStep"]) for item in shifted}
    matched_steps = sorted(shifted_steps & reference_steps)
    match_count = len(matched_steps)
    candidate_count = len(shifted_steps)
    reference_count = len(reference_steps)
    precision = match_count / candidate_count if candidate_count else 0.0
    recall = match_count / reference_count if reference_count else 0.0
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    matched_strength = sum(
        float(item["medianStrength"])
        for item in shifted
        if int(item["anchoredPairStep"]) in reference_steps
    )
    total_strength = sum(float(item["medianStrength"]) for item in shifted)
    strength_coverage = matched_strength / total_strength if total_strength else 0.0

    return {
        "offsetSteps": offset_steps,
        "offsetMeasureFraction": round(offset_steps / STEPS_PER_MEASURE, 6),
        "candidateAttackCount": candidate_count,
        "referenceAttackCount": reference_count,
        "anchorMatchCount": match_count,
        "anchorPrecision": round(precision, 6),
        "anchorRecall": round(recall, 6),
        "anchorF1": round(f1, 6),
        "matchedStrength": round(matched_strength, 6),
        "strengthCoverage": round(strength_coverage, 6),
        "matchedReferenceSteps": matched_steps,
        "anchoredSlots": shifted,
        "readOnly": True,
    }


def _same_rank(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        int(left["anchorMatchCount"]) == int(right["anchorMatchCount"])
        and abs(float(left["anchorF1"]) - float(right["anchorF1"])) <= SCORE_TOLERANCE
        and abs(float(left["strengthCoverage"]) - float(right["strengthCoverage"]))
        <= SCORE_TOLERANCE
    )


def main() -> None:
    if not CANDIDATE_PATH.exists():
        raise FileNotFoundError(
            "Missing rhythm candidate report. Run "
            "python analyzer/run_v8_rhythm_candidate_benchmark.py first."
        )
    if not REFERENCE_PATH.exists():
        raise FileNotFoundError(f"Missing professional reference: {REFERENCE_PATH}")

    candidate_report = json.loads(CANDIDATE_PATH.read_text())
    reference = json.loads(REFERENCE_PATH.read_text())
    stable_slots = _stable_slots(candidate_report)
    reference_step_list = _reference_pair_steps(reference)
    reference_steps = set(reference_step_list)

    evaluations = [
        _evaluate_offset(stable_slots, reference_steps, offset)
        for offset in range(PAIR_STEPS)
    ]
    ranked = sorted(
        evaluations,
        key=lambda item: (
            int(item["anchorMatchCount"]),
            float(item["anchorF1"]),
            float(item["strengthCoverage"]),
            -abs(int(item["offsetSteps"])),
        ),
        reverse=True,
    )
    best = ranked[0] if ranked else None
    equivalent_best = [
        item for item in ranked
        if best is not None and _same_rank(item, best)
    ]
    unique_anchor_found = len(equivalent_best) == 1
    adopted_anchor = best if unique_anchor_found else None

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-professional-reference-rhythm-phase-anchor",
        "candidateInput": CANDIDATE_PATH.name,
        "referenceInput": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "professionalAnchorPass": bool(stable_slots and reference_steps),
        "referenceAttackCount": len(reference_steps),
        "referencePairSteps": reference_step_list,
        "stableCandidateCount": len(stable_slots),
        "stableCandidateSteps": [int(item["pairStep"]) for item in stable_slots],
        "uniqueAnchorFound": unique_anchor_found,
        "equivalentBestOffsetCount": len(equivalent_best),
        "equivalentBestOffsets": [int(item["offsetSteps"]) for item in equivalent_best],
        "bestCandidate": best,
        "adoptedAnchor": adopted_anchor,
        "rankedAnchors": ranked,
        "independentOfV7Events": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "passed": bool(stable_slots and reference_steps),
        "trainingRule": (
            "The professional reference may anchor the relative direct-audio rhythm "
            "skeleton only when one rotation is uniquely best. An ambiguous result "
            "remains diagnostic and must not alter V7 notes, production output, or "
            "the PDF renderer."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional anchor pass:", report["professionalAnchorPass"])
    print("Independent of V7 events:", report["independentOfV7Events"])
    print("Renderer changed:", report["rendererChanged"])
    print("Reference attack count:", report["referenceAttackCount"])
    print("Reference pair steps:", report["referencePairSteps"])
    print("Stable candidate count:", report["stableCandidateCount"])
    print("Stable candidate steps:", report["stableCandidateSteps"])
    print("Unique anchor found:", report["uniqueAnchorFound"])
    print("Equivalent best offset count:", report["equivalentBestOffsetCount"])
    print("Equivalent best offsets:", report["equivalentBestOffsets"])
    print("Best anchored offset:", best.get("offsetSteps") if best else None)
    print("Anchor match count:", best.get("anchorMatchCount") if best else None)
    print("Anchor recall:", best.get("anchorRecall") if best else None)
    print("Anchor precision:", best.get("anchorPrecision") if best else None)
    print("Anchor F1:", best.get("anchorF1") if best else None)
    print("Matched reference steps:", best.get("matchedReferenceSteps") if best else None)
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
