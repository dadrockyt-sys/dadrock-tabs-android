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

app = modal.App("dadrock-gomyway2-full-reference-benchmark")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v15")
    .add_local_python_source("modal_analyzer_v19")
    .add_local_python_source("modal_analyzer_v46")
    .add_local_python_source("modal_analyzer_v72")
)


def inventory_only_tab(mapped_groups: list[list[dict[str, Any]]], transcription_type: str) -> str:
    return "[full-reference benchmark: rendering intentionally skipped]"


def json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass
    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except (TypeError, ValueError):
            pass
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def event_number(event: dict[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        value = event.get(key)
        if isinstance(value, (int, float)):
            return int(round(value))
    return None


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def event_fret(event: dict[str, Any]) -> int | None:
    return event_number(event, ("fret", "fretNumber"))


def event_string(event: dict[str, Any]) -> int | None:
    return event_number(event, ("stringIndex", "string_index", "string"))


def event_midi(event: dict[str, Any]) -> int | None:
    return event_number(event, ("midi", "midiPitch", "pitch"))


def event_text(event: dict[str, Any]) -> str:
    fragments: list[str] = []
    for key, value in event.items():
        fragments.append(str(key))
        if isinstance(value, (str, int, float, bool)):
            fragments.append(str(value))
        elif isinstance(value, (list, tuple, set)):
            fragments.extend(str(item) for item in value)
        elif isinstance(value, dict):
            fragments.extend(f"{nested_key}:{nested_value}" for nested_key, nested_value in value.items())
    return " ".join(fragments).lower().replace("_", "-")


def technique_present(events: list[dict[str, Any]], technique: str) -> bool:
    aliases = {
        "bend": ("bend", "b4", "full"),
        "release": ("release", "return", "r2"),
        "palm-mute": ("palm-mute", "palmmute", "p.m", "pm"),
        "slide": ("slide", "slash", "/14"),
        "mute": ("dead", "muted", "mute", "x"),
        "rest": ("rest", "silence"),
    }
    needles = aliases.get(technique, (technique,))
    return any(any(needle in event_text(event) for needle in needles) for event in events)


def ordered_subsequence_score(observed: list[int], expected: list[int]) -> float:
    if not expected:
        return 1.0
    cursor = 0
    for value in observed:
        if cursor < len(expected) and value == expected[cursor]:
            cursor += 1
    return round(cursor / len(expected), 4)


def compare_part(
    part: str,
    events: list[dict[str, Any]],
    reference: dict[str, Any],
) -> dict[str, Any]:
    ordered_events = sorted(events, key=event_start)
    frets = [fret for event in ordered_events if (fret := event_fret(event)) is not None]
    strings = [string for event in ordered_events if (string := event_string(event)) is not None]
    midis = [midi for event in ordered_events if (midi := event_midi(event)) is not None]

    required_frets = [int(value) for value in reference.get("requiredFrets") or []]
    allowed_frets = {int(value) for value in reference.get("allowedFrets") or []}
    expected_strings = {int(value) for value in reference.get("expectedStrings") or []}
    required_techniques = [str(value) for value in reference.get("requiredTechniques") or []]
    expected_motifs = [
        [int(value) for value in motif]
        for motif in (reference.get("expectedMotifs") or [])
        if isinstance(motif, list)
    ]

    fret_inventory = Counter(frets)
    required_fret_hits = {
        str(fret): fret_inventory.get(fret, 0) > 0
        for fret in required_frets
    }
    fret_coverage = (
        sum(required_fret_hits.values()) / len(required_fret_hits)
        if required_fret_hits
        else 1.0
    )
    allowed_precision = (
        sum(1 for fret in frets if fret in allowed_frets) / len(frets)
        if frets and allowed_frets
        else 0.0
    )

    observed_strings = set(strings)
    string_overlap = (
        len(observed_strings & expected_strings) / len(expected_strings)
        if expected_strings
        else 1.0
    )

    technique_checks = {
        technique: technique_present(ordered_events, technique)
        for technique in required_techniques
    }
    technique_score = (
        sum(technique_checks.values()) / len(technique_checks)
        if technique_checks
        else 1.0
    )

    motif_scores = [ordered_subsequence_score(frets, motif) for motif in expected_motifs]
    motif_score = max(motif_scores, default=0.0)

    register = reference.get("register") or [None, None]
    low, high = register
    register_accuracy = (
        sum(1 for midi in midis if int(low) <= midi <= int(high)) / len(midis)
        if midis and low is not None and high is not None
        else 0.0
    )

    score = round(
        100.0
        * (
            0.24 * fret_coverage
            + 0.18 * allowed_precision
            + 0.12 * string_overlap
            + 0.20 * technique_score
            + 0.16 * motif_score
            + 0.10 * register_accuracy
        ),
        2,
    )

    return {
        "part": part,
        "eventCount": len(events),
        "fretInventory": dict(sorted(fret_inventory.items())),
        "observedStrings": sorted(observed_strings),
        "requiredFretHits": required_fret_hits,
        "requiredFretCoverage": round(fret_coverage, 4),
        "allowedFretPrecision": round(allowed_precision, 4),
        "stringOverlap": round(string_overlap, 4),
        "techniqueChecks": technique_checks,
        "techniqueScore": round(technique_score, 4),
        "motifScores": motif_scores,
        "bestMotifScore": motif_score,
        "registerAccuracy": round(register_accuracy, 4),
        "comparisonScore": score,
        "referenceDescription": reference.get("referenceDescription"),
    }


def run_one(audio_bytes: bytes, audio_name: str, transcription_type: str) -> dict[str, Any]:
    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
        temporary_file.write(audio_bytes)
        temporary_path = temporary_file.name
    try:
        return analyzer.analyze_audio_file(temporary_path, transcription_type)
    finally:
        Path(temporary_path).unlink(missing_ok=True)


@app.function(image=image, timeout=1800, memory=4096)
def analyse_reference(audio_bytes: bytes, audio_name: str, fixture: dict[str, Any]) -> bytes:
    legacy_bridge.group_assignments = legacy_assignments.group_assignments
    legacy_renderer.create_tab = inventory_only_tab

    results = {
        part: run_one(audio_bytes, audio_name, part)
        for part in ("bass", "rhythm", "lead")
    }
    comparisons = {
        part: compare_part(
            part,
            [event for event in (results[part].get("events") or []) if isinstance(event, dict)],
            (fixture.get("parts") or {}).get(part, {}),
        )
        for part in ("bass", "rhythm", "lead")
    }

    scores = [comparison["comparisonScore"] for comparison in comparisons.values()]
    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "gomyway2-three-part-tab-reference-comparison",
        "engineVersion": analyzer.ENGINE_VERSION,
        "tempoBpm": fixture.get("tempoBpm"),
        "instrumentModes": {
            part: results[part].get("instrumentSeparationMode")
            for part in results
        },
        "comparisons": comparisons,
        "overallComparisonScore": round(sum(scores) / len(scores), 2),
        "trainingRule": (
            "diagnostic-only-do-not-lock-until-the-score-and-musical-output-have-"
            "been-reviewed-against-the-user-supplied-tab-references"
        ),
        "protectedBaselinesChanged": False,
    }

    payload = {"report": report, "results": results}
    return json.dumps(payload, default=json_default, separators=(",", ":")).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway2_full_tab_reference.json",
    report_output: str = "/tmp/gomyway2-full-reference-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload_bytes = analyse_reference.remote(audio_file.read_bytes(), audio_file.name, fixture)
    payload = json.loads(bytes(payload_bytes).decode("utf-8"))
    report = payload["report"]

    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    for part, result in payload["results"].items():
        Path(f"/tmp/gomyway2-{part}-reference-result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )

    print("JIMMY PAIGE GO MY WAY 2 FULL TAB REFERENCE BENCHMARK V1")
    print("=" * 68)
    print("Engine:", report.get("engineVersion"))
    print("Tempo:", report.get("tempoBpm"))
    print("Modes:", report.get("instrumentModes"))

    for part in ("bass", "rhythm", "lead"):
        comparison = (report.get("comparisons") or {}).get(part, {})
        print(f"\n{part.upper()} REFERENCE COMPARISON")
        print("Score:", comparison.get("comparisonScore"))
        print("Events:", comparison.get("eventCount"))
        print("Frets:", comparison.get("fretInventory"))
        print("Required frets:", comparison.get("requiredFretHits"))
        print("Techniques:", comparison.get("techniqueChecks"))
        print("Best motif score:", comparison.get("bestMotifScore"))
        print("Register accuracy:", comparison.get("registerAccuracy"))

    print("\nOverall comparison score:", report.get("overallComparisonScore"))
    print("Saved report:", report_output)
    print("Saved results: /tmp/gomyway2-{bass,rhythm,lead}-reference-result.json")
    print("Diagnostic only. V71, V72, and all four locked baselines remain unchanged.")
