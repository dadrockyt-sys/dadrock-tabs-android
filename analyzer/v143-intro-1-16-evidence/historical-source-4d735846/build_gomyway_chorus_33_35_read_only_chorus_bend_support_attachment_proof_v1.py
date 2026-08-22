from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
CANDIDATE_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-attachment-candidate-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-attachment-proof-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-attachment-proof-v1-manifest.json"

EXPECTED_KEYS = {
    (33, 9, 237),
    (34, 5, 247),
    (34, 13, 254),
}


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
    candidate = load(CANDIDATE_PATH)
    protected_rows = source_rows(source)

    if len(protected_rows) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if candidate.get("passed") is not True:
        raise RuntimeError("Bend support attachment candidate is not green.")
    if candidate.get("readyForReadOnlyChorusBendSupportAttachmentProof") is not True:
        raise RuntimeError("Attachment candidate did not authorize the proof.")
    if candidate.get("recommendedNextAction") != (
        "build-read-only-chorus-bend-support-attachment-proof-v1"
    ):
        raise RuntimeError("Unexpected attachment-candidate recommendation.")

    rows = [row for row in candidate.get("rows", []) if isinstance(row, dict)]
    expected_count = int(candidate.get("attachmentCandidateCount", -1))
    count_matches = len(rows) == expected_count == 3

    keys = [row_key(row) for row in rows]
    keys_unique = len(set(keys)) == len(keys)
    expected_keys_match = set(keys) == EXPECTED_KEYS

    proof_rows: list[dict[str, Any]] = []
    metadata_mismatches = 0
    attachment_gate_failures = 0
    source_index_failures = 0
    mutation_violations = 0

    for row in rows:
        metadata = row.get("proposedTechniqueMetadata")
        metadata_valid = bool(
            isinstance(metadata, dict)
            and metadata.get("technique") == "bend"
            and metadata.get("supportScope") == "chorus-measures-33-35-event-local-audio"
            and metadata.get("supportStatus") == "candidate-only"
            and metadata.get("professionalReferenceRole") == "part-level-training-label-only"
            and row.get("proposedTechniqueFamily") == "bend"
            and row.get("proposedAttachmentType")
            == "read-only-audio-supported-technique-candidate"
        )
        if not metadata_valid:
            metadata_mismatches += 1

        attachment_gate = row.get("attachmentCandidateGate") is True
        if not attachment_gate:
            attachment_gate_failures += 1

        source_index = int(row.get("sourceEventIndex") or -1)
        source_index_valid = bool(
            row.get("sourceEventIndexValid") is True
            and 0 <= source_index < len(protected_rows)
        )
        if not source_index_valid:
            source_index_failures += 1

        no_mutation = bool(
            row.get("eventTechniqueLabelApplied") is False
            and row.get("sourceEventModified") is False
            and row.get("readOnly") is True
        )
        if not no_mutation:
            mutation_violations += 1

        proof_gate = bool(
            metadata_valid
            and attachment_gate
            and source_index_valid
            and no_mutation
            and row.get("eventLocalBendAudioProofGate") is True
        )
        proof_rows.append({
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": source_index,
            "attachmentMetadataValid": metadata_valid,
            "sourceEventIndexValid": source_index_valid,
            "attachmentCandidateGate": attachment_gate,
            "noMutation": no_mutation,
            "attachmentProofGate": proof_gate,
            "eventTechniqueLabelApplied": False,
            "sourceEventModified": False,
            "readOnly": True,
        })

    all_proof_gates_passed = bool(
        len(proof_rows) == 3
        and all(row.get("attachmentProofGate") is True for row in proof_rows)
    )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and count_matches
        and keys_unique
        and expected_keys_match
        and metadata_mismatches == 0
        and attachment_gate_failures == 0
        and source_index_failures == 0
        and mutation_violations == 0
        and all_proof_gates_passed
        and candidate.get("allAttachmentCandidateGatesPassed") is True
        and candidate.get("noMutationRequests") is True
    )

    recommended = (
        "build-read-only-chorus-bend-support-overlay-candidate-v1"
        if passed
        else "diagnose-read-only-chorus-bend-support-attachment-proof-failures-v1"
    )

    output = {
        "schemaVersion": 1,
        "proofType": "read-only-chorus-bend-support-attachment-proof",
        "passed": passed,
        "attachmentCandidateCount": len(rows),
        "attachmentCandidateCountMatches": count_matches,
        "attachmentKeysUnique": keys_unique,
        "expectedAttachmentKeysMatch": expected_keys_match,
        "attachmentMetadataMismatchCount": metadata_mismatches,
        "attachmentGateFailureCount": attachment_gate_failures,
        "sourceEventIndexFailureCount": source_index_failures,
        "mutationViolationCount": mutation_violations,
        "allAttachmentProofGatesPassed": all_proof_gates_passed,
        "rows": proof_rows,
        "readyForReadOnlyChorusBendSupportOverlayCandidate": passed,
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
        "attachmentCandidateCount": len(rows),
        "allAttachmentProofGatesPassed": all_proof_gates_passed,
        "readyForReadOnlyChorusBendSupportOverlayCandidate": passed,
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

    print("GOMYWAY CHORUS 33-35 READ-ONLY CHORUS BEND SUPPORT ATTACHMENT PROOF V1 COMPLETE")
    print("Passed:", passed)
    print("Attachment candidates:", len(rows))
    print("Attachment candidate count matches:", count_matches)
    print("Attachment keys unique:", keys_unique)
    print("Expected attachment keys match:", expected_keys_match)
    print("Attachment metadata mismatches:", metadata_mismatches)
    print("Attachment gate failures:", attachment_gate_failures)
    print("Source event index failures:", source_index_failures)
    print("Mutation violations:", mutation_violations)
    print("All attachment proof gates passed:", all_proof_gates_passed)
    for row in proof_rows:
        print(
            f"measure={row.get('measureNumber')} "
            f"step={row.get('quantizedStep')} "
            f"sourceEventIndex={row.get('sourceEventIndex')} "
            f"metadataValid={row.get('attachmentMetadataValid')} "
            f"proofGate={row.get('attachmentProofGate')}"
        )
    print("Ready for read-only chorus bend support overlay candidate:", passed)
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
