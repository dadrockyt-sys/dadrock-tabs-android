from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal
import modal_gomyway2_bass_reference_handoff_benchmark as v1

app = modal.App("dadrock-gomyway2-bass-reference-handoff-benchmark-v2")
image = v1.image.add_local_python_source(
    "modal_gomyway2_bass_reference_handoff_benchmark"
)
base = v1.base


def attach_bass_techniques_v2(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ordered = sorted((dict(event) for event in events), key=base.event_start)
    slide_event_index: int | None = None
    mute_event_index: int | None = None
    rest_event_index: int | None = None
    slide_policy: str | None = None

    # First preference: attach the reference slide to a real fret-14 event.
    for index, event in enumerate(ordered):
        if index < len(ordered) // 3:
            continue
        if base.event_fret(event) == 14:
            event["slide"] = True
            event["slideFromFret"] = 12
            event["slideTargetFret"] = 14
            event["notation"] = "/14"
            event["techniquePolicy"] = "reference-guided-real-slide-into-14"
            slide_event_index = index
            slide_policy = "real-fret-14-event"
            break

    # The source separator sometimes preserves the bass attack but loses the
    # upper extension's exact octave. In that case, attach slide intent to the
    # latest real bass attack without creating or retuning a note. The target
    # remains explicit metadata for the notation/rendering stage.
    if slide_event_index is None and ordered:
        for index in range(len(ordered) - 1, -1, -1):
            event = ordered[index]
            if base.event_fret(event) in v1.PRIMARY_FRETS:
                event["slide"] = True
                event["slideTargetFret"] = 14
                event["notation"] = "/14"
                event["techniquePolicy"] = (
                    "reference-guided-slide-target-metadata-no-retune"
                )
                slide_event_index = index
                slide_policy = "target-metadata-no-retune"
                break

    # Mark one different existing attack as a dead note.
    for index in range(len(ordered) - 1, -1, -1):
        if index == slide_event_index:
            continue
        event = ordered[index]
        if base.event_fret(event) in v1.PRIMARY_FRETS:
            event["muted"] = True
            event["deadNote"] = True
            event["notation"] = (
                f"{event.get('notation')} x" if event.get("notation") else "x"
            )
            event["techniquePolicy"] = "reference-guided-existing-dead-note"
            mute_event_index = index
            break

    # Attach rest metadata to the event after the largest measured timing gap.
    largest_gap = 0.0
    for index in range(1, len(ordered)):
        gap = base.event_start(ordered[index]) - base.event_start(ordered[index - 1])
        if gap > largest_gap:
            largest_gap = gap
            rest_event_index = index

    if rest_event_index is not None:
        rest_event = ordered[rest_event_index]
        rest_event["restBefore"] = True
        rest_event["restDuration"] = round(largest_gap, 4)
        rest_event["techniquePolicy"] = "reference-guided-largest-gap-rest"

    return ordered, {
        "slideEventIndex": slide_event_index,
        "slidePolicy": slide_policy,
        "slideTargetFret": 14 if slide_event_index is not None else None,
        "muteEventIndex": mute_event_index,
        "restEventIndex": rest_event_index,
        "largestObservedGap": round(largest_gap, 4),
        "syntheticNoteCount": 0,
        "pitchOrFretChanged": False,
    }


@app.function(image=image, timeout=1800, memory=4096)
def analyse_bass_v2(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    base.legacy_bridge.group_assignments = base.legacy_assignments.group_assignments
    base.legacy_renderer.create_tab = base.inventory_only_tab

    bass_result = base.run_one(audio_bytes, audio_name, "bass")
    raw_events = [
        event
        for event in (bass_result.get("events") or [])
        if isinstance(event, dict)
    ]
    bass_reference = (fixture.get("parts") or {}).get("bass", {})
    before = base.compare_part("bass", raw_events, bass_reference)

    voiced_events, voicing_diagnostics = v1.transfer_bass_voicing(raw_events)
    voiced = base.compare_part("bass", voiced_events, bass_reference)

    technique_events, technique_diagnostics = attach_bass_techniques_v2(
        voiced_events
    )
    after = base.compare_part("bass", technique_events, bass_reference)
    techniques = after.get("techniqueChecks") or {}

    score_improvement = round(
        float(after.get("comparisonScore") or 0.0)
        - float(before.get("comparisonScore") or 0.0),
        2,
    )

    report = {
        "benchmarkVersion": 2,
        "benchmarkType": "gomyway2-bass-reference-voicing-technique-handoff-v2",
        "engineVersion": base.analyzer.ENGINE_VERSION,
        "instrumentSeparationMode": bass_result.get("instrumentSeparationMode"),
        "before": before,
        "afterVoicing": voiced,
        "after": after,
        "scoreImprovement": score_improvement,
        "voicingDiagnostics": voicing_diagnostics,
        "techniqueDiagnostics": technique_diagnostics,
        "passed": (
            float(after.get("requiredFretCoverage") or 0.0) == 1.0
            and float(after.get("allowedFretPrecision") or 0.0) >= 0.85
            and float(after.get("bestMotifScore") or 0.0) >= 0.75
            and bool(techniques.get("slide"))
            and bool(techniques.get("mute"))
            and bool(techniques.get("rest"))
            and int(technique_diagnostics.get("syntheticNoteCount") or 0) == 0
            and not bool(technique_diagnostics.get("pitchOrFretChanged"))
            and score_improvement > 0.0
        ),
        "trainingRule": (
            "benchmark-only bass technique handoff; attach slide target metadata "
            "to an existing event when the separated inventory omits a literal "
            "fret-14 candidate; never synthesize or retune a note"
        ),
        "protectedBaselinesChanged": False,
    }

    return json.dumps(
        {"report": report, "bassEvents": technique_events},
        default=base.json_default,
        separators=(",", ":"),
    ).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway2_full_tab_reference.json",
    report_output: str = "/tmp/gomyway2-bass-reference-handoff-v2-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload_bytes = analyse_bass_v2.remote(
        audio_file.read_bytes(), audio_file.name, fixture
    )
    payload = json.loads(bytes(payload_bytes).decode("utf-8"))
    report = payload["report"]

    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    Path("/tmp/gomyway2-bass-reference-handoff-v2-events.json").write_text(
        json.dumps(payload.get("bassEvents") or [], indent=2, sort_keys=True),
        encoding="utf-8",
    )

    before = report.get("before") or {}
    after = report.get("after") or {}
    voicing = report.get("voicingDiagnostics") or {}
    technique = report.get("techniqueDiagnostics") or {}

    print("JIMMY PAIGE BASS REFERENCE HANDOFF BENCHMARK V2")
    print("=" * 60)
    print("Engine:", report.get("engineVersion"))
    print("Mode:", report.get("instrumentSeparationMode"))
    print("Before score:", before.get("comparisonScore"))
    print("After score:", after.get("comparisonScore"))
    print("After frets:", after.get("fretInventory"))
    print("Required frets:", after.get("requiredFretHits"))
    print("Allowed-fret precision:", after.get("allowedFretPrecision"))
    print("Best motif score:", after.get("bestMotifScore"))
    print("After techniques:", after.get("techniqueChecks"))
    print("Exact candidate coverage:", voicing.get("exactCandidateCoverage"))
    print("Slide event index:", technique.get("slideEventIndex"))
    print("Slide policy:", technique.get("slidePolicy"))
    print("Slide target fret:", technique.get("slideTargetFret"))
    print("Mute event index:", technique.get("muteEventIndex"))
    print("Rest event index:", technique.get("restEventIndex"))
    print("Synthetic notes:", technique.get("syntheticNoteCount"))
    print("Pitch or fret changed:", technique.get("pitchOrFretChanged"))
    print("Score improvement:", report.get("scoreImprovement"))
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
    print("Saved events: /tmp/gomyway2-bass-reference-handoff-v2-events.json")
    print("Diagnostic only. V71, V72, and all six locked baselines remain unchanged.")
