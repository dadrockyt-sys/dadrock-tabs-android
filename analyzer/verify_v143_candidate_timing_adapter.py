from __future__ import annotations

from typing import Any

from v143_candidate_timing_adapter import (
    PRODUCTION_SWEEPS,
    build_subdivision_grid,
    detect_candidate_slots,
)
from v143_rhythm_runtime import normalize_candidate_slots


CALLS: list[dict[str, Any]] = []


def fake_predict(path: str, **kwargs: Any) -> tuple[dict[str, Any], None, list[Any]]:
    CALLS.append({"path": path, **kwargs})
    if "stem-a" in path:
        events: list[Any] = [
            (1.006, 1.250, 52, 0.80),
            (1.120, 1.340, 55, 0.70),
            (1.129, 1.360, 57, 0.60),
            (3.004, 3.300, 64, 0.90),
            (1.250, 1.400, 30, 0.99),
            (10.000, 10.100, 60, 0.99),
        ]
    else:
        events = [
            {
                "start_time": 1.002,
                "end_time": 1.280,
                "pitch_midi": 52,
                "amplitude": 0.85,
            },
            {
                "startTime": 1.124,
                "endTime": 1.330,
                "midi": 55,
                "confidence": 0.75,
            },
            (3.000, 3.260, 64, 0.88),
        ]
    return {}, None, events


def main() -> None:
    beats = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
    grid = build_subdivision_grid(beats)
    assert len(grid) == 24
    assert (grid[0].measure, grid[0].step, grid[0].time_seconds) == (1, 0, 1.0)
    assert (grid[1].measure, grid[1].step, grid[1].time_seconds) == (1, 1, 1.125)
    assert (grid[15].measure, grid[15].step, grid[15].time_seconds) == (1, 15, 2.875)
    assert (grid[16].measure, grid[16].step, grid[16].time_seconds) == (2, 0, 3.0)

    shifted = build_subdivision_grid(beats, first_beat_in_measure=2)
    assert (shifted[0].measure, shifted[0].step) == (1, 8)
    assert (shifted[8].measure, shifted[8].step) == (2, 0)

    rows = detect_candidate_slots(
        ["/tmp/stem-a.wav", "/tmp/stem-b.wav"],
        beats,
        predictor=fake_predict,
    )

    assert [(row["measure"], row["step"]) for row in rows] == [
        (1, 0),
        (1, 1),
        (2, 0),
    ]
    assert rows[0]["time_seconds"] == 1.0
    assert rows[0]["time_seconds"] != rows[0]["pitchHypotheses"][0]["bestOnsetTime"]
    assert rows[0]["candidatePitchCount"] == 1
    assert rows[0]["sourceCount"] == 2
    assert rows[0]["dominantMidi"] == 52

    assert rows[1]["candidatePitchCount"] == 2
    assert rows[1]["dominantMidi"] == 55
    pitches = [hypothesis["midi"] for hypothesis in rows[1]["pitchHypotheses"]]
    assert pitches == [55, 57]
    assert rows[1]["pitchHypotheses"][0]["sourceCount"] == 2
    assert rows[1]["pitchHypotheses"][1]["sourceCount"] == 1

    assert rows[2]["time_seconds"] == 3.0
    assert rows[2]["dominantMidi"] == 64

    assert len(PRODUCTION_SWEEPS) == 1
    assert len(CALLS) == 2
    for call in CALLS:
        assert abs(float(call["onset_threshold"]) - 0.15) < 1e-12
        assert abs(float(call["frame_threshold"]) - 0.10) < 1e-12
        assert float(call["minimum_note_length"]) == 20.0
        assert float(call["minimum_frequency"]) == 80.0
        assert float(call["maximum_frequency"]) == 1400.0

    normalized = normalize_candidate_slots(rows)
    assert len(normalized) == len(rows)
    assert normalized[0].measure == 1
    assert normalized[0].step == 0
    assert normalized[0].time_seconds == 1.0
    assert normalized[0].metadata["dominantMidi"] == 52

    forbidden = ("label", "professionalReference", "reference")
    for row in rows:
        assert all(key not in row for key in forbidden)

    print("=== V143 GENERIC CANDIDATE/TIMING ADAPTER VERIFIED ===")
    print("Reference-free beat grid: True")
    print("4/4 sixteenth-note within-measure mapping: True")
    print("Explicit bar-phase support: True")
    print("Basic Pitch event parsing: True")
    print("Guitar MIDI filtering: True")
    print("100 ms maximum grid-error gate: True")
    print("Unique rhythmic-slot collapse: True")
    print("Pitch hypotheses retained as metadata: True")
    print("V143 patch time uses quantized grid time: True")
    print("Direct V143 runtime row compatibility: True")
    print("Production Basic Pitch sweeps:", len(PRODUCTION_SWEEPS))
    print("Synthetic candidate slots:", len(rows))
    print("Professional reference used: False")
    print("Runtime labels required: False")
    print("READY FOR REFERENCE-FREE BEAT/DOWNBEAT ESTIMATOR: True")


if __name__ == "__main__":
    main()
