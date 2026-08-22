from __future__ import annotations

import inspect
from pathlib import Path

from v143_reference_free_rhythm_pipeline import analyze_reference_free_rhythm
from v143_reference_free_timing import ReferenceFreeTimingEstimate


timing = ReferenceFreeTimingEstimate(
    beat_times=(0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0),
    first_beat_in_measure=3,
    downbeat_index_mod4=1,
    tempo_bpm=120.0,
    beat_confidence=0.91,
    bar_confidence=0.84,
    source_sample_rate=44_100,
)
predictor = object()
engine = object()
seen: dict[str, object] = {}


def fake_timing(path):
    seen["mix"] = str(path)
    return timing


def fake_candidates(*, stem_paths, beat_times, predictor, first_beat_in_measure):
    seen["candidate_stems"] = tuple(str(path) for path in stem_paths)
    seen["beat_times"] = tuple(float(value) for value in beat_times)
    seen["predictor"] = predictor
    seen["phase"] = int(first_beat_in_measure)
    return [
        {
            "measure": 1,
            "step": 12,
            "time_seconds": 0.5,
            "dominantMidi": 52,
            "pitchHypotheses": [{"midi": 52, "sourceCount": 2}],
        },
        {
            "measure": 2,
            "step": 0,
            "time_seconds": 1.0,
            "dominantMidi": 55,
            "pitchHypotheses": [{"midi": 55, "sourceCount": 2}],
        },
    ]


def fake_loader(path):
    name = Path(path).name
    seen.setdefault("carrier_stems", []).append(name)
    if name == "carrier-a.wav":
        return [0.1, 0.2], 44_100
    if name == "carrier-b.wav":
        return [0.3, 0.4], 48_000
    raise AssertionError(name)


def fake_v143(candidates, audio_a, sr_a, audio_b, sr_b, scorer):
    assert scorer is engine
    assert (audio_a, sr_a) == ([0.1, 0.2], 44_100)
    assert (audio_b, sr_b) == ([0.3, 0.4], 48_000)
    rows = []
    for index, candidate in enumerate(candidates):
        row = dict(candidate)
        row["v143Score"] = (0.9, 0.1)[index]
        row["v143Rank"] = index + 1
        row["v143Selected"] = index == 0
        rows.append(row)
    return rows


def run():
    return analyze_reference_free_rhythm(
        "normalized-full-mix.wav",
        ("candidate-a.wav", "candidate-b.wav"),
        "carrier-a.wav",
        "carrier-b.wav",
        predictor=predictor,
        engine=engine,
        timing_estimator=fake_timing,
        candidate_detector=fake_candidates,
        stem_loader=fake_loader,
        rhythm_analyzer=fake_v143,
    )


result = run()
assert seen["mix"] == "normalized-full-mix.wav"
assert seen["candidate_stems"] == ("candidate-a.wav", "candidate-b.wav")
assert seen["beat_times"] == timing.beat_times
assert seen["phase"] == 3
assert seen["predictor"] is predictor
assert seen["carrier_stems"][:2] == ["carrier-a.wav", "carrier-b.wav"]
assert result.candidate_count == 2
assert result.selected_count == 1
assert result.selected_rows[0]["dominantMidi"] == 52
assert result.selected_rows[0]["pitchHypotheses"] == [{"midi": 52, "sourceCount": 2}]
assert result.rows[0]["v143Score"] == 0.9
assert result.rows[0]["v143Rank"] == 1
assert result.rows[0]["v143Selected"] is True

payload = result.to_dict()
assert payload["timing"]["tempoBpm"] == 120.0
assert payload["timing"]["timeSignature"] == "4/4"
assert payload["timing"]["firstBeatInMeasure"] == 3
assert payload["timing"]["beatConfidence"] == 0.91
assert payload["timing"]["barConfidence"] == 0.84

names = tuple(inspect.signature(analyze_reference_free_rhythm).parameters)
assert not any("reference" in name.lower() or "label" in name.lower() for name in names)
assert run().to_dict() == result.to_dict()

try:
    analyze_reference_free_rhythm(
        "normalized-full-mix.wav", (), "carrier-a.wav", "carrier-b.wav",
        engine=engine, timing_estimator=fake_timing,
        candidate_detector=fake_candidates, stem_loader=fake_loader,
        rhythm_analyzer=fake_v143,
    )
except ValueError:
    pass
else:
    raise AssertionError("Empty candidate stem list must fail")

try:
    analyze_reference_free_rhythm(
        "normalized-full-mix.wav", ("candidate-a.wav",), "carrier-a.wav", "carrier-b.wav",
        engine=engine, timing_estimator=fake_timing,
        candidate_detector=fake_candidates, stem_loader=fake_loader,
        rhythm_analyzer=lambda candidates, *_args: [dict(row) for row in candidates],
    )
except RuntimeError:
    pass
else:
    raise AssertionError("Missing V143 result fields must fail")

print("=== V143 REFERENCE-FREE RHYTHM PIPELINE VERIFIED ===")
print("Full-mix timing handoff: True")
print("Explicit 4/4 bar-phase handoff: True")
print("Candidate Rhythm stem handoff: True")
print("Paired carrier-stem contract preserved: True")
print("Pitch hypotheses metadata preserved: True")
print("Frozen V143 score/rank/selection outputs preserved: True")
print("Timing confidence propagated: True")
print("Reference/label parameters present: False")
print("Deterministic repeat exact: True")
print("READY FOR NOTES/TECHNIQUES INTEGRATION: True")
