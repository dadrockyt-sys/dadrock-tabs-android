from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
HANDOFF_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-technique-handoff-plan-v1.json"
CLASSIFIER_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-classifier-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-event-local-audio-proof-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-event-local-audio-proof-v1-manifest.json"


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
    handoff = load(HANDOFF_PATH)
    classifier = load(CLASSIFIER_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if handoff.get("passed") is not True:
        raise RuntimeError("Chorus technique handoff plan is not green.")
    if handoff.get("readyForReadOnlyChorusBendEventLocalAudioProof") is not True:
        raise RuntimeError("Handoff plan did not authorize event-local bend proof.")
    if handoff.get("recommendedNextAction") != (
        "build-read-only-chorus-bend-event-local-audio-proof-v1"
    ):
        raise RuntimeError("Unexpected handoff-plan recommendation.")
    if classifier.get("passed") is not True:
        raise RuntimeError("Technique evidence classifier is not green.")

    handoff_rows = [row for row in handoff.get("rows", []) if isinstance(row, dict)]
    classifier_rows = [row for row in classifier.get("rows", []) if isinstance(row, dict)]
    classifier_by_key = {row_key(row): row for row in classifier_rows}

    proof_rows: list[dict[str, Any]] = []
    missing_classifier_rows = 0
    event_local_failures = 0

    for handoff_row in handoff_rows:
        key = row_key(handoff_row)
        classifier_row = classifier_by_key.get(key)
        if classifier_row is None:
            missing_classifier_rows += 1
            continue

        bend_gate = classifier_row.get("bendEvidenceGate") is True
        vibrato_gate = classifier_row.get("vibratoEvidenceGate") is True
        evidence_class = classifier_row.get("evidenceClass")
        robust_range = float(classifier_row.get("robustPitchRangeCents") or 0.0)
        net_change = float(classifier_row.get("netPitchChangeCents") or 0.0)
        dominant_ratio = float(classifier_row.get("dominantDirectionRatio") or 0.0)
        direction_changes = int(classifier_row.get("directionChangeCount") or 0)
        voiced_frames = int(classifier_row.get("voicedFrameCount") or 0)

        event_local_gate = bool(
            handoff_row.get("techniqueFamily") == "bend"
            and handoff_row.get("requiresEventLocalAudioProof") is True
            and bend_gate
            and not vibrato_gate
            and evidence_class == "bend-evidence-candidate"
            and voiced_frames >= 6
            and robust_range >= 120.0
            and abs(net_change) >= 90.0
            and dominant_ratio >= 0.70
            and direction_changes <= 3
        )
        if not event_local_gate:
            event_local_failures += 1

        proof_rows.append({
            "measureNumber": handoff_row.get("measureNumber"),
            "quantizedStep": handoff_row.get("quantizedStep"),
            "sourceEventIndex": handoff_row.get("sourceEventIndex"),
            "voicedFrameCount": voiced_frames,
            "robustPitchRangeCents": robust_range,
            "netPitchChangeCents": net_change,
            "dominantDirectionRatio": dominant_ratio,
            "directionChangeCount": direction_changes,
            "bendEvidenceGate": bend_gate,
            "vibratoEvidenceGate": vibrato_gate,
            "evidenceClass": evidence_class,
            "eventLocalBendAudioProofGate": event_local_gate,
            "eventTechniqueLabelApplied": False,
            "sourceEventModified": False,
            "readOnly": True,
        })

    expected_handoff_count = int(handoff.get("handoffCandidateCount", -1))
    handoff_count_matches = len(handoff_rows) == expected_handoff_count == 3
    proof_count_matches = len(proof_rows) == len(handoff_rows)
    all_event_local_passed = event_local_failures == 0 and len(proof_rows) == 3

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and handoff_count_matches
        and proof_count_matches
        and missing_classifier_rows == 0
        and all_event_local_passed
    )

    recommended = (
        "build-read-only-chorus-bend-support-attachment-candidate-v1"
        if passed
        else "diagnose-read-only-chorus-bend-event-local-audio-proof-failures-v1"
    )

    output = {
        "schemaVersion": 1,
        "proofType": "read-only-chorus-bend-event-local-audio-proof",
        "passed": passed,
        "handoffCandidateCount": len(handoff_rows),
        "handoffCandidateCountMatches": handoff_count_matches,
        "eventLocalProofRowCount": len(proof_rows),
        "eventLocalProofRowCountMatches": proof_count_matches,
        "missingClassifierRowCount": missing_classifier_rows,
        "eventLocalBendProofFailureCount": event_local_failures,
        "allEventLocalBendAudioProofsPassed": all_event_local_passed,
        "rows": proof_rows,
        "readyForReadOnlyChorusBendSupportAttachmentCandidate": passed,
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
        "eventLocalProofRowCount": len(proof_rows),
        "eventLocalBendProofFailureCount": event_local_failures,
        "allEventLocalBendAudioProofsPassed": all_event_local_passed,
        "readyForReadOnlyChorusBendSupportAttachmentCandidate": passed,
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

    print("GOMYWAY CHORUS 33-35 READ-ONLY CHORUS BEND EVENT-LOCAL AUDIO PROOF V1 COMPLETE")
    print("Passed:", passed)
    print("Handoff candidates:", len(handoff_rows))
    print("Handoff candidate count matches:", handoff_count_matches)
    print("Event-local proof rows:", len(proof_rows))
    print("Event-local proof row count matches:", proof_count_matches)
    print("Missing classifier rows:", missing_classifier_rows)
    print("Event-local bend proof failures:", event_local_failures)
    print("All event-local bend audio proofs passed:", all_event_local_passed)
    for row in proof_rows:
        print(
            f"measure={row.get('measureNumber')} "
            f"step={row.get('quantizedStep')} "
            f"sourceEventIndex={row.get('sourceEventIndex')} "
            f"range={row.get('robustPitchRangeCents')} "
            f"net={row.get('netPitchChangeCents')} "
            f"dominantRatio={row.get('dominantDirectionRatio')} "
            f"directionChanges={row.get('directionChangeCount')} "
            f"eventLocalGate={row.get('eventLocalBendAudioProofGate')}"
        )
    print("Ready for read-only chorus bend support attachment candidate:", passed)
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
