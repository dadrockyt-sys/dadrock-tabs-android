from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-full-review-after-chorus-resolution.json"
TEXT = ROOT / "public" / "gomyway-professional-rhythm-reference-full-review-after-chorus-resolution.txt"

CHUNKS = [
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-source-resolved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-source-resolved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-source-resolved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-populated.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-populated.json",
]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def approved(measure: dict[str, Any]) -> bool:
    review = measure.get("humanReview", {})
    status = str(review.get("status", "")).lower()
    if status in {"approved", "human-approved", "validated", "source-resolved-approved"}:
        return True
    events = measure.get("events", [])
    return bool(events) and all(bool(event.get("humanValidated")) for event in events)


def warning_measure(measure: dict[str, Any]) -> bool:
    if approved(measure):
        return False
    return any(float(event.get("referenceConfidence", 1.0)) < 0.85 for event in measure.get("events", []))


def main() -> None:
    measures: dict[int, dict[str, Any]] = {}
    chunk_summaries: list[dict[str, Any]] = []
    for path in CHUNKS:
        packet = load(path)
        packet_measures = packet.get("measures", [])
        chunk_summaries.append({
            "path": str(path.relative_to(ROOT)),
            "measureCount": len(packet_measures),
            "readyForTraining": bool(packet.get("readyForTraining", False)),
        })
        for measure in packet_measures:
            number = int(measure["measureNumber"])
            if 17 <= number <= 113:
                measures[number] = measure

    expected = set(range(17, 114))
    missing = sorted(expected - set(measures))
    extra = sorted(set(measures) - expected)
    if missing or extra:
        raise RuntimeError(f"Coverage mismatch missing={missing} extra={extra}")

    approved_measures = sorted(number for number, measure in measures.items() if approved(measure))
    remaining_review = sorted(number for number, measure in measures.items() if warning_measure(measure))
    total_events = sum(len(measure.get("events", [])) for measure in measures.values())
    sections: dict[str, list[int]] = {}
    for number, measure in measures.items():
        section = str(measure.get("section", "Unknown"))
        sections.setdefault(section, []).append(number)

    result = {
        "schemaVersion": 1,
        "referenceRange": [17, 113],
        "measuresCovered": len(measures),
        "referenceEvents": total_events,
        "humanApprovedMeasures": approved_measures,
        "humanApprovedMeasureCount": len(approved_measures),
        "remainingPriorityReviewMeasures": remaining_review,
        "remainingPriorityReviewMeasureCount": len(remaining_review),
        "sections": {key: sorted(value) for key, value in sorted(sections.items())},
        "chunks": chunk_summaries,
        "chorusSourceResolutionApplied": True,
        "readyForTraining": len(approved_measures) == 97 and not remaining_review,
        "nextRequiredStage": (
            "review-remaining-source-grounded-measures"
            if remaining_review
            else "release-professional-reference-to-training-loop"
        ),
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "GOMYWAY FULL RHYTHM REVIEW AFTER CHORUS SOURCE RESOLUTION",
        f"Measures covered: {len(measures)} / 97",
        f"Reference events: {total_events}",
        f"Human-approved measures: {len(approved_measures)} / 97",
        f"Remaining priority review measures: {len(remaining_review)}",
        f"Remaining measures: {remaining_review}",
        "Chorus source resolution applied: True",
        f"Ready for training: {result['readyForTraining']}",
        "Protected baselines changed: False",
    ]
    TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Full rhythm review after chorus source resolution complete")
    print(f"Measures covered: {len(measures)} / 97")
    print(f"Reference events: {total_events}")
    print(f"Human-approved measures: {len(approved_measures)} / 97")
    print(f"Remaining priority review measures: {len(remaining_review)}")
    print(f"Remaining measures: {remaining_review}")
    print("Chorus source resolution applied: True")
    print(f"Ready for training: {result['readyForTraining']}")
    print(f"JSON: {OUTPUT.relative_to(ROOT)}")
    print(f"Text: {TEXT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
