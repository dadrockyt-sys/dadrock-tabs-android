from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FULL_REVIEW = ROOT / "public" / "gomyway-professional-rhythm-reference-full-review-17-113.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-consensus-candidates-17-113.json"
TEXT = ROOT / "public" / "gomyway-professional-rhythm-reference-consensus-candidates-17-113.txt"

CHUNKS = [
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-populated.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-populated.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-populated.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-populated.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-populated.json",
]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": int(event.get("quantizedStep", -1)),
        "duration": int(event.get("durationSteps", -1)),
        "notes": sorted(
            [
                {"string": int(note.get("string", -99)), "fret": int(note.get("fret", -99))}
                for note in event.get("notes", [])
            ],
            key=lambda item: (item["string"], item["fret"]),
        ),
        "techniques": sorted(str(item) for item in event.get("techniques", [])),
    }


def signature(measure: dict[str, Any]) -> str:
    payload = {
        "timeSignature": measure.get("timeSignature"),
        "events": [normalized_event(event) for event in measure.get("events", [])],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def is_human_approved(measure: dict[str, Any]) -> bool:
    review = measure.get("humanReview", {})
    status = str(review.get("status", "")).lower()
    return status in {"approved", "human-approved", "validated"} or all(
        bool(event.get("humanValidated")) for event in measure.get("events", [])
    )


def min_confidence(measure: dict[str, Any]) -> float:
    events = measure.get("events", [])
    if not events:
        return 1.0
    return min(float(event.get("referenceConfidence", 0.0)) for event in events)


def main() -> None:
    review = load(FULL_REVIEW)
    measures: dict[int, dict[str, Any]] = {}
    for path in CHUNKS:
        packet = load(path)
        for measure in packet.get("measures", []):
            number = int(measure["measureNumber"])
            if 17 <= number <= 113:
                measures[number] = measure

    expected = set(range(17, 114))
    if set(measures) != expected:
        raise RuntimeError(
            f"Coverage mismatch missing={sorted(expected - set(measures))} "
            f"extra={sorted(set(measures) - expected)}"
        )

    groups: dict[str, list[int]] = defaultdict(list)
    for number, measure in measures.items():
        groups[signature(measure)].append(number)

    approved = {number for number, measure in measures.items() if is_human_approved(measure)}
    warning_measures = set(int(item) for item in review.get("priorityReviewMeasures", []))

    candidates: list[dict[str, Any]] = []
    manual_only: list[dict[str, Any]] = []
    for sig, numbers in sorted(groups.items(), key=lambda item: min(item[1])):
        numbers = sorted(numbers)
        approved_examples = sorted(set(numbers) & approved)
        warnings = sorted(set(numbers) & warning_measures)
        confidence = min(min_confidence(measures[number]) for number in numbers)

        if len(numbers) >= 2 and approved_examples:
            candidates.append({
                "signature": sig,
                "measures": numbers,
                "approvedExamples": approved_examples,
                "warningMeasures": warnings,
                "minimumConfidence": confidence,
                "candidateReason": "exact semantic event signature matches an already human-approved measure",
                "automaticApprovalApplied": False,
                "humanConfirmationRequired": True,
            })
        elif warnings:
            manual_only.append({
                "signature": sig,
                "measures": numbers,
                "warningMeasures": warnings,
                "minimumConfidence": confidence,
                "reason": "no approved identical example exists",
            })

    candidate_measures = sorted({m for item in candidates for m in item["warningMeasures"]})
    manual_measures = sorted({m for item in manual_only for m in item["warningMeasures"]})

    result = {
        "schemaVersion": 1,
        "referenceRange": [17, 113],
        "measuresCovered": len(measures),
        "referenceEvents": review.get("referenceEvents"),
        "structurallyValidChunks": review.get("structurallyValidChunks"),
        "existingHumanApprovedMeasures": sorted(approved),
        "priorityReviewMeasures": sorted(warning_measures),
        "consensusCandidateGroups": candidates,
        "consensusCandidateMeasures": candidate_measures,
        "manualOnlyGroups": manual_only,
        "manualOnlyMeasures": manual_measures,
        "automaticApprovalApplied": False,
        "readyForTraining": False,
        "nextRequiredStage": "human-confirm-consensus-candidates-and-review-unique-warning-measures",
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "GOMYWAY PROFESSIONAL RHYTHM CONSENSUS CANDIDATES 17-113",
        f"Measures covered: {len(measures)} / 97",
        f"Existing human-approved measures: {len(approved)} / 97",
        f"Priority review measures: {len(warning_measures)}",
        f"Consensus candidate groups: {len(candidates)}",
        f"Consensus candidate measures: {candidate_measures}",
        f"Manual-only warning measures: {manual_measures}",
        "Automatic approval applied: False",
        "Ready for training: False",
        "Protected baselines changed: False",
        "",
    ]
    for item in candidates:
        lines.append(
            f"CONSENSUS {item['signature']}: measures={item['measures']} "
            f"approvedExamples={item['approvedExamples']} warnings={item['warningMeasures']} "
            f"minConfidence={item['minimumConfidence']:.2f}"
        )
    lines.append("")
    for item in manual_only:
        lines.append(
            f"MANUAL {item['signature']}: measures={item['measures']} "
            f"warnings={item['warningMeasures']} minConfidence={item['minimumConfidence']:.2f}"
        )
    TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Professional rhythm consensus candidate audit 17-113 complete")
    print(f"Measures covered: {len(measures)} / 97")
    print(f"Existing human-approved measures: {len(approved)} / 97")
    print(f"Priority review measures: {len(warning_measures)}")
    print(f"Consensus candidate groups: {len(candidates)}")
    print(f"Consensus candidate measures: {len(candidate_measures)}")
    print(f"Manual-only warning measures: {len(manual_measures)}")
    print("Automatic approval applied: False")
    print("Ready for training: False")
    print(f"JSON: {OUTPUT.relative_to(ROOT)}")
    print(f"Text: {TEXT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
