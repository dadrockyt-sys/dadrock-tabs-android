"""Go My Way full-song three-role professional benchmark V2.

Existing-reference development benchmark, not a sealed holdout.

Inference is reference-blind:
- public/gomywayfullaitest.m4a decoded to 44.1 kHz stereo WAV
- untouched BS-Roformer-SW 6-stem FP16 ONNX
- frozen Basic Pitch 0.4.0 defaults on whole mix, raw guitar stem, raw bass stem

Scoring:
- frozen scorer-ready rhythm, lead and bass references across the 113-measure song
- exact MIDI + onset one-to-one matching at fixed 50 ms tolerance
- role-specific source uncertainty exclusions are honored
- guitar separator output is scored against rhythm and lead separately, plus their union
- bass separator output is scored against bass
- whole-mix controls are scored against each reference

No threshold search, no audio mutation, no reference-conditioned inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from evaluate_s0_transcription_failure_attribution_v1 import run_probe
from pretrained_note_front_end_v1 import (
    BASIC_PITCH_VERSION,
    FRAME_THRESHOLD,
    MIN_NOTE_LENGTH_MS,
    ONSET_THRESHOLD,
    basic_pitch_model_identity,
)

ONSET_TOLERANCE_SECONDS = 0.05
EXPECTED_BP_SHA256 = "3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676"
EXPECTED_SCORER_SHA256 = {
    "rhythm": "d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555",
    "bass": "39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1",
    "lead": "8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_audio(path: Path):
    x, fs = sf.read(path, always_2d=True, dtype="float32")
    if fs != 44100:
        raise RuntimeError(f"expected 44100 Hz decoded audio, got {fs}")
    if x.shape[1] != 2:
        raise RuntimeError(f"expected stereo audio, got {x.shape}")
    return x, fs


def boundaries_map(timing: dict) -> dict[int, dict]:
    rows = timing.get("measureBoundaries", [])
    out = {int(r["measureNumber"]): r for r in rows}
    if set(out) != set(range(1, 114)):
        raise RuntimeError("timing map must cover exactly measures 1..113")
    return out


def excluded_measures(reference: dict) -> set[int]:
    policy = reference.get("normalizationPolicy", {})
    out = set(int(x) for x in policy.get("excludedSourceMeasures", []))
    if policy.get("measure88Excluded") is True:
        out.add(88)
    return out


def validate_reference(role: str, path: Path) -> dict:
    actual = sha256_file(path)
    expected = EXPECTED_SCORER_SHA256[role]
    if actual != expected:
        raise RuntimeError(f"{role} scorer SHA mismatch: {actual}")
    d = json.loads(path.read_text())
    if d.get("part") != role:
        raise RuntimeError(f"{role} scorer part mismatch")
    if int(d.get("counts", {}).get("measures", -1)) != 113:
        raise RuntimeError(f"{role} scorer must declare 113 measures")
    if int(d.get("grid", {}).get("stepsPerMeasure", -1)) != 16:
        raise RuntimeError(f"{role} scorer grid mismatch")
    if d.get("normalizationPolicy", {}).get("generatedCandidateRead") is not False:
        raise RuntimeError(f"{role} scorer not reference-blind normalized")
    return d


def scorer_targets(role: str, ref: dict, timing: dict) -> tuple[list[dict], set[int]]:
    boundaries = boundaries_map(timing)
    excluded = excluded_measures(ref)
    targets = []
    for i, note in enumerate(ref.get("notes", [])):
        m = int(note["measure"])
        if m in excluded:
            raise RuntimeError(f"{role} scorer unexpectedly contains excluded measure {m}")
        step = float(note["step"])
        if not 0 <= step < 16:
            raise RuntimeError(f"{role} invalid step {step} in measure {m}")
        b = boundaries[m]
        start = float(b["startSeconds"]) + (step / 16.0) * float(b["durationSeconds"])
        targets.append({
            "id": f"{role}:{i}:m{m}:s{step}",
            "role": role,
            "midi": int(note["midi"]),
            "start": start,
            "measure": m,
            "step": step,
        })
    targets.sort(key=lambda x: (x["start"], x["midi"], x["id"]))
    return targets, excluded


def measure_for_time(t: float, timing: dict) -> int | None:
    # 113 rows only; simple deterministic linear scan is sufficient.
    for row in timing["measureBoundaries"]:
        start = float(row["startSeconds"])
        end = float(row["endSeconds"])
        if start <= t < end:
            return int(row["measureNumber"])
    return None


def filter_predictions(predictions: list[dict], timing: dict, excluded: set[int]) -> list[dict]:
    first = float(timing["measureBoundaries"][0]["startSeconds"])
    last = float(timing["measureBoundaries"][-1]["endSeconds"])
    out = []
    for p in predictions:
        t = float(p["start"])
        if t < first or t >= last:
            continue
        m = measure_for_time(t, timing)
        if m is None or m in excluded:
            continue
        q = dict(p)
        q["measure"] = m
        out.append(q)
    return out


def match_exact_midi_onset(predictions: list[dict], targets: list[dict]) -> dict:
    candidates = []
    for pi, p in enumerate(predictions):
        pm = int(p["midi"])
        ps = float(p["start"])
        for ti, t in enumerate(targets):
            if pm != int(t["midi"]):
                continue
            dt = abs(ps - float(t["start"]))
            if dt <= ONSET_TOLERANCE_SECONDS:
                candidates.append((dt, pi, ti))
    candidates.sort(key=lambda x: (x[0], x[1], x[2]))
    used_p = set()
    used_t = set()
    matches = []
    for dt, pi, ti in candidates:
        if pi in used_p or ti in used_t:
            continue
        used_p.add(pi)
        used_t.add(ti)
        matches.append({
            "predictionId": predictions[pi]["id"],
            "targetId": targets[ti]["id"],
            "midi": int(targets[ti]["midi"]),
            "predictionStart": float(predictions[pi]["start"]),
            "targetStart": float(targets[ti]["start"]),
            "absoluteOnsetErrorSeconds": float(dt),
            "measure": int(targets[ti]["measure"]),
        })

    tp = len(matches)
    fp = len(predictions) - tp
    fn = len(targets) - tp
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else None
    return {
        "predictions": len(predictions),
        "targets": len(targets),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "meanAbsoluteOnsetErrorSeconds": (
            float(np.mean([m["absoluteOnsetErrorSeconds"] for m in matches]))
            if matches else None
        ),
        "matches": matches,
    }


def score_role(predictions: list[dict], targets: list[dict], timing: dict, excluded: set[int]) -> dict:
    pp = filter_predictions(predictions, timing, excluded)
    return match_exact_midi_onset(pp, targets)


def compact_score(s: dict) -> dict:
    return {k: s[k] for k in (
        "predictions", "targets", "tp", "fp", "fn",
        "precision", "recall", "f1", "meanAbsoluteOnsetErrorSeconds",
    )}


def per_measure(predictions: list[dict], targets: list[dict], timing: dict, excluded: set[int]):
    filtered = filter_predictions(predictions, timing, excluded)
    rows = []
    for m in range(1, 114):
        if m in excluded:
            rows.append({"measure": m, "excluded": True, "score": None})
            continue
        pp = [x for x in filtered if int(x["measure"]) == m]
        tt = [x for x in targets if int(x["measure"]) == m]
        s = match_exact_midi_onset(pp, tt)
        rows.append({"measure": m, "excluded": False, "score": compact_score(s)})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio-source", required=True)
    ap.add_argument("--audio-wav", required=True)
    ap.add_argument("--timing-map", required=True)
    ap.add_argument("--rhythm-reference", required=True)
    ap.add_argument("--lead-reference", required=True)
    ap.add_argument("--bass-reference", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--output-json", required=True)
    args = ap.parse_args()

    audio_source = Path(args.audio_source)
    bp = basic_pitch_model_identity()
    if bp["packageVersion"] != BASIC_PITCH_VERSION or bp["modelSha256"] != EXPECTED_BP_SHA256:
        raise RuntimeError("Basic Pitch frozen identity mismatch")

    timing_path = Path(args.timing_map)
    timing = json.loads(timing_path.read_text())
    if timing.get("audioSource") != "public/gomywayfullaitest.m4a":
        raise RuntimeError("timing map audio binding mismatch")
    if int(timing.get("measureCount", -1)) != 113:
        raise RuntimeError("timing map measure count mismatch")

    refs = {
        "rhythm": validate_reference("rhythm", Path(args.rhythm_reference)),
        "lead": validate_reference("lead", Path(args.lead_reference)),
        "bass": validate_reference("bass", Path(args.bass_reference)),
    }
    targets = {}
    excluded = {}
    for role in ("rhythm", "lead", "bass"):
        targets[role], excluded[role] = scorer_targets(role, refs[role], timing)

    # Combined-guitar reference is the union of role-labeled note rows. If two parts
    # truly have the same MIDI/onset, they remain two targets; this preserves the
    # professional multi-part reference rather than collapsing it post hoc.
    combined_targets = sorted(
        targets["rhythm"] + targets["lead"],
        key=lambda x: (x["start"], x["midi"], x["id"]),
    )
    combined_excluded = excluded["rhythm"] | excluded["lead"]

    audio, fs = load_audio(Path(args.audio_wav))
    started = time.perf_counter()
    sep_started = time.perf_counter()
    adapter = BsRoformer6StemOnnxAdapter(Path(args.model))
    stems = adapter.separate_array(audio, fs)
    separator_seconds = time.perf_counter() - sep_started

    with tempfile.TemporaryDirectory(prefix="astra_gomyway_113_") as td:
        td = Path(td)
        bp_started = time.perf_counter()
        whole = run_probe(audio, fs, td / "whole.wav", "whole")
        guitar = run_probe(stems["guitar"], fs, td / "guitar.wav", "guitar")
        bass = run_probe(stems["bass"], fs, td / "bass.wav", "bass")
        bp_seconds = time.perf_counter() - bp_started

    scores = {
        "separator": {
            "rhythmFromGuitarStem": score_role(guitar, targets["rhythm"], timing, excluded["rhythm"]),
            "leadFromGuitarStem": score_role(guitar, targets["lead"], timing, excluded["lead"]),
            "combinedGuitarFromGuitarStem": score_role(guitar, combined_targets, timing, combined_excluded),
            "bassFromBassStem": score_role(bass, targets["bass"], timing, excluded["bass"]),
        },
        "wholeMixControls": {
            "rhythm": score_role(whole, targets["rhythm"], timing, excluded["rhythm"]),
            "lead": score_role(whole, targets["lead"], timing, excluded["lead"]),
            "combinedGuitar": score_role(whole, combined_targets, timing, combined_excluded),
            "bass": score_role(whole, targets["bass"], timing, excluded["bass"]),
        },
        "roleConfusionDiagnostics": {
            "bassStemAgainstRhythm": score_role(bass, targets["rhythm"], timing, excluded["rhythm"]),
            "bassStemAgainstLead": score_role(bass, targets["lead"], timing, excluded["lead"]),
            "guitarStemAgainstBass": score_role(guitar, targets["bass"], timing, excluded["bass"]),
        },
    }

    result = {
        "schemaVersion": 2,
        "kind": "gomyway-full-song-three-role-professional-benchmark-v2",
        "benchmarkClass": "existing-reference-development-not-holdout",
        "referenceBlindInference": True,
        "thresholdSearch": False,
        "separatorOutputMutation": False,
        "automaticCorrection": False,
        "mainModified": False,
        "audio": {
            "sourcePath": args.audio_source,
            "sourceSha256": sha256_file(audio_source),
            "decodedWavSha256": sha256_file(Path(args.audio_wav)),
            "sampleRate": fs,
            "channels": int(audio.shape[1]),
            "durationSeconds": len(audio) / float(fs),
        },
        "separator": {
            "name": "BS-Roformer-SW 6-stem FP16 ONNX",
            "modelSha256": FP16_SHA256,
            "seconds": separator_seconds,
        },
        "transcriber": {
            "name": "Basic Pitch",
            "packageVersion": BASIC_PITCH_VERSION,
            "modelSha256": bp["modelSha256"],
            "onsetThreshold": ONSET_THRESHOLD,
            "frameThreshold": FRAME_THRESHOLD,
            "minimumNoteLengthMs": MIN_NOTE_LENGTH_MS,
            "seconds": bp_seconds,
        },
        "scoring": {
            "exactMidiRequired": True,
            "onsetToleranceSeconds": ONSET_TOLERANCE_SECONDS,
            "gridStepsPerMeasure": 16,
            "timingMapPath": args.timing_map,
            "timingMapSha256": sha256_file(timing_path),
            "referenceHashes": {
                role: sha256_file(Path(getattr(args, f"{role}_reference")))
                for role in ("rhythm", "lead", "bass")
            },
            "targetCounts": {role: len(targets[role]) for role in ("rhythm", "lead", "bass")},
            "combinedGuitarTargetCount": len(combined_targets),
            "excludedMeasures": {
                role: sorted(excluded[role]) for role in ("rhythm", "lead", "bass")
            },
        },
        "scores": {
            group: {name: compact_score(s) for name, s in vals.items()}
            for group, vals in scores.items()
        },
        "perMeasure": {
            "rhythmFromGuitarStem": per_measure(guitar, targets["rhythm"], timing, excluded["rhythm"]),
            "leadFromGuitarStem": per_measure(guitar, targets["lead"], timing, excluded["lead"]),
            "bassFromBassStem": per_measure(bass, targets["bass"], timing, excluded["bass"]),
        },
        "runtimeSeconds": time.perf_counter() - started,
        "interpretationBoundary": (
            "Existing Go My Way development reference, not sealed holdout. "
            "References are used only after inference. Basic Pitch supplies MIDI/onset evidence only; "
            "this benchmark does not claim string/fret, duration, or technique accuracy."
        ),
    }

    Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "kind": result["kind"],
        "targetCounts": result["scoring"]["targetCounts"],
        "excludedMeasures": result["scoring"]["excludedMeasures"],
        "separatorScores": result["scores"]["separator"],
        "wholeMixControls": result["scores"]["wholeMixControls"],
        "roleConfusionDiagnostics": result["scores"]["roleConfusionDiagnostics"],
        "runtimeSeconds": result["runtimeSeconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
