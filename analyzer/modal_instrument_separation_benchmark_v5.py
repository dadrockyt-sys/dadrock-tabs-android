"""Three-way register separation benchmark for bass, rhythm guitar, and octave lead.

V5 extends the proven V4 register gate into all three production transcription
choices. It runs the protected V71 analyzer for lead, rhythm, and bass, then
applies a mutually exclusive register policy before fingering/rendering:

- bass: MIDI 28-51
- rhythm/main guitar: MIDI 52-63
- lead/octave guitar: MIDI 64-76

This remains benchmark-only. V71 and all locked regression baselines are not
modified.
"""

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
import modal_analyzer_v71 as analyzer

app = modal.App("dadrock-instrument-separation-benchmark-v5")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v15")
    .add_local_python_source("modal_analyzer_v19")
    .add_local_python_source("modal_analyzer_v46")
    .add_local_python_source("modal_analyzer_v71")
)

DEFAULT_POLICY = {
    "bass": [28, 51],
    "rhythm": [52, 63],
    "lead": [64, 76],
}


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


def event_midi(event: dict[str, Any]) -> int | None:
    for key in ("midi", "midiPitch", "pitch"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return int(round(value))
    return None


def result_events(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [event for event in (result.get("events") or []) if isinstance(event, dict)]


def inventory_only_tab(mapped_groups: list[list[dict[str, Any]]], transcription_type: str) -> str:
    return "[three-way inventory benchmark: tab rendering intentionally skipped]"


def policy_for(fixture: dict[str, Any]) -> dict[str, list[int]]:
    fixture_policy = fixture.get("threeWayRegisterPolicy") or {}
    policy: dict[str, list[int]] = {}
    for part, fallback in DEFAULT_POLICY.items():
        value = fixture_policy.get(part, fallback)
        if not isinstance(value, list) or len(value) != 2:
            value = fallback
        policy[part] = [int(value[0]), int(value[1])]
    return policy


def gate_events(
    events: list[dict[str, Any]],
    transcription_type: str,
    policy: dict[str, list[int]],
) -> list[dict[str, Any]]:
    low, high = policy[transcription_type]
    return [
        event
        for event in events
        if (midi := event_midi(event)) is not None and low <= midi <= high
    ]


def summarize(events: list[dict[str, Any]], policy: dict[str, list[int]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    midis: list[int] = []
    for event in events:
        midi = event_midi(event)
        if midi is None:
            continue
        midis.append(midi)
        matched = "outside"
        for part, (low, high) in policy.items():
            if low <= midi <= high:
                matched = part
                break
        counts[matched] += 1

    ordered = sorted(midis)
    return {
        "eventCount": len(events),
        "pitchedEventCount": len(midis),
        "minimumMidi": min(midis) if midis else None,
        "maximumMidi": max(midis) if midis else None,
        "medianMidi": ordered[len(ordered) // 2] if ordered else None,
        "registerCounts": dict(counts),
        "midiInventory": sorted(Counter(midis).items()),
    }


def contamination(summary: dict[str, Any], expected_part: str) -> float:
    counts = summary.get("registerCounts") or {}
    total = sum(int(value) for value in counts.values())
    expected = int(counts.get(expected_part, 0))
    return round((total - expected) / total, 4) if total else 1.0


@app.function(image=image, timeout=1200, memory=4096)
def analyse_three_way(audio_bytes: bytes, audio_name: str, fixture: dict[str, Any]) -> bytes:
    legacy_bridge.group_assignments = legacy_assignments.group_assignments
    legacy_renderer.create_tab = inventory_only_tab

    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
        temporary_file.write(audio_bytes)
        temporary_path = temporary_file.name

    try:
        policy = policy_for(fixture)
        raw_results = {
            part: analyzer.analyze_audio_file(temporary_path, part)
            for part in ("lead", "rhythm", "bass")
        }
        raw_events = {part: result_events(result) for part, result in raw_results.items()}
        separated_events = {
            part: gate_events(events, part, policy)
            for part, events in raw_events.items()
        }
        raw_summaries = {
            part: summarize(events, policy)
            for part, events in raw_events.items()
        }
        separated_summaries = {
            part: summarize(events, policy)
            for part, events in separated_events.items()
        }

        minimums = fixture.get("threeWayMinimumEventCounts") or {
            "bass": 2,
            "rhythm": 4,
            "lead": 3,
        }
        max_contamination = float(
            (fixture.get("threeWayExpectations") or {}).get(
                "maximumContaminationRatio", 0.05
            )
        )

        checks: dict[str, dict[str, Any]] = {}
        for part in ("bass", "rhythm", "lead"):
            summary = separated_summaries[part]
            observed = int((summary.get("registerCounts") or {}).get(part, 0))
            unwanted = contamination(summary, part)
            minimum = int(minimums.get(part, 1))
            checks[part] = {
                "observedEventCount": observed,
                "minimumEventCount": minimum,
                "contaminationRatio": unwanted,
                "maximumContaminationRatio": max_contamination,
                "passed": observed >= minimum and unwanted <= max_contamination,
            }

        report = {
            "benchmarkVersion": 5,
            "benchmarkType": "three-way-register-gated-instrument-separation",
            "protectedAnalyzer": raw_results["lead"].get("engineVersion"),
            "policy": policy,
            "rawSummaries": raw_summaries,
            "separatedSummaries": separated_summaries,
            "checks": checks,
            "passed": all(check["passed"] for check in checks.values()),
            "workerRepairs": [
                "v46.group_assignments<-v19.group_assignments",
                "v15.create_tab<-inventory_only_tab",
            ],
        }

        outputs: dict[str, Any] = {}
        for part in ("lead", "rhythm", "bass"):
            output = dict(raw_results[part])
            output["rawEvents"] = raw_events[part]
            output["events"] = separated_events[part]
            output["instrumentSeparationPolicy"] = policy[part]
            outputs[part] = output

        return json.dumps(
            {"results": outputs, "report": report},
            default=json_default,
            separators=(",", ":"),
        ).encode("utf-8")
    finally:
        Path(temporary_path).unlink(missing_ok=True)


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway2_instrument_separation_reference.json",
    report_output: str = "/tmp/gomyway2-instrument-v5-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload_bytes = analyse_three_way.remote(audio_file.read_bytes(), audio_file.name, fixture)
    payload = json.loads(bytes(payload_bytes).decode("utf-8"))
    report = payload["report"]

    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    for part, result in payload["results"].items():
        Path(f"/tmp/gomyway2-{part}-v5-result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )

    print("JIMMY PAIGE THREE-WAY INSTRUMENT SEPARATION BENCHMARK V5")
    print("=" * 66)
    print("Protected analyzer:", report.get("protectedAnalyzer"))
    print("Policy:", report.get("policy"))

    print("\nRaw inventories")
    for part in ("lead", "rhythm", "bass"):
        print(part, (report.get("rawSummaries") or {}).get(part, {}).get("registerCounts"))

    print("\nSeparated inventories")
    for part in ("lead", "rhythm", "bass"):
        print(part, (report.get("separatedSummaries") or {}).get(part, {}).get("registerCounts"))

    print("\nThree-way separation")
    for part in ("bass", "rhythm", "lead"):
        check = (report.get("checks") or {}).get(part, {})
        print(
            f"{part.title()} isolates its register:",
            "PASS" if check.get("passed") else "FAIL",
            f"observed={check.get('observedEventCount')}",
            f"minimum={check.get('minimumEventCount')}",
            f"contamination={check.get('contaminationRatio')}",
        )

    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("\nSaved report:", report_output)
    print("Saved results: /tmp/gomyway2-{lead,rhythm,bass}-v5-result.json")
    print("V71 and both locked regression baselines remain unchanged.")
