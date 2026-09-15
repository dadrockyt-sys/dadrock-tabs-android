#!/usr/bin/env python3
"""Full prospective synthetic gate suite for V3 physical-template iteration 2.

All fixture spectra are generated deterministically in memory. The harness
collects the complete first-run inventory before returning PASS/FAIL.
"""

from __future__ import annotations

import json
import math

import numpy as np

import physical_template_plausibility_v3 as base
import physical_template_plausibility_v3_iteration2 as iteration2

SEED = 730915


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def fresh_spectrum(background_scale: float) -> np.ndarray:
    if background_scale <= 0.0:
        return np.zeros(base.FFT_SIZE // 2 + 1, dtype=np.float64)
    rng = np.random.default_rng(SEED)
    return np.abs(
        rng.normal(0.0, float(background_scale), size=base.FFT_SIZE // 2 + 1)
    ).astype(np.float64)


def add_harmonic_series(
    spectrum: np.ndarray,
    midi: int,
    amplitudes: list[float],
    *,
    cents: float = 0.0,
) -> None:
    fundamental = base.midi_to_hz(float(midi) + float(cents) / 100.0)
    for harmonic, amplitude in enumerate(amplitudes, start=1):
        target = float(harmonic) * fundamental
        if target >= base.SAMPLE_RATE / 2.0:
            break
        position = target * float(base.FFT_SIZE) / float(base.SAMPLE_RATE)
        center = int(math.floor(position + 0.5))
        amplitude = float(amplitude)
        spectrum[center] += amplitude
        if center - 1 >= 0:
            spectrum[center - 1] += 0.5 * amplitude
        if center + 1 < spectrum.size:
            spectrum[center + 1] += 0.5 * amplitude


def add_nonharmonic_peak(spectrum: np.ndarray, frequency_hz: float, amplitude: float) -> None:
    position = float(frequency_hz) * float(base.FFT_SIZE) / float(base.SAMPLE_RATE)
    center = int(math.floor(position + 0.5))
    spectrum[center] += float(amplitude)


def evaluate_case(
    name: str,
    spectrum: np.ndarray,
    selected_midi: int,
    expected_pass: bool,
    *,
    expected_status: str | None = None,
    expected_veto_owner: int | None = None,
    context: str = "ordinary-in-clip",
    synthetic_pre_context_used: bool | None = None,
) -> dict:
    frequencies = base.expected_frequencies()
    template = base.evaluate_candidate_template(selected_midi, spectrum, frequencies)
    base_composite = base.evaluate_composite_necessity(selected_midi, spectrum, frequencies)
    actual = iteration2.evaluate_owner_aware_composite(selected_midi, spectrum, frequencies)
    return {
        "name": name,
        "kind": "composite",
        "selectedMidi": int(selected_midi),
        "context": context,
        "syntheticPreContextUsed": synthetic_pre_context_used,
        "expectedPass": bool(expected_pass),
        "expectedStatus": expected_status,
        "expectedVetoOwner": expected_veto_owner,
        "template": template,
        "baseComposite": base_composite,
        "actual": actual,
    }


def build_inherited_pass_cases(records: list[dict]) -> None:
    strong = fresh_spectrum(0.002)
    add_harmonic_series(strong, 69, [1.00, 0.55, 0.36, 0.24, 0.17, 0.12])
    records.append(evaluate_case("strong_fundamental_inclip", strong, 69, True))

    weak = fresh_spectrum(0.002)
    add_harmonic_series(weak, 69, [0.03, 1.00, 0.72, 0.48, 0.30, 0.18])
    records.append(evaluate_case("weak_fundamental_bright_inclip", weak, 69, True))

    zero_fundamental = fresh_spectrum(0.002)
    add_harmonic_series(zero_fundamental, 69, [0.00, 1.00, 0.65, 0.45, 0.28, 0.16])
    records.append(evaluate_case("zero_fundamental_upper_support_inclip", zero_fundamental, 69, True))

    clip_start = fresh_spectrum(0.002)
    add_harmonic_series(clip_start, 69, [0.03, 1.00, 0.72, 0.48, 0.30, 0.18])
    records.append(
        evaluate_case(
            "weak_fundamental_clip_start_post_only",
            clip_start,
            69,
            True,
            context="clip-start-post-only",
            synthetic_pre_context_used=False,
        )
    )

    poly_owner = fresh_spectrum(0.002)
    add_harmonic_series(poly_owner, 57, [1.00, 0.60, 0.40, 0.30, 0.20, 0.15])
    add_harmonic_series(poly_owner, 76, [0.15, 1.00, 0.70, 0.45, 0.30, 0.20])
    records.append(evaluate_case("true_polyphony_a3_plus_e5", poly_owner, 76, True))

    dyad = fresh_spectrum(0.002)
    add_harmonic_series(dyad, 69, [1.00, 0.50, 0.32, 0.22, 0.15, 0.10])
    add_harmonic_series(dyad, 71, [0.80, 0.55, 0.35, 0.24, 0.16, 0.11])
    records.append(evaluate_case("true_polyphony_a4_plus_b4_selected_69", dyad, 69, True))
    records.append(evaluate_case("true_polyphony_a4_plus_b4_selected_71", dyad, 71, True))


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
            records.append(
                evaluate_case(
                    f"timbre_{profile_name}_{int(cents):+d}c",
                    spectrum,
                    69,
                    True,
                )
            )


def build_inherited_fail_cases(records: list[dict]) -> None:
    octave_alias = fresh_spectrum(0.002)
    add_harmonic_series(octave_alias, 57, [1.00, 0.60, 0.40, 0.30, 0.20, 0.15])
    records.append(
        evaluate_case(
            "octave_alias_lower_a3_selected_a4",
            octave_alias,
            69,
            False,
            expected_status="LOWER_OWNER_EXPLAINS_SELECTED",
            expected_veto_owner=57,
        )
    )

    third_owner = fresh_spectrum(0.002)
    add_harmonic_series(third_owner, 57, [1.00, 0.60, 0.40, 0.30, 0.20, 0.15])
    records.append(evaluate_case("third_harmonic_owner_a3_selected_e5", third_owner, 76, False))

    two_harmonics = fresh_spectrum(0.002)
    add_harmonic_series(two_harmonics, 69, [0.00, 1.00, 0.80, 0.00, 0.00, 0.00])
    records.append(evaluate_case("two_harmonics_only", two_harmonics, 69, False))

    single_peak = fresh_spectrum(0.002)
    add_harmonic_series(single_peak, 69, [0.00, 1.00, 0.00, 0.00, 0.00, 0.00])
    records.append(evaluate_case("single_peak_only", single_peak, 69, False))

    broadband = fresh_spectrum(0.02)
    records.append(evaluate_case("broadband_noise", broadband, 69, False))

    near_silence = fresh_spectrum(1e-10)
    records.append(evaluate_case("near_silence", near_silence, 69, False))

    impulses = fresh_spectrum(0.002)
    for frequency, amplitude in ((311.0, 1.0), (503.0, 0.8), (911.0, 0.6), (1427.0, 0.4)):
        add_nonharmonic_peak(impulses, frequency, amplitude)
    records.append(evaluate_case("nonharmonic_impulses", impulses, 69, False))

    clip_insufficient = fresh_spectrum(0.002)
    add_harmonic_series(clip_insufficient, 69, [0.00, 0.20, 0.00, 0.00, 0.00, 0.00])
    records.append(
        evaluate_case(
            "clip_start_insufficient_support",
            clip_insufficient,
            69,
            False,
            context="clip-start-post-only",
            synthetic_pre_context_used=False,
        )
    )


def build_new_owner_controls(records: list[dict]) -> None:
    octave_poly = fresh_spectrum(0.002)
    add_harmonic_series(octave_poly, 57, [1.00, 0.60, 0.40, 0.30, 0.20, 0.15])
    add_harmonic_series(octave_poly, 69, [0.35, 0.90, 0.65, 0.48, 0.33, 0.22])
    records.append(evaluate_case("true_octave_polyphony_a3_plus_a4", octave_poly, 69, True))

    weak_owner = fresh_spectrum(0.002)
    add_harmonic_series(weak_owner, 57, [0.04, 0.04, 0.04, 0.04, 0.04, 0.04])
    add_harmonic_series(weak_owner, 69, [1.00, 0.50, 0.32, 0.22, 0.15, 0.10])
    records.append(evaluate_case("weak_lower_a3_plus_a4", weak_owner, 69, True))


def build_fail_closed_input_cases(records: list[dict]) -> None:
    frequencies = base.expected_frequencies()
    valid = fresh_spectrum(0.0)
    add_harmonic_series(valid, 69, [1.0, 0.5, 0.33, 0.25, 0.20, 0.16])

    nonfinite = valid.copy()
    nonfinite[10] = np.nan
    records.append(
        {
            "name": "input_nonfinite",
            "kind": "composite",
            "expectedPass": False,
            "expectedStatus": "NONFINITE_SPECTRUM_OR_FREQUENCY",
            "expectedVetoOwner": None,
            "baseComposite": base.evaluate_composite_necessity(69, nonfinite, frequencies),
            "actual": iteration2.evaluate_owner_aware_composite(69, nonfinite, frequencies),
        }
    )

    records.append(
        {
            "name": "input_shape_mismatch",
            "kind": "composite",
            "expectedPass": False,
            "expectedStatus": "SPECTRUM_FREQUENCY_SHAPE_MISMATCH",
            "expectedVetoOwner": None,
            "baseComposite": base.evaluate_composite_necessity(69, valid, frequencies[:-1]),
            "actual": iteration2.evaluate_owner_aware_composite(69, valid, frequencies[:-1]),
        }
    )

    negative = valid.copy()
    negative[10] = -1.0
    records.append(
        {
            "name": "input_negative",
            "kind": "composite",
            "expectedPass": False,
            "expectedStatus": "NEGATIVE_INNOVATION_NOT_ALLOWED",
            "expectedVetoOwner": None,
            "baseComposite": base.evaluate_composite_necessity(69, negative, frequencies),
            "actual": iteration2.evaluate_owner_aware_composite(69, negative, frequencies),
        }
    )

    records.append(
        {
            "name": "input_missing_frequency_bin",
            "kind": "composite",
            "expectedPass": False,
            "expectedStatus": "FREQUENCY_GRID_MISSING_BINS",
            "expectedVetoOwner": None,
            "baseComposite": base.evaluate_composite_necessity(69, valid[:-1], frequencies[:-1]),
            "actual": iteration2.evaluate_owner_aware_composite(69, valid[:-1], frequencies[:-1]),
        }
    )

    high_anchor = base._anchor_observation(120, 0.0, valid, frequencies)
    records.append(
        {
            "name": "input_fewer_than_three_available_harmonics",
            "kind": "direct-template",
            "expectedValid": False,
            "expectedStatus": "FEWER_THAN_THREE_AVAILABLE_HARMONICS",
            "actual": high_anchor,
        }
    )


def collect_mismatches(records: list[dict]) -> list[dict]:
    mismatches: list[dict] = []
    for record in records:
        name = str(record["name"])
        actual = record.get("actual", {})
        if record["kind"] == "direct-template":
            if actual.get("valid") is not record["expectedValid"]:
                mismatches.append({"name": name, "reason": "VALIDITY_MISMATCH", "actual": actual})
                continue
            if actual.get("status") != record["expectedStatus"]:
                mismatches.append({"name": name, "reason": "STATUS_MISMATCH", "actual": actual})
            continue

        expected_pass = bool(record["expectedPass"])
        observed_pass = actual.get("passed") is True
        if observed_pass != expected_pass:
            mismatches.append(
                {
                    "name": name,
                    "reason": "PASS_FAIL_MISMATCH",
                    "expectedPass": expected_pass,
                    "observedPass": observed_pass,
                    "actualStatus": actual.get("status"),
                }
            )
            continue

        expected_status = record.get("expectedStatus")
        if expected_status is not None and actual.get("status") != expected_status:
            mismatches.append(
                {
                    "name": name,
                    "reason": "STATUS_MISMATCH",
                    "expectedStatus": expected_status,
                    "actualStatus": actual.get("status"),
                }
            )
            continue

        expected_owner = record.get("expectedVetoOwner")
        if expected_owner is not None:
            owners = [int(row.get("ownerMidi")) for row in actual.get("vetoingOwners", [])]
            if int(expected_owner) not in owners:
                mismatches.append(
                    {
                        "name": name,
                        "reason": "EXPECTED_VETO_OWNER_MISSING",
                        "expectedOwner": int(expected_owner),
                        "actualOwners": owners,
                    }
                )
                continue

        base_composite = record.get("baseComposite")
        if isinstance(base_composite, dict) and base_composite.get("passed") is not True and observed_pass:
            mismatches.append({"name": name, "reason": "ILLEGAL_PROMOTION_OF_BASE_FAILURE"})
    return mismatches


def run_fixture_suite() -> dict:
    records: list[dict] = []
    build_inherited_pass_cases(records)
    build_timbre_detuning_matrix(records)
    build_inherited_fail_cases(records)
    build_new_owner_controls(records)
    build_fail_closed_input_cases(records)
    mismatches = collect_mismatches(records)
    return {
        "contract": "songsterr-fresh-v3-physical-template-owner-aware-synthetic-test-v2",
        "seed": SEED,
        "fixtureCount": len(records),
        "mismatchCount": len(mismatches),
        "mismatches": mismatches,
        "fixtures": records,
    }


def main() -> int:
    reports = [run_fixture_suite() for _ in range(3)]
    serializations = [canonical_json(report) for report in reports]
    deterministic = bool(serializations[0] == serializations[1] == serializations[2])
    first = reports[0]
    passed = bool(deterministic and first["mismatchCount"] == 0)
    summary = {
        "contract": first["contract"],
        "fixtureCount": first["fixtureCount"],
        "mismatchCount": first["mismatchCount"],
        "mismatches": first["mismatches"],
        "repetitions": 3,
        "deterministic": deterministic,
        "result": "PASS" if passed else "FAIL",
    }
    print(canonical_json(summary))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
