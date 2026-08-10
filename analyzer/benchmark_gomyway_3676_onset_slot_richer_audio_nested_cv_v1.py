from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

import profile_gomyway_3676_onset_slot_richer_audio_stability_v1 as richer

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-nested-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-nested-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 3
FEATURES = list(richer.FEATURE_NAMES)
TOP_K_CHOICES = [1, 2, 3, 5, 8]
CONSISTENCY_CHOICES = [0.75, 0.85, 1.0]
QUANTILES = [0.80, 0.90, 0.95, 0.975]


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


def feature_value(row: dict[str, Any], name: str) -> float:
    return float((row.get("features") or {}).get(name, 0.0))


def base_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    t = sum(str(r.get("label")) == "true" for r in rows)
    f = len(rows) - t
    return {"true": t, "false": f, "precision": round(precision(t, f), 2)}


def standardized_effect(rows: list[dict[str, Any]], name: str) -> float:
    true_rows = [r for r in rows if str(r.get("label")) == "true"]
    false_rows = [r for r in rows if str(r.get("label")) != "true"]
    if not true_rows or not false_rows:
        return 0.0
    vals = np.asarray([feature_value(r, name) for r in rows], dtype=np.float64)
    sd = float(np.std(vals))
    if not math.isfinite(sd) or sd < 1e-9:
        return 0.0
    tm = float(np.mean([feature_value(r, name) for r in true_rows]))
    fm = float(np.mean([feature_value(r, name) for r in false_rows]))
    return (tm - fm) / sd


def orientation_evidence(rows: list[dict[str, Any]], folds: int = INNER_FOLDS) -> dict[str, dict[str, Any]]:
    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    schemes: list[Callable[[int], int]] = [
        lambda m: m % folds,
        lambda m: contiguous_fold(m, lo, hi, folds),
        lambda m: shifted_fold(m, lo, hi, folds),
    ]
    out: dict[str, dict[str, Any]] = {}
    for name in FEATURES:
        signs: list[int] = []
        effects: list[float] = []
        for fold_fn in schemes:
            for fold in range(folds):
                train = [r for r in rows if fold_fn(int(r["measure"])) != fold]
                eff = standardized_effect(train, name)
                if abs(eff) < 1e-9:
                    continue
                signs.append(1 if eff > 0 else -1)
                effects.append(eff)
        pos = sum(s > 0 for s in signs)
        neg = sum(s < 0 for s in signs)
        support = pos + neg
        dominant = 1 if pos >= neg else -1
        consistency = max(pos, neg) / support if support else 0.0
        out[name] = {
            "positive": pos,
            "negative": neg,
            "support": support,
            "dominantSign": dominant,
            "consistency": consistency,
            "meanAbsEffect": float(np.mean(np.abs(effects))) if effects else 0.0,
        }
    return out


def learn_model(rows: list[dict[str, Any]], top_k: int, min_consistency: float) -> dict[str, Any]:
    orientation = orientation_evidence(rows)
    eligible = [
        (name, info)
        for name, info in orientation.items()
        if int(info["support"]) >= 5
        and float(info["consistency"]) >= min_consistency
        and float(info["meanAbsEffect"]) >= 0.02
    ]
    eligible.sort(
        key=lambda x: (
            -float(x[1]["consistency"]),
            -float(x[1]["meanAbsEffect"]),
            x[0],
        )
    )
    chosen = eligible[: max(1, min(top_k, len(eligible)))]
    center: dict[str, float] = {}
    scale: dict[str, float] = {}
    weights: dict[str, float] = {}
    for name, info in chosen:
        vals = np.asarray([feature_value(r, name) for r in rows], dtype=np.float64)
        mu = float(np.mean(vals))
        sd = float(np.std(vals))
        if not math.isfinite(sd) or sd < 1e-9:
            sd = 1.0
        eff = standardized_effect(rows, name)
        magnitude = max(abs(eff), float(info["meanAbsEffect"]), 1e-6)
        weights[name] = float(info["dominantSign"]) * magnitude
        center[name] = mu
        scale[name] = sd
    return {
        "features": [name for name, _ in chosen],
        "center": center,
        "scale": scale,
        "weights": weights,
        "orientation": orientation,
        "minConsistency": min_consistency,
    }


def score_row(row: dict[str, Any], model: dict[str, Any]) -> float:
    total = 0.0
    norm = 0.0
    for name in model.get("features") or []:
        w = float(model["weights"][name])
        z = (feature_value(row, name) - float(model["center"][name])) / float(model["scale"][name])
        total += w * z
        norm += abs(w)
    return total / norm if norm > 1e-12 else -1e9


def threshold_for(rows: list[dict[str, Any]], model: dict[str, Any], quantile: float) -> float:
    scores = np.asarray([score_row(r, model) for r in rows], dtype=np.float64)
    return float(np.quantile(scores, quantile)) if scores.size else float("inf")


def apply(rows: list[dict[str, Any]], model: dict[str, Any], threshold: float) -> dict[str, Any]:
    chosen = [r for r in rows if score_row(r, model) >= threshold]
    t = sum(str(r.get("label")) == "true" for r in chosen)
    f = len(chosen) - t
    return {
        "selected": len(chosen),
        "true": t,
        "false": f,
        "precision": round(precision(t, f), 2),
    }


def choose_hyperparams(train: list[dict[str, Any]]) -> tuple[int, float, float, dict[str, Any]]:
    measures = [int(r["measure"]) for r in train]
    lo, hi = min(measures), max(measures)
    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % INNER_FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS)),
        ("shifted", lambda m: shifted_fold(m, lo, hi, INNER_FOLDS)),
    ]
    candidates: list[dict[str, Any]] = []
    for consistency in CONSISTENCY_CHOICES:
        for top_k in TOP_K_CHOICES:
            for q in QUANTILES:
                fold_rows: list[dict[str, Any]] = []
                for scheme_name, fold_fn in schemes:
                    for fold in range(INNER_FOLDS):
                        inner_train = [r for r in train if fold_fn(int(r["measure"])) != fold]
                        inner_test = [r for r in train if fold_fn(int(r["measure"])) == fold]
                        if not inner_train or not inner_test:
                            continue
                        model = learn_model(inner_train, top_k, consistency)
                        if not model["features"]:
                            held = {"selected": 0, "true": 0, "false": 0, "precision": 0.0}
                        else:
                            threshold = threshold_for(inner_train, model, q)
                            held = apply(inner_test, model, threshold)
                        base = base_stats(inner_test)
                        lift = float(held["precision"]) - float(base["precision"])
                        passed = held["true"] > 0 and lift >= 5.0
                        fold_rows.append({
                            "scheme": scheme_name,
                            "fold": fold,
                            "true": held["true"],
                            "false": held["false"],
                            "precision": held["precision"],
                            "basePrecision": base["precision"],
                            "lift": round(lift, 2),
                            "passed": passed,
                        })
                pass_count = sum(bool(r["passed"]) for r in fold_rows)
                true_total = sum(int(r["true"]) for r in fold_rows)
                false_total = sum(int(r["false"]) for r in fold_rows)
                mean_lift = (
                    sum(float(r["lift"]) for r in fold_rows) / len(fold_rows)
                    if fold_rows else -999.0
                )
                candidates.append({
                    "minConsistency": consistency,
                    "topK": top_k,
                    "quantile": q,
                    "innerPassCount": pass_count,
                    "innerFoldCount": len(fold_rows),
                    "innerTrue": true_total,
                    "innerFalse": false_total,
                    "meanLift": round(mean_lift, 3),
                    "folds": fold_rows,
                })
    chosen = max(
        candidates,
        key=lambda r: (
            int(r["innerPassCount"]),
            float(r["meanLift"]),
            int(r["innerTrue"]) - int(r["innerFalse"]),
            int(r["innerTrue"]),
            float(r["minConsistency"]),
            -int(r["topK"]),
            -float(r["quantile"]),
        ),
    )
    return (
        int(chosen["topK"]),
        float(chosen["minConsistency"]),
        float(chosen["quantile"]),
        chosen,
    )


def evaluate_scheme(
    rows: list[dict[str, Any]],
    name: str,
    fold_fn: Callable[[int], int],
) -> tuple[bool, list[dict[str, Any]]]:
    out: list[dict[str, Any]] = []
    pass_count = 0
    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        train = [r for r in rows if fold_fn(int(r["measure"])) != fold]
        test = [r for r in rows if fold_fn(int(r["measure"])) == fold]
        top_k, consistency, q, inner = choose_hyperparams(train)
        model = learn_model(train, top_k, consistency)
        threshold = threshold_for(train, model, q) if model["features"] else float("inf")
        held = (
            apply(test, model, threshold)
            if model["features"]
            else {"selected": 0, "true": 0, "false": 0, "precision": 0.0}
        )
        base = base_stats(test)
        lift = float(held["precision"]) - float(base["precision"])
        passed = bool(model["features"]) and held["true"] > 0 and lift >= 5.0
        pass_count += int(passed)
        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "chosenTopK": top_k,
            "chosenMinConsistency": consistency,
            "chosenQuantile": q,
            "model": model,
            "threshold": threshold,
            "innerSelection": inner,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": passed,
        }
        out.append(row)
        print(
            f"  features={model['features']} consistency={consistency} q={q} "
            f"held={held['true']}/{held['false']} precision={held['precision']} "
            f"base={base['precision']} lift={round(lift, 2)} pass={passed}",
            flush=True,
        )
    return pass_count == OUTER_FOLDS, out


def main() -> None:
    before = sha256(richer.onset.prof.recall.CANDIDATE_PATH)
    payload = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError(
            "Richer onset-slot candidateSlots missing; run "
            "profile_gomyway_3676_onset_slot_richer_audio_stability_v1.py first"
        )
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Richer onset-slot profile is not anchored to frozen 36.76 champion")

    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)

    print("Starting strict nested richer-audio onset-slot CV V1", flush=True)
    normal_pass, normal = evaluate_scheme(
        rows, "normal", lambda m: m % OUTER_FOLDS
    )
    section_pass, section = evaluate_scheme(
        rows, "section", lambda m: contiguous_fold(m, lo, hi, OUTER_FOLDS)
    )
    shifted_pass, shifted = evaluate_scheme(
        rows, "shiftedWindow", lambda m: shifted_fold(m, lo, hi, OUTER_FOLDS)
    )
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during richer-audio onset-slot nested CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-onset-slot-richer-audio-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "featureNames": FEATURES,
        "normalCvPassed": normal_pass,
        "normalCv": normal,
        "sectionStabilityPassed": section_pass,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_pass,
        "shiftedWindowCv": shifted,
        "richerAudioOnsetSlotArchitectureGeneralizes": generalizes,
        "validatedNewChampion": False,
        "validationNote": (
            "Exploratory event-slot validation only. Richer audio feature orientation "
            "stability, feature count, consistency threshold, score weights, and "
            "decision quantile are learned from training data only through nested "
            "validation. No pitch recovery or champion promotion is allowed."
        ),
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
        "richerAudioOnsetSlotArchitectureGeneralizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 ONSET SLOT RICHER AUDIO NESTED CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Richer-audio onset-slot architecture generalizes:", generalizes)
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
