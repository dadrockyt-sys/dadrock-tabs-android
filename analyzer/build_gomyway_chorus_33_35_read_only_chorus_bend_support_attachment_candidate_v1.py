from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
EVENT_LOCAL_PROOF_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-event-local-audio-proof-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-attachment-candidate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-attachment-candidate-v1-manifest.json"


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def row_key(row: dict[str, Any]) -> tuple[int, int, int]:
    return (
        int(row.get("measureNumber") or -1),
        int(row.get("quantizedStep") or -1),
        int(row.get("sourceEventIndex") or -1),
    )


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    proof = load(EVENT_LOCAL_PROOF_PATH)
    protected_rows = source_rows(source)

    if len(protected_rows) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if proof.get("passed") is not True:
        raise RuntimeError("Event-local bend audio proof is not green.")
    if proof.get("readyForReadOnlyChorusBendSupportAttachmentCandidate") is not True:
        raise RuntimeError("Event-local proof did not authorize attachment candidate.")
    if proof.get("recommendedNextAction") != (
        "build-read-only-chorus-bend-support-attachment-candidate-v1"
    ):
        raise RuntimeError("Unexpected event-local proof recommendation.")

    proof_rows = [row for row in proof.get("rows", []) if isinstance(row, dict)]
    expected_count = int(proof.get("eventLocalProofRowCount", -1))
    proof_count_matches = len(proof_rows) == expected_count == 3

    attachment_rows: list[dict[str, Any]] = []
    duplicate_keys: set[tuple[int, int, int]] = set()
    seen: set[tuple[int, int, int]] = set()
    invalid_source_indexes = 0
    proof_gate_failures = 0

    for row in proof_rows:
        key = row_key(row)
        if key in seen:
            duplicate_keys.add(key)
        seen.add(key)

        source_index = int(row.get("sourceEventIndex") or -1)
        source_index_valid = 0 <= source_index < len(protected_rows)
        if not source_index_valid:
            invalid_source_indexes += 1

        event_local_gate = row.get("eventLocalBendAudioProofGate") is True
        if not event_local_gate:
            proof_gate_failures += 1

        attachment_gate = bool(
            source_index_valid
            and event_local_gate
            and row.get("bendEvidenceGate") is True
            and row.get("vibratoEvidenceGate") is False
            and row.get("evidenceClass") == "bend-evidence-candidate"
        )

        attachment_rows.append({
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": source_index,
            "sourceEventIndexValid": source_index_valid,
            "eventLocalBendAudioProofGate": event_local_gate,
            "proposedTechniqueFamily": "bend",
            "proposedAttachmentType": "read-only-audio-supported-technique-candidate",
            "proposedTechniqueMetadata": {
                "technique": "bend",
                "supportScope": "chorus-measures-33-35-event-local-audio",
                "supportStatus": "candidate-only",
                "professionalReferenceRole": "part-level-training-label-only",
            },
            "attachmentCandidateGate": attachment_gate,
            "eventTechniqueLabelApplied": False,
            "sourceEventModified": False,
            "readOnly": True,
        })

    all_attachment_gates_passed = bool(
        len(attachment_rows) == 3
        and all(row.get("attachmentCandidateGate") is True for row in attachment_rows)
    )
    no_mutation_requests = all(
        row.get("eventTechniqueLabelApplied") is False
        and row.get("sourceEventModified") is False
        and row.get("readOnly") is True
        for row in attachment_rows
    )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and proof_count_matches
        and not duplicate_keys
        and invalid_source_indexes == 0
        and proof_gate_failures == 0
        and all_attachment_gates_passed
        and no_mutation_requests
    )

    recommended = (
        "build-read-only-chorus-bend-support-attachment-proof-v1"
        if passed
        else "diagnose-read-only-chorus-bend-support-attachment-candidate-failures-v1"
    )

    output = {
        "schemaVersion": 1,
        "candidateType": "read-only-chorus-bend-support-attachment-candidate",
        "passed": passed,
        "eventLocalProofRowCount": len(proof_rows),
        "eventLocalProofRowCountMatches": proof_count_matches,
        "attachmentCandidateCount": len(attachment_rows),
        "duplicateAttachmentKeyCount": len(duplicate_keys),
        "invalidSourceEventIndexCount": invalid_source_indexes,
        "eventLocalProofGateFailureCount": proof_gate_failures,
        "allAttachmentCandidateGatesPassed": all_attachment_gates_passed,
        "noMutationRequests": no_mutation_requests,
        "rows": attachment_rows,
        "readyForReadOnlyChorusBendSupportAttachmentProof": passed,
        "recommendedNextAction": recommended,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalEventLocalLabelsAvailable": False,
        "eventTechniqueLabelsApplied": False,
        "bendSupportClaimed": False,
        "vibratoSupportClaimed": False,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceEventCount": 949,
        "protectedSourceHashBefore": source_hash_before,
        "protectedSourceHashAfter": source_hash_after,
        "protectedSourceHashUnchanged": source_unchanged,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "attachmentCandidateCount": len(attachment_rows),
        "allAttachmentCandidateGatesPassed": all_attachment_gates_passed,
        "readyForReadOnlyChorusBendSupportAttachmentProof": passed,
        "recommendedNextAction": recommended,
        "eventTechniqueLabelsApplied": False,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 READ-ONLY CHORUS BEND SUPPORT ATTACHMENT CANDIDATE V1 COMPLETE")
    print("Passed:", passed)
    print("Event-local proof rows:", len(proof_rows))
    print("Event-local proof row count matches:", proof_count_matches)
    print("Attachment candidates:", len(attachment_rows))
    print("Duplicate attachment keys:", len(duplicate_keys))
    print("Invalid source event indexes:", invalid_source_indexes)
    print("Event-local proof gate failures:", proof_gate_failures)
    print("All attachment candidate gates passed:", all_attachment_gates_passed)
    print("No mutation requests:", no_mutation_requests)
    for row in attachment_rows:
        print(
            f"measure={row.get('measureNumber')} "
            f"step={row.get('quantizedStep')} "
            f"sourceEventIndex={row.get('sourceEventIndex')} "
            f"sourceIndexValid={row.get('sourceEventIndexValid')} "
            f"attachmentGate={row.get('attachmentCandidateGate')}"
        )
    print("Ready for read-only chorus bend support attachment proof:", passed)
    print("Recommended next action:", recommended)
    print("Professional reference used as training label only: True")
    print("Professional event-local labels available: False")
    print("Event technique labels applied: False")
    print("Bend support claimed: False")
    print("Vibrato support claimed: False")
    print("Audio technique support claimed: False")
    print("Protected source event count: 949")
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
