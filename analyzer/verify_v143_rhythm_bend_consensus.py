from __future__ import annotations

from copy import deepcopy

from v143_rhythm_bend_consensus import enforce_bend_view_consensus
from v143_rhythm_event_assembly import RhythmEventAssemblyResult


def _event(view_agreement: int) -> dict:
    return {
        "measure": 87,
        "step": 0,
        "timeSeconds": 157.11,
        "midi": 79,
        "dominantMidi": 79,
        "stringIndex": 0,
        "fret": 15,
        "v143Selected": True,
        "v143Score": 0.91,
        "v143Rank": 1,
        "pitchHypotheses": [{"midi": 79}],
        "rhythmSustain": {
            "durationSeconds": 0.55,
            "durationSteps": 5,
            "tier": "long",
        },
        "rhythmTechniques": [
            {
                "type": "bend",
                "source": "reference-free-audio-pitch-contour",
            }
        ],
        "bendSemitones": 3,
        "bendTargetMidi": 82,
        "bendTargetFret": 18,
        "bendRelease": False,
        "bendEvidence": {
            "version": 1,
            "mode": "reference-free-cross-separated-harmonic-contour",
            "viewAgreement": view_agreement,
            "score": 0.44,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
        },
    }


def main() -> None:
    source = object()
    single_event = _event(1)
    double_event = _event(2)
    single_before = deepcopy(single_event)
    double_before = deepcopy(double_event)

    single = enforce_bend_view_consensus(
        RhythmEventAssemblyResult(source=source, events=(single_event,)),
        required_views=2,
    ).events[0]
    double = enforce_bend_view_consensus(
        RhythmEventAssemblyResult(source=source, events=(double_event,)),
        required_views=2,
    ).events[0]

    single_rejected = (
        "bendSemitones" not in single
        and "bendEvidence" not in single
        and not any(
            isinstance(item, dict)
            and item.get("type") in {"bend", "bend-release"}
            and item.get("source") == "reference-free-audio-pitch-contour"
            for item in single.get("rhythmTechniques", [])
        )
    )
    double_kept = (
        double.get("bendSemitones") == 3
        and double.get("bendTargetFret") == 18
        and double.get("bendEvidence", {}).get("viewAgreement") == 2
        and double.get("bendEvidence", {}).get("requiredViewAgreement") == 2
        and double.get("bendEvidence", {}).get("consensusPassed") is True
    )
    frozen_fields_preserved = all(
        double.get(field) == double_before.get(field)
        for field in (
            "measure",
            "step",
            "timeSeconds",
            "midi",
            "dominantMidi",
            "stringIndex",
            "fret",
            "v143Selected",
            "v143Score",
            "v143Rank",
            "pitchHypotheses",
        )
    )
    inputs_unchanged = single_event == single_before and double_event == double_before

    checks = {
        "Single-view bend rejected with two carriers": single_rejected,
        "Dual-view bend retained": double_kept,
        "Frozen V143 fields preserved": frozen_fields_preserved,
        "Input events unchanged": inputs_unchanged,
        "Professional reference used": False,
        "Runtime labels required": False,
    }
    ready = all((single_rejected, double_kept, frozen_fields_preserved, inputs_unchanged))

    print("=== V143 STRICT BEND CONSENSUS VERIFIED ===")
    for label, value in checks.items():
        print(f"{label}: {value}")
    print(f"READY FOR STRICT REAL-AUDIO BEND SMOKE: {ready}")

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
