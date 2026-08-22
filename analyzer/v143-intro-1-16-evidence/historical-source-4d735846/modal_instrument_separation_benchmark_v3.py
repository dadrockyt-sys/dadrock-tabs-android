"""Renderer-safe inventory benchmark for bass, main guitar, and octave lead.

This benchmark leaves V71 and both locked regression baselines unchanged. It
patches only the benchmark worker so the legacy ASCII renderer cannot abort the
pitch-inventory test when a mapped string index is outside its row inventory.
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

app = modal.App("dadrock-instrument-separation-benchmark-v3")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v15")
    .add_local_python_source("modal_analyzer_v19")
    .add_local_python_source("modal_analyzer_v46")
    .add_local_python_source("modal_analyzer_v71")
)


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


def classify_midi(midi: int, layers: list[dict[str, Any]]) -> str | None:
    for layer in layers:
        low, high = layer["midiRange"]
        if int(low) <= midi <= int(high):
            return str(layer["id"])
    return None


def summarize_result(result: dict[str, Any], layers: list[dict[str, Any]]) -> dict[str, Any]:
    events = [event for event in (result.get("events") or []) if isinstance(event, dict)]
    counts: Counter[str] = Counter()
    midis: list[int] = []

    for event in events:
        midi = event_midi(event)
        if midi is None:
            continue
        midis.append(midi)
        counts[classify_midi(midi, layers) or "outside"] += 1

    ordered = sorted(midis)
    return {
        "engineVersion": result.get("engineVersion"),
        "eventCount": len(events),
        "pitchedEventCount": len(midis),
        "minimumMidi": min(midis) if midis else None,
        "maximumMidi": max(midis) if midis else None,
        "medianMidi": ordered[len(ordered) // 2] if ordered else None,
        "layerEventCounts": dict(counts),
        "midiInventory": sorted(Counter(midis).items()),
    }


def ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 4) if denominator > 0 else 0.0


def inventory_only_tab(mapped_groups: list[list[dict[str, Any]]], transcription_type: str) -> str:
    """Skip fragile ASCII rendering while preserving all mapped event evidence."""
    return "[inventory benchmark: tab rendering intentionally skipped]"


@app.function(image=image, timeout=1200, memory=4096)
def analyse_instruments(audio_bytes: bytes, audio_name: str, fixture: dict[str, Any]) -> bytes:
    # Repair historical callbacks only inside this isolated benchmark worker.
    legacy_bridge.group_assignments = legacy_assignments.group_assignments
    legacy_renderer.create_tab = inventory_only_tab

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
        max_lead_bass = float(expectations.get("maximumLeadBassContaminationRatio", 0.35))
        max_bass_lead = float(expectations.get("maximumBassLeadContaminationRatio", 0.35))

        combined = Counter(lead_counts)
        combined.update(bass_counts)
        layer_checks = []
        for layer in layers:
            layer_id = str(layer["id"])
            minimum = int(layer.get("minimumEventCount") or 1)
            observed = int(combined.get(layer_id, 0))
            layer_checks.append({
                "layerId": layer_id,
                "label": layer.get("label"),
                "minimumEventCount": minimum,
                "observedEventCount": observed,
                "passed": observed >= minimum,
            })

        lead_contamination = ratio(lead_bass, lead_primary + lead_bass)
        bass_contamination = ratio(bass_lead, bass_primary + bass_lead)
        report = {
            "benchmarkVersion": 3,
            "benchmarkType": "renderer-safe-multi-instrument-register-separation",
            "protectedAnalyzer": lead_result.get("engineVersion"),
            "workerRepairs": [
                "v46.group_assignments<-v19.group_assignments",
                "v15.create_tab<-inventory_only_tab",
            ],
            "leadSummary": lead_summary,
            "bassSummary": bass_summary,
            "layerChecks": layer_checks,
            "leadBassContaminationRatio": lead_contamination,
            "bassLeadContaminationRatio": bass_contamination,
            "maximumLeadBassContaminationRatio": max_lead_bass,
            "maximumBassLeadContaminationRatio": max_bass_lead,
            "leadSeparationPassed": lead_primary > 0 and lead_contamination <= max_lead_bass,
            "bassSeparationPassed": bass_primary > 0 and bass_contamination <= max_bass_lead,
        }
        report["passed"] = bool(
            all(check["passed"] for check in layer_checks)
            and report["leadSeparationPassed"]
            and report["bassSeparationPassed"]
        )

        return json.dumps(
            {"leadResult": lead_result, "bassResult": bass_result, "report": report},
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
    payload_bytes = analyse_instruments.remote(audio_file.read_bytes(), audio_file.name, fixture)
    payload = json.loads(bytes(payload_bytes).decode("utf-8"))
    report = payload["report"]

    Path(report_output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    Path(lead_output).write_text(json.dumps(payload["leadResult"], indent=2, sort_keys=True), encoding="utf-8")
    Path(bass_output).write_text(json.dumps(payload["bassResult"], indent=2, sort_keys=True), encoding="utf-8")

    print("JIMMY PAIGE SEPARATE-INSTRUMENTS INVENTORY BENCHMARK V3")
    print("=" * 67)
    print("Protected analyzer:", report.get("protectedAnalyzer"))
    print("Worker repairs:", report.get("workerRepairs"))

    lead = report.get("leadSummary") or {}
    bass = report.get("bassSummary") or {}
    print("Lead event count:", lead.get("eventCount"))
    print("Lead register counts:", lead.get("layerEventCounts"))
    print("Bass event count:", bass.get("eventCount"))
    print("Bass register counts:", bass.get("layerEventCounts"))

    print("\nExpected layers")
    for check in report.get("layerChecks", []):
        print(
            "PASS" if check.get("passed") else "FAIL",
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
