#!/usr/bin/env python3

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

CONTRACT = "songsterr-fresh-v3-activation-spectral-rejection-context-v1"
NOTE_CONTRACT = "songsterr-fresh-isolated-polyphonic-note-evidence-v1"
V2_RELEASE_CONTRACT = "songsterr-fresh-cpu-spectral-release-evidence-v2"
REATTACK_REASON = "NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK"
CORROBORATED = "CORROBORATED"
INSUFFICIENT_SPECTRAL = "INSUFFICIENT_SPECTRAL_CORROBORATION"
HOP_LENGTH = 512


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Record fixed-rule activation-valley and selected-pitch CQT context for "
            "corroborated and insufficient-spectral-corroboration events without "
            "changing duration evidence or selecting thresholds."
        )
    )
    parser.add_argument("--input", help="isolated guitar stem")
    parser.add_argument("--evidence", help="v2 release evidence JSON")
    parser.add_argument("--activation-evidence", help="same-inference activation sidecar JSON")
    parser.add_argument("--output", help="output JSON")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test and not all((args.input, args.evidence, args.activation_evidence, args.output)):
        parser.error("--input, --evidence, --activation-evidence, and --output are required unless --self-test is used")
    return args


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def percentile(values, q):
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def stats(values):
    cleaned = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    if not cleaned:
        return {
            "count": 0,
            "minimum": None,
            "p10": None,
            "median": None,
            "mean": None,
            "p90": None,
            "maximum": None,
        }
    return {
        "count": len(cleaned),
        "minimum": min(cleaned),
        "p10": percentile(cleaned, 0.10),
        "median": percentile(cleaned, 0.50),
        "mean": sum(cleaned) / len(cleaned),
        "p90": percentile(cleaned, 0.90),
        "maximum": max(cleaned),
    }


def midi_histogram(rows):
    counts = Counter(int(row["midi"]) for row in rows)
    return {str(midi): count for midi, count in sorted(counts.items())}


def summarize_rows(rows):
    return {
        "count": len(rows),
        "midiHistogram": midi_histogram(rows),
        "onsetActivationPeak": stats([row.get("onsetActivationPeak") for row in rows]),
        "valleyActivationMean": stats([row.get("valleyActivationMean") for row in rows]),
        "activationDrop": stats([row.get("activationDrop") for row in rows]),
        "onsetSpectralDb": stats([row.get("onsetSpectralDb") for row in rows]),
        "valleySpectralDb": stats([row.get("valleySpectralDb") for row in rows]),
        "spectralDropDb": stats([row.get("spectralDropDb") for row in rows]),
        "observedSpanFromOnsetSeconds": stats([row.get("observedSpanFromOnsetSeconds") for row in rows]),
        "samePitchReattackGapSeconds": stats([row.get("samePitchReattackGapSeconds") for row in rows]),
        "valleyToReattackMarginSeconds": stats([row.get("valleyToReattackMarginSeconds") for row in rows]),
    }


def validate_evidence(evidence):
    require(evidence.get("contract") == NOTE_CONTRACT, "V3_SPECTRAL_CONTEXT_NOTE_CONTRACT_CHANGED")
    require(evidence.get("version") == 1, "V3_SPECTRAL_CONTEXT_NOTE_VERSION_CHANGED")
    require(evidence.get("referenceBlind") is True, "V3_SPECTRAL_CONTEXT_REFERENCE_BLIND_GUARD_CHANGED")
    require(evidence.get("structureFrozen") is True, "V3_SPECTRAL_CONTEXT_STRUCTURE_FROZEN_GUARD_CHANGED")

    provenance = evidence.get("provenance") or {}
    require(provenance.get("referenceBlind") is True, "V3_SPECTRAL_CONTEXT_PROVENANCE_REFERENCE_BLIND_CHANGED")
    require(provenance.get("structureFrozen") is True, "V3_SPECTRAL_CONTEXT_PROVENANCE_STRUCTURE_FROZEN_CHANGED")
    require(provenance.get("modelInvoked") is True, "V3_SPECTRAL_CONTEXT_REQUIRES_MODEL_NOTE_EVIDENCE")
    require(provenance.get("modelNoteEndsUsedAsDuration") is False, "V3_SPECTRAL_CONTEXT_MODEL_END_DURATION_GUARD_CHANGED")
    require(provenance.get("activationEvidenceSameInference") is True, "V3_SPECTRAL_CONTEXT_REQUIRES_SAME_INFERENCE_ACTIVATION")
    require(provenance.get("activationEvidenceActiveDurationAuthority") is False, "V3_SPECTRAL_CONTEXT_ACTIVATION_AUTHORITY_CHANGED")
    require(provenance.get("durationEvidenceSource") == V2_RELEASE_CONTRACT, "V3_SPECTRAL_CONTEXT_REQUIRES_V2_RELEASE_EVIDENCE")
    require(provenance.get("durationEvidenceModelInvoked") is False, "V3_SPECTRAL_CONTEXT_RELEASE_STAGE_MODEL_GUARD_CHANGED")

    release = (evidence.get("diagnostics") or {}).get("releaseEvidence") or {}
    require(release.get("contract") == V2_RELEASE_CONTRACT, "V3_SPECTRAL_CONTEXT_V2_RELEASE_CONTRACT_CHANGED")
    require(release.get("samePitchReattackIsCensorOnly") is True, "V3_SPECTRAL_CONTEXT_REATTACK_CENSOR_GUARD_CHANGED")
    require(release.get("nextOnsetUsedAsDuration") is False, "V3_SPECTRAL_CONTEXT_NEXT_ONSET_DURATION_GUARD_CHANGED")
    return release


def next_same_pitch(onsets, index, midi):
    for later in onsets[index + 1:]:
        if later.get("classification") != "unambiguous" or later.get("selectedMidi") is None:
            continue
        if int(later["selectedMidi"]) == midi:
            return float(later["sourceStart"])
    return None


def base_payload(*, evidence, input_path, evidence_path, activation_path, fixed_rule, identity):
    return {
        "contract": CONTRACT,
        "version": 1,
        "descriptiveOnly": True,
        "referenceBlind": True,
        "changesDuration": False,
        "changesPitchIdentity": False,
        "invokesModel": False,
        "readsDecodedModelNoteEnd": False,
        "usesDecodedModelNoteEndAsDuration": False,
        "usesNextOnsetAsDuration": False,
        "usesSamePitchReattackAsDuration": False,
        "proposesNewReleaseRule": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
        "ownsAcceptanceDecision": False,
        "fixedEvidenceRule": fixed_rule,
        "source": {
            "audioPath": str(input_path),
            "audioSha256": sha256_file(input_path),
            "evidencePath": str(evidence_path),
            "evidenceSha256": sha256_file(evidence_path),
            "activationEvidencePath": str(activation_path),
            "activationEvidenceSha256": sha256_file(activation_path),
            "structureIdentity": evidence.get("structureIdentity"),
            "noteInferenceIdentity": identity.get("noteInferenceIdentity"),
            "inferenceBundleIdentity": identity.get("inferenceBundleIdentity"),
        },
        "hardGuards": {
            "inputEventMutation": False,
            "durationWrite": False,
            "sourceEndWrite": False,
            "pitchIdentityWrite": False,
            "modelInferenceByProbe": False,
            "decodedModelEndRead": False,
            "nextOnsetDuration": False,
            "samePitchReattackDuration": False,
            "newThresholdSelection": False,
            "acceptanceDecision": False,
        },
    }


def run_probe(input_path, evidence_path, activation_path):
    # Heavy dependencies and project modules are intentionally lazy-loaded so the
    # contract self-test stays model/dependency-free.
    import librosa
    import numpy as np
    import soundfile as sf

    script_dir = str(Path(__file__).resolve().parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    from activation_valley_release_evidence import (
        MIN_DURATION_SECONDS,
        first_activation_valley,
        fixed_rule_manifest,
        spectral_corroboration,
    )
    from basic_pitch_activation_evidence import decode_and_verify_activation_sidecar

    evidence = load_json(evidence_path)
    release = validate_evidence(evidence)
    sidecar = load_json(activation_path)
    decoded = decode_and_verify_activation_sidecar(sidecar, evidence=evidence)
    activations = np.asarray(decoded["activations"], dtype=np.float32)
    frame_times = np.asarray(decoded["frameTimesSeconds"], dtype=np.float64)
    minimum_midi = int(decoded["minimumMidi"])
    maximum_midi = int(decoded["maximumMidi"])

    y, sr = sf.read(input_path, always_2d=False)
    if y.ndim != 1:
        y = np.mean(y, axis=1)
    y = np.asarray(y, dtype=np.float32)
    harmonic = librosa.effects.harmonic(y, margin=2.0)
    cqt = np.abs(librosa.cqt(
        harmonic,
        sr=sr,
        hop_length=HOP_LENGTH,
        fmin=librosa.midi_to_hz(40),
        n_bins=49,
        bins_per_octave=12,
    ))
    cqt_db = librosa.amplitude_to_db(cqt, ref=np.max, top_db=80.0)

    rows = []
    pre_spectral_rejections = Counter()
    examined = 0
    activation_qualified = 0
    onsets = evidence.get("onsets") or []
    for index, onset in enumerate(onsets):
        duration_evidence = (onset.get("provenance") or {}).get("durationEvidence") or {}
        if duration_evidence.get("reason") != REATTACK_REASON:
            continue
        midi = int(onset["selectedMidi"])
        reattack = next_same_pitch(onsets, index, midi)
        if reattack is None:
            pre_spectral_rejections["MISSING_SAME_PITCH_REATTACK"] += 1
            continue
        pitch_index = midi - minimum_midi
        if midi > maximum_midi or pitch_index < 0 or pitch_index >= activations.shape[1]:
            pre_spectral_rejections["MIDI_OUTSIDE_ACTIVATION_MATRIX"] += 1
            continue
        examined += 1

        valley, reason = first_activation_valley(
            activations[:, pitch_index],
            frame_times,
            float(onset["sourceStart"]),
            float(reattack),
        )
        if valley is None:
            pre_spectral_rejections[reason] += 1
            continue

        activation_qualified += 1
        corroboration = spectral_corroboration(
            cqt_db,
            bin_index=midi - 40,
            source_start=float(onset["sourceStart"]),
            valley_time=float(valley["timeSeconds"]),
            sr=sr,
            hop_length=HOP_LENGTH,
        )
        observed_span = float(valley["timeSeconds"] - float(onset["sourceStart"]))
        require(observed_span >= MIN_DURATION_SECONDS, f"V3_SPECTRAL_CONTEXT_VALLEY_BEFORE_MIN_SPAN:{onset.get('onsetId')}")
        require(float(valley["timeSeconds"]) < float(reattack), f"V3_SPECTRAL_CONTEXT_VALLEY_NOT_BEFORE_REATTACK:{onset.get('onsetId')}")
        category = CORROBORATED if corroboration.get("passed") is True else INSUFFICIENT_SPECTRAL
        rows.append({
            "onsetId": onset.get("onsetId"),
            "midi": midi,
            "sourceStartSeconds": float(onset["sourceStart"]),
            "samePitchReattackSeconds": float(reattack),
            "samePitchReattackGapSeconds": float(reattack - float(onset["sourceStart"])),
            "observedValleySeconds": float(valley["timeSeconds"]),
            "observedSpanFromOnsetSeconds": observed_span,
            "valleyToReattackMarginSeconds": float(reattack - float(valley["timeSeconds"])),
            "onsetActivationPeak": float(valley["onsetActivationPeak"]),
            "valleyActivationMean": float(valley["valleyActivationMean"]),
            "activationDrop": float(valley["activationDrop"]),
            "onsetSpectralDb": float(corroboration["onsetSpectralDb"]),
            "valleySpectralDb": float(corroboration["valleySpectralDb"]),
            "spectralDropDb": float(corroboration["spectralDropDb"]),
            "spectralCorroborationPassed": bool(corroboration["passed"]),
            "category": category,
        })

    grouped = defaultdict(list)
    for row in rows:
        grouped[row["category"]].append(row)

    expected_reattack = int((release.get("unresolvedReasonCounts") or {}).get(REATTACK_REASON, -1))
    require(expected_reattack == examined, f"V3_SPECTRAL_CONTEXT_REATTACK_EXAMINED_COUNT_MISMATCH:{examined}:{expected_reattack}")
    require(activation_qualified == len(rows), "V3_SPECTRAL_CONTEXT_ACTIVATION_QUALIFIED_ACCOUNTING_MISMATCH")

    identity = {
        "noteInferenceIdentity": decoded.get("noteInferenceIdentity"),
        "inferenceBundleIdentity": decoded.get("inferenceBundleIdentity"),
    }
    payload = base_payload(
        evidence=evidence,
        input_path=input_path,
        evidence_path=evidence_path,
        activation_path=activation_path,
        fixed_rule=fixed_rule_manifest(),
        identity=identity,
    )
    payload.update({
        "diagnostics": {
            "reattackCensoredExaminedCount": examined,
            "activationQualifiedCount": activation_qualified,
            "preSpectralRejectionReasonCounts": dict(sorted(pre_spectral_rejections.items())),
            "spectralOutcomeCounts": {
                CORROBORATED: len(grouped.get(CORROBORATED, [])),
                INSUFFICIENT_SPECTRAL: len(grouped.get(INSUFFICIENT_SPECTRAL, [])),
            },
        },
        "groups": {
            CORROBORATED: summarize_rows(grouped.get(CORROBORATED, [])),
            INSUFFICIENT_SPECTRAL: summarize_rows(grouped.get(INSUFFICIENT_SPECTRAL, [])),
        },
        "rows": rows,
    })
    return payload


def run_self_test():
    resolved = [
        {
            "midi": 52,
            "onsetActivationPeak": 0.60,
            "valleyActivationMean": 0.15,
            "activationDrop": 0.45,
            "onsetSpectralDb": -15.0,
            "valleySpectralDb": -25.0,
            "spectralDropDb": 10.0,
            "observedSpanFromOnsetSeconds": 0.30,
            "samePitchReattackGapSeconds": 0.55,
            "valleyToReattackMarginSeconds": 0.25,
        },
        {
            "midi": 55,
            "onsetActivationPeak": 0.50,
            "valleyActivationMean": 0.18,
            "activationDrop": 0.32,
            "onsetSpectralDb": -20.0,
            "valleySpectralDb": -28.0,
            "spectralDropDb": 8.0,
            "observedSpanFromOnsetSeconds": 0.20,
            "samePitchReattackGapSeconds": 0.45,
            "valleyToReattackMarginSeconds": 0.25,
        },
    ]
    rejected = [{
        "midi": 52,
        "onsetActivationPeak": 0.55,
        "valleyActivationMean": 0.17,
        "activationDrop": 0.38,
        "onsetSpectralDb": -18.0,
        "valleySpectralDb": -21.0,
        "spectralDropDb": 3.0,
        "observedSpanFromOnsetSeconds": 0.25,
        "samePitchReattackGapSeconds": 0.70,
        "valleyToReattackMarginSeconds": 0.45,
    }]
    a = summarize_rows(resolved)
    b = summarize_rows(rejected)
    assert a["count"] == 2
    assert a["spectralDropDb"]["median"] == 9.0
    assert b["count"] == 1
    assert b["spectralDropDb"]["median"] == 3.0
    assert a["midiHistogram"] == {"52": 1, "55": 1}

    guards = {
        "descriptiveOnly": True,
        "changesDuration": False,
        "changesPitchIdentity": False,
        "invokesModel": False,
        "usesDecodedModelNoteEndAsDuration": False,
        "usesNextOnsetAsDuration": False,
        "usesSamePitchReattackAsDuration": False,
        "proposesNewReleaseRule": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
        "ownsAcceptanceDecision": False,
    }
    assert guards["descriptiveOnly"] is True
    assert all(value is False for key, value in guards.items() if key != "descriptiveOnly")
    first = json.dumps({"a": a, "b": b, "guards": guards}, sort_keys=True)
    second = json.dumps({"a": summarize_rows(resolved), "b": summarize_rows(rejected), "guards": guards}, sort_keys=True)
    assert first == second
    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "passed",
        "deterministic": True,
        "modelInvoked": False,
        "changesDuration": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
    }, sort_keys=True))


def main():
    args = parse_args()
    if args.self_test:
        run_self_test()
        return

    input_path = Path(args.input)
    evidence_path = Path(args.evidence)
    activation_path = Path(args.activation_evidence)
    output_path = Path(args.output)
    payload = run_probe(input_path, evidence_path, activation_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(json.dumps({
        "contract": CONTRACT,
        "diagnostics": payload["diagnostics"],
        "corroboratedSpectralDropDb": payload["groups"][CORROBORATED]["spectralDropDb"],
        "insufficientSpectralDropDb": payload["groups"][INSUFFICIENT_SPECTRAL]["spectralDropDb"],
        "hardGuards": payload["hardGuards"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
