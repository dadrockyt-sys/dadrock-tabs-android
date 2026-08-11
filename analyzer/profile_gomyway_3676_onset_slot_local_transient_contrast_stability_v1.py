from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np

import profile_gomyway_3676_onset_slot_richer_audio_stability_v1 as richer

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-local-transient-contrast-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-local-transient-contrast-stability-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLDS = 5

FEATURES = [
    "localFluxShortContrast",
    "localFluxMediumContrast",
    "localAttackShortContrast",
    "localAttackMediumContrast",
    "localSustainLongDrop",
    "localSustainShortDrop",
    "localHighBandContrast",
    "localCrestContrast",
    "localStemAttackContrast",
    "localStemFluxContrast",
    "localStemTimingContrast",
    "localTransientContrast",
    "localDualStemTransientContrast",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fv(row: dict[str, Any], name: str) -> float:
    return float((row.get("features") or {}).get(name, 0.0))


def step_of(row: dict[str, Any]) -> int:
    return int(row.get("step", row.get("gridStep", 0)))


def robust_neighbor_mean(neighbors: list[dict[str, Any]], name: str) -> float:
    vals = [fv(r, name) for r in neighbors]
    return float(np.mean(vals)) if vals else 0.0


def derive_local(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Build local context without reading labels. Neighbors are nearby residual slots
    # in the same/adjacent measure, ranked by grid distance.
    by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_measure[int(r["measure"])].append(r)
    for arr in by_measure.values():
        arr.sort(key=step_of)

    out: list[dict[str, Any]] = []
    for row in rows:
        m = int(row["measure"])
        s = step_of(row)
        candidates: list[tuple[int, dict[str, Any]]] = []
        for mm in (m - 1, m, m + 1):
            for other in by_measure.get(mm, []):
                if other is row:
                    continue
                # Adjacent-measure penalty keeps same-measure neighbors preferred.
                d = abs(step_of(other) - s) + (16 if mm != m else 0)
                candidates.append((d, other))
        candidates.sort(key=lambda x: x[0])
        neighbors = [r for _, r in candidates[:4]]

        flux_s_local = robust_neighbor_mean(neighbors, "fluxShortMean")
        flux_m_local = robust_neighbor_mean(neighbors, "fluxMediumMean")
        attack_s_local = robust_neighbor_mean(neighbors, "attackShortMean")
        attack_m_local = robust_neighbor_mean(neighbors, "attackMediumMean")
        sustain_l_local = robust_neighbor_mean(neighbors, "sustainLongMean")
        sustain_s_local = robust_neighbor_mean(neighbors, "sustainShortMean")
        high_local = robust_neighbor_mean(neighbors, "highBandAttackMean")
        crest_local = robust_neighbor_mean(neighbors, "crestMean")
        stem_a_local = robust_neighbor_mean(neighbors, "stemAttackAgreement")
        stem_f_local = robust_neighbor_mean(neighbors, "stemFluxAgreement")
        stem_t_local = robust_neighbor_mean(neighbors, "stemPeakTimingAgreement")

        transient = 0.5 * ((fv(row, "attackShortMean") - fv(row, "sustainLongMean")) +
                           (fv(row, "fluxShortMean") - fv(row, "sustainLongMean")))
        local_transient = 0.5 * ((attack_s_local - sustain_l_local) +
                                 (flux_s_local - sustain_l_local))
        dual = 0.5 * (fv(row, "stemAttackAgreement") + fv(row, "stemFluxAgreement")) * transient
        local_dual = 0.5 * (stem_a_local + stem_f_local) * local_transient

        local = {
            "localFluxShortContrast": fv(row, "fluxShortMean") - flux_s_local,
            "localFluxMediumContrast": fv(row, "fluxMediumMean") - flux_m_local,
            "localAttackShortContrast": fv(row, "attackShortMean") - attack_s_local,
            "localAttackMediumContrast": fv(row, "attackMediumMean") - attack_m_local,
            "localSustainLongDrop": sustain_l_local - fv(row, "sustainLongMean"),
            "localSustainShortDrop": sustain_s_local - fv(row, "sustainShortMean"),
            "localHighBandContrast": fv(row, "highBandAttackMean") - high_local,
            "localCrestContrast": fv(row, "crestMean") - crest_local,
            "localStemAttackContrast": fv(row, "stemAttackAgreement") - stem_a_local,
            "localStemFluxContrast": fv(row, "stemFluxAgreement") - stem_f_local,
            "localStemTimingContrast": fv(row, "stemPeakTimingAgreement") - stem_t_local,
            "localTransientContrast": transient - local_transient,
            "localDualStemTransientContrast": dual - local_dual,
        }
        cp = dict(row)
        cp["localContrastFeatures"] = local
        out.append(cp)
    return out


def contiguous_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    return min(folds - 1, int(folds * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / folds
    pos = ((measure - lo) + width / 2.0) % span
    return min(folds - 1, int(pos / width))


def effect(rows: list[dict[str, Any]], name: str) -> float:
    tv = [float(r["localContrastFeatures"][name]) for r in rows if str(r.get("label")) == "true"]
    fv_ = [float(r["localContrastFeatures"][name]) for r in rows if str(r.get("label")) != "true"]
    if not tv or not fv_:
        return 0.0
    vals = np.asarray(tv + fv_, dtype=np.float64)
    sd = float(np.std(vals))
    if not math.isfinite(sd) or sd < 1e-9:
        return 0.0
    return (float(np.mean(tv)) - float(np.mean(fv_))) / sd


def evaluate(rows: list[dict[str, Any]], name: str, schemes: list[tuple[str, Callable[[int], int]]]) -> dict[str, Any]:
    full = effect(rows, name)
    positive = negative = useful = 0
    parts: list[dict[str, Any]] = []
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
    consistency = 100.0 * max(positive, negative) / signed if signed else 0.0
    stable = signed >= 12 and consistency >= 80.0 and useful >= 8 and abs(full) >= 0.15
    return {
        "feature": name,
        "fullEffect": round(full, 4),
        "direction": "positive" if positive >= negative else "negative",
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
    source = list(payload.get("candidateSlots") or [])
    if not source:
        raise RuntimeError("Richer onset-slot candidateSlots missing")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source profile not anchored to frozen 36.76 champion")

    # All local contrast measurements are derived before labels are read below.
    rows = derive_local(source)
    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi, FOLDS)),
        ("shiftedWindow", lambda m: shifted_fold(m, lo, hi, FOLDS)),
    ]

    results = [evaluate(rows, name, schemes) for name in FEATURES]
    results.sort(key=lambda r: (not bool(r["stable"]), -float(r["directionConsistencyPct"]), -abs(float(r["fullEffect"]))))
    stable = [r for r in results if r["stable"]]

    after = sha256(richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during local transient contrast diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-onset-slot-local-transient-contrast-stability-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "candidateSlots": len(rows),
        "featureCount": len(FEATURES),
        "stableFeatureCount": len(stable),
        "stableFeatures": stable,
        "allFeatures": results,
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
        "stableFeatureCount": len(stable),
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 ONSET SLOT LOCAL TRANSIENT CONTRAST STABILITY V1 COMPLETE")
    print("Candidate slots:", len(rows))
    print("Stable local-contrast features:", len(stable))
    for r in stable:
        print("STABLE", {"feature": r["feature"], "fullEffect": r["fullEffect"], "direction": r["direction"], "consistencyPct": r["directionConsistencyPct"], "usefulFolds": r["usefulFolds"]})
    if not stable:
        print("No stable local-contrast features passed the diagnostic gate.")
        for r in results[:8]:
            print("TOP", {"feature": r["feature"], "fullEffect": r["fullEffect"], "direction": r["direction"], "consistencyPct": r["directionConsistencyPct"], "usefulFolds": r["usefulFolds"]})
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
