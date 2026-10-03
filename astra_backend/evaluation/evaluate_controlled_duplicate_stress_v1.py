"""Controlled duplicate-class stress evaluation V1.

Creates synthetic separator-output pairs from known isolated guitar/bass fixtures.
No separator inference is used. One real source waveform is deliberately split
across pseudo guitar and pseudo bass outputs at prospectively frozen amplitude
ratios, then the existing pair classifier is evaluated unchanged.

The purpose is to test whether duplicate-class consolidation generalizes in both
directions and where the current pair-energy gate stops detecting a split.
"""
from __future__ import annotations

import argparse
import csv
import json
from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
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
    ("bass", "B20", "freesound_community-fretless-bass-open-d-bridge-pickup-100754.mp3"),
    ("guitar", "G09", "freesound_community-clean-electric-guitar-loop-83895(1).mp3"),
    ("guitar", "G14", "freesound_community-electric-guitar-tapping-34546(1).mp3"),
    ("guitar", "G23", "sunnyscy-guitar-riff-in-e-minor-95-bpm-dry-475013(1).mp3"),
]

# Amplitude shares sum to 1.0. 30/70 is intentionally outside the current
# 6 dB pair-energy-gap gate; the others are intended positive cases.
SPLITS = [
    ("50_50", 0.50, 0.50),
    ("40_60", 0.40, 0.60),
    ("35_65", 0.35, 0.65),
    ("30_70", 0.30, 0.70),
]

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

def claim_row(name, claimed, stems, diagnostics, ev):
    strongest = max(
        (k for k in stems if k != claimed),
        key=lambda k: diagnostics[claimed]["perCompetitor"][k]["overlapPressure"],
    )
    return {
        "mixture": name,
        "claimedStem": claimed,
        "claimedStemEnergy": energy(stems[claimed]),
        "claimedEvidence": ev[claimed],
        "strongestOverlapCompetitor": strongest,
    }

def expected_state(source_class, label):
    if label == "30_70":
        return "ambiguous_pair"
    return f"duplicate_{source_class}_candidate"

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

        for split_label, guitar_share, bass_share in SPLITS:
            # Same source intentionally split across both claimed outputs.
            if source_class == "bass":
                false_claim = "guitar"
                companion = "bass"
            else:
                false_claim = "bass"
                companion = "guitar"

            stems = {
                "guitar": (source * guitar_share).astype(np.float32),
                "bass": (source * bass_share).astype(np.float32),
            }
            mixture = (stems["guitar"] + stems["bass"]).astype(np.float32)
            diagnostics = diagnose_stems(mixture, stems, fs, diag_cfg)
            ev = {k: evidence(yam, names, v, fs) for k, v in stems.items()}

            name = f"{source_id}_{split_label}"
            g = claim_row(name, "guitar", stems, diagnostics, ev)
            b = claim_row(name, "bass", stems, diagnostics, ev)
            pair = classify_pair(g, b, pair_cfg)

            merged = {
                companion: (stems[companion] + stems[false_claim]).astype(np.float32),
                false_claim: np.zeros_like(stems[false_claim]),
            }
            companion_raw = si_sdr(source, stems[companion])
            companion_merged = si_sdr(source, merged[companion])
            recon_error = float(np.max(np.abs(
                (merged["guitar"] + merged["bass"]) - mixture
            )))

            rows.append({
                "id": name,
                "sourceClass": source_class,
                "sourceId": source_id,
                "splitLabel": split_label,
                "guitarShare": guitar_share,
                "bassShare": bass_share,
                "expectedPairState": expected_state(source_class, split_label),
                "observedPairState": pair["state"],
                "pairCorrect": pair["state"] == expected_state(source_class, split_label),
                "guitarEvidence": ev["guitar"],
                "bassEvidence": ev["bass"],
                "energyGapDb": pair["energyGapDb"],
                "companionStem": companion,
                "falseClaimStem": false_claim,
                "rawCompanionSiSdrDb": companion_raw,
                "mergedCompanionSiSdrDb": companion_merged,
                "mergeImprovementDb": companion_merged - companion_raw,
                "mergeReconstructionMaxAbsError": recon_error,
            })

    positives = [r for r in rows if r["splitLabel"] != "30_70"]
    hard_negatives = [r for r in rows if r["splitLabel"] == "30_70"]
    result = {
        "schemaVersion": 1,
        "kind": "controlled-duplicate-class-stress-v1",
        "pairClassifierConfig": pair_cfg.to_dict(),
        "sourceCount": len(SOURCES),
        "caseCount": len(rows),
        "positiveCaseCount": len(positives),
        "hardNegativeCaseCount": len(hard_negatives),
        "positivePairAccuracy": sum(r["pairCorrect"] for r in positives) / len(positives),
        "hardNegativeAccuracy": sum(r["pairCorrect"] for r in hard_negatives) / len(hard_negatives),
        "meanMergeImprovementDb": float(np.mean([r["mergeImprovementDb"] for r in rows])),
        "minimumMergeImprovementDb": float(np.min([r["mergeImprovementDb"] for r in rows])),
        "minimumMergedSiSdrDb": float(np.min([r["mergedCompanionSiSdrDb"] for r in rows])),
        "maximumMergeReconstructionMaxAbsError": float(np.max([r["mergeReconstructionMaxAbsError"] for r in rows])),
        "results": rows,
        "interpretationBoundary": (
            "Controlled synthetic separator-output stress test only. "
            "No production or real-recording consolidation is authorized."
        ),
    }

    Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
