from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-full-review-after-all-source-resolution.json"
TEXT = ROOT / "public" / "gomyway-professional-rhythm-reference-full-review-after-all-source-resolution.txt"

CHUNKS = [
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-source-resolved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-source-resolved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-source-reviewed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-source-resolved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-source-resolved.json",
]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def approved(measure: dict[str, Any]) -> bool:
    review = measure.get("humanReview", {})
    status = str(review.get("status", "")).lower()
    if status in {"approved", "human-approved", "validated", "source-approved", "source-reviewed"}:
        return True
    events = measure.get("events", [])
    return bool(events) and all(bool(event.get("humanValidated")) for event in events)


def musical_signature(measure: dict[str, Any]) -> str:
    payload = {
        "timeSignature": measure.get("timeSignature"),
        "events": [
            {
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
            for event in measure.get("events", [])
        ],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def main() -> None:
    measures: dict[int, dict[str, Any]] = {}
    total_events = 0
    for path in CHUNKS:
        packet = load(path)
        for measure in packet.get("measures", []):
            number = int(measure["measureNumber"])
            if 17 <= number <= 113:
                if number in measures:
                    raise RuntimeError(f"Duplicate measure {number}")
                measures[number] = measure
                total_events += len(measure.get("events", []))

    expected = set(range(17, 114))
    if set(measures) != expected:
        raise RuntimeError(
            f"Coverage mismatch missing={sorted(expected - set(measures))} extra={sorted(set(measures) - expected)}"
        )

    approved_measures = sorted(number for number, measure in measures.items() if approved(measure))
    unapproved_measures = sorted(expected - set(approved_measures))

    groups: dict[str, list[int]] = defaultdict(list)
    for number, measure in measures.items():
        groups[musical_signature(measure)].append(number)

    repeat_candidates: list[dict[str, Any]] = []
    repeat_candidate_measures: set[int] = set()
    unique_unapproved: list[int] = []
    approved_set = set(approved_measures)

    for signature, numbers in sorted(groups.items(), key=lambda item: min(item[1])):
        numbers = sorted(numbers)
        approved_examples = sorted(set(numbers) & approved_set)
        pending = sorted(set(numbers) - approved_set)
        if pending and approved_examples:
            repeat_candidates.append({
                "signature": signature,
                "measures": numbers,
                "approvedExamples": approved_examples,
                "pendingExactRepeats": pending,
                "automaticApprovalApplied": False,
                "humanConfirmationRequired": True,
            })
            repeat_candidate_measures.update(pending)

    for number in unapproved_measures:
        if number not in repeat_candidate_measures:
            unique_unapproved.append(number)

    result = {
        "schemaVersion": 1,
        "referenceRange": [17, 113],
        "measuresCovered": len(measures),
        "referenceEvents": total_events,
        "humanApprovedMeasures": approved_measures,
        "humanApprovedCount": len(approved_measures),
        "unapprovedMeasures": unapproved_measures,
        "unapprovedCount": len(unapproved_measures),
        "exactRepeatCandidateGroups": repeat_candidates,
        "exactRepeatCandidateMeasures": sorted(repeat_candidate_measures),
        "uniqueUnapprovedMeasures": unique_unapproved,
        "automaticApprovalApplied": False,
        "readyForTraining": len(unapproved_measures) == 0,
        "nextRequiredStage": (
            "confirm-exact-repeat-candidates-then-review-unique-unapproved-measures"
            if unapproved_measures
            else "release-professional-reference-to-training"
        ),
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "GOMYWAY FULL RHYTHM REVIEW AFTER ALL SOURCE RESOLUTION",
        f"Measures covered: {len(measures)} / 97",
        f"Reference events: {total_events}",
        f"Human-approved measures: {len(approved_measures)} / 97",
        f"Unapproved measures: {len(unapproved_measures)}",
        f"Exact-repeat candidate groups: {len(repeat_candidates)}",
        f"Exact-repeat candidate measures: {sorted(repeat_candidate_measures)}",
        f"Unique unapproved measures: {unique_unapproved}",
        "Automatic approval applied: False",
        f"Ready for training: {len(unapproved_measures) == 0}",
        "Protected baselines changed: False",
        "",
    ]
    for item in repeat_candidates:
        lines.append(
            f"REPEAT {item['signature']}: approved={item['approvedExamples']} pending={item['pendingExactRepeats']} all={item['measures']}"
        )
    TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Full rhythm review after all source resolution complete")
    print(f"Measures covered: {len(measures)} / 97")
    print(f"Reference events: {total_events}")
    print(f"Human-approved measures: {len(approved_measures)} / 97")
    print(f"Unapproved measures: {len(unapproved_measures)}")
    print(f"Exact-repeat candidate groups: {len(repeat_candidates)}")
    print(f"Exact-repeat candidate measures: {len(repeat_candidate_measures)}")
    print(f"Unique unapproved measures: {len(unique_unapproved)}")
    print("Automatic approval applied: False")
    print(f"Ready for training: {len(unapproved_measures) == 0}")
    print(f"JSON: {OUTPUT.relative_to(ROOT)}")
    print(f"Text: {TEXT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
