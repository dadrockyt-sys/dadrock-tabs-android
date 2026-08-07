from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
OVERLAY_PROOF_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-overlay-proof-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-evidence-summary-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-evidence-summary-v1-manifest.json"

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
    proof = load(OVERLAY_PROOF_PATH)
    protected_rows = source_rows(source)

    if len(protected_rows) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if proof.get("passed") is not True:
        raise RuntimeError("Bend support overlay proof is not green.")
    if proof.get("readyForReadOnlyChorusBendSupportEvidenceSummary") is not True:
        raise RuntimeError("Overlay proof did not authorize the evidence summary.")
    if proof.get("recommendedNextAction") != (
        "build-read-only-chorus-bend-support-evidence-summary-v1"
    ):
        raise RuntimeError("Unexpected overlay-proof recommendation.")

    rows = [row for row in proof.get("rows", []) if isinstance(row, dict)]
    expected_count = int(proof.get("overlayCandidateCount", -1))
    count_matches = len(rows) == expected_count == 3

    keys = [row_key(row) for row in rows]
    keys_unique = len(set(keys)) == len(keys)
    expected_keys_match = set(keys) == EXPECTED_KEYS

    summary_rows: list[dict[str, Any]] = []
    proof_gate_failures = 0
    metadata_failures = 0
    source_index_failures = 0
    mutation_violations = 0

    for row in rows:
        proof_gate = row.get("overlayProofGate") is True
        if not proof_gate:
            proof_gate_failures += 1

        metadata_valid = row.get("overlayMetadataValid") is True
        if not metadata_valid:
            metadata_failures += 1

        source_index_valid = row.get("sourceEventIndexValid") is True
        if not source_index_valid:
            source_index_failures += 1

        no_mutation = bool(
            row.get("applyToProtectedSource") is False
            and row.get("applyToV7") is False
            and row.get("applyToRenderer") is False
            and row.get("productionEligible") is False
            and row.get("readOnly") is True
        )
        if not no_mutation:
            mutation_violations += 1

        summary_gate = bool(
            proof_gate
            and metadata_valid
            and source_index_valid
            and no_mutation
        )

        summary_rows.append({
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": row.get("sourceEventIndex"),
            "techniqueFamily": "bend",
            "evidenceStatus": "audio-supported-read-only",
            "eventLocalAudioEvidence": True,
            "professionalReferenceRole": "part-level-training-label-only",
            "eventLocalProfessionalLabelAvailable": False,
            "summaryGate": summary_gate,
            "applyToProtectedSource": False,
            "applyToV7": False,
            "applyToRenderer": False,
            "productionEligible": False,
            "readOnly": True,
        })

    all_summary_gates_passed = bool(
        len(summary_rows) == 3
        and all(row.get("summaryGate") is True for row in summary_rows)
    )
    no_apply_requests = all(
        row.get("applyToProtectedSource") is False
        and row.get("applyToV7") is False
        and row.get("applyToRenderer") is False
        and row.get("productionEligible") is False
        and row.get("readOnly") is True
        for row in summary_rows
    )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after

    passed = bool(
        source_unchanged
        and count_matches
        and keys_unique
        and expected_keys_match
        and proof_gate_failures == 0
        and metadata_failures == 0
        and source_index_failures == 0
        and mutation_violations == 0
        and all_summary_gates_passed
        and no_apply_requests
        and proof.get("allOverlayProofGatesPassed") is True
    )

    recommended = (
        "build-read-only-chorus-33-35-technique-closure-proof-v1"
        if passed
        else "diagnose-read-only-chorus-bend-support-evidence-summary-failures-v1"
    )

    output = {
        "schemaVersion": 1,
        "summaryType": "read-only-chorus-bend-support-evidence-summary",
        "passed": passed,
        "overlayProofRowCount": len(rows),
        "overlayProofRowCountMatches": count_matches,
        "summaryRowCount": len(summary_rows),
        "summaryKeysUnique": keys_unique,
        "expectedSummaryKeysMatch": expected_keys_match,
        "overlayProofGateFailureCount": proof_gate_failures,
        "overlayMetadataFailureCount": metadata_failures,
        "sourceEventIndexFailureCount": source_index_failures,
        "mutationViolationCount": mutation_violations,
        "bendEvidenceSupportedCount": len(summary_rows),
        "vibratoEvidenceSupportedCount": 0,
        "allSummaryGatesPassed": all_summary_gates_passed,
        "noApplyRequests": no_apply_requests,
        "rows": summary_rows,
        "readyForReadOnlyChorusTechniqueClosureProof": passed,
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
        "bendEvidenceSupportedCount": len(summary_rows),
        "vibratoEvidenceSupportedCount": 0,
        "allSummaryGatesPassed": all_summary_gates_passed,
        "readyForReadOnlyChorusTechniqueClosureProof": passed,
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

    print("GOMYWAY CHORUS 33-35 READ-ONLY CHORUS BEND SUPPORT EVIDENCE SUMMARY V1 COMPLETE")
    print("Passed:", passed)
    print("Overlay proof rows:", len(rows))
    print("Overlay proof row count matches:", count_matches)
    print("Summary rows:", len(summary_rows))
    print("Summary keys unique:", keys_unique)
    print("Expected summary keys match:", expected_keys_match)
    print("Overlay proof gate failures:", proof_gate_failures)
    print("Overlay metadata failures:", metadata_failures)
    print("Source event index failures:", source_index_failures)
    print("Mutation violations:", mutation_violations)
    print("Bend evidence supported:", len(summary_rows))
    print("Vibrato evidence supported: 0")
    print("All summary gates passed:", all_summary_gates_passed)
    print("No apply requests:", no_apply_requests)
    for row in summary_rows:
        print(
            f"measure={row.get('measureNumber')} "
            f"step={row.get('quantizedStep')} "
            f"sourceEventIndex={row.get('sourceEventIndex')} "
            f"technique={row.get('techniqueFamily')} "
            f"summaryGate={row.get('summaryGate')}"
        )
    print("Ready for read-only chorus technique closure proof:", passed)
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
