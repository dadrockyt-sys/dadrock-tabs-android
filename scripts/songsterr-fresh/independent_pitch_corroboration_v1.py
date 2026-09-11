#!/usr/bin/env python3
"""Independent two-channel pitch corroboration research contract v1.

Reference-blind research only. This module does not invoke Demucs or Basic Pitch,
does not change upstream event identity, does not write duration, and does not
promote model validation or customer eligibility.

The method is preregistered in:
docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V1.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import wave
from pathlib import Path

import numpy as np

CONTRACT = "songsterr-fresh-independent-pitch-corroboration-research-v1"
FIXTURE_CONTRACT = "songsterr-fresh-independent-pitch-corroboration-fixtures-v1"
EXPECTED_EVIDENCE_CONTRACT = "songsterr-fresh-isolated-polyphonic-note-evidence-v1"

SAMPLE_RATE = 44100
WINDOW_SAMPLES = 8192
FFT_SIZE = 8192
PLAYABLE_MIDI_MIN = 40
PLAYABLE_MIDI_MAX = 88
COMPETITOR_OFFSETS = (-12, -2, -1, 1, 2, 12)
HARMONIC_WEIGHTS = (1.0, 0.75, 0.5, 0.35, 0.25)
TIE_ABS_TOLERANCE = 1e-6
MIN_WINDOW_RMS = 1e-4
FIXTURE_PEAK = 0.75

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


def midi_to_hz(midi: int) -> float:
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def competitor_midis(selected_midi: int) -> list[int]:
    values = [selected_midi]
    for offset in COMPETITOR_OFFSETS:
        candidate = selected_midi + offset
        if PLAYABLE_MIDI_MIN <= candidate <= PLAYABLE_MIDI_MAX:
            values.append(candidate)
    return values


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


def _prepare_window(samples: np.ndarray) -> np.ndarray:
    values = np.asarray(samples, dtype=np.float64)
    if values.ndim != 1:
        raise CorroborationError("MONO_WINDOW_REQUIRED")
    if values.size != WINDOW_SAMPLES:
        raise CorroborationError("EXACT_WINDOW_SAMPLE_COUNT_REQUIRED")
    if not np.all(np.isfinite(values)):
        raise CorroborationError("NONFINITE_AUDIO_WINDOW")
    return values - float(np.mean(values))


def _linear_power_at_frequency(
    power: np.ndarray,
    frequency_hz: float,
    bin_hz: float,
) -> float | None:
    if frequency_hz <= 0.0 or frequency_hz >= SAMPLE_RATE / 2.0:
        return None
    position = frequency_hz / bin_hz
    left = int(math.floor(position))
    right = left + 1
    if left < 0 or right >= power.size:
        return None
    fraction = position - float(left)
    return float((1.0 - fraction) * power[left] + fraction * power[right])


def harmonic_stack_scores(
    samples: np.ndarray,
    midis: list[int],
) -> dict[int, float]:
    """Channel A: fixed Hann/FFT harmonic-stack score."""
    values = _prepare_window(samples)
    windowed = values * np.hanning(WINDOW_SAMPLES)
    spectrum = np.fft.rfft(windowed, n=FFT_SIZE)
    power = np.square(np.abs(spectrum))
    bin_hz = SAMPLE_RATE / float(FFT_SIZE)

    scores: dict[int, float] = {}
    for midi in midis:
        fundamental = midi_to_hz(midi)
        weighted_sum = 0.0
        used_weight = 0.0
        for harmonic, weight in enumerate(HARMONIC_WEIGHTS, start=1):
            value = _linear_power_at_frequency(
                power,
                fundamental * float(harmonic),
                bin_hz,
            )
            if value is None:
                continue
            weighted_sum += float(weight) * math.log1p(value)
            used_weight += float(weight)
        scores[midi] = (
            float("-inf") if used_weight <= 0.0 else weighted_sum / used_weight
        )
    return scores


def _normalized_autocorrelation_at_integer_lag(
    values: np.ndarray,
    lag: int,
) -> float:
    if lag <= 0 or lag >= values.size - 1:
        return float("-inf")
    left = values[:-lag]
    right = values[lag:]
    left_energy = float(np.dot(left, left))
    right_energy = float(np.dot(right, right))
    denominator = math.sqrt(left_energy * right_energy)
    if denominator <= 0.0:
        return float("-inf")
    return float(np.dot(left, right)) / denominator


def _interpolated_normalized_autocorrelation(
    values: np.ndarray,
    lag: float,
) -> float:
    if not math.isfinite(lag) or lag <= 0.0:
        return float("-inf")
    lower = int(math.floor(lag))
    upper = lower + 1
    fraction = lag - float(lower)
    lower_value = _normalized_autocorrelation_at_integer_lag(values, lower)
    upper_value = _normalized_autocorrelation_at_integer_lag(values, upper)
    if not math.isfinite(lower_value) or not math.isfinite(upper_value):
        return float("-inf")
    return (1.0 - fraction) * lower_value + fraction * upper_value


def periodicity_competition_scores(
    samples: np.ndarray,
    midis: list[int],
) -> dict[int, float]:
    """Channel B: normalized autocorrelation with a subharmonic penalty.

    For candidate period T: score = NAC(T) - max(0, NAC(T/2)).
    """
    values = _prepare_window(samples)
    scores: dict[int, float] = {}
    for midi in midis:
        lag = SAMPLE_RATE / midi_to_hz(midi)
        primary = _interpolated_normalized_autocorrelation(values, lag)
        half_period = _interpolated_normalized_autocorrelation(values, lag / 2.0)
        if not math.isfinite(primary) or not math.isfinite(half_period):
            scores[midi] = float("-inf")
            continue
        scores[midi] = primary - max(0.0, half_period)
    return scores


def _winner_measurement(scores: dict[int, float], selected_midi: int) -> dict:
    if selected_midi not in scores:
        raise CorroborationError("SELECTED_MIDI_SCORE_MISSING")
    selected = float(scores[selected_midi])
    competitors = {
        int(midi): float(score)
        for midi, score in scores.items()
        if int(midi) != int(selected_midi)
    }
    finite_competitors = {
        midi: score for midi, score in competitors.items() if math.isfinite(score)
    }
    if not math.isfinite(selected) or not finite_competitors:
        return {
            "selectedScore": None if not math.isfinite(selected) else selected,
            "bestCompetitorMidi": None,
            "bestCompetitorScore": None,
            "selectedMinusBestCompetitor": None,
            "uniqueBest": False,
            "insufficient": True,
        }

    best_midi, best_score = max(
        finite_competitors.items(),
        key=lambda item: (item[1], -abs(item[0] - selected_midi), -item[0]),
    )
    margin = selected - best_score
    return {
        "selectedScore": selected,
        "bestCompetitorMidi": int(best_midi),
        "bestCompetitorScore": float(best_score),
        "selectedMinusBestCompetitor": float(margin),
        "uniqueBest": bool(margin > TIE_ABS_TOLERANCE),
        "insufficient": False,
    }


def classify_window(samples: np.ndarray, selected_midi: int) -> dict:
    if isinstance(selected_midi, bool):
        raise CorroborationError("SELECTED_MIDI_INTEGER_REQUIRED")
    selected_midi = int(selected_midi)
    if not PLAYABLE_MIDI_MIN <= selected_midi <= PLAYABLE_MIDI_MAX:
        raise CorroborationError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")

    values = _prepare_window(samples)
    rms = float(np.sqrt(np.mean(np.square(values))))
    candidates = competitor_midis(selected_midi)

    if rms < MIN_WINDOW_RMS:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "competitorMidis": candidates,
            "windowRms": rms,
            "channelA": None,
            "channelB": None,
            "reason": "WINDOW_RMS_BELOW_FIXED_MINIMUM",
        }

    channel_a_scores = harmonic_stack_scores(values, candidates)
    channel_b_scores = periodicity_competition_scores(values, candidates)
    channel_a = _winner_measurement(channel_a_scores, selected_midi)
    channel_b = _winner_measurement(channel_b_scores, selected_midi)

    if channel_a["insufficient"] or channel_b["insufficient"]:
        classification = CLASS_INSUFFICIENT
        reason = "CHANNEL_SCORE_INSUFFICIENT"
    elif channel_a["uniqueBest"] and channel_b["uniqueBest"]:
        classification = CLASS_CORROBORATED
        reason = "BOTH_CHANNELS_UNIQUE_BEST"
    else:
        classification = CLASS_NOT_CORROBORATED
        reason = "CHANNEL_DISAGREEMENT_OR_NON_UNIQUE_SELECTED"

    return {
        "classification": classification,
        "selectedMidi": selected_midi,
        "competitorMidis": candidates,
        "windowRms": rms,
        "channelA": {
            "method": "hann8192-rfft8192-harmonic-stack-log1p-power-linear-bin-interpolation",
            "scores": {str(k): float(v) for k, v in sorted(channel_a_scores.items())},
            **channel_a,
        },
        "channelB": {
            "method": "normalized-autocorrelation-period-minus-positive-half-period",
            "scores": {str(k): float(v) for k, v in sorted(channel_b_scores.items())},
            **channel_b,
        },
        "reason": reason,
    }


def _pluck(
    midi: int,
    *,
    amplitudes=(1.0, 0.55, 0.30, 0.18, 0.10),
    decay_per_second: float = 8.0,
) -> np.ndarray:
    time = np.arange(WINDOW_SAMPLES, dtype=np.float64) / float(SAMPLE_RATE)
    envelope = np.exp(-float(decay_per_second) * time)
    fundamental = midi_to_hz(midi)
    signal = np.zeros(WINDOW_SAMPLES, dtype=np.float64)
    for harmonic, amplitude in enumerate(amplitudes, start=1):
        frequency = fundamental * float(harmonic)
        if frequency >= SAMPLE_RATE / 2.0:
            continue
        signal += float(amplitude) * np.sin(2.0 * np.pi * frequency * time)
    return signal * envelope


def _normalize_peak(values: np.ndarray, peak: float = FIXTURE_PEAK) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    maximum = float(np.max(np.abs(values))) if values.size else 0.0
    return values.copy() if maximum <= 0.0 else values * (float(peak) / maximum)


def _fixture_signals() -> dict[str, tuple[np.ndarray, int, str]]:
    low_noise_rng = np.random.default_rng(2468)
    return {
        "mono_low_m40": (_normalize_peak(_pluck(40)), 40, CLASS_CORROBORATED),
        "mono_mid_m64": (_normalize_peak(_pluck(64)), 64, CLASS_CORROBORATED),
        "mono_high_m88": (_normalize_peak(_pluck(88)), 88, CLASS_CORROBORATED),
        "octave_confusion_m52": (
            _normalize_peak(
                _pluck(
                    52,
                    amplitudes=(0.05, 1.0, 0.05, 0.02, 0.01),
                    decay_per_second=6.0,
                )
            ),
            52,
            CLASS_NOT_CORROBORATED,
        ),
        "semitone_adversarial_m60": (
            _normalize_peak(0.4 * _pluck(60) + 1.0 * _pluck(61)),
            60,
            CLASS_NOT_CORROBORATED,
        ),
        "dyad_close_m60": (
            _normalize_peak(_pluck(60) + _pluck(61)),
            60,
            CLASS_NOT_CORROBORATED,
        ),
        "triad_cluster_m60": (
            _normalize_peak(_pluck(59) + _pluck(60) + _pluck(61)),
            60,
            CLASS_NOT_CORROBORATED,
        ),
        "silence_m60": (
            np.zeros(WINDOW_SAMPLES, dtype=np.float64),
            60,
            CLASS_INSUFFICIENT,
        ),
        "low_noise_m60": (
            1e-5 * low_noise_rng.standard_normal(WINDOW_SAMPLES),
            60,
            CLASS_INSUFFICIENT,
        ),
    }


def _pcm16_wav_bytes(values: np.ndarray) -> bytes:
    import io

    clipped = np.clip(np.asarray(values, dtype=np.float64), -1.0, 1.0)
    pcm = np.rint(clipped * 32767.0).astype("<i2")
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(pcm.tobytes())
    return buffer.getvalue()


def _decode_pcm16_fixture_bytes(data: bytes) -> np.ndarray:
    import io

    with wave.open(io.BytesIO(data), "rb") as handle:
        if (
            handle.getnchannels() != 1
            or handle.getsampwidth() != 2
            or handle.getframerate() != SAMPLE_RATE
            or handle.getnframes() != WINDOW_SAMPLES
        ):
            raise CorroborationError("CONTROLLED_FIXTURE_WAV_FORMAT_CHANGED")
        pcm = handle.readframes(WINDOW_SAMPLES)
    return np.frombuffer(pcm, dtype="<i2").astype(np.float64) / 32768.0


def write_controlled_fixtures(output_dir: Path) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for name, (signal, selected_midi, expected_classification) in _fixture_signals().items():
        wav_bytes = _pcm16_wav_bytes(signal)
        path = output_dir / f"{name}.wav"
        path.write_bytes(wav_bytes)
        records.append(
            {
                "name": name,
                "selectedMidi": selected_midi,
                "expectedClassification": expected_classification,
                "pcm16WavSha256": sha256_bytes(wav_bytes),
                "sampleRate": SAMPLE_RATE,
                "sampleCount": WINDOW_SAMPLES,
                "channels": 1,
            }
        )
    return records


def load_fixture_manifest(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CorroborationError("FIXTURE_MANIFEST_LOAD_FAILED") from exc
    if value.get("contract") != FIXTURE_CONTRACT:
        raise CorroborationError("FIXTURE_MANIFEST_CONTRACT_CHANGED")
    if value.get("version") != 1:
        raise CorroborationError("FIXTURE_MANIFEST_VERSION_CHANGED")
    return value


def run_controlled_fixture_suite(manifest_path: Path, output_dir: Path) -> dict:
    manifest = load_fixture_manifest(manifest_path)
    generated = write_controlled_fixtures(output_dir)
    expected_by_name = {item["name"]: item for item in manifest.get("fixtures", [])}
    generated_by_name = {item["name"]: item for item in generated}
    if set(expected_by_name) != set(generated_by_name):
        raise CorroborationError("FIXTURE_NAME_SET_CHANGED")

    rows = []
    for name in sorted(expected_by_name):
        expected = expected_by_name[name]
        actual = generated_by_name[name]
        for field in (
            "selectedMidi",
            "expectedClassification",
            "pcm16WavSha256",
            "sampleRate",
            "sampleCount",
            "channels",
        ):
            if actual.get(field) != expected.get(field):
                raise CorroborationError(f"FIXTURE_IDENTITY_CHANGED:{name}:{field}")
        data = (output_dir / f"{name}.wav").read_bytes()
        samples = _decode_pcm16_fixture_bytes(data)
        result = classify_window(samples, int(expected["selectedMidi"]))
        if result["classification"] != expected["expectedClassification"]:
            raise CorroborationError(
                f"FIXTURE_CLASSIFICATION_FAILED:{name}:"
                f"{result['classification']}!={expected['expectedClassification']}"
            )
        rows.append(
            {
                "name": name,
                "expectedClassification": expected["expectedClassification"],
                "observedClassification": result["classification"],
                "pcm16WavSha256": expected["pcm16WavSha256"],
                "channelAUniqueBest": (
                    None if result["channelA"] is None else result["channelA"]["uniqueBest"]
                ),
                "channelBUniqueBest": (
                    None if result["channelB"] is None else result["channelB"]["uniqueBest"]
                ),
            }
        )

    return {
        "contract": CONTRACT,
        "fixtureContract": FIXTURE_CONTRACT,
        "suiteStatus": "PASS",
        "fixtureCount": len(rows),
        "fixtures": rows,
        "policyBoundary": {
            "authorizedSongEvaluated": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
            "basicPitchActivationUsed": False,
            "basicPitchDecisionSurfaceUsed": False,
            "basicPitchNoteSpanAmplitudeUsed": False,
            "basicPitchDecodedNoteEndUsed": False,
            "durationAuthorityChanged": False,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "customerEligibleEvents": 0,
        },
    }


def _read_audio(path: Path) -> tuple[np.ndarray, int]:
    try:
        import soundfile as sf
    except Exception as exc:
        raise CorroborationError("SOUNDFILE_PACKAGE_REQUIRED") from exc
    try:
        audio, sample_rate = sf.read(str(path), dtype="float64", always_2d=True)
    except Exception as exc:
        raise CorroborationError("AUDIO_READ_FAILED") from exc
    if int(sample_rate) != SAMPLE_RATE:
        raise CorroborationError(f"SAMPLE_RATE_MUST_BE_{SAMPLE_RATE}")
    if audio.shape[0] < WINDOW_SAMPLES:
        raise CorroborationError("AUDIO_TOO_SHORT")
    mono = np.mean(audio, axis=1, dtype=np.float64)
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
        source_start = _finite_float(onset.get("sourceStart"), f"onsets[{index}].sourceStart")
        midi_raw = onset.get("selectedMidi")
        if isinstance(midi_raw, bool) or not isinstance(midi_raw, int):
            raise CorroborationError(f"onsets[{index}].selectedMidi:INTEGER_REQUIRED")
        if not PLAYABLE_MIDI_MIN <= midi_raw <= PLAYABLE_MIDI_MAX:
            raise CorroborationError(f"onsets[{index}].selectedMidi:OUT_OF_RANGE")
        if onset.get("sourceEnd") is not None or onset.get("durationSeconds") is not None:
            raise CorroborationError(f"onsets[{index}]:DURATION_MUST_REMAIN_UNRESOLVED")
        onset_id = onset.get("onsetId")
        if not isinstance(onset_id, str) or not onset_id:
            raise CorroborationError(f"onsets[{index}].onsetId:NONEMPTY_STRING_REQUIRED")
        rows.append(
            {
                "onsetId": onset_id,
                "sourceStart": source_start,
                "selectedMidi": midi_raw,
            }
        )
    if not rows:
        raise CorroborationError("EVIDENCE_ONSETS_REQUIRED")
    return rows


def evaluate_evidence(stem_path: Path, evidence_path: Path) -> dict:
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    events = _validate_evidence(evidence)
    audio, sample_rate = _read_audio(stem_path)
    stem_sha256 = sha256_bytes(stem_path.read_bytes())

    results = []
    counts = {name: 0 for name in sorted(ALLOWED_CLASSES)}
    for event in events:
        start_sample = int(math.floor(event["sourceStart"] * sample_rate + 0.5))
        stop_sample = start_sample + WINDOW_SAMPLES
        if start_sample < 0 or stop_sample > audio.size:
            result = {
                "classification": CLASS_INSUFFICIENT,
                "selectedMidi": event["selectedMidi"],
                "competitorMidis": competitor_midis(event["selectedMidi"]),
                "windowRms": None,
                "channelA": None,
                "channelB": None,
                "reason": "FIXED_WINDOW_OUTSIDE_AUDIO",
            }
        else:
            result = classify_window(audio[start_sample:stop_sample], event["selectedMidi"])
        counts[result["classification"]] += 1
        results.append(
            {
                "onsetId": event["onsetId"],
                "sourceStart": event["sourceStart"],
                "selectedMidi": event["selectedMidi"],
                "startSample": start_sample,
                "stopSampleExclusive": stop_sample,
                **result,
            }
        )

    return {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "researchOnly": True,
        "methodFrozenBeforeAuthorizedSongEvaluation": True,
        "method": {
            "sampleRate": SAMPLE_RATE,
            "windowSamples": WINDOW_SAMPLES,
            "windowSeconds": WINDOW_SAMPLES / float(SAMPLE_RATE),
            "startSampleRule": "floor(sourceStartSeconds*44100+0.5)",
            "playableMidiRange": [PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX],
            "competitorOffsetsSemitones": list(COMPETITOR_OFFSETS),
            "tieAbsoluteTolerance": TIE_ABS_TOLERANCE,
            "minimumWindowRms": MIN_WINDOW_RMS,
            "channelA": {
                "window": "numpy.hanning(8192)",
                "fftSize": FFT_SIZE,
                "spectrum": "rfft-power",
                "frequencySampling": "linear-interpolation-adjacent-power-bins",
                "harmonicWeights": list(HARMONIC_WEIGHTS),
                "harmonicTransform": "log1p(power)",
                "scoreAggregation": "weighted-mean-available-harmonics",
            },
            "channelB": {
                "autocorrelation": "normalized-dot-product",
                "fractionalLagInterpolation": "linear-between-adjacent-integer-lags",
                "score": "NAC(T)-max(0,NAC(T/2))",
            },
            "corroborationRule": (
                "selected MIDI must exceed every fixed competitor by >1e-6 "
                "in both channels; otherwise fail closed"
            ),
        },
        "identityProof": {
            "inputStemSha256": stem_sha256,
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
            "usesBasicPitchActivations": False,
            "usesBasicPitchDecisionSurface": False,
            "usesBasicPitchNoteSpanAmplitude": False,
            "usesBasicPitchDecodedNoteEnd": False,
            "usesReferenceTab": False,
            "usesProfessionalScorer": False,
            "importsArchivedV143Logic": False,
            "changesPitchIdentity": False,
            "writesDurationSeconds": False,
            "writesSourceEnd": False,
            "ownsAdmissionDecision": False,
            "setsModelValidationComplete": False,
            "setsCustomerEligibility": False,
        },
        "policyBoundary": {
            "status": "INDEPENDENT_CORROBORATION_RESEARCH_ONLY",
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "customerEligibleEvents": 0,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--fixture-manifest")
    parser.add_argument("--fixture-output-dir")
    parser.add_argument("--input-stem")
    parser.add_argument("--evidence")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        if not args.fixture_manifest or not args.fixture_output_dir:
            raise CorroborationError("SELF_TEST_REQUIRES_FIXTURE_MANIFEST_AND_OUTPUT_DIR")
        report = run_controlled_fixture_suite(
            Path(args.fixture_manifest),
            Path(args.fixture_output_dir),
        )
        print(canonical_json(report))
        return 0

    if not args.input_stem or not args.evidence or not args.output:
        raise CorroborationError("USAGE_REQUIRES_INPUT_STEM_EVIDENCE_AND_OUTPUT")
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
        print(f"INDEPENDENT_CORROBORATION_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
