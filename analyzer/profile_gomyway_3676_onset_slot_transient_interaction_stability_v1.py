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
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-transient-interaction-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-transient-interaction-stability-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLDS = 5

INTERACTIONS = [
    "shortLongDecay",
    "attackShortMinusSustainLong",
    "attackMediumMinusSustainLong",
    "fluxShortMinusSustainLong",
    "fluxMediumMinusSustainLong",
    "highBandMinusSustainLong",
    "crestMinusSustainLong",
    "stemAttackTimesTransient",
    "stemFluxTimesTransient",
    "stemPeakTimingTimesTransient",
    "dualStemTransient",
    "fluxAttackTransient",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f(row: dict[str, Any], name: str) -> float:
    return float((row.get("features") or {}).get(name, 0.0))


def derive(row: dict[str, Any]) -> dict[str, float]:
    attack_s = f(row, "attackShortMean")
    attack_m = f(row, "attackMediumMean")
    flux_s = f(row, "fluxShortMean")
    flux_m = f(row, "fluxMediumMean")
    sustain_s = f(row, "sustainShortMean")
    sustain_l = f(row, "sustainLongMean")
    high = f(row, "highBandAttackMean")
    crest = f(row, "crestMean")
    stem_attack = f(row, "stemAttackAgreement")
    stem_flux = f(row, "stemFluxAgreement")
    stem_timing = f(row, "stemPeakTimingAgreement")

    transient_a = attack_s - sustain_l
    transient_f = flux_s - sustain_l
    return {
        "shortLongDecay": sustain_s - sustain_l,
        "attackShortMinusSustainLong": transient_a,
        "attackMediumMinusSustainLong": attack_m - sustain_l,
        "fluxShortMinusSustainLong": transient_f,
        "fluxMediumMinusSustainLong": flux_m - sustain_l,
        "highBandMinusSustainLong": high - sustain_l,
        "crestMinusSustainLong": crest - sustain_l,
        "stemAttackTimesTransient": stem_attack * transient_a,
        "stemFluxTimesTransient": stem_flux * transient_f,
        "stemPeakTimingTimesTransient": stem_timing * transient_f,
        "dualStemTransient": 0.5 * (stem_attack * transient_a + stem_flux * transient_f),
        "fluxAttackTransient": 0.5 * (transient_a + transient_f),
    }


def contiguous_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    return min(folds - 1, int(folds * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / folds
    pos = ((measure - lo) + width / 2.0) % span
    return min(folds - 1, int(pos / width))


def effect(rows: list[dict[str, Any]], name: str) -> float:
    true_vals = [float(r["interactionFeatures"][name]) for r in rows if str(r.get("label")) == "true"]
    false_vals = [float(r["interactionFeatures"][name]) for r in rows if str(r.get("label")) != "true"]
    if not true_vals or not false_vals:
        return 0.0
    all_vals = np.asarray(true_vals + false_vals, dtype=np.float64)
    sd = float(np.std(all_vals))
    if not math.isfinite(sd) or sd < 1e-9:
        return 0.0
    return (float(np.mean(true_vals)) - float(np.mean(false_vals))) / sd


def evaluate_feature(
    rows: list[dict[str, Any]],
    name: str,
    schemes: list[tuple[str, Callable[[int], int]]],
) -> dict[str, Any]:
    full = effect(rows, name)
    parts: list[dict[str, Any]] = []
    positive = 0
    negative = 0
    useful = 0
    for scheme_name, fold_fn in schemes:
        for fold in range(FOLDS):
            part = [r for r in rows if fold_fn(int(r["measure"])) == fold]
            e = effect(part, name)
            if e > 0:
                positive += 1
            elif e < 0:
                negative += 1
            if abs(e) >= 0.10:
                useful += 1
            parts.append({"scheme": scheme_name, "fold": fold, "effect": round(e, 4), "rows": len(part)})

    signed = positive + negative
    dominant = "positive" if positive >= negative else "negative"
    consistency = 100.0 * max(positive, negative) / signed if signed else 0.0
    stable = (
        signed >= 12
        and consistency >= 80.0
        and useful >= 8
        and abs(full) >= 0.15
    )
    return {
        "feature": name,
        "fullEffect": round(full, 4),
        "direction": dominant,
        "positiveFolds": positive,
        "negativeFolds": negative,
        "directionConsistencyPct": round(consistency, 2),
        "usefulFolds": useful,
        "stable": stable,
        "parts": parts,
    }


def main() -> None:
    before = sha256(richer.onset.prof.recall.CANDIDATE_PATH)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source_rows = list(payload.get("candidateSlots") or [])
    if not source_rows:
        raise RuntimeError("Richer onset-slot candidateSlots missing")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source profile not anchored to frozen 36.76 champion")

    # Important separation: derive every interaction from audio measurements first.
    # Labels already present in source_rows are not read by derive(). They are used only below for grading/stability.
    rows: list[dict[str, Any]] = []
    for row in source_rows:
        copy = dict(row)
        copy["interactionFeatures"] = derive(row)
        rows.append(copy)

    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi, FOLDS)),
        ("shiftedWindow", lambda m: shifted_fold(m, lo, hi, FOLDS)),
    ]

    results = [evaluate_feature(rows, name, schemes) for name in INTERACTIONS]
    results.sort(key=lambda r: (not bool(r["stable"]), -float(r["directionConsistencyPct"]), -abs(float(r["fullEffect"]))))
    stable = [r for r in results if r["stable"]]

    after = sha256(richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during transient interaction diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-onset-slot-transient-interaction-stability-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "candidateSlots": len(rows),
        "interactionFeatureCount": len(INTERACTIONS),
        "stableInteractionCount": len(stable),
        "stableInteractions": stable,
        "allInteractions": results,
        "validatedNewChampion": False,
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
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "profileType": output["profileType"],
        "candidateSha256": after,
        "stableInteractionCount": len(stable),
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 ONSET SLOT TRANSIENT INTERACTION STABILITY V1 COMPLETE")
    print("Candidate slots:", len(rows))
    print("Stable transient interactions:", len(stable))
    for result in stable:
        print("STABLE", {
            "feature": result["feature"],
            "fullEffect": result["fullEffect"],
            "direction": result["direction"],
            "consistencyPct": result["directionConsistencyPct"],
            "usefulFolds": result["usefulFolds"],
        })
    if not stable:
        print("No stable interaction features passed the diagnostic gate.")
        for result in results[:8]:
            print("TOP", {
                "feature": result["feature"],
                "fullEffect": result["fullEffect"],
                "direction": result["direction"],
                "consistencyPct": result["directionConsistencyPct"],
                "usefulFolds": result["usefulFolds"],
            })
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
