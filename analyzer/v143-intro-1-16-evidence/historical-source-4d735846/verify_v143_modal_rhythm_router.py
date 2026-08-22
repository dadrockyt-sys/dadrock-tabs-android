from __future__ import annotations

import json
from pathlib import Path

from v143_modal_rhythm_router import RhythmStemBundle, route_normalized_audio


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main() -> None:
    calls: dict[str, list[object]] = {
        "legacy": [],
        "provider": [],
        "pipeline": [],
        "assembler": [],
        "output": [],
    }

    lead_payload = {
        "generatedTab": "LEGACY LEAD TAB",
        "engineVersion": "legacy-lead",
        "events": [{"midi": 64}],
    }
    bass_payload = {
        "generatedTab": "LEGACY BASS TAB",
        "engineVersion": "legacy-bass",
        "events": [{"midi": 40}],
    }

    def legacy(path: str, transcription_type: str):
        calls["legacy"].append((path, transcription_type))
        if transcription_type == "lead":
            return lead_payload
        if transcription_type == "bass":
            return bass_payload
        raise AssertionError("Legacy analyzer must never receive rhythm")

    bundle = RhythmStemBundle(
        candidate_stem_paths=("rhythm-candidate-a.wav", "rhythm-candidate-b.wav"),
        carrier_stem_a_path="carrier-a.wav",
        carrier_stem_b_path="carrier-b.wav",
    )

    def provider(path):
        calls["provider"].append(str(path))
        return bundle

    rhythm_result = object()
    assembly_result = object()

    def pipeline(full_mix, candidate_paths, carrier_a, carrier_b, **kwargs):
        calls["pipeline"].append(
            {
                "fullMix": str(full_mix),
                "candidates": tuple(str(path) for path in candidate_paths),
                "carrierA": str(carrier_a),
                "carrierB": str(carrier_b),
                "kwargs": dict(kwargs),
            }
        )
        return rhythm_result

    def assembler(value):
        calls["assembler"].append(value)
        assert value is rhythm_result
        return assembly_result

    def output_builder(value):
        calls["output"].append(value)
        assert value is assembly_result
        return {
            "generatedTab": "Measure 1\ne|0---|",
            "tuning": "E Standard",
            "tempo": 120.0,
            "timeSignature": "4/4",
            "techniques": [],
            "events": [{"measure": 1, "step": 0, "fret": 0}],
            "noteCount": 1,
            "engineVersion": "v143-reference-free-rhythm-output-v1",
        }

    # Lead and bass must be delegated exactly and must not touch any V143 inputs.
    lead = route_normalized_audio(
        "normalized.wav",
        "lead",
        legacy_analyzer=legacy,
        rhythm_stem_provider=provider,
        rhythm_pipeline=pipeline,
        event_assembler=assembler,
        output_builder=output_builder,
    )
    bass = route_normalized_audio(
        "normalized.wav",
        "bass",
        legacy_analyzer=legacy,
        rhythm_stem_provider=provider,
        rhythm_pipeline=pipeline,
        event_assembler=assembler,
        output_builder=output_builder,
    )
    assert lead is lead_payload
    assert bass is bass_payload
    assert calls["provider"] == []
    assert calls["pipeline"] == []
    assert calls["assembler"] == []
    assert calls["output"] == []

    # Rhythm must bypass legacy analysis and consume the V143 stem contract.
    legacy_count_before = len(calls["legacy"])
    first = route_normalized_audio(
        "normalized.wav",
        "rhythm",
        legacy_analyzer=legacy,
        rhythm_stem_provider=provider,
        rhythm_pipeline=pipeline,
        event_assembler=assembler,
        output_builder=output_builder,
        rhythm_pipeline_kwargs={"predictor": "predictor", "engine": "engine"},
    )
    assert len(calls["legacy"]) == legacy_count_before
    assert calls["provider"] == ["normalized.wav"]
    assert calls["pipeline"][0] == {
        "fullMix": "normalized.wav",
        "candidates": ("rhythm-candidate-a.wav", "rhythm-candidate-b.wav"),
        "carrierA": "carrier-a.wav",
        "carrierB": "carrier-b.wav",
        "kwargs": {"predictor": "predictor", "engine": "engine"},
    }
    assert calls["assembler"] == [rhythm_result]
    assert calls["output"] == [assembly_result]

    routing = first["rhythmRouting"]
    assert routing["mode"] == "v143-reference-free-rhythm-only"
    assert routing["legacyLeadChanged"] is False
    assert routing["legacyBassChanged"] is False
    assert routing["normalizedFullMixTimingSource"] is True
    assert routing["candidateStemCount"] == 2
    assert routing["pairedCarrierStemContractPreserved"] is True
    assert routing["professionalReferenceUsed"] is False
    assert routing["runtimeLabelsRequired"] is False

    # Repeat with fresh call logs must serialize identically.
    second = route_normalized_audio(
        "normalized.wav",
        "rhythm",
        legacy_analyzer=legacy,
        rhythm_stem_provider=provider,
        rhythm_pipeline=pipeline,
        event_assembler=assembler,
        output_builder=output_builder,
        rhythm_pipeline_kwargs={"predictor": "predictor", "engine": "engine"},
    )
    assert canonical(first) == canonical(second)

    # Invalid requests and incomplete stem contracts must fail before V143 runs.
    try:
        route_normalized_audio(
            "normalized.wav",
            "drums",
            legacy_analyzer=legacy,
            rhythm_stem_provider=provider,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid transcription type was accepted")

    def empty_provider(_path):
        return RhythmStemBundle((), "carrier-a.wav", "carrier-b.wav")

    pipeline_calls_before = len(calls["pipeline"])
    try:
        route_normalized_audio(
            Path("normalized.wav"),
            "rhythm",
            legacy_analyzer=legacy,
            rhythm_stem_provider=empty_provider,
            rhythm_pipeline=pipeline,
            event_assembler=assembler,
            output_builder=output_builder,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Empty rhythm candidate stem bundle was accepted")
    assert len(calls["pipeline"]) == pipeline_calls_before

    print("=== V143 MODAL RHYTHM ROUTER VERIFIED ===")
    print("Lead path delegated unchanged: True")
    print("Bass path delegated unchanged: True")
    print("Rhythm path bypasses legacy analyzer: True")
    print("Normalized full mix passed to V143 timing: True")
    print("Candidate stem bundle passed unchanged: True")
    print("Paired carrier-stem contract preserved: True")
    print("V143 event assembly consumed downstream: True")
    print("Production rhythm output adapter consumed: True")
    print("Invalid transcription type rejected: True")
    print("Incomplete stem bundle rejected: True")
    print("Professional reference used: False")
    print("Runtime labels required: False")
    print("Deterministic repeat exact: True")
    print("READY FOR MODAL STEM PROVIDER INTEGRATION: True")


if __name__ == "__main__":
    main()
