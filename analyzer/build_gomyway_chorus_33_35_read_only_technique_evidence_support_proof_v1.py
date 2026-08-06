from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
CANDIDATE_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-support-candidate-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-support-proof-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-support-proof-v1-manifest.json"


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

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if candidate.get("passed") is not True:
        raise RuntimeError("Technique-evidence support candidate is not green.")
    if candidate.get("readyForReadOnlyTechniqueEvidenceSupportProof") is not True:
        raise RuntimeError("Support candidate did not authorize the support proof.")
    if candidate.get("recommendedNextAction") != (
        "build-read-only-technique-evidence-support-proof-v1"
    ):
        raise RuntimeError("Unexpected support-candidate recommendation.")

    rows = [row for row in candidate.get("rows", []) if isinstance(row, dict)]
    expected_count = int(candidate.get("singleNoteCandidateCount", -1))
    candidate_count_matches = len(rows) == expected_count == 17

    keys = [row_key(row) for row in rows]
    unique_keys = len(set(keys)) == len(keys)
    bend_rows = [
        row for row in rows
        if row.get("calibratedBendEvidenceSupportCandidate") is True
    ]
    vibrato_rows = [
        row for row in rows
        if row.get("calibratedVibratoEvidenceSupportCandidate") is True
    ]
    no_label_rows = [
        row for row in rows
        if row.get("eventTechniqueLabelApplied") is not False
        or row.get("sourceEventModified") is not False
        or row.get("readOnly") is not True
    ]
    class_mismatches = [
        row for row in bend_rows
        if row.get("supportCandidateClass") != "read-only-bend-support-candidate"
    ] + [
        row for row in vibrato_rows
        if row.get("supportCandidateClass") != "read-only-vibrato-support-candidate"
    ]

    bend_count_matches = (
        len(bend_rows)
        == int(candidate.get("calibratedBendSupportCandidateCount", -1))
        == 3
    )
    vibrato_count_matches = (
        len(vibrato_rows)
        == int(candidate.get("calibratedVibratoSupportCandidateCount", -1))
        == 0
    )
    exclusivity_preserved = all(
        row.get("mutuallyExclusiveTechniqueCandidate") is True for row in rows
    )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and candidate_count_matches
        and unique_keys
        and bend_count_matches
        and vibrato_count_matches
        and exclusivity_preserved
        and not no_label_rows
        and not class_mismatches
        and candidate.get("bendCandidateCountMatchesProof") is True
        and candidate.get("vibratoCandidateCountMatchesProof") is True
        and candidate.get("allTechniqueCandidatesMutuallyExclusive") is True
    )

    recommended = (
        "build-read-only-chorus-technique-handoff-plan-v1"
        if passed
        else "diagnose-read-only-technique-evidence-support-proof-failures-v1"
    )

    proof_rows = [
        {
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": row.get("sourceEventIndex"),
            "supportCandidateClass": row.get("supportCandidateClass"),
            "supportCandidatePreserved": True,
            "eventTechniqueLabelApplied": False,
            "sourceEventModified": False,
            "readOnly": True,
        }
        for row in bend_rows + vibrato_rows
    ]

    output = {
        "schemaVersion": 1,
        "proofType": "read-only-calibrated-technique-evidence-support-proof",
        "passed": passed,
        "singleNoteCandidateCount": len(rows),
        "candidateCountMatches": candidate_count_matches,
        "rowKeysUnique": unique_keys,
        "calibratedBendSupportCandidateCount": len(bend_rows),
        "calibratedVibratoSupportCandidateCount": len(vibrato_rows),
        "bendCandidateCountMatches": bend_count_matches,
        "vibratoCandidateCountMatches": vibrato_count_matches,
        "techniqueCandidateExclusivityPreserved": exclusivity_preserved,
        "supportClassMismatchCount": len(class_mismatches),
        "eventOrSourceMutationViolationCount": len(no_label_rows),
        "supportedRows": proof_rows,
        "readyForReadOnlyChorusTechniqueHandoffPlan": passed,
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
        "singleNoteCandidateCount": len(rows),
        "calibratedBendSupportCandidateCount": len(bend_rows),
        "calibratedVibratoSupportCandidateCount": len(vibrato_rows),
        "readyForReadOnlyChorusTechniqueHandoffPlan": passed,
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

    print("GOMYWAY CHORUS 33-35 READ-ONLY TECHNIQUE EVIDENCE SUPPORT PROOF V1 COMPLETE")
    print("Passed:", passed)
    print("Single-note candidates:", len(rows))
    print("Candidate count matches:", candidate_count_matches)
    print("Row keys unique:", unique_keys)
    print("Calibrated bend support candidates:", len(bend_rows))
    print("Calibrated vibrato support candidates:", len(vibrato_rows))
    print("Bend candidate count matches:", bend_count_matches)
    print("Vibrato candidate count matches:", vibrato_count_matches)
    print("Technique candidate exclusivity preserved:", exclusivity_preserved)
    print("Support-class mismatches:", len(class_mismatches))
    print("Event/source mutation violations:", len(no_label_rows))
    for row in proof_rows:
        print(
            f"measure={row.get('measureNumber')} "
            f"step={row.get('quantizedStep')} "
            f"sourceEventIndex={row.get('sourceEventIndex')} "
            f"supportClass={row.get('supportCandidateClass')}"
        )
    print("Ready for read-only chorus technique handoff plan:", passed)
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
