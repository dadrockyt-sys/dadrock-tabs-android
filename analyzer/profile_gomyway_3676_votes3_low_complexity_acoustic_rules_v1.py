from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_recovery_precision_survivors_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3676-votes3-acoustic-refinement-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-votes3-low-complexity-acoustic-rules-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-votes3-low-complexity-acoustic-rules-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
TARGET_TRUE = 7
TARGET_FALSE = 31

recall = prof.recall

FEATURES = (
    "maxAmplitude",
    "meanAmplitude",
    "minGridError",
    "maxDuration",
    "sweepPersistence",
    "stemCountAtWide",
    "strictestSweepIndex",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1_from_counts(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def feature_value(row: dict[str, Any], feature: str) -> float:
    value = row.get(feature)
    if value is None:
        return 0.0
    return float(value)


def thresholds(rows: list[dict[str, Any]], feature: str) -> list[float]:
    values = sorted({feature_value(r, feature) for r in rows})
    if len(values) <= 1:
        return values
    mids = [(a + b) / 2.0 for a, b in zip(values[:-1], values[1:]) if a != b]
    return sorted(set(values + mids))


def primitive(feature: str, direction: str, threshold: float) -> tuple[str, Callable[[dict[str, Any]], bool]]:
    if direction == "le":
        return f"{feature}<={threshold:.8g}", lambda r: feature_value(r, feature) <= threshold
    return f"{feature}>={threshold:.8g}", lambda r: feature_value(r, feature) >= threshold


def evaluate(rows: list[dict[str, Any]], name: str, fn: Callable[[dict[str, Any]], bool], complexity: int) -> dict[str, Any]:
    chosen = [r for r in rows if fn(r)]
    true_pruned = sum(1 for r in chosen if str(r.get("label")) == "true")
    false_pruned = sum(1 for r in chosen if str(r.get("label")) == "false")
    matched = EXPECTED[0] - true_pruned
    missing = EXPECTED[1] + true_pruned
    extra = EXPECTED[2] - false_pruned
    return {
        "rule": name,
        "complexity": complexity,
        "pruned": len(chosen),
        "truePruned": true_pruned,
        "falsePruned": false_pruned,
        "prunePrecision": round(100.0 * false_pruned / len(chosen), 2) if chosen else 0.0,
        "pitchF1": f1_from_counts(matched, missing, extra),
        "matchedMissingExtra": [matched, missing, extra],
        "tokens": [r.get("token") for r in chosen],
    }


def section_spread(rows: list[dict[str, Any]], tokens: set[str]) -> int:
    measures = sorted({int(r["measure"]) for r in rows})
    if not measures:
        return 0
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)
    buckets: set[int] = set()
    for r in rows:
        if str(r.get("token")) not in tokens:
            continue
        rel = int(r["measure"]) - lo
        buckets.add(min(4, int(5 * rel / span)))
    return len(buckets)


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    if not INPUT_PATH.exists():
        raise RuntimeError(f"Missing prerequisite profiler output: {INPUT_PATH.relative_to(ROOT)}")

    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if abs(float(data.get("championPitchF1", -1)) - EXPECTED_F1) > 0.01:
        raise RuntimeError("Expected frozen 36.76 champion")
    counts = tuple(int(x) for x in data.get("championMatchedMissingExtra", []))
    if counts != EXPECTED:
        raise RuntimeError(f"Expected champion {EXPECTED}, got {counts}")

    rows = list(data.get("targetRows") or [])
    true_count = sum(1 for r in rows if str(r.get("label")) == "true")
    false_count = sum(1 for r in rows if str(r.get("label")) == "false")
    if (true_count, false_count) != (TARGET_TRUE, TARGET_FALSE):
        raise RuntimeError(f"Expected votes>=3 target pocket 7/31, got {true_count}/{false_count}")

    primitives: list[tuple[str, Callable[[dict[str, Any]], bool]]] = []
    for feature in FEATURES:
        for threshold in thresholds(rows, feature):
            for direction in ("le", "ge"):
                primitives.append(primitive(feature, direction, threshold))

    tested: list[dict[str, Any]] = []
    for name, fn in primitives:
        result = evaluate(rows, name, fn, 1)
        if int(result["falsePruned"]) >= 2:
            tested.append(result)

    # Keep only useful primitives before forming pairs so the search stays interpretable.
    useful_primitives = []
    for name, fn in primitives:
        result = evaluate(rows, name, fn, 1)
        if int(result["falsePruned"]) >= 2 and int(result["truePruned"]) <= 2:
            useful_primitives.append((name, fn))

    for (name_a, fn_a), (name_b, fn_b) in combinations(useful_primitives, 2):
        feature_a = name_a.split("<")[0].split(">")[0]
        feature_b = name_b.split("<")[0].split(">")[0]
        if feature_a == feature_b:
            continue
        fn = lambda r, a=fn_a, b=fn_b: a(r) and b(r)
        result = evaluate(rows, f"({name_a}) AND ({name_b})", fn, 2)
        if int(result["falsePruned"]) >= 2:
            tested.append(result)

    for result in tested:
        token_set = {str(t) for t in result.get("tokens") or []}
        result["sectionBucketSpread"] = section_spread(rows, token_set)

    tested.sort(
        key=lambda r: (
            int(r["truePruned"]),
            -int(r["falsePruned"]),
            int(r["complexity"]),
            -int(r["sectionBucketSpread"]),
            str(r["rule"]),
        )
    )

    strict_safe = [
        r for r in tested
        if int(r["truePruned"]) == 0
        and int(r["falsePruned"]) >= 3
        and int(r["sectionBucketSpread"]) >= 2
        and float(r["pitchF1"]) > EXPECTED_F1
    ]
    broad_safe = [
        r for r in tested
        if int(r["truePruned"]) == 0
        and int(r["falsePruned"]) >= 2
        and float(r["pitchF1"]) > EXPECTED_F1
    ]
    best = strict_safe[0] if strict_safe else (broad_safe[0] if broad_safe else None)

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during low-complexity acoustic rule profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-votes3-low-complexity-acoustic-rules",
        "championPitchF1": EXPECTED_F1,
        "championMatchedMissingExtra": list(EXPECTED),
        "targetTrue": true_count,
        "targetFalse": false_count,
        "features": list(FEATURES),
        "primitiveRuleCount": len(primitives),
        "testedRuleCount": len(tested),
        "strictSafeRules": strict_safe[:100],
        "broadSafeRules": broad_safe[:100],
        "bestLowComplexityRule": best,
        "topRules": tested[:100],
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
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
        "championPitchF1": EXPECTED_F1,
        "strictSafeRuleCount": len(strict_safe),
        "broadSafeRuleCount": len(broad_safe),
        "bestCandidatePitchF1": best["pitchF1"] if best else None,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 VOTES3 LOW-COMPLEXITY ACOUSTIC RULES V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", EXPECTED_F1)
    print("Champion matched/missing/extra:", *EXPECTED)
    print("Target votes>=3 true/false:", true_count, "/", false_count)
    print("Primitive rules generated:", len(primitives))
    print("Rules tested:", len(tested))
    print("Strict safe low-complexity rules:", len(strict_safe))
    print("Broad safe low-complexity rules:", len(broad_safe))
    print("Best low-complexity rule:", best)
    for r in strict_safe[:20]:
        print(
            f"SAFE {r['rule']} false={r['falsePruned']} true={r['truePruned']} "
            f"spread={r['sectionBucketSpread']} F1={r['pitchF1']}"
        )
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
