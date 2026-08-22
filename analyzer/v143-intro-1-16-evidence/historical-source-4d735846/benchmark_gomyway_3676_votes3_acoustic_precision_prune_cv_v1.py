from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_votes3_acoustic_refinement_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3676-votes3-acoustic-refinement-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-votes3-acoustic-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-votes3-acoustic-precision-prune-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5
SUPPORTS = (2, 3)

recall = prof.recall


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def learn(rows: list[dict[str, Any]], support: int) -> set[str]:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        label = str(row["label"])
        for sig in row.get("signatures") or []:
            groups[str(sig)][label] += 1
    return {
        sig for sig, c in groups.items()
        if int(c["true"]) == 0 and int(c["false"]) >= support
    }


def evaluate(rows: list[dict[str, Any]], signatures: set[str]) -> dict[str, Any]:
    chosen = [
        row for row in rows
        if signatures.intersection(str(s) for s in row.get("signatures") or [])
    ]
    true_pruned = sum(1 for row in chosen if str(row["label"]) == "true")
    false_pruned = sum(1 for row in chosen if str(row["label"]) == "false")
    matched = EXPECTED[0] - true_pruned
    missing = EXPECTED[1] + true_pruned
    extra = EXPECTED[2] - false_pruned
    return {
        "pruned": len(chosen),
        "truePruned": true_pruned,
        "falsePruned": false_pruned,
        "pitchF1": f1(matched, missing, extra),
        "matchedMissingExtra": [matched, missing, extra],
    }


def validate_partition(
    rows: list[dict[str, Any]],
    fold_fn: Callable[[dict[str, Any]], int],
    support: int,
    name: str,
) -> tuple[bool, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    passed = True
    for fold in range(FOLD_COUNT):
        train = [r for r in rows if fold_fn(r) != fold]
        test = [r for r in rows if fold_fn(r) == fold]
        if not test:
            results.append({"partition": name, "fold": fold, "skipped": True, "passed": True})
            continue
        if not train:
            results.append({"partition": name, "fold": fold, "skipped": False, "passed": False})
            passed = False
            continue
        scaled_support = max(2, int(round(support * len(train) / len(rows))))
        signatures = learn(train, scaled_support)
        held = evaluate(test, signatures)
        fold_pass = int(held["truePruned"]) == 0
        passed = passed and fold_pass
        results.append({
            "partition": name,
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "support": scaled_support,
            "learnedSignatureCount": len(signatures),
            **held,
            "passed": fold_pass,
        })
    # Require zero held-out true loss everywhere and at least one held-out false removal overall.
    false_total = sum(int(r.get("falsePruned", 0)) for r in results)
    return passed and false_total > 0, results


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
    if (true_count, false_count) != (7, 31):
        raise RuntimeError(f"Expected votes>=3 target 7/31, got {true_count}/{false_count}")

    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)

    def section_fold(row: dict[str, Any]) -> int:
        rel = int(row["measure"]) - lo
        return min(FOLD_COUNT - 1, int(FOLD_COUNT * rel / span))

    candidates: list[dict[str, Any]] = []
    for support in SUPPORTS:
        full_signatures = learn(rows, support)
        full = evaluate(rows, full_signatures)
        full_pass = (
            int(full["truePruned"]) == 0
            and int(full["falsePruned"]) > 0
            and float(full["pitchF1"]) > EXPECTED_F1
        )

        cv_pass, cv_rows = validate_partition(
            rows, lambda r: int(r["measure"]) % FOLD_COUNT, support, "normal"
        )
        shifted_pass, shifted_rows = validate_partition(
            rows, lambda r: (int(r["measure"]) + 2) % FOLD_COUNT, support, "shifted"
        )
        section_pass, section_rows = validate_partition(rows, section_fold, support, "section")

        validated = bool(full_pass and cv_pass and shifted_pass and section_pass)
        candidates.append({
            "support": support,
            "fullDataSignatureCount": len(full_signatures),
            "fullDataCandidate": full,
            "crossValidationPassed": cv_pass,
            "crossValidationFolds": cv_rows,
            "shiftedWindowStabilityPassed": shifted_pass,
            "shiftedWindowFolds": shifted_rows,
            "sectionStabilityPassed": section_pass,
            "sectionFolds": section_rows,
            "validatedNewChampion": validated,
        })

    valid = [c for c in candidates if c["validatedNewChampion"]]
    best = max(
        valid,
        key=lambda c: (
            float(c["fullDataCandidate"]["pitchF1"]),
            int(c["fullDataCandidate"]["falsePruned"]),
        ),
    ) if valid else None

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during votes3 acoustic prune CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "36.76-votes3-acoustic-precision-prune-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "targetTrue": true_count,
        "targetFalse": false_count,
        "candidates": candidates,
        "bestValidatedCandidate": best,
        "validatedNewChampion": best is not None,
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
        "baselinePitchF1": EXPECTED_F1,
        "validatedNewChampion": best is not None,
        "candidatePitchF1": best["fullDataCandidate"]["pitchF1"] if best else None,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 VOTES3 ACOUSTIC PRECISION PRUNE CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", EXPECTED_F1)
    print("Baseline matched/missing/extra:", *EXPECTED)
    print("Target votes>=3 true/false:", true_count, "/", false_count)
    for c in candidates:
        f = c["fullDataCandidate"]
        print(
            f"support={c['support']} signatures={c['fullDataSignatureCount']} "
            f"F1={f['pitchF1']} m/m/e={f['matchedMissingExtra']} "
            f"pruned={f['pruned']} truePruned={f['truePruned']} falsePruned={f['falsePruned']} "
            f"cv={c['crossValidationPassed']} section={c['sectionStabilityPassed']} "
            f"shifted={c['shiftedWindowStabilityPassed']} accepted={c['validatedNewChampion']}"
        )
    print("Best validated candidate:", best)
    print("Validated new champion:", best is not None)
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
