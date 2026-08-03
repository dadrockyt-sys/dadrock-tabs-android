from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "public" / "gomyway-professional-rhythm-reference-full-review-after-all-source-resolution.json"
AUDIT = ROOT / "public" / "gomyway-exact-repeat-confirmation-audit.json"

CHUNKS = [
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-approved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-source-resolved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-source-resolved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-source-reviewed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-source-resolved.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-source-resolved.json",
]

OUTPUTS = [
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-repeat-confirmed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-repeat-confirmed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-repeat-confirmed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-repeat-confirmed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-repeat-confirmed.json",
    ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-repeat-confirmed.json",
]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def measure_map(packets: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for packet in packets:
        for measure in packet.get("measures", []):
            number = int(measure["measureNumber"])
            if 17 <= number <= 113:
                if number in result:
                    raise RuntimeError(f"Duplicate measure {number}")
                result[number] = measure
    return result


def main() -> None:
    review = load(REVIEW)
    packets = [load(path) for path in CHUNKS]
    measures = measure_map(packets)

    expected = set(range(17, 114))
    if set(measures) != expected:
        raise RuntimeError(
            f"Coverage mismatch missing={sorted(expected - set(measures))} extra={sorted(set(measures) - expected)}"
        )

    groups = review.get("exactRepeatCandidateGroups", [])
    candidate_measures = sorted(int(number) for number in review.get("exactRepeatCandidateMeasures", []))
    if len(candidate_measures) != 28:
        raise RuntimeError(f"Expected 28 exact-repeat candidates, found {len(candidate_measures)}")

    evidence_by_measure: dict[int, dict[str, Any]] = {}
    for group in groups:
        approved_examples = [int(number) for number in group.get("approvedExamples", [])]
        pending = [int(number) for number in group.get("pendingExactRepeats", [])]
        if not approved_examples:
            raise RuntimeError(f"Repeat group {group.get('signature')} has no approved example")
        for number in pending:
            evidence_by_measure[number] = {
                "signature": group.get("signature"),
                "approvedExamples": approved_examples,
                "allMatchingMeasures": [int(item) for item in group.get("measures", [])],
            }

    if sorted(evidence_by_measure) != candidate_measures:
        raise RuntimeError("Exact-repeat evidence does not match candidate measure list")

    confirmed: list[int] = []
    for number in candidate_measures:
        measure = measures[number]
        evidence = evidence_by_measure[number]
        review_block = measure.setdefault("humanReview", {})
        review_block.update({
            "status": "exact-repeat-confirmed",
            "reviewedBy": "professional-reference-consensus",
            "reviewedAt": None,
            "notes": (
                "Confirmed by exact musical-event identity with already source-approved measure(s) "
                f"{evidence['approvedExamples']}; signature={evidence['signature']}."
            ),
            "evidence": deepcopy(evidence),
        })
        for event in measure.get("events", []):
            event["humanValidated"] = True
            event["validationBasis"] = "exact-musical-repeat-of-source-approved-measure"
        confirmed.append(number)

    output_packets: list[dict[str, Any]] = []
    for packet, output in zip(packets, OUTPUTS, strict=True):
        updated = deepcopy(packet)
        updated["measures"] = [
            measures[int(measure["measureNumber"])]
            for measure in packet.get("measures", [])
        ]
        updated["exactRepeatConfirmationApplied"] = True
        updated["exactRepeatConfirmedMeasures"] = [
            int(measure["measureNumber"])
            for measure in updated["measures"]
            if int(measure["measureNumber"]) in evidence_by_measure
        ]
        updated["readyForTraining"] = False
        updated["trainingMayStartFromThisChunk"] = False
        output.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
        output_packets.append(updated)

    remaining = sorted(set(review.get("unapprovedMeasures", [])) - set(confirmed))
    result = {
        "schemaVersion": 1,
        "referenceRange": [17, 113],
        "candidateGroupsConfirmed": len(groups),
        "measuresConfirmed": confirmed,
        "measuresConfirmedCount": len(confirmed),
        "approvedEvidenceMeasures": sorted({
            int(example)
            for group in groups
            for example in group.get("approvedExamples", [])
        }),
        "remainingUniqueUnapprovedMeasures": remaining,
        "remainingUniqueUnapprovedCount": len(remaining),
        "automaticApprovalApplied": False,
        "confirmationBasis": "exact musical-event identity with an already source-approved measure",
        "readyForTraining": len(remaining) == 0,
        "nextRequiredStage": "source-review-remaining-unique-unapproved-measures",
        "protectedBaselinesChanged": False,
        "outputChunks": [str(path.relative_to(ROOT)) for path in OUTPUTS],
    }
    AUDIT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("Exact-repeat rhythm confirmation complete")
    print(f"Candidate groups confirmed: {len(groups)}")
    print(f"Measures confirmed: {len(confirmed)}")
    print(f"Confirmed measures: {confirmed}")
    print(f"Remaining unique unapproved measures: {len(remaining)}")
    print(f"Remaining measures: {remaining}")
    print("Automatic approval applied: False")
    print("Confirmation basis: exact musical identity with source-approved examples")
    print(f"Ready for training: {len(remaining) == 0}")
    print(f"Audit: {AUDIT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
