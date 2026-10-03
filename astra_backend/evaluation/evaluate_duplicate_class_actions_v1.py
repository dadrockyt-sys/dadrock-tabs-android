"""Evaluate duplicate-class false-stem actions on frozen S0 mixtures.

Only pair states classified as duplicate_guitar_candidate or duplicate_bass_candidate
are modified. Other pair states are preserved untouched.

Actions:
- raw: separator output unchanged
- mute_false: zero the false claimed stem, leave companion unchanged
- merge_false_into_companion: add false stem waveform to companion, then zero false stem

This is S0-only development evidence.
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

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from stem_bleed_cleanup_v1 import si_sdr
from stem_bleed_diagnostics_v1 import DiagnosticConfig, diagnose_stems
from pair_consistency_classifier_v1 import PairClassifierConfig, classify_pair

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

def load(path):
    return sf.read(path, always_2d=True, dtype="float32")

def truth_stems(directory):
    out = {}
    for p in sorted(directory.glob("*.wav")):
        if p.name.endswith("_mix.wav"):
            continue
        out[p.stem.split("_", 1)[1]] = load(p)
    return out

def truth_presence(directory):
    return {
        p.stem.split("_", 1)[1]
        for p in directory.glob("*.wav")
        if not p.name.endswith("_mix.wav")
    }

def collapse_truth(truth, target, length):
    exact = [v[0][:length] for k, v in truth.items() if k == target]
    if exact:
        return np.sum(np.stack(exact), axis=0).astype(np.float32)
    sample = next(iter(truth.values()))[0]
    return np.zeros_like(sample[:length], dtype=np.float32)

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

def row_for_claim(mixture, claimed, raw, diagnostics, evidence_map, presence):
    strongest = max(
        (k for k in raw if k != claimed),
        key=lambda k: diagnostics[claimed]["perCompetitor"][k]["overlapPressure"],
    )
    return {
        "mixture": mixture,
        "claimedStem": claimed,
        "targetActuallyAbsent": claimed not in presence,
        "claimedStemEnergy": energy(raw[claimed]),
        "claimedEvidence": evidence_map[claimed],
        "strongestOverlapCompetitor": strongest,
    }

def reconstruction_error(mix, stems):
    n = len(mix)
    recon = np.zeros_like(mix[:n], dtype=np.float32)
    for x in stems.values():
        recon += x[:n]
    return float(np.max(np.abs(recon - mix[:n])))

def false_and_companion(pair_state):
    if pair_state == "duplicate_bass_candidate":
        return "guitar", "bass"
    if pair_state == "duplicate_guitar_candidate":
        return "bass", "guitar"
    raise ValueError(pair_state)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s0-root", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--hub-url", default="https://tfhub.dev/google/yamnet/1")
    args = ap.parse_args()

    sep = BsRoformer6StemOnnxAdapter(Path(args.model))
    yam = hub.load(args.hub_url)
    names = class_names(yam)
    diag_cfg = DiagnosticConfig()
    pair_cfg = PairClassifierConfig()
    results = []

    for directory in sorted(Path(args.s0_root).glob("S0M*")):
        mixes = list(directory.glob("*_mix.wav"))
        if len(mixes) != 1:
            continue

        mix, fs = load(mixes[0])
        truth = truth_stems(directory)
        presence = truth_presence(directory)
        raw = sep.separate_array(mix, fs)
        diagnostics = diagnose_stems(mix, raw, fs, diag_cfg)
        ev = {name: evidence(yam, names, wav, fs) for name, wav in raw.items()}

        guitar_row = row_for_claim(directory.name, "guitar", raw, diagnostics, ev, presence)
        bass_row = row_for_claim(directory.name, "bass", raw, diagnostics, ev, presence)
        pair = classify_pair(guitar_row, bass_row, pair_cfg)

        row = {"id": directory.name, "pairState": pair["state"], "actions": {}}

        if pair["state"] not in {"duplicate_guitar_candidate", "duplicate_bass_candidate"}:
            row["actions"]["raw"] = {
                "applied": False,
                "reason": "not_duplicate_candidate",
            }
            results.append(row)
            continue

        duplicate, companion = false_and_companion(pair["state"])
        length = len(mix)
        ref_comp = collapse_truth(truth, companion, length)
        raw_comp = si_sdr(ref_comp, raw[companion]) if companion in presence else None

        raw_err = reconstruction_error(mix, raw)

        mute = {k: v.copy() for k, v in raw.items()}
        mute[duplicate] = np.zeros_like(mute[duplicate])

        merge = {k: v.copy() for k, v in raw.items()}
        merge[companion] = (merge[companion] + merge[duplicate]).astype(np.float32)
        merge[duplicate] = np.zeros_like(merge[duplicate])

        row["duplicateStem"] = duplicate
        row["companionStem"] = companion
        row["duplicateActuallyAbsent"] = duplicate not in presence
        row["companionActuallyPresent"] = companion in presence

        row["actions"]["raw"] = {
            "companionSiSdrDb": raw_comp,
            "duplicateEnergy": energy(raw[duplicate]),
            "reconstructionMaxAbsError": raw_err,
        }
        row["actions"]["mute_false"] = {
            "companionSiSdrDb": si_sdr(ref_comp, mute[companion]) if companion in presence else None,
            "duplicateEnergy": energy(mute[duplicate]),
            "reconstructionMaxAbsError": reconstruction_error(mix, mute),
        }
        row["actions"]["merge_false_into_companion"] = {
            "companionSiSdrDb": si_sdr(ref_comp, merge[companion]) if companion in presence else None,
            "duplicateEnergy": energy(merge[duplicate]),
            "reconstructionMaxAbsError": reconstruction_error(mix, merge),
        }
        results.append(row)

    acted = [r for r in results if "duplicateStem" in r]
    result = {
        "schemaVersion": 1,
        "kind": "s0-duplicate-class-action-evaluation-v1",
        "modelSha256": FP16_SHA256,
        "pairClassifierConfig": pair_cfg.to_dict(),
        "mixtureCount": len(results),
        "duplicateCandidateCount": len(acted),
        "results": results,
        "interpretationBoundary": "Frozen S0 only. No production action authorized.",
    }

    Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
