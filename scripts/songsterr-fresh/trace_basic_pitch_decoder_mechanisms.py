#!/usr/bin/env python3

"""Replay Basic Pitch 0.4.0 note decoding and label decoder mechanism.

Consumes already-captured same-inference activation + decision-surface sidecars.
It does not invoke a model, change event inventory, score acceptance, or infer
customer duration. The replay must reproduce the adapted evidence note multiset
exactly or it fails closed.
"""

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from basic_pitch_activation_evidence import decode_and_verify_activation_sidecar
from basic_pitch_decision_surface_diagnostic import (
    DecisionSurfaceError,
    decode_and_verify_decision_surface,
)
from compare_basic_pitch_cross_run_evidence import (
    ComparisonError,
    canonical_json,
    make_test_evidence,
    validate_evidence,
)

CONTRACT = "songsterr-fresh-basic-pitch-decoder-mechanism-trace-v1"
EXPECTED_PACKAGE_VERSION = "0.4.0"
DEFAULT_ENERGY_TOL = 11
AUDIO_SAMPLE_RATE = 22050
FFT_HOP = 256


class DecoderTraceError(RuntimeError):
    pass


def _load(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(
                handle,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    DecoderTraceError(f"NONSTANDARD_JSON_CONSTANT:{value}")
                ),
            )
    except DecoderTraceError:
        raise
    except Exception as exc:
        raise DecoderTraceError(f"JSON_LOAD_FAILED:{path}") from exc


def _finite(value, label):
    if isinstance(value, bool):
        raise DecoderTraceError(f"{label}:FINITE_NUMBER_REQUIRED")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DecoderTraceError(f"{label}:FINITE_NUMBER_REQUIRED") from exc
    if not math.isfinite(number):
        raise DecoderTraceError(f"{label}:FINITE_NUMBER_REQUIRED")
    return number


def _strict_peak_indices(onsets, threshold):
    # Equivalent to scipy.signal.argrelmax(onsets, axis=0) with default order=1,
    # followed by >= onset_thresh, for non-edge frames.
    result = []
    for time_index in range(1, onsets.shape[0] - 1):
        row = onsets[time_index]
        mask = (
            (row > onsets[time_index - 1])
            & (row > onsets[time_index + 1])
            & (row >= threshold)
        )
        for freq_index in np.flatnonzero(mask):
            result.append((int(time_index), int(freq_index)))
    # np.where(...)[::-1] in Basic Pitch reverses row-major onset candidates.
    return list(reversed(result))


def _append_event(events, frames, start, end, freq_index, minimum_midi, mechanism):
    amplitude = float(np.mean(frames[start:end, freq_index]))
    events.append({
        "startFrame": int(start),
        "endFrame": int(end),
        "midi": int(minimum_midi + freq_index),
        "amplitude": amplitude,
        "mechanism": mechanism,
    })


def replay_decoder(effective_onsets, frames, *, minimum_midi, onset_threshold, frame_threshold, min_note_len, energy_tol=DEFAULT_ENERGY_TOL):
    onsets = np.asarray(effective_onsets, dtype=np.float32)
    note_frames = np.asarray(frames, dtype=np.float32)
    if onsets.ndim != 2 or note_frames.ndim != 2 or onsets.shape != note_frames.shape or onsets.size == 0:
        raise DecoderTraceError("REPLAY_MATRIX_SHAPE_MISMATCH")
    if not np.all(np.isfinite(onsets)) or not np.all(np.isfinite(note_frames)):
        raise DecoderTraceError("REPLAY_MATRIX_NONFINITE")

    n_frames, n_freqs = note_frames.shape
    remaining_energy = np.zeros(note_frames.shape, dtype=note_frames.dtype)
    remaining_energy[:, :] = note_frames[:, :]
    events = []

    for note_start_idx, freq_idx in _strict_peak_indices(onsets, onset_threshold):
        if note_start_idx >= n_frames - 1:
            continue
        i = note_start_idx + 1
        k = 0
        while i < n_frames - 1 and k < energy_tol:
            if remaining_energy[i, freq_idx] < frame_threshold:
                k += 1
            else:
                k = 0
            i += 1
        i -= k
        if i - note_start_idx <= min_note_len:
            continue
        remaining_energy[note_start_idx:i, freq_idx] = 0
        if freq_idx < n_freqs - 1:
            remaining_energy[note_start_idx:i, freq_idx + 1] = 0
        if freq_idx > 0:
            remaining_energy[note_start_idx:i, freq_idx - 1] = 0
        _append_event(
            events,
            note_frames,
            note_start_idx,
            i,
            freq_idx,
            minimum_midi,
            "threshold-onset-pass",
        )

    while float(np.max(remaining_energy)) > frame_threshold:
        i_mid, freq_idx = np.unravel_index(np.argmax(remaining_energy), remaining_energy.shape)
        i_mid = int(i_mid)
        freq_idx = int(freq_idx)
        remaining_energy[i_mid, freq_idx] = 0

        i = i_mid + 1
        k = 0
        while i < n_frames - 1 and k < energy_tol:
            if remaining_energy[i, freq_idx] < frame_threshold:
                k += 1
            else:
                k = 0
            remaining_energy[i, freq_idx] = 0
            if freq_idx < n_freqs - 1:
                remaining_energy[i, freq_idx + 1] = 0
            if freq_idx > 0:
                remaining_energy[i, freq_idx - 1] = 0
            i += 1
        i_end = i - 1 - k

        i = i_mid - 1
        k = 0
        while i > 0 and k < energy_tol:
            if remaining_energy[i, freq_idx] < frame_threshold:
                k += 1
            else:
                k = 0
            remaining_energy[i, freq_idx] = 0
            if freq_idx < n_freqs - 1:
                remaining_energy[i, freq_idx + 1] = 0
            if freq_idx > 0:
                remaining_energy[i, freq_idx - 1] = 0
            i -= 1
        i_start = i + 1 + k

        if i_start < 0 or i_end >= n_frames:
            raise DecoderTraceError("MELODIA_REPLAY_INDEX_INVALID")
        if i_end - i_start <= min_note_len:
            continue
        _append_event(
            events,
            note_frames,
            i_start,
            i_end,
            freq_idx,
            minimum_midi,
            "melodia-residual-pass",
        )

    return events


def _event_key(start_seconds, end_seconds, midi, amplitude):
    # Exact float values are expected because frame times and float32 activation
    # matrices are the same sidecar values that generated the original decoder output.
    return (
        float(start_seconds),
        float(end_seconds),
        int(midi),
        float(amplitude),
    )


def build_trace(evidence, activation, decision):
    try:
        validated = validate_evidence(evidence, "evidence")
        decoded_activation = decode_and_verify_activation_sidecar(activation, evidence=evidence)
        decoded_decision = decode_and_verify_decision_surface(
            decision,
            activation_payload=activation,
            evidence=evidence,
        )
    except (ComparisonError, DecisionSurfaceError, RuntimeError) as exc:
        raise DecoderTraceError(f"INPUT_INVALID_OR_UNBOUND:{exc}") from exc

    model = validated["model"]
    if model.get("packageVersion") != EXPECTED_PACKAGE_VERSION:
        raise DecoderTraceError("BASIC_PITCH_PACKAGE_VERSION_NOT_0_4_0")
    if decision.get("diagnostics", {}).get("melodiaTrick") is not True:
        raise DecoderTraceError("MELODIA_SETTING_CHANGED")
    if decision.get("effectiveOnsetMatrix", {}).get("inferOnsets") is not True:
        raise DecoderTraceError("INFER_ONSETS_SETTING_CHANGED")
    if int(decision.get("effectiveOnsetMatrix", {}).get("inferOnsetDiffCount", -1)) != 2:
        raise DecoderTraceError("INFER_ONSET_DIFF_COUNT_CHANGED")

    onset_threshold = _finite(model.get("onsetThreshold"), "model.onsetThreshold")
    frame_threshold = _finite(model.get("frameThreshold"), "model.frameThreshold")
    minimum_note_length_ms = _finite(model.get("minimumNoteLengthMs"), "model.minimumNoteLengthMs")
    min_note_len = int(np.round(minimum_note_length_ms / 1000.0 * (AUDIO_SAMPLE_RATE / FFT_HOP)))
    if min_note_len <= 0:
        raise DecoderTraceError("MIN_NOTE_LENGTH_FRAME_COUNT_INVALID")

    frame_times = np.asarray(decoded_activation["frameTimesSeconds"], dtype=np.float64)
    frames = np.asarray(decoded_activation["activations"], dtype=np.float32)
    effective_onsets = np.asarray(decoded_decision["effectiveOnsets"], dtype=np.float32)
    if len(frame_times) != frames.shape[0]:
        raise DecoderTraceError("FRAME_TIME_COUNT_MISMATCH")

    replayed = replay_decoder(
        effective_onsets,
        frames,
        minimum_midi=decoded_activation["minimumMidi"],
        onset_threshold=onset_threshold,
        frame_threshold=frame_threshold,
        min_note_len=min_note_len,
    )

    replay_multimap = defaultdict(list)
    for item in replayed:
        if item["endFrame"] >= len(frame_times):
            raise DecoderTraceError("REPLAY_END_FRAME_OUTSIDE_TIME_AXIS")
        key = _event_key(
            frame_times[item["startFrame"]],
            frame_times[item["endFrame"]],
            item["midi"],
            item["amplitude"],
        )
        replay_multimap[key].append(item)

    evidence_rows = []
    for onset in validated["onsets"]:
        key = _event_key(
            onset["sourceStart"],
            onset["diagnosticModelEndSeconds"],
            onset["selectedMidi"],
            onset["onsetConfidence"],
        )
        evidence_rows.append((key, onset))

    evidence_counts = Counter(key for key, _ in evidence_rows)
    replay_counts = Counter({key: len(items) for key, items in replay_multimap.items()})
    if evidence_counts != replay_counts:
        missing = list((evidence_counts - replay_counts).elements())[:10]
        extra = list((replay_counts - evidence_counts).elements())[:10]
        raise DecoderTraceError(
            "DECODER_REPLAY_DOES_NOT_EXACTLY_REPRODUCE_EVIDENCE:"
            + canonical_json({"missing": missing, "extra": extra})
        )

    traced = []
    mechanism_counts = Counter()
    for key, onset in sorted(evidence_rows, key=lambda row: (row[0][0], row[0][2], row[0][1], row[0][3])):
        item = replay_multimap[key].pop(0)
        mechanism_counts[item["mechanism"]] += 1
        traced.append({
            "sourceStart": onset["sourceStart"],
            "diagnosticModelEndSeconds": onset["diagnosticModelEndSeconds"],
            "selectedMidi": onset["selectedMidi"],
            "noteSpanMeanActivation": onset["onsetConfidence"],
            "nearestStructureSlot": onset["nearestStructureSlot"],
            "decoderStartFrame": item["startFrame"],
            "decoderEndFrame": item["endFrame"],
            "decoderMechanism": item["mechanism"],
        })

    return {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "measurementOnly": True,
        "sourceEvidenceSha256": validated["digestSha256"],
        "noteInferenceIdentity": validated["noteIdentity"],
        "activationEvidenceIdentity": validated["activationIdentity"],
        "decisionSurfaceIdentity": decision["decisionSurfaceIdentity"],
        "decoderContract": {
            "basicPitchPackageVersion": EXPECTED_PACKAGE_VERSION,
            "inferOnsets": True,
            "inferOnsetDiffCount": 2,
            "onsetThreshold": onset_threshold,
            "frameThreshold": frame_threshold,
            "minimumNoteLengthMs": minimum_note_length_ms,
            "minimumNoteLengthFrames": min_note_len,
            "melodiaTrick": True,
            "energyToleranceFrames": DEFAULT_ENERGY_TOL,
        },
        "eventCount": len(traced),
        "mechanismCounts": dict(sorted(mechanism_counts.items())),
        "events": traced,
        "hardGuards": {
            "decoderReplayExactlyReproducedEvidence": True,
            "modelInvokedByTracer": False,
            "changesDecodedEventInventory": False,
            "usedForAcceptance": False,
            "usedForDuration": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
        },
        "policyBoundary": {
            "status": "TRACED_BASIC_PITCH_DECODER_MECHANISMS",
            "thresholdsAppliedForAdmission": False,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
        },
    }


def _make_sidecars():
    # Synthetic matrices designed to exercise both passes.
    from basic_pitch_activation_evidence import build_activation_sidecar
    from basic_pitch_decision_surface_diagnostic import build_decision_surface_sidecar

    frame_count = 80
    full_bins = 88
    frames = np.zeros((frame_count, full_bins), dtype=np.float32)
    raw_onsets = np.zeros((frame_count, full_bins), dtype=np.float32)
    col40 = 40 - 21
    col64 = 64 - 21

    # Threshold-onset event, frames 10:25.
    raw_onsets[10, col40] = 0.9
    frames[10:25, col40] = 0.8
    # Melodia event with no thresholded onset peak, frames 40:56.
    # 0.4 stays above frameThreshold=0.3 while inferred onset scales to 0.45 < 0.5.
    frames[40:56, col64] = 0.4
    # Ensure inferred-onset scale is non-degenerate and remains subthreshold at MIDI64.
    raw_onsets[35, 52 - 21] = 0.8
    frames[35:39, 52 - 21] = [0.5, 0.4, 0.2, 0.1]

    # Build effective surface first so synthetic expected note inventory is generated
    # by the same replay function under test.
    note_identity_seed = {
        "contract": "songsterr-fresh-basic-pitch-note-identity-v1",
        "version": 1,
        "algorithm": "sha256",
        "canonicalization": "seed",
        "eventCount": 0,
        "sha256": hashlib.sha256(b"seed").hexdigest(),
    }
    # Temporary activation identity is replaced after replay-derived notes exist.
    frame_times = np.arange(frame_count, dtype=np.float64) * 0.01
    model = {
        "family": "Spotify Basic Pitch",
        "package": "basic-pitch",
        "packageVersion": "0.4.0",
        "polyphonic": True,
        "instrumentAgnostic": True,
        "minimumMidi": 40,
        "maximumMidi": 88,
        "onsetThreshold": 0.5,
        "frameThreshold": 0.3,
        "minimumNoteLengthMs": 127.7,
    }

    # Reconstruct effective onsets with helper using a provisional valid activation bundle.
    dummy_notes = [{"startSeconds": 0.1, "midi": 40, "confidence": 0.8}]
    provisional = build_activation_sidecar(
        model_note_matrix=frames,
        frame_times=frame_times,
        notes=dummy_notes,
        minimum_midi=40,
        maximum_midi=88,
        audio_source="fixture.m4a",
        separation_source="stem.wav",
        model_metadata=model,
    )
    provisional_decision = build_decision_surface_sidecar(
        model_onset_matrix=raw_onsets,
        model_note_matrix=frames,
        note_identity=provisional["noteInferenceIdentity"],
        activation_bundle_identity=provisional["inferenceBundleIdentity"],
        minimum_midi=40,
        maximum_midi=88,
        audio_source="fixture.m4a",
        separation_source="stem.wav",
        model_metadata=model,
    )
    effective = decode_and_verify_decision_surface(provisional_decision)["effectiveOnsets"]
    selected_frames = frames[:, 40 - 21 : 88 - 21 + 1]
    replay = replay_decoder(
        effective,
        selected_frames,
        minimum_midi=40,
        onset_threshold=0.5,
        frame_threshold=0.3,
        min_note_len=11,
    )
    notes = [
        {
            "startSeconds": float(frame_times[event["startFrame"]]),
            "midi": event["midi"],
            "confidence": event["amplitude"],
        }
        for event in replay
    ]
    activation = build_activation_sidecar(
        model_note_matrix=frames,
        frame_times=frame_times,
        notes=notes,
        minimum_midi=40,
        maximum_midi=88,
        audio_source="fixture.m4a",
        separation_source="stem.wav",
        model_metadata=model,
    )
    decision = build_decision_surface_sidecar(
        model_onset_matrix=raw_onsets,
        model_note_matrix=frames,
        note_identity=activation["noteInferenceIdentity"],
        activation_bundle_identity=activation["inferenceBundleIdentity"],
        minimum_midi=40,
        maximum_midi=88,
        audio_source="fixture.m4a",
        separation_source="stem.wav",
        model_metadata=model,
    )

    evidence_events = []
    for event in replay:
        start = float(frame_times[event["startFrame"]])
        end = float(frame_times[event["endFrame"]])
        evidence_events.append((start, start, event["midi"], event["amplitude"], end))
    evidence = make_test_evidence(evidence_events, audio_source="fixture.m4a")
    evidence["provenance"]["sourceSeparationSource"] = "stem.wav"
    evidence["capabilities"]["instrumentIsolation"] = "stem.wav"
    evidence["diagnostics"]["sourceSeparation"] = "stem.wav"
    for onset in evidence["onsets"]:
        onset["provenance"]["separationSource"] = "stem.wav"
    evidence["diagnostics"]["polyphonicInference"] = model
    evidence["diagnostics"]["noteInferenceIdentity"] = activation["noteInferenceIdentity"]
    evidence["provenance"]["noteInferenceIdentity"] = activation["noteInferenceIdentity"]
    evidence["diagnostics"]["activationEvidenceIdentity"] = activation["inferenceBundleIdentity"]
    evidence["provenance"]["activationEvidenceIdentity"] = activation["inferenceBundleIdentity"]
    evidence["diagnostics"]["onsetCount"] = len(evidence["onsets"])
    return evidence, activation, decision


def run_self_test():
    evidence, activation, decision = _make_sidecars()
    trace = build_trace(evidence, activation, decision)
    assert trace["eventCount"] == len(evidence["onsets"])
    assert trace["mechanismCounts"].get("threshold-onset-pass", 0) >= 1
    assert trace["mechanismCounts"].get("melodia-residual-pass", 0) >= 1
    assert trace["hardGuards"]["decoderReplayExactlyReproducedEvidence"] is True
    assert trace["hardGuards"]["modelInvokedByTracer"] is False
    assert trace["hardGuards"]["usedForAcceptance"] is False
    assert trace["policyBoundary"]["modelValidationComplete"] is False

    bad = json.loads(json.dumps(evidence))
    bad["onsets"][0]["onsetConfidence"] = min(1.0, bad["onsets"][0]["onsetConfidence"] + 0.01)
    bad["onsets"][0]["candidates"][0]["confidence"] = bad["onsets"][0]["onsetConfidence"]
    try:
        build_trace(bad, activation, decision)
    except DecoderTraceError:
        pass
    else:
        raise AssertionError("modified evidence must fail exact replay/binding")

    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "PASS",
        "thresholdPassExercised": True,
        "melodiaPassExercised": True,
        "exactEvidenceReplayRequired": True,
        "modelInvokedByTracer": False,
        "usedForAcceptance": False,
        "usedForDuration": False,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", nargs="?")
    parser.add_argument("activation", nargs="?")
    parser.add_argument("decision", nargs="?")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    if not args.evidence or not args.activation or not args.decision:
        raise DecoderTraceError("EVIDENCE_ACTIVATION_DECISION_REQUIRED")
    trace = build_trace(_load(args.evidence), _load(args.activation), _load(args.decision))
    text = json.dumps(trace, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    try:
        main()
    except DecoderTraceError as exc:
        print(f"DECODER_TRACE_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
