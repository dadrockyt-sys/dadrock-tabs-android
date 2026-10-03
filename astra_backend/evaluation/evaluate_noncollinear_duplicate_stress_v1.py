"""Non-collinear duplicate-class stress V1.

Uses known isolated guitar/bass fixtures, then creates two imperfect pseudo stems
that are not simple scalar copies of each other. The frozen PairClassifierConfig
V1 is evaluated unchanged. Consolidation quality is measured against the original
source using SI-SDR because these pseudo stems are no longer collinear copies.

No real recordings beyond the existing private fixture set are opened here.
"""
from __future__ import annotations

import argparse
import csv
import json
from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
import tensorflow_hub as hub

from pair_consistency_classifier_v1 import PairClassifierConfig, classify_pair
from stem_bleed_cleanup_v1 import si_sdr
from stem_bleed_diagnostics_v1 import DiagnosticConfig, diagnose_stems

TARGET_SR = 16000
GUITAR_LABELS = {
    "Guitar",
    "Electric guitar",
    "Acoustic guitar",
    "Steel guitar, slide guitar",
    "Tapping (guitar technique)",
    "Strum",
}
BASS_LABELS = {"Bass guitar"}

SOURCES = [
    ("bass", "B01", "freesound_community-electric-bass-guitar-loop-2-bpm-110-43631.mp3"),
    ("bass", "B08", "idoberg-funk-rock-slap-bass-riff-em-106bpm-490940.mp3"),
    ("guitar", "G09", "freesound_community-clean-electric-guitar-loop-83895(1).mp3"),
    ("guitar", "G14", "freesound_community-electric-guitar-tapping-34546(1).mp3"),
]

PERTURBATIONS = (
    "frequency_partition",
    "delayed_highband_leak",
    "time_varying_split",
    "filtered_plus_contamination",
)

def load(path: Path):
    return sf.read(path, always_2d=True, dtype="float32")

def class_names(model):
    path = model.class_map_path().numpy().decode("utf-8")
    with open(path, newline="", encoding="utf-8") as f:
        return [row["display_name"] for row in csv.DictReader(f)]

def mono16(x, fs):
    mono = np.mean(x, axis=1)
    if fs != TARGET_SR:
        g = gcd(fs, TARGET_SR)
        mono = resample_poly(mono, TARGET_SR // g, fs // g).astype(np.float32)
    return mono.astype(np.float32)

def evidence(model, names, x, fs):
    scores, _, _ = model(mono16(x, fs))
    arr = scores.numpy()
    idx = {n: i for i, n in enumerate(names)}
    gi = [idx[n] for n in GUITAR_LABELS]
    bi = [idx[n] for n in BASS_LABELS]
    return {
        "guitar": float(np.max(np.mean(arr[:, gi], axis=0))),
        "bass": float(np.max(np.mean(arr[:, bi], axis=0))),
    }

def energy(x):
    return float(np.mean(np.asarray(x, dtype=np.float64) ** 2))

def filt(x, fs, kind, cutoff):
    nyq = fs * 0.5
    if kind == "low":
        sos = butter(4, min(cutoff / nyq, 0.99), btype="lowpass", output="sos")
    else:
        sos = butter(4, max(cutoff / nyq, 1e-4), btype="highpass", output="sos")
    y = np.stack([sosfilt(sos, x[:, c]) for c in range(x.shape[1])], axis=1)
    return y.astype(np.float32)

def normalize_pair(a, b, source):
    merged = a + b
    denom = float(np.sqrt(np.mean(merged.astype(np.float64) ** 2)) + 1e-12)
    target = float(np.sqrt(np.mean(source.astype(np.float64) ** 2)) + 1e-12)
    scale = target / denom
    return (a * scale).astype(np.float32), (b * scale).astype(np.float32)

def make_split(source, fs, mode, source_class):
    cutoff = 220.0 if source_class == "bass" else 900.0
    lo = filt(source, fs, "low", cutoff)
    hi = filt(source, fs, "high", cutoff)

    if mode == "frequency_partition":
        a = 0.55 * lo + 0.15 * hi
        b = 0.15 * lo + 0.55 * hi

    elif mode == "delayed_highband_leak":
        delay = max(1, int(round(fs * 0.006)))
        hi_delayed = np.pad(hi, ((delay, 0), (0, 0)))[: len(hi)]
        a = 0.60 * lo + 0.18 * hi_delayed
        b = 0.12 * lo + 0.58 * hi

    elif mode == "time_varying_split":
        t = np.arange(len(source), dtype=np.float32) / fs
        env = (0.50 + 0.22 * np.sin(2 * np.pi * 0.7 * t))[:, None]
        a = env * source
        b = (1.0 - env) * source

    elif mode == "filtered_plus_contamination":
        contam = np.zeros_like(source)
        contam[1:] = 0.03 * source[:-1]
        a = 0.58 * lo + 0.12 * hi + contam
        b = 0.14 * lo + 0.58 * hi - 0.5 * contam

    else:
        raise ValueError(mode)

    return normalize_pair(a.astype(np.float32), b.astype(np.float32), source)

def claim_row(case_id, claimed, stems, diagnostics, ev):
    strongest = max(
        (k for k in stems if k != claimed),
        key=lambda k: diagnostics[claimed]["perCompetitor"][k]["overlapPressure"],
    )
    return {
        "mixture": case_id,
        "claimedStem": claimed,
        "claimedStemEnergy": energy(stems[claimed]),
        "claimedEvidence": ev[claimed],
        "strongestOverlapCompetitor": strongest,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture-dir", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--hub-url", default="https://tfhub.dev/google/yamnet/1")
    args = ap.parse_args()

    yam = hub.load(args.hub_url)
    names = class_names(yam)
    pair_cfg = PairClassifierConfig()
    diag_cfg = DiagnosticConfig()
    rows = []

    for source_class, source_id, filename in SOURCES:
        source, fs = load(Path(args.fixture_dir) / filename)

        for mode in PERTURBATIONS:
            part_a, part_b = make_split(source, fs, mode, source_class)

            if source_class == "bass":
                stems = {"guitar": part_a, "bass": part_b}
                false_claim, companion = "guitar", "bass"
                expected_state = "duplicate_bass_candidate"
            else:
                stems = {"guitar": part_b, "bass": part_a}
                false_claim, companion = "bass", "guitar"
                expected_state = "duplicate_guitar_candidate"

            mixture = stems["guitar"] + stems["bass"]
            diagnostics = diagnose_stems(mixture, stems, fs, diag_cfg)
            ev = {k: evidence(yam, names, v, fs) for k, v in stems.items()}
            g = claim_row(f"{source_id}_{mode}", "guitar", stems, diagnostics, ev)
            b = claim_row(f"{source_id}_{mode}", "bass", stems, diagnostics, ev)
            pair = classify_pair(g, b, pair_cfg)

            merged_companion = (stems[companion] + stems[false_claim]).astype(np.float32)
            raw_score = si_sdr(source, stems[companion])
            merged_score = si_sdr(source, merged_companion)
            recon_error = float(np.max(np.abs(merged_companion - mixture)))

            rows.append({
                "id": f"{source_id}_{mode}",
                "sourceClass": source_class,
                "sourceId": source_id,
                "perturbation": mode,
                "expectedPairState": expected_state,
                "observedPairState": pair["state"],
                "pairCorrect": pair["state"] == expected_state,
                "guitarEvidence": ev["guitar"],
                "bassEvidence": ev["bass"],
                "energyGapDb": pair["energyGapDb"],
                "falseClaimStem": false_claim,
                "companionStem": companion,
                "rawCompanionSiSdrDb": raw_score,
                "mergedCompanionSiSdrDb": merged_score,
                "mergeImprovementDb": merged_score - raw_score,
                "mergeReconstructionMaxAbsError": recon_error,
            })

    result = {
        "schemaVersion": 1,
        "kind": "non-collinear-duplicate-class-stress-v1",
        "pairClassifierConfig": pair_cfg.to_dict(),
        "sourceCount": len(SOURCES),
        "caseCount": len(rows),
        "pairAccuracy": sum(r["pairCorrect"] for r in rows) / len(rows),
        "meanMergeImprovementDb": float(np.mean([r["mergeImprovementDb"] for r in rows])),
        "minimumMergeImprovementDb": float(np.min([r["mergeImprovementDb"] for r in rows])),
        "maximumMergeImprovementDb": float(np.max([r["mergeImprovementDb"] for r in rows])),
        "minimumMergedSiSdrDb": float(np.min([r["mergedCompanionSiSdrDb"] for r in rows])),
        "maximumMergeReconstructionMaxAbsError": float(np.max([r["mergeReconstructionMaxAbsError"] for r in rows])),
        "results": rows,
        "interpretationBoundary": (
            "Controlled non-collinear synthetic separator-output stress only. "
            "Pair classifier is frozen and no production action is authorized."
        ),
    }

    Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
