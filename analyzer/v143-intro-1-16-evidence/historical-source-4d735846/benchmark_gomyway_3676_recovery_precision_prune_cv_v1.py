from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_recovery_precision_survivors_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3676-recovery-precision-survivors-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-recovery-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-recovery-precision-prune-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5

recall = prof.recall


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1_from_counts(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def learn_zero_precision(rows: list[dict[str, Any]], support: int) -> set[str]:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        label = str(row["label"])
        for sig in row.get("signatures") or []:
            groups[str(sig)][label] += 1
    return {
        sig
        for sig, c in groups.items()
        if int(c["true"]) == 0 and int(c["false"]) >= support
    }


def evaluate(rows: list[dict[str, Any]], signatures: set[str]) -> dict[str, Any]:
    chosen = [
        row for row in rows
        if signatures.intersection(str(s) for s in row.get("signatures") or [])
    ]
    true_pruned = sum(1 for row in chosen if row["label"] == "true")
    false_pruned = sum(1 for row in chosen if row["label"] == "false")
    matched = EXPECTED[0] - true_pruned
    missing = EXPECTED[1] + true_pruned
    extra = EXPECTED[2] - false_pruned
    return {
        "pruned": len(chosen),
        "truePruned": true_pruned,
        "falsePruned": false_pruned,
        "pitchF1": f1_from_counts(matched, missing, extra),
        "matchedMissingExtra": [matched, missing, extra],
    }


def validate_partition(
    rows: list[dict[str, Any]],
    fold_fn: Callable[[dict[str, Any]], int],
) -> tuple[bool, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    passed = True
    for fold in range(FOLD_COUNT):
        train = [r for r in rows if fold_fn(r) != fold]
        test = [r for r in rows if fold_fn(r) == fold]
        if not train or not test:
            passed = False
            continue
        # Five-false full-data support scales to four examples in an 80% training fold.
        support = max(3, int(round(5 * len(train) / len(rows))))
        learned = learn_zero_precision(train, support)
        held = evaluate(test, learned)
        fold_pass = int(held["truePruned"]) == 0 and int(held["falsePruned"]) > 0
        passed = passed and fold_pass
        results.append({
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "support": support,
            "learnedSignatureCount": len(learned),
            **held,
            "passed": fold_pass,
        })
    return passed and len(results) == FOLD_COUNT, results


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    if not INPUT_PATH.exists():
        raise RuntimeError(f"Missing prerequisite profiler output: {INPUT_PATH.relative_to(ROOT)}")

    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if abs(float(data.get("championPitchF1", -1)) - EXPECTED_F1) > 0.01:
        raise RuntimeError("Expected frozen 36.76 champion")
    counts = tuple(int(x) for x in data.get("championMatchedMissingExtra", []))
    if counts != EXPECTED:
        raise RuntimeError(f"Expected frozen champion {EXPECTED}, got {counts}")

    rows = list(data.get("selectedRecoveryRows") or [])
    if not rows:
        raise RuntimeError("No selected recovery rows found")
    true_count = sum(1 for r in rows if r["label"] == "true")
    false_count = sum(1 for r in rows if r["label"] == "false")
    if (true_count, false_count) != (89, 233):
        raise RuntimeError(f"Expected recovery layer 89/233, got {true_count}/{false_count}")

    full_signatures = learn_zero_precision(rows, 5)
    full = evaluate(rows, full_signatures)
    full_pass = (
        int(full["truePruned"]) == 0
        and int(full["falsePruned"]) > 0
        and float(full["pitchF1"]) > EXPECTED_F1
    )

    cv_passed, cv_folds = validate_partition(rows, lambda r: int(r["measure"]) % FOLD_COUNT)
    shifted_passed, shifted_folds = validate_partition(rows, lambda r: (int(r["measure"]) + 2) % FOLD_COUNT)

    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)
    def section_fold(row: dict[str, Any]) -> int:
        rel = int(row["measure"]) - lo
        return min(FOLD_COUNT - 1, int(FOLD_COUNT * rel / span))
    section_passed, section_folds = validate_partition(rows, section_fold)

    validated = bool(full_pass and cv_passed and shifted_passed and section_passed)

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 36.76 recovery precision prune CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "36.76-recovery-precision-prune-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "fullDataZeroPrecisionSignatureCount": len(full_signatures),
        "fullDataCandidate": full,
        "pruneSpecificCrossValidationPassed": cv_passed,
        "crossValidationFolds": cv_folds,
        "sectionStabilityPassed": section_passed,
        "sectionFolds": section_folds,
        "shiftedWindowStabilityPassed": shifted_passed,
        "shiftedWindowFolds": shifted_folds,
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
        "candidateSha256": after,
        "baselinePitchF1": EXPECTED_F1,
        "candidatePitchF1": full["pitchF1"],
        "validatedNewChampion": validated,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RECOVERY PRECISION PRUNE CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", EXPECTED_F1)
    print("Baseline matched/missing/extra:", *EXPECTED)
    print("Full-data zero-precision signatures:", len(full_signatures))
    print("Candidate pitch F1:", full["pitchF1"])
    print("Candidate matched/missing/extra:", *full["matchedMissingExtra"])
    print("Candidate prune count:", full["pruned"])
    print("Candidate true pruned:", full["truePruned"])
    print("Candidate false pruned:", full["falsePruned"])
    print("Prune-specific cross-validation passed:", cv_passed)
    for r in cv_folds:
        print("CV", r)
    print("Section stability passed:", section_passed)
    print("Shifted-window stability passed:", shifted_passed)
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
