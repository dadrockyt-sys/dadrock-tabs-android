#!/usr/bin/env python3
"""Frozen prospective synthetic gates for physical_template_plausibility_v3.py.

No repository media, model output, workflow, V6 classifier, network resource, or
external fixture file is read. All spectra are generated deterministically in
memory from the frozen PRE.
"""

from __future__ import annotations

import json
import math

import numpy as np

import physical_template_plausibility_v3 as v3

SEED = 730915


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def fresh_spectrum(background_scale: float) -> np.ndarray:
    if background_scale <= 0.0:
        return np.zeros(v3.FFT_SIZE // 2 + 1, dtype=np.float64)
    rng = np.random.default_rng(SEED)
    return np.abs(
        rng.normal(0.0, float(background_scale), size=v3.FFT_SIZE // 2 + 1)
    ).astype(np.float64)


def add_harmonic_series(
    spectrum: np.ndarray,
    midi: int,
    amplitudes: list[float],
    *,
    cents: float = 0.0,
) -> None:
    fundamental = v3.midi_to_hz(float(midi) + float(cents) / 100.0)
    for harmonic, amplitude in enumerate(amplitudes, start=1):
        target = float(harmonic) * fundamental
        if target >= v3.SAMPLE_RATE / 2.0:
            break
        position = target * float(v3.FFT_SIZE) / float(v3.SAMPLE_RATE)
        center = int(math.floor(position + 0.5))
        amplitude = float(amplitude)
        spectrum[center] += amplitude
        if center - 1 >= 0:
            spectrum[center - 1] += 0.5 * amplitude
        if center + 1 < spectrum.size:
            spectrum[center + 1] += 0.5 * amplitude


def add_nonharmonic_peak(spectrum: np.ndarray, frequency_hz: float, amplitude: float) -> None:
    position = float(frequency_hz) * float(v3.FFT_SIZE) / float(v3.SAMPLE_RATE)
    center = int(math.floor(position + 0.5))
    spectrum[center] += float(amplitude)


def evaluate_case(
    name: str,
    spectrum: np.ndarray,
    selected_midi: int,
    *,
    context: str,
    synthetic_pre_context_used: bool | None = None,
) -> dict:
    frequencies = v3.expected_frequencies()
    template = v3.evaluate_candidate_template(selected_midi, spectrum, frequencies)
    composite = v3.evaluate_composite_necessity(selected_midi, spectrum, frequencies)
    return {
        "name": name,
        "selectedMidi": int(selected_midi),
        "context": context,
        "syntheticPreContextUsed": synthetic_pre_context_used,
        "template": template,
        "composite": composite,
    }


def expect_pass(record: dict) -> None:
    require(record["template"].get("valid") is True, f"{record['name']}: template must be eligible")
    require(record["composite"].get("passed") is True, f"{record['name']}: composite must PASS")


def expect_ineligible_fail(record: dict) -> None:
    require(record["template"].get("valid") is False, f"{record['name']}: template must be ineligible")
    require(record["composite"].get("passed") is False, f"{record['name']}: composite must FAIL")


def expect_composite_fail(record: dict) -> None:
    require(record["composite"].get("passed") is False, f"{record['name']}: composite must FAIL")


def build_pass_cases(records: list[dict]) -> None:
    strong = fresh_spectrum(0.002)
    add_harmonic_series(strong, 69, [1.00, 0.55, 0.36, 0.24, 0.17, 0.12])
    row = evaluate_case("strong_fundamental_inclip", strong, 69, context="ordinary-in-clip")
    expect_pass(row)
    records.append(row)

    weak = fresh_spectrum(0.002)
    add_harmonic_series(weak, 69, [0.03, 1.00, 0.72, 0.48, 0.30, 0.18])
    row = evaluate_case("weak_fundamental_bright_inclip", weak, 69, context="ordinary-in-clip")
    expect_pass(row)
    records.append(row)

    zero_fundamental = fresh_spectrum(0.002)
    add_harmonic_series(zero_fundamental, 69, [0.00, 1.00, 0.65, 0.45, 0.28, 0.16])
    row = evaluate_case(
        "zero_fundamental_upper_support_inclip",
        zero_fundamental,
        69,
        context="ordinary-in-clip",
    )
    expect_pass(row)
    records.append(row)

    clip_start = fresh_spectrum(0.002)
    add_harmonic_series(clip_start, 69, [0.03, 1.00, 0.72, 0.48, 0.30, 0.18])
    row = evaluate_case(
        "weak_fundamental_clip_start_post_only",
        clip_start,
        69,
        context="clip-start-post-only",
        synthetic_pre_context_used=False,
    )
    expect_pass(row)
    records.append(row)

    poly_owner = fresh_spectrum(0.002)
    add_harmonic_series(poly_owner, 57, [1.00, 0.60, 0.40, 0.30, 0.20, 0.15])
    add_harmonic_series(poly_owner, 76, [0.15, 1.00, 0.70, 0.45, 0.30, 0.20])
    row = evaluate_case("true_polyphony_a3_plus_e5", poly_owner, 76, context="ordinary-in-clip")
    expect_pass(row)
    records.append(row)

    dyad = fresh_spectrum(0.002)
    add_harmonic_series(dyad, 69, [1.00, 0.50, 0.32, 0.22, 0.15, 0.10])
    add_harmonic_series(dyad, 71, [0.80, 0.55, 0.35, 0.24, 0.16, 0.11])
    for selected in (69, 71):
        row = evaluate_case(
            f"true_polyphony_a4_plus_b4_selected_{selected}",
            dyad,
            selected,
            context="ordinary-in-clip",
        )
        expect_pass(row)
        records.append(row)


def build_timbre_detuning_matrix(records: list[dict]) -> None:
    profiles = {
        "bright": [0.05, 1.00, 0.80, 0.60, 0.45, 0.30],
        "dark": [1.00, 0.45, 0.22, 0.12, 0.08, 0.05],
        "fundamental_notch": [0.02, 0.85, 0.70, 0.50, 0.12, 0.11],
    }
    for profile_name, amplitudes in profiles.items():
        for cents in (-30.0, 0.0, 30.0):
            spectrum = fresh_spectrum(0.002)
            add_harmonic_series(spectrum, 69, amplitudes, cents=cents)
            name = f"timbre_{profile_name}_{int(cents):+d}c"
            row = evaluate_case(name, spectrum, 69, context="ordinary-in-clip")
            expect_pass(row)
            records.append(row)


def build_fail_cases(records: list[dict]) -> None:
    octave_alias = fresh_spectrum(0.002)
    add_harmonic_series(octave_alias, 57, [1.00, 0.60, 0.40, 0.30, 0.20, 0.15])
    row = evaluate_case(
        "octave_alias_lower_a3_selected_a4",
        octave_alias,
        69,
        context="ordinary-in-clip",
    )
    expect_composite_fail(row)
    records.append(row)

    third_owner = fresh_spectrum(0.002)
    add_harmonic_series(third_owner, 57, [1.00, 0.60, 0.40, 0.30, 0.20, 0.15])
    row = evaluate_case(
        "third_harmonic_owner_a3_selected_e5",
        third_owner,
        76,
        context="ordinary-in-clip",
    )
    expect_composite_fail(row)
    records.append(row)

    two_harmonics = fresh_spectrum(0.002)
    add_harmonic_series(two_harmonics, 69, [0.00, 1.00, 0.80, 0.00, 0.00, 0.00])
    row = evaluate_case("two_harmonics_only", two_harmonics, 69, context="ordinary-in-clip")
    expect_ineligible_fail(row)
    records.append(row)

    single_peak = fresh_spectrum(0.002)
    add_harmonic_series(single_peak, 69, [0.00, 1.00, 0.00, 0.00, 0.00, 0.00])
    row = evaluate_case("single_peak_only", single_peak, 69, context="ordinary-in-clip")
    expect_ineligible_fail(row)
    records.append(row)

    broadband = fresh_spectrum(0.02)
    row = evaluate_case("broadband_noise", broadband, 69, context="ordinary-in-clip")
    expect_ineligible_fail(row)
    records.append(row)

    near_silence = fresh_spectrum(1e-10)
    row = evaluate_case("near_silence", near_silence, 69, context="ordinary-in-clip")
    expect_ineligible_fail(row)
    records.append(row)

    impulses = fresh_spectrum(0.002)
    for frequency, amplitude in ((311.0, 1.0), (503.0, 0.8), (911.0, 0.6), (1427.0, 0.4)):
        add_nonharmonic_peak(impulses, frequency, amplitude)
    row = evaluate_case("nonharmonic_impulses", impulses, 69, context="ordinary-in-clip")
    expect_ineligible_fail(row)
    records.append(row)

    clip_insufficient = fresh_spectrum(0.002)
    add_harmonic_series(clip_insufficient, 69, [0.00, 0.20, 0.00, 0.00, 0.00, 0.00])
    row = evaluate_case(
        "clip_start_insufficient_support",
        clip_insufficient,
        69,
        context="clip-start-post-only",
        synthetic_pre_context_used=False,
    )
    expect_ineligible_fail(row)
    records.append(row)


def build_fail_closed_input_cases(records: list[dict]) -> None:
    frequencies = v3.expected_frequencies()
    valid = fresh_spectrum(0.0)
    add_harmonic_series(valid, 69, [1.0, 0.5, 0.33, 0.25, 0.20, 0.16])

    nonfinite = valid.copy()
    nonfinite[10] = np.nan
    row = v3.evaluate_candidate_template(69, nonfinite, frequencies)
    require(row.get("valid") is False and row.get("status") == "NONFINITE_SPECTRUM_OR_FREQUENCY", "nonfinite must fail closed")
    records.append({"name": "input_nonfinite", "template": row})

    shape_row = v3.evaluate_candidate_template(69, valid, frequencies[:-1])
    require(shape_row.get("valid") is False and shape_row.get("status") == "SPECTRUM_FREQUENCY_SHAPE_MISMATCH", "shape mismatch must fail closed")
    records.append({"name": "input_shape_mismatch", "template": shape_row})

    negative = valid.copy()
    negative[10] = -1.0
    row = v3.evaluate_candidate_template(69, negative, frequencies)
    require(row.get("valid") is False and row.get("status") == "NEGATIVE_INNOVATION_NOT_ALLOWED", "negative innovation must fail closed")
    records.append({"name": "input_negative", "template": row})

    missing = v3.evaluate_candidate_template(69, valid[:-1], frequencies[:-1])
    require(missing.get("valid") is False and missing.get("status") == "FREQUENCY_GRID_MISSING_BINS", "missing bins must fail closed")
    records.append({"name": "input_missing_frequency_bin", "template": missing})

    high_anchor = v3._anchor_observation(120, 0.0, valid, frequencies)
    require(
        high_anchor.get("valid") is False
        and high_anchor.get("status") == "FEWER_THAN_THREE_AVAILABLE_HARMONICS",
        "fewer than three available harmonic orders must fail closed",
    )
    records.append({"name": "input_fewer_than_three_available_harmonics", "template": high_anchor})


def run_fixture_suite() -> dict:
    records: list[dict] = []
    build_pass_cases(records)
    build_timbre_detuning_matrix(records)
    build_fail_cases(records)
    build_fail_closed_input_cases(records)
    return {
        "contract": "songsterr-fresh-v3-physical-template-synthetic-test-v1",
        "seed": SEED,
        "fixtureCount": len(records),
        "fixtures": records,
    }


def main() -> int:
    serializations = [canonical_json(run_fixture_suite()) for _ in range(3)]
    require(serializations[0] == serializations[1] == serializations[2], "full fixture diagnostics must be byte-identical across three repetitions")
    first = json.loads(serializations[0])
    print(
        canonical_json(
            {
                "contract": first["contract"],
                "fixtureCount": first["fixtureCount"],
                "repetitions": 3,
                "deterministic": True,
                "result": "PASS",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
