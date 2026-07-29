"""Run Jimmy PAIge against a repeatable fixture without deploying the website.

Example:
    modal run analyzer/modal_analyzer_benchmark.py \
        --audio-path ./stairway-test.mp3

Optional:
    modal run analyzer/modal_analyzer_benchmark.py \
        --audio-path ./stairway-test.mp3 \
        --fixture-path analyzer/fixtures/stairway_intro_reference.json \
        --result-output /tmp/jimmy-result.json \
        --report-output /tmp/jimmy-report.json
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v44 as analyzer
import evaluate_fingering

app = modal.App("dadrock-tab-analyzer-benchmark")

image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v44")
    .add_local_python_source("evaluate_fingering")
)


@app.function(
    image=image,
    timeout=900,
    memory=4096,
)
def analyze_and_score(
    audio_bytes: bytes,
    filename: str,
    transcription_type: str,
    fixture: dict[str, Any],
) -> dict[str, Any]:
    suffix = Path(filename).suffix.lower() or ".audio"
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / f"source{suffix}"
        normalized = Path(temp_dir) / "normalized.wav"
        source.write_bytes(audio_bytes)

        original_metadata = analyzer.engine.inspect_audio_file(str(source))
        analyzer.engine.validate_audio_metadata(original_metadata)
        analyzer.engine.normalize_audio_file(str(source), str(normalized))
        normalized_metadata = analyzer.engine.inspect_audio_file(str(normalized))

        result = analyzer.analyze_audio_file(str(normalized), transcription_type)
        result["audioMetadata"] = original_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }
        report = evaluate_fingering.evaluate(result, fixture)
        return {
            "result": analyzer.to_json_safe(result),
            "report": analyzer.to_json_safe(report),
        }


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/stairway_intro_reference.json",
    transcription_type: str = "lead",
    result_output: str = "/tmp/jimmy-result.json",
    report_output: str = "/tmp/jimmy-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)

    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")
    if transcription_type not in {"lead", "rhythm", "bass"}:
        raise ValueError("transcription_type must be lead, rhythm, or bass")

    fixture = evaluate_fingering.load_json(fixture_file)
    payload = analyze_and_score.remote(
        audio_file.read_bytes(),
        audio_file.name,
        transcription_type,
        fixture,
    )

    result = dict(payload["result"])
    report = dict(payload["report"])

    Path(result_output).write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    evaluate_fingering.print_report(report)
    print("\nSaved files")
    print(f"Analyzer result: {result_output}")
    print(f"Benchmark report: {report_output}")
    print("\nUse this same command after every analyzer change.")
    print("Only deploy a new website analyzer when the benchmark score improves.")
