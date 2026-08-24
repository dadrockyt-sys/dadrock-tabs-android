from __future__ import annotations

import subprocess

from v143_candidate_sustain_promotion import promote_candidate_sustain_preserving_physical_onset


EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"


def _identity(event):
    return (
        int(event["measure"]),
        int(event["step"]),
        int(event["midi"]),
        int(event["stringIndex"]),
        int(event["fret"]),
        float(event["timeSeconds"]),
    )


def main() -> int:
    physical_onset = 1.60088
    grid_time = 0.6965986394557823
    source = [{
        "measure": 1,
        "step": 3,
        "timeSeconds": grid_time,
        "onsetTime": physical_onset,
        "midi": 52,
        "dominantMidi": 52,
        "stringIndex": 2,
        "stringName": "D",
        "fret": 2,
        "rhythmTechniques": [],
        "rhythmSustainShadow": {
            "durationSeconds": 0.42,
            "durationSteps": 4,
            "attackTimingChanged": False,
            "pitchChanged": False,
        },
    }]
    before_identity = [_identity(event) for event in source]
    promoted = promote_candidate_sustain_preserving_physical_onset(source, 129.19921875)
    assert len(promoted) == len(source), promoted
    assert [_identity(event) for event in promoted] == before_identity, promoted
    event = promoted[0]
    assert abs(float(event["onsetTime"]) - physical_onset) < 1e-12, event
    assert abs(float(event["timeSeconds"]) - grid_time) < 1e-12, event
    assert abs(float(event["start"]) - grid_time) < 1e-12, event
    assert abs(float(event["offsetTime"]) - (physical_onset + 0.42)) < 1e-12, event
    assert abs((float(event["offsetTime"]) - float(event["onsetTime"])) - float(event["duration"])) < 1e-12, event
    sustain = event["rhythmSustain"]
    assert sustain["attackTimingChanged"] is False, sustain
    assert sustain["physicalOnsetPreserved"] is True, sustain
    assert sustain["gridStartUnchanged"] is True, sustain
    assert sustain["professionalReferenceUsed"] is False, sustain
    assert sustain["runtimeLabelsRequired"] is False, sustain

    # Missing physical provenance falls back to grid time rather than inventing
    # a different attack time.
    fallback_source = [dict(source[0])]
    fallback_source[0].pop("onsetTime")
    fallback = promote_candidate_sustain_preserving_physical_onset(fallback_source, 129.19921875)[0]
    assert abs(float(fallback["onsetTime"]) - grid_time) < 1e-12, fallback

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        text=True,
    ).strip()
    assert protected == EXPECTED_PROTECTED_BLOB, protected
    print("V143 candidate sustain physical-onset promotion checker: PASS")
    print({
        "eventCountUnchanged": True,
        "attackIdentityUnchanged": True,
        "gridStartUnchanged": True,
        "physicalOnsetPreserved": True,
        "offsetDurationConsistent": True,
        "protectedPipelineBlob": protected,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
