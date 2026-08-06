from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
CANDIDATE_PATH = PUBLIC / "gomyway-chorus-33-35-recomputed-corrected-pitch-quality-candidate-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-final-post-correction-pitch-proof-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-final-post-correction-pitch-proof-v1-manifest.json"


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
    candidate = load(CANDIDATE_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if candidate.get("passed") is not True:
        raise RuntimeError("Recomputed corrected pitch-quality candidate is not green.")
    if candidate.get("readyForFinalPostCorrectionPlausibilityProof") is not True:
        raise RuntimeError("Candidate did not authorize the final post-correction proof.")

    rows = [row for row in candidate.get("rows", []) if isinstance(row, dict)]
    expected_count = int(candidate.get("singleNoteCandidateCount", -1))

    failed_rows: list[dict[str, Any]] = []
    changed_rows: list[dict[str, Any]] = []
    for row in rows:
        final_gate = row.get("correctedPitchQualityGate") is True
        if not final_gate:
            failed_rows.append(row)
        if row.get("qualityGateChanged") is True:
            changed_rows.append(row)

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    count_matches = len(rows) == expected_count
    all_pass = bool(rows and count_matches and not failed_rows)
    ready = bool(source_unchanged and all_pass)

    proof_rows = [
        {
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": row.get("sourceEventIndex"),
            "oldQualityGate": row.get("oldCorrectedPitchQualityGate"),
            "newQualityGate": row.get("correctedPitchQualityGate"),
            "qualityGateChanged": row.get("qualityGateChanged") is True,
            "featureQualityGate": row.get("featureQualityGate"),
            "frameCountGate": row.get("frameCountGate"),
            "correctedRangePlausibilityGate": row.get("correctedRangePlausibilityGate"),
            "correctedMedianJumpPlausibilityGate": row.get("correctedMedianJumpPlausibilityGate"),
            "correctedRobustPitchRangeCents": row.get("correctedRobustPitchRangeCents"),
            "correctedMedianContiguousJumpCents": row.get("correctedMedianContiguousJumpCents"),
            "finalPostCorrectionPitchProofGate": row.get("correctedPitchQualityGate") is True,
            "bendSupportClaimed": False,
            "vibratoSupportClaimed": False,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        }
        for row in rows
    ]

    output = {
        "schemaVersion": 1,
        "proofType": "read-only-final-post-correction-pitch-quality-proof",
        "passed": ready,
        "singleNoteCandidateCount": len(rows),
        "expectedSingleNoteCandidateCount": expected_count,
        "candidateCountMatches": count_matches,
        "qualityGateChangeCount": len(changed_rows),
        "finalPitchQualityGatePassedCount": len(rows) - len(failed_rows),
        "finalPitchQualityGateFailedCount": len(failed_rows),
        "allCorrectedPitchQualityGatesPassed": all_pass,
        "rows": proof_rows,
        "readyForTechniqueEvidenceClassification": ready,
        "recommendedNextAction": (
            "build-read-only-technique-evidence-classifier-v1"
            if ready
            else "diagnose-final-post-correction-pitch-proof-failures"
        ),
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
        "passed": ready,
        "singleNoteCandidateCount": len(rows),
        "qualityGateChangeCount": len(changed_rows),
        "finalPitchQualityGatePassedCount": len(rows) - len(failed_rows),
        "finalPitchQualityGateFailedCount": len(failed_rows),
        "allCorrectedPitchQualityGatesPassed": all_pass,
        "readyForTechniqueEvidenceClassification": ready,
        "recommendedNextAction": output["recommendedNextAction"],
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 FINAL POST-CORRECTION PITCH PROOF V1 COMPLETE")
    print("Passed:", ready)
    print("Single-note candidates:", len(rows))
    print("Candidate count matches:", count_matches)
    print("Quality gate changes preserved:", len(changed_rows))
    print("Final pitch quality gates passed:", len(rows) - len(failed_rows))
    print("Final pitch quality gates failed:", len(failed_rows))
    print("All corrected pitch quality gates passed:", all_pass)
    for row in proof_rows:
        if not row["qualityGateChanged"]:
            continue
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"oldGate={row['oldQualityGate']} newGate={row['newQualityGate']} "
            f"featureGate={row['featureQualityGate']} "
            f"frameGate={row['frameCountGate']} "
            f"rangeGate={row['correctedRangePlausibilityGate']} "
            f"jumpGate={row['correctedMedianJumpPlausibilityGate']} "
            f"proofGate={row['finalPostCorrectionPitchProofGate']}"
        )
    print("Ready for technique evidence classification:", ready)
    print("Recommended next action:", output["recommendedNextAction"])
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

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
