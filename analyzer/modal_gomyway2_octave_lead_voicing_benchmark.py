from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal
import modal_gomyway2_full_reference_benchmark as base

app = modal.App("dadrock-gomyway2-octave-lead-voicing-benchmark")
image = base.image.add_local_python_source(
    "modal_gomyway2_full_reference_benchmark"
)

# Standard guitar tuning from high E to low E, matching Jimmy's stringIndex order.
GUITAR_OPEN_MIDI = [64, 59, 55, 50, 45, 40]
TARGET_FRETS = {12, 14}


def event_midi(event: dict[str, Any]) -> int | None:
    return base.event_midi(event)


def event_fret(event: dict[str, Any]) -> int | None:
    return base.event_fret(event)


def event_string(event: dict[str, Any]) -> int | None:
    return base.event_string(event)


def exact_twelfth_position_candidates(midi_pitch: int) -> list[tuple[int, int]]:
    candidates: list[tuple[int, int]] = []
    for string_index, open_midi in enumerate(GUITAR_OPEN_MIDI):
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
    if previous is None:
        return min(candidates, key=lambda item: (item[1], item[0]))

    previous_string, previous_fret = previous
    return min(
        candidates,
        key=lambda item: (
            abs(item[0] - previous_string) * 3
            + abs(item[1] - previous_fret),
            item[1],
            item[0],
        ),
    )


def transfer_octave_lead_voicing(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ordered = sorted(events, key=base.event_start)
    transferred: list[dict[str, Any]] = []
    previous: tuple[int, int] | None = None
    changed = 0
    exact_candidate_events = 0
    missing_candidate_events: list[dict[str, Any]] = []

    for event in ordered:
        copied = dict(event)
        midi_pitch = event_midi(copied)
        if midi_pitch is None:
            transferred.append(copied)
            continue

        candidates = exact_twelfth_position_candidates(midi_pitch)
        selected = choose_candidate(candidates, previous)
        if selected is None:
            missing_candidate_events.append(
                {
                    "start": base.event_start(copied),
                    "midi": midi_pitch,
                    "originalStringIndex": event_string(copied),
                    "originalFret": event_fret(copied),
                }
            )
            transferred.append(copied)
            continue

        exact_candidate_events += 1
        string_index, fret = selected
        original_string = event_string(copied)
        original_fret = event_fret(copied)
        copied["originalStringIndex"] = original_string
        copied["originalFret"] = original_fret
        copied["stringIndex"] = string_index
        copied["fret"] = fret
        copied["voicingPolicy"] = "octave-lead-exact-12-or-14"
        copied["voicingCandidateCount"] = len(candidates)

        if original_string != string_index or original_fret != fret:
            changed += 1

        previous = selected
        transferred.append(copied)

    diagnostics = {
        "eventCount": len(ordered),
        "changedEventCount": changed,
        "exactCandidateEventCount": exact_candidate_events,
        "exactCandidateCoverage": round(
            exact_candidate_events / len(ordered), 4
        ) if ordered else 0.0,
        "missingCandidateEvents": missing_candidate_events,
    }
    return transferred, diagnostics


@app.function(image=image, timeout=1800, memory=4096)
def analyse_voicing(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    base.legacy_bridge.group_assignments = base.legacy_assignments.group_assignments
    base.legacy_renderer.create_tab = base.inventory_only_tab

    lead_result = base.run_one(audio_bytes, audio_name, "lead")
    raw_events = [
        event
        for event in (lead_result.get("events") or [])
        if isinstance(event, dict)
    ]
    transferred_events, diagnostics = transfer_octave_lead_voicing(raw_events)
    lead_reference = (fixture.get("parts") or {}).get("lead", {})

    before = base.compare_part("lead", raw_events, lead_reference)
    after = base.compare_part("lead", transferred_events, lead_reference)

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "gomyway2-octave-lead-twelfth-position-voicing",
        "engineVersion": base.analyzer.ENGINE_VERSION,
        "instrumentSeparationMode": lead_result.get("instrumentSeparationMode"),
        "before": before,
        "after": after,
        "scoreImprovement": round(
            float(after.get("comparisonScore") or 0.0)
            - float(before.get("comparisonScore") or 0.0),
            2,
        ),
        "diagnostics": diagnostics,
        "passed": (
            float(after.get("requiredFretCoverage") or 0.0) == 1.0
            and float(after.get("allowedFretPrecision") or 0.0) >= 0.90
            and float(after.get("comparisonScore") or 0.0)
            > float(before.get("comparisonScore") or 0.0)
        ),
        "trainingRule": (
            "benchmark-only-position-policy; do not integrate until all four "
            "locked regression guards remain green"
        ),
        "protectedBaselinesChanged": False,
    }

    payload = {
        "report": report,
        "rawLeadResult": lead_result,
        "transferredLeadEvents": transferred_events,
    }
    return json.dumps(
        payload,
        default=base.json_default,
        separators=(",", ":"),
    ).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway2_full_tab_reference.json",
    report_output: str = "/tmp/gomyway2-octave-lead-voicing-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload_bytes = analyse_voicing.remote(
        audio_file.read_bytes(), audio_file.name, fixture
    )
    payload = json.loads(bytes(payload_bytes).decode("utf-8"))
    report = payload["report"]

    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    Path("/tmp/gomyway2-lead-voicing-events.json").write_text(
        json.dumps(
            payload.get("transferredLeadEvents") or [],
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    before = report.get("before") or {}
    after = report.get("after") or {}
    diagnostics = report.get("diagnostics") or {}

    print("JIMMY PAIGE OCTAVE-LEAD VOICING BENCHMARK V1")
    print("=" * 61)
    print("Engine:", report.get("engineVersion"))
    print("Mode:", report.get("instrumentSeparationMode"))
    print("Before score:", before.get("comparisonScore"))
    print("Before frets:", before.get("fretInventory"))
    print("After score:", after.get("comparisonScore"))
    print("After frets:", after.get("fretInventory"))
    print("Required frets:", after.get("requiredFretHits"))
    print("Allowed-fret precision:", after.get("allowedFretPrecision"))
    print("Best motif score:", after.get("bestMotifScore"))
    print("Techniques retained:", after.get("techniqueChecks"))
    print("Exact candidate coverage:", diagnostics.get("exactCandidateCoverage"))
    print("Changed events:", diagnostics.get("changedEventCount"))
    print("Score improvement:", report.get("scoreImprovement"))
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
    print("Saved events: /tmp/gomyway2-lead-voicing-events.json")
    print("Diagnostic only. V71, V72, and all four locked baselines remain unchanged.")
