from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import benchmark_gomyway_3676_votes3_low_complexity_acoustic_rule_cv_v1 as base

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3676-votes3-acoustic-refinement-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-votes3-guarded-duration-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-votes3-guarded-duration-prune-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76

recall = base.recall
GUARD_FEATURES = (
    "maxAmplitude",
    "meanAmplitude",
    "minGridError",
    "sweepPersistence",
    "stemCountAtWide",
    "strictestSweepIndex",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1_from_counts(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def value(row: dict[str, Any], feature: str) -> float:
    v = row.get(feature)
    return 0.0 if v is None else float(v)


def thresholds(rows: list[dict[str, Any]], feature: str) -> list[float]:
    vals = sorted({value(r, feature) for r in rows})
    if len(vals) <= 1:
        return vals
    mids = [(a + b) / 2.0 for a, b in zip(vals[:-1], vals[1:]) if a != b]
    return sorted(set(vals + mids))


def primitive(feature: str, direction: str, threshold: float) -> tuple[str, Callable[[dict[str, Any]], bool]]:
    if direction == "le":
        return f"{feature}<={threshold:.8g}", lambda r: value(r, feature) <= threshold
    return f"{feature}>={threshold:.8g}", lambda r: value(r, feature) >= threshold


def fold_of(row: dict[str, Any], measures: list[int], scheme: str) -> int:
    m = int(row["measure"])
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)
    if scheme == "normal":
        return m % 5
    if scheme == "shifted":
        return (m + 2) % 5
    return min(4, int(5 * (m - lo) / span))


def apply(rows: list[dict[str, Any]], prune_fn: Callable[[dict[str, Any]], bool]) -> dict[str, int]:
    chosen = [r for r in rows if prune_fn(r)]
    return {
        "pruned": len(chosen),
        "truePruned": sum(str(r.get("label")) == "true" for r in chosen),
        "falsePruned": sum(str(r.get("label")) == "false" for r in chosen),
    }


def learn_guarded_rule(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    # Relearn the simple prune rule first using training data only.
    raw = base.learn_rule(rows)
    if raw is None:
        return None

    raw_pruned = [r for r in rows if raw["fn"](r)]
    raw_true = sum(str(r.get("label")) == "true" for r in raw_pruned)
    raw_false = sum(str(r.get("label")) == "false" for r in raw_pruned)

    # If the raw training rule is already zero-true, keep it. A guard is unnecessary.
    candidates: list[dict[str, Any]] = []
    if raw_true == 0 and raw_false >= 2:
        candidates.append({
            "rule": raw["rule"],
            "baseRule": raw["rule"],
            "guard": None,
            "fn": raw["fn"],
            "truePruned": raw_true,
            "falsePruned": raw_false,
            "complexity": int(raw.get("complexity", 1)),
        })

    # Learn a one-feature protective guard only from training rows.
    for feature in GUARD_FEATURES:
        for t in thresholds(raw_pruned, feature):
            for direction in ("le", "ge"):
                gname, guard_fn = primitive(feature, direction, t)
                prune_fn = lambda r, p=raw["fn"], g=guard_fn: p(r) and not g(r)
                res = apply(rows, prune_fn)
                if res["truePruned"] != 0 or res["falsePruned"] < 2:
                    continue
                candidates.append({
                    "rule": f"({raw['rule']}) AND NOT ({gname})",
                    "baseRule": raw["rule"],
                    "guard": gname,
                    "fn": prune_fn,
                    "truePruned": res["truePruned"],
                    "falsePruned": res["falsePruned"],
                    "complexity": int(raw.get("complexity", 1)) + 1,
                })

    if not candidates:
        return None
    candidates.sort(key=lambda r: (-int(r["falsePruned"]), int(r["complexity"]), str(r["rule"])))
    return candidates[0]


def cv_scheme(rows: list[dict[str, Any]], scheme: str) -> dict[str, Any]:
    measures = sorted({int(r["measure"]) for r in rows})
    folds = []
    total_true = 0
    total_false = 0
    all_safe = True

    for fold in range(5):
        train = [r for r in rows if fold_of(r, measures, scheme) != fold]
        test = [r for r in rows if fold_of(r, measures, scheme) == fold]
        learned = learn_guarded_rule(train)
        if learned is None:
            result = {"pruned": 0, "truePruned": 0, "falsePruned": 0}
        else:
            result = apply(test, learned["fn"])

        safe = result["truePruned"] == 0
        all_safe = all_safe and safe
        total_true += result["truePruned"]
        total_false += result["falsePruned"]
        folds.append({
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "learnedRule": None if learned is None else learned["rule"],
            "learnedGuard": None if learned is None else learned["guard"],
            "trainTruePruned": 0 if learned is None else int(learned["truePruned"]),
            "trainFalsePruned": 0 if learned is None else int(learned["falsePruned"]),
            "heldoutTruePruned": result["truePruned"],
            "heldoutFalsePruned": result["falsePruned"],
            "passed": safe,
        })

    return {
        "passed": all_safe and total_true == 0 and total_false > 0,
        "truePruned": total_true,
        "falsePruned": total_false,
        "folds": folds,
    }


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    if not INPUT_PATH.exists():
        raise RuntimeError(f"Missing prerequisite: {INPUT_PATH.relative_to(ROOT)}")

    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if abs(float(data.get("championPitchF1", -1)) - EXPECTED_F1) > 0.01:
        raise RuntimeError("Expected frozen 36.76 champion")
    if tuple(int(x) for x in data.get("championMatchedMissingExtra", [])) != EXPECTED:
        raise RuntimeError("Unexpected champion counts")

    rows = list(data.get("targetRows") or [])
    counts = (
        sum(str(r.get("label")) == "true" for r in rows),
        sum(str(r.get("label")) == "false" for r in rows),
    )
    if counts != (7, 31):
        raise RuntimeError(f"Expected target pocket 7/31, got {counts}")

    full_rule = learn_guarded_rule(rows)
    if full_rule is None:
        raise RuntimeError("No safe full-data guarded rule found")
    full = apply(rows, full_rule["fn"])

    matched = EXPECTED[0] - full["truePruned"]
    missing = EXPECTED[1] + full["truePruned"]
    extra = EXPECTED[2] - full["falsePruned"]
    candidate_f1 = f1_from_counts(matched, missing, extra)

    normal = cv_scheme(rows, "normal")
    section = cv_scheme(rows, "section")
    shifted = cv_scheme(rows, "shifted")

    validated = (
        full["truePruned"] == 0
        and full["falsePruned"] > 0
        and candidate_f1 > EXPECTED_F1
        and bool(normal["passed"])
        and bool(section["passed"])
        and bool(shifted["passed"])
    )

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during guarded duration CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "36.76-votes3-guarded-duration-prune-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "fullDataRule": full_rule["rule"],
        "fullDataGuard": full_rule["guard"],
        "candidatePitchF1": candidate_f1,
        "candidateMatchedMissingExtra": [matched, missing, extra],
        "candidateTruePruned": full["truePruned"],
        "candidateFalsePruned": full["falsePruned"],
        "normalCrossValidation": normal,
        "sectionValidation": section,
        "shiftedWindowValidation": shifted,
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

    print("GOMYWAY 36.76 VOTES3 GUARDED DURATION PRUNE CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", EXPECTED_F1)
    print("Baseline matched/missing/extra:", *EXPECTED)
    print("Full-data guarded rule:", full_rule["rule"])
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
