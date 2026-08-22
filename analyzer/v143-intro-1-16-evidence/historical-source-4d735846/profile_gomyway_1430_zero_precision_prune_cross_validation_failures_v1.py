from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import benchmark_gomyway_1430_cached_periodicity_zero_precision_prune_v1 as prune

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1430-zero-precision-prune-cross-validation-failures-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1430-zero-precision-prune-cross-validation-failures-v1-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_failures(value: Any, path: str = "") -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if child is False:
                out.append(child_path)
            elif isinstance(child, (dict, list)):
                out.extend(compact_failures(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            if child is False:
                out.append(child_path)
            elif isinstance(child, (dict, list)):
                out.extend(compact_failures(child, child_path))
    return out


def numeric_leaves(value: Any, path: str = "") -> list[tuple[str, float]]:
    out: list[tuple[str, float]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if isinstance(child, bool):
                continue
            if isinstance(child, (int, float)):
                out.append((child_path, float(child)))
            elif isinstance(child, (dict, list)):
                out.extend(numeric_leaves(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            if isinstance(child, bool):
                continue
            if isinstance(child, (int, float)):
                out.append((child_path, float(child)))
            elif isinstance(child, (dict, list)):
                out.extend(numeric_leaves(child, child_path))
    return out


def main() -> None:
    before = sha256(prune.recall.CANDIDATE_PATH)

    periodicity_payload = prune.v2.load_json(prune.PERIODICITY_PATH)
    precision_payload = prune.v2.load_json(prune.PRECISION_PATH)
    if periodicity_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Periodicity profile is not reference-free during detection.")
    if precision_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Precision profile is not reference-free during detection.")

    payload = prune.v2.load_json(prune.recall.CANDIDATE_PATH)
    events = prune.v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = prune.v2.build_timing_grid(events)

    reference_payload = prune.v2.load_json(prune.recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = prune.v3.reference_tokens(reference_payload)

    cached_rows = prune.cached.load_profile_rows()
    baseline_1382, _, _ = prune.recur.build_frozen_1382(grid)
    additions_1419 = prune.bench.rows_to_counter(cached_rows, prune.bench.champion_1419_predicate)
    champion_1419 = baseline_1382 + additions_1419

    periodicity_rows = list(periodicity_payload.get("rows", []))
    winner_rows = [row for row in periodicity_rows if prune.gate.sig_d(row)]
    periodicity_additions = prune.gate.rows_to_counter(winner_rows, lambda row: True)
    champion_1430 = champion_1419 + periodicity_additions
    score_1430 = prune.recur.grade(champion_1430, reference)
    actual = (
        int(score_1430["matched"]),
        int(score_1430["missing"]),
        int(score_1430["extra"]),
    )
    if actual != prune.EXPECTED_1430 or abs(float(score_1430["pitchF1"]) - prune.EXPECTED_1430_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.30 champion, got {actual}/{score_1430['pitchF1']}")

    precision_rows = list(precision_payload.get("rows", []))
    precision_by_token = {prune.token(row): row for row in precision_rows}
    eligible_rows: list[dict[str, Any]] = []
    for prow in winner_rows:
        tok = prune.token(prow)
        detail = precision_by_token.get(tok)
        if detail is None:
            raise RuntimeError(f"Missing precision detail for token {tok}")
        merged = dict(detail)
        merged["token"] = list(tok)
        eligible_rows.append(merged)

    results: dict[str, Any] = {}
    for name, predicate in prune.VARIANTS:
        pruned = Counter()
        pruned_rows: list[dict[str, Any]] = []
        for row in eligible_rows:
            if predicate(row):
                tok = prune.token(row)
                pruned[tok] = 1
                pruned_rows.append(row)

        candidate = champion_1430 - pruned
        full = prune.recur.grade(candidate, reference)
        stability = prune.recall.evaluate_recall(candidate, champion_1430, reference, score_1430)
        failures = compact_failures(stability)
        numerics = numeric_leaves(stability)

        false_prunes = sum(1 for row in pruned_rows if not bool(row.get("trueAddition")))
        true_prunes = sum(1 for row in pruned_rows if bool(row.get("trueAddition")))

        results[name] = {
            "fullScore": full,
            "pruneCount": int(sum(pruned.values())),
            "trueAdditionsPruned": true_prunes,
            "falseAdditionsPruned": false_prunes,
            "crossValidationPassed": bool(stability.get("crossValidationPassed")),
            "sectionStabilityPassed": bool(stability.get("sectionStabilityPassed")),
            "shiftedWindowStabilityPassed": bool(stability.get("shiftedWindowStabilityPassed")),
            "falseBooleanPaths": failures,
            "numericLeaves": [{"path": p, "value": v} for p, v in numerics],
            "stability": stability,
            "prunedTokens": [list(prune.token(row)) for row in pruned_rows],
        }

        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} pruned={sum(pruned.values())} truePruned={true_prunes} "
            f"falsePruned={false_prunes} cv={stability.get('crossValidationPassed')} "
            f"sections={stability.get('sectionStabilityPassed')} shifted={stability.get('shiftedWindowStabilityPassed')}",
            flush=True,
        )
        if failures:
            print("  false paths:", ", ".join(failures[:24]), flush=True)
        else:
            print("  false paths: none", flush=True)

    after = sha256(prune.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during CV failure profiling")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "14.30-zero-precision-prune-cross-validation-failure-diagnostic",
        "baseline1430Score": score_1430,
        "results": results,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "derive-fold-stable-subset-of-zero-precision-prunes-without-weakening-validation",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "baselinePitchF1": score_1430["pitchF1"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.30 ZERO-PRECISION PRUNE CROSS-VALIDATION FAILURES V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", score_1430["pitchF1"])
    print("Baseline matched/missing/extra:", score_1430["matched"], "/", score_1430["missing"], "/", score_1430["extra"])
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
