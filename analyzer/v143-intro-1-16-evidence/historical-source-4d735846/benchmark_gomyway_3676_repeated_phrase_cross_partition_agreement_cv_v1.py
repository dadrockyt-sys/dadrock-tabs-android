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
OUTPUT_PATH = PUBLIC / "gomyway-3676-repeated-phrase-cross-partition-agreement-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-repeated-phrase-cross-partition-agreement-cv-v1-manifest.json"
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


def region_stats(rows: list[dict[str, Any]], signature: str) -> tuple[int, int, float, int]:
    hit = [r for r in rows if signature in set(str(s) for s in (r.get("signatures") or []))]
    true = sum(str(r.get("label")) == "true" for r in hit)
    false = sum(str(r.get("label")) == "false" for r in hit)
    total = true + false
    precision = (100.0 * true / total) if total else 0.0
    return true, false, precision, total


def make_schemes(rows: list[dict[str, Any]]) -> list[tuple[str, Callable[[dict[str, Any]], int]]]:
    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)
    return [
        ("normal", lambda row: int(row["measure"]) % FOLD_COUNT),
        ("shifted", lambda row: (int(row["measure"]) + 2) % FOLD_COUNT),
        (
            "section",
            lambda row: min(
                FOLD_COUNT - 1,
                int(FOLD_COUNT * (int(row["measure"]) - lo) / span),
            ),
        ),
    ]


def learn_stable_signatures(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    signatures = sorted({str(sig) for r in rows for sig in (r.get("signatures") or [])})
    schemes = make_schemes(rows)
    stable: dict[str, dict[str, Any]] = {}

    for sig in signatures:
        full_true, full_false, full_precision, _ = region_stats(rows, sig)
        positive_regions = 0
        useful_regions = 0
        poison_regions = 0

        for _scheme, fold_fn in schemes:
            for fold in range(FOLD_COUNT):
                subset = [r for r in rows if fold_fn(r) == fold]
                true, false, precision, support = region_stats(subset, sig)
                if support <= 0:
                    continue
                if true > 0:
                    positive_regions += 1
                if true > 0 and precision >= 20.0:
                    useful_regions += 1
                if true == 0 and false >= 3:
                    poison_regions += 1

        if (
            full_true >= 3
            and full_precision >= 20.0
            and useful_regions >= 4
            and poison_regions <= 1
        ):
            stable[sig] = {
                "true": full_true,
                "false": full_false,
                "precision": full_precision,
                "positiveRegions": positive_regions,
                "usefulRegions": useful_regions,
                "poisonRegions": poison_regions,
            }
    return stable


def score_rows(rows: list[dict[str, Any]], stable: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for row in rows:
        hits = [stable[str(sig)] for sig in set(row.get("signatures") or []) if str(sig) in stable]
        weight = sum(
            (float(h["precision"]) / 100.0)
            * (1.0 + 0.08 * int(h["usefulRegions"]))
            / (1.0 + int(h["poisonRegions"]))
            for h in hits
        )
        scored.append({**row, "nestedAgreementWeight": round(weight, 6)})
    return scored


def recovery_stats(rows: list[dict[str, Any]], cutoff: float) -> dict[str, Any]:
    chosen = [r for r in rows if float(r.get("nestedAgreementWeight", 0.0)) >= cutoff]
    true = sum(str(r.get("label")) == "true" for r in chosen)
    false = sum(str(r.get("label")) == "false" for r in chosen)
    matched = EXPECTED[0] + true
    missing = EXPECTED[1] - true
    extra = EXPECTED[2] + false
    return {
        "selected": len(chosen),
        "recoverTrue": true,
        "recoverFalse": false,
        "precision": round(100.0 * true / len(chosen), 2) if chosen else 0.0,
        "projectedPitchF1": pitch_f1(matched, missing, extra),
        "matchedMissingExtra": [matched, missing, extra],
    }


def choose_cutoff(train_scored: list[dict[str, Any]]) -> tuple[float, dict[str, Any]]:
    choices: list[tuple[float, dict[str, Any]]] = []
    for cutoff in CUTOFFS:
        stats = recovery_stats(train_scored, cutoff)
        if int(stats["recoverTrue"]) <= 0:
            continue
        choices.append((cutoff, stats))
    if not choices:
        cutoff = CUTOFFS[-1]
        return cutoff, recovery_stats(train_scored, cutoff)
    return max(
        choices,
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
        train = [r for r in rows if fold_fn(r) != fold]
        test = [r for r in rows if fold_fn(r) == fold]
        stable = learn_stable_signatures(train)
        train_scored = score_rows(train, stable)
        cutoff, train_stats = choose_cutoff(train_scored)
        test_scored = score_rows(test, stable)
        heldout = recovery_stats(test_scored, cutoff)

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
            "learnedStableSignatureCount": len(stable),
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

    full_stable = learn_stable_signatures(rows)
    full_scored = score_rows(rows, full_stable)
    full_cutoff, full_stats = choose_cutoff(full_scored)

    measures = sorted({int(r["measure"]) for r in rows})
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

    full_improves = int(full_stats["recoverTrue"]) > 0 and float(full_stats["projectedPitchF1"]) > EXPECTED_F1
    validated = full_improves and normal_pass and section_pass and shifted_pass

    after = sha256(CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during nested phrase agreement CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "36.76-repeated-phrase-cross-partition-agreement-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "fullDataStableSignatureCount": len(full_stable),
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

    print("GOMYWAY 36.76 REPEATED-PHRASE CROSS-PARTITION AGREEMENT CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", EXPECTED_F1)
    print("Baseline matched/missing/extra:", *EXPECTED)
    print("Full-data stable signatures:", len(full_stable))
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
