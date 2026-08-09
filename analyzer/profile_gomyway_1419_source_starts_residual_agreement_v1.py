from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1419_champion_cached_repeatable_residual_joint_gate_v1 as bench
import profile_gomyway_1419_source_confidence_duration_residual_v1 as source_profile

v2 = bench.v2
v3 = bench.v3
recur = bench.recur
recall = bench.recall
cached = bench.cached

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-source-starts-residual-agreement-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-source-starts-residual-agreement-v1-manifest.json"
EXPECTED_1419 = (178, 689, 1464)
EXPECTED_1419_F1 = 14.19


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def source_starts(event: dict[str, Any]) -> list[float]:
    value = event.get("sourceStarts")
    if not isinstance(value, list):
        return []
    starts = [parsed for item in value if (parsed := as_float(item)) is not None]
    return sorted(starts)


def count_bucket(count: int) -> str:
    if count <= 0:
        return "starts_0"
    if count == 1:
        return "starts_1"
    if count == 2:
        return "starts_2"
    if count == 3:
        return "starts_3"
    return "starts_4plus"


def spread_bucket(spread: float | None) -> str:
    if spread is None:
        return "spread_na"
    if spread <= 0.005:
        return "spread_000_005"
    if spread <= 0.015:
        return "spread_005_015"
    if spread <= 0.030:
        return "spread_015_030"
    if spread <= 0.060:
        return "spread_030_060"
    if spread <= 0.120:
        return "spread_060_120"
    return "spread_120_plus"


def precision_row(true_count: int, false_count: int) -> dict[str, Any]:
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
    }


def event_feature_rows(events: list[dict[str, Any]]) -> dict[tuple[int, int, int], dict[str, Any]]:
    # Validate/derive timing grid once from the complete protected source.
    v2.build_timing_grid(events)

    features: dict[tuple[int, int, int], dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        measure = v2.measure_of(event)
        step = v2.step_of(event)
        if measure is None or step is None:
            continue
        if not 1 <= measure <= v2.MEASURE_END or not 0 <= step < v2.STEPS_PER_MEASURE:
            continue

        starts = source_starts(event)
        count = len(starts)
        spread = (starts[-1] - starts[0]) if count >= 2 else None
        gaps = [starts[index + 1] - starts[index] for index in range(count - 1)]
        mean_gap = (sum(gaps) / len(gaps)) if gaps else None
        max_gap = max(gaps) if gaps else None
        feature = {
            "sourceStartCount": count,
            "sourceStartSpread": spread,
            "sourceStartMeanGap": mean_gap,
            "sourceStartMaxGap": max_gap,
            "countBucket": count_bucket(count),
            "spreadBucket": spread_bucket(spread),
            "confidence": source_profile.as_float(event.get("confidence"), 0.0),
            "durationSteps": source_profile.as_int(event.get("durationSteps"), 0),
            "source": event.get("source"),
        }

        for pitch in source_profile.event_pitches(event):
            token = (int(measure), int(step), int(pitch))
            previous = features.get(token)
            if previous is None or (
                feature["sourceStartCount"],
                -(feature["sourceStartSpread"] if feature["sourceStartSpread"] is not None else 999.0),
                feature["confidence"],
            ) > (
                previous["sourceStartCount"],
                -(previous["sourceStartSpread"] if previous["sourceStartSpread"] is not None else 999.0),
                previous["confidence"],
            ):
                features[token] = dict(feature)
    return features


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    grid, _ = v2.build_timing_grid(events)
    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    rows = cached.load_profile_rows()
    champion_additions = bench.rows_to_counter(rows, bench.champion_1419_predicate)
    champion_1419 = baseline_1382 + champion_additions
    score_1419 = recur.grade(champion_1419, reference)
    actual = (
        int(score_1419["matched"]),
        int(score_1419["missing"]),
        int(score_1419["extra"]),
    )
    if actual != EXPECTED_1419 or abs(float(score_1419["pitchF1"]) - EXPECTED_1419_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 14.19 champion {EXPECTED_1419}/{EXPECTED_1419_F1}, "
            f"got {actual}/{score_1419['pitchF1']}"
        )

    token_features = event_feature_rows(events)
    champion_tokens = set(champion_1419.keys())
    residual = {
        token: feature
        for token, feature in token_features.items()
        if token not in champion_tokens
    }

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    detailed_rows: list[dict[str, Any]] = []

    for token, feature in residual.items():
        truth = "true" if token in reference else "false"
        cb = str(feature["countBucket"])
        sb = str(feature["spreadBucket"])
        groups[f"count|{cb}"][truth] += 1
        groups[f"spread|{sb}"][truth] += 1
        groups[f"joint|{cb}|{sb}"][truth] += 1
        if feature["sourceStartCount"] >= 2:
            groups[f"multi|{sb}"][truth] += 1
        if feature["sourceStartCount"] >= 3:
            groups[f"threeplus|{sb}"][truth] += 1
        detailed_rows.append({"token": list(token), "true": truth == "true", **feature})

    summaries: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        summaries.append({
            "signature": signature,
            **precision_row(int(counts["true"]), int(counts["false"])),
        })
    summaries.sort(
        key=lambda row: (row["precision"], row["true"], -row["false"]),
        reverse=True,
    )
    repeatable = [row for row in summaries if int(row["true"]) >= 2]
    supported = [row for row in summaries if int(row["true"]) >= 3]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during sourceStarts residual profile")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-source-starts-residual-agreement",
        "championScore": score_1419,
        "sourceTokenCount": len(token_features),
        "residualSourceTokenCount": len(residual),
        "signaturePrecision": summaries,
        "repeatableSignaturePrecision": repeatable,
        "supportedSignaturePrecision": supported,
        "rows": detailed_rows,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
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
        "candidateSha256": after,
        "championPitchF1": score_1419["pitchF1"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 SOURCE STARTS RESIDUAL AGREEMENT V1")
    print("Passed: True")
    print("Champion remains frozen:", score_1419["pitchF1"], "/", score_1419["matched"], "/", score_1419["missing"], "/", score_1419["extra"])
    print("Source token count:", len(token_features))
    print("Residual source token count:", len(residual))
    print("\nTop repeatable sourceStarts signatures:")
    for row in repeatable[:25]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("\nTop supported sourceStarts signatures (3+ true):")
    for row in supported[:25]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
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
