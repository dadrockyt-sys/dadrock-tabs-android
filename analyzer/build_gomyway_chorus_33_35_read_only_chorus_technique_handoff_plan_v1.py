from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
SUPPORT_PROOF_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-support-proof-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-technique-handoff-plan-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-technique-handoff-plan-v1-manifest.json"


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
    proof = load(SUPPORT_PROOF_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if proof.get("passed") is not True:
        raise RuntimeError("Technique-evidence support proof is not green.")
    if proof.get("readyForReadOnlyChorusTechniqueHandoffPlan") is not True:
        raise RuntimeError("Support proof did not authorize a handoff plan.")
    if proof.get("recommendedNextAction") != (
        "build-read-only-chorus-technique-handoff-plan-v1"
    ):
        raise RuntimeError("Unexpected support-proof recommendation.")

    # The support proof intentionally stores only the three supported rows in
    # `supportedRows`; `singleNoteCandidateCount` remains the full classifier
    # population of 17. Do not expect the handoff subset to contain 17 rows.
    rows = [
        row for row in proof.get("supportedRows", []) if isinstance(row, dict)
    ]
    expected_total_count = int(proof.get("singleNoteCandidateCount", -1))
    candidate_count_matches = expected_total_count == 17

    bend_rows = [
        row for row in rows
        if row.get("supportCandidateClass") == "read-only-bend-support-candidate"
    ]
    vibrato_rows = [
        row for row in rows
        if row.get("supportCandidateClass") == "read-only-vibrato-support-candidate"
    ]

    handoff_rows: list[dict[str, Any]] = []
    duplicate_keys: set[tuple[int, int, int]] = set()
    seen: set[tuple[int, int, int]] = set()

    for row in bend_rows + vibrato_rows:
        key = row_key(row)
        if key in seen:
            duplicate_keys.add(key)
        seen.add(key)

        support_class = str(row.get("supportCandidateClass") or "")
        technique_family = (
            "bend" if support_class == "read-only-bend-support-candidate"
            else "vibrato"
        )
        handoff_rows.append({
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": row.get("sourceEventIndex"),
            "techniqueFamily": technique_family,
            "supportCandidateClass": support_class,
            "handoffAction": "review-for-event-local-technique-attachment",
            "requiresEventLocalAudioProof": True,
            "professionalEventLocalLabelAvailable": False,
            "eventTechniqueLabelApplied": False,
            "sourceEventModified": False,
            "readOnly": True,
        })

    expected_bend_count = int(proof.get("calibratedBendSupportCandidateCount", -1))
    expected_vibrato_count = int(proof.get("calibratedVibratoSupportCandidateCount", -1))
    bend_count_matches = len(bend_rows) == expected_bend_count == 3
    vibrato_count_matches = len(vibrato_rows) == expected_vibrato_count == 0
    handoff_count_matches = len(handoff_rows) == len(bend_rows) + len(vibrato_rows)
    no_mutation_requests = all(
        row.get("eventTechniqueLabelApplied") is False
        and row.get("sourceEventModified") is False
        for row in handoff_rows
    )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and candidate_count_matches
        and bend_count_matches
        and vibrato_count_matches
        and handoff_count_matches
        and not duplicate_keys
        and no_mutation_requests
        and len(handoff_rows) == 3
    )

    recommended = (
        "build-read-only-chorus-bend-event-local-audio-proof-v1"
        if passed
        else "diagnose-read-only-chorus-technique-handoff-plan-failures-v1"
    )

    output = {
        "schemaVersion": 1,
        "planType": "read-only-chorus-technique-evidence-handoff-plan",
        "passed": passed,
        "singleNoteCandidateCount": expected_total_count,
        "candidateCountMatches": candidate_count_matches,
        "handoffCandidateCount": len(handoff_rows),
        "bendHandoffCandidateCount": len(bend_rows),
        "vibratoHandoffCandidateCount": len(vibrato_rows),
        "bendCandidateCountMatchesProof": bend_count_matches,
        "vibratoCandidateCountMatchesProof": vibrato_count_matches,
        "duplicateHandoffKeyCount": len(duplicate_keys),
        "noMutationRequests": no_mutation_requests,
        "rows": handoff_rows,
        "readyForReadOnlyChorusBendEventLocalAudioProof": passed,
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
        "handoffCandidateCount": len(handoff_rows),
        "bendHandoffCandidateCount": len(bend_rows),
        "vibratoHandoffCandidateCount": len(vibrato_rows),
        "readyForReadOnlyChorusBendEventLocalAudioProof": passed,
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

    print("GOMYWAY CHORUS 33-35 READ-ONLY CHORUS TECHNIQUE HANDOFF PLAN V1 COMPLETE")
    print("Passed:", passed)
    print("Single-note candidates:", expected_total_count)
    print("Candidate count matches:", candidate_count_matches)
    print("Handoff candidates:", len(handoff_rows))
    print("Bend handoff candidates:", len(bend_rows))
    print("Vibrato handoff candidates:", len(vibrato_rows))
    print("Bend candidate count matches proof:", bend_count_matches)
    print("Vibrato candidate count matches proof:", vibrato_count_matches)
    print("Duplicate handoff keys:", len(duplicate_keys))
    print("No mutation requests:", no_mutation_requests)
    for row in handoff_rows:
        print(
            f"measure={row.get('measureNumber')} "
            f"step={row.get('quantizedStep')} "
            f"sourceEventIndex={row.get('sourceEventIndex')} "
            f"techniqueFamily={row.get('techniqueFamily')} "
            f"handoffAction={row.get('handoffAction')}"
        )
    print("Ready for read-only chorus bend event-local audio proof:", passed)
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
