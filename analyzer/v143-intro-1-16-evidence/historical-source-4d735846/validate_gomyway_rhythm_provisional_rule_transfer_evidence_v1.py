from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
PROOF_PATH = PUBLIC / "gomyway-rhythm-whole-song-provisional-generalization-proof-v1.json"
REVIEW_PATH = PUBLIC / "gomyway-rhythm-whole-song-provisional-generalization-proof-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-provisional-rule-transfer-evidence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-provisional-rule-transfer-evidence-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_PROVED = [37, 70, 80, 88, 93, 94]
EXPECTED_HELD_OUT = [101]

# Domain-specific evidence floors. These authorize only read-only evidence claims,
# never mutation or automatic transfer.
RHYTHM_MIN_OCCUPIED = 0.60
RHYTHM_MIN_ROW_DENSITY = 0.60
RHYTHM_MIN_NOTE_DENSITY = 0.60
CHORD_MIN_MULTIPLICITY = 0.75
CHORD_MIN_PITCH_CLASS = 0.10


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def integer(row: dict[str, Any], key: str) -> int:
    value = row.get(key)
    if isinstance(value, bool):
        raise RuntimeError(f"Unexpected boolean for {key}")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {value!r}") from exc


def number(row: dict[str, Any], key: str) -> float:
    value = row.get(key)
    if isinstance(value, bool):
        raise RuntimeError(f"Unexpected boolean for {key}")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {value!r}") from exc


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    proof = load(PROOF_PATH)
    review = load(REVIEW_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if review.get("passed") is not True:
        raise RuntimeError("Provisional generalization proof review V1 is not green.")
    if review.get("provedSubsetReadyForRuleTransferEvidenceValidation") is not True:
        raise RuntimeError("Proved subset is not ready for rule-transfer evidence validation.")
    if review.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Proof review unexpectedly allows threshold relaxation.")
    if review.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Proof review unexpectedly allows automatic application.")
    if review.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Proof review did not preserve protected source hash.")

    proved = review.get("provedRelationshipMeasures")
    held_out = review.get("heldOutMeasures")
    if proved != EXPECTED_PROVED:
        raise RuntimeError(f"Expected proved subset {EXPECTED_PROVED}, found {proved}.")
    if held_out != EXPECTED_HELD_OUT:
        raise RuntimeError(f"Expected held-out measures {EXPECTED_HELD_OUT}, found {held_out}.")

    raw_rows = proof.get("rows")
    if not isinstance(raw_rows, list):
        raise RuntimeError("Generalization proof rows missing.")

    by_measure: dict[int, dict[str, Any]] = {}
    for row in raw_rows:
        if isinstance(row, dict):
            by_measure[integer(row, "measureNumber")] = row

    validation_rows: list[dict[str, Any]] = []
    for measure in EXPECTED_PROVED:
        row = by_measure.get(measure)
        if row is None:
            raise RuntimeError(f"Missing proof row for measure {measure}.")
        if row.get("provisionalGeneralizationRelationshipProved") is not True:
            raise RuntimeError(f"Measure {measure} is not marked proved in proof artifact.")

        occupied = number(row, "occupiedStepJaccard")
        multiplicity = number(row, "sharedStepMultiplicitySimilarity")
        row_density = number(row, "rowDensitySimilarity")
        note_density = number(row, "noteDensitySimilarity")
        pitch_class = number(row, "sharedStepPitchClassSimilarity")

        rhythm_evidence = bool(
            occupied >= RHYTHM_MIN_OCCUPIED
            and row_density >= RHYTHM_MIN_ROW_DENSITY
            and note_density >= RHYTHM_MIN_NOTE_DENSITY
        )
        chord_evidence = bool(
            multiplicity >= CHORD_MIN_MULTIPLICITY
            and pitch_class >= CHORD_MIN_PITCH_CLASS
        )

        validation_rows.append(
            {
                "measureNumber": measure,
                "anchorMeasure": integer(row, "anchorMeasure"),
                "occupiedStepJaccard": occupied,
                "sharedStepMultiplicitySimilarity": multiplicity,
                "rowDensitySimilarity": row_density,
                "noteDensitySimilarity": note_density,
                "sharedStepPitchClassSimilarity": pitch_class,
                "rhythmStructureEvidenceSupported": rhythm_evidence,
                "chordShapeEvidenceSupported": chord_evidence,
                "timingTransferEvidenceSupported": False,
                "timingTransferEvidenceReason": "structural-similarity-alone-does-not-prove-timing-transfer",
                "techniqueTransferEvidenceSupported": False,
                "techniqueTransferEvidenceReason": "no-explicit-candidate-technique-evidence-validated",
                "rhythmRuleTransferAllowed": False,
                "chordRuleTransferAllowed": False,
                "timingRuleTransferAllowed": False,
                "techniqueRuleTransferAllowed": False,
                "automaticApplyAllowed": False,
            }
        )

    rhythm_supported = [
        row["measureNumber"] for row in validation_rows if row["rhythmStructureEvidenceSupported"]
    ]
    chord_supported = [
        row["measureNumber"] for row in validation_rows if row["chordShapeEvidenceSupported"]
    ]
    rhythm_unsupported = [
        row["measureNumber"] for row in validation_rows if not row["rhythmStructureEvidenceSupported"]
    ]
    chord_unsupported = [
        row["measureNumber"] for row in validation_rows if not row["chordShapeEvidenceSupported"]
    ]

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and len(validation_rows) == len(EXPECTED_PROVED)
        and not rhythm_unsupported
    )

    recommended = (
        "review-gomyway-rhythm-provisional-rule-transfer-evidence-v1"
        if passed
        else "diagnose-gomyway-rhythm-provisional-rule-transfer-evidence-v1"
    )

    output = {
        "schemaVersion": 1,
        "validationType": "read-only-provisional-rhythm-domain-rule-transfer-evidence",
        "passed": passed,
        "provedRelationshipMeasures": EXPECTED_PROVED,
        "heldOutMeasures": EXPECTED_HELD_OUT,
        "rhythmEvidenceFloors": {
            "occupiedStepJaccard": RHYTHM_MIN_OCCUPIED,
            "rowDensitySimilarity": RHYTHM_MIN_ROW_DENSITY,
            "noteDensitySimilarity": RHYTHM_MIN_NOTE_DENSITY,
        },
        "chordEvidenceFloors": {
            "multiplicitySimilarity": CHORD_MIN_MULTIPLICITY,
            "pitchClassSimilarity": CHORD_MIN_PITCH_CLASS,
        },
        "rows": validation_rows,
        "rhythmStructureEvidenceSupportedCount": len(rhythm_supported),
        "rhythmStructureEvidenceSupportedMeasures": rhythm_supported,
        "rhythmStructureEvidenceUnsupportedMeasures": rhythm_unsupported,
        "chordShapeEvidenceSupportedCount": len(chord_supported),
        "chordShapeEvidenceSupportedMeasures": chord_supported,
        "chordShapeEvidenceUnsupportedMeasures": chord_unsupported,
        "timingTransferEvidenceSupportedCount": 0,
        "techniqueTransferEvidenceSupportedCount": 0,
        "classificationClaimed": False,
        "ruleTransferClaimed": False,
        "automaticApplyAllowed": False,
        "readOnlyValidation": True,
        "readyForRuleTransferEvidenceReview": passed,
        "recommendedNextAction": recommended,
        "protectedSourceEventCount": len(events),
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
        "provedRelationshipCount": len(EXPECTED_PROVED),
        "rhythmStructureEvidenceSupportedCount": len(rhythm_supported),
        "chordShapeEvidenceSupportedCount": len(chord_supported),
        "timingTransferEvidenceSupportedCount": 0,
        "techniqueTransferEvidenceSupportedCount": 0,
        "classificationClaimed": False,
        "ruleTransferClaimed": False,
        "automaticApplyAllowed": False,
        "readyForRuleTransferEvidenceReview": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM PROVISIONAL RULE-TRANSFER EVIDENCE VALIDATION V1 COMPLETE")
    print("Passed:", passed)
    print("Proved relationships validated:", len(validation_rows), EXPECTED_PROVED)
    print("Held out from validation:", EXPECTED_HELD_OUT)
    print("Rhythm-structure evidence supported:", len(rhythm_supported), rhythm_supported)
    print("Rhythm-structure evidence unsupported:", len(rhythm_unsupported), rhythm_unsupported)
    print("Chord-shape evidence supported:", len(chord_supported), chord_supported)
    print("Chord-shape evidence unsupported:", len(chord_unsupported), chord_unsupported)
    print("Timing-transfer evidence supported: 0")
    print("Technique-transfer evidence supported: 0")
    for row in validation_rows:
        print(
            f"measure={row['measureNumber']} anchor={row['anchorMeasure']} "
            f"occupied={row['occupiedStepJaccard']} "
            f"multiplicity={row['sharedStepMultiplicitySimilarity']} "
            f"rowDensity={row['rowDensitySimilarity']} "
            f"noteDensity={row['noteDensitySimilarity']} "
            f"pitchClass={row['sharedStepPitchClassSimilarity']} "
            f"rhythmEvidence={row['rhythmStructureEvidenceSupported']} "
            f"chordEvidence={row['chordShapeEvidenceSupported']}"
        )
    print("Classification claimed: False")
    print("Rule transfer claimed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for rule-transfer evidence review:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
