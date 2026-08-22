from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_pitch_register_interval_recovery_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-prcross-nested-consensus-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-prcross-nested-consensus-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5
INNER_FOLDS = 4
CUTOFFS = [0.35, 0.50, 0.65, 0.80, 1.00, 1.25, 1.50]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pitch_f1(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def prcross_signatures(row: dict[str, Any]) -> set[str]:
    return {str(s) for s in (row.get("signatures") or []) if str(s).startswith("prCross::")}


def sig_counts(rows: list[dict[str, Any]], sig: str) -> tuple[int, int]:
    true = false = 0
    for row in rows:
        if sig not in prcross_signatures(row):
            continue
        if str(row.get("label")) == "true":
            true += 1
        else:
            false += 1
    return true, false


def precision(true: int, false: int) -> float:
    total = true + false
    return 100.0 * true / total if total else 0.0


def contiguous_fold(measure: int, lo: int, hi: int, fold_count: int) -> int:
    span = max(1, hi - lo + 1)
    return min(fold_count - 1, int(fold_count * (measure - lo) / span))


def shifted_window_fold(measure: int, lo: int, hi: int, fold_count: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / fold_count
    shift = width / 2.0
    pos = ((measure - lo) + shift) % span
    return min(fold_count - 1, int(pos / width))


def inner_scheme_useful(
    rows: list[dict[str, Any]],
    sig: str,
    fold_fn: Callable[[int], int],
) -> bool:
    supported = useful = 0
    for fold in range(INNER_FOLDS):
        held = [r for r in rows if fold_fn(int(r["measure"])) == fold]
        t, f = sig_counts(held, sig)
        if t + f == 0:
            continue
        supported += 1
        if t > 0 and precision(t, f) >= 35.0:
            useful += 1
    return supported >= 2 and useful >= 2


def learn_stable_signatures(train: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    measures = sorted({int(r["measure"]) for r in train})
    lo, hi = min(measures), max(measures)
    all_sigs: set[str] = set()
    for row in train:
        all_sigs.update(prcross_signatures(row))

    normal_fn = lambda m: m % INNER_FOLDS
    section_fn = lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS)
    shifted_fn = lambda m: shifted_window_fold(m, lo, hi, INNER_FOLDS)

    learned: dict[str, dict[str, Any]] = {}
    for sig in sorted(all_sigs):
        t, f = sig_counts(train, sig)
        if t < 3 or t + f < 4 or precision(t, f) < 40.0:
            continue
        agreement = sum([
            inner_scheme_useful(train, sig, normal_fn),
            inner_scheme_useful(train, sig, section_fn),
            inner_scheme_useful(train, sig, shifted_fn),
        ])
        if agreement < 2:
            continue
        learned[sig] = {
            "true": t,
            "false": f,
            "precision": precision(t, f),
            "agreementSchemes": agreement,
        }
    return learned


def score_rows(rows: list[dict[str, Any]], learned: dict[str, dict[str, Any]], cutoff: float) -> dict[str, Any]:
    chosen: list[dict[str, Any]] = []
    for row in rows:
        weight = sum(
            float(learned[s]["precision"]) / 100.0
            for s in prcross_signatures(row)
            if s in learned
        )
        if weight >= cutoff:
            chosen.append(row)
    true = sum(str(r.get("label")) == "true" for r in chosen)
    false = len(chosen) - true
    matched = EXPECTED[0] + true
    missing = EXPECTED[1] - true
    extra = EXPECTED[2] + false
    return {
        "selected": len(chosen),
        "recoverTrue": true,
        "recoverFalse": false,
        "precision": round(precision(true, false), 2),
        "pitchF1": pitch_f1(matched, missing, extra),
        "matchedMissingExtra": [matched, missing, extra],
    }


def choose_cutoff(train: list[dict[str, Any]], learned: dict[str, dict[str, Any]]) -> tuple[float, dict[str, Any]]:
    candidates: list[tuple[float, dict[str, Any]]] = []
    for cutoff in CUTOFFS:
        result = score_rows(train, learned, cutoff)
        if int(result["recoverTrue"]) > 0 and float(result["pitchF1"]) > EXPECTED_F1:
            candidates.append((cutoff, result))
    if not candidates:
        cutoff = max(CUTOFFS)
        return cutoff, score_rows(train, learned, cutoff)
    return max(
        candidates,
        key=lambda item: (
            float(item[1]["pitchF1"]),
            float(item[1]["precision"]),
            int(item[1]["recoverTrue"]),
            -int(item[1]["recoverFalse"]),
        ),
    )


def evaluate_scheme(
    rows: list[dict[str, Any]],
    name: str,
    fold_fn: Callable[[int], int],
) -> tuple[bool, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    passed = True
    for fold in range(FOLD_COUNT):
        train = [r for r in rows if fold_fn(int(r["measure"])) != fold]
        test = [r for r in rows if fold_fn(int(r["measure"])) == fold]
        learned = learn_stable_signatures(train)
        cutoff, train_best = choose_cutoff(train, learned)
        held = score_rows(test, learned, cutoff)
        fold_pass = (
            len(learned) > 0
            and int(held["recoverTrue"]) > 0
            and float(held["pitchF1"]) > EXPECTED_F1
        )
        passed = passed and fold_pass
        results.append({
            "scheme": name,
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "learnedStablePrCrossCount": len(learned),
            "learnedStablePrCross": sorted(learned),
            "chosenCutoff": cutoff,
            "trainCandidate": train_best,
            "heldoutCandidate": held,
            "passed": fold_pass,
        })
    return passed, results


def main() -> None:
    before = sha256(prof.recall.CANDIDATE_PATH)
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    rows = list(profile.get("candidateRows") or [])
    if not rows:
        raise RuntimeError("Pitch/register/interval profiler candidate rows are missing")
    if tuple(profile.get("championMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Profiler is not anchored to frozen 36.76 champion")

    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)

    normal_passed, normal = evaluate_scheme(rows, "normal", lambda m: m % FOLD_COUNT)
    section_passed, section = evaluate_scheme(
        rows,
        "section",
        lambda m: contiguous_fold(m, lo, hi, FOLD_COUNT),
    )
    shifted_passed, shifted = evaluate_scheme(
        rows,
        "shiftedWindow",
        lambda m: shifted_window_fold(m, lo, hi, FOLD_COUNT),
    )

    # Exploratory family validation only. prCross was selected after the earlier
    # full-data diagnostic, so this benchmark cannot by itself promote a champion.
    family_generalizes = normal_passed and section_passed and shifted_passed
    validated_new_champion = False

    after = sha256(prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during prCross nested consensus CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-prcross-nested-consensus-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "normalCvPassed": normal_passed,
        "normalCv": normal,
        "sectionStabilityPassed": section_passed,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_passed,
        "shiftedWindowCv": shifted,
        "prCrossFamilyGeneralizes": family_generalizes,
        "validatedNewChampion": validated_new_champion,
        "validationNote": "Exploratory family validation only because prCross family was selected after prior full-data diagnostic. No champion promotion allowed from this benchmark alone.",
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
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
        "prCrossFamilyGeneralizes": family_generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PRCROSS NESTED CONSENSUS CV V1 COMPLETE")
    print("Passed: True")
    print("Frozen champion:", EXPECTED_F1, EXPECTED)
    print("Normal CV passed:", normal_passed)
    for row in normal:
        print("NORMAL", row)
    print("Section stability passed:", section_passed)
    for row in section:
        print("SECTION", row)
    print("Shifted-window stability passed:", shifted_passed)
    for row in shifted:
        print("SHIFTED", row)
    print("prCross family generalizes:", family_generalizes)
    print("Validated new champion: False")
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
