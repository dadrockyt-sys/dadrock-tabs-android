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
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-micro-temporal-shape-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-micro-temporal-shape-stability-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLDS = 5

OFFSETS = (-0.060, -0.030, 0.000, 0.030, 0.060, 0.120)
WINDOW_S = 0.020

FEATURES = [
    "rise30Mean",
    "rise60Mean",
    "decay30Mean",
    "decay60Mean",
    "decay120Mean",
    "attackSharpnessMean",
    "postDecaySlopeMean",
    "fluxIntoAttackMean",
    "fluxOut30Mean",
    "fluxAsymmetryMean",
    "highBandBurstMean",
    "rise30Agreement",
    "decay30Agreement",
    "decay60Agreement",
    "sharpnessAgreement",
    "fluxAsymmetryAgreement",
    "highBandBurstAgreement",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contiguous_fold(measure: int, lo: int, hi: int) -> int:
    span = max(1, hi - lo + 1)
    return min(FOLDS - 1, int(FOLDS * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / FOLDS
    pos = ((measure - lo) + width / 2.0) % span
    return min(FOLDS - 1, int(pos / width))


def log_rms(x: np.ndarray) -> float:
    return math.log(richer.rms(x) + 1e-9)


def high_band_share(x: np.ndarray, sr: int) -> float:
    mag, freqs = richer.spectrum(x, sr)
    total = float(np.sum(np.square(mag, dtype=np.float64))) + 1e-12
    high = richer.band_power(mag, freqs, 1200.0, 3500.0)
    return high / total


def stem_shape(audio: np.ndarray, sr: int, t: float) -> dict[str, float]:
    windows = [richer.extract(audio, sr, t + off, WINDOW_S) for off in OFFSETS]
    lr = [log_rms(x) for x in windows]
    hb = [high_band_share(x, sr) for x in windows]

    # Consecutive directional spectral-flux trajectory.
    flux = [richer.spectral_flux(windows[i], windows[i + 1], sr) for i in range(len(windows) - 1)]

    pre60, pre30, now, post30, post60, post120 = lr
    flux_into = flux[1]   # -30 ms -> 0 ms
    flux_out30 = flux[2]  # 0 ms -> +30 ms

    return {
        "rise30": now - pre30,
        "rise60": now - pre60,
        "decay30": now - post30,
        "decay60": now - post60,
        "decay120": now - post120,
        "attackSharpness": 2.0 * now - pre30 - post30,
        "postDecaySlope": post30 - post120,
        "fluxIntoAttack": flux_into,
        "fluxOut30": flux_out30,
        "fluxAsymmetry": flux_into - flux_out30,
        "highBandBurst": hb[2] - 0.5 * (hb[1] + hb[3]),
    }


def agreement(a: float, b: float) -> float:
    return 1.0 / (1.0 + abs(float(a) - float(b)))


def pair_shape(a: dict[str, float], b: dict[str, float]) -> dict[str, float]:
    def mean(name: str) -> float:
        return 0.5 * (float(a[name]) + float(b[name]))

    return {
        "rise30Mean": mean("rise30"),
        "rise60Mean": mean("rise60"),
        "decay30Mean": mean("decay30"),
        "decay60Mean": mean("decay60"),
        "decay120Mean": mean("decay120"),
        "attackSharpnessMean": mean("attackSharpness"),
        "postDecaySlopeMean": mean("postDecaySlope"),
        "fluxIntoAttackMean": mean("fluxIntoAttack"),
        "fluxOut30Mean": mean("fluxOut30"),
        "fluxAsymmetryMean": mean("fluxAsymmetry"),
        "highBandBurstMean": mean("highBandBurst"),
        "rise30Agreement": agreement(a["rise30"], b["rise30"]),
        "decay30Agreement": agreement(a["decay30"], b["decay30"]),
        "decay60Agreement": agreement(a["decay60"], b["decay60"]),
        "sharpnessAgreement": agreement(a["attackSharpness"], b["attackSharpness"]),
        "fluxAsymmetryAgreement": agreement(a["fluxAsymmetry"], b["fluxAsymmetry"]),
        "highBandBurstAgreement": agreement(a["highBandBurst"], b["highBandBurst"]),
    }


def effect(rows: list[dict[str, Any]], feature: str) -> float:
    tv = [float(r["features"][feature]) for r in rows if str(r.get("label")) == "true"]
    fv = [float(r["features"][feature]) for r in rows if str(r.get("label")) != "true"]
    if not tv or not fv:
        return 0.0
    vals = np.asarray(tv + fv, dtype=np.float64)
    sd = float(np.std(vals))
    if not math.isfinite(sd) or sd < 1e-9:
        return 0.0
    return (float(np.mean(tv)) - float(np.mean(fv))) / sd


def summarize(rows: list[dict[str, Any]], feature: str, schemes: list[tuple[str, Callable[[int], int]]]) -> dict[str, Any]:
    full = effect(rows, feature)
    parts: list[dict[str, Any]] = []
    pos = neg = nonzero = useful = 0
    for scheme_name, fold_fn in schemes:
        for fold in range(FOLDS):
            held = [r for r in rows if fold_fn(int(r["measure"])) == fold]
            e = effect(held, feature)
            if abs(e) >= 0.02:
                nonzero += 1
                pos += int(e > 0)
                neg += int(e < 0)
            if abs(e) >= 0.08:
                useful += 1
            parts.append({"scheme": scheme_name, "fold": fold, "effect": round(e, 6)})

    dominant = "positive" if pos >= neg else "negative"
    consistency = 100.0 * max(pos, neg) / nonzero if nonzero else 0.0
    stable = nonzero >= 8 and consistency >= 80.0 and useful >= 6 and abs(full) >= 0.08
    return {
        "feature": feature,
        "fullEffect": round(full, 6),
        "dominantDirection": dominant,
        "directionConsistencyPct": round(consistency, 2),
        "positiveFolds": pos,
        "negativeFolds": neg,
        "nonzeroFolds": nonzero,
        "usefulFolds": useful,
        "stableDiagnostic": stable,
        "foldEffects": parts,
    }


def main() -> None:
    before = sha256(richer.onset.prof.recall.CANDIDATE_PATH)
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source_slots = list(source.get("candidateSlots") or [])
    if not source_slots:
        raise RuntimeError("Onset-slot source candidateSlots missing")
    if tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source profile not anchored to frozen 36.76 champion")

    candidate_payload = richer.onset.prof.v2.load_json(richer.onset.prof.recall.CANDIDATE_PATH)
    events = richer.onset.prof.v2.candidate_rows(candidate_payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = richer.onset.prof.v2.build_timing_grid(events)

    winner_audio, winner_sr = richer.onset.prof.harmonic.load_mono(richer.onset.prof.harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = richer.onset.prof.harmonic.load_mono(richer.onset.prof.harmonic.legacy.ALT_STEM)
    winner_audio = np.asarray(winner_audio)
    alt_audio = np.asarray(alt_audio)

    # Detection-side micro-temporal measurements are completed before labels are attached.
    measured: list[dict[str, Any]] = []
    total = len(source_slots)
    for idx, slot in enumerate(source_slots):
        measure = int(slot["measure"])
        step = int(slot["step"])
        t = float(grid.get((measure, step), 0.0))
        a = stem_shape(winner_audio, int(winner_sr), t)
        b = stem_shape(alt_audio, int(alt_sr), t)
        measured.append({"measure": measure, "step": step, "features": pair_shape(a, b)})
        if idx and idx % 200 == 0:
            print(f"heartbeat micro-temporal measurement {idx}/{total} ...", flush=True)

    rows: list[dict[str, Any]] = []
    for measured_row, source_row in zip(measured, source_slots):
        rows.append({**measured_row, "label": str(source_row.get("label"))})

    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi)),
        ("shiftedWindow", lambda m: shifted_fold(m, lo, hi)),
    ]

    summaries = [summarize(rows, feature, schemes) for feature in FEATURES]
    summaries.sort(key=lambda r: (not bool(r["stableDiagnostic"]), -float(r["directionConsistencyPct"]), -abs(float(r["fullEffect"]))))
    stable = [r for r in summaries if r["stableDiagnostic"]]

    after = sha256(richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during micro-temporal shape diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-onset-slot-micro-temporal-shape-stability-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "slotCount": len(rows),
        "featureCount": len(FEATURES),
        "stableFeatureCount": len(stable),
        "stableFeatures": stable,
        "featureSummaries": summaries,
        "candidateSlots": rows,
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
        "candidateSha256": after,
        "stableFeatureCount": len(stable),
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 ONSET SLOT MICRO TEMPORAL SHAPE STABILITY V1 COMPLETE")
    print("Measured slots:", len(rows))
    print("Stable micro-temporal features:", len(stable))
    for item in stable:
        print("STABLE", {
            "feature": item["feature"],
            "fullEffect": item["fullEffect"],
            "direction": item["dominantDirection"],
            "consistencyPct": item["directionConsistencyPct"],
            "usefulFolds": item["usefulFolds"],
        })
    if not stable:
        print("No stable micro-temporal features passed the diagnostic gate.")
        for item in summaries[:8]:
            print("TOP", {
                "feature": item["feature"],
                "fullEffect": item["fullEffect"],
                "direction": item["dominantDirection"],
                "consistencyPct": item["directionConsistencyPct"],
                "usefulFolds": item["usefulFolds"],
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
