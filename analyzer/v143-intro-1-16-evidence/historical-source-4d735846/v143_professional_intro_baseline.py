from __future__ import annotations

import json
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

from v143_modal_live_endpoint import app, rhythm_image


REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
DEFAULT_AUDIO_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "baseline-intro-grade.json"
)

INTRO_FIRST_MEASURE = 1
INTRO_LAST_MEASURE = 16

# This image is the same deterministic V143 production stack. The professional
# reference is deliberately NOT mounted into the remote image and is never read
# by the analyzer. It is used only by the local post-run grader.
baseline_image = rhythm_image.add_local_python_source("v143_modal_live_endpoint")


@app.function(
    image=baseline_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def run_current_v143_for_grading(
    source_audio: bytes,
    suffix: str = ".m4a",
) -> dict[str, Any]:
    """Run the current deterministic strict V143 Rhythm stack on real audio."""
    import modal_analyzer as legacy
    from v143_modal_rhythm_router import route_normalized_audio
    from v143_rhythm_bend_consensus import enrich_router_assembly_with_consensus_bends
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )
    from v143_rhythm_legato_evidence import enrich_router_assembly_with_legato

    safe_suffix = str(suffix or ".audio").lower()
    if safe_suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        safe_suffix = ".audio"

    with tempfile.TemporaryDirectory(prefix="v143-prof-grade-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)

        if source.stat().st_size <= 0:
            raise RuntimeError("Professional baseline source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        def legacy_must_not_run(_audio_path: str, _part: str) -> dict[str, Any]:
            raise RuntimeError("Legacy analyzer ran during V143 professional baseline")

        def enrich_strict(assembly: Any, bundle: Any) -> Any:
            with_bends = enrich_router_assembly_with_consensus_bends(assembly, bundle)
            return enrich_router_assembly_with_legato(with_bends, bundle)

        result = route_normalized_audio(
            normalized,
            "rhythm",
            legacy_analyzer=legacy_must_not_run,
            rhythm_stem_provider=build_deterministic_rhythm_stem_bundle,
            assembly_enricher=enrich_strict,
        )

    events = [
        dict(event)
        for event in (result.get("events") or [])
        if isinstance(event, dict)
    ]
    return {
        "success": bool(str(result.get("generatedTab") or "").strip()),
        "events": events,
        "tempo": result.get("tempo"),
        "timeSignature": result.get("timeSignature"),
        "tuning": result.get("tuning"),
        "techniques": list(result.get("techniques") or []),
        "sourceDurationSeconds": source_metadata.get("duration"),
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
        "runtimeLabelsRequired": False,
    }


def _event_int(event: dict[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = event.get(key)
        if value is None:
            continue
        try:
            return int(round(float(value)))
        except (TypeError, ValueError):
            continue
    return None


def _candidate_techniques(event: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    for item in event.get("rhythmTechniques", []) or []:
        if isinstance(item, dict) and item.get("type"):
            values.add(str(item["type"]).strip().lower())
        elif isinstance(item, str):
            values.add(item.strip().lower())
    if event.get("bendSemitones") is not None:
        values.add("bend")
    if event.get("bendRelease") is True:
        values.add("bend-release")
    return values


def _technique_matches(reference: dict[str, Any], candidate: dict[str, Any]) -> bool:
    reference_type = str(reference.get("technique") or "picked-note").strip().lower()
    candidate_types = _candidate_techniques(candidate)

    if "bend" in reference_type:
        expected_amount = _event_int(reference, "bendSemitones")
        actual_amount = _event_int(candidate, "bendSemitones")
        release_required = "release" in reference_type
        return (
            actual_amount == expected_amount
            and (not release_required or candidate.get("bendRelease") is True)
        )

    if reference_type in {"hammer-on", "pull-off", "slide-up", "slide-down"}:
        return reference_type in candidate_types

    if "palm" in reference_type or "mute" in reference_type:
        return bool({"palm-mute", "muted", "mute"} & candidate_types)

    # A normal picked note should not be mislabeled as a bend or legato event.
    special = {
        "bend",
        "bend-release",
        "hammer-on",
        "pull-off",
        "slide-up",
        "slide-down",
    }
    return not bool(candidate_types & special)


def _match_quality(reference: dict[str, Any], candidate: dict[str, Any]) -> tuple[int, ...]:
    reference_midi = _event_int(reference, "midiPitch", "soundingMidiPitch")
    candidate_midi = _event_int(candidate, "midi", "dominantMidi")
    reference_string = _event_int(reference, "stringIndex")
    candidate_string = _event_int(candidate, "stringIndex")
    reference_fret = _event_int(reference, "fret")
    candidate_fret = _event_int(candidate, "fret")
    return (
        int(reference_string == candidate_string and reference_fret == candidate_fret),
        int(reference_midi == candidate_midi),
        int(reference_string == candidate_string),
        int(reference_fret == candidate_fret),
        int(_technique_matches(reference, candidate)),
    )


def _percent(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 100.0
    return round(100.0 * numerator / denominator, 3)


def grade_intro(
    reference_payload: dict[str, Any],
    candidate_events: list[dict[str, Any]],
) -> dict[str, Any]:
    reference_events: list[dict[str, Any]] = []
    reference_by_location: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)

    for measure in reference_payload.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        measure_number = int(measure.get("measureNumber") or 0)
        if not INTRO_FIRST_MEASURE <= measure_number <= INTRO_LAST_MEASURE:
            continue
        for raw_event in measure.get("events", []) or []:
            if not isinstance(raw_event, dict):
                continue
            event = dict(raw_event)
            event["measureNumber"] = measure_number
            step = int(event.get("step") or 0)
            reference_events.append(event)
            reference_by_location[(measure_number, step)].append(event)

    candidates = [
        dict(event)
        for event in candidate_events
        if INTRO_FIRST_MEASURE
        <= int(_event_int(event, "measure", "measureNumber") or 0)
        <= INTRO_LAST_MEASURE
    ]
    candidate_by_location: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for event in candidates:
        measure = int(_event_int(event, "measure", "measureNumber") or 0)
        step = int(_event_int(event, "step", "quantizedStep") or 0)
        candidate_by_location[(measure, step)].append(event)

    location_matches = 0
    pitch_matches = 0
    fret_matches = 0
    string_matches = 0
    duration_matches = 0
    technique_matches = 0
    matched_candidate_ids: set[int] = set()
    mismatch_examples: list[dict[str, Any]] = []

    for reference in reference_events:
        location = (int(reference["measureNumber"]), int(reference.get("step") or 0))
        available = [
            candidate
            for candidate in candidate_by_location.get(location, [])
            if id(candidate) not in matched_candidate_ids
        ]
        if not available:
            if len(mismatch_examples) < 30:
                mismatch_examples.append({
                    "measure": location[0],
                    "step": location[1],
                    "problem": "missing-event",
                    "reference": reference,
                })
            continue

        candidate = max(available, key=lambda item: _match_quality(reference, item))
        matched_candidate_ids.add(id(candidate))
        location_matches += 1

        reference_midi = _event_int(reference, "midiPitch")
        candidate_midi = _event_int(candidate, "midi", "dominantMidi")
        if reference_midi == candidate_midi:
            pitch_matches += 1

        reference_fret = _event_int(reference, "fret")
        candidate_fret = _event_int(candidate, "fret")
        if reference_fret == candidate_fret:
            fret_matches += 1

        reference_string = _event_int(reference, "stringIndex")
        candidate_string = _event_int(candidate, "stringIndex")
        if reference_string == candidate_string:
            string_matches += 1

        reference_duration = _event_int(reference, "durationSteps")
        candidate_duration = _event_int(candidate, "durationSteps")
        if (
            reference_duration is not None
            and candidate_duration is not None
            and abs(reference_duration - candidate_duration) <= 1
        ):
            duration_matches += 1

        if _technique_matches(reference, candidate):
            technique_matches += 1

        if len(mismatch_examples) < 30 and (
            reference_midi != candidate_midi
            or reference_fret != candidate_fret
            or reference_string != candidate_string
            or not _technique_matches(reference, candidate)
        ):
            mismatch_examples.append({
                "measure": location[0],
                "step": location[1],
                "problem": "wrong-note-or-technique",
                "reference": reference,
                "candidate": {
                    "stringIndex": candidate_string,
                    "fret": candidate_fret,
                    "midi": candidate_midi,
                    "durationSteps": candidate_duration,
                    "bendSemitones": candidate.get("bendSemitones"),
                    "bendRelease": candidate.get("bendRelease"),
                    "techniques": sorted(_candidate_techniques(candidate)),
                },
            })

    reference_voicings = {
        location: events
        for location, events in reference_by_location.items()
        if len(events) >= 2
    }
    voicing_matches = 0
    for location, reference_group in reference_voicings.items():
        expected = sorted(
            (
                int(_event_int(event, "stringIndex") or 0),
                int(_event_int(event, "fret") or 0),
            )
            for event in reference_group
        )
        actual = sorted(
            (
                int(_event_int(event, "stringIndex") or 0),
                int(_event_int(event, "fret") or 0),
            )
            for event in candidate_by_location.get(location, [])
        )
        if actual == expected:
            voicing_matches += 1

    total_reference = len(reference_events)
    matched_candidate_count = len(matched_candidate_ids)
    extra_candidate_count = max(0, len(candidates) - matched_candidate_count)

    scores = {
        "onsetStepRecall": _percent(location_matches, total_reference),
        "pitch": _percent(pitch_matches, total_reference),
        "fret": _percent(fret_matches, total_reference),
        "string": _percent(string_matches, total_reference),
        "duration": _percent(duration_matches, total_reference),
        "technique": _percent(technique_matches, total_reference),
        "voicing": _percent(voicing_matches, len(reference_voicings)),
        "candidatePrecision": _percent(matched_candidate_count, len(candidates)),
    }

    weights = {
        "onsetStepRecall": 0.18,
        "pitch": 0.18,
        "fret": 0.14,
        "string": 0.14,
        "duration": 0.10,
        "technique": 0.10,
        "voicing": 0.10,
        "candidatePrecision": 0.06,
    }
    composite = round(
        sum(scores[name] * weight for name, weight in weights.items()),
        3,
    )

    gate = (
        composite >= 90.0
        and scores["onsetStepRecall"] >= 90.0
        and scores["pitch"] >= 90.0
        and scores["fret"] >= 85.0
        and scores["string"] >= 85.0
        and scores["technique"] >= 85.0
        and scores["voicing"] >= 80.0
        and scores["candidatePrecision"] >= 90.0
    )

    return {
        "graderVersion": 1,
        "scope": "professional-measures-1-16",
        "referenceEventCount": total_reference,
        "candidateEventCount": len(candidates),
        "matchedAtExactMeasureStep": location_matches,
        "extraCandidateEventCount": extra_candidate_count,
        "referenceVoicingLocationCount": len(reference_voicings),
        "scoresPercent": scores,
        "compositePercent": composite,
        "readyForMusicalPromotion": gate,
        "mismatchExamples": mismatch_examples,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedByOfflineGrader": True,
        "runtimeLabelsRequired": False,
    }


@app.local_entrypoint()
def main(
    audio_path: str = str(DEFAULT_AUDIO_PATH),
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Audio file missing or empty: {source}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Professional reference missing: {REFERENCE_PATH}")

    payload = source.read_bytes()
    if len(payload) / (1024 * 1024) >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print("Running CURRENT deterministic V143 against real audio...")
    analysis = run_current_v143_for_grading.remote(payload, source.suffix)
    if analysis.get("success") is not True:
        raise RuntimeError("Current V143 returned no generated tab")

    # The protected human reference is loaded only after the audio analysis has
    # finished. It cannot affect separation, timing, V143 selection, mapping, or
    # technique detection.
    reference = json.loads(REFERENCE_PATH.read_text())
    grade = grade_intro(reference, list(analysis.get("events") or []))
    report = {
        "analysis": {
            "tempo": analysis.get("tempo"),
            "timeSignature": analysis.get("timeSignature"),
            "tuning": analysis.get("tuning"),
            "totalEventCount": len(analysis.get("events") or []),
            "techniques": analysis.get("techniques"),
            "referenceFree": analysis.get("referenceFree") is True,
        },
        "grade": grade,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, default=str) + "\n")

    print()
    print("=== V143 PROFESSIONAL INTRO BASELINE ===")
    print(f"Reference events: {grade['referenceEventCount']}")
    print(f"Candidate events in measures 1-16: {grade['candidateEventCount']}")
    for name, value in grade["scoresPercent"].items():
        print(f"{name}: {value:.3f}%")
    print(f"COMPOSITE: {grade['compositePercent']:.3f}%")
    print(f"READY FOR MUSICAL PROMOTION: {grade['readyForMusicalPromotion']}")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")

    if analysis.get("professionalReferenceUsedByAnalyzer") is not False:
        raise RuntimeError("Professional reference leaked into analyzer runtime")
    if grade.get("professionalReferenceUsedByAnalyzer") is not False:
        raise RuntimeError("Professional reference leaked into analyzer runtime")


if __name__ == "__main__":
    main()
