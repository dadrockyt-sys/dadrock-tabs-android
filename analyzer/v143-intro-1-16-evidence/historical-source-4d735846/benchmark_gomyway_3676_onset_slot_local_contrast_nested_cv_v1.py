from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import profile_gomyway_3676_onset_slot_local_transient_contrast_stability_v1 as local

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-local-contrast-nested-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-local-contrast-nested-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 3
FEATURES = list(local.FEATURES)
TAIL_QUANTILES = [0.05, 0.075, 0.10, 0.15, 0.20, 0.25]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision(t: int, f: int) -> float:
    return 100.0 * t / (t + f) if t + f else 0.0


def contiguous_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    return min(folds - 1, int(folds * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / folds
    pos = ((measure - lo) + width / 2.0) % span
    return min(folds - 1, int(pos / width))


def value(row: dict[str, Any], feature: str) -> float:
    return float((row.get("localContrastFeatures") or {}).get(feature, 0.0))


def base_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    t = sum(str(r.get("label")) == "true" for r in rows)
    f = len(rows) - t
    return {"true": t, "false": f, "precision": round(precision(t, f), 2)}


def learn_direction(rows: list[dict[str, Any]], feature: str) -> int:
    tv = [value(r, feature) for r in rows if str(r.get("label")) == "true"]
    fv = [value(r, feature) for r in rows if str(r.get("label")) != "true"]
    if not tv or not fv:
        return 1
    return 1 if float(np.mean(tv)) >= float(np.mean(fv)) else -1


def threshold_for(rows: list[dict[str, Any]], feature: str, direction: int, q: float) -> float:
    scores = np.asarray([direction * value(r, feature) for r in rows], dtype=np.float64)
    return float(np.quantile(scores, 1.0 - q)) if scores.size else float("inf")


def apply(rows: list[dict[str, Any]], feature: str, direction: int, threshold: float) -> dict[str, Any]:
    chosen = [r for r in rows if direction * value(r, feature) >= threshold]
    t = sum(str(r.get("label")) == "true" for r in chosen)
    f = len(chosen) - t
    return {"selected": len(chosen), "true": t, "false": f, "precision": round(precision(t, f), 2)}


def inner_splits(train: list[dict[str, Any]]) -> list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]]:
    measures = [int(r["measure"]) for r in train]
    lo, hi = min(measures), max(measures)
    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % INNER_FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS)),
        ("shifted", lambda m: shifted_fold(m, lo, hi, INNER_FOLDS)),
    ]
    out: list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]] = []
    for scheme_name, fold_fn in schemes:
        for fold in range(INNER_FOLDS):
            inner_train = [r for r in train if fold_fn(int(r["measure"])) != fold]
            inner_test = [r for r in train if fold_fn(int(r["measure"])) == fold]
            if inner_train and inner_test:
                out.append((f"{scheme_name}:{fold}", inner_train, inner_test))
    return out


def choose_feature_and_tail(train: list[dict[str, Any]]) -> dict[str, Any]:
    splits = inner_splits(train)
    candidates: list[dict[str, Any]] = []
    total = len(FEATURES) * len(TAIL_QUANTILES)
    done = 0
    for feature in FEATURES:
        for q in TAIL_QUANTILES:
            done += 1
            if done == 1 or done % 13 == 0 or done == total:
                print(f"    heartbeat local-contrast search {done}/{total}", flush=True)
            folds: list[dict[str, Any]] = []
            for split_name, inner_train, inner_test in splits:
                direction = learn_direction(inner_train, feature)
                threshold = threshold_for(inner_train, feature, direction, q)
                held = apply(inner_test, feature, direction, threshold)
                b = base_stats(inner_test)
                lift = float(held["precision"]) - float(b["precision"])
                passed = held["true"] > 0 and lift >= 5.0
                folds.append({
                    "split": split_name,
                    "direction": direction,
                    "true": held["true"],
                    "false": held["false"],
                    "precision": held["precision"],
                    "basePrecision": b["precision"],
                    "lift": round(lift, 2),
                    "passed": passed,
                })
            pass_count = sum(bool(r["passed"]) for r in folds)
            mean_lift = sum(float(r["lift"]) for r in folds) / len(folds) if folds else -999.0
            true_total = sum(int(r["true"]) for r in folds)
            false_total = sum(int(r["false"]) for r in folds)
            direction_votes = sum(int(r["direction"]) for r in folds)
            candidates.append({
                "feature": feature,
                "tailQuantile": q,
                "innerPassCount": pass_count,
                "innerFoldCount": len(folds),
                "meanLift": round(mean_lift, 3),
                "innerTrue": true_total,
                "innerFalse": false_total,
                "directionVoteSum": direction_votes,
                "folds": folds,
            })
    return max(
        candidates,
        key=lambda r: (
            int(r["innerPassCount"]),
            float(r["meanLift"]),
            int(r["innerTrue"]) - int(r["innerFalse"]),
            int(r["innerTrue"]),
            -float(r["tailQuantile"]),
            r["feature"],
        ),
    )


def evaluate_scheme(rows: list[dict[str, Any]], name: str, fold_fn: Callable[[int], int]) -> tuple[bool, list[dict[str, Any]]]:
    out: list[dict[str, Any]] = []
    pass_count = 0
    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        train = [r for r in rows if fold_fn(int(r["measure"])) != fold]
        test = [r for r in rows if fold_fn(int(r["measure"])) == fold]
        chosen = choose_feature_and_tail(train)
        feature = str(chosen["feature"])
        q = float(chosen["tailQuantile"])
        direction = learn_direction(train, feature)
        threshold = threshold_for(train, feature, direction, q)
        held = apply(test, feature, direction, threshold)
        b = base_stats(test)
        lift = float(held["precision"]) - float(b["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        pass_count += int(passed)
        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "chosen": chosen,
            "feature": feature,
            "direction": direction,
            "threshold": threshold,
            "heldoutBase": b,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": passed,
        }
        out.append(row)
        print(
            f"  feature={feature} direction={direction:+d} q={q} held={held['true']}/{held['false']} "
            f"precision={held['precision']} base={b['precision']} lift={round(lift, 2)} pass={passed}",
            flush=True,
        )
    return pass_count == OUTER_FOLDS, out


def main() -> None:
    before = sha256(local.richer.onset.prof.recall.CANDIDATE_PATH)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source = list(payload.get("candidateSlots") or [])
    if not source:
        raise RuntimeError("Richer onset-slot candidateSlots missing")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source profile not anchored to frozen 36.76 champion")

    # Context features are computed from audio measurements before labels are used for model fitting/grading.
    rows = local.derive_local(source)
    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)

    print("Starting strict nested local-contrast onset-slot CV V1", flush=True)
    normal_pass, normal = evaluate_scheme(rows, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(rows, "section", lambda m: contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted_pass, shifted = evaluate_scheme(rows, "shiftedWindow", lambda m: shifted_fold(m, lo, hi, OUTER_FOLDS))
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(local.richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during local-contrast nested CV")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-onset-slot-local-contrast-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "normalCvPassed": normal_pass,
        "normalCv": normal,
        "sectionStabilityPassed": section_pass,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_pass,
        "shiftedWindowCv": shifted,
        "localContrastOnsetSlotArchitectureGeneralizes": generalizes,
        "validatedNewChampion": False,
        "validationNote": "Exploratory event-slot validation only. Feature identity, direction, and tail threshold are learned from training data only inside each outer fold. Held-out labels are grading only. No pitch recovery or champion promotion allowed.",
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
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
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "localContrastOnsetSlotArchitectureGeneralizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 ONSET SLOT LOCAL CONTRAST NESTED CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Local-contrast onset-slot architecture generalizes:", generalizes)
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
