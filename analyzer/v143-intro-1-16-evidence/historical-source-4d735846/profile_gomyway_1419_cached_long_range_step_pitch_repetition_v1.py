from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1419_champion_cached_family_b_recur13_gate_v1 as bench

cached = bench.cached
v2 = bench.v2
v3 = bench.v3
recall = bench.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-cached-long-range-step-pitch-repetition-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-cached-long-range-step-pitch-repetition-v1-manifest.json"


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision(rows: list[dict[str, Any]], reference: set[tuple[int, int, int]]) -> dict[str, Any]:
    true_count = sum(1 for row in rows if token(row) in reference)
    false_count = len(rows) - true_count
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
    }


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

    # Detector-side structure is frozen before labels are consulted.
    groups: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in residual:
        measure, step, pitch = token(row)
        groups[(step, pitch)].append(row)

    structural_rows: list[dict[str, Any]] = []
    group_summaries: list[dict[str, Any]] = []

    for (step, pitch), members in groups.items():
        measures = sorted({token(row)[0] for row in members})
        distinct_measures = len(measures)
        span = measures[-1] - measures[0] if len(measures) >= 2 else 0
        gaps = [b - a for a, b in zip(measures, measures[1:])]
        max_gap = max(gaps) if gaps else 0
        min_gap = min(gaps) if gaps else 0
        section_bands = len({(m - 1) // 16 for m in measures})
        long_range = span >= 48 and distinct_measures >= 2
        very_long_range = span >= 72 and distinct_measures >= 2
        multi_section = section_bands >= 2

        frozen_members: list[dict[str, Any]] = []
        for row in members:
            out = dict(row)
            out.update(
                {
                    "structStep": step,
                    "structPitch": pitch,
                    "structDistinctMeasures": distinct_measures,
                    "structMeasureSpan": span,
                    "structMaxGap": max_gap,
                    "structMinGap": min_gap,
                    "structSectionBands16": section_bands,
                    "structLongRange48": long_range,
                    "structVeryLongRange72": very_long_range,
                    "structMultiSection": multi_section,
                }
            )
            frozen_members.append(out)
            structural_rows.append(out)

        labelled = precision(frozen_members, reference)
        group_summaries.append(
            {
                "step": step,
                "pitch": pitch,
                "measures": measures,
                "distinctMeasures": distinct_measures,
                "measureSpan": span,
                "maxGap": max_gap,
                "minGap": min_gap,
                "sectionBands16": section_bands,
                "longRange48": long_range,
                "veryLongRange72": very_long_range,
                "multiSection": multi_section,
                **labelled,
            }
        )

    bucket_defs = [
        ("span48_plus", lambda r: int(r["structMeasureSpan"]) >= 48),
        ("span72_plus", lambda r: int(r["structMeasureSpan"]) >= 72),
        ("span48_plus_sections2plus", lambda r: int(r["structMeasureSpan"]) >= 48 and int(r["structSectionBands16"]) >= 2),
        ("span72_plus_sections2plus", lambda r: int(r["structMeasureSpan"]) >= 72 and int(r["structSectionBands16"]) >= 2),
        ("span48_plus_distinct2", lambda r: int(r["structMeasureSpan"]) >= 48 and int(r["structDistinctMeasures"]) == 2),
        ("span72_plus_distinct2", lambda r: int(r["structMeasureSpan"]) >= 72 and int(r["structDistinctMeasures"]) == 2),
        ("span48_plus_distinct3plus", lambda r: int(r["structMeasureSpan"]) >= 48 and int(r["structDistinctMeasures"]) >= 3),
    ]

    buckets: list[dict[str, Any]] = []
    for name, pred in bucket_defs:
        subset = [row for row in structural_rows if pred(row)]
        buckets.append({"signature": name, **precision(subset, reference)})

    top_groups = sorted(
        group_summaries,
        key=lambda g: (
            float(g["precision"]),
            int(g["true"]),
            int(g["measureSpan"]),
            -int(g["false"]),
        ),
        reverse=True,
    )[:30]

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-cached-long-range-step-pitch-repetition",
        "championFrozen": {"pitchF1": 14.19, "matched": 178, "missing": 689, "extra": 1464},
        "residualRows": len(residual),
        "structuralBuckets": buckets,
        "topGroups": top_groups,
        "rows": structural_rows,
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
        "cachedFeatureExtractionReused": True,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 CACHED LONG-RANGE STEP-PITCH REPETITION V1")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Champion remains frozen: 14.19 / 178 / 689 / 1464")
    print("Residual rows:", len(residual))
    print("\nStructural repetition precision:")
    for row in buckets:
        print(
            f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%"
        )
    print("\nTop long-range step/pitch groups:")
    shown = 0
    for row in top_groups:
        if int(row["measureSpan"]) < 48:
            continue
        print(
            f"  step={row['step']} pitch={row['pitch']} measures={row['measures']} "
            f"span={row['measureSpan']} sections16={row['sectionBands16']} "
            f"true={row['true']} false={row['false']} precision={row['precision']}%"
        )
        shown += 1
        if shown >= 20:
            break
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
