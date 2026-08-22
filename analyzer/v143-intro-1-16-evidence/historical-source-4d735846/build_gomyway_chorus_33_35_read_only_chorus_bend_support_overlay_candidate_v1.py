from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
ATTACHMENT_PROOF_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-attachment-proof-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-overlay-candidate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-overlay-candidate-v1-manifest.json"

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
    proof = load(ATTACHMENT_PROOF_PATH)
    protected_rows = source_rows(source)

    if len(protected_rows) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if proof.get("passed") is not True:
        raise RuntimeError("Bend support attachment proof is not green.")
    if proof.get("readyForReadOnlyChorusBendSupportOverlayCandidate") is not True:
        raise RuntimeError("Attachment proof did not authorize overlay candidate.")
    if proof.get("recommendedNextAction") != (
        "build-read-only-chorus-bend-support-overlay-candidate-v1"
    ):
        raise RuntimeError("Unexpected attachment-proof recommendation.")

    proof_rows = [row for row in proof.get("rows", []) if isinstance(row, dict)]
    expected_count = int(proof.get("attachmentCandidateCount", -1))
    proof_count_matches = len(proof_rows) == expected_count == 3

    keys = [row_key(row) for row in proof_rows]
    keys_unique = len(set(keys)) == len(keys)
    expected_keys_match = set(keys) == EXPECTED_KEYS

    overlay_rows: list[dict[str, Any]] = []
    invalid_source_indexes = 0
    proof_gate_failures = 0
    mutation_requests = 0

    for row in proof_rows:
        source_index = int(row.get("sourceEventIndex") or -1)
        source_index_valid = 0 <= source_index < len(protected_rows)
        if not source_index_valid:
            invalid_source_indexes += 1

        proof_gate = row.get("attachmentProofGate") is True
        if not proof_gate:
            proof_gate_failures += 1

        no_mutation = bool(
            row.get("eventTechniqueLabelApplied") is False
            and row.get("sourceEventModified") is False
            and row.get("readOnly") is True
        )
        if not no_mutation:
            mutation_requests += 1

        overlay_gate = bool(
            source_index_valid
            and proof_gate
            and no_mutation
            and row.get("attachmentMetadataValid") is True
            and row.get("sourceEventIndexValid") is True
        )

        overlay_rows.append({
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": source_index,
            "overlayTechniqueFamily": "bend",
            "overlaySupportStatus": "audio-supported-read-only",
            "overlaySupportScope": "chorus-measures-33-35-event-local-audio",
            "overlayProfessionalReferenceRole": "part-level-training-label-only",
            "overlayCandidateGate": overlay_gate,
            "applyToProtectedSource": False,
            "applyToV7": False,
            "applyToRenderer": False,
            "productionEligible": False,
            "readOnly": True,
        })

    overlay_count_matches = len(overlay_rows) == 3
    all_overlay_gates_passed = bool(
        overlay_count_matches
        and all(row.get("overlayCandidateGate") is True for row in overlay_rows)
    )
    no_apply_requests = all(
        row.get("applyToProtectedSource") is False
        and row.get("applyToV7") is False
        and row.get("applyToRenderer") is False
        and row.get("productionEligible") is False
        and row.get("readOnly") is True
        for row in overlay_rows
    )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after

    passed = bool(
        source_unchanged
        and proof_count_matches
        and keys_unique
        and expected_keys_match
        and invalid_source_indexes == 0
        and proof_gate_failures == 0
        and mutation_requests == 0
        and all_overlay_gates_passed
        and no_apply_requests
        and proof.get("allAttachmentProofGatesPassed") is True
    )

    recommended = (
        "build-read-only-chorus-bend-support-overlay-proof-v1"
        if passed
        else "diagnose-read-only-chorus-bend-support-overlay-candidate-failures-v1"
    )

    output = {
        "schemaVersion": 1,
        "candidateType": "read-only-chorus-bend-support-overlay-candidate",
        "passed": passed,
        "attachmentProofRowCount": len(proof_rows),
        "attachmentProofRowCountMatches": proof_count_matches,
        "overlayCandidateCount": len(overlay_rows),
        "overlayCandidateCountMatches": overlay_count_matches,
        "overlayKeysUnique": keys_unique,
        "expectedOverlayKeysMatch": expected_keys_match,
        "invalidSourceEventIndexCount": invalid_source_indexes,
        "attachmentProofGateFailureCount": proof_gate_failures,
        "mutationRequestCount": mutation_requests,
        "allOverlayCandidateGatesPassed": all_overlay_gates_passed,
        "noApplyRequests": no_apply_requests,
        "rows": overlay_rows,
        "readyForReadOnlyChorusBendSupportOverlayProof": passed,
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
        "overlayCandidateCount": len(overlay_rows),
        "allOverlayCandidateGatesPassed": all_overlay_gates_passed,
        "readyForReadOnlyChorusBendSupportOverlayProof": passed,
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

    print("GOMYWAY CHORUS 33-35 READ-ONLY CHORUS BEND SUPPORT OVERLAY CANDIDATE V1 COMPLETE")
    print("Passed:", passed)
    print("Attachment proof rows:", len(proof_rows))
    print("Attachment proof row count matches:", proof_count_matches)
    print("Overlay candidates:", len(overlay_rows))
    print("Overlay candidate count matches:", overlay_count_matches)
    print("Overlay keys unique:", keys_unique)
    print("Expected overlay keys match:", expected_keys_match)
    print("Invalid source event indexes:", invalid_source_indexes)
    print("Attachment proof gate failures:", proof_gate_failures)
    print("Mutation requests:", mutation_requests)
    print("All overlay candidate gates passed:", all_overlay_gates_passed)
    print("No apply requests:", no_apply_requests)
    for row in overlay_rows:
        print(
            f"measure={row.get('measureNumber')} "
            f"step={row.get('quantizedStep')} "
            f"sourceEventIndex={row.get('sourceEventIndex')} "
            f"technique={row.get('overlayTechniqueFamily')} "
            f"overlayGate={row.get('overlayCandidateGate')}"
        )
    print("Ready for read-only chorus bend support overlay proof:", passed)
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
