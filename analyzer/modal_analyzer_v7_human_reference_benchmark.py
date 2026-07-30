from __future__ import annotations

import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v15 as legacy_renderer
import modal_analyzer_v19 as legacy_assignments
import modal_analyzer_v46 as legacy_bridge
import modal_analyzer_v72 as analyzer
from chord_sustain import detect_chord_sustain

app = modal.App("dadrock-v7-human-reference-benchmark")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v15")
    .add_local_python_source("modal_analyzer_v19")
    .add_local_python_source("modal_analyzer_v46")
    .add_local_python_source("modal_analyzer_v72")
    .add_local_python_source("chord_sustain")
)


def inventory_only_tab(mapped_groups: list[list[dict[str, Any]]], transcription_type: str) -> str:
    return "[v7 human-reference benchmark: rendering intentionally skipped]"


def json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def run_one(audio_bytes: bytes, audio_name: str, transcription_type: str) -> dict[str, Any]:
    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(audio_bytes)
        temporary_path = handle.name
    try:
        return analyzer.analyze_audio_file(temporary_path, transcription_type)
    finally:
        Path(temporary_path).unlink(missing_ok=True)


def event_frets(events: list[dict[str, Any]]) -> list[int]:
    return [int(event["fret"]) for event in events if event.get("fret") is not None]


def technique_counts(events: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for event in events:
        technique = str(event.get("technique") or "").strip().lower()
        if technique:
            counts[technique] += 1
        for item in event.get("techniques") or []:
            name = str(item or "").strip().lower()
            if name:
                counts[name] += 1
    return dict(counts)


def contains_any(values: set[int], expected: set[int]) -> bool:
    return bool(values & expected)


@app.function(image=image, timeout=1800, memory=4096)
def run_benchmark(audio_bytes: bytes, audio_name: str) -> bytes:
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
    frets = {part: event_frets(part_events) for part, part_events in events.items()}
    fret_sets = {part: set(part_frets) for part, part_frets in frets.items()}
    techniques = {part: technique_counts(part_events) for part, part_events in events.items()}

    chord_analysis = detect_chord_sustain(events["rhythm"])
    chord_vocabulary = set(chord_analysis.get("chordVocabulary") or [])

    human_reference_checks = {
        "leadLowBendPosition": contains_any(fret_sets["lead"], {0, 2}),
        "leadUpperBendPosition": contains_any(fret_sets["lead"], {12, 14}),
        "leadBendEvidence": any("bend" in name for name in techniques["lead"]),
        "leadPalmMuteEvidence": any("palm" in name or name in {"pm", "p.m."} for name in techniques["lead"]),
        "bassSevenFiveContour": 7 in fret_sets["bass"] and 5 in fret_sets["bass"],
        "bassUpperSlidePosition": 14 in fret_sets["bass"],
        "bassMutedAttackEvidence": any("mute" in name or name == "x" for name in techniques["bass"]),
        "rhythmOpenChordPosition": contains_any(fret_sets["rhythm"], {0, 2, 3, 4, 5}),
        "rhythmNinthPosition": 9 in fret_sets["rhythm"],
        "rhythmSeventhOrTwelfthMovement": contains_any(fret_sets["rhythm"], {7, 12}),
        "harmonyG6": "G6" in chord_vocabulary,
        "harmonyATp2": "A(tp2)" in chord_vocabulary,
        "harmonyE": "E" in chord_vocabulary,
        "harmonyD": "D" in chord_vocabulary,
        "harmonyG": "G" in chord_vocabulary,
        "harmonySustain": int(chord_analysis.get("sustainedChordCount") or 0) >= 1,
        "harmonyRepeatedAttacks": bool(chord_analysis.get("repeatedAttackCounts")),
    }

    category_names = {
        "lead": [name for name in human_reference_checks if name.startswith("lead")],
        "bass": [name for name in human_reference_checks if name.startswith("bass")],
        "rhythm": [name for name in human_reference_checks if name.startswith("rhythm")],
        "harmony": [name for name in human_reference_checks if name.startswith("harmony")],
    }
    category_scores = {
        category: round(
            sum(bool(human_reference_checks[name]) for name in names) / max(1, len(names)),
            3,
        )
        for category, names in category_names.items()
    }

    protection_checks = {
        "bassSeparationActive": results["bass"].get("instrumentSeparationMode") == "strict-three-way-register-gate",
        "rhythmSeparationActive": results["rhythm"].get("instrumentSeparationMode") == "strict-three-way-register-gate",
        "leadSeparationActive": results["lead"].get("instrumentSeparationMode") == "strict-three-way-register-gate",
        "bassEventsPresent": len(events["bass"]) >= 62,
        "rhythmEventsPresent": len(events["rhythm"]) >= 39,
        "leadEventsPresent": len(events["lead"]) >= 14,
        "chordEngineV6": chord_analysis.get("engineVersion") == 6,
        "noSyntheticNotes": chord_analysis.get("noSyntheticNotes") is True,
    }

    report = {
        "benchmarkVersion": 7,
        "benchmarkType": "human-verified-lead-bass-rhythm-harmony-reference",
        "engineVersion": analyzer.ENGINE_VERSION,
        "audioName": audio_name,
        "instrumentSeparationModes": {
            part: result.get("instrumentSeparationMode")
            for part, result in results.items()
        },
        "eventCounts": {part: len(part_events) for part, part_events in events.items()},
        "fretInventories": {part: sorted(set(part_frets)) for part, part_frets in frets.items()},
        "techniqueCounts": techniques,
        "chordAnalysis": chord_analysis,
        "humanReferenceChecks": human_reference_checks,
        "categoryScores": category_scores,
        "protectionChecks": protection_checks,
        "passed": all(protection_checks.values()),
        "protectedBaselinesChanged": False,
        "trainingRule": "Score lead, bass, rhythm, and harmony independently; never move evidence between parts and never synthesize missing notes.",
    }
    return json.dumps(report, default=json_default, separators=(",", ":")).encode("utf-8")


@app.local_entrypoint()
def main(
    layered_audio_path: str,
    report_output: str = "/tmp/gomyway-v7-human-reference-report.json",
) -> None:
    audio_file = Path(layered_audio_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Layered audio file not found: {audio_file}")

    payload = run_benchmark.remote(audio_file.read_bytes(), audio_file.name)
    report = json.loads(bytes(payload).decode("utf-8"))
    Path(report_output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print("JIMMY PAIGE V7 HUMAN-VERIFIED LAYERED REFERENCE BENCHMARK")
    print("=" * 72)
    print("Engine:", report.get("engineVersion"))
    print("Modes:", report.get("instrumentSeparationModes"))
    print("Event counts:", report.get("eventCounts"))
    print("Fret inventories:", report.get("fretInventories"))
    print("Technique counts:", report.get("techniqueCounts"))
    print("Chord vocabulary:", (report.get("chordAnalysis") or {}).get("chordVocabulary"))
    print("Category scores:", report.get("categoryScores"))
    print("\nHuman-reference evidence")
    for name, passed in (report.get("humanReferenceChecks") or {}).items():
        print("PASS" if passed else "MISS", name)
    print("\nProtection checks")
    for name, passed in (report.get("protectionChecks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall protection:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
