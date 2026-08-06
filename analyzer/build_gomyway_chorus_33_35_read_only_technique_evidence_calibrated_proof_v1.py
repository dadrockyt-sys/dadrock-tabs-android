from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
CLASSIFIER_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-classifier-v1.json"
LABEL_BENCHMARK_PATH = PUBLIC / "gomyway-chorus-33-35-technique-evidence-professional-label-benchmark-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-calibrated-proof-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-calibrated-proof-v1-manifest.json"


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
    classifier = load(CLASSIFIER_PATH)
    label_benchmark = load(LABEL_BENCHMARK_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if classifier.get("passed") is not True:
        raise RuntimeError("Technique evidence classifier is not green.")
    if label_benchmark.get("passed") is not True:
        raise RuntimeError("Professional-label technique benchmark is not green.")
    if label_benchmark.get("readyForCalibratedTechniqueEvidenceProof") is not True:
        raise RuntimeError("Professional-label benchmark did not authorize calibrated proof.")
    if label_benchmark.get("recommendedNextAction") != (
        "build-read-only-technique-evidence-calibrated-proof-v1"
    ):
        raise RuntimeError("Unexpected professional-label benchmark recommendation.")

    classifier_rows = [
        row for row in classifier.get("rows", []) if isinstance(row, dict)
    ]
    label_rows = [
        row for row in label_benchmark.get("rows", []) if isinstance(row, dict)
    ]

    classifier_by_key = {row_key(row): row for row in classifier_rows}
    label_by_key = {row_key(row): row for row in label_rows}
    row_keys_match = set(classifier_by_key) == set(label_by_key)
    candidate_count_matches = (
        len(classifier_rows)
        == len(label_rows)
        == int(classifier.get("singleNoteCandidateCount", -1))
        == int(label_benchmark.get("singleNoteCandidateCount", -1))
    )

    expected_bend_present = label_benchmark.get("expectedBendPresent") is True
    expected_vibrato_present = label_benchmark.get("expectedVibratoPresent") is True

    calibrated_rows: list[dict[str, Any]] = []
    bend_supported_rows: list[dict[str, Any]] = []
    vibrato_supported_rows: list[dict[str, Any]] = []
    calibration_mismatch_count = 0

    for key in sorted(classifier_by_key):
        classifier_row = classifier_by_key[key]
        label_row = label_by_key.get(key, {})

        bend_gate = classifier_row.get("bendEvidenceGate") is True
        vibrato_gate = classifier_row.get("vibratoEvidenceGate") is True
        label_bend_gate = label_row.get("bendEvidenceGate") is True
        label_vibrato_gate = label_row.get("vibratoEvidenceGate") is True
        gates_match = (
            bend_gate == label_bend_gate
            and vibrato_gate == label_vibrato_gate
        )
        if not gates_match:
            calibration_mismatch_count += 1

        calibrated_bend_support = bool(
            gates_match
            and expected_bend_present
            and bend_gate
            and not vibrato_gate
        )
        calibrated_vibrato_support = bool(
            gates_match
            and expected_vibrato_present
            and vibrato_gate
            and not bend_gate
        )

        calibrated_row = {
            "measureNumber": classifier_row.get("measureNumber"),
            "quantizedStep": classifier_row.get("quantizedStep"),
            "sourceEventIndex": classifier_row.get("sourceEventIndex"),
            "evidenceClass": classifier_row.get("evidenceClass"),
            "bendEvidenceGate": bend_gate,
            "vibratoEvidenceGate": vibrato_gate,
            "classifierAndLabelBenchmarkGatesMatch": gates_match,
            "calibratedBendEvidenceSupportCandidate": calibrated_bend_support,
            "calibratedVibratoEvidenceSupportCandidate": calibrated_vibrato_support,
            "eventTechniqueLabelApplied": False,
            "sourceEventModified": False,
            "readOnly": True,
        }
        calibrated_rows.append(calibrated_row)
        if calibrated_bend_support:
            bend_supported_rows.append(calibrated_row)
        if calibrated_vibrato_support:
            vibrato_supported_rows.append(calibrated_row)

    observed_bend_candidate_count = int(
        classifier.get("bendEvidenceCandidateCount", -1)
    )
    observed_vibrato_candidate_count = int(
        classifier.get("vibratoEvidenceCandidateCount", -1)
    )
    bend_count_matches = len(bend_supported_rows) == observed_bend_candidate_count
    vibrato_count_matches = (
        len(vibrato_supported_rows) == observed_vibrato_candidate_count
    )

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    proof_pass = bool(
        source_unchanged
        and candidate_count_matches
        and row_keys_match
        and calibration_mismatch_count == 0
        and bend_count_matches
        and vibrato_count_matches
        and len(bend_supported_rows) > 0
        and len(vibrato_supported_rows) == 0
        and label_benchmark.get("techniqueFamilyMismatchCount") == 0
        and label_benchmark.get("ambiguousTechniqueEvidenceCount") == 0
    )

    recommended = (
        "build-read-only-technique-evidence-support-candidate-v1"
        if proof_pass
        else "diagnose-technique-evidence-calibration-proof-failures-v1"
    )

    output = {
        "schemaVersion": 1,
        "proofType": "read-only-professional-label-calibrated-technique-evidence-proof",
        "passed": proof_pass,
        "singleNoteCandidateCount": len(calibrated_rows),
        "candidateCountMatches": candidate_count_matches,
        "rowKeysMatch": row_keys_match,
        "calibrationMismatchCount": calibration_mismatch_count,
        "expectedBendPresent": expected_bend_present,
        "expectedVibratoPresent": expected_vibrato_present,
        "calibratedBendEvidenceSupportCandidateCount": len(bend_supported_rows),
        "calibratedVibratoEvidenceSupportCandidateCount": len(vibrato_supported_rows),
        "bendCandidateCountMatchesClassifier": bend_count_matches,
        "vibratoCandidateCountMatchesClassifier": vibrato_count_matches,
        "rows": calibrated_rows,
        "readyForReadOnlyTechniqueEvidenceSupportCandidate": proof_pass,
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
        "passed": proof_pass,
        "singleNoteCandidateCount": len(calibrated_rows),
        "calibrationMismatchCount": calibration_mismatch_count,
        "calibratedBendEvidenceSupportCandidateCount": len(bend_supported_rows),
        "calibratedVibratoEvidenceSupportCandidateCount": len(vibrato_supported_rows),
        "readyForReadOnlyTechniqueEvidenceSupportCandidate": proof_pass,
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

    print("GOMYWAY CHORUS 33-35 READ-ONLY TECHNIQUE EVIDENCE CALIBRATED PROOF V1 COMPLETE")
    print("Passed:", proof_pass)
    print("Single-note candidates:", len(calibrated_rows))
    print("Candidate count matches:", candidate_count_matches)
    print("Row keys match:", row_keys_match)
    print("Calibration mismatches:", calibration_mismatch_count)
    print("Expected bend present:", expected_bend_present)
    print("Expected vibrato present:", expected_vibrato_present)
    print("Calibrated bend support candidates:", len(bend_supported_rows))
    print("Calibrated vibrato support candidates:", len(vibrato_supported_rows))
    print("Bend candidate count matches classifier:", bend_count_matches)
    print("Vibrato candidate count matches classifier:", vibrato_count_matches)
    for row in bend_supported_rows + vibrato_supported_rows:
        print(
            f"measure={row.get('measureNumber')} "
            f"step={row.get('quantizedStep')} "
            f"bendSupportCandidate={row.get('calibratedBendEvidenceSupportCandidate')} "
            f"vibratoSupportCandidate={row.get('calibratedVibratoEvidenceSupportCandidate')} "
            f"class={row.get('evidenceClass')}"
        )
    print("Ready for read-only technique evidence support candidate:", proof_pass)
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

    if not proof_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
