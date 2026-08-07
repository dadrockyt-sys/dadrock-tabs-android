from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
DIAGNOSTIC_PATH = PUBLIC / "gomyway-rhythm-whole-song-learned-similarity-diagnostic-v1.json"
REVIEW_PATH = PUBLIC / "gomyway-rhythm-whole-song-similarity-calibration-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-whole-song-provisional-generalization-proof-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-whole-song-provisional-generalization-proof-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_CANDIDATES = [37, 70, 80, 88, 93, 94, 101]
EXPECTED_ANCHOR_MAP = {
    37: 27,
    70: 34,
    80: 35,
    88: 24,
    93: 27,
    94: 27,
    101: 24,
}

# These floors prove a structural relationship only. They do not authorize
# transferring chord, timing, bend, vibrato, or any other labels.
MIN_STRUCTURAL = 0.80
MIN_MUSICAL = 0.65
MIN_MARGIN = 0.02
MIN_OCCUPIED_STEP_JACCARD = 0.60
MIN_MULTIPLICITY_SIMILARITY = 0.60
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


def number(row: dict[str, Any], key: str) -> float:
    value = row.get(key)
    if isinstance(value, bool):
        raise RuntimeError(f"Unexpected boolean for {key}")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {value!r}") from exc


def integer(row: dict[str, Any], key: str) -> int:
    value = row.get(key)
    if isinstance(value, bool):
        raise RuntimeError(f"Unexpected boolean for {key}")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Missing/invalid {key}: {value!r}") from exc


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    diagnostic = load(DIAGNOSTIC_PATH)
    review = load(REVIEW_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if diagnostic.get("passed") is not True:
        raise RuntimeError("Whole-song learned similarity diagnostic V1 is not green.")
    if review.get("passed") is not True:
        raise RuntimeError("Similarity calibration review V1 is not green.")
    if review.get("readyForProvisionalGeneralizationProof") is not True:
        raise RuntimeError("Calibration review is not ready for provisional proof.")
    if review.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Calibration review unexpectedly allows automatic application.")
    if review.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Calibration review did not preserve protected source hash.")

    review_candidates = review.get("provisionalCandidateMeasures")
    if review_candidates != EXPECTED_CANDIDATES:
        raise RuntimeError(
            f"Expected provisional candidates {EXPECTED_CANDIDATES}, found {review_candidates}."
        )

    raw_rows = diagnostic.get("rows")
    if not isinstance(raw_rows, list):
        raise RuntimeError("Diagnostic rows missing.")

    by_measure: dict[int, dict[str, Any]] = {}
    for row in raw_rows:
        if isinstance(row, dict):
            by_measure[integer(row, "measureNumber")] = row

    proof_rows: list[dict[str, Any]] = []
    for measure in EXPECTED_CANDIDATES:
        row = by_measure.get(measure)
        if row is None:
            raise RuntimeError(f"Missing diagnostic row for measure {measure}.")

        anchor = integer(row, "bestAnchorMeasure")
        expected_anchor = EXPECTED_ANCHOR_MAP[measure]
        if anchor != expected_anchor:
            raise RuntimeError(
                f"Measure {measure} expected anchor {expected_anchor}, found {anchor}."
            )

        comparison = row.get("bestComparison")
        if not isinstance(comparison, dict):
            raise RuntimeError(f"Measure {measure} bestComparison missing.")

        structural = number(row, "bestStructuralSimilarityScore")
        musical = number(row, "bestMusicalSimilarityScore")
        margin = number(row, "bestVsRunnerUpMargin")
        occupied = number(comparison, "occupiedStepJaccard")
        multiplicity = number(comparison, "sharedStepMultiplicitySimilarity")
        row_density = number(comparison, "rowDensitySimilarity")
        note_density = number(comparison, "noteDensitySimilarity")
        pitch_class = number(comparison, "sharedStepPitchClassSimilarity")

        gates = {
            "structural": structural >= MIN_STRUCTURAL,
            "musical": musical >= MIN_MUSICAL,
            "margin": margin >= MIN_MARGIN,
            "occupiedStepJaccard": occupied >= MIN_OCCUPIED_STEP_JACCARD,
            "multiplicitySimilarity": multiplicity >= MIN_MULTIPLICITY_SIMILARITY,
            "rowDensitySimilarity": row_density >= MIN_ROW_DENSITY_SIMILARITY,
            "noteDensitySimilarity": note_density >= MIN_NOTE_DENSITY_SIMILARITY,
        }
        relationship_proved = all(gates.values())

        proof_rows.append(
            {
                "measureNumber": measure,
                "anchorMeasure": anchor,
                "runnerUpAnchorMeasure": integer(row, "runnerUpAnchorMeasure"),
                "structuralSimilarityScore": structural,
                "musicalSimilarityScore": musical,
                "bestVsRunnerUpMargin": margin,
                "occupiedStepJaccard": occupied,
                "sharedStepMultiplicitySimilarity": multiplicity,
                "rowDensitySimilarity": row_density,
                "noteDensitySimilarity": note_density,
                "sharedStepPitchClassSimilarity": pitch_class,
                "proofGates": gates,
                "provisionalGeneralizationRelationshipProved": relationship_proved,
                "rhythmRuleTransferAllowed": False,
                "chordRuleTransferAllowed": False,
                "timingRuleTransferAllowed": False,
                "techniqueRuleTransferAllowed": False,
                "automaticApplyAllowed": False,
            }
        )

    proved = [
        row["measureNumber"]
        for row in proof_rows
        if row["provisionalGeneralizationRelationshipProved"]
    ]
    rejected = [
        row["measureNumber"]
        for row in proof_rows
        if not row["provisionalGeneralizationRelationshipProved"]
    ]

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and len(proof_rows) == len(EXPECTED_CANDIDATES)
        and not rejected
    )

    recommended = (
        "validate-gomyway-rhythm-provisional-rule-transfer-evidence-v1"
        if passed
        else "review-gomyway-rhythm-whole-song-provisional-generalization-proof-v1"
    )

    output = {
        "schemaVersion": 1,
        "proofType": "read-only-whole-song-provisional-generalization-relationship-proof",
        "passed": passed,
        "candidateCount": len(proof_rows),
        "candidateMeasures": EXPECTED_CANDIDATES,
        "anchorMap": {str(measure): anchor for measure, anchor in EXPECTED_ANCHOR_MAP.items()},
        "relationshipProvedCount": len(proved),
        "relationshipProvedMeasures": proved,
        "relationshipRejectedCount": len(rejected),
        "relationshipRejectedMeasures": rejected,
        "proofFloors": {
            "structural": MIN_STRUCTURAL,
            "musical": MIN_MUSICAL,
            "margin": MIN_MARGIN,
            "occupiedStepJaccard": MIN_OCCUPIED_STEP_JACCARD,
            "multiplicitySimilarity": MIN_MULTIPLICITY_SIMILARITY,
            "rowDensitySimilarity": MIN_ROW_DENSITY_SIMILARITY,
            "noteDensitySimilarity": MIN_NOTE_DENSITY_SIMILARITY,
        },
        "rows": proof_rows,
        "classificationClaimed": False,
        "ruleTransferClaimed": False,
        "automaticApplyAllowed": False,
        "readOnlyProof": True,
        "readyForRuleTransferEvidenceValidation": passed,
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
        "candidateCount": len(proof_rows),
        "relationshipProvedCount": len(proved),
        "relationshipProvedMeasures": proved,
        "relationshipRejectedMeasures": rejected,
        "classificationClaimed": False,
        "ruleTransferClaimed": False,
        "automaticApplyAllowed": False,
        "readyForRuleTransferEvidenceValidation": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM WHOLE SONG PROVISIONAL GENERALIZATION PROOF V1 COMPLETE")
    print("Passed:", passed)
    print("Candidates proved:", len(proved), proved)
    print("Candidates rejected:", len(rejected), rejected)
    for row in proof_rows:
        print(
            f"measure={row['measureNumber']} anchor={row['anchorMeasure']} "
            f"structural={row['structuralSimilarityScore']} "
            f"musical={row['musicalSimilarityScore']} "
            f"margin={row['bestVsRunnerUpMargin']} "
            f"occupied={row['occupiedStepJaccard']} "
            f"multiplicity={row['sharedStepMultiplicitySimilarity']} "
            f"rowDensity={row['rowDensitySimilarity']} "
            f"noteDensity={row['noteDensitySimilarity']} "
            f"pitchClass={row['sharedStepPitchClassSimilarity']} "
            f"proved={row['provisionalGeneralizationRelationshipProved']}"
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
    print("Ready for rule-transfer evidence validation:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
