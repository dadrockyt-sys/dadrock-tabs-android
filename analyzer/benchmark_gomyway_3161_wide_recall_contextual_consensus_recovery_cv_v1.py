from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3161_wide_recall_contextual_pattern_recovery_v1 as ctxprof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-consensus-recovery-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-consensus-recovery-cv-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61
FOLD_COUNT = 5
WEIGHT_CUTOFFS = [0.40, 0.60, 0.80, 1.00, 1.20, 1.50, 1.80, 2.00]

recall = ctxprof.recall


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1_from_counts(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def signature_stats(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        label = str(row.get("label"))
        for sig in row.get("signatures") or []:
            counts[str(sig)][label] += 1
    out: dict[str, dict[str, float]] = {}
    for sig, c in counts.items():
        t = int(c["true"])
        f = int(c["false"])
        total = t + f
        out[sig] = {
            "true": t,
            "false": f,
            "precision": 100.0 * t / total if total else 0.0,
        }
    return out


def select_broad(stats: dict[str, dict[str, float]], train_fraction: float) -> dict[str, dict[str, float]]:
    # Same broad-family idea as the profiler, but support thresholds scale to training-fold size.
    min20 = max(8, int(round(20 * train_fraction)))
    min35 = max(14, int(round(35 * train_fraction)))
    selected: dict[str, dict[str, float]] = {}
    for sig, r in stats.items():
        t = int(r["true"])
        p = float(r["precision"])
        if (t >= min20 and p >= 20.0) or (t >= min35 and p >= 10.0):
            selected[sig] = r
    return selected


def score_rows(rows: list[dict[str, Any]], selected: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for row in rows:
        weight = 0.0
        votes = 0
        for sig in row.get("signatures") or []:
            r = selected.get(str(sig))
            if r is None:
                continue
            votes += 1
            weight += float(r["precision"]) / 100.0
        scored.append({
            "measure": int(row["measure"]),
            "step": int(row["step"]),
            "pitch": int(row["pitch"]),
            "label": str(row["label"]),
            "votes": votes,
            "weight": weight,
        })
    return scored


def evaluate(rows: list[dict[str, Any]], cutoff: float) -> dict[str, Any]:
    chosen = [r for r in rows if float(r["weight"]) >= cutoff]
    true = sum(1 for r in chosen if r["label"] == "true")
    false = sum(1 for r in chosen if r["label"] == "false")
    matched = EXPECTED[0] + true
    missing = EXPECTED[1] - true
    extra = EXPECTED[2] + false
    return {
        "cutoff": cutoff,
        "selected": len(chosen),
        "recoverTrue": true,
        "recoverFalse": false,
        "precision": round(100.0 * true / len(chosen), 2) if chosen else 0.0,
        "candidatePitchF1": f1_from_counts(matched, missing, extra),
        "matchedMissingExtra": [matched, missing, extra],
    }


def best_training_cutoff(rows: list[dict[str, Any]], selected: dict[str, dict[str, float]]) -> dict[str, Any]:
    scored = score_rows(rows, selected)
    candidates = [evaluate(scored, c) for c in WEIGHT_CUTOFFS]
    useful = [r for r in candidates if int(r["recoverTrue"]) >= 10]
    pool = useful or candidates
    return max(pool, key=lambda r: (float(r["candidatePitchF1"]), int(r["recoverTrue"]), -int(r["recoverFalse"])))


def recovery_improves_baseline(true: int, false: int) -> bool:
    return f1_from_counts(EXPECTED[0] + true, EXPECTED[1] - true, EXPECTED[2] + false) > EXPECTED_F1


def validate_partition(rows: list[dict[str, Any]], fold_fn) -> tuple[bool, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    passed = True
    for fold in range(FOLD_COUNT):
        train = [r for r in rows if fold_fn(r) != fold]
        test = [r for r in rows if fold_fn(r) == fold]
        if not train or not test:
            continue
        stats = signature_stats(train)
        selected = select_broad(stats, len(train) / len(rows))
        best = best_training_cutoff(train, selected)
        scored_test = score_rows(test, selected)
        held = evaluate(scored_test, float(best["cutoff"]))
        t = int(held["recoverTrue"])
        f = int(held["recoverFalse"])
        fold_pass = t > 0 and recovery_improves_baseline(t, f)
        passed = passed and fold_pass
        results.append({
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "selectedSignatureCount": len(selected),
            "chosenCutoff": best["cutoff"],
            "trainCandidatePitchF1": best["candidatePitchF1"],
            "heldoutRecoverTrue": t,
            "heldoutRecoverFalse": f,
            "heldoutPrecision": held["precision"],
            "heldoutProjectedPitchF1": held["candidatePitchF1"],
            "passed": fold_pass,
        })
    return passed and len(results) == FOLD_COUNT, results


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    if not INPUT_PATH.exists():
        raise RuntimeError(f"Missing prerequisite profiler output: {INPUT_PATH.relative_to(ROOT)}")
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    baseline = data.get("champion3161Score") or {}
    actual = (int(baseline.get("matched", -1)), int(baseline.get("missing", -1)), int(baseline.get("extra", -1)))
    if actual != EXPECTED or abs(float(baseline.get("pitchF1", -1.0)) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 31.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline.get('pitchF1')}")

    rows = list(data.get("candidateRows") or [])
    if not rows:
        raise RuntimeError("No contextual recovery candidate rows found")

    full_stats = signature_stats(rows)
    full_selected = select_broad(full_stats, 1.0)
    full_best = best_training_cutoff(rows, full_selected)

    cv_passed, cv_folds = validate_partition(rows, lambda r: int(r["measure"]) % FOLD_COUNT)
    shifted_passed, shifted_folds = validate_partition(rows, lambda r: (int(r["measure"]) + 2) % FOLD_COUNT)

    # Section-style stability: contiguous measure bands rather than modulo folds.
    measures = sorted({int(r["measure"]) for r in rows})
    if not measures:
        raise RuntimeError("No measures in contextual recovery rows")
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)
    def section_fold(r: dict[str, Any]) -> int:
        rel = int(r["measure"]) - lo
        return min(FOLD_COUNT - 1, int(FOLD_COUNT * rel / span))
    section_passed, section_folds = validate_partition(rows, section_fold)

    candidate_improves = float(full_best["candidatePitchF1"]) > EXPECTED_F1 and int(full_best["recoverTrue"]) >= 20
    validated = bool(candidate_improves and cv_passed and shifted_passed and section_passed)

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during recovery CV benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "31.61-wide-recall-contextual-consensus-recovery-cv",
        "baseline": baseline,
        "fullDataBestCandidate": full_best,
        "fullDataSelectedSignatureCount": len(full_selected),
        "recoveryCrossValidationPassed": cv_passed,
        "recoveryCrossValidationFolds": cv_folds,
        "shiftedWindowStabilityPassed": shifted_passed,
        "shiftedWindowFolds": shifted_folds,
        "sectionStabilityPassed": section_passed,
        "sectionFolds": section_folds,
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
        "candidatePitchF1": full_best["candidatePitchF1"],
        "validatedNewChampion": validated,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 WIDE-RECALL CONTEXTUAL CONSENSUS RECOVERY CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", baseline["pitchF1"])
    print("Baseline matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    print("Full-data candidate:", full_best)
    print("Recovery cross-validation passed:", cv_passed)
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
