from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v19 as legacy_assignments
import modal_analyzer_v46 as legacy_v46
import modal_analyzer_v73 as analyzer
import modal_gomyway_full_chord_sustain_benchmark as benchmark_v1

# V63's emergency fallback walks the historical module chain until V46.
# V46 predates the exported group_assignments helper, while V19 contains the
# compatible implementation. Restore that helper only inside this diagnostic
# process; no protected analyzer or baseline file is changed.
legacy_v46.group_assignments = legacy_assignments.group_assignments

app = modal.App("dadrock-gomyway-full-chord-sustain-benchmark-v2")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v73")
    .add_local_python_source("modal_analyzer_v19")
    .add_local_python_source("modal_analyzer_v46")
    .add_local_python_source("modal_gomyway_full_chord_sustain_benchmark")
)


def json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, set):
        return sorted(value)
    return str(value)


@app.function(image=image, timeout=3600, memory=4096)
def run_benchmark(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    # Apply inside the Modal worker as well as at module import time.
    legacy_v46.group_assignments = legacy_assignments.group_assignments

    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(audio_bytes)
        audio_path = handle.name

    result = analyzer.analyze_audio_file(audio_path, "rhythm")
    report = benchmark_v1.evaluate(result, fixture)
    report["benchmarkVersion"] = 2
    report["compatibilityRepair"] = (
        "V46 group_assignments restored from compatible V19 helper inside diagnostic worker"
    )
    return json.dumps(
        report,
        default=json_default,
        separators=(",", ":"),
    ).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_full_chord_sustain_reference.json",
    report_output: str = "/tmp/gomyway-full-chord-sustain-v2-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    report_bytes = run_benchmark.remote(
        audio_file.read_bytes(),
        audio_file.name,
        fixture,
    )
    report = json.loads(bytes(report_bytes).decode("utf-8"))
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("JIMMY PAIGE FULL-SONG CHORD STRUCTURE & SUSTAIN BENCHMARK V2")
    print("=" * 72)
    print("Engine:", report.get("engineVersion"))
    print("Events:", report.get("eventCount"))
    print("Duration:", report.get("fullSongDuration"))
    print("Chord clusters:", report.get("chordClusterCount"))
    print("Matched chord clusters:", report.get("matchedChordClusterCount"))
    print("Chord vocabulary:", report.get("chordVocabulary"))
    print("Observed progression:", report.get("observedProgression"))
    print("Sustained chords:", report.get("sustainedChordCount"))
    print("Scores:", report.get("scores"))
    print("Checks:")
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
    print("V71, V72, V73, and all seven locked baselines remain unchanged.")
