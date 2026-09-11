#!/usr/bin/env python3
"""Synthetic-development temporal-consensus pitch corroboration V4.

Reference-blind research only. Frozen by
`SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V4.md` before any
external-corpus or protected-song evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from importlib.metadata import version as package_version
from pathlib import Path

import librosa
import numpy as np

CONTRACT = "songsterr-fresh-temporal-consensus-pitch-corroboration-research-v4"
VERSION = 4
EXPECTED_EVIDENCE_CONTRACT = "songsterr-fresh-isolated-polyphonic-note-evidence-v1"

SAMPLE_RATE = 44100
WINDOW_SAMPLES = 8192
WINDOW_OFFSETS = (1024, 7168, 13312)
FFT_SIZE = 32768
PLAYABLE_MIDI_MIN = 40
PLAYABLE_MIDI_MAX = 88
HARMONIC_COUNT_MAX = 6
SPECTRAL_LOG_FLOOR = 1e-15
YIN_TROUGH_THRESHOLD = 0.1
LIBROSA_VERSION = "0.11.0"

CLASS_CORROBORATED = "independently-corroborated-candidate"
CLASS_NOT_CORROBORATED = "not-independently-corroborated"
CLASS_INSUFFICIENT = "insufficient-evidence"
ALLOWED_CLASSES = {
    CLASS_CORROBORATED,
    CLASS_NOT_CORROBORATED,
    CLASS_INSUFFICIENT,
}


class CorroborationError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def midi_to_hz(midi: float) -> float:
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def _finite_float(value, label: str) -> float:
    if isinstance(value, bool):
        raise CorroborationError(f"{label}:FINITE_NUMBER_REQUIRED")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise CorroborationError(f"{label}:FINITE_NUMBER_REQUIRED") from exc
    if not math.isfinite(number):
        raise CorroborationError(f"{label}:FINITE_NUMBER_REQUIRED")
    return number


def _prepare_window(samples: np.ndarray) -> tuple[np.ndarray, float]:
    values = np.asarray(samples, dtype=np.float64)
    if values.ndim != 1:
        raise CorroborationError("MONO_WINDOW_REQUIRED")
    if values.size != WINDOW_SAMPLES:
        raise CorroborationError("EXACT_WINDOW_SAMPLE_COUNT_REQUIRED")
    if not np.all(np.isfinite(values)):
        raise CorroborationError("NONFINITE_AUDIO_WINDOW")
    demeaned = values - float(np.mean(values))
    energy = float(np.dot(demeaned, demeaned))
    if not math.isfinite(energy):
        raise CorroborationError("WINDOW_ENERGY_NONFINITE")
    return demeaned, energy


def _spectral_scores(samples: np.ndarray) -> tuple[dict[int, float], dict[int, dict]]:
    values, energy = _prepare_window(samples)
    if energy == 0.0:
        raise CorroborationError("ZERO_DEMEANED_WINDOW_ENERGY")

    windowed = values * np.hanning(WINDOW_SAMPLES)
    magnitude = np.abs(np.fft.rfft(windowed, n=FFT_SIZE))
    frequencies = np.fft.rfftfreq(FFT_SIZE, d=1.0 / float(SAMPLE_RATE))

    scores: dict[int, float] = {}
    details: dict[int, dict] = {}

    for midi in range(PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX + 1):
        low_hz = midi_to_hz(float(midi) - 0.5)
        high_hz = midi_to_hz(float(midi) + 0.5)
        indices = np.flatnonzero((frequencies >= low_hz) & (frequencies < high_hz))
        if indices.size == 0:
            scores[midi] = float("-inf")
            details[midi] = {
                "fundamentalBin": None,
                "fundamentalHz": None,
                "harmonicMagnitudes": [],
            }
            continue

        local = magnitude[indices]
        fundamental_bin = int(indices[int(np.argmax(local))])
        f_hat = float(frequencies[fundamental_bin])
        harmonic_magnitudes: list[float] = []

        for harmonic in range(1, HARMONIC_COUNT_MAX + 1):
            target_hz = float(harmonic) * f_hat
            if target_hz >= SAMPLE_RATE / 2.0:
                break
            position = target_hz * float(FFT_SIZE) / float(SAMPLE_RATE)
            nearest = int(math.floor(position + 0.5))
            left = max(0, nearest - 1)
            right = min(magnitude.size - 1, nearest + 1)
            harmonic_magnitudes.append(float(np.max(magnitude[left : right + 1])))

        if not harmonic_magnitudes or not all(
            math.isfinite(value) for value in harmonic_magnitudes
        ):
            scores[midi] = float("-inf")
        else:
            logs = [
                math.log(max(SPECTRAL_LOG_FLOOR, value))
                for value in harmonic_magnitudes
            ]
            scores[midi] = float(sum(logs) / float(len(logs)))

        details[midi] = {
            "fundamentalBin": fundamental_bin,
            "fundamentalHz": f_hat,
            "harmonicMagnitudes": harmonic_magnitudes,
        }

    return scores, details


def _unique_winner(scores: dict[int, float]) -> int | None:
    finite = {
        int(midi): float(score)
        for midi, score in scores.items()
        if math.isfinite(float(score))
    }
    if len(finite) != len(scores) or not finite:
        return None
    best = max(finite.values())
    winners = [midi for midi, score in finite.items() if score == best]
    return winners[0] if len(winners) == 1 else None


def _yin_measurement(samples: np.ndarray) -> dict:
    actual_librosa = package_version("librosa")
    if actual_librosa != LIBROSA_VERSION:
        raise CorroborationError(
            f"LIBROSA_VERSION_CHANGED:{actual_librosa}!={LIBROSA_VERSION}"
        )

    _values, energy = _prepare_window(samples)
    if energy == 0.0:
        raise CorroborationError("ZERO_DEMEANED_WINDOW_ENERGY")

    f0 = librosa.yin(
        np.asarray(samples, dtype=np.float64),
        fmin=midi_to_hz(PLAYABLE_MIDI_MIN - 0.5),
        fmax=midi_to_hz(PLAYABLE_MIDI_MAX + 0.5),
        sr=SAMPLE_RATE,
        frame_length=WINDOW_SAMPLES,
        hop_length=WINDOW_SAMPLES,
        trough_threshold=YIN_TROUGH_THRESHOLD,
        center=False,
    )
    estimates = np.asarray(f0, dtype=np.float64).reshape(-1)
    if (
        estimates.size != 1
        or not math.isfinite(float(estimates[0]))
        or float(estimates[0]) <= 0.0
    ):
        raise CorroborationError("YIN_FINITE_SINGLE_ESTIMATE_REQUIRED")

    frequency_hz = float(estimates[0])
    midi_float = 69.0 + 12.0 * math.log2(frequency_hz / 440.0)
    winner_midi = None
    for midi in range(PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX + 1):
        if float(midi) - 0.5 <= midi_float < float(midi) + 0.5:
            winner_midi = midi
            break

    return {
        "frequencyHz": frequency_hz,
        "midiFloat": midi_float,
        "winnerMidi": winner_midi,
    }


def classify_audio_event(
    audio: np.ndarray,
    onset_sample: int,
    selected_midi: int,
) -> dict:
    if isinstance(selected_midi, bool) or not isinstance(
        selected_midi, (int, np.integer)
    ):
        raise CorroborationError("SELECTED_MIDI_INTEGER_REQUIRED")
    selected_midi = int(selected_midi)
    if not PLAYABLE_MIDI_MIN <= selected_midi <= PLAYABLE_MIDI_MAX:
        raise CorroborationError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")

    values = np.asarray(audio, dtype=np.float64)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise CorroborationError("FINITE_MONO_AUDIO_REQUIRED")

    if isinstance(onset_sample, bool) or not isinstance(
        onset_sample, (int, np.integer)
    ):
        raise CorroborationError("ONSET_SAMPLE_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)
    if onset_sample < 0:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "views": [],
            "reason": "ONSET_BEFORE_AUDIO",
        }

    views = []
    for offset in WINDOW_OFFSETS:
        start = onset_sample + int(offset)
        stop = start + WINDOW_SAMPLES
        if stop > values.size:
            return {
                "classification": CLASS_INSUFFICIENT,
                "selectedMidi": selected_midi,
                "views": views,
                "reason": "REQUIRED_TEMPORAL_WINDOW_OUTSIDE_AUDIO",
            }

        window = values[start:stop]
        try:
            _demeaned, energy = _prepare_window(window)
            if energy == 0.0:
                return {
                    "classification": CLASS_INSUFFICIENT,
                    "selectedMidi": selected_midi,
                    "views": views,
                    "reason": "ZERO_DEMEANED_WINDOW_ENERGY",
                }
            spectral_scores, _spectral_details = _spectral_scores(window)
            spectral_winner = _unique_winner(spectral_scores)
            yin = _yin_measurement(window)
        except CorroborationError:
            return {
                "classification": CLASS_INSUFFICIENT,
                "selectedMidi": selected_midi,
                "views": views,
                "reason": "VIEW_SCORE_INSUFFICIENT",
            }

        selected_score = (
            float(spectral_scores[selected_midi])
            if math.isfinite(float(spectral_scores[selected_midi]))
            else None
        )
        competitors = [
            (midi, score)
            for midi, score in spectral_scores.items()
            if midi != selected_midi and math.isfinite(float(score))
        ]
        best_competitor = None
        if competitors:
            best_midi, best_score = max(
                competitors,
                key=lambda item: (
                    item[1],
                    -abs(item[0] - selected_midi),
                    -item[0],
                ),
            )
            best_competitor = {
                "midi": int(best_midi),
                "score": float(best_score),
            }

        views.append(
            {
                "offsetSamples": int(offset),
                "startSample": int(start),
                "stopSampleExclusive": int(stop),
                "spectralWinnerMidi": (
                    None if spectral_winner is None else int(spectral_winner)
                ),
                "selectedSpectralScore": selected_score,
                "bestSpectralCompetitor": best_competitor,
                "yinFrequencyHz": yin["frequencyHz"],
                "yinMidiFloat": yin["midiFloat"],
                "yinWinnerMidi": yin["winnerMidi"],
                "selectedWinsSpectral": spectral_winner == selected_midi,
                "selectedWinsYin": yin["winnerMidi"] == selected_midi,
            }
        )

    unanimous = all(
        row["selectedWinsSpectral"] and row["selectedWinsYin"] for row in views
    )
    return {
        "classification": (
            CLASS_CORROBORATED if unanimous else CLASS_NOT_CORROBORATED
        ),
        "selectedMidi": selected_midi,
        "views": views,
        "reason": (
            "ALL_THREE_WINDOWS_SPECTRAL_AND_YIN_AGREE"
            if unanimous
            else "TEMPORAL_OR_VIEW_DISAGREEMENT"
        ),
    }


def _synth_note(
    midi: int,
    *,
    sample_count: int = 23552,
    cents: float = 0.0,
    decay_per_second: float = 1.5,
    amplitudes=(1.0, 0.55, 0.30, 0.18, 0.10, 0.06),
) -> np.ndarray:
    time = np.arange(sample_count, dtype=np.float64) / float(SAMPLE_RATE)
    frequency = midi_to_hz(float(midi) + float(cents) / 100.0)
    signal = np.zeros(sample_count, dtype=np.float64)
    envelope = np.exp(-float(decay_per_second) * time)
    for harmonic, amplitude in enumerate(amplitudes, start=1):
        harmonic_hz = float(harmonic) * frequency
        if harmonic_hz < SAMPLE_RATE / 2.0:
            signal += float(amplitude) * np.sin(
                2.0 * np.pi * harmonic_hz * time
            )
    return signal * envelope


def _normalize(values: np.ndarray, peak: float = 0.75) -> np.ndarray:
    samples = np.asarray(values, dtype=np.float64)
    maximum = float(np.max(np.abs(samples))) if samples.size else 0.0
    return samples.copy() if maximum <= 0.0 else samples * (float(peak) / maximum)


def run_self_test() -> dict:
    assert tuple(WINDOW_OFFSETS) == (1024, 7168, 13312)
    assert WINDOW_SAMPLES == 8192
    assert FFT_SIZE == 32768
    assert (PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX) == (40, 88)
    assert package_version("librosa") == LIBROSA_VERSION

    fixtures: dict[str, tuple[np.ndarray, int, str]] = {}
    for midi in (40, 64, 88):
        fixtures[f"stable_{midi}"] = (
            _normalize(_synth_note(midi)),
            midi,
            CLASS_CORROBORATED,
        )

    fixtures["detuned_plus25_m64"] = (
        _normalize(_synth_note(64, cents=25.0)),
        64,
        CLASS_CORROBORATED,
    )

    attack_rng = np.random.default_rng(404)
    attack = np.zeros(23552, dtype=np.float64)
    attack[:800] = (
        0.4
        * attack_rng.standard_normal(800)
        * np.exp(-np.arange(800, dtype=np.float64) / 140.0)
    )
    fixtures["attack_noise_m64"] = (
        _normalize(_synth_note(64) + attack),
        64,
        CLASS_CORROBORATED,
    )

    fixtures["wrong_octave_selected52"] = (
        _normalize(_synth_note(64)),
        52,
        CLASS_NOT_CORROBORATED,
    )
    fixtures["stronger_adjacent_selected60"] = (
        _normalize(0.35 * _synth_note(60) + _synth_note(61)),
        60,
        CLASS_NOT_CORROBORATED,
    )
    fixtures["stronger_fifth_selected60"] = (
        _normalize(0.35 * _synth_note(60) + _synth_note(67)),
        60,
        CLASS_NOT_CORROBORATED,
    )
    fixtures["poly_competitor_selected60"] = (
        _normalize(0.4 * _synth_note(60) + _synth_note(64)),
        60,
        CLASS_NOT_CORROBORATED,
    )

    changed = _synth_note(64)
    later_pitch = _synth_note(67)
    changed[9000:] = later_pitch[9000:]
    fixtures["temporal_change_selected64"] = (
        _normalize(changed),
        64,
        CLASS_NOT_CORROBORATED,
    )

    fixtures["zero_selected60"] = (
        np.zeros(23552, dtype=np.float64),
        60,
        CLASS_INSUFFICIENT,
    )
    fixtures["truncated_selected64"] = (
        _normalize(_synth_note(64, sample_count=18000)),
        64,
        CLASS_INSUFFICIENT,
    )

    rows = []
    for name, (audio, midi, expected) in fixtures.items():
        result = classify_audio_event(audio, 0, midi)
        if result["classification"] != expected:
            raise CorroborationError(
                f"SELF_TEST_FAILED:{name}:"
                f"{result['classification']}!={expected}"
            )
        rows.append(
            {
                "name": name,
                "expected": expected,
                "observed": result["classification"],
            }
        )

    if _unique_winner({40: 1.0, 41: 1.0, 42: 0.5}) is not None:
        raise CorroborationError("STRICT_SPECTRAL_TIE_GUARD_FAILED")

    full_range_scores, _ = _spectral_scores(
        _normalize(_synth_note(64))[:WINDOW_SAMPLES]
    )
    if set(full_range_scores) != set(range(40, 89)):
        raise CorroborationError("FULL_RANGE_SPECTRAL_COMPETITION_CHANGED")

    policy = {
        "guitarsetEvaluated": False,
        "idmtEvaluated": False,
        "protectedSongEvaluated": False,
        "referenceTabUsed": False,
        "professionalScorerUsed": False,
        "archivedV143Imported": False,
        "goatResearchUsed": False,
        "durationAuthorityChanged": False,
        "admissionDecisionMade": False,
        "modelValidationComplete": False,
        "mayAdvanceDelivery": False,
        "customerEligibleEvents": 0,
    }

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "selfTest": "PASS",
        "fixtures": rows,
        "policyBoundary": policy,
    }


def _read_audio(path: Path) -> tuple[np.ndarray, int]:
    try:
        import soundfile as sf
    except Exception as exc:
        raise CorroborationError("SOUNDFILE_PACKAGE_REQUIRED") from exc
    try:
        audio, sample_rate = sf.read(
            str(path), dtype="float64", always_2d=True
        )
    except Exception as exc:
        raise CorroborationError("AUDIO_READ_FAILED") from exc
    if int(sample_rate) != SAMPLE_RATE:
        raise CorroborationError(f"SAMPLE_RATE_MUST_BE_{SAMPLE_RATE}")
    if audio.shape[1] != 1:
        raise CorroborationError("MONO_AUDIO_REQUIRED")
    mono = np.asarray(audio[:, 0], dtype=np.float64)
    if not np.all(np.isfinite(mono)):
        raise CorroborationError("AUDIO_CONTAINS_NONFINITE_VALUES")
    return mono, int(sample_rate)


def _validate_evidence(evidence: dict) -> list[dict]:
    if evidence.get("contract") != EXPECTED_EVIDENCE_CONTRACT:
        raise CorroborationError("EVIDENCE_CONTRACT_CHANGED")
    if evidence.get("referenceBlind") is not True:
        raise CorroborationError("EVIDENCE_NOT_REFERENCE_BLIND")
    if evidence.get("structureFrozen") is not True:
        raise CorroborationError("EVIDENCE_STRUCTURE_NOT_FROZEN")
    if evidence.get("role") != "guitar":
        raise CorroborationError("EVIDENCE_ROLE_NOT_GUITAR")

    provenance = evidence.get("provenance", {})
    for field in (
        "referenceTabUsed",
        "professionalScorerUsed",
        "legacyV143ScorerImported",
        "modelNoteEndsUsedAsDuration",
    ):
        if provenance.get(field) is not False:
            raise CorroborationError(f"EVIDENCE_PROVENANCE_GUARD_CHANGED:{field}")

    rows = []
    for index, onset in enumerate(evidence.get("onsets", [])):
        source_start = _finite_float(
            onset.get("sourceStart"), f"onsets[{index}].sourceStart"
        )
        midi = onset.get("selectedMidi")
        if isinstance(midi, bool) or not isinstance(midi, int):
            raise CorroborationError(
                f"onsets[{index}].selectedMidi:INTEGER_REQUIRED"
            )
        if not PLAYABLE_MIDI_MIN <= midi <= PLAYABLE_MIDI_MAX:
            raise CorroborationError(
                f"onsets[{index}].selectedMidi:OUT_OF_RANGE"
            )
        if (
            onset.get("sourceEnd") is not None
            or onset.get("durationSeconds") is not None
        ):
            raise CorroborationError(
                f"onsets[{index}]:DURATION_MUST_REMAIN_UNRESOLVED"
            )
        onset_id = onset.get("onsetId")
        if not isinstance(onset_id, str) or not onset_id:
            raise CorroborationError(
                f"onsets[{index}].onsetId:NONEMPTY_STRING_REQUIRED"
            )
        rows.append(
            {
                "onsetId": onset_id,
                "sourceStart": source_start,
                "selectedMidi": midi,
            }
        )

    if not rows:
        raise CorroborationError("EVIDENCE_ONSETS_REQUIRED")
    return rows


def evaluate_evidence(stem_path: Path, evidence_path: Path) -> dict:
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    events = _validate_evidence(evidence)
    audio, sample_rate = _read_audio(stem_path)

    counts = {classification: 0 for classification in sorted(ALLOWED_CLASSES)}
    results = []

    for event in events:
        onset_sample = int(
            math.floor(event["sourceStart"] * float(sample_rate) + 0.5)
        )
        classification = classify_audio_event(
            audio,
            onset_sample,
            event["selectedMidi"],
        )
        counts[classification["classification"]] += 1
        results.append(
            {
                "onsetId": event["onsetId"],
                "sourceStart": event["sourceStart"],
                "selectedMidi": event["selectedMidi"],
                "onsetSample": onset_sample,
                **classification,
            }
        )

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "referenceBlind": True,
        "researchOnly": True,
        "method": {
            "sampleRate": SAMPLE_RATE,
            "windowSamples": WINDOW_SAMPLES,
            "windowOffsetsSamples": list(WINDOW_OFFSETS),
            "fftSize": FFT_SIZE,
            "playableMidiRange": [PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX],
            "spectralHarmonicCountMax": HARMONIC_COUNT_MAX,
            "spectralLogFloor": SPECTRAL_LOG_FLOOR,
            "yin": {
                "library": "librosa",
                "requiredVersion": LIBROSA_VERSION,
                "troughThreshold": YIN_TROUGH_THRESHOLD,
                "fminMidi": PLAYABLE_MIDI_MIN - 0.5,
                "fmaxMidi": PLAYABLE_MIDI_MAX + 0.5,
                "frameLength": WINDOW_SAMPLES,
                "hopLength": WINDOW_SAMPLES,
                "center": False,
            },
            "winnerRule": (
                "selected MIDI must win spectral and YIN decisions in all "
                "three windows; no voting or margin threshold"
            ),
        },
        "identityProof": {
            "inputStemSha256": sha256_bytes(stem_path.read_bytes()),
            "evidenceCanonicalSha256": hashlib.sha256(
                canonical_json(evidence).encode("utf-8")
            ).hexdigest(),
            "structureIdentity": evidence.get("structureIdentity"),
            "eventCount": len(events),
            "exactEventIdentityPreserved": True,
        },
        "summary": {
            "eventCount": len(results),
            "classificationCounts": counts,
        },
        "events": results,
        "hardGuards": {
            "invokesDemucs": False,
            "invokesBasicPitch": False,
            "usesBasicPitchConfidence": False,
            "usesBasicPitchDecodedNoteEnd": False,
            "usesDuration": False,
            "usesNextOnset": False,
            "usesBasicPitchActivations": False,
            "usesBasicPitchDecisionSurface": False,
            "usesReferenceTab": False,
            "usesProfessionalScorer": False,
            "importsArchivedV143Logic": False,
            "usesGoatResearch": False,
            "usesGuitarSet": False,
            "usesIdmt": False,
            "changesPitchIdentity": False,
            "changesOnsetIdentity": False,
            "dropsEvents": False,
            "ownsAdmissionDecision": False,
            "setsModelValidationComplete": False,
            "setsCustomerEligibility": False,
            "changesDurationAuthority": False,
        },
        "policyBoundary": {
            "status": "TEMPORAL_CONSENSUS_V4_RESEARCH_ONLY",
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--input-stem")
    parser.add_argument("--evidence")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        print(canonical_json(run_self_test()))
        return 0

    if not args.input_stem or not args.evidence or not args.output:
        raise CorroborationError(
            "USAGE_REQUIRES_INPUT_STEM_EVIDENCE_AND_OUTPUT"
        )

    result = evaluate_evidence(Path(args.input_stem), Path(args.evidence))
    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        canonical_json(
            {
                "contract": CONTRACT,
                "output": args.output,
                "summary": result["summary"],
                "policyBoundary": result["policyBoundary"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CorroborationError as exc:
        print(f"TEMPORAL_CONSENSUS_V4_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
