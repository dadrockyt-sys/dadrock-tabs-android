from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
CALIBRATED_PROOF_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-calibrated-proof-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-support-candidate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-support-candidate-v1-manifest.json"


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
    proof = load(CALIBRATED_PROOF_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if proof.get("passed") is not True:
        raise RuntimeError("Calibrated technique-evidence proof is not green.")
    if proof.get("readyForReadOnlyTechniqueEvidenceSupportCandidate") is not True:
        raise RuntimeError("Calibrated proof did not authorize a support candidate.")
    if proof.get("recommendedNextAction") != (
        "build-read-only-technique-evidence-support-candidate-v1"
    ):
        raise RuntimeError("Unexpected calibrated-proof recommendation.")

    proof_rows = [row for row in proof.get("rows", []) if isinstance(row, dict)]
    expected_count = int(proof.get("singleNoteCandidateCount", -1))
    count_matches = len(proof_rows) == expected_count == 17

    candidate_rows: list[dict[str, Any]] = []
    bend_rows: list[dict[str, Any]] = []
    vibrato_rows: list[dict[str, Any]] = []
    duplicate_keys: set[tuple[int, int, int]] = set()
    seen: set[tuple[int, int, int]] = set()

    for row in proof_rows:
        key = row_key(row)
        if key in seen:
            duplicate_keys.add(key)
        seen.add(key)

        bend_candidate = row.get("calibratedBendEvidenceSupportCandidate") is True
        vibrato_candidate = row.get("calibratedVibratoEvidenceSupportCandidate") is True
        mutually_exclusive = not (bend_candidate and vibrato_candidate)

        support_class = "no-calibrated-technique-support"
        if bend_candidate and mutually_exclusive:
            support_class = "read-only-bend-support-candidate"
        elif vibrato_candidate and mutually_exclusive:
            support_class = "read-only-vibrato-support-candidate"

        candidate_row = {
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": row.get("sourceEventIndex"),
            "evidenceClass": row.get("evidenceClass"),
            "calibratedBendEvidenceSupportCandidate": bend_candidate,
            "calibratedVibratoEvidenceSupportCandidate": vibrato_candidate,
            "mutuallyExclusiveTechniqueCandidate": mutually_exclusive,
            "supportCandidateClass": support_class,
            "eventTechniqueLabelApplied": False,
            "sourceEventModified": False,
            "readOnly": True,
        }
        candidate_rows.append(candidate_row)
        if bend_candidate:
            bend_rows.append(candidate_row)
        if vibrato_candidate:
            vibrato_rows.append(candidate_row)

    expected_bend_count = int(
        proof.get("calibratedBendEvidenceSupportCandidateCount", -1)
    )
    expected_vibrato_count = int(
        proof.get("calibratedVibratoEvidenceSupportCandidateCount", -1)
    )
    bend_count_matches = len(bend_rows) == expected_bend_count == 3
    vibrato_count_matches = len(vibrato_rows) == expected_vibrato_count == 0
    all_mutually_exclusive = all(
        row.get("mutuallyExclusiveTechniqueCandidate") is True
        for row in candidate_rows
    )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and count_matches
        and not duplicate_keys
        and bend_count_matches
        and vibrato_count_matches
        and all_mutually_exclusive
        and proof.get("calibrationMismatchCount") == 0
        and proof.get("rowKeysMatch") is True
    )

    recommended = (
        "build-read-only-technique-evidence-support-proof-v1"
        if passed
        else "diagnose-read-only-technique-evidence-support-candidate-failures-v1"
    )

    output = {
        "schemaVersion": 1,
        "candidateType": "read-only-calibrated-technique-evidence-support-candidate",
        "passed": passed,
        "singleNoteCandidateCount": len(candidate_rows),
        "candidateCountMatches": count_matches,
        "duplicateRowKeyCount": len(duplicate_keys),
        "calibratedBendSupportCandidateCount": len(bend_rows),
        "calibratedVibratoSupportCandidateCount": len(vibrato_rows),
        "bendCandidateCountMatchesProof": bend_count_matches,
        "vibratoCandidateCountMatchesProof": vibrato_count_matches,
        "allTechniqueCandidatesMutuallyExclusive": all_mutually_exclusive,
        "rows": candidate_rows,
        "readyForReadOnlyTechniqueEvidenceSupportProof": passed,
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
        "singleNoteCandidateCount": len(candidate_rows),
        "calibratedBendSupportCandidateCount": len(bend_rows),
        "calibratedVibratoSupportCandidateCount": len(vibrato_rows),
        "readyForReadOnlyTechniqueEvidenceSupportProof": passed,
        "recommendedNextAction": recommended,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "eventTechniqueLabelsApplied": False,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 READ-ONLY TECHNIQUE EVIDENCE SUPPORT CANDIDATE V1 COMPLETE")
    print("Passed:", passed)
    print("Single-note candidates:", len(candidate_rows))
    print("Candidate count matches:", count_matches)
    print("Duplicate row keys:", len(duplicate_keys))
    print("Calibrated bend support candidates:", len(bend_rows))
    print("Calibrated vibrato support candidates:", len(vibrato_rows))
    print("Bend candidate count matches proof:", bend_count_matches)
    print("Vibrato candidate count matches proof:", vibrato_count_matches)
    print("All technique candidates mutually exclusive:", all_mutually_exclusive)
    for row in bend_rows + vibrato_rows:
        print(
            f"measure={row.get('measureNumber')} "
            f"step={row.get('quantizedStep')} "
            f"sourceEventIndex={row.get('sourceEventIndex')} "
            f"supportClass={row.get('supportCandidateClass')}"
        )
    print("Ready for read-only technique evidence support proof:", passed)
    print("Recommended next action:", recommended)
    print("Professional reference used as training label only: True")
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
