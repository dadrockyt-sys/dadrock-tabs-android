from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
CANDIDATE_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-overlay-candidate-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-overlay-proof-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-overlay-proof-v1-manifest.json"

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
        raise RuntimeError("Bend support overlay candidate is not green.")
    if candidate.get("readyForReadOnlyChorusBendSupportOverlayProof") is not True:
        raise RuntimeError("Overlay candidate did not authorize the proof.")
    if candidate.get("recommendedNextAction") != (
        "build-read-only-chorus-bend-support-overlay-proof-v1"
    ):
        raise RuntimeError("Unexpected overlay-candidate recommendation.")

    rows = [row for row in candidate.get("rows", []) if isinstance(row, dict)]
    expected_count = int(candidate.get("overlayCandidateCount", -1))
    count_matches = len(rows) == expected_count == 3

    keys = [row_key(row) for row in rows]
    keys_unique = len(set(keys)) == len(keys)
    expected_keys_match = set(keys) == EXPECTED_KEYS

    proof_rows: list[dict[str, Any]] = []
    metadata_mismatches = 0
    overlay_gate_failures = 0
    apply_violations = 0
    source_index_failures = 0

    for row in rows:
        source_index = int(row.get("sourceEventIndex") or -1)
        source_index_valid = 0 <= source_index < len(protected_rows)
        if not source_index_valid:
            source_index_failures += 1

        overlay_metadata_valid = bool(
            row.get("overlayTechniqueFamily") == "bend"
            and row.get("overlaySupportStatus") == "audio-supported-read-only"
            and row.get("overlaySupportScope")
            == "chorus-measures-33-35-event-local-audio"
            and row.get("overlayProfessionalReferenceRole")
            == "part-level-training-label-only"
        )
        if not overlay_metadata_valid:
            metadata_mismatches += 1

        overlay_gate = row.get("overlayCandidateGate") is True
        if not overlay_gate:
            overlay_gate_failures += 1

        no_apply = bool(
            row.get("applyToProtectedSource") is False
            and row.get("applyToV7") is False
            and row.get("applyToRenderer") is False
            and row.get("productionEligible") is False
            and row.get("readOnly") is True
        )
        if not no_apply:
            apply_violations += 1

        proof_gate = bool(
            source_index_valid
            and overlay_metadata_valid
            and overlay_gate
            and no_apply
        )

        proof_rows.append({
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": source_index,
            "sourceEventIndexValid": source_index_valid,
            "overlayMetadataValid": overlay_metadata_valid,
            "overlayCandidateGate": overlay_gate,
            "noApply": no_apply,
            "overlayProofGate": proof_gate,
            "readOnly": True,
        })

    all_proof_gates_passed = bool(
        len(proof_rows) == 3
        and all(row.get("overlayProofGate") is True for row in proof_rows)
    )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after

    passed = bool(
        source_unchanged
        and count_matches
        and keys_unique
        and expected_keys_match
        and metadata_mismatches == 0
        and overlay_gate_failures == 0
        and apply_violations == 0
        and source_index_failures == 0
        and all_proof_gates_passed
        and candidate.get("allOverlayCandidateGatesPassed") is True
        and candidate.get("noApplyRequests") is True
    )

    recommended = (
        "build-read-only-chorus-bend-support-evidence-summary-v1"
        if passed
        else "diagnose-read-only-chorus-bend-support-overlay-proof-failures-v1"
    )

    output = {
        "schemaVersion": 1,
        "proofType": "read-only-chorus-bend-support-overlay-proof",
        "passed": passed,
        "overlayCandidateCount": len(rows),
        "overlayCandidateCountMatches": count_matches,
        "overlayKeysUnique": keys_unique,
        "expectedOverlayKeysMatch": expected_keys_match,
        "overlayMetadataMismatchCount": metadata_mismatches,
        "overlayGateFailureCount": overlay_gate_failures,
        "applyViolationCount": apply_violations,
        "sourceEventIndexFailureCount": source_index_failures,
        "allOverlayProofGatesPassed": all_proof_gates_passed,
        "rows": proof_rows,
        "readyForReadOnlyChorusBendSupportEvidenceSummary": passed,
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
        "overlayCandidateCount": len(rows),
        "allOverlayProofGatesPassed": all_proof_gates_passed,
        "readyForReadOnlyChorusBendSupportEvidenceSummary": passed,
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

    print("GOMYWAY CHORUS 33-35 READ-ONLY CHORUS BEND SUPPORT OVERLAY PROOF V1 COMPLETE")
    print("Passed:", passed)
    print("Overlay candidates:", len(rows))
    print("Overlay candidate count matches:", count_matches)
    print("Overlay keys unique:", keys_unique)
    print("Expected overlay keys match:", expected_keys_match)
    print("Overlay metadata mismatches:", metadata_mismatches)
    print("Overlay gate failures:", overlay_gate_failures)
    print("Apply violations:", apply_violations)
    print("Source event index failures:", source_index_failures)
    print("All overlay proof gates passed:", all_proof_gates_passed)
    for row in proof_rows:
        print(
            f"measure={row.get('measureNumber')} "
            f"step={row.get('quantizedStep')} "
            f"sourceEventIndex={row.get('sourceEventIndex')} "
            f"metadataValid={row.get('overlayMetadataValid')} "
            f"proofGate={row.get('overlayProofGate')}"
        )
    print("Ready for read-only chorus bend support evidence summary:", passed)
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
