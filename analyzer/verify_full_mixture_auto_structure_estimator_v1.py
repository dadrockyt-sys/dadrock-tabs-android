from __future__ import annotations

import json
import os
from pathlib import Path

from full_mixture_auto_structure_estimator_v1 import (
    estimate_full_mixture_structure_v1,
)

SAMPLE_RATE = 4000


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def synth_clicks(
    clicks: list[tuple[float, float]],
    duration_seconds: float,
    sample_rate: int = SAMPLE_RATE,
) -> list[float]:
    samples = [0.0] * int(round(duration_seconds * sample_rate))
    click_length = max(1, int(round(0.008 * sample_rate)))

    for time_seconds, amplitude in clicks:
        start = int(round(time_seconds * sample_rate))
        for offset in range(click_length):
            index = start + offset
            if index >= len(samples):
                break
            envelope = 1.0 - offset / click_length
            samples[index] += float(amplitude) * envelope

    return samples


def beat_train(
    bpm: float,
    beat_count: int,
    *,
    meter: int | None = None,
    downbeat_offset: int = 0,
    strong: float = 1.0,
    weak: float = 0.4,
    equal: bool = False,
) -> tuple[list[float], float]:
    period = 60.0 / bpm
    clicks: list[tuple[float, float]] = []

    for beat_index in range(beat_count):
        if equal or meter is None:
            amplitude = strong
        else:
            amplitude = (
                strong
                if (beat_index - downbeat_offset) % meter == 0
                else weak
            )
        clicks.append((beat_index * period, amplitude))

    duration = beat_count * period + 0.5
    return synth_clicks(clicks, duration), duration


def field_value(result: dict, name: str):
    field = result.get(name)
    return field.get("value") if isinstance(field, dict) else None


results: dict[str, str] = {}

# A1 — silence
silence = [0.0] * (SAMPLE_RATE * 4)
a1 = estimate_full_mixture_structure_v1(silence, SAMPLE_RATE)
assert_true(a1["tempoBpm"] is None, "A1 tempo must remain unresolved")
assert_true(a1["timeSignature"] is None, "A1 meter must remain unresolved")
assert_true(a1["pickupBeats"] is None, "A1 pickup must remain unresolved")
assert_true(a1["feel"] is None, "A1 feel must remain unresolved")
results["A1"] = "PASS"

# A2 — too few clicks
few = synth_clicks([(0.0, 1.0), (0.5, 1.0), (1.0, 1.0)], 2.0)
a2 = estimate_full_mixture_structure_v1(few, SAMPLE_RATE)
assert_true(a2["tempoBpm"] is None, "A2 tempo must remain unresolved with <4 onsets")
results["A2"] = "PASS"

# A3 — 120 BPM quarter notes
samples, _ = beat_train(120.0, 32)
a3 = estimate_full_mixture_structure_v1(samples, SAMPLE_RATE)
a3_bpm = field_value(a3, "tempoBpm")
assert_true(a3_bpm is not None and abs(a3_bpm - 120.0) <= 1.0, f"A3 expected ~120 BPM, got {a3_bpm}")
results["A3"] = "PASS"

# A4 — 90 BPM quarter notes
samples, _ = beat_train(90.0, 28)
a4 = estimate_full_mixture_structure_v1(samples, SAMPLE_RATE)
a4_bpm = field_value(a4, "tempoBpm")
assert_true(a4_bpm is not None and abs(a4_bpm - 90.0) <= 1.0, f"A4 expected ~90 BPM, got {a4_bpm}")
results["A4"] = "PASS"

# A5 — accented 4/4
samples, _ = beat_train(120.0, 40, meter=4)
a5 = estimate_full_mixture_structure_v1(samples, SAMPLE_RATE)
assert_true(field_value(a5, "timeSignature") == {"numerator": 4, "denominator": 4}, f"A5 expected 4/4, got {field_value(a5, 'timeSignature')}")
results["A5"] = "PASS"

# A6 — accented 3/4
samples, _ = beat_train(120.0, 39, meter=3)
a6 = estimate_full_mixture_structure_v1(samples, SAMPLE_RATE)
assert_true(field_value(a6, "timeSignature") == {"numerator": 3, "denominator": 4}, f"A6 expected 3/4, got {field_value(a6, 'timeSignature')}")
results["A6"] = "PASS"

# A7 — unaccented ambiguity must not guess meter
samples, _ = beat_train(120.0, 36, equal=True)
a7 = estimate_full_mixture_structure_v1(samples, SAMPLE_RATE)
assert_true(a7["timeSignature"] is None, f"A7 meter must remain unresolved, got {a7['timeSignature']}")
results["A7"] = "PASS"

# A8 — one-beat pickup before first accented 4/4 downbeat
samples, _ = beat_train(120.0, 40, meter=4, downbeat_offset=1)
a8 = estimate_full_mixture_structure_v1(samples, SAMPLE_RATE)
a8_pickup = field_value(a8, "pickupBeats")
assert_true(a8_pickup is not None and abs(a8_pickup - 1.0) <= 0.15, f"A8 expected ~1 beat pickup, got {a8_pickup}")
results["A8"] = "PASS"

# A9 — straight eighth-note offbeats
period = 60.0 / 120.0
straight_clicks: list[tuple[float, float]] = []
for beat_index in range(24):
    beat_start = beat_index * period
    straight_clicks.append((beat_start, 1.0))
    straight_clicks.append((beat_start + period / 2.0, 0.45))
a9 = estimate_full_mixture_structure_v1(
    synth_clicks(straight_clicks, 24 * period + 0.5),
    SAMPLE_RATE,
)
assert_true(field_value(a9, "feel") == "straight", f"A9 expected straight feel, got {field_value(a9, 'feel')}")
results["A9"] = "PASS"

# A10 — triplet subdivision evidence
triplet_clicks: list[tuple[float, float]] = []
for beat_index in range(24):
    beat_start = beat_index * period
    triplet_clicks.append((beat_start, 1.0))
    triplet_clicks.append((beat_start + period / 3.0, 0.35))
    triplet_clicks.append((beat_start + 2.0 * period / 3.0, 0.35))
a10 = estimate_full_mixture_structure_v1(
    synth_clicks(triplet_clicks, 24 * period + 0.5),
    SAMPLE_RATE,
)
assert_true(field_value(a10, "feel") == "triplet", f"A10 expected triplet feel, got {field_value(a10, 'feel')}")
results["A10"] = "PASS"

# A11 — no offbeat evidence => feel unresolved
samples, _ = beat_train(120.0, 32)
a11 = estimate_full_mixture_structure_v1(samples, SAMPLE_RATE)
assert_true(a11["feel"] is None, f"A11 feel must remain unresolved, got {a11['feel']}")
results["A11"] = "PASS"

# A12 — trusted full-mixture provenance/schema
provenance = a5["provenance"]
assert_true(a5["version"] == 1, "A12 estimator observation version must be 1")
assert_true(provenance["sourceKind"] == "full-mixture", "A12 sourceKind must be full-mixture")
assert_true(provenance["sourceIdentity"] == "request-audio", "A12 sourceIdentity must be request-audio")
assert_true(provenance["referenceBlind"] is True, "A12 referenceBlind must be true")
assert_true(provenance["referenceRuntimeInputUsed"] is False, "A12 referenceRuntimeInputUsed must be false")
serialized = json.dumps(a5, sort_keys=True)
for forbidden in [
    "productionEligible",
    "productionPromotionAuthorized",
    "referenceScoreAuthorized",
]:
    assert_true(forbidden not in serialized, f"A12 estimator must not introduce {forbidden}")
assert_true(a5["diagnostics"]["carrierInputUsed"] is False, "A12 carrier input must remain false")
assert_true(a5["diagnostics"]["transcribedEventInputUsed"] is False, "A12 transcribed event input must remain false")
results["A12"] = "PASS"


evidence = {
    "schemaVersion": 1,
    "gate": "full-mixture-auto-structure-estimator-v1",
    "referenceBlind": True,
    "referenceScoreAuthorized": False,
    "syntheticWaveformsOnly": True,
    "externalAudioAssetsUsed": False,
    "basicPitchEventsUsed": False,
    "separatedCarrierUsed": False,
    "guitarSetRead": False,
    "splitMySongRead": False,
    "goatRestrictedBytesRead": False,
    "modalInvoked": False,
    "gpuUsed": False,
    "routeEstimatorConnected": False,
    "productModified": False,
    "productionModified": False,
    "productionPromotionAuthorized": False,
    "tests": results,
    "passed": all(value == "PASS" for value in results.values()),
}

result_path = os.environ.get("FULL_MIXTURE_STRUCTURE_V1_RESULT_PATH", "").strip()
if result_path:
    path = Path(result_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

print(json.dumps(evidence, indent=2))
print("FULL MIXTURE AUTO STRUCTURE ESTIMATOR V1 A1-A12 VERIFIED")
