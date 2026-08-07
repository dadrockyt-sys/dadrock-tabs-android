from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
PROOF_PATH = PUBLIC / "gomyway-rhythm-whole-song-provisional-generalization-proof-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-whole-song-provisional-generalization-proof-review-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-whole-song-provisional-generalization-proof-review-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
EXPECTED_PROVED = [37, 70, 80, 88, 93, 94]
EXPECTED_HELD_OUT = [101]
EXPECTED_HELD_OUT_ANCHOR = 24


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


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    proof = load(PROOF_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if proof.get("classificationClaimed") is not False:
        raise RuntimeError("Proof unexpectedly claimed classification.")
    if proof.get("ruleTransferClaimed") is not False:
        raise RuntimeError("Proof unexpectedly claimed rule transfer.")
    if proof.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Proof unexpectedly allows automatic application.")
    if proof.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Proof did not preserve protected source hash.")

    proved = proof.get("relationshipProvedMeasures")
    rejected = proof.get("relationshipRejectedMeasures")
    rows = proof.get("rows")

    if proved != EXPECTED_PROVED:
        raise RuntimeError(f"Expected proved measures {EXPECTED_PROVED}, found {proved}.")
    if rejected != EXPECTED_HELD_OUT:
        raise RuntimeError(f"Expected held-out measure {EXPECTED_HELD_OUT}, found {rejected}.")
    if not isinstance(rows, list):
        raise RuntimeError("Proof rows missing.")

    held_out_row: dict[str, Any] | None = None
    for row in rows:
        if isinstance(row, dict) and row.get("measureNumber") == 101:
            held_out_row = row
            break
    if held_out_row is None:
        raise RuntimeError("Measure 101 proof row missing.")

    if held_out_row.get("anchorMeasure") != EXPECTED_HELD_OUT_ANCHOR:
        raise RuntimeError("Measure 101 anchor changed unexpectedly.")

    gates = held_out_row.get("proofGates")
    if not isinstance(gates, dict):
        raise RuntimeError("Measure 101 proof gates missing.")

    failed_gates = sorted(key for key, value in gates.items() if value is not True)
    if failed_gates != ["occupiedStepJaccard"]:
        raise RuntimeError(
            f"Measure 101 expected only occupiedStepJaccard to fail, found {failed_gates}."
        )

    occupied = float(held_out_row.get("occupiedStepJaccard", 0.0))
    structural = float(held_out_row.get("structuralSimilarityScore", 0.0))
    musical = float(held_out_row.get("musicalSimilarityScore", 0.0))
    margin = float(held_out_row.get("bestVsRunnerUpMargin", 0.0))
    multiplicity = float(held_out_row.get("sharedStepMultiplicitySimilarity", 0.0))
    row_density = float(held_out_row.get("rowDensitySimilarity", 0.0))
    note_density = float(held_out_row.get("noteDensitySimilarity", 0.0))

    # Review conclusion: preserve the six proved relationships. Measure 101 is not
    # promoted and the occupied-step floor is not weakened. Its strong density and
    # multiplicity evidence justify only a separate read-only rhythm-placement diagnosis.
    held_out_reason = "occupied-step-structure-below-proof-floor"
    threshold_relaxation_allowed = False
    proved_subset_ready = bool(len(EXPECTED_PROVED) == 6)

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(
        source_unchanged
        and failed_gates == ["occupiedStepJaccard"]
        and occupied < 0.60
        and structural >= 0.80
        and musical >= 0.65
        and margin >= 0.02
        and multiplicity >= 0.60
        and row_density >= 0.60
        and note_density >= 0.60
    )

    recommended = (
        "validate-gomyway-rhythm-provisional-rule-transfer-evidence-v1"
        if passed and proved_subset_ready
        else "review-gomyway-rhythm-whole-song-provisional-generalization-proof-v1"
    )

    output = {
        "schemaVersion": 1,
        "reviewType": "read-only-provisional-generalization-proof-review",
        "passed": passed,
        "proofPassedAsAllCandidates": False,
        "provedRelationshipMeasures": EXPECTED_PROVED,
        "provedRelationshipCount": len(EXPECTED_PROVED),
        "heldOutMeasures": EXPECTED_HELD_OUT,
        "heldOutCount": len(EXPECTED_HELD_OUT),
        "heldOutReview": {
            "measureNumber": 101,
            "anchorMeasure": EXPECTED_HELD_OUT_ANCHOR,
            "failedProofGates": failed_gates,
            "heldOutReason": held_out_reason,
            "structuralSimilarityScore": structural,
            "musicalSimilarityScore": musical,
            "bestVsRunnerUpMargin": margin,
            "occupiedStepJaccard": occupied,
            "sharedStepMultiplicitySimilarity": multiplicity,
            "rowDensitySimilarity": row_density,
            "noteDensitySimilarity": note_density,
            "thresholdRelaxationAllowed": threshold_relaxation_allowed,
            "relationshipProved": False,
            "ruleTransferAllowed": False,
            "automaticApplyAllowed": False,
        },
        "provedSubsetReadyForRuleTransferEvidenceValidation": passed and proved_subset_ready,
        "heldOutReadyForRhythmPlacementDiagnosis": passed,
        "classificationClaimed": False,
        "ruleTransferClaimed": False,
        "automaticApplyAllowed": False,
        "thresholdRelaxationAllowed": False,
        "readOnlyReview": True,
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
        "provedRelationshipMeasures": EXPECTED_PROVED,
        "heldOutMeasures": EXPECTED_HELD_OUT,
        "heldOutReason": held_out_reason,
        "thresholdRelaxationAllowed": False,
        "provedSubsetReadyForRuleTransferEvidenceValidation": passed and proved_subset_ready,
        "heldOutReadyForRhythmPlacementDiagnosis": passed,
        "classificationClaimed": False,
        "ruleTransferClaimed": False,
        "automaticApplyAllowed": False,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM WHOLE SONG PROVISIONAL GENERALIZATION PROOF REVIEW V1 COMPLETE")
    print("Passed:", passed)
    print("Proved relationships preserved:", len(EXPECTED_PROVED), EXPECTED_PROVED)
    print("Held out:", EXPECTED_HELD_OUT)
    print("Measure 101 anchor:", EXPECTED_HELD_OUT_ANCHOR)
    print("Measure 101 failed proof gates:", failed_gates)
    print("Measure 101 occupied-step Jaccard:", occupied)
    print("Threshold relaxation allowed: False")
    print("Proved subset ready for rule-transfer evidence validation:", passed and proved_subset_ready)
    print("Held-out measure ready for rhythm-placement diagnosis:", passed)
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
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
