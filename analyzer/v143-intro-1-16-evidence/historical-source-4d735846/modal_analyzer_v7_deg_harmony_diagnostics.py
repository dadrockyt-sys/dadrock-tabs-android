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

app = modal.App("dadrock-v7-deg-harmony-diagnostics")
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
    return "[v7 D/E/G harmony diagnostics: rendering intentionally skipped]"


def json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(
        f"Object of type {type(value).__name__} is not JSON serializable"
    )


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
        return analyzer.analyze_audio_file(
            temporary_path,
            transcription_type,
        )
    finally:
        Path(temporary_path).unlink(missing_ok=True)


def target_window_evidence(
    windows: list[dict[str, Any]],
    target_pitch_classes: set[int],
) -> dict[str, Any]:
    evidence: list[dict[str, Any]] = []

    for window in windows:
        observed = {
            int(value)
            for value in window.get("pitchClasses") or []
        }
        intersection = observed & target_pitch_classes
        duration_map = {
            int(key): float(value)
            for key, value in (
                window.get("pitchClassWeightedDuration") or {}
            ).items()
        }
        total_duration = sum(duration_map.values()) or 1.0
        weighted_support = sum(
            duration_map.get(pitch_class, 0.0)
            for pitch_class in target_pitch_classes
        ) / total_duration
        coverage = len(intersection) / len(target_pitch_classes)

        evidence.append(
            {
                "start": round(float(window.get("start") or 0.0), 3),
                "end": round(float(window.get("end") or 0.0), 3),
                "coverage": round(coverage, 4),
                "weightedSupport": round(weighted_support, 4),
                "matchedPitchClasses": sorted(intersection),
                "missingPitchClasses": sorted(
                    target_pitch_classes - observed
                ),
                "observedPitchClasses": sorted(observed),
                "midis": list(window.get("midis") or []),
                "uniqueMidiCount": int(
                    window.get("uniqueMidiCount") or 0
                ),
            }
        )

    evidence.sort(
        key=lambda item: (
            float(item["coverage"]),
            float(item["weightedSupport"]),
            int(item["uniqueMidiCount"]),
        ),
        reverse=True,
    )
    strongest = evidence[:8]

    return {
        "strongestWindows": strongest,
        "fullCoverageWindowCount": sum(
            float(item["coverage"]) >= 1.0
            for item in evidence
        ),
        "twoToneWindowCount": sum(
            len(item["matchedPitchClasses"]) >= 2
            for item in evidence
        ),
        "maximumCoverage": max(
            (float(item["coverage"]) for item in evidence),
            default=0.0,
        ),
        "maximumWeightedSupport": max(
            (float(item["weightedSupport"]) for item in evidence),
            default=0.0,
        ),
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

    fixture_chords = [
        chord
        for chord in fixture.get("chords", [])
        if isinstance(chord, dict)
    ]
    progression = [
        str(name)
        for name in fixture.get("expectedProgression", [])
    ]

    analysis = detect_chord_sustain(
        events["rhythm"],
        chords=fixture_chords,
        progression=progression,
        minimum_sustain_seconds=float(
            fixture.get("minimumSustainSeconds") or 0.35
        ),
    )

    harmonic_events = prepare_harmonic_events(events["rhythm"])
    windows = build_soft_register_windows(harmonic_events)
    chord_windows = [
        window
        for window in windows
        if int(window.get("uniqueMidiCount") or 0) >= 3
        and len(window.get("pitchClasses") or []) >= 2
    ]

    targets = {
        str(chord.get("name")): {
            int(value)
            for value in chord.get("pitchClasses") or []
        }
        for chord in fixture_chords
        if str(chord.get("name") or "") in {"D", "E", "G"}
    }
    diagnostics = {
        name: target_window_evidence(chord_windows, pitch_classes)
        for name, pitch_classes in targets.items()
    }

    protection_checks = {
        "bassSeparationActive": (
            results["bass"].get("instrumentSeparationMode")
            == "strict-three-way-register-gate"
        ),
        "rhythmSeparationActive": (
            results["rhythm"].get("instrumentSeparationMode")
            == "strict-three-way-register-gate"
        ),
        "leadSeparationActive": (
            results["lead"].get("instrumentSeparationMode")
            == "strict-three-way-register-gate"
        ),
        "bassEventsPresent": len(events["bass"]) >= 62,
        "rhythmEventsPresent": len(events["rhythm"]) >= 39,
        "leadEventsPresent": len(events["lead"]) >= 14,
        "engineV6": analysis.get("engineVersion") == 6,
        "noSyntheticNotes": analysis.get("noSyntheticNotes") is True,
    }

    report = {
        "benchmarkVersion": 7,
        "benchmarkType": "D-E-G-window-evidence-diagnostics",
        "engineVersion": analyzer.ENGINE_VERSION,
        "audioName": audio_name,
        "eventCounts": {
            part: len(part_events)
            for part, part_events in events.items()
        },
        "detectedVocabulary": analysis.get("chordVocabulary") or [],
        "observedProgression": analysis.get("observedProgression") or [],
        "targetDiagnostics": diagnostics,
        "protectionChecks": protection_checks,
        "passed": all(protection_checks.values()),
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "Inspect real D, E, and G pitch evidence before changing any "
            "matching threshold; never synthesize or reassign notes."
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
        "analyzer/fixtures/"
        "gomyway_full_chord_sustain_reference.json"
    ),
    report_output: str = (
        "/tmp/gomyway-v7-deg-harmony-diagnostics.json"
    ),
) -> None:
    audio_file = Path(layered_audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(
            f"Layered audio file not found: {audio_file}"
        )
    if not fixture_file.is_file():
        raise FileNotFoundError(
            f"Fixture file not found: {fixture_file}"
        )

    fixture = json.loads(
        fixture_file.read_text(encoding="utf-8")
    )
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

    print("JIMMY PAIGE V7 D / E / G HARMONY EVIDENCE DIAGNOSTICS")
    print("=" * 72)
    print("Detected vocabulary:", report.get("detectedVocabulary"))
    print("Observed progression:", report.get("observedProgression"))

    for name, diagnostic in (
        report.get("targetDiagnostics") or {}
    ).items():
        print(f"\n{name} evidence")
        print("Maximum coverage:", diagnostic.get("maximumCoverage"))
        print(
            "Maximum weighted support:",
            diagnostic.get("maximumWeightedSupport"),
        )
        print(
            "Full-coverage windows:",
            diagnostic.get("fullCoverageWindowCount"),
        )
        print(
            "Two-tone windows:",
            diagnostic.get("twoToneWindowCount"),
        )
        print("Strongest windows:")
        for window in diagnostic.get("strongestWindows") or []:
            print(
                " ",
                window.get("start"),
                "coverage=",
                window.get("coverage"),
                "support=",
                window.get("weightedSupport"),
                "matched=",
                window.get("matchedPitchClasses"),
                "missing=",
                window.get("missingPitchClasses"),
                "midis=",
                window.get("midis"),
            )

    print("\nProtection checks")
    for name, passed in (
        report.get("protectionChecks") or {}
    ).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall protection:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
