from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONSENSUS = ROOT / "public" / "gomyway-professional-rhythm-reference-consensus-candidates-17-113.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-manual-review-31-measures.json"
TEXT = ROOT / "public" / "gomyway-professional-rhythm-reference-manual-review-31-measures.txt"

CHUNKS = [
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


def source_page(measure: dict[str, Any]) -> int | None:
    source = measure.get("source", {})
    for key in ("page", "pageNumber", "sourcePage"):
        if key in source:
            try:
                return int(source[key])
            except (TypeError, ValueError):
                pass
    return None


def compact_event(index: int, event: dict[str, Any]) -> dict[str, Any]:
    return {
        "eventIndex": index,
        "quantizedStep": event.get("quantizedStep"),
        "durationSteps": event.get("durationSteps"),
        "notes": event.get("notes", []),
        "techniques": event.get("techniques", []),
        "referenceConfidence": event.get("referenceConfidence"),
        "humanValidated": bool(event.get("humanValidated", False)),
    }


def main() -> None:
    consensus = load(CONSENSUS)
    manual_numbers = sorted(int(item) for item in consensus.get("manualOnlyMeasures", []))
    if len(manual_numbers) != 31:
        raise RuntimeError(f"Expected 31 manual-only measures, found {len(manual_numbers)}: {manual_numbers}")

    measures: dict[int, dict[str, Any]] = {}
    for path in CHUNKS:
        packet = load(path)
        for measure in packet.get("measures", []):
            number = int(measure["measureNumber"])
            if number in manual_numbers:
                measures[number] = measure

    missing = sorted(set(manual_numbers) - set(measures))
    if missing:
        raise RuntimeError(f"Missing manual-review measures: {missing}")

    entries: list[dict[str, Any]] = []
    total_low_confidence_events = 0
    for number in manual_numbers:
        measure = measures[number]
        all_events = measure.get("events", [])
        flagged = [
            compact_event(index, event)
            for index, event in enumerate(all_events)
            if float(event.get("referenceConfidence", 0.0)) < 0.85
        ]
        total_low_confidence_events += len(flagged)
        entries.append({
            "measureNumber": number,
            "section": measure.get("section"),
            "sectionVariant": measure.get("sectionVariant"),
            "sourcePage": source_page(measure),
            "timeSignature": measure.get("timeSignature"),
            "tempoBpm": measure.get("tempoBpm"),
            "eventCount": len(all_events),
            "flaggedEventCount": len(flagged),
            "flaggedEvents": flagged,
            "fullEvents": [compact_event(index, event) for index, event in enumerate(all_events)],
            "reviewDecision": None,
            "reviewNotes": "",
            "approved": False,
        })

    by_section: dict[str, list[int]] = {}
    by_page: dict[str, list[int]] = {}
    for entry in entries:
        section = str(entry.get("section") or "Unknown")
        page = str(entry.get("sourcePage") or "Unknown")
        by_section.setdefault(section, []).append(entry["measureNumber"])
        by_page.setdefault(page, []).append(entry["measureNumber"])

    result = {
        "schemaVersion": 1,
        "referenceRange": [17, 113],
        "manualReviewMeasureCount": len(entries),
        "manualReviewMeasures": manual_numbers,
        "lowConfidenceEventCount": total_low_confidence_events,
        "groupedBySection": by_section,
        "groupedBySourcePage": by_page,
        "measures": entries,
        "automaticApprovalApplied": False,
        "readyForTraining": False,
        "requiredDecisionValues": ["approve-as-written", "correct-and-approve", "reject-and-retranscribe"],
        "nextRequiredStage": "human-review-31-measures-against-professional-pdf",
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "GOMYWAY PROFESSIONAL RHYTHM MANUAL REVIEW — 31 MEASURES",
        f"Measures: {manual_numbers}",
        f"Low-confidence events: {total_low_confidence_events}",
        f"Grouped by section: {by_section}",
        f"Grouped by source page: {by_page}",
        "Automatic approval applied: False",
        "Ready for training: False",
        "Protected baselines changed: False",
        "",
    ]
    for entry in entries:
        lines.append(
            f"MEASURE {entry['measureNumber']} | section={entry['section']} | "
            f"page={entry['sourcePage']} | events={entry['eventCount']} | "
            f"flagged={entry['flaggedEventCount']}"
        )
        for event in entry["flaggedEvents"]:
            lines.append(
                f"  event={event['eventIndex']} step={event['quantizedStep']} "
                f"duration={event['durationSteps']} notes={event['notes']} "
                f"techniques={event['techniques']} confidence={event['referenceConfidence']}"
            )
        lines.append("  decision: ____________________")
        lines.append("  notes: _______________________")
        lines.append("")
    TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Professional rhythm manual review packet complete")
    print(f"Manual-review measures: {len(entries)}")
    print(f"Low-confidence events: {total_low_confidence_events}")
    print(f"Sections represented: {len(by_section)}")
    print(f"Source pages represented: {len(by_page)}")
    print("Automatic approval applied: False")
    print("Ready for training: False")
    print(f"JSON: {OUTPUT.relative_to(ROOT)}")
    print(f"Text: {TEXT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
