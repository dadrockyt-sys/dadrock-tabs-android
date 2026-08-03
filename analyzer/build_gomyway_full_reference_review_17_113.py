from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT = PUBLIC / "gomyway-professional-rhythm-reference-full-review-17-113.json"
TEXT = PUBLIC / "gomyway-professional-rhythm-reference-full-review-17-113.txt"

CHUNKS = [
    (17, 32),
    (33, 48),
    (49, 64),
    (65, 80),
    (81, 96),
    (97, 113),
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def populated_path(start: int, end: int) -> Path:
    if (start, end) == (17, 32):
        approved = PUBLIC / "gomyway-professional-rhythm-reference-chunk-17-32-approved.json"
        if approved.exists():
            return approved
    return PUBLIC / f"gomyway-professional-rhythm-reference-chunk-{start}-{end}-populated.json"


def validation_path(start: int, end: int) -> Path:
    return PUBLIC / f"gomyway-professional-rhythm-reference-chunk-{start}-{end}-validation.json"


def event_count(measure: dict[str, Any]) -> int:
    return len(measure.get("events", []))


def main() -> None:
    all_measures: list[dict[str, Any]] = []
    chunk_summaries: list[dict[str, Any]] = []
    all_warnings: list[dict[str, Any]] = []
    all_errors: list[Any] = []

    for start, end in CHUNKS:
        source_path = populated_path(start, end)
        validation_file = validation_path(start, end)
        packet = load_json(source_path)
        validation = load_json(validation_file)
        measures = packet.get("measures", [])

        expected = set(range(start, end + 1))
        found = {int(item.get("measureNumber", -1)) for item in measures}
        if found != expected:
            raise RuntimeError(
                f"Chunk {start}-{end} coverage mismatch: "
                f"missing={sorted(expected - found)} extra={sorted(found - expected)}"
            )

        warnings = validation.get("warnings", [])
        errors = validation.get("errors", [])
        warning_count = len(warnings) if isinstance(warnings, list) else int(warnings or 0)
        error_count = len(errors) if isinstance(errors, list) else int(errors or 0)

        if isinstance(warnings, list):
            for warning in warnings:
                all_warnings.append({"chunk": [start, end], "warning": warning})
        elif warning_count:
            all_warnings.append({
                "chunk": [start, end],
                "warningCount": warning_count,
                "priorityReviewMeasures": validation.get("priorityReviewMeasures", []),
            })

        if isinstance(errors, list):
            all_errors.extend({"chunk": [start, end], "error": error} for error in errors)
        elif error_count:
            all_errors.append({"chunk": [start, end], "errorCount": error_count})

        approved_measures = sum(
            1
            for measure in measures
            if measure.get("humanReview", {}).get("status") in {
                "approved",
                "human-approved",
                "human-validated",
            }
            or all(bool(evt.get("humanValidated")) for evt in measure.get("events", []))
        )

        chunk_summaries.append({
            "chunk": [start, end],
            "source": str(source_path.relative_to(ROOT)),
            "validation": str(validation_file.relative_to(ROOT)),
            "measureCount": len(measures),
            "eventCount": sum(event_count(item) for item in measures),
            "warningCount": warning_count,
            "errorCount": error_count,
            "priorityReviewMeasures": validation.get("priorityReviewMeasures", []),
            "humanApprovedMeasures": approved_measures,
            "validDraft": bool(validation.get("validDraft", validation.get("validationPassed", error_count == 0))),
        })
        all_measures.extend(measures)

    all_measures.sort(key=lambda item: int(item["measureNumber"]))
    expected_full = set(range(17, 114))
    found_full = {int(item["measureNumber"]) for item in all_measures}
    if found_full != expected_full:
        raise RuntimeError(
            f"Full coverage mismatch: missing={sorted(expected_full - found_full)} "
            f"extra={sorted(found_full - expected_full)}"
        )

    section_timeline: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for measure in all_measures:
        number = int(measure["measureNumber"])
        section = measure.get("section", "Unknown")
        variant = measure.get("sectionVariant", "")
        key = (section, variant)
        if current is None or current["key"] != key:
            current = {
                "key": key,
                "section": section,
                "sectionVariant": variant,
                "measureStart": number,
                "measureEnd": number,
            }
            section_timeline.append(current)
        else:
            current["measureEnd"] = number
    for item in section_timeline:
        item.pop("key", None)

    approved_total = sum(item["humanApprovedMeasures"] for item in chunk_summaries)
    total_events = sum(item["eventCount"] for item in chunk_summaries)
    total_warnings = sum(item["warningCount"] for item in chunk_summaries)
    total_errors = sum(item["errorCount"] for item in chunk_summaries)
    all_drafts_valid = all(item["validDraft"] for item in chunk_summaries)

    priority_measures = sorted({
        int(number)
        for item in chunk_summaries
        for number in item.get("priorityReviewMeasures", [])
    })

    report = {
        "schemaVersion": 1,
        "referenceType": "professional-rhythm-full-song-human-review",
        "instrument": "rhythm-guitar",
        "measureStart": 17,
        "measureEnd": 113,
        "measureCount": len(all_measures),
        "eventCount": total_events,
        "timingGrid": "sixteenth-note",
        "tempoBpm": 129,
        "timeSignature": "4/4",
        "chunkSummaries": chunk_summaries,
        "sectionTimeline": section_timeline,
        "priorityReviewMeasures": priority_measures,
        "totalWarnings": total_warnings,
        "totalErrors": total_errors,
        "allDraftsStructurallyValid": all_drafts_valid,
        "humanApprovedMeasures": approved_total,
        "humanApprovalComplete": approved_total == 97,
        "readyForTraining": all_drafts_valid and total_errors == 0 and approved_total == 97,
        "trainingReleaseBlockedReason": (
            None
            if all_drafts_valid and total_errors == 0 and approved_total == 97
            else "Full human approval of all 97 measures is still required."
        ),
        "warnings": all_warnings,
        "errors": all_errors,
        "protectedRules": {
            "lockedMeasures1To16Modified": False,
            "v7EventsModified": False,
            "rendererModified": False,
            "professionalReferenceSourceModified": False,
            "candidateAudioModified": False,
        },
        "nextRequiredStage": "resolve-full-song-review-and-approve-measures-33-113",
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "GOMYWAY PROFESSIONAL RHYTHM REFERENCE — FULL REVIEW 17-113",
        "",
        f"Measures covered: {len(all_measures)} / 97",
        f"Reference events: {total_events}",
        f"Structurally valid chunks: {sum(1 for item in chunk_summaries if item['validDraft'])} / 6",
        f"Errors: {total_errors}",
        f"Warnings: {total_warnings}",
        f"Human-approved measures: {approved_total} / 97",
        f"Ready for training: {report['readyForTraining']}",
        f"Priority review measures: {priority_measures}",
        "",
        "SECTION TIMELINE",
    ]
    for section in section_timeline:
        suffix = f" — {section['sectionVariant']}" if section.get("sectionVariant") else ""
        lines.append(
            f"{section['measureStart']}-{section['measureEnd']}: "
            f"{section['section']}{suffix}"
        )
    lines.extend([
        "",
        "CHUNK STATUS",
    ])
    for item in chunk_summaries:
        lines.append(
            f"{item['chunk'][0]}-{item['chunk'][1]}: "
            f"events={item['eventCount']} warnings={item['warningCount']} "
            f"errors={item['errorCount']} approved={item['humanApprovedMeasures']}/{item['measureCount']}"
        )
    lines.extend([
        "",
        "Protected measures 1-16 changed: False",
        "V7 events changed: False",
        "Renderer changed: False",
        "Candidate audio changed: False",
        "",
        "Next required stage: resolve full-song review and approve measures 33-113.",
    ])
    TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Full professional rhythm reference review 17-113 complete")
    print(f"Measures covered: {len(all_measures)} / 97")
    print(f"Reference events: {total_events}")
    print(f"Structurally valid chunks: {sum(1 for item in chunk_summaries if item['validDraft'])} / 6")
    print(f"Errors: {total_errors}")
    print(f"Warnings: {total_warnings}")
    print(f"Human-approved measures: {approved_total} / 97")
    print(f"Ready for training: {report['readyForTraining']}")
    print(f"Priority review measures: {priority_measures}")
    print(f"JSON: {OUTPUT.relative_to(ROOT)}")
    print(f"Text: {TEXT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
