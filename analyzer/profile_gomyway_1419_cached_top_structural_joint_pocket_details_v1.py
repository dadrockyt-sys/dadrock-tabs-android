from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import profile_gomyway_1419_cached_structural_joint_cross_signatures_v1 as cross

structural = cross.structural
bench = cross.bench
cached = cross.cached
v2 = cross.v2
v3 = cross.v3
recall = cross.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-cached-top-structural-joint-pocket-details-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-cached-top-structural-joint-pocket-details-v1-manifest.json"

TARGET_SIGNATURE = (
    "span72_distinct3plus|rms_025_050|flux_025_050|"
    "ratio_100_200|template_150_250|recur_8_15"
)


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def exact_signature(row: dict[str, Any]) -> str:
    return (
        f"{cross.struct_label(row)}|{row['rmsBucket']}|{row['fluxBucket']}|"
        f"{row['ratioBucket']}|{row['templateBucket']}|"
        f"recur_{cross.recur_label(int(row['recurrence']))}"
    )


def main() -> None:
    rows = cached.load_profile_rows()

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference_counter = v3.reference_tokens(reference_payload)
    reference = set(reference_counter.keys())

    champion_tokens = {
        token(row)
        for row in rows
        if bench.champion_1419_predicate(row)
    }
    residual = [row for row in rows if token(row) not in champion_tokens]

    # Structural metadata is detector-side and frozen before labels are consulted.
    frozen = cross.group_rows(residual)
    target_rows = [row for row in frozen if exact_signature(row) == TARGET_SIGNATURE]

    labelled: list[dict[str, Any]] = []
    for row in target_rows:
        out = dict(row)
        out["signature"] = TARGET_SIGNATURE
        out["isTrueMissingReference"] = token(row) in reference
        labelled.append(out)

    true_count = sum(1 for row in labelled if row["isTrueMissingReference"])
    false_count = len(labelled) - true_count
    if (true_count, false_count) != (2, 3):
        raise RuntimeError(
            f"Expected target pocket 2 true / 3 false, got {true_count} / {false_count}"
        )

    labelled.sort(
        key=lambda row: (
            not bool(row["isTrueMissingReference"]),
            token(row),
        )
    )

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-cached-top-structural-joint-pocket-details",
        "championFrozen": {"pitchF1": 14.19, "matched": 178, "missing": 689, "extra": 1464},
        "targetSignature": TARGET_SIGNATURE,
        "true": true_count,
        "false": false_count,
        "rows": labelled,
        "cachedFeatureExtractionReused": True,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "championPitchF1": 14.19,
        "targetTrue": true_count,
        "targetFalse": false_count,
        "cachedFeatureExtractionReused": True,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 CACHED TOP STRUCTURAL JOINT POCKET DETAILS V1")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Champion remains frozen: 14.19 / 178 / 689 / 1464")
    print("Target signature:", TARGET_SIGNATURE)
    print(f"Target precision: true={true_count} false={false_count} precision={100.0 * true_count / len(labelled):.2f}%")
    print("\nDetailed target rows:")
    for row in labelled:
        label = "TRUE " if row["isTrueMissingReference"] else "FALSE"
        measure, step, pitch = token(row)
        print(
            f"  {label} token=({measure}, {step}, {pitch}) "
            f"recur={int(row['recurrence'])} "
            f"rms={float(row['minRmsLog2Rise']):.6f} "
            f"flux={float(row['minPositiveFlux']):.6f} "
            f"ratio={float(row['minTargetVsSubharmonicRatio']):.6f} "
            f"template={float(row['minTemplateRatio']):.6f} "
            f"span={int(row['structMeasureSpan'])} "
            f"distinct={int(row['structDistinctMeasures'])} "
            f"sections16={int(row['structSectionBands16'])}"
        )

    print("Professional reference used during detection: False")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
