"""Benchmark whether Jimmy can keep bass, main guitar, and octave lead distinct.

This is an inventory/separation benchmark only. It does not modify V71 or the
locked Go My Way bend handoff. The worker returns plain JSON bytes so NumPy
objects never cross the Modal boundary.
"""

from __future__ import annotations

import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v71 as analyzer

app = modal.App("dadrock-instrument-separation-benchmark")
image = analyzer.image.add_local_python_source("modal_analyzer_v71")


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


def event_confidence(event: dict[str, Any]) -> float:
    for key in ("confidence", "amplitude", "velocity", "score"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return 1.0


def classify_midi(midi: int, layers: list[dict[str, Any]]) -> str | None:
    for layer in layers:
        low, high = layer["midiRange"]
        if int(low) <= midi <= int(high):
            return str(layer["id"])
    return None


def summarize_result(
    result: dict[str, Any],
    layers: list[dict[str, Any]],
) -> dict[str, Any]:
    raw_events = result.get("events") or []
    events = [event for event in raw_events if isinstance(event, dict)]

    counts: Counter[str] = Counter()
    weighted: Counter[str] = Counter()
    midis: list[int] = []

    for event in events:
        midi = event_midi(event)
        if midi is None:
            continue
        midis.append(midi)
        layer_id = classify_midi(midi, layers)
        if layer_id is None:
            counts["outside"] += 1
            weighted["outside"] += event_confidence(event)
            continue
        counts[layer_id] += 1
        weighted[layer_id] += event_confidence(event)

    return {
        "engineVersion": result.get("engineVersion"),
        "eventCount": len(events),
        "pitchedEventCount": len(midis),
        "minimumMidi": min(midis) if midis else None,
        "maximumMidi": max(midis) if midis else None,
        "medianMidi": (
            sorted(midis)[len(midis) // 2]
            if midis
            else None
        ),
        "layerEventCounts": dict(counts),
        "layerWeightedEvidence": {
            key: round(float(value), 4) for key, value in weighted.items()
        },
        "midiInventory": sorted(Counter(midis).items()),
    }


def ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


@app.function(image=image, timeout=1200, memory=4096)
def analyse_instruments(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
        temporary_file.write(audio_bytes)
        temporary_path = temporary_file.name

    try:
        layers = list(fixture.get("expectedLayers") or [])
        lead_result = analyzer.analyze_audio_file(temporary_path, "lead")
        bass_result = analyzer.analyze_audio_file(temporary_path, "bass")

        lead_summary = summarize_result(lead_result, layers)
        bass_summary = summarize_result(bass_result, layers)

        lead_counts = lead_summary["layerEventCounts"]
        bass_counts = bass_summary["layerEventCounts"]

        lead_primary = float(lead_counts.get("octave-lead", 0))
        lead_bass = float(lead_counts.get("bass", 0))
        bass_primary = float(bass_counts.get("bass", 0))
        bass_lead = float(bass_counts.get("octave-lead", 0))

        expectations = fixture.get("separationExpectations") or {}
        max_lead_bass = float(
            expectations.get("maximumLeadBassContaminationRatio", 0.35)
        )
        max_bass_lead = float(
            expectations.get("maximumBassLeadContaminationRatio", 0.35)
        )

        layer_checks: list[dict[str, Any]] = []
        combined_counts = Counter(lead_counts)
        combined_counts.update(bass_counts)
        for layer in layers:
            layer_id = str(layer["id"])
            minimum = int(layer.get("minimumEventCount") or 1)
            observed = int(combined_counts.get(layer_id, 0))
            layer_checks.append(
                {
                    "layerId": layer_id,
                    "label": layer.get("label"),
                    "minimumEventCount": minimum,
                    "observedEventCount": observed,
                    "passed": observed >= minimum,
                }
            )

        lead_contamination = ratio(lead_bass, lead_primary + lead_bass)
        bass_contamination = ratio(bass_lead, bass_primary + bass_lead)

        report = {
            "benchmarkVersion": 1,
            "benchmarkType": "multi-instrument-register-separation-inventory",
            "protectedAnalyzer": lead_result.get("engineVersion"),
            "leadSummary": lead_summary,
            "bassSummary": bass_summary,
            "layerChecks": layer_checks,
            "leadBassContaminationRatio": lead_contamination,
            "bassLeadContaminationRatio": bass_contamination,
            "maximumLeadBassContaminationRatio": max_lead_bass,
            "maximumBassLeadContaminationRatio": max_bass_lead,
            "leadSeparationPassed": (
                lead_primary > 0 and lead_contamination <= max_lead_bass
            ),
            "bassSeparationPassed": (
                bass_primary > 0 and bass_contamination <= max_bass_lead
            ),
        }
        report["passed"] = bool(
            all(check["passed"] for check in layer_checks)
            and report["leadSeparationPassed"]
            and report["bassSeparationPassed"]
        )

        payload = {
            "leadResult": lead_result,
            "bassResult": bass_result,
            "report": report,
        }
        return json.dumps(
            payload,
            default=json_default,
            separators=(",", ":"),
        ).encode("utf-8")
    finally:
        Path(temporary_path).unlink(missing_ok=True)


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway2_instrument_separation_reference.json",
    report_output: str = "/tmp/gomyway2-instrument-report.json",
    lead_output: str = "/tmp/gomyway2-lead-result.json",
    bass_output: str = "/tmp/gomyway2-bass-result.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload_bytes = analyse_instruments.remote(
        audio_file.read_bytes(),
        audio_file.name,
        fixture,
    )
    payload = json.loads(bytes(payload_bytes).decode("utf-8"))
    report = payload["report"]

    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    Path(lead_output).write_text(
        json.dumps(payload["leadResult"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    Path(bass_output).write_text(
        json.dumps(payload["bassResult"], indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("JIMMY PAIGE SEPARATE-INSTRUMENTS INVENTORY BENCHMARK")
    print("=" * 62)
    print("Protected analyzer:", report.get("protectedAnalyzer"))

    lead = report.get("leadSummary") or {}
    bass = report.get("bassSummary") or {}
    print("Lead event count:", lead.get("eventCount"))
    print("Lead register counts:", lead.get("layerEventCounts"))
    print("Bass event count:", bass.get("eventCount"))
    print("Bass register counts:", bass.get("layerEventCounts"))

    print("\nExpected layers")
    for check in report.get("layerChecks", []):
        status = "PASS" if check.get("passed") else "FAIL"
        print(
            status,
            check.get("layerId"),
            f"observed={check.get('observedEventCount')}",
            f"minimum={check.get('minimumEventCount')}",
        )

    print("\nSeparation")
    print(
        "Lead excludes bass:",
        "PASS" if report.get("leadSeparationPassed") else "FAIL",
        f"contamination={report.get('leadBassContaminationRatio')}",
    )
    print(
        "Bass excludes octave lead:",
        "PASS" if report.get("bassSeparationPassed") else "FAIL",
        f"contamination={report.get('bassLeadContaminationRatio')}",
    )
    print("Overall:", "PASS" if report.get("passed") else "FAIL")

    print("\nSaved lead result:", lead_output)
    print("Saved bass result:", bass_output)
    print("Saved report:", report_output)
    print("V71 and both locked regression baselines remain unchanged.")
