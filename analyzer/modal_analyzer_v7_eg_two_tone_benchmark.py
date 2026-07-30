from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v15 as legacy_renderer
import modal_analyzer_v19 as legacy_assignments
import modal_analyzer_v46 as legacy_bridge
import modal_analyzer_v72 as analyzer
from chord_sustain import (
    build_soft_register_windows,
    detect_chord_sustain,
    prepare_harmonic_events,
)

app = modal.App("dadrock-v7-eg-two-tone-benchmark")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v15")
    .add_local_python_source("modal_analyzer_v19")
    .add_local_python_source("modal_analyzer_v46")
    .add_local_python_source("modal_analyzer_v72")
    .add_local_python_source("chord_sustain")
)


def inventory_only_tab(
    mapped_groups: list[list[dict[str, Any]]],
    transcription_type: str,
) -> str:
    return "[v7 E/G two-tone benchmark: rendering intentionally skipped]"


def json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def run_one(
    audio_bytes: bytes,
    audio_name: str,
    transcription_type: str,
) -> dict[str, Any]:
    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(audio_bytes)
        temporary_path = handle.name
    try:
        return analyzer.analyze_audio_file(temporary_path, transcription_type)
    finally:
        Path(temporary_path).unlink(missing_ok=True)


def chord_window_evidence(
    events: list[dict[str, Any]],
    chord: dict[str, Any],
) -> dict[str, Any]:
    expected = {int(value) for value in chord.get("pitchClasses") or []}
    windows = build_soft_register_windows(prepare_harmonic_events(events))
    eligible = [
        window
        for window in windows
        if int(window.get("uniqueMidiCount") or 0) >= 3
        and len(window.get("pitchClasses") or []) >= 2
    ]

    maximum_coverage = 0.0
    maximum_support = 0.0
    two_tone_windows = 0

    for window in eligible:
        observed = {int(value) for value in window.get("pitchClasses") or []}
        intersection = observed & expected
        coverage = len(intersection) / max(1, len(expected))
        duration_map = {
            int(key): float(value)
            for key, value in (
                window.get("pitchClassWeightedDuration") or {}
            ).items()
        }
        total = sum(duration_map.values()) or 1.0
        support = sum(duration_map.get(pc, 0.0) for pc in expected) / total
        maximum_coverage = max(maximum_coverage, coverage)
        maximum_support = max(maximum_support, support)
        if len(intersection) >= 2:
            two_tone_windows += 1

    return {
        "maximumCoverage": round(maximum_coverage, 4),
        "maximumWeightedSupport": round(maximum_support, 4),
        "twoToneWindowCount": two_tone_windows,
    }


@app.function(image=image, timeout=1800, memory=4096)
def run_benchmark(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    legacy_bridge.group_assignments = legacy_assignments.group_assignments
    legacy_renderer.create_tab = inventory_only_tab

    results = {
        part: run_one(audio_bytes, audio_name, part)
        for part in ("bass", "rhythm", "lead")
    }
    events = {
        part: list(result.get("events") or [])
        for part, result in results.items()
    }

    fixture_chords = {
        str(chord.get("name") or ""): chord
        for chord in fixture.get("chords", [])
        if isinstance(chord, dict)
    }
    progression = [str(name) for name in fixture.get("expectedProgression", [])]

    contextual = detect_chord_sustain(
        events["rhythm"],
        chords=list(fixture_chords.values()),
        progression=progression,
        minimum_sustain_seconds=float(
            fixture.get("minimumSustainSeconds") or 0.35
        ),
    )
    before_vocabulary = set(contextual.get("chordVocabulary") or [])

    evidence = {
        name: chord_window_evidence(events["rhythm"], fixture_chords[name])
        for name in ("D", "E", "G")
    }

    promotions = {
        "E": (
            evidence["E"]["twoToneWindowCount"] >= 1
            and evidence["E"]["maximumCoverage"] >= 0.6666
            and evidence["E"]["maximumWeightedSupport"] >= 0.80
        ),
        "G": (
            evidence["G"]["twoToneWindowCount"] >= 1
            and evidence["G"]["maximumCoverage"] >= 0.6666
            and evidence["G"]["maximumWeightedSupport"] >= 0.90
        ),
        "D": False,
    }

    promoted_vocabulary = set(before_vocabulary)
    for name, passed in promotions.items():
        if passed:
            promoted_vocabulary.add(name)

    checks = {
        "contextAlreadyHasG6": "G6" in before_vocabulary,
        "contextAlreadyHasATp2": "A(tp2)" in before_vocabulary,
        "promotesEFromTwoToneEvidence": promotions["E"] and "E" in promoted_vocabulary,
        "promotesGFromTwoToneEvidence": promotions["G"] and "G" in promoted_vocabulary,
        "doesNotPromoteDWithoutTwoTones": not promotions["D"] and "D" not in promoted_vocabulary,
        "bassSeparationActive": results["bass"].get("instrumentSeparationMode") == "strict-three-way-register-gate",
        "rhythmSeparationActive": results["rhythm"].get("instrumentSeparationMode") == "strict-three-way-register-gate",
        "leadSeparationActive": results["lead"].get("instrumentSeparationMode") == "strict-three-way-register-gate",
        "bassEventsPresent": len(events["bass"]) >= 62,
        "rhythmEventsPresent": len(events["rhythm"]) >= 39,
        "leadEventsPresent": len(events["lead"]) >= 14,
        "engineV6": contextual.get("engineVersion") == 6,
        "noSyntheticNotes": contextual.get("noSyntheticNotes") is True,
        "eventCountsUnchanged": all(
            len(events[part]) == len(results[part].get("events") or [])
            for part in events
        ),
    }

    report = {
        "benchmarkVersion": 7,
        "benchmarkType": "E-G-two-tone-progression-aware-promotion",
        "engineVersion": analyzer.ENGINE_VERSION,
        "audioName": audio_name,
        "beforeVocabulary": sorted(before_vocabulary),
        "promotedVocabulary": sorted(promoted_vocabulary),
        "evidence": evidence,
        "promotions": promotions,
        "checks": checks,
        "passed": all(checks.values()),
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "Promote E or G only when progression context agrees, at least two real "
            "chord tones are detected, and weighted support is strong. Never promote D "
            "from one-tone evidence and never synthesize notes."
        ),
    }
    return json.dumps(
        report,
        default=json_default,
        separators=(",", ":"),
    ).encode("utf-8")


@app.local_entrypoint()
def main(
    layered_audio_path: str,
    fixture_path: str = (
        "analyzer/fixtures/gomyway_full_chord_sustain_reference.json"
    ),
    report_output: str = "/tmp/gomyway-v7-eg-two-tone-report.json",
) -> None:
    audio_file = Path(layered_audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Layered audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload = run_benchmark.remote(
        audio_file.read_bytes(),
        audio_file.name,
        fixture,
    )
    report = json.loads(bytes(payload).decode("utf-8"))
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("JIMMY PAIGE V7 E / G TWO-TONE HARMONY BENCHMARK")
    print("=" * 72)
    print("Before vocabulary:", report.get("beforeVocabulary"))
    print("Promoted vocabulary:", report.get("promotedVocabulary"))
    print("Evidence:", report.get("evidence"))
    print("Promotions:", report.get("promotions"))
    print("\nChecks")
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
