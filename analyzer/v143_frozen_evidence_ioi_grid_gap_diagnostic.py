from __future__ import annotations

import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
RETIRED_EVENT_SHA256 = "a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb"
ATTACK_COUNT = 725
MEASURE_COUNT = 113
STEPS_PER_MEASURE = 16
MAX_PHYSICAL_GAP_STEPS = 16
CONFIDENCE_BANDS = (0.10, 0.15, 0.20, 0.25)


def _rate(numerator: int, denominator: int) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "min": None, "median": None, "mean": None, "max": None}
    return {
        "count": len(values),
        "min": min(values),
        "median": statistics.median(values),
        "mean": statistics.mean(values),
        "max": max(values),
    }


def _load(evidence: dict[str, Any]) -> tuple[list[dict[str, Any]], float]:
    provenance = evidence.get("provenance") or {}
    if provenance.get("sourceAudioSha256") != APPROVED_AUDIO_SHA256:
        raise RuntimeError("approved frozen source audio changed")
    if provenance.get("retiredFrozenEventSha256") != RETIRED_EVENT_SHA256:
        raise RuntimeError("frozen source identity changed")
    if provenance.get("referenceFree") is not True:
        raise RuntimeError("frozen evidence is not reference-free")
    if provenance.get("professionalReferenceUsed") is not False:
        raise RuntimeError("professional reference provenance is unsafe")
    if provenance.get("referenceRuntimeInputUsed") is not False:
        raise RuntimeError("reference entered runtime evidence")
    if provenance.get("preScorer") is not True:
        raise RuntimeError("evidence is not sealed pre-scorer evidence")

    attacks = list(evidence.get("attacks") or [])
    tempo = float(evidence.get("tempoBpm") or 0.0)
    if len(attacks) != ATTACK_COUNT or tempo <= 0.0:
        raise RuntimeError("frozen attack cardinality/tempo changed")

    rows: list[dict[str, Any]] = []
    seen_slots: set[int] = set()
    for index, attack in enumerate(attacks):
        measure = int(attack[0])
        step = int(attack[1])
        time_seconds = float(attack[2])
        global_step = (measure - 1) * STEPS_PER_MEASURE + step
        if not (1 <= measure <= MEASURE_COUNT and 0 <= step < STEPS_PER_MEASURE):
            raise RuntimeError(f"invalid frozen slot at attack {index}")
        if global_step in seen_slots:
            raise RuntimeError(f"duplicate frozen grid slot {global_step}")
        if not math.isfinite(time_seconds):
            raise RuntimeError(f"non-finite frozen attack time at {index}")
        seen_slots.add(global_step)
        rows.append(
            {
                "measure": measure,
                "step": step,
                "globalStep": global_step,
                "timeSeconds": time_seconds,
            }
        )

    rows.sort(key=lambda row: (float(row["timeSeconds"]), int(row["globalStep"])))
    if any(float(right["timeSeconds"]) <= float(left["timeSeconds"]) for left, right in zip(rows, rows[1:])):
        raise RuntimeError("frozen attack timestamps are not strictly increasing")
    return rows, tempo


def _band_report(pairs: list[dict[str, Any]], band: float) -> dict[str, Any]:
    scoped = [pair for pair in pairs if float(pair["nearestMultipleResidualSteps"]) <= band]
    offsets = Counter(int(pair["labeledGapSteps"]) - int(pair["nearestPhysicalGapSteps"]) for pair in scoped)
    exact = int(offsets.get(0, 0))
    one_step = int(offsets.get(-1, 0) + offsets.get(1, 0))
    two_step = int(offsets.get(-2, 0) + offsets.get(2, 0))
    larger = len(scoped) - exact - one_step - two_step
    return {
        "maxNearestMultipleResidualSteps": float(band),
        "pairCount": len(scoped),
        "exactGapMatchCount": exact,
        "exactGapMatchRate": _rate(exact, len(scoped)),
        "absoluteOneStepMismatchCount": one_step,
        "absoluteTwoStepMismatchCount": two_step,
        "absoluteLargerMismatchCount": larger,
        "signedLabeledMinusPhysicalGapCounts": {str(key): offsets[key] for key in sorted(offsets)},
    }


def diagnose(evidence: dict[str, Any]) -> dict[str, Any]:
    rows, tempo = _load(evidence)
    nominal_step_seconds = 60.0 / tempo / 4.0

    pairs: list[dict[str, Any]] = []
    for left, right in zip(rows, rows[1:]):
        delta_time = float(right["timeSeconds"]) - float(left["timeSeconds"])
        raw_multiple = delta_time / nominal_step_seconds
        nearest = int(round(raw_multiple))
        if nearest < 1 or nearest > MAX_PHYSICAL_GAP_STEPS:
            continue
        labeled_gap = int(right["globalStep"]) - int(left["globalStep"])
        if labeled_gap <= 0:
            continue
        residual = abs(raw_multiple - nearest)
        pairs.append(
            {
                "leftMeasure": int(left["measure"]),
                "leftStep": int(left["step"]),
                "rightMeasure": int(right["measure"]),
                "rightStep": int(right["step"]),
                "deltaSeconds": delta_time,
                "nominalGapSteps": raw_multiple,
                "nearestPhysicalGapSteps": nearest,
                "nearestMultipleResidualSteps": residual,
                "labeledGapSteps": labeled_gap,
                "labeledMinusPhysicalGapSteps": labeled_gap - nearest,
            }
        )

    if not pairs:
        raise RuntimeError("no usable physical IOI pairs")

    band_reports = [_band_report(pairs, band) for band in CONFIDENCE_BANDS]
    strict = band_reports[0]
    broad = band_reports[-1]

    by_measure_window: list[dict[str, Any]] = []
    for start in range(1, MEASURE_COUNT + 1, 8):
        end = min(MEASURE_COUNT, start + 7)
        scoped = [
            pair
            for pair in pairs
            if start <= int(pair["leftMeasure"]) <= end
            and float(pair["nearestMultipleResidualSteps"]) <= 0.20
        ]
        offsets = [int(pair["labeledMinusPhysicalGapSteps"]) for pair in scoped]
        exact = sum(value == 0 for value in offsets)
        by_measure_window.append(
            {
                "startMeasure": start,
                "endMeasure": end,
                "highConfidencePairCount": len(scoped),
                "exactGapMatchCount": exact,
                "exactGapMatchRate": _rate(exact, len(scoped)),
                "signedOffsetMedianSteps": statistics.median(offsets) if offsets else None,
                "signedOffsetMeanSteps": statistics.mean(offsets) if offsets else None,
                "nonzeroOffsetCount": sum(value != 0 for value in offsets),
            }
        )

    all_offsets = [int(pair["labeledMinusPhysicalGapSteps"]) for pair in pairs]
    high_confidence_020 = [
        pair for pair in pairs if float(pair["nearestMultipleResidualSteps"]) <= 0.20
    ]
    high_offsets = [int(pair["labeledMinusPhysicalGapSteps"]) for pair in high_confidence_020]

    return {
        "schemaVersion": 1,
        "mode": "v143-frozen-evidence-ioi-grid-gap-diagnostic",
        "sourceAudioSha256": APPROVED_AUDIO_SHA256,
        "sourceRetiredEventSha256": RETIRED_EVENT_SHA256,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "modalUsed": False,
        "newInferenceUsed": False,
        "productionModified": False,
        "protectedRuntimeModified": False,
        "candidateRenderProduced": False,
        "eventMutationProposed": False,
        "attackCount": len(rows),
        "tempoMetadataBpm": tempo,
        "nominalSecondsPerSixteenthStep": nominal_step_seconds,
        "method": {
            "physicalEvidence": "consecutive frozen attack timestamps only",
            "physicalGapEstimate": "round each IOI to nearest integer multiple of metadata sixteenth duration",
            "labelUsage": "existing measure/step labels are used only after physical-gap estimation for comparison and window grouping",
            "maximumPhysicalGapSteps": MAX_PHYSICAL_GAP_STEPS,
            "confidenceBandsResidualSixteenthSteps": list(CONFIDENCE_BANDS),
            "selectionBoundary": "diagnostic only; no gap correction or grid mutation is selected",
        },
        "pairUniverse": {
            "usableConsecutivePairCount": len(pairs),
            "nearestMultipleResidualSteps": _summary([float(pair["nearestMultipleResidualSteps"]) for pair in pairs]),
            "labeledMinusPhysicalGapSteps": _summary([float(value) for value in all_offsets]),
        },
        "confidenceBands": band_reports,
        "highConfidence020": {
            "pairCount": len(high_confidence_020),
            "exactGapMatchCount": sum(value == 0 for value in high_offsets),
            "exactGapMatchRate": _rate(sum(value == 0 for value in high_offsets), len(high_offsets)),
            "nonzeroOffsetCount": sum(value != 0 for value in high_offsets),
            "absoluteOffsetSteps": _summary([abs(float(value)) for value in high_offsets]),
        },
        "eightMeasureWindows": by_measure_window,
        "diagnosticFlags": {
            "strict010MajorityExactGapMatch": float(strict["exactGapMatchRate"]) >= 0.5,
            "broad025MajorityExactGapMatch": float(broad["exactGapMatchRate"]) >= 0.5,
            "highConfidence020HasSystematicSignedOffset": (
                bool(high_offsets)
                and abs(float(statistics.median(high_offsets))) >= 1.0
            ),
            "highConfidence020NonzeroMismatchRateAboveQuarter": (
                bool(high_offsets)
                and _rate(sum(value != 0 for value in high_offsets), len(high_offsets)) > 0.25
            ),
        },
        "interpretationBoundary": (
            "This asks whether physical inter-onset intervals near integer sixteenth multiples agree with the existing labeled gap. "
            "It does not prove musical correctness, does not infer missing attacks, and does not select a new timing grid."
        ),
        "invariants": {
            "all725AttacksRead": len(rows) == ATTACK_COUNT,
            "eventsMutated": False,
            "attackGridMutated": False,
            "pitchSelectionMutated": False,
            "referenceConsulted": False,
            "modalInvoked": False,
        },
    }


def main(source: str, destination: str) -> None:
    evidence = json.loads(Path(source).read_text(encoding="utf-8"))
    report = diagnose(evidence)
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "pairUniverse": report["pairUniverse"],
        "confidenceBands": report["confidenceBands"],
        "highConfidence020": report["highConfidence020"],
        "diagnosticFlags": report["diagnosticFlags"],
    }, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: v143_frozen_evidence_ioi_grid_gap_diagnostic.py EVIDENCE OUTPUT")
    main(sys.argv[1], sys.argv[2])
