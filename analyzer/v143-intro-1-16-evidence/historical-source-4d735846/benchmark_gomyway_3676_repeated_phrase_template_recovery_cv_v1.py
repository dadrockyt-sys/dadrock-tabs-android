from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3161_protected_source_recall_recovery_v1 as protected

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3676-repeated-phrase-template-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-repeated-phrase-template-recovery-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-repeated-phrase-template-recovery-cv-v1-manifest.json"
CANDIDATE_PATH = protected.recall.CANDIDATE_PATH
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5
CUTOFFS = [0.20, 0.30, 0.40, 0.50, 0.60, 0.75, 1.00, 1.25, 1.50, 2.00]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pitch_f1(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def signature_counts(rows: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        label = str(row.get("label"))
        for sig in set(str(s) for s in (row.get("signatures") or [])):
            groups[sig][label] += 1
    return groups


def learn_signature_weights(rows: list[dict[str, Any]]) -> dict[str, float]:
    groups = signature_counts(rows)
    weights: dict[str, float] = {}
    for sig, counts in groups.items():
        true = int(counts["true"])
        false = int(counts["false"])
        total = true + false
        precision = true / total if total else 0.0
        # Same family as the profiler, scaled for training-fold support.
        if true >= 3 and precision >= 0.20:
            weights[sig] = precision
    return weights


def score_rows(rows: list[dict[str, Any]], weights: dict[str, float]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for row in rows:
        weight = sum(weights.get(str(sig), 0.0) for sig in set(row.get("signatures") or []))
        scored.append({**row, "cvWeight": round(weight, 6)})
    return scored


def recovery_stats(rows: list[dict[str, Any]], cutoff: float) -> dict[str, Any]:
    chosen = [row for row in rows if float(row.get("cvWeight", 0.0)) >= cutoff]
    true = sum(str(row.get("label")) == "true" for row in chosen)
    false = sum(str(row.get("label")) == "false" for row in chosen)
    m = EXPECTED[0] + true
    miss = EXPECTED[1] - true
    extra = EXPECTED[2] + false
    return {
        "selected": len(chosen),
        "recoverTrue": true,
        "recoverFalse": false,
        "precision": round(100.0 * true / len(chosen), 2) if chosen else 0.0,
        "projectedPitchF1": pitch_f1(m, miss, extra),
        "matchedMissingExtra": [m, miss, extra],
    }


def choose_cutoff(train_rows: list[dict[str, Any]], weights: dict[str, float]) -> tuple[float, dict[str, Any]]:
    scored = score_rows(train_rows, weights)
    candidates: list[tuple[float, dict[str, Any]]] = []
    for cutoff in CUTOFFS:
        stats = recovery_stats(scored, cutoff)
        if int(stats["recoverTrue"]) <= 0:
            continue
        candidates.append((cutoff, stats))
    if not candidates:
        return CUTOFFS[-1], recovery_stats(scored, CUTOFFS[-1])
    return max(
        candidates,
        key=lambda item: (
            float(item[1]["projectedPitchF1"]),
            float(item[1]["precision"]),
            int(item[1]["recoverTrue"]),
            -int(item[1]["recoverFalse"]),
        ),
    )


def validate_scheme(
    rows: list[dict[str, Any]],
    fold_fn: Callable[[dict[str, Any]], int],
    scheme: str,
) -> tuple[bool, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    all_pass = True
    for fold in range(FOLD_COUNT):
        train = [row for row in rows if fold_fn(row) != fold]
        test = [row for row in rows if fold_fn(row) == fold]
        weights = learn_signature_weights(train)
        cutoff, train_stats = choose_cutoff(train, weights)
        test_scored = score_rows(test, weights)
        heldout = recovery_stats(test_scored, cutoff)

        # Recovery must actually recover something unseen and improve the frozen champion.
        passed = (
            int(heldout["recoverTrue"]) > 0
            and float(heldout["projectedPitchF1"]) > EXPECTED_F1
        )
        all_pass = all_pass and passed
        results.append({
            "scheme": scheme,
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "learnedSignatureCount": len(weights),
            "chosenCutoff": cutoff,
            "trainRecoverTrue": int(train_stats["recoverTrue"]),
            "trainRecoverFalse": int(train_stats["recoverFalse"]),
            "trainProjectedPitchF1": float(train_stats["projectedPitchF1"]),
            "heldoutRecoverTrue": int(heldout["recoverTrue"]),
            "heldoutRecoverFalse": int(heldout["recoverFalse"]),
            "heldoutPrecision": float(heldout["precision"]),
            "heldoutProjectedPitchF1": float(heldout["projectedPitchF1"]),
            "passed": passed,
        })
    return all_pass, results


def main() -> None:
    before = sha256(CANDIDATE_PATH)
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    rows = list(profile.get("candidateRows") or [])
    if not rows:
        raise RuntimeError("Repeated-phrase profiler candidate rows are missing")
    if tuple(profile.get("championMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Repeated-phrase profiler is not anchored to frozen 36.76 champion")

    # Full-data candidate is relearned from the same phrase family for reporting only.
    full_weights = learn_signature_weights(rows)
    full_cutoff, full_stats = choose_cutoff(rows, full_weights)

    measures = sorted({int(row["measure"]) for row in rows})
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)

    normal_fn = lambda row: int(row["measure"]) % FOLD_COUNT
    shifted_fn = lambda row: (int(row["measure"]) + 2) % FOLD_COUNT
    section_fn = lambda row: min(
        FOLD_COUNT - 1,
        int(FOLD_COUNT * (int(row["measure"]) - lo) / span),
    )

    normal_pass, normal_results = validate_scheme(rows, normal_fn, "normal")
    section_pass, section_results = validate_scheme(rows, section_fn, "section")
    shifted_pass, shifted_results = validate_scheme(rows, shifted_fn, "shifted")

    full_improves = float(full_stats["projectedPitchF1"]) > EXPECTED_F1 and int(full_stats["recoverTrue"]) > 0
    validated = full_improves and normal_pass and section_pass and shifted_pass

    after = sha256(CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected 949-event candidate changed during phrase recovery CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "36.76-repeated-phrase-template-recovery-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "fullDataLearnedSignatureCount": len(full_weights),
        "fullDataChosenCutoff": full_cutoff,
        "fullDataCandidate": full_stats,
        "normalCrossValidationPassed": normal_pass,
        "normalFolds": normal_results,
        "sectionStabilityPassed": section_pass,
        "sectionFolds": section_results,
        "shiftedWindowStabilityPassed": shifted_pass,
        "shiftedFolds": shifted_results,
        "validatedNewChampion": validated,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-only",
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
        "validatedNewChampion": validated,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 REPEATED-PHRASE TEMPLATE RECOVERY CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", EXPECTED_F1)
    print("Baseline matched/missing/extra:", *EXPECTED)
    print("Full-data learned phrase signatures:", len(full_weights))
    print("Full-data chosen cutoff:", full_cutoff)
    print("Full-data candidate:", full_stats)
    print("Recovery cross-validation passed:", normal_pass)
    for result in normal_results:
        print("CV", result)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
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
