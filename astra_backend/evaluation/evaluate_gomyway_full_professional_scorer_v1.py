"""Go My Way full-song professional scorer benchmark V1.

Reference-blind candidate generation:
  full-song audio -> BS-Roformer guitar/bass -> frozen Basic Pitch note events.

Only after candidate events are frozen in memory do we load the existing frozen
professional scorer-ready payload and timing map for retrospective scoring.

No candidate correction, threshold sweep, or reference-guided generation occurs.
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

STEP_TOLERANCE = 1


def load_audio(path: Path):
    return sf.read(path, always_2d=True, dtype="float32")


def write_audio(path: Path, audio: np.ndarray, fs: int):
    sf.write(path, np.asarray(audio, dtype=np.float32), fs, subtype="FLOAT")


def basic_pitch_events(path: Path):
    rows = []
    for i, n in enumerate(run_basic_pitch(str(path))):
        if len(n) < 3:
            continue
        start, end, midi = float(n[0]), float(n[1]), int(n[2])
        if not (math.isfinite(start) and math.isfinite(end)) or end <= start:
            continue
        rows.append({
            "id": i,
            "start": start,
            "end": end,
            "midi": midi,
            "amplitude": float(n[3]) if len(n) > 3 and math.isfinite(float(n[3])) else None,
        })
    return rows


def load_timing_map(path: Path):
    d = json.loads(path.read_text())
    bounds = d["measureBoundaries"]
    if len(bounds) != 113:
        raise RuntimeError(f"expected 113 timing-map measures, got {len(bounds)}")
    return d, bounds


def project_to_grid(events, bounds):
    projected = []
    for e in events:
        t = float(e["start"])
        match = None
        for b in bounds:
            if b["startSeconds"] <= t < b["endSeconds"]:
                match = b
                break
        if match is None:
            continue
        dur = float(match["endSeconds"]) - float(match["startSeconds"])
        frac = (t - float(match["startSeconds"])) / max(dur, 1e-12)
        step = int(round(frac * 16.0))
        step = max(0, min(15, step))
        projected.append({
            **e,
            "measure": int(match["measureNumber"]),
            "step": step,
        })
    return projected


def unique_rows(rows):
    seen = set()
    out = []
    for r in rows:
        key = (int(r["measure"]), int(r["midi"]), int(round(float(r["step"]))))
        if key in seen:
            continue
        seen.add(key)
        out.append({"measure": key[0], "midi": key[1], "step": key[2]})
    return out


def score(candidate, reference, step_tolerance=STEP_TOLERANCE):
    pairs = []
    for ci, c in enumerate(candidate):
        for ri, r in enumerate(reference):
            if int(c["measure"]) != int(r["measure"]):
                continue
            if int(c["midi"]) != int(r["midi"]):
                continue
            delta = abs(int(c["step"]) - int(round(float(r["step"]))))
            if delta <= step_tolerance:
                pairs.append((delta, ci, ri))
    used_c = set()
    used_r = set()
    matches = []
    for delta, ci, ri in sorted(pairs, key=lambda x: (x[0], x[1], x[2])):
        if ci in used_c or ri in used_r:
            continue
        used_c.add(ci)
        used_r.add(ri)
        matches.append((ci, ri, delta))

    tp = len(matches)
    fp = len(candidate) - tp
    fn = len(reference) - tp
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else None
    return {
        "candidateCount": len(candidate),
        "referenceCount": len(reference),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": p,
        "recall": r,
        "f1": f1,
        "meanAbsoluteStepError": float(np.mean([m[2] for m in matches])) if matches else None,
        "exactStepMatchFractionAmongMatches": (
            sum(m[2] == 0 for m in matches) / len(matches) if matches else None
        ),
    }


def recall_only(candidate, reference):
    s = score(candidate, reference)
    return {
        "referenceCount": s["referenceCount"],
        "matchedReferenceCount": s["tp"],
        "recall": s["recall"],
        "meanAbsoluteStepError": s["meanAbsoluteStepError"],
        "exactStepMatchFractionAmongMatches": s["exactStepMatchFractionAmongMatches"],
        "precisionIntentionallyNotReported": True,
        "reason": "candidate guitar stem contains both rhythm and lead roles",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--reference-payload", required=True)
    ap.add_argument("--timing-map", required=True)
    ap.add_argument("--output-json", required=True)
    args = ap.parse_args()

    identity = basic_pitch_model_identity()
    if identity["packageVersion"] != BASIC_PITCH_VERSION:
        raise RuntimeError("Basic Pitch version mismatch")
    if identity["modelSha256"] != "3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676":
        raise RuntimeError("Basic Pitch model SHA mismatch")

    audio_path = Path(args.audio)
    mix, fs = load_audio(audio_path)
    adapter = BsRoformer6StemOnnxAdapter(Path(args.model))
    started = time.perf_counter()

    # REFERENCE-BLIND CANDIDATE GENERATION. Do not load scorer references above this line.
    raw = adapter.separate_array(mix, fs)
    with tempfile.TemporaryDirectory(prefix="gomyway_prof_benchmark_") as td:
        td = Path(td)
        guitar_path = td / "guitar.wav"
        bass_path = td / "bass.wav"
        mix_path = td / "mix.wav"
        write_audio(guitar_path, raw["guitar"], fs)
        write_audio(bass_path, raw["bass"], fs)
        write_audio(mix_path, mix, fs)

        guitar_events = basic_pitch_events(guitar_path)
        bass_events = basic_pitch_events(bass_path)
        mix_events = basic_pitch_events(mix_path)

    candidate_generation_seconds = time.perf_counter() - started

    # Reference-facing scoring begins only here.
    timing, bounds = load_timing_map(Path(args.timing_map))
    refs = json.loads(Path(args.reference_payload).read_text())
    if refs["counts"] != {"bass": 547, "combinedGuitar": 1393, "lead": 447, "rhythm": 946}:
        raise RuntimeError(f"reference payload counts drifted: {refs['counts']}")

    guitar_grid = project_to_grid(guitar_events, bounds)
    bass_grid = project_to_grid(bass_events, bounds)
    mix_grid = project_to_grid(mix_events, bounds)

    rhythm_ref = unique_rows(refs["parts"]["rhythm"])
    lead_ref = unique_rows(refs["parts"]["lead"])
    bass_ref = unique_rows(refs["parts"]["bass"])
    combined_guitar_ref = unique_rows(rhythm_ref + lead_ref)
    full_instrument_ref = unique_rows(combined_guitar_ref + bass_ref)

    result = {
        "schemaVersion": 1,
        "kind": "gomyway-full-song-professional-scorer-benchmark-v1",
        "referenceBlindCandidateGeneration": True,
        "referenceGuidedCandidateModification": False,
        "thresholdSweep": False,
        "audioPath": str(audio_path),
        "separatorModelSha256": FP16_SHA256,
        "transcriber": {
            "name": "Basic Pitch",
            "packageVersion": BASIC_PITCH_VERSION,
            "modelSha256": identity["modelSha256"],
            "onsetThreshold": ONSET_THRESHOLD,
            "frameThreshold": FRAME_THRESHOLD,
            "minimumNoteLengthMs": MIN_NOTE_LENGTH_MS,
        },
        "timingMap": {
            "path": args.timing_map,
            "audioSource": timing.get("audioSource"),
            "measureCount": len(bounds),
            "resolvedTempoBpm": timing.get("alignment", {}).get("resolvedTempoBpm"),
            "resolvedFirstMeasureOffsetSeconds": timing.get("alignment", {}).get("resolvedFirstMeasureOffsetSeconds"),
        },
        "referencePayloadPath": args.reference_payload,
        "referenceCounts": {
            "rhythm": len(rhythm_ref),
            "lead": len(lead_ref),
            "bass": len(bass_ref),
            "combinedGuitarUnique": len(combined_guitar_ref),
            "fullInstrumentUnique": len(full_instrument_ref),
        },
        "candidateCounts": {
            "guitarBasicPitch": len(guitar_grid),
            "bassBasicPitch": len(bass_grid),
            "mixBasicPitch": len(mix_grid),
        },
        "scores": {
            "bassSeparatedVsBassReference": score(bass_grid, bass_ref),
            "guitarSeparatedVsCombinedGuitarReference": score(guitar_grid, combined_guitar_ref),
            "fullMixVsAllInstrumentReferences": score(mix_grid, full_instrument_ref),
            "rhythmReferenceCoverageByGuitarStem": recall_only(guitar_grid, rhythm_ref),
            "leadReferenceCoverageByGuitarStem": recall_only(guitar_grid, lead_ref),
        },
        "unscoredDimensions": {
            "stringAndFret": "Basic Pitch candidate does not emit string/fret identity",
            "technique": "Basic Pitch candidate does not emit bends/slides/hammer-ons/etc.",
            "duration": "not scored in V1; scorer-ready payload is pitch/onset rows",
            "separateRhythmPrecision": "not valid because separator emits one aggregate guitar stem",
            "separateLeadPrecision": "not valid because separator emits one aggregate guitar stem",
        },
        "candidateGenerationSeconds": candidate_generation_seconds,
        "interpretationBoundary": (
            "Existing Go My Way development benchmark, not a new sealed holdout. "
            "Professional references are loaded only after reference-blind candidate generation. "
            "V1 scores exact MIDI with +/-1 sixteenth-step onset tolerance on measures 1-113."
        ),
    }

    Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
