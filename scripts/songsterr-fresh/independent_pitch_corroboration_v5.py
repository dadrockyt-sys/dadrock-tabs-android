#!/usr/bin/env python3
"""Synthetic-development polyphonic harmonic-necessity corroboration V5.

Reference-blind research only. Frozen by
SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md before any
real-corpus V5 correctness evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from importlib.metadata import version as package_version
from pathlib import Path

import numpy as np
from scipy.optimize import nnls

CONTRACT = "songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5"
VERSION = 5

SAMPLE_RATE = 44100
WINDOW_SAMPLES = 8192
WINDOW_OFFSETS = (2048, 8192, 14336)
FFT_SIZE = 32768
PLAYABLE_MIDI_MIN = 40
PLAYABLE_MIDI_MAX = 88
HARMONIC_COUNT_MAX = 8
MIN_DEMEANED_RMS = 1e-4
NECESSITY_FRACTION_MIN = 0.01
FUNDAMENTAL_TO_MAX_HARMONIC_MIN = 0.05
NUMPY_VERSION = "1.26.4"
SCIPY_VERSION = "1.15.3"

CLASS_CORROBORATED = "independently-corroborated-candidate"
CLASS_NOT_CORROBORATED = "not-independently-corroborated"
CLASS_INSUFFICIENT = "insufficient-evidence"


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


def _check_runtime() -> None:
    actual_numpy = package_version("numpy")
    actual_scipy = package_version("scipy")
    if actual_numpy != NUMPY_VERSION:
        raise CorroborationError(f"NUMPY_VERSION_CHANGED:{actual_numpy}!={NUMPY_VERSION}")
    if actual_scipy != SCIPY_VERSION:
        raise CorroborationError(f"SCIPY_VERSION_CHANGED:{actual_scipy}!={SCIPY_VERSION}")


def _prepare_window(samples: np.ndarray) -> tuple[np.ndarray, float]:
    values = np.asarray(samples, dtype=np.float64)
    if values.ndim != 1 or values.size != WINDOW_SAMPLES:
        raise CorroborationError("EXACT_MONO_WINDOW_REQUIRED")
    if not np.all(np.isfinite(values)):
        raise CorroborationError("NONFINITE_AUDIO_WINDOW")
    demeaned = values - float(np.mean(values))
    rms = float(np.sqrt(np.mean(np.square(demeaned))))
    if not math.isfinite(rms):
        raise CorroborationError("WINDOW_RMS_NONFINITE")
    return demeaned, rms


def _candidate_template(
    midi: int,
    magnitude: np.ndarray,
    frequencies: np.ndarray,
) -> dict:
    low_hz = midi_to_hz(float(midi) - 0.5)
    high_hz = midi_to_hz(float(midi) + 0.5)
    indices = np.flatnonzero((frequencies >= low_hz) & (frequencies < high_hz))
    if indices.size == 0:
        return {"valid": False, "reason": "NO_FUNDAMENTAL_CELL_BIN"}

    local = magnitude[indices]
    fundamental_bin = int(indices[int(np.argmax(local))])
    f_hat = float(frequencies[fundamental_bin])
    if not math.isfinite(f_hat) or f_hat <= 0.0:
        return {"valid": False, "reason": "INVALID_FUNDAMENTAL_FREQUENCY"}

    bins: list[int] = []
    weights: list[float] = []
    observed: list[float] = []
    for harmonic in range(1, HARMONIC_COUNT_MAX + 1):
        target_hz = float(harmonic) * f_hat
        if target_hz >= SAMPLE_RATE / 2.0:
            break
        position = target_hz * float(FFT_SIZE) / float(SAMPLE_RATE)
        nearest = int(math.floor(position + 0.5))
        left = max(0, nearest - 1)
        right = min(magnitude.size - 1, nearest + 1)
        search = magnitude[left : right + 1]
        chosen = int(left + int(np.argmax(search)))
        bins.append(chosen)
        weights.append(1.0 / float(harmonic))
        observed.append(float(magnitude[chosen]))

    if len(bins) < 3:
        return {"valid": False, "reason": "FEWER_THAN_THREE_HARMONICS"}
    if not all(math.isfinite(x) and x >= 0.0 for x in observed):
        return {"valid": False, "reason": "NONFINITE_HARMONIC_MAGNITUDE"}

    norm = math.sqrt(sum(w * w for w in weights))
    if not math.isfinite(norm) or norm <= 0.0:
        return {"valid": False, "reason": "INVALID_TEMPLATE_NORM"}
    weights = [w / norm for w in weights]

    fundamental_magnitude = observed[0]
    max_harmonic_magnitude = max(observed)
    guard_ratio = (
        0.0
        if max_harmonic_magnitude <= 0.0
        else float(fundamental_magnitude / max_harmonic_magnitude)
    )

    return {
        "valid": True,
        "midi": int(midi),
        "fundamentalBin": fundamental_bin,
        "fundamentalHz": f_hat,
        "bins": bins,
        "weights": weights,
        "observedHarmonicMagnitudes": observed,
        "fundamentalToMaxHarmonicRatio": guard_ratio,
        "fundamentalGuardPassed": guard_ratio >= FUNDAMENTAL_TO_MAX_HARMONIC_MIN,
    }


def _build_dictionary(samples: np.ndarray) -> dict:
    demeaned, rms = _prepare_window(samples)
    if rms < MIN_DEMEANED_RMS:
        return {"status": "INSUFFICIENT_LOW_SUPPORT", "rms": rms}

    windowed = demeaned * np.hanning(WINDOW_SAMPLES)
    magnitude = np.abs(np.fft.rfft(windowed, n=FFT_SIZE))
    frequencies = np.fft.rfftfreq(FFT_SIZE, d=1.0 / float(SAMPLE_RATE))
    if not np.all(np.isfinite(magnitude)):
        raise CorroborationError("NONFINITE_FFT_MAGNITUDE")

    templates: dict[int, dict] = {}
    for midi in range(PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX + 1):
        templates[midi] = _candidate_template(midi, magnitude, frequencies)

    valid_midis = [m for m, t in templates.items() if t.get("valid")]
    if not valid_midis:
        return {"status": "INSUFFICIENT_NO_VALID_TEMPLATES", "rms": rms}

    feature_bins = sorted({b for m in valid_midis for b in templates[m]["bins"]})
    if not feature_bins:
        return {"status": "INSUFFICIENT_NO_FEATURE_BINS", "rms": rms}
    bin_to_row = {b: i for i, b in enumerate(feature_bins)}
    observed = np.asarray([magnitude[b] for b in feature_bins], dtype=np.float64)
    if not np.all(np.isfinite(observed)):
        raise CorroborationError("NONFINITE_FEATURE_VECTOR")

    dictionary = np.zeros((len(feature_bins), len(valid_midis)), dtype=np.float64)
    for col, midi in enumerate(valid_midis):
        template = templates[midi]
        for b, w in zip(template["bins"], template["weights"]):
            dictionary[bin_to_row[b], col] += float(w)

    if not np.all(np.isfinite(dictionary)):
        raise CorroborationError("NONFINITE_DICTIONARY")

    return {
        "status": "OK",
        "rms": rms,
        "magnitude": magnitude,
        "templates": templates,
        "validMidis": valid_midis,
        "featureBins": feature_bins,
        "observed": observed,
        "dictionary": dictionary,
    }


def _fit_view(samples: np.ndarray, selected_midi: int) -> dict:
    built = _build_dictionary(samples)
    if built["status"] != "OK":
        return {
            "status": built["status"],
            "rms": built.get("rms"),
            "selectedMidi": selected_midi,
        }

    templates = built["templates"]
    selected = templates.get(selected_midi)
    if not selected or not selected.get("valid"):
        return {
            "status": "INSUFFICIENT_SELECTED_TEMPLATE_INVALID",
            "rms": built["rms"],
            "selectedMidi": selected_midi,
        }

    observed = built["observed"]
    dictionary = built["dictionary"]
    valid_midis = built["validMidis"]
    energy = float(np.linalg.norm(observed))
    if not math.isfinite(energy) or energy <= 0.0:
        return {
            "status": "INSUFFICIENT_ZERO_FEATURE_ENERGY",
            "rms": built["rms"],
            "selectedMidi": selected_midi,
        }

    try:
        coefficients, full_residual = nnls(dictionary, observed)
    except Exception as exc:  # fail closed; solver exceptions are evidence insufficiency
        return {
            "status": "INSUFFICIENT_NNLS_FULL_FAILED",
            "rms": built["rms"],
            "selectedMidi": selected_midi,
            "errorType": type(exc).__name__,
        }

    selected_col = valid_midis.index(selected_midi)
    reduced = np.delete(dictionary, selected_col, axis=1)
    if reduced.shape[1] == 0:
        return {
            "status": "INSUFFICIENT_REDUCED_DICTIONARY_EMPTY",
            "rms": built["rms"],
            "selectedMidi": selected_midi,
        }
    try:
        _reduced_coefficients, without_residual = nnls(reduced, observed)
    except Exception as exc:
        return {
            "status": "INSUFFICIENT_NNLS_REDUCED_FAILED",
            "rms": built["rms"],
            "selectedMidi": selected_midi,
            "errorType": type(exc).__name__,
        }

    selected_coefficient = float(coefficients[selected_col])
    full_residual = float(full_residual)
    without_residual = float(without_residual)
    necessity_fraction = float((without_residual - full_residual) / energy)
    if not all(
        math.isfinite(v)
        for v in (
            selected_coefficient,
            full_residual,
            without_residual,
            necessity_fraction,
        )
    ):
        return {
            "status": "INSUFFICIENT_NONFINITE_FIT_RESULT",
            "rms": built["rms"],
            "selectedMidi": selected_midi,
        }

    necessity_passed = (
        selected_coefficient > 0.0 and necessity_fraction >= NECESSITY_FRACTION_MIN
    )
    guard_passed = bool(selected["fundamentalGuardPassed"])

    return {
        "status": "OK",
        "rms": built["rms"],
        "selectedMidi": selected_midi,
        "selectedCoefficient": selected_coefficient,
        "fullResidual": full_residual,
        "withoutSelectedResidual": without_residual,
        "featureEnergy": energy,
        "necessityFraction": necessity_fraction,
        "necessityPassed": necessity_passed,
        "fundamentalHz": selected["fundamentalHz"],
        "fundamentalToMaxHarmonicRatio": selected["fundamentalToMaxHarmonicRatio"],
        "fundamentalGuardPassed": guard_passed,
        "passed": bool(necessity_passed and guard_passed),
    }


def classify_audio_event(audio: np.ndarray, onset_sample: int, selected_midi: int) -> dict:
    _check_runtime()
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise CorroborationError("SELECTED_MIDI_INTEGER_REQUIRED")
    selected_midi = int(selected_midi)
    if not PLAYABLE_MIDI_MIN <= selected_midi <= PLAYABLE_MIDI_MAX:
        raise CorroborationError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise CorroborationError("ONSET_SAMPLE_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)

    values = np.asarray(audio, dtype=np.float64)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise CorroborationError("FINITE_MONO_AUDIO_REQUIRED")
    if onset_sample < 0:
        return {
            "classification": CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "views": [],
            "reason": "ONSET_BEFORE_AUDIO",
        }

    views: list[dict] = []
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
        view = _fit_view(values[start:stop], selected_midi)
        view = {"offsetSamples": int(offset), **view}
        views.append(view)
        if view["status"] != "OK":
            return {
                "classification": CLASS_INSUFFICIENT,
                "selectedMidi": selected_midi,
                "views": views,
                "reason": view["status"],
            }

    corroborated = all(bool(view["passed"]) for view in views)
    return {
        "classification": CLASS_CORROBORATED if corroborated else CLASS_NOT_CORROBORATED,
        "selectedMidi": selected_midi,
        "views": views,
        "reason": "ALL_VIEWS_NECESSARY_AND_FUNDAMENTAL_PRESENT" if corroborated else "AT_LEAST_ONE_VIEW_FAILED",
    }


def _synth_note(
    duration_seconds: float,
    notes: list[dict],
    *,
    seed: int = 0,
    attack_noise: float = 0.0,
    noise: float = 0.0,
    temporal_change: dict | None = None,
) -> np.ndarray:
    count = int(round(duration_seconds * SAMPLE_RATE))
    t = np.arange(count, dtype=np.float64) / float(SAMPLE_RATE)
    audio = np.zeros(count, dtype=np.float64)
    for note in notes:
        midi = float(note["midi"])
        amp = float(note.get("amplitude", 1.0))
        cents = float(note.get("cents", 0.0))
        harmonic_amplitudes = note.get("harmonicAmplitudes")
        f0 = midi_to_hz(midi + cents / 100.0)
        if harmonic_amplitudes is None:
            harmonic_amplitudes = [1.0 / float(h) for h in range(1, HARMONIC_COUNT_MAX + 1)]
        for h, h_amp in enumerate(harmonic_amplitudes, start=1):
            freq = f0 * float(h)
            if freq >= SAMPLE_RATE / 2.0:
                break
            audio += amp * float(h_amp) * np.sin(2.0 * math.pi * freq * t)

    if temporal_change:
        change_sample = int(round(float(temporal_change["atSeconds"]) * SAMPLE_RATE))
        if 0 <= change_sample < count:
            replacement = _synth_note(
                duration_seconds - float(temporal_change["atSeconds"]),
                temporal_change["notes"],
                seed=seed + 991,
            )
            audio[change_sample:] = replacement[: count - change_sample]

    rng = np.random.default_rng(seed)
    if attack_noise > 0.0:
        attack_len = min(count, int(round(0.08 * SAMPLE_RATE)))
        envelope = np.linspace(1.0, 0.0, attack_len, endpoint=False)
        audio[:attack_len] += attack_noise * envelope * rng.standard_normal(attack_len)
    if noise > 0.0:
        audio += noise * rng.standard_normal(count)

    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 0.95:
        audio = audio * (0.95 / peak)
    return audio.astype(np.float64, copy=False)


def _fixture_audio(fixture: dict) -> np.ndarray:
    kind = fixture["kind"]
    if kind == "silence":
        return np.zeros(int(round(float(fixture["durationSeconds"]) * SAMPLE_RATE)), dtype=np.float64)
    if kind == "low_noise":
        rng = np.random.default_rng(int(fixture.get("seed", 0)))
        return float(fixture["noiseAmplitude"]) * rng.standard_normal(
            int(round(float(fixture["durationSeconds"]) * SAMPLE_RATE))
        )
    if kind == "harmonic_mix":
        return _synth_note(
            float(fixture["durationSeconds"]),
            list(fixture["notes"]),
            seed=int(fixture.get("seed", 0)),
            attack_noise=float(fixture.get("attackNoise", 0.0)),
            noise=float(fixture.get("noise", 0.0)),
            temporal_change=fixture.get("temporalChange"),
        )
    raise CorroborationError(f"UNKNOWN_FIXTURE_KIND:{kind}")


def run_self_test(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("contract") != "songsterr-fresh-v5-synthetic-fixtures-v1":
        raise CorroborationError("FIXTURE_MANIFEST_CONTRACT_CHANGED")
    rows = []
    counts: dict[str, int] = {}
    for fixture in manifest["fixtures"]:
        audio = _fixture_audio(fixture)
        actual = classify_audio_event(
            audio,
            int(fixture.get("onsetSample", 0)),
            int(fixture["selectedMidi"]),
        )
        expected = fixture["expectedClassification"]
        classification = actual["classification"]
        counts[classification] = counts.get(classification, 0) + 1
        rows.append({
            "id": fixture["id"],
            "expected": expected,
            "actual": classification,
            "audioSha256": sha256_bytes(np.asarray(audio, dtype="<f8").tobytes()),
            "reason": actual.get("reason"),
        })
        if classification != expected:
            raise CorroborationError(
                f"SYNTHETIC_CLASSIFICATION_CHANGED:{fixture['id']}:{classification}!={expected}"
            )
        if actual["selectedMidi"] != int(fixture["selectedMidi"]):
            raise CorroborationError(f"EVENT_MIDI_IDENTITY_CHANGED:{fixture['id']}")

    return {
        "contract": CONTRACT,
        "fixtureContract": manifest["contract"],
        "fixtureCount": len(rows),
        "classificationCounts": dict(sorted(counts.items())),
        "results": rows,
        "policyBoundary": {
            "realCorpusEvaluated": False,
            "protectedSongUsed": False,
            "modelInferenceInvoked": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--fixture-manifest")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        if not args.fixture_manifest:
            raise CorroborationError("SELF_TEST_REQUIRES_FIXTURE_MANIFEST")
        print(canonical_json(run_self_test(Path(args.fixture_manifest))))
        return 0
    raise CorroborationError("NO_STANDALONE_REAL_CORPUS_MODE_AUTHORIZED")


if __name__ == "__main__":
    raise SystemExit(main())
