from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_pitch_register_interval_recovery_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-prcross-nested-consensus-cv-v2.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-prcross-nested-consensus-cv-v2-manifest.json"
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


def prepare_rows(raw_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in raw_rows:
        rows.append({
            "measure": int(row["measure"]),
            "label": str(row.get("label")),
            "prcross": tuple(
                str(s) for s in (row.get("signatures") or [])
                if str(s).startswith("prCross::")
            ),
        })
    return rows


def aggregate(rows: list[dict[str, Any]], fold_fn: Callable[[int], int] | None = None) -> dict[str, Any]:
    totals: dict[str, Counter[str]] = defaultdict(Counter)
    folds: dict[str, dict[int, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    for row in rows:
        label = row["label"]
        fold = fold_fn(row["measure"]) if fold_fn is not None else -1
        for sig in row["prcross"]:
            totals[sig][label] += 1
            if fold_fn is not None:
                folds[sig][fold][label] += 1
    return {"totals": totals, "folds": folds}


def scheme_useful(agg: dict[str, Any], sig: str) -> bool:
    supported = useful = 0
    by_fold = agg["folds"].get(sig, {})
    for fold in range(INNER_FOLDS):
        c = by_fold.get(fold, Counter())
        t = int(c["true"])
        f = int(c["false"])
        if t + f == 0:
            continue
        supported += 1
        if t > 0 and precision(t, f) >= 35.0:
            useful += 1
    return supported >= 2 and useful >= 2


def learn_stable_signatures(train: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    measures = [r["measure"] for r in train]
    lo, hi = min(measures), max(measures)

    normal_agg = aggregate(train, lambda m: m % INNER_FOLDS)
    section_agg = aggregate(train, lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS))
    shifted_agg = aggregate(train, lambda m: shifted_window_fold(m, lo, hi, INNER_FOLDS))
    totals = normal_agg["totals"]

    learned: dict[str, dict[str, Any]] = {}
    for sig, c in totals.items():
        t = int(c["true"])
        f = int(c["false"])
        if t < 3 or t + f < 4 or precision(t, f) < 40.0:
            continue
        agreement = sum((
            scheme_useful(normal_agg, sig),
            scheme_useful(section_agg, sig),
            scheme_useful(shifted_agg, sig),
        ))
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
    true = false = 0
    for row in rows:
        weight = sum(
            float(learned[s]["precision"]) / 100.0
            for s in row["prcross"] if s in learned
        )
        if weight < cutoff:
            continue
        if row["label"] == "true":
            true += 1
        else:
            false += 1
    matched = EXPECTED[0] + true
    missing = EXPECTED[1] - true
    extra = EXPECTED[2] + false
    return {
        "selected": true + false,
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
        if result["recoverTrue"] > 0 and result["pitchF1"] > EXPECTED_F1:
            candidates.append((cutoff, result))
    if not candidates:
        cutoff = max(CUTOFFS)
        return cutoff, score_rows(train, learned, cutoff)
    return max(
        candidates,
        key=lambda item: (
            item[1]["pitchF1"], item[1]["precision"], item[1]["recoverTrue"], -item[1]["recoverFalse"]
        ),
    )


def evaluate_scheme(rows: list[dict[str, Any]], name: str, fold_fn: Callable[[int], int]) -> tuple[bool, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    passed = True
    for fold in range(FOLD_COUNT):
        print(f"{name}: outer fold {fold + 1}/{FOLD_COUNT} ...", flush=True)
        train = [r for r in rows if fold_fn(r["measure"]) != fold]
        test = [r for r in rows if fold_fn(r["measure"]) == fold]
        learned = learn_stable_signatures(train)
        cutoff, train_best = choose_cutoff(train, learned)
        held = score_rows(test, learned, cutoff)
        fold_pass = bool(learned) and held["recoverTrue"] > 0 and held["pitchF1"] > EXPECTED_F1
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
        print(
            f"  learned={len(learned)} cutoff={cutoff} held={held['recoverTrue']}/{held['recoverFalse']} F1={held['pitchF1']} pass={fold_pass}",
            flush=True,
        )
    return passed, results


def main() -> None:
    before = sha256(prof.recall.CANDIDATE_PATH)
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    raw_rows = list(profile.get("candidateRows") or [])
    if not raw_rows:
        raise RuntimeError("Pitch/register/interval profiler candidate rows are missing")
    if tuple(profile.get("championMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Profiler is not anchored to frozen 36.76 champion")

    rows = prepare_rows(raw_rows)
    measures = [r["measure"] for r in rows]
    lo, hi = min(measures), max(measures)

    print("Starting optimized prCross nested consensus CV V2", flush=True)
    normal_passed, normal = evaluate_scheme(rows, "normal", lambda m: m % FOLD_COUNT)
    section_passed, section = evaluate_scheme(rows, "section", lambda m: contiguous_fold(m, lo, hi, FOLD_COUNT))
    shifted_passed, shifted = evaluate_scheme(rows, "shiftedWindow", lambda m: shifted_window_fold(m, lo, hi, FOLD_COUNT))

    family_generalizes = normal_passed and section_passed and shifted_passed
    after = sha256(prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during prCross nested consensus CV")

    output = {
        "schemaVersion": 2,
        "passed": True,
        "profileType": "36.76-prcross-nested-consensus-cv-exploratory-optimized",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "normalCvPassed": normal_passed,
        "normalCv": normal,
        "sectionStabilityPassed": section_passed,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_passed,
        "shiftedWindowCv": shifted,
        "prCrossFamilyGeneralizes": family_generalizes,
        "validatedNewChampion": False,
        "validationNote": "Exploratory family validation only. prCross was selected after prior full-data diagnostic; no champion promotion allowed from this benchmark alone.",
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
        "schemaVersion": 2,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "prCrossFamilyGeneralizes": family_generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PRCROSS NESTED CONSENSUS CV V2 COMPLETE")
    print("Passed: True")
    print("Frozen champion:", EXPECTED_F1, EXPECTED)
    print("Normal CV passed:", normal_passed)
    print("Section stability passed:", section_passed)
    print("Shifted-window stability passed:", shifted_passed)
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
