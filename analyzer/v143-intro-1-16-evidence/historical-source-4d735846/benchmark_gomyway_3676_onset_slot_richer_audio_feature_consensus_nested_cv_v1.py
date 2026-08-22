from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_onset_slot_richer_audio_nested_cv_v1 as base

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-feature-consensus-nested-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-feature-consensus-nested-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 3
FEATURES = list(base.FEATURES)
CONSENSUS_MIN_SUPPORT = [2, 3, 4]
FAILURE_PENALTY = [0.0, 0.5, 1.0]
QUANTILES = [0.80, 0.90, 0.95, 0.975]
TOP_K_CHOICES = [2, 3, 5, 8]


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


def score_row(row: dict[str, Any], model: dict[str, Any]) -> float:
    total = 0.0
    norm = 0.0
    for name in model.get("features") or []:
        w = float(model["weights"][name])
        z = (feature_value(row, name) - float(model["center"][name])) / float(model["scale"][name])
        total += w * z
        norm += abs(w)
    return total / norm if norm > 1e-12 else -1e9


def threshold_for(rows: list[dict[str, Any]], model: dict[str, Any], q: float) -> float:
    scores = np.asarray([score_row(r, model) for r in rows], dtype=np.float64)
    return float(np.quantile(scores, q)) if scores.size else float("inf")


def apply(rows: list[dict[str, Any]], model: dict[str, Any], threshold: float) -> dict[str, Any]:
    chosen = [r for r in rows if score_row(r, model) >= threshold]
    t = sum(str(r.get("label")) == "true" for r in chosen)
    f = len(chosen) - t
    return {"selected": len(chosen), "true": t, "false": f, "precision": round(precision(t, f), 2)}


def inner_schemes(rows: list[dict[str, Any]]) -> list[tuple[str, Callable[[int], int]]]:
    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    return [
        ("normal", lambda m: m % INNER_FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS)),
        ("shifted", lambda m: shifted_fold(m, lo, hi, INNER_FOLDS)),
    ]


def collect_inner_models(train: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for scheme_name, fold_fn in inner_schemes(train):
        for fold in range(INNER_FOLDS):
            inner_train = [r for r in train if fold_fn(int(r["measure"])) != fold]
            inner_test = [r for r in train if fold_fn(int(r["measure"])) == fold]
            if not inner_train or not inner_test:
                continue
            top_k, consistency, q, _ = base.choose_hyperparams(inner_train)
            model = base.learn_model(inner_train, top_k, consistency)
            if not model.get("features"):
                held = {"true": 0, "false": 0, "precision": 0.0}
                lift = -float(base_stats(inner_test)["precision"])
                passed = False
            else:
                threshold = base.threshold_for(inner_train, model, q)
                held = base.apply(inner_test, model, threshold)
                b = base_stats(inner_test)
                lift = float(held["precision"]) - float(b["precision"])
                passed = held["true"] > 0 and lift >= 5.0
            out.append({
                "scheme": scheme_name,
                "fold": fold,
                "features": list(model.get("features") or []),
                "weights": dict(model.get("weights") or {}),
                "passed": passed,
                "lift": round(lift, 2),
                "true": int(held["true"]),
                "false": int(held["false"]),
            })
    return out


def learn_consensus_model(
    train: list[dict[str, Any]],
    min_support: int,
    failure_penalty: float,
    top_k: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    inner = collect_inner_models(train)
    success_count: Counter[str] = Counter()
    failure_count: Counter[str] = Counter()
    sign_votes: dict[str, Counter[int]] = defaultdict(Counter)
    abs_weight_sum: Counter[str] = Counter()

    for result in inner:
        bucket = success_count if result["passed"] else failure_count
        for name in result["features"]:
            bucket[name] += 1
            w = float(result["weights"].get(name, 0.0))
            if w != 0.0:
                sign_votes[name][1 if w > 0 else -1] += 1
                abs_weight_sum[name] += abs(w)

    ranked: list[tuple[str, float, int, int]] = []
    for name in FEATURES:
        s = int(success_count[name])
        f = int(failure_count[name])
        score = float(s) - failure_penalty * float(f)
        if s < min_support or score <= 0.0:
            continue
        ranked.append((name, score, s, f))
    ranked.sort(key=lambda x: (-x[1], -x[2], x[3], x[0]))
    chosen_names = [name for name, *_ in ranked[: max(1, min(top_k, len(ranked)))]]

    center: dict[str, float] = {}
    scale: dict[str, float] = {}
    weights: dict[str, float] = {}
    for name in chosen_names:
        vals = np.asarray([feature_value(r, name) for r in train], dtype=np.float64)
        mu = float(np.mean(vals))
        sd = float(np.std(vals))
        if not math.isfinite(sd) or sd < 1e-9:
            sd = 1.0
        votes = sign_votes[name]
        dominant_sign = 1 if votes[1] >= votes[-1] else -1
        eff = standardized_effect(train, name)
        mean_inner_abs = abs_weight_sum[name] / max(1, votes[1] + votes[-1])
        magnitude = max(abs(eff), float(mean_inner_abs), 1e-6)
        center[name] = mu
        scale[name] = sd
        weights[name] = float(dominant_sign) * magnitude

    model = {
        "features": chosen_names,
        "center": center,
        "scale": scale,
        "weights": weights,
    }
    diagnostics = {
        "innerModels": inner,
        "successSelections": dict(success_count),
        "failureSelections": dict(failure_count),
        "rankedConsensus": [
            {"feature": n, "consensusScore": s, "successSelections": sp, "failureSelections": fp}
            for n, s, sp, fp in ranked
        ],
    }
    return model, diagnostics


def choose_consensus_hyperparams(train: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    measures = [int(r["measure"]) for r in train]
    lo, hi = min(measures), max(measures)
    schemes = [
        ("normal", lambda m: m % INNER_FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS)),
        ("shifted", lambda m: shifted_fold(m, lo, hi, INNER_FOLDS)),
    ]
    candidates: list[dict[str, Any]] = []
    for min_support in CONSENSUS_MIN_SUPPORT:
        for penalty in FAILURE_PENALTY:
            for top_k in TOP_K_CHOICES:
                for q in QUANTILES:
                    folds: list[dict[str, Any]] = []
                    for scheme_name, fold_fn in schemes:
                        for fold in range(INNER_FOLDS):
                            inner_train = [r for r in train if fold_fn(int(r["measure"])) != fold]
                            inner_test = [r for r in train if fold_fn(int(r["measure"])) == fold]
                            if not inner_train or not inner_test:
                                continue
                            model, _ = learn_consensus_model(inner_train, min_support, penalty, top_k)
                            if not model["features"]:
                                held = {"true": 0, "false": 0, "precision": 0.0}
                            else:
                                threshold = threshold_for(inner_train, model, q)
                                held = apply(inner_test, model, threshold)
                            b = base_stats(inner_test)
                            lift = float(held["precision"]) - float(b["precision"])
                            passed = held["true"] > 0 and lift >= 5.0
                            folds.append({
                                "scheme": scheme_name,
                                "fold": fold,
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
                    candidates.append({
                        "minSupport": min_support,
                        "failurePenalty": penalty,
                        "topK": top_k,
                        "quantile": q,
                        "innerPassCount": pass_count,
                        "innerFoldCount": len(folds),
                        "meanLift": round(mean_lift, 3),
                        "innerTrue": true_total,
                        "innerFalse": false_total,
                        "folds": folds,
                    })
    chosen = max(
        candidates,
        key=lambda r: (
            int(r["innerPassCount"]),
            float(r["meanLift"]),
            int(r["innerTrue"]) - int(r["innerFalse"]),
            int(r["innerTrue"]),
            float(r["failurePenalty"]),
            int(r["minSupport"]),
            -int(r["topK"]),
            -float(r["quantile"]),
        ),
    )
    return chosen, {"candidates": candidates}


def evaluate_scheme(rows: list[dict[str, Any]], name: str, fold_fn: Callable[[int], int]) -> tuple[bool, list[dict[str, Any]]]:
    out: list[dict[str, Any]] = []
    pass_count = 0
    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        train = [r for r in rows if fold_fn(int(r["measure"])) != fold]
        test = [r for r in rows if fold_fn(int(r["measure"])) == fold]
        chosen, search = choose_consensus_hyperparams(train)
        model, consensus = learn_consensus_model(
            train,
            int(chosen["minSupport"]),
            float(chosen["failurePenalty"]),
            int(chosen["topK"]),
        )
        threshold = threshold_for(train, model, float(chosen["quantile"])) if model["features"] else float("inf")
        held = apply(test, model, threshold) if model["features"] else {"selected": 0, "true": 0, "false": 0, "precision": 0.0}
        b = base_stats(test)
        lift = float(held["precision"]) - float(b["precision"])
        passed = bool(model["features"]) and held["true"] > 0 and lift >= 5.0
        pass_count += int(passed)
        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "chosen": chosen,
            "model": model,
            "consensusDiagnostics": consensus,
            "heldoutBase": b,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": passed,
        }
        out.append(row)
        print(
            f"  features={model['features']} support={chosen['minSupport']} penalty={chosen['failurePenalty']} "
            f"q={chosen['quantile']} held={held['true']}/{held['false']} precision={held['precision']} "
            f"base={b['precision']} lift={round(lift, 2)} pass={passed}",
            flush=True,
        )
    return pass_count == OUTER_FOLDS, out


def main() -> None:
    before = sha256(base.richer.onset.prof.recall.CANDIDATE_PATH)
    payload = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Richer onset-slot candidateSlots missing; run richer-audio stability profiler first")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Richer onset-slot profile is not anchored to frozen 36.76 champion")

    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    print("Starting strict nested richer-audio feature-consensus onset-slot CV V1", flush=True)
    normal_pass, normal = evaluate_scheme(rows, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(rows, "section", lambda m: contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted_pass, shifted = evaluate_scheme(rows, "shiftedWindow", lambda m: shifted_fold(m, lo, hi, OUTER_FOLDS))
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(base.richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during richer-audio feature-consensus nested CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-onset-slot-richer-audio-feature-consensus-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "normalCvPassed": normal_pass,
        "normalCv": normal,
        "sectionStabilityPassed": section_pass,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_pass,
        "shiftedWindowCv": shifted,
        "featureConsensusOnsetSlotArchitectureGeneralizes": generalizes,
        "validatedNewChampion": False,
        "validationNote": "Exploratory event-slot validation only. Feature success/failure consensus, feature signs/weights, and score threshold are derived from training data only inside each outer fold. Held-out labels are grading only. No pitch recovery or champion promotion is allowed.",
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
        "featureConsensusOnsetSlotArchitectureGeneralizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 ONSET SLOT RICHER AUDIO FEATURE CONSENSUS NESTED CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Feature-consensus onset-slot architecture generalizes:", generalizes)
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
