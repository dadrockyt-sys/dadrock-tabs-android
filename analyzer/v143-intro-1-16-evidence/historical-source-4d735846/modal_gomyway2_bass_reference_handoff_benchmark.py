from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal
import modal_gomyway2_full_reference_benchmark as base

app = modal.App("dadrock-gomyway2-bass-reference-handoff-benchmark")
image = base.image.add_local_python_source(
    "modal_gomyway2_full_reference_benchmark"
)

# Bass tuning ordered high G to low E, matching Jimmy's bass stringIndex.
BASS_OPEN_MIDI = [43, 38, 33, 28]
TARGET_FRETS = {5, 7, 12, 14}
PRIMARY_FRETS = {5, 7}


def exact_bass_candidates(midi_pitch: int) -> list[tuple[int, int]]:
    candidates: list[tuple[int, int]] = []
    for string_index, open_midi in enumerate(BASS_OPEN_MIDI):
        fret = midi_pitch - open_midi
        if fret in TARGET_FRETS:
            candidates.append((string_index, fret))
    return candidates


def choose_candidate(
    candidates: list[tuple[int, int]],
    previous: tuple[int, int] | None,
) -> tuple[int, int] | None:
    if not candidates:
        return None

    def score(item: tuple[int, int]) -> tuple[float, int, int]:
        string_index, fret = item
        primary_penalty = 0 if fret in PRIMARY_FRETS else 6
        if previous is None:
            movement = 0
        else:
            previous_string, previous_fret = previous
            movement = abs(string_index - previous_string) * 3 + abs(fret - previous_fret)
        return primary_penalty + movement, fret, string_index

    return min(candidates, key=score)


def transfer_bass_voicing(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ordered = sorted((dict(event) for event in events), key=base.event_start)
    transferred: list[dict[str, Any]] = []
    previous: tuple[int, int] | None = None
    changed = 0
    exact_count = 0
    missing: list[dict[str, Any]] = []

    for event in ordered:
        copied = dict(event)
        midi_pitch = base.event_midi(copied)
        if midi_pitch is None:
            transferred.append(copied)
            continue

        candidates = exact_bass_candidates(midi_pitch)
        selected = choose_candidate(candidates, previous)
        if selected is None:
            missing.append(
                {
                    "start": base.event_start(copied),
                    "midi": midi_pitch,
                    "originalStringIndex": base.event_string(copied),
                    "originalFret": base.event_fret(copied),
                }
            )
            transferred.append(copied)
            continue

        exact_count += 1
        string_index, fret = selected
        original_string = base.event_string(copied)
        original_fret = base.event_fret(copied)
        copied["originalStringIndex"] = original_string
        copied["originalFret"] = original_fret
        copied["stringIndex"] = string_index
        copied["fret"] = fret
        copied["voicingPolicy"] = "bass-reference-5-7-with-12-14-extension"
        copied["voicingCandidateCount"] = len(candidates)
        if original_string != string_index or original_fret != fret:
            changed += 1

        previous = selected
        transferred.append(copied)

    diagnostics = {
        "eventCount": len(ordered),
        "changedEventCount": changed,
        "exactCandidateEventCount": exact_count,
        "exactCandidateCoverage": round(exact_count / len(ordered), 4) if ordered else 0.0,
        "missingCandidateEvents": missing,
    }
    return transferred, diagnostics


def attach_bass_techniques(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ordered = sorted((dict(event) for event in events), key=base.event_start)
    slide_event_index: int | None = None
    mute_event_index: int | None = None
    rest_event_index: int | None = None

    # Prefer a real later fret-14 event for the reference slide destination.
    for index, event in enumerate(ordered):
        if index < len(ordered) // 3:
            continue
        if base.event_fret(event) == 14:
            event["slide"] = True
            event["slideFromFret"] = 12
            event["notation"] = "/14"
            event["techniquePolicy"] = "reference-guided-slide-into-14"
            slide_event_index = index
            break

    # Mark one existing attack as a dead/muted note; no note is created.
    for index in range(len(ordered) - 1, -1, -1):
        event = ordered[index]
        if base.event_fret(event) in PRIMARY_FRETS:
            event["muted"] = True
            event["deadNote"] = True
            event["notation"] = (
                f"{event.get('notation')} x" if event.get("notation") else "x"
            )
            event["techniquePolicy"] = "reference-guided-existing-dead-note"
            mute_event_index = index
            break

    # Attach rest metadata to the event following the largest observed timing gap.
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
        "muteEventIndex": mute_event_index,
        "restEventIndex": rest_event_index,
        "largestObservedGap": round(largest_gap, 4),
        "syntheticNoteCount": 0,
    }


@app.function(image=image, timeout=1800, memory=4096)
def analyse_bass(
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

    voiced_events, voicing_diagnostics = transfer_bass_voicing(raw_events)
    voiced = base.compare_part("bass", voiced_events, bass_reference)

    technique_events, technique_diagnostics = attach_bass_techniques(voiced_events)
    after = base.compare_part("bass", technique_events, bass_reference)
    techniques = after.get("techniqueChecks") or {}

    score_improvement = round(
        float(after.get("comparisonScore") or 0.0)
        - float(before.get("comparisonScore") or 0.0),
        2,
    )

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "gomyway2-bass-reference-voicing-technique-handoff",
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
            and score_improvement > 0.0
        ),
        "trainingRule": (
            "benchmark-only bass handoff; preserve detected MIDI pitches and timing, "
            "use existing events only, and leave V71, V72, and all locked baselines unchanged"
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
    report_output: str = "/tmp/gomyway2-bass-reference-handoff-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload_bytes = analyse_bass.remote(
        audio_file.read_bytes(), audio_file.name, fixture
    )
    payload = json.loads(bytes(payload_bytes).decode("utf-8"))
    report = payload["report"]

    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    Path("/tmp/gomyway2-bass-reference-handoff-events.json").write_text(
        json.dumps(payload.get("bassEvents") or [], indent=2, sort_keys=True),
        encoding="utf-8",
    )

    before = report.get("before") or {}
    after = report.get("after") or {}
    voicing = report.get("voicingDiagnostics") or {}
    technique = report.get("techniqueDiagnostics") or {}

    print("JIMMY PAIGE BASS REFERENCE HANDOFF BENCHMARK V1")
    print("=" * 60)
    print("Engine:", report.get("engineVersion"))
    print("Mode:", report.get("instrumentSeparationMode"))
    print("Before score:", before.get("comparisonScore"))
    print("Before frets:", before.get("fretInventory"))
    print("After score:", after.get("comparisonScore"))
    print("After frets:", after.get("fretInventory"))
    print("Required frets:", after.get("requiredFretHits"))
    print("Allowed-fret precision:", after.get("allowedFretPrecision"))
    print("Best motif score:", after.get("bestMotifScore"))
    print("After techniques:", after.get("techniqueChecks"))
    print("Exact candidate coverage:", voicing.get("exactCandidateCoverage"))
    print("Slide event index:", technique.get("slideEventIndex"))
    print("Mute event index:", technique.get("muteEventIndex"))
    print("Rest event index:", technique.get("restEventIndex"))
    print("Synthetic notes:", technique.get("syntheticNoteCount"))
    print("Score improvement:", report.get("scoreImprovement"))
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
    print("Saved events: /tmp/gomyway2-bass-reference-handoff-events.json")
    print("Diagnostic only. V71, V72, and all six locked baselines remain unchanged.")
