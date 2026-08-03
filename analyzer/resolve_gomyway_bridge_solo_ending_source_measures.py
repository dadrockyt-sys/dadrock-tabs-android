from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

INPUTS = {
    "65-80": ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-source-resolved.json",
    "81-96": ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-populated.json",
    "97-113": ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-populated.json",
}

OUTPUTS = {
    "65-80": ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-source-reviewed.json",
    "81-96": ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-source-resolved.json",
    "97-113": ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-source-resolved.json",
}

AUDIT = ROOT / "public" / "gomyway-bridge-solo-ending-source-resolution-audit.json"

SOURCE_APPROVED = {
    70: {"page": 5, "reason": "Bridge D chord/dead-note pattern visibly confirmed."},
    71: {"page": 5, "reason": "Bridge A chord movement visibly confirmed."},
    74: {"page": 5, "reason": "Repeated Bridge D chord/dead-note pattern visibly confirmed."},
    75: {"page": 6, "reason": "Repeated Bridge A chord movement visibly confirmed."},
    78: {"page": 6, "reason": "Solo backing D chord/dead-note pattern visibly confirmed."},
    79: {"page": 6, "reason": "Solo backing A-D6-A movement visibly confirmed."},
    81: {"page": 6, "reason": "Repeated solo backing D pattern visibly confirmed."},
    82: {"page": 6, "reason": "Repeated solo backing E pattern visibly confirmed."},
    83: {"page": 6, "reason": "Repeated solo backing A-D6-A movement visibly confirmed."},
    84: {"page": 6, "reason": "Repeated solo backing E pattern visibly confirmed."},
    85: {"page": 6, "reason": "Repeated solo backing D pattern visibly confirmed."},
    86: {"page": 6, "reason": "Repeated solo backing A-D6-A movement visibly confirmed."},
    87: {"page": 6, "reason": "Repeated solo backing E pattern visibly confirmed."},
    88: {"page": 6, "reason": "Repeated solo backing D pattern visibly confirmed."},
    89: {"page": 6, "reason": "Repeated solo backing A-D6-A movement visibly confirmed."},
    90: {"page": 6, "reason": "Repeated solo backing E pattern visibly confirmed."},
    91: {"page": 7, "reason": "Final repeated solo backing D pattern visibly confirmed."},
    92: {"page": 7, "reason": "Solo-ending E chord attacks visibly confirmed."},
    93: {"page": 7, "reason": "Tied sustained chord across the solo-ending transition visibly confirmed."},
    94: {"page": 7, "reason": "Short single-note transition run into the returning Em riff visibly confirmed."},
    113: {"page": 8, "reason": "Final sustained A(add2) resolution and stop visibly confirmed."},
}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def approve_measure(measure: dict[str, Any], page: int, reason: str, reviewed_at: str) -> None:
    for event in measure.get("events", []):
        event["humanValidated"] = True
        event["sourceReviewPage"] = page

    measure["humanReview"] = {
        "status": "approved",
        "reviewedBy": "human-assisted-professional-source-review",
        "reviewedAt": reviewed_at,
        "notes": reason,
        "sourcePage": page,
        "professionalReferenceUsedForScoringOnly": True,
    }
    flags = measure.setdefault("measureFlags", {})
    flags["sourceResolved"] = True
    flags["humanApproved"] = True


def main() -> None:
    packets = {name: load(path) for name, path in INPUTS.items()}
    measure_locations: dict[int, tuple[str, dict[str, Any]]] = {}

    for chunk_name, packet in packets.items():
        for measure in packet.get("measures", []):
            number = int(measure["measureNumber"])
            measure_locations[number] = (chunk_name, measure)

    missing = sorted(set(SOURCE_APPROVED) - set(measure_locations))
    if missing:
        raise RuntimeError(f"Missing source-review measures: {missing}")

    reviewed_at = datetime.now(timezone.utc).isoformat()
    approved_by_chunk: dict[str, list[int]] = {name: [] for name in packets}

    for number, source in sorted(SOURCE_APPROVED.items()):
        chunk_name, measure = measure_locations[number]
        approve_measure(measure, source["page"], source["reason"], reviewed_at)
        approved_by_chunk[chunk_name].append(number)

    for chunk_name, packet in packets.items():
        approved_numbers = sorted(approved_by_chunk[chunk_name])
        packet["sourceResolutionApplied"] = True
        packet["sourceResolutionPages"] = sorted(
            {SOURCE_APPROVED[number]["page"] for number in approved_numbers}
        )
        packet["sourceApprovedMeasuresThisStage"] = approved_numbers
        packet["readyForTraining"] = False
        packet["trainingMayStartFromThisChunk"] = False
        packet["protectedBaselinesChanged"] = False
        OUTPUTS[chunk_name].write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    audit = {
        "schemaVersion": 1,
        "stage": "bridge-solo-ending-professional-source-resolution",
        "sourcePagesReviewed": [5, 6, 7, 8],
        "measuresApproved": sorted(SOURCE_APPROVED),
        "approvedMeasureCount": len(SOURCE_APPROVED),
        "approvedByChunk": approved_by_chunk,
        "decisions": [
            {
                "measureNumber": number,
                "sourcePage": source["page"],
                "decision": "approve-as-notated-in-current-source-derived-draft",
                "reason": source["reason"],
            }
            for number, source in sorted(SOURCE_APPROVED.items())
        ],
        "automaticApprovalApplied": False,
        "humanSourceReviewApplied": True,
        "readyForTraining": False,
        "nextRequiredStage": "rebuild-full-review-after-bridge-solo-ending-resolution",
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Bridge, solo, and ending source resolution complete")
    print("Source pages reviewed: 5, 6, 7, 8")
    print("Measures approved:", len(SOURCE_APPROVED))
    print("Approved measures:", sorted(SOURCE_APPROVED))
    print("Human source review applied: True")
    print("Automatic approval applied: False")
    print("Ready for training: False")
    for chunk_name, output in OUTPUTS.items():
        print(f"Output {chunk_name}:", output.relative_to(ROOT))
    print("Audit:", AUDIT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
