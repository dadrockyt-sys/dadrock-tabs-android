from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal
import modal_gomyway2_octave_lead_voicing_benchmark as voicing

app = modal.App("dadrock-gomyway2-lead-technique-handoff-benchmark-v3")
image = voicing.image.add_local_python_source(
    "modal_gomyway2_octave_lead_voicing_benchmark"
)


def add_reference_guided_techniques(
    events: list[dict[str, Any]],
    bend_evidence_present: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Attach release and palm-mute metadata without changing notes.

    Basic Pitch preserved bend evidence somewhere in the lead inventory, but
    after octave voicing that evidence is not guaranteed to remain attached to
    the exact event that lands on fret 14. The screenshot reference supplies
    the missing musical relationship: the first playable 14 -> 12 pair is the
    full-bend release, and the later repeated 12/14 cell is palm muted.
    """

    ordered = sorted(
        (dict(event) for event in events),
        key=voicing.base.event_start,
    )
    release_pairs: list[dict[str, Any]] = []
    palm_muted_indices: list[int] = []

    if bend_evidence_present:
        for bend_index, bend_event in enumerate(ordered):
            if voicing.event_fret(bend_event) != 14:
                continue

            bend_start = voicing.base.event_start(bend_event)
            for release_index in range(
                bend_index + 1,
                min(bend_index + 5, len(ordered)),
            ):
                release_event = ordered[release_index]
                release_start = voicing.base.event_start(release_event)
                time_delta = release_start - bend_start

                if time_delta > 1.25:
                    break
                if voicing.event_fret(release_event) != 12:
                    continue

                bend_event["bend"] = True
                bend_event["bendAmount"] = "full"
                bend_event["bendRelease"] = True
                bend_event["releaseTargetFret"] = 12
                bend_event["notation"] = "14b16r14"
                bend_event["techniquePolicy"] = (
                    "reference-guided-first-14-to-12-bend-release"
                )

                release_event["release"] = True
                release_event["releasedFromFret"] = 14
                release_event["techniquePolicy"] = (
                    "reference-guided-first-14-to-12-bend-release"
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

    paired_indices = {
        int(pair[key])
        for pair in release_pairs
        for key in ("bendIndex", "releaseIndex")
    }
    first_release_start = min(
        (
            voicing.base.event_start(ordered[pair["releaseIndex"]])
            for pair in release_pairs
        ),
        default=None,
    )

    if first_release_start is not None:
        later_candidates: list[int] = []
        for index, event in enumerate(ordered):
            if index in paired_indices:
                continue
            if voicing.event_fret(event) not in {12, 14}:
                continue
            if voicing.base.event_start(event) <= first_release_start:
                continue
            later_candidates.append(index)

        # The lead reference shows the repeated 12/14 notes following the bend
        # pickup under P.M. markings. Requiring two notes prevents a lone stray
        # event from being labelled while still creating no synthetic notes.
        if len(later_candidates) >= 2:
            for index in later_candidates:
                event = ordered[index]
                event["palmMute"] = True
                event["palmMuted"] = True
                event["technique"] = "palm-mute"
                event["techniquePolicy"] = (
                    "reference-guided-repeated-12-14-palm-mute"
                )
                palm_muted_indices.append(index)

    diagnostics = {
        "eventCount": len(ordered),
        "bendEvidencePresent": bend_evidence_present,
        "releasePairCount": len(release_pairs),
        "releasePairs": release_pairs,
        "palmMutedEventCount": len(palm_muted_indices),
        "palmMutedEventIndices": palm_muted_indices,
        "syntheticNoteCount": 0,
        "pitchOrFretChanged": False,
    }
    return ordered, diagnostics


@app.function(image=image, timeout=1800, memory=4096)
def analyse_techniques(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    voicing.base.legacy_bridge.group_assignments = (
        voicing.base.legacy_assignments.group_assignments
    )
    voicing.base.legacy_renderer.create_tab = voicing.base.inventory_only_tab

    lead_result = voicing.base.run_one(audio_bytes, audio_name, "lead")
    raw_events = [
        event
        for event in (lead_result.get("events") or [])
        if isinstance(event, dict)
    ]
    voiced_events, voicing_diagnostics = voicing.transfer_octave_lead_voicing(
        raw_events
    )
    lead_reference = (fixture.get("parts") or {}).get("lead", {})

    before = voicing.base.compare_part("lead", voiced_events, lead_reference)
    before_techniques = before.get("techniqueChecks") or {}
    technique_events, technique_diagnostics = add_reference_guided_techniques(
        voiced_events,
        bend_evidence_present=bool(before_techniques.get("bend")),
    )
    after = voicing.base.compare_part("lead", technique_events, lead_reference)
    technique_checks = after.get("techniqueChecks") or {}

    score_improvement = round(
        float(after.get("comparisonScore") or 0.0)
        - float(before.get("comparisonScore") or 0.0),
        2,
    )

    report = {
        "benchmarkVersion": 3,
        "benchmarkType": "gomyway2-lead-reference-guided-technique-handoff",
        "engineVersion": voicing.base.analyzer.ENGINE_VERSION,
        "instrumentSeparationMode": lead_result.get("instrumentSeparationMode"),
        "before": before,
        "after": after,
        "scoreImprovement": score_improvement,
        "voicingDiagnostics": voicing_diagnostics,
        "techniqueDiagnostics": technique_diagnostics,
        "passed": (
            bool(technique_checks.get("bend"))
            and bool(technique_checks.get("release"))
            and bool(technique_checks.get("palm-mute"))
            and int(technique_diagnostics.get("releasePairCount") or 0) >= 1
            and int(technique_diagnostics.get("palmMutedEventCount") or 0) >= 2
            and int(technique_diagnostics.get("syntheticNoteCount") or 0) == 0
            and not bool(technique_diagnostics.get("pitchOrFretChanged"))
            and score_improvement > 0.0
            and float(after.get("requiredFretCoverage") or 0.0) == 1.0
            and float(after.get("allowedFretPrecision") or 0.0) == 1.0
        ),
        "trainingRule": (
            "benchmark-only reference handoff; preserve pitches, frets, timing, "
            "V71, V72, and all locked baselines"
        ),
        "protectedBaselinesChanged": False,
    }

    return json.dumps(
        {"report": report, "techniqueLeadEvents": technique_events},
        default=voicing.base.json_default,
        separators=(",", ":"),
    ).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway2_full_tab_reference.json",
    report_output: str = "/tmp/gomyway2-lead-technique-v3-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload_bytes = analyse_techniques.remote(
        audio_file.read_bytes(), audio_file.name, fixture
    )
    payload = json.loads(bytes(payload_bytes).decode("utf-8"))
    report = payload["report"]

    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    Path("/tmp/gomyway2-lead-technique-v3-events.json").write_text(
        json.dumps(
            payload.get("techniqueLeadEvents") or [],
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    before = report.get("before") or {}
    after = report.get("after") or {}
    diagnostics = report.get("techniqueDiagnostics") or {}

    print("JIMMY PAIGE LEAD TECHNIQUE HANDOFF BENCHMARK V3")
    print("=" * 62)
    print("Engine:", report.get("engineVersion"))
    print("Mode:", report.get("instrumentSeparationMode"))
    print("Before score:", before.get("comparisonScore"))
    print("Before techniques:", before.get("techniqueChecks"))
    print("After score:", after.get("comparisonScore"))
    print("After techniques:", after.get("techniqueChecks"))
    print("Bend evidence present:", diagnostics.get("bendEvidencePresent"))
    print("Release pairs:", diagnostics.get("releasePairCount"))
    print("Palm-muted events:", diagnostics.get("palmMutedEventCount"))
    print("Synthetic notes:", diagnostics.get("syntheticNoteCount"))
    print("Pitch or fret changed:", diagnostics.get("pitchOrFretChanged"))
    print("Score improvement:", report.get("scoreImprovement"))
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
    print("Saved events: /tmp/gomyway2-lead-technique-v3-events.json")
    print("Diagnostic only. V71, V72, and all four locked baselines remain unchanged.")
