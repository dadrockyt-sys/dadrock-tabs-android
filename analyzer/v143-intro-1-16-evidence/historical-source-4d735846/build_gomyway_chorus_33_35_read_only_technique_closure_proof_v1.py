from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
FOCUSED_CHORD_PROOF_PATH = PUBLIC / "gomyway-chorus-33-35-focused-proof-v1.json"
TIMING_PROOF_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v3.json"
TECHNIQUE_SUMMARY_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-chorus-bend-support-evidence-summary-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-closure-proof-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-closure-proof-v1-manifest.json"

EXPECTED_TECHNIQUE_KEYS = {
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


def technique_key(row: dict[str, Any]) -> tuple[int, int, int]:
    return (
        int(row.get("measureNumber") or -1),
        int(row.get("quantizedStep") or -1),
        int(row.get("sourceEventIndex") or -1),
    )


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    chord_proof = load(FOCUSED_CHORD_PROOF_PATH)
    timing_proof = load(TIMING_PROOF_PATH)
    technique_summary = load(TECHNIQUE_SUMMARY_PATH)

    protected_rows = source_rows(source)
    if len(protected_rows) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")

    chord_gate = bool(
        chord_proof.get("passed") is True
        and chord_proof.get("supportedTargetCount") == 10
        and chord_proof.get("allSupportedTargetsPassed") is True
        and chord_proof.get("unsupportedTargetsPreserved") is True
        and chord_proof.get("sourceEventsModified") is False
        and chord_proof.get("v7EventsModified") is False
        and chord_proof.get("rendererModified") is False
        and chord_proof.get("protectedBaselinesChanged") is False
        and chord_proof.get("productionPromotionAllowed") is False
    )

    timing_gate = bool(
        timing_proof.get("passed") is True
        and timing_proof.get("resolvedTimingCount") == 30
        and timing_proof.get("timingQualityGatePassedCount") == 30
        and timing_proof.get("monotonicityConflictCount") == 0
        and timing_proof.get("strictlyMonotonicTiming") is True
        and timing_proof.get("sourceEventsModified") is False
        and timing_proof.get("v7EventsModified") is False
        and timing_proof.get("rendererModified") is False
        and timing_proof.get("protectedBaselinesChanged") is False
        and timing_proof.get("productionPromotionAllowed") is False
    )

    summary_rows = [
        row for row in technique_summary.get("rows", []) if isinstance(row, dict)
    ]
    technique_keys = {technique_key(row) for row in summary_rows}
    technique_keys_match = technique_keys == EXPECTED_TECHNIQUE_KEYS
    technique_gate = bool(
        technique_summary.get("passed") is True
        and technique_summary.get("summaryRowCount") == 3
        and technique_summary.get("bendEvidenceSupportedCount") == 3
        and technique_summary.get("vibratoEvidenceSupportedCount") == 0
        and technique_summary.get("allSummaryGatesPassed") is True
        and technique_summary.get("noApplyRequests") is True
        and technique_keys_match
        and technique_summary.get("eventTechniqueLabelsApplied") is False
        and technique_summary.get("bendSupportClaimed") is False
        and technique_summary.get("vibratoSupportClaimed") is False
        and technique_summary.get("audioTechniqueSupportClaimed") is False
        and technique_summary.get("sourceEventsModified") is False
        and technique_summary.get("v7EventsModified") is False
        and technique_summary.get("rendererModified") is False
        and technique_summary.get("protectedBaselinesChanged") is False
        and technique_summary.get("productionPromotionAllowed") is False
    )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after

    passed = bool(
        source_unchanged
        and chord_gate
        and timing_gate
        and technique_gate
    )

    recommended = (
        "inventory-gomyway-next-rhythm-section-after-chorus-v1"
        if passed
        else "diagnose-gomyway-chorus-33-35-technique-closure-proof-failures-v1"
    )

    output = {
        "schemaVersion": 1,
        "proofType": "read-only-chorus-33-35-technique-closure-proof",
        "passed": passed,
        "chordFocusedProofPassed": chord_gate,
        "timingClosurePassed": timing_gate,
        "techniqueEvidenceSummaryPassed": technique_gate,
        "techniqueEvidenceKeysMatch": technique_keys_match,
        "supportedChordTargetCount": chord_proof.get("supportedTargetCount"),
        "unsupportedChordTargetsPreserved": chord_proof.get("unsupportedTargetsPreserved"),
        "resolvedTimingCount": timing_proof.get("resolvedTimingCount"),
        "strictlyMonotonicTiming": timing_proof.get("strictlyMonotonicTiming"),
        "bendEvidenceSupportedCount": technique_summary.get("bendEvidenceSupportedCount"),
        "vibratoEvidenceSupportedCount": technique_summary.get("vibratoEvidenceSupportedCount"),
        "eventTechniqueLabelsApplied": False,
        "bendSupportClaimed": False,
        "vibratoSupportClaimed": False,
        "audioTechniqueSupportClaimed": False,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalEventLocalLabelsAvailable": False,
        "protectedSourceEventCount": len(protected_rows),
        "protectedSourceHashBefore": source_hash_before,
        "protectedSourceHashAfter": source_hash_after,
        "protectedSourceHashUnchanged": source_unchanged,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "chorusMeasures33To35ClosedReadOnly": passed,
        "readyForNextRhythmSectionInventory": passed,
        "recommendedNextAction": recommended,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "chordFocusedProofPassed": chord_gate,
        "timingClosurePassed": timing_gate,
        "techniqueEvidenceSummaryPassed": technique_gate,
        "protectedSourceHashUnchanged": source_unchanged,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "readyForNextRhythmSectionInventory": passed,
        "recommendedNextAction": recommended,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 READ-ONLY TECHNIQUE CLOSURE PROOF V1 COMPLETE")
    print("Passed:", passed)
    print("Chord focused proof passed:", chord_gate)
    print("Supported chord targets:", chord_proof.get("supportedTargetCount"))
    print("Unsupported chord targets preserved:", chord_proof.get("unsupportedTargetsPreserved"))
    print("Timing closure passed:", timing_gate)
    print("Resolved timings:", timing_proof.get("resolvedTimingCount"))
    print("Strictly monotonic timing:", timing_proof.get("strictlyMonotonicTiming"))
    print("Technique evidence summary passed:", technique_gate)
    print("Technique evidence keys match:", technique_keys_match)
    print("Bend evidence supported:", technique_summary.get("bendEvidenceSupportedCount"))
    print("Vibrato evidence supported:", technique_summary.get("vibratoEvidenceSupportedCount"))
    print("Event technique labels applied: False")
    print("Bend support claimed: False")
    print("Vibrato support claimed: False")
    print("Audio technique support claimed: False")
    print("Professional reference used as training label only: True")
    print("Professional event-local labels available: False")
    print("Protected source event count:", len(protected_rows))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Chorus measures 33-35 closed read-only:", passed)
    print("Ready for next rhythm section inventory:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
