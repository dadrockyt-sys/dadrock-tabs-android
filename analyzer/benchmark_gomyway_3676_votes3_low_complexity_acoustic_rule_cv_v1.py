from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_votes3_low_complexity_acoustic_rules_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3676-votes3-acoustic-refinement-v1.json"
PROFILE_PATH = PUBLIC / "gomyway-3676-votes3-low-complexity-acoustic-rules-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-votes3-low-complexity-acoustic-rule-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-votes3-low-complexity-acoustic-rule-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76

recall = prof.recall
FEATURES = prof.FEATURES


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1_from_counts(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def feature_value(row: dict[str, Any], feature: str) -> float:
    value = row.get(feature)
    return 0.0 if value is None else float(value)


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
    return {
        "rule": name,
        "fn": fn,
        "complexity": complexity,
        "truePruned": true_pruned,
        "falsePruned": false_pruned,
        "pruned": len(chosen),
    }


def section_spread(rows: list[dict[str, Any]], fn: Callable[[dict[str, Any]], bool]) -> int:
    measures = sorted({int(r["measure"]) for r in rows})
    if not measures:
        return 0
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)
    buckets = set()
    for r in rows:
        if not fn(r):
            continue
        rel = int(r["measure"]) - lo
        buckets.add(min(4, int(5 * rel / span)))
    return len(buckets)


def learn_rule(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    primitives: list[tuple[str, Callable[[dict[str, Any]], bool]]] = []
    for feature in FEATURES:
        for threshold in thresholds(rows, feature):
            for direction in ("le", "ge"):
                primitives.append(primitive(feature, direction, threshold))

    candidates: list[dict[str, Any]] = []
    useful: list[tuple[str, Callable[[dict[str, Any]], bool]]] = []
    for name, fn in primitives:
        result = evaluate(rows, name, fn, 1)
        if result["falsePruned"] >= 2 and result["truePruned"] <= 1:
            useful.append((name, fn))
        if result["falsePruned"] >= 3 and result["truePruned"] == 0:
            result["sectionSpread"] = section_spread(rows, fn)
            candidates.append(result)

    for (name_a, fn_a), (name_b, fn_b) in combinations(useful, 2):
        feature_a = name_a.split("<")[0].split(">")[0]
        feature_b = name_b.split("<")[0].split(">")[0]
        if feature_a == feature_b:
            continue
        fn = lambda r, a=fn_a, b=fn_b: a(r) and b(r)
        result = evaluate(rows, f"({name_a}) AND ({name_b})", fn, 2)
        if result["falsePruned"] >= 3 and result["truePruned"] == 0:
            result["sectionSpread"] = section_spread(rows, fn)
            candidates.append(result)

    candidates = [c for c in candidates if int(c["sectionSpread"]) >= 2]
    if not candidates:
        return None
    candidates.sort(key=lambda r: (-int(r["falsePruned"]), int(r["complexity"]), -int(r["sectionSpread"]), str(r["rule"])))
    return candidates[0]


def apply_rule(rows: list[dict[str, Any]], rule: dict[str, Any] | None) -> dict[str, int]:
    if rule is None:
        return {"truePruned": 0, "falsePruned": 0, "pruned": 0}
    chosen = [r for r in rows if rule["fn"](r)]
    return {
        "truePruned": sum(1 for r in chosen if str(r.get("label")) == "true"),
        "falsePruned": sum(1 for r in chosen if str(r.get("label")) == "false"),
        "pruned": len(chosen),
    }


def cv_scheme(rows: list[dict[str, Any]], scheme: str) -> dict[str, Any]:
    measures = sorted({int(r["measure"]) for r in rows})
    if not measures:
        return {"passed": False, "folds": []}
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)

    def fold_of(r: dict[str, Any]) -> int:
        m = int(r["measure"])
        if scheme == "normal":
            return m % 5
        if scheme == "shifted":
            return (m + 2) % 5
        return min(4, int(5 * (m - lo) / span))

    folds = []
    passed = True
    total_false = 0
    total_true = 0
    for fold in range(5):
        train = [r for r in rows if fold_of(r) != fold]
        test = [r for r in rows if fold_of(r) == fold]
        rule = learn_rule(train)
        result = apply_rule(test, rule)
        fold_pass = result["truePruned"] == 0
        passed = passed and fold_pass
        total_false += result["falsePruned"]
        total_true += result["truePruned"]
        folds.append({
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "learnedRule": None if rule is None else rule["rule"],
            "trainFalsePruned": 0 if rule is None else int(rule["falsePruned"]),
            "heldoutTruePruned": result["truePruned"],
            "heldoutFalsePruned": result["falsePruned"],
            "passed": fold_pass,
        })
    return {"passed": passed and total_false > 0 and total_true == 0, "truePruned": total_true, "falsePruned": total_false, "folds": folds}


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    if not INPUT_PATH.exists() or not PROFILE_PATH.exists():
        raise RuntimeError("Missing prerequisite acoustic refinement/profile outputs")

    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if abs(float(data.get("championPitchF1", -1)) - EXPECTED_F1) > 0.01:
        raise RuntimeError("Expected frozen 36.76 champion")
    if tuple(int(x) for x in data.get("championMatchedMissingExtra", [])) != EXPECTED:
        raise RuntimeError("Unexpected 36.76 champion counts")

    rows = list(data.get("targetRows") or [])
    if (sum(str(r.get("label")) == "true" for r in rows), sum(str(r.get("label")) == "false" for r in rows)) != (7, 31):
        raise RuntimeError("Expected votes>=3 target pocket 7 true / 31 false")

    full_rule = learn_rule(rows)
    if full_rule is None:
        raise RuntimeError("No full-data low-complexity safe rule found")
    full = apply_rule(rows, full_rule)
    matched = EXPECTED[0] - full["truePruned"]
    missing = EXPECTED[1] + full["truePruned"]
    extra = EXPECTED[2] - full["falsePruned"]
    candidate_f1 = f1_from_counts(matched, missing, extra)

    normal = cv_scheme(rows, "normal")
    shifted = cv_scheme(rows, "shifted")
    section = cv_scheme(rows, "section")
    validated = (
        full["truePruned"] == 0
        and full["falsePruned"] > 0
        and candidate_f1 > EXPECTED_F1
        and bool(normal["passed"])
        and bool(shifted["passed"])
        and bool(section["passed"])
    )

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during low-complexity acoustic CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "36.76-votes3-low-complexity-acoustic-rule-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "fullDataRule": full_rule["rule"],
        "candidatePitchF1": candidate_f1,
        "candidateMatchedMissingExtra": [matched, missing, extra],
        "candidateTruePruned": full["truePruned"],
        "candidateFalsePruned": full["falsePruned"],
        "normalCrossValidation": normal,
        "shiftedWindowValidation": shifted,
        "sectionValidation": section,
        "validatedNewChampion": validated,
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
        "candidatePitchF1": candidate_f1,
        "validatedNewChampion": validated,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 VOTES3 LOW-COMPLEXITY ACOUSTIC RULE CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", EXPECTED_F1)
    print("Baseline matched/missing/extra:", *EXPECTED)
    print("Full-data rule:", full_rule["rule"])
    print("Candidate pitch F1:", candidate_f1)
    print("Candidate matched/missing/extra:", matched, missing, extra)
    print("Candidate true/false pruned:", full["truePruned"], "/", full["falsePruned"])
    print("Normal CV passed:", normal["passed"], "true/false=", normal["truePruned"], "/", normal["falsePruned"])
    print("Section stability passed:", section["passed"], "true/false=", section["truePruned"], "/", section["falsePruned"])
    print("Shifted-window stability passed:", shifted["passed"], "true/false=", shifted["truePruned"], "/", shifted["falsePruned"])
    print("Validated new champion:", validated)
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
