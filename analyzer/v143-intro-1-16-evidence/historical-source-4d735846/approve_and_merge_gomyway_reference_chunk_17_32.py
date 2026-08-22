from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POPULATED = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-populated.json"
VALIDATION = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-validation.json"
FULL_REFERENCE = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
APPROVED_CHUNK = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-approved.json"
MERGE_AUDIT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-merge-audit.json"

START = 17
END = 32


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict[str, Any]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def main() -> None:
    chunk = load(POPULATED)
    validation = load(VALIDATION)
    full = load(FULL_REFERENCE)

    if validation.get("validDraft") is not True:
        raise RuntimeError("Cannot approve: structural validation did not pass")
    if int(validation.get("errorCount", 0)) != 0:
        raise RuntimeError("Cannot approve: validation contains errors")

    measures = {int(item["measureNumber"]): item for item in chunk.get("measures", [])}
    expected = set(range(START, END + 1))
    if set(measures) != expected:
        raise RuntimeError("Approved chunk does not contain exactly measures 17-32")

    # User-confirmed interpretation: measure 28 step 6 is a muted grace/rake
    # attached to the following fretted-3 attack rather than a standalone note.
    m28 = measures[28]
    events = list(m28.get("events", []))
    target_index = next(
        (index for index, event in enumerate(events) if int(event.get("quantizedStep", -1)) == 6),
        None,
    )
    if target_index is None:
        raise RuntimeError("Cannot find measure 28 step-6 event")
    target = events[target_index]
    target["techniques"] = ["muted-grace-rake", "downstroke"]
    target["referenceConfidence"] = 0.95
    target["interpretationLocked"] = True
    target["interpretationNote"] = (
        "User-approved professional-reference interpretation: muted grace/rake into fret 3."
    )
    target["humanValidated"] = True
    m28["events"] = events

    approved_at = datetime.now(timezone.utc).isoformat()
    for number in range(START, END + 1):
        measure = measures[number]
        for event in measure.get("events", []):
            event["humanValidated"] = True
        measure["humanReview"] = {
            "status": "approved",
            "reviewedBy": "user-and-assistant",
            "reviewedAt": approved_at,
            "notes": (
                "Approved against the uploaded professional rhythm reference. "
                "Measure 28 step 6 locked as muted grace/rake into fret 3."
            ),
        }

    chunk["measures"] = [measures[number] for number in range(START, END + 1)]
    chunk["readyForTraining"] = True
    chunk["trainingMayStartFromThisChunk"] = True
    chunk["humanValidationRequired"] = False
    chunk["humanApprovedMeasureCount"] = 16
    chunk["approvedAt"] = approved_at
    write(APPROVED_CHUNK, chunk)

    full_measures = {
        int(item["measureNumber"]): item
        for item in full.get("measures", [])
    }
    for number in range(START, END + 1):
        full_measures[number] = measures[number]
    full["measures"] = [full_measures[number] for number in sorted(full_measures)]
    full["approvedMeasureRanges"] = sorted(
        {tuple(item) for item in full.get("approvedMeasureRanges", [])} | {(START, END)}
    )
    full["humanValidatedMeasureCount"] = sum(
        1
        for item in full["measures"]
        if (item.get("humanReview") or {}).get("status") == "approved"
    )
    full["readyForTraining"] = full["humanValidatedMeasureCount"] == 97
    full["lastMergedChunk"] = [START, END]
    full["updatedAt"] = approved_at
    write(FULL_REFERENCE, full)

    audit = {
        "approvedChunk": [START, END],
        "measuresApproved": 16,
        "eventsApproved": sum(len(item.get("events", [])) for item in chunk["measures"]),
        "measure28Step6Interpretation": "muted-grace-rake-into-fret-3",
        "fullReferenceHumanValidatedMeasures": full["humanValidatedMeasureCount"],
        "fullReferenceReadyForTraining": full["readyForTraining"],
        "nextRequiredChunk": [33, 48],
        "lockedMeasures1To16Modified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "candidateAudioModified": False,
        "professionalReferenceSourceModified": False,
    }
    write(MERGE_AUDIT, audit)

    print("Professional rhythm reference chunk 17-32 approved and merged")
    print("Measures approved: 16")
    print("Events approved:", audit["eventsApproved"])
    print("Measure 28 step 6: muted grace/rake into fret 3")
    print("Full reference human validated measures:", full["humanValidatedMeasureCount"])
    print("Full reference ready for training:", full["readyForTraining"])
    print("Next required chunk: 33-48")
    print("Protected baselines changed: False")
    print("Approved chunk:", APPROVED_CHUNK.relative_to(ROOT))
    print("Merged reference:", FULL_REFERENCE.relative_to(ROOT))
    print("Audit:", MERGE_AUDIT.relative_to(ROOT))


if __name__ == "__main__":
    main()
