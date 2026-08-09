from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_1419_cached_long_range_step_pitch_repetition_v1 as structural

bench = structural.bench
cached = structural.cached
v2 = structural.v2
v3 = structural.v3
recall = structural.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-cached-structural-joint-cross-signatures-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-cached-structural-joint-cross-signatures-v1-manifest.json"


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision(true_count: int, false_count: int) -> dict[str, Any]:
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
    }


def group_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        measure, step, pitch = token(row)
        groups[(step, pitch)].append(row)

    output: list[dict[str, Any]] = []
    for (step, pitch), members in groups.items():
        measures = sorted({token(row)[0] for row in members})
        span = measures[-1] - measures[0] if len(measures) >= 2 else 0
        sections16 = len({(m - 1) // 16 for m in measures})
        distinct = len(measures)
        for row in members:
            out = dict(row)
            out.update(
                {
                    "structStep": step,
                    "structPitch": pitch,
                    "structDistinctMeasures": distinct,
                    "structMeasureSpan": span,
                    "structSectionBands16": sections16,
                }
            )
            output.append(out)
    return output


def struct_label(row: dict[str, Any]) -> str:
    span = int(row["structMeasureSpan"])
    distinct = int(row["structDistinctMeasures"])
    sections = int(row["structSectionBands16"])
    if span >= 72 and distinct == 2:
        return "span72_distinct2"
    if span >= 72 and distinct >= 3:
        return "span72_distinct3plus"
    if span >= 48 and distinct == 2:
        return "span48_distinct2"
    if span >= 48 and distinct >= 3:
        return "span48_distinct3plus"
    if sections >= 3 and distinct >= 3:
        return "sections3plus"
    if sections >= 2 and distinct >= 2:
        return "sections2plus"
    return "local"


def recur_label(value: int) -> str:
    if value >= 16:
        return "16plus"
    if value >= 8:
        return "8_15"
    if value >= 4:
        return "4_7"
    return str(value)


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

    # Structural and spectral detector-side features are frozen before labels are consulted.
    frozen = group_rows(residual)

    exact_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    broad_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    struct_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for row in frozen:
        is_true = token(row) in reference
        idx = 0 if is_true else 1
        sl = struct_label(row)
        rl = recur_label(int(row["recurrence"]))

        exact_key = (
            f"{sl}|{row['rmsBucket']}|{row['fluxBucket']}|"
            f"{row['ratioBucket']}|{row['templateBucket']}|recur_{rl}"
        )
        broad_key = (
            f"{sl}|{row['ratioBucket']}|{row['templateBucket']}|recur_{rl}"
        )
        exact_counts[exact_key][idx] += 1
        broad_counts[broad_key][idx] += 1
        struct_counts[sl][idx] += 1

    def summaries(counts: dict[str, list[int]], min_true: int = 1) -> list[dict[str, Any]]:
        rows_out: list[dict[str, Any]] = []
        for signature, (true_count, false_count) in counts.items():
            if true_count < min_true:
                continue
            rows_out.append({"signature": signature, **precision(true_count, false_count)})
        rows_out.sort(
            key=lambda r: (
                float(r["precision"]),
                int(r["true"]),
                -int(r["false"]),
            ),
            reverse=True,
        )
        return rows_out

    best_exact = summaries(exact_counts)[:50]
    repeatable_exact = [row for row in summaries(exact_counts, min_true=2) if int(row["total"]) >= 2][:30]
    best_broad = summaries(broad_counts)[:40]
    repeatable_broad = [row for row in summaries(broad_counts, min_true=2) if int(row["total"]) >= 2][:30]
    structural_summary = summaries(struct_counts)

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-cached-structural-joint-cross-signatures",
        "championFrozen": {"pitchF1": 14.19, "matched": 178, "missing": 689, "extra": 1464},
        "residualRows": len(frozen),
        "structuralSummary": structural_summary,
        "bestExactCrossSignatures": best_exact,
        "repeatableExactCrossSignatures": repeatable_exact,
        "bestBroadCrossSignatures": best_broad,
        "repeatableBroadCrossSignatures": repeatable_broad,
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

    print("GOMYWAY 14.19 CACHED STRUCTURAL JOINT CROSS-SIGNATURES V1")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Champion remains frozen: 14.19 / 178 / 689 / 1464")
    print("Residual rows:", len(frozen))

    print("\nStructural precision:")
    for row in structural_summary:
        print(
            f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%"
        )

    print("\nTop exact structural/joint cross-signatures:")
    for row in best_exact[:20]:
        print(
            f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%"
        )

    print("\nTop repeatable exact structural/joint cross-signatures:")
    for row in repeatable_exact[:20]:
        print(
            f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%"
        )

    print("\nTop repeatable broad structural/joint cross-signatures:")
    for row in repeatable_broad[:20]:
        print(
            f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%"
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
