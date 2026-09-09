#!/usr/bin/env python3

import argparse
import json
import math
from importlib.metadata import version as package_version
from pathlib import Path

from basic_pitch.inference import predict

CONTRACT = "songsterr-fresh-basic-pitch-isolated-guitar-v1"
DEFAULT_MIN_MIDI = 40
DEFAULT_MAX_MIDI = 88
SIMULTANEOUS_TOLERANCE_SECONDS = 0.01


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--audio-source", required=True)
    parser.add_argument("--separation-source", required=True)
    parser.add_argument("--minimum-midi", type=int, default=DEFAULT_MIN_MIDI)
    parser.add_argument("--maximum-midi", type=int, default=DEFAULT_MAX_MIDI)
    parser.add_argument("--onset-threshold", type=float, default=0.5)
    parser.add_argument("--frame-threshold", type=float, default=0.3)
    parser.add_argument("--minimum-note-length-ms", type=float, default=127.7)
    parser.add_argument("--gpu-invoked", action="store_true")
    return parser.parse_args()


def midi_to_hz(midi):
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def finite(value, label):
    number = float(value)
    if not math.isfinite(number):
        raise RuntimeError(f"BASIC_PITCH_NONFINITE_{label}")
    return number


def build_start_clusters(notes):
    clusters = []
    current = None
    for note in notes:
        start = float(note["startSeconds"])
        if current is None or start - current["anchorStart"] > SIMULTANEOUS_TOLERANCE_SECONDS:
            current = {
                "anchorStart": start,
                "noteIds": [],
                "midis": [],
            }
            clusters.append(current)
        current["noteIds"].append(note["noteId"])
        current["midis"].append(note["midi"])
    return clusters


def histogram(values):
    result = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return result


def main():
    args = parse_args()
    if args.minimum_midi < 0 or args.maximum_midi > 127 or args.minimum_midi > args.maximum_midi:
        raise RuntimeError("BASIC_PITCH_INVALID_MIDI_RANGE")
    if not 0.0 <= args.onset_threshold <= 1.0:
        raise RuntimeError("BASIC_PITCH_INVALID_ONSET_THRESHOLD")
    if not 0.0 <= args.frame_threshold <= 1.0:
        raise RuntimeError("BASIC_PITCH_INVALID_FRAME_THRESHOLD")
    if args.minimum_note_length_ms <= 0:
        raise RuntimeError("BASIC_PITCH_INVALID_MINIMUM_NOTE_LENGTH")

    _, _, note_events = predict(
        args.input,
        onset_threshold=args.onset_threshold,
        frame_threshold=args.frame_threshold,
        minimum_note_length=args.minimum_note_length_ms,
        minimum_frequency=midi_to_hz(args.minimum_midi),
        maximum_frequency=midi_to_hz(args.maximum_midi),
        multiple_pitch_bends=False,
        melodia_trick=True,
    )

    normalized = []
    for index, event in enumerate(note_events):
        if len(event) < 4:
            raise RuntimeError("BASIC_PITCH_NOTE_EVENT_SHAPE_INVALID")
        start_seconds = finite(event[0], "START")
        diagnostic_end_seconds = finite(event[1], "END")
        midi = int(event[2])
        confidence = finite(event[3], "CONFIDENCE")
        pitch_bends = event[4] if len(event) > 4 else None
        if start_seconds < 0 or diagnostic_end_seconds <= start_seconds:
            raise RuntimeError("BASIC_PITCH_NOTE_TIME_INVALID")
        if midi < args.minimum_midi or midi > args.maximum_midi:
            raise RuntimeError("BASIC_PITCH_NOTE_OUTSIDE_REQUESTED_RANGE")
        if confidence < 0 or confidence > 1:
            raise RuntimeError("BASIC_PITCH_NOTE_CONFIDENCE_INVALID")
        normalized.append({
            "noteId": f"basic-pitch-note-{index:06d}",
            "startSeconds": start_seconds,
            # This is diagnostic model output only. It MUST NOT become durationSeconds/sourceEnd.
            "diagnosticModelEndSeconds": diagnostic_end_seconds,
            "midi": midi,
            "confidence": confidence,
            "pitchBendPointCount": len(pitch_bends) if pitch_bends else 0,
        })

    normalized.sort(key=lambda note: (note["startSeconds"], note["midi"], note["diagnosticModelEndSeconds"]))
    # Reissue deterministic IDs after sorting so identical model output gives identical JSON.
    for index, note in enumerate(normalized):
        note["noteId"] = f"basic-pitch-note-{index:06d}"

    clusters = build_start_clusters(normalized)
    polyphonic_clusters = [cluster for cluster in clusters if len(cluster["noteIds"]) > 1]
    max_cluster_size = max((len(cluster["noteIds"]) for cluster in clusters), default=0)

    payload = {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "role": "guitar",
        "model": {
            "family": "Spotify Basic Pitch",
            "package": "basic-pitch",
            "packageVersion": package_version("basic-pitch"),
            "polyphonic": True,
            "instrumentAgnostic": True,
            "minimumMidi": args.minimum_midi,
            "maximumMidi": args.maximum_midi,
            "onsetThreshold": args.onset_threshold,
            "frameThreshold": args.frame_threshold,
            "minimumNoteLengthMs": args.minimum_note_length_ms,
        },
        "notes": normalized,
        "diagnostics": {
            "noteCount": len(normalized),
            "simultaneousClusterToleranceSeconds": SIMULTANEOUS_TOLERANCE_SECONDS,
            "startClusterCount": len(clusters),
            "polyphonicStartClusterCount": len(polyphonic_clusters),
            "maxStartClusterSize": max_cluster_size,
            "midiHistogram": histogram(note["midi"] for note in normalized),
            "modelNoteEndsAreDiagnosticOnly": True,
            "modelNoteEndsUsedAsDuration": False,
        },
        "provenance": {
            "source": CONTRACT,
            "audioSource": args.audio_source,
            "separationSource": args.separation_source,
            "referenceBlind": True,
            "modelInvoked": True,
            "gpuInvoked": bool(args.gpu_invoked),
            "legacyV143ScorerImported": False,
            "professionalScorerUsed": False,
            "referenceTabUsed": False,
        },
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")

    print(json.dumps({
        "contract": CONTRACT,
        "model": payload["model"],
        "diagnostics": payload["diagnostics"],
        "provenance": payload["provenance"],
    }))


if __name__ == "__main__":
    main()
