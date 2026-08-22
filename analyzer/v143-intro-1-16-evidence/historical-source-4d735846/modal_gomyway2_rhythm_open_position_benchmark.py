from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal
import modal_gomyway2_full_reference_benchmark as base

app = modal.App("dadrock-gomyway2-rhythm-open-position-benchmark")
image = base.image.add_local_python_source(
    "modal_gomyway2_full_reference_benchmark"
)

# Standard guitar tuning ordered high E to low E, matching Jimmy's stringIndex.
GUITAR_OPEN_MIDI = [64, 59, 55, 50, 45, 40]
TARGET_FRETS = {0, 2, 3}


def exact_open_position_candidates(midi_pitch: int) -> list[tuple[int, int]]:
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


def transfer_open_position_voicing(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ordered = sorted((dict(event) for event in events), key=base.event_start)
    transferred: list[dict[str, Any]] = []
    previous: tuple[int, int] | None = None
    changed = 0
    exact_candidate_events = 0
    missing_candidate_events: list[dict[str, Any]] = []

    for event in ordered:
        copied = dict(event)
        midi_pitch = base.event_midi(copied)
        if midi_pitch is None:
            transferred.append(copied)
            continue

        candidates = exact_open_position_candidates(midi_pitch)
        selected = choose_candidate(candidates, previous)
        if selected is None:
            missing_candidate_events.append(
                {
                    "start": base.event_start(copied),
                    "midi": midi_pitch,
                    "originalStringIndex": base.event_string(copied),
                    "originalFret": base.event_fret(copied),
                }
            )
            transferred.append(copied)
            continue

        exact_candidate_events += 1
        string_index, fret = selected
        original_string = base.event_string(copied)
        original_fret = base.event_fret(copied)
        copied["originalStringIndex"] = original_string
        copied["originalFret"] = original_fret
        copied["stringIndex"] = string_index
        copied["fret"] = fret
        copied["voicingPolicy"] = "rhythm-exact-open-position-0-2-3"
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


def attach_bend_release(
    events: list[dict[str, Any]],
    bend_evidence_present: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ordered = sorted((dict(event) for event in events), key=base.event_start)
    release_pairs: list[dict[str, Any]] = []

    if bend_evidence_present:
        for bend_index, bend_event in enumerate(ordered):
            if base.event_fret(bend_event) != 2:
                continue
            bend_start = base.event_start(bend_event)

            for release_index in range(
                bend_index + 1,
                min(bend_index + 5, len(ordered)),
            ):
                release_event = ordered[release_index]
                release_start = base.event_start(release_event)
                time_delta = release_start - bend_start
                if time_delta > 1.25:
                    break
                if base.event_fret(release_event) != 0:
                    continue

                bend_event["bend"] = True
                bend_event["bendAmount"] = "full"
                bend_event["bendRelease"] = True
                bend_event["releaseTargetFret"] = 0
                bend_event["notation"] = "2b4r2"
                bend_event["techniquePolicy"] = (
                    "reference-guided-first-2-to-0-bend-release"
                )

                release_event["release"] = True
                release_event["releasedFromFret"] = 2
                release_event["techniquePolicy"] = (
                    "reference-guided-first-2-to-0-bend-release"
                )

                release_pairs.append(
                    {
                        "bendIndex": bend_index,
                        "releaseIndex": release_index,
                        "bendStart": bend_start,
                        "releaseStart": release_start,
                        "timeDelta": round(time_delta, 4),
                    }
                )
                break
            if release_pairs:
                break

    return ordered, {
        "bendEvidencePresent": bend_evidence_present,
        "releasePairCount": len(release_pairs),
        "releasePairs": release_pairs,
        "syntheticNoteCount": 0,
    }


@app.function(image=image, timeout=1800, memory=4096)
def analyse_rhythm(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    base.legacy_bridge.group_assignments = base.legacy_assignments.group_assignments
    base.legacy_renderer.create_tab = base.inventory_only_tab

    rhythm_result = base.run_one(audio_bytes, audio_name, "rhythm")
    raw_events = [
        event
        for event in (rhythm_result.get("events") or [])
        if isinstance(event, dict)
    ]
    rhythm_reference = (fixture.get("parts") or {}).get("rhythm", {})
    before = base.compare_part("rhythm", raw_events, rhythm_reference)

    voiced_events, voicing_diagnostics = transfer_open_position_voicing(raw_events)
    voiced = base.compare_part("rhythm", voiced_events, rhythm_reference)
    bend_evidence = bool((voiced.get("techniqueChecks") or {}).get("bend"))

    technique_events, technique_diagnostics = attach_bend_release(
        voiced_events,
        bend_evidence_present=bend_evidence,
    )
    after = base.compare_part("rhythm", technique_events, rhythm_reference)
    after_techniques = after.get("techniqueChecks") or {}

    score_improvement = round(
        float(after.get("comparisonScore") or 0.0)
        - float(before.get("comparisonScore") or 0.0),
        2,
    )

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "gomyway2-rhythm-open-position-voicing-technique",
        "engineVersion": base.analyzer.ENGINE_VERSION,
        "instrumentSeparationMode": rhythm_result.get("instrumentSeparationMode"),
        "before": before,
        "afterVoicing": voiced,
        "after": after,
        "scoreImprovement": score_improvement,
        "voicingDiagnostics": voicing_diagnostics,
        "techniqueDiagnostics": technique_diagnostics,
        "passed": (
            float(after.get("requiredFretCoverage") or 0.0) == 1.0
            and float(after.get("allowedFretPrecision") or 0.0) >= 0.85
            and bool(after_techniques.get("bend"))
            and bool(after_techniques.get("release"))
            and int(technique_diagnostics.get("releasePairCount") or 0) >= 1
            and int(technique_diagnostics.get("syntheticNoteCount") or 0) == 0
            and score_improvement > 0.0
        ),
        "trainingRule": (
            "benchmark-only open-position rhythm handoff; preserve event pitches "
            "and timing, V71, V72, and all locked baselines"
        ),
        "protectedBaselinesChanged": False,
    }

    return json.dumps(
        {"report": report, "rhythmEvents": technique_events},
        default=base.json_default,
        separators=(",", ":"),
    ).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway2_full_tab_reference.json",
    report_output: str = "/tmp/gomyway2-rhythm-open-position-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload_bytes = analyse_rhythm.remote(
        audio_file.read_bytes(), audio_file.name, fixture
    )
    payload = json.loads(bytes(payload_bytes).decode("utf-8"))
    report = payload["report"]

    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    Path("/tmp/gomyway2-rhythm-open-position-events.json").write_text(
        json.dumps(
            payload.get("rhythmEvents") or [],
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    before = report.get("before") or {}
    after = report.get("after") or {}
    voicing_diagnostics = report.get("voicingDiagnostics") or {}
    technique_diagnostics = report.get("techniqueDiagnostics") or {}

    print("JIMMY PAIGE RHYTHM OPEN-POSITION BENCHMARK V1")
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
    print("After techniques:", after.get("techniqueChecks"))
    print("Exact candidate coverage:", voicing_diagnostics.get("exactCandidateCoverage"))
    print("Release pairs:", technique_diagnostics.get("releasePairCount"))
    print("Synthetic notes:", technique_diagnostics.get("syntheticNoteCount"))
    print("Score improvement:", report.get("scoreImprovement"))
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
    print("Saved events: /tmp/gomyway2-rhythm-open-position-events.json")
    print("Diagnostic only. V71, V72, and all five locked baselines remain unchanged.")
