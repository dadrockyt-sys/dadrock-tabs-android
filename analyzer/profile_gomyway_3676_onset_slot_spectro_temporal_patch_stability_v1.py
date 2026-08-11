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
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLDS = 5

OFFSETS = (-0.090, -0.060, -0.030, 0.000, 0.030, 0.060, 0.120)
WINDOW_S = 0.028
BANDS = (
    (70.0, 220.0, "low"),
    (220.0, 500.0, "lowMid"),
    (500.0, 1200.0, "mid"),
    (1200.0, 2400.0, "highMid"),
    (2400.0, 4200.0, "high"),
)


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


def band_log_power(x: np.ndarray, sr: int, lo: float, hi: float) -> float:
    mag, freqs = richer.spectrum(x, sr)
    p = richer.band_power(mag, freqs, lo, hi)
    return math.log1p(max(0.0, p))


def stem_patch(audio: np.ndarray, sr: int, t: float) -> dict[str, float]:
    windows = [richer.extract(audio, sr, t + off, WINDOW_S) for off in OFFSETS]
    out: dict[str, float] = {}
    for bi, (lo, hi, name) in enumerate(BANDS):
        vals = [band_log_power(w, sr, lo, hi) for w in windows]
        for ti, v in enumerate(vals):
            out[f"{name}T{ti}"] = float(v)
        # Shape summaries derived from the patch itself.
        out[f"{name}Rise"] = float(vals[3] - vals[2])
        out[f"{name}Decay30"] = float(vals[3] - vals[4])
        out[f"{name}Decay60"] = float(vals[3] - vals[5])
        out[f"{name}PostSlope"] = float(vals[4] - vals[6])
        out[f"{name}Burst"] = float(vals[3] - 0.5 * (vals[2] + vals[4]))
    return out


def pair_patch(a: dict[str, float], b: dict[str, float]) -> dict[str, float]:
    out: dict[str, float] = {}
    for key in sorted(a):
        av = float(a[key])
        bv = float(b[key])
        out[f"mean::{key}"] = 0.5 * (av + bv)
        out[f"agree::{key}"] = 1.0 / (1.0 + abs(av - bv))
    return out


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
    consistency = 100.0 * max(pos, neg) / nonzero if nonzero else 0.0
    stable = nonzero >= 8 and consistency >= 80.0 and useful >= 6 and abs(full) >= 0.08
    return {
        "feature": feature,
        "fullEffect": round(full, 6),
        "dominantDirection": "positive" if pos >= neg else "negative",
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
    slots = list(source.get("candidateSlots") or [])
    if not slots:
        raise RuntimeError("Onset-slot source candidateSlots missing")
    if tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source profile not anchored to frozen 36.76 champion")

    payload = richer.onset.prof.v2.load_json(richer.onset.prof.recall.CANDIDATE_PATH)
    events = richer.onset.prof.v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = richer.onset.prof.v2.build_timing_grid(events)

    winner_audio, winner_sr = richer.onset.prof.harmonic.load_mono(richer.onset.prof.harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = richer.onset.prof.harmonic.load_mono(richer.onset.prof.harmonic.legacy.ALT_STEM)
    winner_audio = np.asarray(winner_audio)
    alt_audio = np.asarray(alt_audio)

    # Detection-side patch extraction is completed before labels are attached.
    measured: list[dict[str, Any]] = []
    total = len(slots)
    for idx, slot in enumerate(slots):
        measure = int(slot["measure"])
        step = int(slot["step"])
        t = float(grid.get((measure, step), 0.0))
        a = stem_patch(winner_audio, int(winner_sr), t)
        b = stem_patch(alt_audio, int(alt_sr), t)
        measured.append({"measure": measure, "step": step, "features": pair_patch(a, b)})
        if idx and idx % 150 == 0:
            print(f"heartbeat spectro-temporal patch {idx}/{total} ...", flush=True)

    rows = [
        {**m, "label": str(s.get("label"))}
        for m, s in zip(measured, slots)
    ]
    feature_names = sorted(rows[0]["features"].keys()) if rows else []
    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi)),
        ("shiftedWindow", lambda m: shifted_fold(m, lo, hi)),
    ]

    summaries = [summarize(rows, f, schemes) for f in feature_names]
    summaries.sort(key=lambda r: (not bool(r["stableDiagnostic"]), -float(r["directionConsistencyPct"]), -abs(float(r["fullEffect"]))))
    stable = [r for r in summaries if r["stableDiagnostic"]]

    after = sha256(richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during spectro-temporal patch diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-onset-slot-spectro-temporal-patch-stability-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "slotCount": len(rows),
        "featureCount": len(feature_names),
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

    print("GOMYWAY 36.76 ONSET SLOT SPECTRO TEMPORAL PATCH STABILITY V1 COMPLETE")
    print("Measured slots:", len(rows))
    print("Patch features:", len(feature_names))
    print("Stable patch features:", len(stable))
    for item in stable[:20]:
        print("STABLE", {
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
