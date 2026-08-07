from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
VALIDATION_PATH = PUBLIC / "gomyway-rhythm-provisional-rule-transfer-evidence-v1.json"
RHYTHM_REVIEW_PATH = PUBLIC / "gomyway-rhythm-structure-transfer-proof-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chord-shape-transfer-proof-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chord-shape-transfer-proof-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_CHORD_SUBSET = [37, 88]
EXPECTED_ANCHORS = {37: 27, 88: 24}
EXPECTED_RHYTHM_CLOSED = [37, 70, 80, 88, 93, 94]
EXPECTED_HELD_OUT = [101]

# Chord-shape proof floors. These prove only chord-shape transfer evidence.
# They never authorize timing, technique, source mutation, automatic application,
# protected baseline changes, or production promotion.
MIN_MULTIPLICITY_SIMILARITY = 0.75
MIN_PITCH_CLASS_SIMILARITY = 0.10


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
    validation = load(VALIDATION_PATH)
    rhythm_review = load(RHYTHM_REVIEW_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if validation.get("passed") is not True:
        raise RuntimeError("Provisional rule-transfer evidence validation V1 is not green.")
    if validation.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Validation unexpectedly allows automatic application.")
    if validation.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Validation did not preserve protected source hash.")

    if rhythm_review.get("passed") is not True:
        raise RuntimeError("Rhythm-structure transfer proof review V1 is not green.")
    if rhythm_review.get("rhythmStructureTransferClosedReadOnly") is not True:
        raise RuntimeError("Rhythm-structure transfer subset is not formally closed read-only.")
    if rhythm_review.get("rhythmStructureClosedMeasures") != EXPECTED_RHYTHM_CLOSED:
        raise RuntimeError("Closed rhythm-structure measure set changed unexpectedly.")
    if rhythm_review.get("chordShapePendingMeasures") != EXPECTED_CHORD_SUBSET:
        raise RuntimeError("Pending chord-shape subset changed unexpectedly.")
    if rhythm_review.get("heldOutMeasures") != EXPECTED_HELD_OUT:
        raise RuntimeError("Held-out measure set changed unexpectedly.")
    if rhythm_review.get("readyForChordShapeTransferProof") is not True:
        raise RuntimeError("Rhythm review is not ready for chord-shape transfer proof.")
    if rhythm_review.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Rhythm review unexpectedly allows threshold relaxation.")
    if rhythm_review.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Rhythm review unexpectedly allows automatic application.")

    if validation.get("chordShapeEvidenceSupportedMeasures") != EXPECTED_CHORD_SUBSET:
        raise RuntimeError(
            f"Expected chord-supported measures {EXPECTED_CHORD_SUBSET}, found "
            f"{validation.get('chordShapeEvidenceSupportedMeasures')}."
        )

    raw_rows = validation.get("rows")
    if not isinstance(raw_rows, list):
        raise RuntimeError("Validation rows missing.")

    by_measure: dict[int, dict[str, Any]] = {}
    for row in raw_rows:
        if isinstance(row, dict):
            by_measure[integer(row, "measureNumber")] = row

    proof_rows: list[dict[str, Any]] = []
    for measure in EXPECTED_CHORD_SUBSET:
        row = by_measure.get(measure)
        if row is None:
            raise RuntimeError(f"Missing validation row for measure {measure}.")
        if row.get("chordShapeEvidenceSupported") is not True:
            raise RuntimeError(f"Measure {measure} lacks chord-shape evidence support.")

        anchor = integer(row, "anchorMeasure")
        if anchor != EXPECTED_ANCHORS[measure]:
            raise RuntimeError(
                f"Measure {measure} expected anchor {EXPECTED_ANCHORS[measure]}, found {anchor}."
            )

        multiplicity = number(row, "sharedStepMultiplicitySimilarity")
        pitch_class = number(row, "sharedStepPitchClassSimilarity")
        gates = {
            "multiplicitySimilarity": multiplicity >= MIN_MULTIPLICITY_SIMILARITY,
            "pitchClassSimilarity": pitch_class >= MIN_PITCH_CLASS_SIMILARITY,
        }
        proved = all(gates.values())

        proof_rows.append(
            {
                "measureNumber": measure,
                "anchorMeasure": anchor,
                "sharedStepMultiplicitySimilarity": multiplicity,
                "sharedStepPitchClassSimilarity": pitch_class,
                "proofGates": gates,
                "chordShapeTransferProved": proved,
                "timingTransferProved": False,
                "techniqueTransferProved": False,
                "automaticApplyAllowed": False,
            }
        )

    proved_measures = [
        row["measureNumber"] for row in proof_rows if row["chordShapeTransferProved"]
    ]
    rejected_measures = [
        row["measureNumber"] for row in proof_rows if not row["chordShapeTransferProved"]
    ]

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and len(proof_rows) == len(EXPECTED_CHORD_SUBSET)
        and not rejected_measures
    )

    recommended = (
        "review-gomyway-chord-shape-transfer-proof-v1"
        if passed
        else "diagnose-gomyway-chord-shape-transfer-proof-v1"
    )

    output = {
        "schemaVersion": 1,
        "proofType": "read-only-chord-shape-transfer-proof",
        "passed": passed,
        "candidateMeasures": EXPECTED_CHORD_SUBSET,
        "anchorMap": {str(measure): anchor for measure, anchor in EXPECTED_ANCHORS.items()},
        "rhythmStructureClosedMeasures": EXPECTED_RHYTHM_CLOSED,
        "heldOutMeasures": EXPECTED_HELD_OUT,
        "proofFloors": {
            "multiplicitySimilarity": MIN_MULTIPLICITY_SIMILARITY,
            "pitchClassSimilarity": MIN_PITCH_CLASS_SIMILARITY,
        },
        "rows": proof_rows,
        "chordShapeTransferProvedCount": len(proved_measures),
        "chordShapeTransferProvedMeasures": proved_measures,
        "chordShapeTransferRejectedMeasures": rejected_measures,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "classificationClaimed": False,
        "automaticApplyAllowed": False,
        "thresholdRelaxationAllowed": False,
        "readOnlyProof": True,
        "readyForChordShapeTransferReview": passed,
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
        "chordShapeTransferProvedCount": len(proved_measures),
        "chordShapeTransferProvedMeasures": proved_measures,
        "chordShapeTransferRejectedMeasures": rejected_measures,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "classificationClaimed": False,
        "automaticApplyAllowed": False,
        "thresholdRelaxationAllowed": False,
        "readyForChordShapeTransferReview": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORD SHAPE TRANSFER PROOF V1 COMPLETE")
    print("Passed:", passed)
    print("Chord-shape candidates:", len(proof_rows), EXPECTED_CHORD_SUBSET)
    print("Chord-shape transfer proved:", len(proved_measures), proved_measures)
    print("Chord-shape transfer rejected:", len(rejected_measures), rejected_measures)
    for row in proof_rows:
        print(
            f"measure={row['measureNumber']} anchor={row['anchorMeasure']} "
            f"multiplicity={row['sharedStepMultiplicitySimilarity']} "
            f"pitchClass={row['sharedStepPitchClassSimilarity']} "
            f"proved={row['chordShapeTransferProved']}"
        )
    print("Timing transfer claimed: False")
    print("Technique transfer claimed: False")
    print("Classification claimed: False")
    print("Automatic apply allowed: False")
    print("Threshold relaxation allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for chord-shape transfer review:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
