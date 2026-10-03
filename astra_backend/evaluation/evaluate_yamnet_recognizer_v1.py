"""Zero-shot YAMNet guitar/bass recognition feasibility on frozen private fixtures.

This is an independent recognizer evaluation. It does not train YAMNet and does
not alter separator stems. It reports evidence scores first; threshold gating is
deliberately deferred until the evidence is reviewed.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import tensorflow_hub as hub

TARGET_SR = 16000

FIXTURES = {
    "freesound_community-clean-electric-guitar-loop-83895(1).mp3": ("G09", "guitar"),
    "freesound_community-electric-guitar-metal-riff-107087(1).mp3": ("G10", "guitar"),
    "freesound_community-electric-guitar-strumming-3-97679(1).mp3": ("G13", "guitar"),
    "freesound_community-electric-guitar-tapping-34546(1).mp3": ("G14", "guitar"),
    "shidenbeatsmusic-jingle-slide-guitar-22108(1).mp3": ("G21", "guitar"),
    "sunnyscy-guitar-riff-in-e-minor-95-bpm-dry-475013(1).mp3": ("G23", "guitar"),
    "freesound_community-electric-bass-guitar-loop-2-bpm-110-43631.mp3": ("B01", "bass"),
    "freesound_community-bass-guitar-death-metal-loop-240-bpm-101327.mp3": ("B06", "bass"),
    "freesound_community-picked_bassnote_a-100710.mp3": ("B12", "bass"),
    "idoberg-funk-rock-slap-bass-riff-em-106bpm-490940.mp3": ("B08", "bass"),
    "freesound_community-fretless-bass-open-d-bridge-pickup-100754.mp3": ("B20", "bass"),
    "freesound_community-bass60bpm-78680.mp3": ("B26", "bass"),
    "dragon-studio-atmospheric-drums-443147(1).mp3": ("N01", "other"),
    "freesound_community-speech-dramatic-female-38105(1).mp3": ("N04", "other"),
}

GUITAR_LABELS = {
    "Guitar",
    "Electric guitar",
    "Acoustic guitar",
    "Steel guitar, slide guitar",
    "Tapping (guitar technique)",
    "Strum",
}
BASS_LABELS = {"Bass guitar"}

def load_mono_16k(path: Path) -> np.ndarray:
    audio, sr = sf.read(path, always_2d=True, dtype="float32")
    mono = np.mean(audio, axis=1)
    if sr != TARGET_SR:
        from math import gcd
        g = gcd(sr, TARGET_SR)
        mono = resample_poly(mono, TARGET_SR // g, sr // g).astype(np.float32)
    return mono.astype(np.float32)

def class_names(model) -> list[str]:
    class_map_path = model.class_map_path().numpy().decode("utf-8")
    with open(class_map_path, newline="", encoding="utf-8") as f:
        return [row["display_name"] for row in csv.DictReader(f)]

def aggregate(scores: np.ndarray, indexes: list[int]) -> dict:
    selected = scores[:, indexes]
    return {
        "meanMaxClassScore": float(np.max(np.mean(selected, axis=0))),
        "framePeakScore": float(np.max(selected)),
        "meanCombinedScore": float(np.mean(np.max(selected, axis=1))),
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture-dir", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--hub-url", default="https://tfhub.dev/google/yamnet/1")
    args = ap.parse_args()

    model = hub.load(args.hub_url)
    names = class_names(model)
    name_to_idx = {name: i for i, name in enumerate(names)}
    missing = sorted((GUITAR_LABELS | BASS_LABELS) - set(name_to_idx))
    if missing:
        raise SystemExit(f"YAMNet class map missing required labels: {missing}")

    guitar_idx = [name_to_idx[n] for n in sorted(GUITAR_LABELS)]
    bass_idx = [name_to_idx[n] for n in sorted(BASS_LABELS)]
    rows = []

    for filename, (fixture_id, expected) in FIXTURES.items():
        path = Path(args.fixture_dir) / filename
        if not path.exists():
            raise SystemExit(f"missing fixture: {filename}")
        waveform = load_mono_16k(path)
        scores, _, _ = model(waveform)
        scores_np = scores.numpy()
        guitar = aggregate(scores_np, guitar_idx)
        bass = aggregate(scores_np, bass_idx)
        evidence_winner = "guitar" if guitar["meanMaxClassScore"] >= bass["meanMaxClassScore"] else "bass"
        margin = guitar["meanMaxClassScore"] - bass["meanMaxClassScore"]
        rows.append({
            "id": fixture_id,
            "filename": filename,
            "expected": expected,
            "durationSeconds": float(len(waveform) / TARGET_SR),
            "guitarEvidence": guitar,
            "bassEvidence": bass,
            "guitarMinusBassMeanScore": float(margin),
            "stringInstrumentEvidenceWinner": evidence_winner,
        })

    guitar_rows = [r for r in rows if r["expected"] == "guitar"]
    bass_rows = [r for r in rows if r["expected"] == "bass"]
    other_rows = [r for r in rows if r["expected"] == "other"]

    result = {
        "schemaVersion": 1,
        "kind": "yamnet-zero-shot-string-instrument-recognition-feasibility",
        "hubUrl": args.hub_url,
        "targetSampleRateHz": TARGET_SR,
        "guitarLabels": sorted(GUITAR_LABELS),
        "bassLabels": sorted(BASS_LABELS),
        "fixtureCount": len(rows),
        "summary": {
            "guitarFixtures": len(guitar_rows),
            "bassFixtures": len(bass_rows),
            "otherFixtures": len(other_rows),
            "guitarCorrectVsBassOnly": sum(r["stringInstrumentEvidenceWinner"] == "guitar" for r in guitar_rows),
            "bassCorrectVsGuitarOnly": sum(r["stringInstrumentEvidenceWinner"] == "bass" for r in bass_rows),
            "otherMeanGuitarEvidence": float(np.mean([r["guitarEvidence"]["meanMaxClassScore"] for r in other_rows])),
            "otherMeanBassEvidence": float(np.mean([r["bassEvidence"]["meanMaxClassScore"] for r in other_rows])),
        },
        "results": rows,
        "interpretationBoundary": (
            "Zero-shot feasibility only. 'Other' threshold is intentionally not frozen. "
            "Do not use this result as a cleanup gate until evidence is reviewed."
        ),
    }

    Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
