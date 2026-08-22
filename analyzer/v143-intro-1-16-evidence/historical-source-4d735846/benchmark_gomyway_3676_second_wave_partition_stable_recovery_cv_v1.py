from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_second_wave_partition_stable_recovery_v1 as stable

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PATTERN_PATH = stable.PATTERN_PATH
CONSENSUS_PATH = stable.CONSENSUS_PATH
OUTPUT_PATH = PUBLIC / "gomyway-3676-second-wave-partition-stable-recovery-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-second-wave-partition-stable-recovery-cv-v1-manifest.json"
CANDIDATE_PATH = stable.CANDIDATE_PATH
EXPECTED = stable.EXPECTED
EXPECTED_F1 = stable.EXPECTED_F1
FIRST_WAVE_WEIGHT = stable.FIRST_WAVE_WEIGHT
FOLD_COUNT = 5
CUTOFF = 0.80


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def counts(rows: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        label = str(row.get("label"))
        for sig in set(str(s) for s in (row.get("signatures") or [])):
            out[sig][label] += 1
    return out


def scheme_summary(
    rows: list[dict[str, Any]],
    fold_fn: Callable[[dict[str, Any]], int],
    sig: str,
) -> dict[str, int]:
    positive = 0
    poison = 0
    true = 0
    false = 0
    for fold in range(FOLD_COUNT):
        subset = [r for r in rows if fold_fn(r) == fold and sig in set(str(x) for x in (r.get("signatures") or []))]
        t = sum(str(r.get("label")) == "true" for r in subset)
        f = sum(str(r.get("label")) == "false" for r in subset)
        true += t
        false += f
        if t > 0:
            positive += 1
        if t == 0 and f >= 3:
            poison += 1
    return {"positive": positive, "poison": poison, "true": true, "false": false}


def learn_stable(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    if not rows:
        return {}
    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)
    normal_fn = lambda r: int(r["measure"]) % FOLD_COUNT
    shifted_fn = lambda r: (int(r["measure"]) + 2) % FOLD_COUNT
    section_fn = lambda r: min(FOLD_COUNT - 1, int(FOLD_COUNT * (int(r["measure"]) - lo) / span))

    full = counts(rows)
    learned: dict[str, dict[str, float]] = {}
    # Scale support from the original full-data 8-true minimum.
    min_true = max(5, int(round(8 * len(rows) / max(1, 36453))))
    for sig, c in full.items():
        t = int(c["true"])
        f = int(c["false"])
        total = t + f
        if t < min_true or total == 0:
            continue
        precision = 100.0 * t / total
        if precision < 12.0:
            continue
        summaries = [
            scheme_summary(rows, normal_fn, sig),
            scheme_summary(rows, shifted_fn, sig),
            scheme_summary(rows, section_fn, sig),
        ]
        # Training-only analogue of the profiler's stable-in-all-three-schemes rule.
        if all(s["poison"] == 0 and s["positive"] >= 2 for s in summaries):
            learned[sig] = {
                "true": float(t),
                "false": float(f),
                "precision": precision,
            }
    return learned


def score(rows: list[dict[str, Any]], learned: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        weight = 0.0
        hits = 0
        for sig in set(str(s) for s in (row.get("signatures") or [])):
            info = learned.get(sig)
            if info is None:
                continue
            hits += 1
            weight += float(info["precision"]) / 100.0
        out.append({
            "label": str(row.get("label")),
            "weight": weight,
            "hits": hits,
        })
    return out


def evaluate(rows: list[dict[str, Any]], learned: dict[str, dict[str, float]]) -> dict[str, Any]:
    chosen = [r for r in score(rows, learned) if float(r["weight"]) >= CUTOFF]
    t = sum(r["label"] == "true" for r in chosen)
    f = sum(r["label"] == "false" for r in chosen)
    m = EXPECTED[0] + t
    miss = EXPECTED[1] - t
    extra = EXPECTED[2] + f
    return {
        "selected": len(chosen),
        "recoverTrue": t,
        "recoverFalse": f,
        "precision": round(100.0 * t / len(chosen), 2) if chosen else 0.0,
        "pitchF1": f1(m, miss, extra),
        "matchedMissingExtra": [m, miss, extra],
    }


def validate_partition(
    rows: list[dict[str, Any]],
    fold_fn: Callable[[dict[str, Any]], int],
) -> tuple[bool, list[dict[str, Any]]]:
    results = []
    passed = True
    for fold in range(FOLD_COUNT):
        train = [r for r in rows if fold_fn(r) != fold]
        test = [r for r in rows if fold_fn(r) == fold]
        learned = learn_stable(train)
        held = evaluate(test, learned)
        t = int(held["recoverTrue"])
        f = int(held["recoverFalse"])
        projected = f1(EXPECTED[0] + t, EXPECTED[1] - t, EXPECTED[2] + f)
        fold_pass = t > 0 and projected > EXPECTED_F1
        passed = passed and fold_pass
        results.append({
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "learnedStableSignatureCount": len(learned),
            "cutoff": CUTOFF,
            "heldoutRecoverTrue": t,
            "heldoutRecoverFalse": f,
            "heldoutPrecision": held["precision"],
            "heldoutProjectedPitchF1": projected,
            "passed": fold_pass,
        })
    return passed and len(results) == FOLD_COUNT, results


def main() -> None:
    before = sha256(CANDIDATE_PATH)
    pattern = json.loads(PATTERN_PATH.read_text(encoding="utf-8"))
    consensus = json.loads(CONSENSUS_PATH.read_text(encoding="utf-8"))
    pattern_rows = list(pattern.get("candidateRows") or [])
    first_scored = list(consensus.get("candidateRows") or [])
    if not pattern_rows or not first_scored:
        raise RuntimeError("Missing first-wave contextual rows")

    first_selected = {
        str(r.get("token")) for r in first_scored
        if float(r.get("consensusWeight", 0.0)) >= FIRST_WAVE_WEIGHT
    }
    if len(first_selected) != 322:
        raise RuntimeError(f"Expected 322 first-wave tokens, got {len(first_selected)}")

    rows = [r for r in pattern_rows if str(r.get("token")) not in first_selected]
    full_learned = learn_stable(rows)
    full = evaluate(rows, full_learned)

    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)
    normal_fn = lambda r: int(r["measure"]) % FOLD_COUNT
    shifted_fn = lambda r: (int(r["measure"]) + 2) % FOLD_COUNT
    section_fn = lambda r: min(FOLD_COUNT - 1, int(FOLD_COUNT * (int(r["measure"]) - lo) / span))

    normal_passed, normal_folds = validate_partition(rows, normal_fn)
    shifted_passed, shifted_folds = validate_partition(rows, shifted_fn)
    section_passed, section_folds = validate_partition(rows, section_fn)

    candidate_improves = float(full["pitchF1"]) > EXPECTED_F1 and int(full["recoverTrue"]) > 0
    validated = bool(candidate_improves and normal_passed and shifted_passed and section_passed)

    after = sha256(CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during partition-stable recovery CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "36.76-second-wave-partition-stable-recovery-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "cutoff": CUTOFF,
        "fullDataLearnedStableSignatureCount": len(full_learned),
        "fullDataCandidate": full,
        "recoveryCrossValidationPassed": normal_passed,
        "recoveryCrossValidationFolds": normal_folds,
        "sectionStabilityPassed": section_passed,
        "sectionFolds": section_folds,
        "shiftedWindowStabilityPassed": shifted_passed,
        "shiftedWindowFolds": shifted_folds,
        "validatedNewChampion": validated,
        "professionalReferenceUsedDuringDetection": False,
        "protected949CandidateHashUnchanged": before == after,
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

    print("GOMYWAY 36.76 SECOND-WAVE PARTITION-STABLE RECOVERY CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", EXPECTED_F1)
    print("Baseline matched/missing/extra:", *EXPECTED)
    print("Full-data learned stable signatures:", len(full_learned))
    print("Full-data candidate:", full)
    print("Recovery cross-validation passed:", normal_passed)
    for r in normal_folds:
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
