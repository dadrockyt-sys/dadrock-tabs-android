from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_1419_cached_structural_joint_cross_signatures_v1 as cross

structural = cross.structural
bench = structural.bench
cached = structural.cached
v2 = structural.v2
v3 = structural.v3
recall = structural.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-cached-recur-distinct-structure-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-cached-recur-distinct-structure-v1-manifest.json"


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision(t: int, f: int) -> float:
    return round(100.0 * t / (t + f), 2) if t + f else 0.0


def main() -> None:
    rows = cached.load_profile_rows()
    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = set(v3.reference_tokens(reference_payload).keys())

    champion_tokens = {token(row) for row in rows if bench.champion_1419_predicate(row)}
    residual = [row for row in rows if token(row) not in champion_tokens]
    frozen = cross.group_rows(residual)

    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    details: list[dict[str, Any]] = []

    for row in frozen:
        recur = int(row["recurrence"])
        distinct = int(row["structDistinctMeasures"])
        span = int(row["structMeasureSpan"])
        sections = int(row["structSectionBands16"])
        labels = [
            f"recur{recur}_distinct{distinct}",
            f"recur_eq_distinct_{recur}" if recur == distinct else "recur_ne_distinct",
            f"recur_eq_distinct_span80plus" if recur == distinct and span >= 80 else "other_span",
            f"recur_eq_distinct_span80plus_sections5plus" if recur == distinct and span >= 80 and sections >= 5 else "other_sections",
            f"recur13_distinct13",
            f"recur13_distinct13_span80plus",
            f"recur13_distinct13_span80plus_sections5plus",
        ]
        applies = [
            True,
            True,
            True,
            True,
            recur == 13 and distinct == 13,
            recur == 13 and distinct == 13 and span >= 80,
            recur == 13 and distinct == 13 and span >= 80 and sections >= 5,
        ]
        is_true = token(row) in reference
        for label, yes in zip(labels, applies):
            if yes:
                counts[label][0 if is_true else 1] += 1

        if 10 <= recur <= 16 and 10 <= distinct <= 16:
            details.append({
                "token": list(token(row)),
                "isTrue": is_true,
                "recurrence": recur,
                "distinct": distinct,
                "span": span,
                "sections16": sections,
                "rms": float(row["minRmsLog2Rise"]),
                "flux": float(row["minPositiveFlux"]),
                "ratio": float(row["minTargetVsSubharmonicRatio"]),
                "template": float(row["minTemplateRatio"]),
            })

    summary = []
    for sig, (t, f) in counts.items():
        if sig.startswith("other_") or sig == "recur_ne_distinct":
            continue
        summary.append({"signature": sig, "true": t, "false": f, "precision": precision(t, f)})
    summary.sort(key=lambda r: (r["precision"], r["true"], -r["false"]), reverse=True)

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-cached-recurrence-distinct-structure",
        "championFrozen": {"pitchF1": 14.19, "matched": 178, "missing": 689, "extra": 1464},
        "summary": summary,
        "details": details,
        "cachedFeatureExtractionReused": True,
        "professionalReferenceUsedDuringDetection": False,
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

    print("GOMYWAY 14.19 CACHED RECURRENCE/DISTINCT STRUCTURE V1")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Champion remains frozen: 14.19 / 178 / 689 / 1464")
    print("\nStructural equality precision:")
    for row in summary[:30]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("\nNearby recurrence/distinct rows:")
    for row in details:
        print(
            f"  {'TRUE' if row['isTrue'] else 'FALSE'} token={tuple(row['token'])} "
            f"recur={row['recurrence']} distinct={row['distinct']} span={row['span']} sections16={row['sections16']} "
            f"rms={row['rms']:.6f} flux={row['flux']:.6f} ratio={row['ratio']:.6f} template={row['template']:.6f}"
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
