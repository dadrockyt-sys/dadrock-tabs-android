"""S0 Transcription Failure Attribution V1.

Diagnostic-only experiment. For each frozen S0 mixture and each guitar/bass role:

1. Run frozen Basic Pitch 0.4.0 defaults on the exact rendered ground-truth role
   component ("oracle audio probe").
2. Run the identical Basic Pitch configuration on the untouched raw BS-Roformer
   output for that role.
3. Compare note-onset event sets with exact MIDI and a fixed 50 ms onset tolerance.

This does NOT treat Basic Pitch output as musical ground truth. The clean-component
event set is an oracle-audio *transcriber baseline* used to isolate transcription
instability introduced by source separation.

No separator output is modified and no threshold/model search occurs.
"""
from __future__ import annotations

import argparse
import json
import math
import tempfile
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from pretrained_note_front_end_v1 import (
    BASIC_PITCH_VERSION,
    FRAME_THRESHOLD,
    MIN_NOTE_LENGTH_MS,
    ONSET_THRESHOLD,
    basic_pitch_model_identity,
    run_basic_pitch,
)
from score_note_onsets import score_note_onsets
from stem_bleed_cleanup_v1 import si_sdr

ONSET_TOLERANCE_SECONDS = 0.05
NEAR_ONSET_WINDOW_SECONDS = 0.15


def load(path: Path):
    x, fs = sf.read(path, always_2d=True, dtype="float32")
    return x, fs


def truth_stems(directory: Path):
    out = {}
    for p in sorted(directory.glob("*.wav")):
        if p.name.endswith("_mix.wav"):
            continue
        role = p.stem.split("_", 1)[1]
        x, fs = load(p)
        out.setdefault(role, []).append((x, fs, p.name))
    return out


def collapse_truth(truth, target, length, channels=2):
    exact = [v[0][:length] for k, rows in truth.items() if k == target for v in rows]
    if exact:
        return np.sum(np.stack(exact), axis=0).astype(np.float32)
    return np.zeros((length, channels), dtype=np.float32)


def to_events(notes, prefix):
    rows = []
    for i, n in enumerate(notes):
        if len(n) < 3:
            continue
        start, end, midi = float(n[0]), float(n[1]), int(n[2])
        if not (math.isfinite(start) and math.isfinite(end)) or end <= start:
            continue
        rows.append({
            "id": f"{prefix}:{i}",
            "midi": midi,
            "start": start,
            "end": end,
            "amplitude": float(n[3]) if len(n) > 3 and math.isfinite(float(n[3])) else None,
        })
    return rows


def write_probe(path: Path, audio: np.ndarray, fs: int):
    sf.write(path, np.asarray(audio, dtype=np.float32), fs, subtype="FLOAT")


def unmatched_ids(score):
    matched_pred = {m["predictionId"] for m in score["matches"]}
    matched_ref = {m["targetId"] for m in score["matches"]}
    return matched_pred, matched_ref


def classify_unmatched(predictions, references, score):
    matched_pred, matched_ref = unmatched_ids(score)
    fp = [x for x in predictions if x["id"] not in matched_pred]
    fn = [x for x in references if x["id"] not in matched_ref]

    octave_fp = 0
    near_pitch_fp = 0
    timing_only_fp = 0
    for p in fp:
        near = [r for r in references if abs(p["start"] - r["start"]) <= ONSET_TOLERANCE_SECONDS]
        if any(abs(p["midi"] - r["midi"]) >= 12 and abs(p["midi"] - r["midi"]) % 12 == 0 for r in near):
            octave_fp += 1
            continue
        if any(0 < abs(p["midi"] - r["midi"]) <= 2 for r in near):
            near_pitch_fp += 1
            continue
        same_pitch = [r for r in references if r["midi"] == p["midi"]]
        if same_pitch and min(abs(p["start"] - r["start"]) for r in same_pitch) <= NEAR_ONSET_WINDOW_SECONDS:
            timing_only_fp += 1

    octave_fn = 0
    near_pitch_fn = 0
    timing_only_fn = 0
    for r in fn:
        near = [p for p in predictions if abs(p["start"] - r["start"]) <= ONSET_TOLERANCE_SECONDS]
        if any(abs(p["midi"] - r["midi"]) >= 12 and abs(p["midi"] - r["midi"]) % 12 == 0 for p in near):
            octave_fn += 1
            continue
        if any(0 < abs(p["midi"] - r["midi"]) <= 2 for p in near):
            near_pitch_fn += 1
            continue
        same_pitch = [p for p in predictions if p["midi"] == r["midi"]]
        if same_pitch and min(abs(p["start"] - r["start"]) for p in same_pitch) <= NEAR_ONSET_WINDOW_SECONDS:
            timing_only_fn += 1

    return {
        "unmatchedSeparatedEventCount": len(fp),
        "unmatchedOracleEventCount": len(fn),
        "octaveRelatedSeparatedFalsePositiveCount": octave_fp,
        "nearPitchSeparatedFalsePositiveCount": near_pitch_fp,
        "timingOnlySeparatedFalsePositiveCount": timing_only_fp,
        "octaveRelatedOracleMissCount": octave_fn,
        "nearPitchOracleMissCount": near_pitch_fn,
        "timingOnlyOracleMissCount": timing_only_fn,
    }


def run_probe(audio: np.ndarray, fs: int, path: Path, prefix: str):
    write_probe(path, audio, fs)
    return to_events(run_basic_pitch(str(path)), prefix)


def micro_metrics(rows):
    tp = sum(r["eventAgreement"]["tp"] for r in rows)
    fp = sum(r["eventAgreement"]["fp"] for r in rows)
    fn = sum(r["eventAgreement"]["fn"] for r in rows)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else None
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s0-root", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--output-json", required=True)
    args = ap.parse_args()

    model_identity = basic_pitch_model_identity()
    if model_identity["packageVersion"] != BASIC_PITCH_VERSION:
        raise RuntimeError("Basic Pitch package version mismatch")
    if model_identity["modelSha256"] != "3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676":
        raise RuntimeError("Basic Pitch model SHA mismatch")

    adapter = BsRoformer6StemOnnxAdapter(Path(args.model))
    root = Path(args.s0_root)
    rows = []
    started = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="astra_s0_transcription_") as tmp:
        tmp = Path(tmp)
        for d in sorted(root.glob("S0M*")):
            mixes = list(d.glob("*_mix.wav"))
            if len(mixes) != 1:
                continue

            mix, fs = load(mixes[0])
            truth = truth_stems(d)
            raw = adapter.separate_array(mix, fs)
            length = len(mix)

            for target in ("guitar", "bass"):
                oracle_audio = collapse_truth(truth, target, length, mix.shape[1])
                oracle_energy = float(np.mean(oracle_audio.astype(np.float64) ** 2))
                separated_audio = raw[target][:length]
                separated_energy = float(np.mean(separated_audio.astype(np.float64) ** 2))
                target_present = oracle_energy > 1e-12

                safe = f"{d.name}_{target}"
                oracle_path = tmp / f"{safe}_oracle.wav"
                sep_path = tmp / f"{safe}_separated.wav"

                if target_present:
                    oracle_events = run_probe(oracle_audio, fs, oracle_path, f"{safe}:oracle")
                else:
                    oracle_events = []
                separated_events = run_probe(separated_audio, fs, sep_path, f"{safe}:sep")

                row = {
                    "id": d.name,
                    "target": target,
                    "targetPresent": target_present,
                    "oracleAudioEnergy": oracle_energy,
                    "separatedAudioEnergy": separated_energy,
                    "oracleEventCount": len(oracle_events),
                    "separatedEventCount": len(separated_events),
                }

                if target_present:
                    duration = length / float(fs)
                    agreement = score_note_onsets(
                        separated_events,
                        oracle_events,
                        start=0.0,
                        end=duration + 1e-9,
                        tolerance=ONSET_TOLERANCE_SECONDS,
                    )
                    row["rawSiSdrDb"] = float(si_sdr(oracle_audio, separated_audio))
                    row["eventAgreement"] = {
                        k: agreement[k]
                        for k in (
                            "predictions", "targets", "tp", "fp", "fn",
                            "precision", "recall", "f1",
                            "meanAbsoluteOnsetErrorSeconds",
                        )
                    }
                    row["failureAttribution"] = classify_unmatched(
                        separated_events, oracle_events, agreement
                    )
                else:
                    row["eventAgreement"] = None
                    row["failureAttribution"] = {
                        "absentTargetSeparatedFalseNoteCount": len(separated_events)
                    }

                rows.append(row)

    present = [r for r in rows if r["targetPresent"]]
    absent = [r for r in rows if not r["targetPresent"]]
    f1s = [r["eventAgreement"]["f1"] for r in present if r["eventAgreement"]["f1"] is not None]
    severe = [
        {"id": r["id"], "target": r["target"], "f1": r["eventAgreement"]["f1"], "rawSiSdrDb": r["rawSiSdrDb"]}
        for r in present
        if r["eventAgreement"]["f1"] is not None and r["eventAgreement"]["f1"] < 0.5
    ]

    result = {
        "schemaVersion": 1,
        "kind": "s0-transcription-failure-attribution-v1",
        "diagnosticOnly": True,
        "separatorOutputMutation": False,
        "thresholdSearch": False,
        "modelTraining": False,
        "separatorModelSha256": FP16_SHA256,
        "transcriber": {
            "name": "Basic Pitch",
            "packageVersion": BASIC_PITCH_VERSION,
            "modelSha256": model_identity["modelSha256"],
            "onsetThreshold": ONSET_THRESHOLD,
            "frameThreshold": FRAME_THRESHOLD,
            "minimumNoteLengthMs": MIN_NOTE_LENGTH_MS,
            "onsetAgreementToleranceSeconds": ONSET_TOLERANCE_SECONDS,
        },
        "mixtureCount": len({r["id"] for r in rows}),
        "roleProbeCount": len(rows),
        "targetPresentProbeCount": len(present),
        "targetAbsentProbeCount": len(absent),
        "presentTargetMicroAgreement": micro_metrics(present),
        "presentTargetMacroF1": float(np.mean(f1s)) if f1s else None,
        "presentTargetMinimumF1": float(np.min(f1s)) if f1s else None,
        "presentTargetMaximumF1": float(np.max(f1s)) if f1s else None,
        "severeAgreementFailureCountF1Below0_5": len(severe),
        "severeAgreementFailures": severe,
        "absentTargetTotalSeparatedFalseNoteCount": sum(
            r["separatedEventCount"] for r in absent
        ),
        "absentTargetProbesWithAnySeparatedFalseNotes": sum(
            r["separatedEventCount"] > 0 for r in absent
        ),
        "totalWallSeconds": time.perf_counter() - started,
        "results": rows,
        "interpretationBoundary": (
            "S0 synthetic mixtures only. Clean-component Basic Pitch events are not musical ground truth; "
            "they are a fixed oracle-audio transcriber baseline used only to measure separator-induced "
            "transcription instability. No separator output is modified and no production action is authorized."
        ),
    }

    Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
