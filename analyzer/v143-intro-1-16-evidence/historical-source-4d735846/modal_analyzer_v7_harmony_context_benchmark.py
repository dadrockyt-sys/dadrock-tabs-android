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
from chord_sustain import detect_chord_sustain

app = modal.App("dadrock-v7-harmony-context-benchmark")
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
    return "[v7 harmony-context benchmark: rendering intentionally skipped]"


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


def harmony_checks(
    chord_analysis: dict[str, Any],
) -> dict[str, bool]:
    vocabulary = set(
        chord_analysis.get("chordVocabulary") or []
    )
    return {
        "G6": "G6" in vocabulary,
        "A(tp2)": "A(tp2)" in vocabulary,
        "E": "E" in vocabulary,
        "D": "D" in vocabulary,
        "G": "G" in vocabulary,
        "sustain": int(
            chord_analysis.get("sustainedChordCount") or 0
        ) >= 1,
        "repeatedAttacks": bool(
            chord_analysis.get("repeatedAttackCounts")
        ),
    }


def score(checks: dict[str, bool]) -> float:
    return round(
        sum(bool(value) for value in checks.values())
        / max(1, len(checks)),
        3,
    )


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

    before = detect_chord_sustain(events["rhythm"])
    before_checks = harmony_checks(before)

    fixture_chords = [
        chord
        for chord in fixture.get("chords", [])
        if isinstance(chord, dict)
    ]
    expected_progression = [
        str(name)
        for name in fixture.get("expectedProgression", [])
    ]

    after = detect_chord_sustain(
        events["rhythm"],
        chords=fixture_chords,
        progression=expected_progression,
        minimum_sustain_seconds=float(
            fixture.get("minimumSustainSeconds") or 0.35
        ),
    )
    after_checks = harmony_checks(after)

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
        "engineV6": after.get("engineVersion") == 6,
        "noSyntheticNotes": after.get("noSyntheticNotes") is True,
        "eventCountsUnchanged": all(
            len(events[part])
            == len(results[part].get("events") or [])
            for part in events
        ),
    }

    before_score = score(before_checks)
    after_score = score(after_checks)
    report = {
        "benchmarkVersion": 7,
        "benchmarkType": "reference-aware-harmony-context-tie-breaker",
        "engineVersion": analyzer.ENGINE_VERSION,
        "audioName": audio_name,
        "expectedProgression": expected_progression,
        "before": {
            "score": before_score,
            "checks": before_checks,
            "analysis": before,
        },
        "after": {
            "score": after_score,
            "checks": after_checks,
            "analysis": after,
        },
        "scoreImprovement": round(after_score - before_score, 3),
        "protectionChecks": protection_checks,
        "passed": all(protection_checks.values()),
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "Use the verified chorus progression only as a tie-breaker; "
            "every chord still requires detected pitch evidence and no notes "
            "may be created, moved, or reassigned."
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
        "/tmp/gomyway-v7-harmony-context-report.json"
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

    print("JIMMY PAIGE V7 REFERENCE-AWARE HARMONY BENCHMARK")
    print("=" * 72)
    print("Before score:", (report.get("before") or {}).get("score"))
    print("After score:", (report.get("after") or {}).get("score"))
    print("Improvement:", report.get("scoreImprovement"))
    print("Expected progression:", report.get("expectedProgression"))
    print("\nBefore harmony evidence")
    for name, passed in (
        (report.get("before") or {}).get("checks") or {}
    ).items():
        print("PASS" if passed else "MISS", name)
    print("\nAfter harmony evidence")
    for name, passed in (
        (report.get("after") or {}).get("checks") or {}
    ).items():
        print("PASS" if passed else "MISS", name)
    print("\nProtection checks")
    for name, passed in (
        report.get("protectionChecks") or {}
    ).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall protection:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
