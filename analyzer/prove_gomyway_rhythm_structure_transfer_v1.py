from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
VALIDATION_PATH = PUBLIC / "gomyway-rhythm-provisional-rule-transfer-evidence-v1.json"
REVIEW_PATH = PUBLIC / "gomyway-rhythm-provisional-rule-transfer-evidence-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-structure-transfer-proof-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-structure-transfer-proof-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_RHYTHM_SUBSET = [37, 70, 80, 88, 93, 94]
EXPECTED_CHORD_SUBSET = [37, 88]
EXPECTED_HELD_OUT = [101]

# Rhythm-transfer proof floors. These prove only rhythm-structure transfer.
# They never authorize chord, timing, technique, source mutation, or production use.
MIN_OCCUPIED_STEP_JACCARD = 0.60
MIN_ROW_DENSITY_SIMILARITY = 0.60
MIN_NOTE_DENSITY_SIMILARITY = 0.60


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
    review = load(REVIEW_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if validation.get("passed") is not True:
        raise RuntimeError("Provisional rule-transfer evidence validation V1 is not green.")
    if review.get("passed") is not True:
        raise RuntimeError("Provisional rule-transfer evidence review V1 is not green.")
    if review.get("readyForRhythmStructureTransferProof") is not True:
        raise RuntimeError("Review is not ready for rhythm-structure transfer proof.")
    if review.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Review unexpectedly allows threshold relaxation.")
    if review.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Review unexpectedly allows automatic application.")
    if review.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Review did not preserve protected source hash.")

    rhythm_subset = review.get("rhythmStructureSubset")
    chord_subset = review.get("chordShapeSubset")
    held_out = review.get("heldOutMeasures")
    if rhythm_subset != EXPECTED_RHYTHM_SUBSET:
        raise RuntimeError(f"Expected rhythm subset {EXPECTED_RHYTHM_SUBSET}, found {rhythm_subset}.")
    if chord_subset != EXPECTED_CHORD_SUBSET:
        raise RuntimeError(f"Expected chord subset {EXPECTED_CHORD_SUBSET}, found {chord_subset}.")
    if held_out != EXPECTED_HELD_OUT:
        raise RuntimeError(f"Expected held-out measures {EXPECTED_HELD_OUT}, found {held_out}.")

    raw_rows = validation.get("rows")
    if not isinstance(raw_rows, list):
        raise RuntimeError("Validation rows missing.")

    by_measure: dict[int, dict[str, Any]] = {}
    for row in raw_rows:
        if isinstance(row, dict):
            by_measure[integer(row, "measureNumber")] = row

    proof_rows: list[dict[str, Any]] = []
    for measure in EXPECTED_RHYTHM_SUBSET:
        row = by_measure.get(measure)
        if row is None:
            raise RuntimeError(f"Missing validation row for measure {measure}.")
        if row.get("rhythmStructureEvidenceSupported") is not True:
            raise RuntimeError(f"Measure {measure} lacks rhythm-structure evidence support.")

        occupied = number(row, "occupiedStepJaccard")
        row_density = number(row, "rowDensitySimilarity")
        note_density = number(row, "noteDensitySimilarity")

        gates = {
            "occupiedStepJaccard": occupied >= MIN_OCCUPIED_STEP_JACCARD,
            "rowDensitySimilarity": row_density >= MIN_ROW_DENSITY_SIMILARITY,
            "noteDensitySimilarity": note_density >= MIN_NOTE_DENSITY_SIMILARITY,
        }
        proved = all(gates.values())

        proof_rows.append(
            {
                "measureNumber": measure,
                "anchorMeasure": integer(row, "anchorMeasure"),
                "occupiedStepJaccard": occupied,
                "rowDensitySimilarity": row_density,
                "noteDensitySimilarity": note_density,
                "proofGates": gates,
                "rhythmStructureTransferProved": proved,
                "chordTransferProved": False,
                "timingTransferProved": False,
                "techniqueTransferProved": False,
                "automaticApplyAllowed": False,
            }
        )

    proved_measures = [
        row["measureNumber"] for row in proof_rows if row["rhythmStructureTransferProved"]
    ]
    rejected_measures = [
        row["measureNumber"] for row in proof_rows if not row["rhythmStructureTransferProved"]
    ]

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and len(proof_rows) == len(EXPECTED_RHYTHM_SUBSET)
        and not rejected_measures
    )

    recommended = (
        "review-gomyway-rhythm-structure-transfer-proof-v1"
        if passed
        else "diagnose-gomyway-rhythm-structure-transfer-proof-v1"
    )

    output = {
        "schemaVersion": 1,
        "proofType": "read-only-rhythm-structure-transfer-proof",
        "passed": passed,
        "candidateMeasures": EXPECTED_RHYTHM_SUBSET,
        "chordShapeSubset": EXPECTED_CHORD_SUBSET,
        "heldOutMeasures": EXPECTED_HELD_OUT,
        "proofFloors": {
            "occupiedStepJaccard": MIN_OCCUPIED_STEP_JACCARD,
            "rowDensitySimilarity": MIN_ROW_DENSITY_SIMILARITY,
            "noteDensitySimilarity": MIN_NOTE_DENSITY_SIMILARITY,
        },
        "rows": proof_rows,
        "rhythmStructureTransferProvedCount": len(proved_measures),
        "rhythmStructureTransferProvedMeasures": proved_measures,
        "rhythmStructureTransferRejectedMeasures": rejected_measures,
        "chordTransferClaimed": False,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "classificationClaimed": False,
        "automaticApplyAllowed": False,
        "readOnlyProof": True,
        "readyForRhythmStructureTransferReview": passed,
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
        "rhythmStructureTransferProvedCount": len(proved_measures),
        "rhythmStructureTransferProvedMeasures": proved_measures,
        "rhythmStructureTransferRejectedMeasures": rejected_measures,
        "classificationClaimed": False,
        "automaticApplyAllowed": False,
        "readyForRhythmStructureTransferReview": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM STRUCTURE TRANSFER PROOF V1 COMPLETE")
    print("Passed:", passed)
    print("Rhythm-structure candidates:", len(proof_rows), EXPECTED_RHYTHM_SUBSET)
    print("Rhythm-structure transfer proved:", len(proved_measures), proved_measures)
    print("Rhythm-structure transfer rejected:", len(rejected_measures), rejected_measures)
    for row in proof_rows:
        print(
            f"measure={row['measureNumber']} anchor={row['anchorMeasure']} "
            f"occupied={row['occupiedStepJaccard']} "
            f"rowDensity={row['rowDensitySimilarity']} "
            f"noteDensity={row['noteDensitySimilarity']} "
            f"proved={row['rhythmStructureTransferProved']}"
        )
    print("Chord transfer claimed: False")
    print("Timing transfer claimed: False")
    print("Technique transfer claimed: False")
    print("Classification claimed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for rhythm-structure transfer review:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
