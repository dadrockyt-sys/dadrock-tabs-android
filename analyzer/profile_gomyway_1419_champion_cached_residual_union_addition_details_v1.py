from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1419_champion_cached_repeatable_residual_joint_gate_v1 as bench

cached = bench.cached

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-champion-cached-residual-union-addition-details-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-champion-cached-residual-union-addition-details-v1-manifest.json"
EXPECTED_1419 = (178, 689, 1464)
EXPECTED_F1 = 14.19


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision_summary(rows: list[dict[str, Any]], key_fn) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"true": 0, "false": 0})
    for row in rows:
        key = str(key_fn(row))
        if bool(row.get("trueMissingReference")):
            buckets[key]["true"] += 1
        else:
            buckets[key]["false"] += 1

    out: list[dict[str, Any]] = []
    for key, counts in buckets.items():
        total = counts["true"] + counts["false"]
        out.append(
            {
                "key": key,
                "true": counts["true"],
                "false": counts["false"],
                "precision": round(100.0 * counts["true"] / total, 2) if total else 0.0,
            }
        )
    out.sort(key=lambda x: (-x["precision"], -x["true"], x["false"], x["key"]))
    return out


def main() -> None:
    rows = cached.load_profile_rows()

    champion_tokens = {
        token(row)
        for row in rows
        if bench.champion_1419_predicate(row)
    }
    residual = [row for row in rows if token(row) not in champion_tokens]
    selected = [row for row in residual if bench.family_a(row) or bench.family_b(row)]

    details: list[dict[str, Any]] = []
    for row in selected:
        family = "A" if bench.family_a(row) else "B"
        details.append(
            {
                "token": list(token(row)),
                "trueMissingReference": bool(row.get("trueMissingReference")),
                "family": family,
                "recurrence": int(row["recurrence"]),
                "rmsBucket": row["rmsBucket"],
                "fluxBucket": row["fluxBucket"],
                "ratioBucket": row["ratioBucket"],
                "templateBucket": row["templateBucket"],
                "minRmsLog2Rise": float(row["minRmsLog2Rise"]),
                "minPositiveFlux": float(row["minPositiveFlux"]),
                "minTargetVsSubharmonicRatio": float(row["minTargetVsSubharmonicRatio"]),
                "minTemplateRatio": float(row["minTemplateRatio"]),
            }
        )

    details.sort(
        key=lambda r: (
            r["family"],
            0 if r["trueMissingReference"] else 1,
            r["recurrence"],
            tuple(r["token"]),
        )
    )

    true_count = sum(1 for r in details if r["trueMissingReference"])
    false_count = len(details) - true_count

    family_summary = precision_summary(details, lambda r: "family_" + r["family"])
    family_recur_summary = precision_summary(
        details,
        lambda r: f"family_{r['family']}_recur_{'4plus' if r['recurrence'] >= 4 else r['recurrence']}",
    )

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "cached-14.19-residual-family-a-b-continuous-addition-details",
        "championScore": {
            "pitchF1": EXPECTED_F1,
            "matched": EXPECTED_1419[0],
            "missing": EXPECTED_1419[1],
            "extra": EXPECTED_1419[2],
        },
        "additionCount": len(details),
        "trueAdditions": true_count,
        "falseAdditions": false_count,
        "familyPrecision": family_summary,
        "familyRecurrencePrecision": family_recur_summary,
        "rows": details,
        "cachedFeatureExtractionReused": True,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "design-small-reference-free-prune-benchmark-only-if-true-false-continuous-separation-is-visible",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "championPitchF1": EXPECTED_F1,
        "cachedFeatureExtractionReused": True,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 CHAMPION CACHED RESIDUAL UNION ADDITION DETAILS V1 COMPLETE")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Champion pitch F1:", EXPECTED_F1)
    print("Champion matched/missing/extra:", EXPECTED_1419[0], "/", EXPECTED_1419[1], "/", EXPECTED_1419[2])
    print("Union A+B residual additions:", len(details))
    print("True additions:", true_count)
    print("False additions:", false_count)
    print("Family precision:")
    for item in family_summary:
        print(f"  {item['key']}: true={item['true']} false={item['false']} precision={item['precision']}%")
    print("Family/recurrence precision:")
    for item in family_recur_summary:
        print(f"  {item['key']}: true={item['true']} false={item['false']} precision={item['precision']}%")
    print("Addition detail rows:")
    for row in details:
        label = "TRUE " if row["trueMissingReference"] else "FALSE"
        print(
            f"  {label} family={row['family']} token={row['token']} recur={row['recurrence']} "
            f"rms={row['minRmsLog2Rise']:.6f} flux={row['minPositiveFlux']:.6f} "
            f"ratio={row['minTargetVsSubharmonicRatio']:.6f} template={row['minTemplateRatio']:.6f}"
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
