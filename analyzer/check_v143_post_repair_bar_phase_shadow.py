from __future__ import annotations

import math
import subprocess

import numpy as np

from v143_post_repair_bar_phase_shadow import assess_post_repair_bar_phase_from_samples
from v143_reference_free_beat_grid_repair import repair_reference_free_beat_grid_from_samples
from v143_reference_free_timing import ReferenceFreeTimingEstimate


EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"


def _add_click(
    audio: np.ndarray,
    sample_rate: int,
    beat_time: float,
    *,
    amplitude: float,
    frequency: float,
) -> None:
    start = int(round(float(beat_time) * sample_rate))
    length = int(round(0.10 * sample_rate))
    x = np.arange(length, dtype=np.float64) / float(sample_rate)
    envelope = np.exp(-x * 34.0)
    pulse = float(amplitude) * np.sin(2.0 * math.pi * float(frequency) * x) * envelope
    hi = min(len(audio), start + length)
    if hi > start:
        audio[start:hi] += pulse[: hi - start]


def _corrupted_index_fixture(sample_rate: int = 22050):
    period = 0.5
    true_beats = [0.5 + index * period for index in range(64)]
    duration = true_beats[-1] + 0.35
    audio = np.zeros(int(math.ceil(duration * sample_rate)), dtype=np.float64)
    for index, beat_time in enumerate(true_beats):
        phase = index % 4
        if phase == 0:
            amplitude = 1.35
            frequency = 82.0
        elif phase == 2:
            amplitude = 0.78
            frequency = 164.0
        else:
            amplitude = 0.56
            frequency = 246.0
        _add_click(
            audio,
            sample_rate,
            beat_time,
            amplitude=amplitude,
            frequency=frequency,
        )

    # One false sub-beat early in the sequence shifts raw sequence_index % 4 for
    # every later physical beat. The test encodes only that generic indexing
    # corruption; the post-repair recovery itself must still come from audio.
    raw_beats = list(true_beats)
    raw_beats.append(true_beats[8] + 0.25)
    raw_beats.sort()
    return audio, sample_rate, true_beats, raw_beats


def main() -> int:
    audio, sample_rate, true_beats, raw_beats = _corrupted_index_fixture()

    # Before the false pulse, physical downbeats are raw residue 0. After one
    # insertion, all later physical downbeats become raw residue 1. This proves
    # that a phase tied to raw list indices can become stale when repair removes
    # an inserted pulse, without relying on any song or reference labels.
    pre_insert_downbeats = [true_beats[index] for index in range(0, 9, 4)]
    post_insert_downbeats = [true_beats[index] for index in range(12, 64, 4)]
    assert {raw_beats.index(value) % 4 for value in pre_insert_downbeats} == {0}
    assert {raw_beats.index(value) % 4 for value in post_insert_downbeats} == {1}

    inherited_phase = 1
    inherited_first = (-inherited_phase) % 4
    timing = ReferenceFreeTimingEstimate(
        beat_times=tuple(raw_beats),
        first_beat_in_measure=inherited_first,
        downbeat_index_mod4=inherited_phase,
        tempo_bpm=120.0,
        beat_confidence=0.9,
        bar_confidence=0.2,
        source_sample_rate=sample_rate,
    )
    repaired = repair_reference_free_beat_grid_from_samples(
        audio,
        sample_rate,
        timing,
    )
    repair_diag = repaired.diagnostics()
    assert repaired.repaired_interval_outlier_count == 0, repair_diag
    assert repaired.timing.downbeat_index_mod4 == inherited_phase
    assert repaired.timing.first_beat_in_measure == inherited_first
    assert len(repaired.repaired_beat_times) >= len(true_beats) - 1, repair_diag
    assert max(
        abs(float(repaired_time) - float(true_time))
        for repaired_time, true_time in zip(repaired.repaired_beat_times[:56], true_beats[:56])
    ) < 0.12, repair_diag

    assessment = assess_post_repair_bar_phase_from_samples(
        audio,
        sample_rate,
        repaired.repaired_beat_times,
        inherited_downbeat_index_mod4=repaired.timing.downbeat_index_mod4,
    )
    diag = assessment.diagnostics()
    assert assessment.preferred_downbeat_index_mod4 == 0, diag
    assert assessment.preferred_first_beat_in_measure == 0, diag
    assert assessment.robust_preference is True, diag
    assert assessment.phase_change_recommended is True, diag
    assert assessment.preferred_downbeat_index_mod4 != repaired.timing.downbeat_index_mod4, diag
    assert diag["referenceFree"] is True
    assert diag["runtimeLabelsRequired"] is False
    assert diag["productionModified"] is False

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        text=True,
    ).strip()
    assert protected == EXPECTED_PROTECTED_BLOB, protected

    print("V143 post-repair bar phase synthetic shadow: PASS")
    print({
        "inheritedPhase": inherited_phase,
        "repair": repair_diag,
        "postRepairPhase": diag,
        "protectedPipelineBlob": protected,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
