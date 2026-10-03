"""Go My Way full-song current-pipeline professional benchmark V1.

Existing-reference development benchmark, not a sealed holdout.

Inference:
- main/public/gomywayfullaitest.m4a decoded to 44.1 kHz stereo WAV
- untouched BS-Roformer-SW 6-stem FP16 ONNX output
- frozen Basic Pitch 0.4.0 defaults on whole mix, raw guitar stem, raw bass stem

Scoring in V1:
- complete rhythm-guitar measures 1..113
- measures 1..16 expanded from analyzer/fixtures/gomyway_professional_intro_reference_v1.json
- measures 17..113 from public/gomyway-professional-rhythm-reference-17-113.json
- timing from public/gomyway-professional-timing-map-v2.json
- exact MIDI + onset one-to-one matching, fixed 50 ms tolerance

Bass/lead prediction streams are cached in the output but are not scored until their
full professional PDFs have machine-normalized note labels. No reference data is
available to separator or Basic Pitch inference.
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
from score_note_onsets import score_note_onsets

GUITAR_OPEN_MIDI = [64, 59, 55, 50, 45, 40]  # high E -> low E
ONSET_TOLERANCE_SECONDS = 0.05
EXPECTED_BP_SHA256 = "3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676"
EXPECTED_AUDIO_GIT_BLOB = "5e34fb55fbd011c55b56bc40cc5d062735b3fcd0"
EXPECTED_BASS_PDF_SHA256 = "18e6822394980d22a960a1bd4d923aaddf677f3341b8cc1a2dbb29ea1e8771d0"
EXPECTED_LEAD_PDF_SHA256 = "a11a2c04fdda73e667df16df99aedf9ae0a3ed7af85f62f3c1773b7784a97f56"


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
        raise RuntimeError(f"expected stereo decoded audio, got shape {x.shape}")
    return x, fs


def expand_intro_reference(intro: dict) -> list[dict]:
    base = intro["notes"]
    source_measures = intro.get("repeat", {}).get("sourceMeasures", [1, 2])
    target_starts = [1] + list(intro.get("repeat", {}).get("targetMeasureStarts", []))
    if source_measures != [1, 2] or target_starts != [1, 3, 5, 7, 9, 11, 13, 15]:
        raise RuntimeError("unexpected intro repeat contract")

    out = []
    for start in target_starts:
        for note in base:
            source_measure = int(note["measure"])
            measure = start + (source_measure - 1)
            if not 1 <= measure <= 16:
                raise RuntimeError("expanded intro measure out of range")
            string_index = int(note["stringIndex"])
            fret = int(note["fret"])
            midi = GUITAR_OPEN_MIDI[string_index] + fret
            out.append({
                "measure": measure,
                "step": float(note["step"]),
                "midi": midi,
                "stringIndex": string_index,
                "fret": fret,
                "technique": note.get("technique"),
                "source": "intro-fixture-expanded",
            })
    return out


def build_rhythm_reference(
    intro: dict,
    later: dict,
    timing: dict,
) -> tuple[list[dict], list[dict]]:
    boundaries = {int(x["measureNumber"]): x for x in timing["measureBoundaries"]}
    if set(boundaries) != set(range(1, 114)):
        raise RuntimeError("timing map must cover exactly measures 1..113")

    raw_notes = expand_intro_reference(intro)
    unpitched = []

    if int(later.get("measureStart", -1)) != 17 or int(later.get("measureEnd", -1)) != 113:
        raise RuntimeError("17-113 rhythm reference range mismatch")
    if int(later.get("humanApprovedMeasureCount", -1)) != 97:
        raise RuntimeError("17-113 rhythm reference is not fully human-approved")
    if later.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("professional reference scoring-only boundary missing")

    for measure in later["measures"]:
        m = int(measure["measureNumber"])
        for event_index, event in enumerate(measure.get("events", [])):
            step = float(event["quantizedStep"])
            for note_index, note in enumerate(event.get("notes", [])):
                string_one_based = int(note["string"])
                fret = int(note["fret"])
                common = {
                    "measure": m,
                    "step": step,
                    "stringIndex": string_one_based - 1,
                    "fret": fret,
                    "techniques": list(event.get("techniques", [])),
                    "eventIndex": event_index,
                    "noteIndex": note_index,
                    "source": "human-approved-17-113",
                }
                if fret < 0:
                    unpitched.append(common)
                    continue
                if not 1 <= string_one_based <= 6:
                    raise RuntimeError(f"invalid professional string {string_one_based}")
                common["midi"] = GUITAR_OPEN_MIDI[string_one_based - 1] + fret
                raw_notes.append(common)

    targets = []
    for index, row in enumerate(raw_notes):
        m = int(row["measure"])
        b = boundaries[m]
        measure_start = float(b["startSeconds"])
        measure_duration = float(b["durationSeconds"])
        # Professional references use a 16-step normalized grid even in the short
        # measure. The timing map carries the actual bar duration.
        onset = measure_start + (float(row["step"]) / 16.0) * measure_duration
        targets.append({
            "id": f"rhythm:{index}:m{m}:s{row['step']}",
            "midi": int(row["midi"]),
            "start": float(onset),
            "measure": m,
            "step": row["step"],
            "stringIndex": row["stringIndex"],
            "fret": row["fret"],
            "source": row["source"],
        })

    targets.sort(key=lambda x: (x["start"], x["midi"], x["id"]))
    return targets, unpitched


def score_window(predictions, targets, timing):
    start = float(timing["measureBoundaries"][0]["startSeconds"]) - 0.10
    end = float(timing["measureBoundaries"][-1]["endSeconds"]) + 0.10
    return score_note_onsets(
        predictions,
        targets,
        start=max(0.0, start),
        end=end,
        tolerance=ONSET_TOLERANCE_SECONDS,
    )


def per_measure_scores(predictions, targets, timing):
    rows = []
    for boundary in timing["measureBoundaries"]:
        m = int(boundary["measureNumber"])
        start = float(boundary["startSeconds"])
        end = float(boundary["endSeconds"])
        rr = [x for x in targets if x["measure"] == m]
        # Tight local window; score_note_onsets itself re-filters.
        pp = [
            x for x in predictions
            if start - ONSET_TOLERANCE_SECONDS <= float(x["start"]) < end + ONSET_TOLERANCE_SECONDS
        ]
        s = score_note_onsets(
            pp, rr,
            start=max(0.0, start - ONSET_TOLERANCE_SECONDS),
            end=end + ONSET_TOLERANCE_SECONDS,
            tolerance=ONSET_TOLERANCE_SECONDS,
        )
        rows.append({
            "measureNumber": m,
            "referenceTargetCount": len(rr),
            "score": {k: s[k] for k in (
                "predictions", "targets", "tp", "fp", "fn",
                "precision", "recall", "f1", "meanAbsoluteOnsetErrorSeconds",
            )},
        })
    return rows


def serializable_events(events):
    return [{
        "id": str(e["id"]),
        "midi": int(e["midi"]),
        "start": float(e["start"]),
        "end": float(e["end"]),
        "amplitude": None if e.get("amplitude") is None else float(e["amplitude"]),
    } for e in events]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio-wav", required=True)
    ap.add_argument("--audio-source-path", required=True)
    ap.add_argument("--intro-reference", required=True)
    ap.add_argument("--later-reference", required=True)
    ap.add_argument("--timing-map", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--bass-pdf", required=True)
    ap.add_argument("--lead-pdf", required=True)
    ap.add_argument("--output-json", required=True)
    args = ap.parse_args()

    audio_path = Path(args.audio_wav)
    intro_path = Path(args.intro_reference)
    later_path = Path(args.later_reference)
    timing_path = Path(args.timing_map)
    bass_pdf_path = Path(args.bass_pdf)
    lead_pdf_path = Path(args.lead_pdf)

    if sha256_file(bass_pdf_path) != EXPECTED_BASS_PDF_SHA256:
        raise RuntimeError("bass professional PDF SHA mismatch")
    if sha256_file(lead_pdf_path) != EXPECTED_LEAD_PDF_SHA256:
        raise RuntimeError("lead professional PDF SHA mismatch")

    intro = json.loads(intro_path.read_text())
    later = json.loads(later_path.read_text())
    timing = json.loads(timing_path.read_text())

    if timing.get("audioSource") != "public/gomywayfullaitest.m4a":
        raise RuntimeError("timing map is not bound to gomywayfullaitest.m4a")
    if int(timing.get("measureCount", -1)) != 113:
        raise RuntimeError("timing map does not cover 113 measures")

    bp = basic_pitch_model_identity()
    if bp["packageVersion"] != BASIC_PITCH_VERSION or bp["modelSha256"] != EXPECTED_BP_SHA256:
        raise RuntimeError("Basic Pitch frozen identity mismatch")

    audio, fs = load_audio(audio_path)
    duration = len(audio) / float(fs)
    rhythm_targets, unpitched = build_rhythm_reference(intro, later, timing)

    started = time.perf_counter()
    separator_started = time.perf_counter()
    adapter = BsRoformer6StemOnnxAdapter(Path(args.model))
    stems = adapter.separate_array(audio, fs)
    separator_seconds = time.perf_counter() - separator_started

    with tempfile.TemporaryDirectory(prefix="astra_gomyway_full_") as td:
        td = Path(td)
        bp_started = time.perf_counter()
        whole_events = run_probe(audio, fs, td / "whole.wav", "whole")
        guitar_events = run_probe(stems["guitar"], fs, td / "guitar.wav", "guitar")
        bass_events = run_probe(stems["bass"], fs, td / "bass.wav", "bass")
        basic_pitch_seconds = time.perf_counter() - bp_started

    whole_score = score_window(whole_events, rhythm_targets, timing)
    guitar_score = score_window(guitar_events, rhythm_targets, timing)
    per_measure = per_measure_scores(guitar_events, rhythm_targets, timing)

    scored = [r for r in per_measure if r["referenceTargetCount"] > 0]
    ranked = sorted(
        scored,
        key=lambda r: (
            -1 if r["score"]["f1"] is None else -float(r["score"]["f1"]),
            r["measureNumber"],
        )
    )

    result = {
        "schemaVersion": 1,
        "kind": "gomyway-full-song-current-pipeline-professional-benchmark-v1",
        "benchmarkClass": "existing-reference-development-not-holdout",
        "referenceBlindInference": True,
        "thresholdSearch": False,
        "separatorOutputMutation": False,
        "mainModified": False,
        "audio": {
            "sourcePath": args.audio_source_path,
            "decodedWavSha256": sha256_file(audio_path),
            "durationSeconds": duration,
            "sampleRate": fs,
            "channels": int(audio.shape[1]),
            "expectedMainGitBlob": EXPECTED_AUDIO_GIT_BLOB,
        },
        "professionalReferences": {
            "rhythm": {
                "coverage": [1, 113],
                "introFixturePath": str(intro_path),
                "introFixtureSha256": sha256_file(intro_path),
                "laterReferencePath": str(later_path),
                "laterReferenceSha256": sha256_file(later_path),
                "timingMapPath": str(timing_path),
                "timingMapSha256": sha256_file(timing_path),
                "pitchedTargetCount": len(rhythm_targets),
                "unpitchedDeadOrMutedNoteCount": len(unpitched),
                "scoredNow": True,
            },
            "bass": {
                "pdfPath": args.bass_pdf,
                "pdfSha256": EXPECTED_BASS_PDF_SHA256,
                "coverage": [1, 113],
                "scoredNow": False,
                "reason": "full professional PDF is authoritative but machine-normalized note labels are not yet committed",
            },
            "lead": {
                "pdfPath": args.lead_pdf,
                "pdfSha256": EXPECTED_LEAD_PDF_SHA256,
                "coverage": [1, 113],
                "scoredNow": False,
                "reason": "full professional PDF is authoritative but machine-normalized note labels are not yet committed",
            },
        },
        "separator": {
            "name": "BS-Roformer-SW 6-stem ONNX",
            "modelSha256": FP16_SHA256,
            "wallSeconds": separator_seconds,
        },
        "transcriber": {
            "name": "Basic Pitch",
            "packageVersion": BASIC_PITCH_VERSION,
            "modelSha256": bp["modelSha256"],
            "onsetThreshold": ONSET_THRESHOLD,
            "frameThreshold": FRAME_THRESHOLD,
            "minimumNoteLengthMs": MIN_NOTE_LENGTH_MS,
            "onsetToleranceSeconds": ONSET_TOLERANCE_SECONDS,
            "wallSecondsForThreeStreams": basic_pitch_seconds,
        },
        "predictionCounts": {
            "wholeMix": len(whole_events),
            "rawGuitarStem": len(guitar_events),
            "rawBassStem": len(bass_events),
        },
        "rhythmScore": {
            "wholeMixControl": {k: whole_score[k] for k in (
                "predictions", "targets", "tp", "fp", "fn",
                "precision", "recall", "f1", "meanAbsoluteOnsetErrorSeconds",
            )},
            "rawGuitarStem": {k: guitar_score[k] for k in (
                "predictions", "targets", "tp", "fp", "fn",
                "precision", "recall", "f1", "meanAbsoluteOnsetErrorSeconds",
            )},
            "f1DeltaRawGuitarVsWholeMix": (
                None if whole_score["f1"] is None or guitar_score["f1"] is None
                else float(guitar_score["f1"] - whole_score["f1"])
            ),
            "perMeasure": per_measure,
            "highestF1Measures": ranked[:12],
            "lowestF1Measures": list(reversed(ranked[-12:])),
        },
        "predictionCache": {
            "wholeMix": serializable_events(whole_events),
            "rawGuitarStem": serializable_events(guitar_events),
            "rawBassStem": serializable_events(bass_events),
        },
        "unscoredDimensions": [
            "string/fret identity for Basic Pitch predictions",
            "duration/sustain agreement",
            "techniques/articulations",
            "bass professional PDF note labels",
            "lead professional PDF note labels",
        ],
        "totalWallSeconds": time.perf_counter() - started,
        "interpretationBoundary": (
            "This is an existing-reference development benchmark. Professional references are scoring-only. "
            "Bass and lead inference is cached but not scored until their full PDFs are machine-normalized. "
            "No automatic trust threshold or production action is authorized."
        ),
    }

    Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "predictionCounts": result["predictionCounts"],
        "rhythmScore": result["rhythmScore"],
        "separatorWallSeconds": separator_seconds,
        "basicPitchWallSeconds": basic_pitch_seconds,
        "totalWallSeconds": result["totalWallSeconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
