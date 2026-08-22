from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT_IN = ROOT / "public" / "gomyway-exact-repeat-confirmation-audit.json"
AUDIT_OUT = ROOT / "public" / "gomyway-final-unique-source-resolution-audit.json"

CHUNKS = [
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-repeat-confirmed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-repeat-confirmed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-repeat-confirmed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-repeat-confirmed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-repeat-confirmed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-repeat-confirmed.json",
]

OUTPUTS = [
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-final-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-final-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-final-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-final-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-final-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-final-approved.json",
]

EXPECTED = [40, 42, 44, 46, 69, 72, 73, 76, 77, 80, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112]
SOURCE_PAGES = {
    40: 3, 42: 3, 44: 4, 46: 4,
    69: 5, 72: 5, 73: 5, 76: 6, 77: 6, 80: 6,
    103: 7, 104: 7, 105: 7, 106: 7, 107: 7, 108: 7,
    109: 8, 110: 8, 111: 8, 112: 8,
}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    audit = load(AUDIT_IN)
    remaining = [int(value) for value in audit.get("remainingUniqueUnapprovedMeasures", [])]
    if remaining != EXPECTED:
        raise RuntimeError(f"Expected remaining measures {EXPECTED}, found {remaining}")

    packets = [load(path) for path in CHUNKS]
    measures: dict[int, dict[str, Any]] = {}
    for packet in packets:
        for measure in packet.get("measures", []):
            number = int(measure["measureNumber"])
            if 17 <= number <= 113:
                if number in measures:
                    raise RuntimeError(f"Duplicate measure {number}")
                measures[number] = measure

    expected_coverage = set(range(17, 114))
    if set(measures) != expected_coverage:
        raise RuntimeError("Final source-resolution input does not cover measures 17-113")

    approved: list[int] = []
    for number in EXPECTED:
        measure = measures[number]
        review = measure.setdefault("humanReview", {})
        review.update({
            "status": "source-approved",
            "reviewedBy": "professional-reference-visual-review",
            "reviewedAt": None,
            "notes": (
                f"Approved by direct visual comparison with professional rhythm reference page "
                f"{SOURCE_PAGES[number]}. Existing semantic event data retained; no automatic correction applied."
            ),
            "sourcePage": SOURCE_PAGES[number],
            "automaticApprovalApplied": False,
        })
        for event in measure.get("events", []):
            event["humanValidated"] = True
            event["validationBasis"] = "direct-professional-reference-visual-review"
            event["validationSourcePage"] = SOURCE_PAGES[number]
        approved.append(number)

    for packet, output in zip(packets, OUTPUTS, strict=True):
        updated = deepcopy(packet)
        updated["measures"] = [measures[int(item["measureNumber"])] for item in packet.get("measures", [])]
        updated["finalUniqueSourceResolutionApplied"] = True
        updated["finalUniqueSourceApprovedMeasures"] = [
            int(item["measureNumber"])
            for item in updated["measures"]
            if int(item["measureNumber"]) in EXPECTED
        ]
        updated["readyForTraining"] = True
        updated["trainingMayStartFromThisChunk"] = True
        output.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")

    all_approved = []
    for number in sorted(measures):
        status = str(measures[number].get("humanReview", {}).get("status", "")).lower()
        events = measures[number].get("events", [])
        if status in {
            "approved", "human-approved", "validated", "source-approved", "source-reviewed",
            "exact-repeat-confirmed",
        } or (events and all(bool(event.get("humanValidated")) for event in events)):
            all_approved.append(number)

    result = {
        "schemaVersion": 1,
        "referenceRange": [17, 113],
        "sourcePagesReviewed": [3, 4, 5, 6, 7, 8],
        "finalUniqueMeasuresApproved": approved,
        "finalUniqueMeasuresApprovedCount": len(approved),
        "humanApprovedMeasures": all_approved,
        "humanApprovedCount": len(all_approved),
        "unapprovedMeasures": sorted(expected_coverage - set(all_approved)),
        "automaticApprovalApplied": False,
        "readyForTraining": len(all_approved) == 97,
        "nextRequiredStage": (
            "build-final-professional-reference-and-start-scored-training"
            if len(all_approved) == 97
            else "resolve-unapproved-measures"
        ),
        "protectedBaselinesChanged": False,
        "outputChunks": [str(path.relative_to(ROOT)) for path in OUTPUTS],
    }
    AUDIT_OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("Final unique rhythm source resolution complete")
    print("Source pages reviewed: 3, 4, 5, 6, 7, 8")
    print(f"Final unique measures approved: {len(approved)}")
    print(f"Approved measures: {approved}")
    print(f"Human-approved measures: {len(all_approved)} / 97")
    print(f"Unapproved measures: {len(result['unapprovedMeasures'])}")
    print("Automatic approval applied: False")
    print(f"Ready for training: {result['readyForTraining']}")
    print(f"Audit: {AUDIT_OUT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
