from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
FIXTURES = ROOT / "analyzer" / "fixtures"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
CLASSIFIER_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-classifier-v1.json"
PROFESSIONAL_LABEL_PATH = FIXTURES / "gomyway2_full_tab_reference.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-technique-evidence-professional-label-benchmark-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-technique-evidence-professional-label-benchmark-v1-manifest.json"


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


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    classifier = load(CLASSIFIER_PATH)
    professional = load(PROFESSIONAL_LABEL_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if classifier.get("passed") is not True:
        raise RuntimeError("Technique evidence classifier is not green.")
    if classifier.get("readyForProfessionalLabelEvidenceBenchmark") is not True:
        raise RuntimeError("Classifier did not authorize professional-label benchmarking.")
    if classifier.get("recommendedNextAction") != (
        "build-read-only-technique-evidence-professional-label-benchmark-v1"
    ):
        raise RuntimeError("Unexpected classifier recommendation.")

    rhythm_label = ((professional.get("parts") or {}).get("rhythm") or {})
    required_techniques = {
        str(value).strip().lower()
        for value in rhythm_label.get("requiredTechniques", [])
        if str(value).strip()
    }
    if not required_techniques:
        raise RuntimeError("Professional rhythm label contains no required techniques.")

    # The supplied professional fixture is a part-level training label rather
    # than an event-by-event measure/step transcription. This benchmark tests
    # only presence/absence of the bend and vibrato technique families. It does
    # not copy reference notes, frets, timing, or labels into source events.
    expected_bend_present = "bend" in required_techniques
    expected_vibrato_present = "vibrato" in required_techniques
    release_label_present = "release" in required_techniques

    rows = [row for row in classifier.get("rows", []) if isinstance(row, dict)]
    expected_count = int(classifier.get("singleNoteCandidateCount", -1))
    count_matches = len(rows) == expected_count

    bend_rows = [row for row in rows if row.get("bendEvidenceGate") is True]
    vibrato_rows = [row for row in rows if row.get("vibratoEvidenceGate") is True]
    ambiguous_rows = [
        row for row in rows
        if row.get("bendEvidenceGate") is True
        and row.get("vibratoEvidenceGate") is True
    ]

    observed_bend_present = bool(bend_rows)
    observed_vibrato_present = bool(vibrato_rows)
    bend_label_match = observed_bend_present == expected_bend_present
    vibrato_label_match = observed_vibrato_present == expected_vibrato_present
    ambiguity_gate = len(ambiguous_rows) == 0

    benchmark_rows: list[dict[str, Any]] = []
    for row in rows:
        benchmark_rows.append({
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": row.get("sourceEventIndex"),
            "evidenceClass": row.get("evidenceClass"),
            "bendEvidenceGate": row.get("bendEvidenceGate") is True,
            "vibratoEvidenceGate": row.get("vibratoEvidenceGate") is True,
            "professionalLabelScope": "rhythm-part-level-technique-family",
            "professionalEventLocalLabelAvailable": False,
            "professionalNotesCopiedIntoProtectedSource": False,
            "bendSupportClaimed": False,
            "vibratoSupportClaimed": False,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        })

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    benchmark_pass = bool(
        source_unchanged
        and count_matches
        and len(rows) > 0
        and bend_label_match
        and vibrato_label_match
        and ambiguity_gate
    )

    mismatch_count = int(not bend_label_match) + int(not vibrato_label_match)
    recommended = (
        "build-read-only-technique-evidence-calibrated-proof-v1"
        if benchmark_pass
        else "diagnose-technique-evidence-professional-label-mismatches-v1"
    )

    output = {
        "schemaVersion": 1,
        "benchmarkType": "read-only-professional-part-label-technique-evidence-benchmark",
        "passed": benchmark_pass,
        "singleNoteCandidateCount": len(rows),
        "candidateCountMatches": count_matches,
        "professionalLabelPath": str(PROFESSIONAL_LABEL_PATH.relative_to(ROOT)),
        "professionalLabelScope": "rhythm-part-level-technique-family",
        "professionalEventLocalLabelsAvailable": False,
        "professionalRequiredTechniques": sorted(required_techniques),
        "releaseLabelPresentButOutOfClassifierScope": release_label_present,
        "expectedBendPresent": expected_bend_present,
        "observedBendEvidencePresent": observed_bend_present,
        "bendEvidenceCandidateCount": len(bend_rows),
        "bendProfessionalLabelMatch": bend_label_match,
        "expectedVibratoPresent": expected_vibrato_present,
        "observedVibratoEvidencePresent": observed_vibrato_present,
        "vibratoEvidenceCandidateCount": len(vibrato_rows),
        "vibratoProfessionalLabelMatch": vibrato_label_match,
        "ambiguousTechniqueEvidenceCount": len(ambiguous_rows),
        "ambiguityGate": ambiguity_gate,
        "techniqueFamilyMismatchCount": mismatch_count,
        "rows": benchmark_rows,
        "readyForCalibratedTechniqueEvidenceProof": benchmark_pass,
        "recommendedNextAction": recommended,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoProtectedSource": False,
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
        "passed": benchmark_pass,
        "singleNoteCandidateCount": len(rows),
        "bendEvidenceCandidateCount": len(bend_rows),
        "vibratoEvidenceCandidateCount": len(vibrato_rows),
        "techniqueFamilyMismatchCount": mismatch_count,
        "readyForCalibratedTechniqueEvidenceProof": benchmark_pass,
        "recommendedNextAction": recommended,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoProtectedSource": False,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 TECHNIQUE EVIDENCE PROFESSIONAL-LABEL BENCHMARK V1 COMPLETE")
    print("Passed:", benchmark_pass)
    print("Single-note candidates:", len(rows))
    print("Candidate count matches:", count_matches)
    print("Professional label scope: rhythm-part-level-technique-family")
    print("Professional required techniques:", sorted(required_techniques))
    print("Expected bend present:", expected_bend_present)
    print("Observed bend evidence present:", observed_bend_present)
    print("Bend evidence candidates:", len(bend_rows))
    print("Bend professional-label match:", bend_label_match)
    print("Expected vibrato present:", expected_vibrato_present)
    print("Observed vibrato evidence present:", observed_vibrato_present)
    print("Vibrato evidence candidates:", len(vibrato_rows))
    print("Vibrato professional-label match:", vibrato_label_match)
    print("Ambiguous technique evidence:", len(ambiguous_rows))
    print("Technique-family mismatches:", mismatch_count)
    for row in bend_rows + vibrato_rows:
        print(
            f"measure={row.get('measureNumber')} step={row.get('quantizedStep')} "
            f"bendGate={row.get('bendEvidenceGate') is True} "
            f"vibratoGate={row.get('vibratoEvidenceGate') is True} "
            f"class={row.get('evidenceClass')}"
        )
    print("Ready for calibrated technique evidence proof:", benchmark_pass)
    print("Recommended next action:", recommended)
    print("Professional reference used as training label only: True")
    print("Professional notes copied into protected source: False")
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

    if not benchmark_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
