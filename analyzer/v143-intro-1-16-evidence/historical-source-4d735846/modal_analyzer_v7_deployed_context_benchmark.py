from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v7 as analyzer

app = modal.App("dadrock-v7-deployed-context-benchmark")
image = analyzer.image.add_local_python_source(
    "modal_analyzer_v7",
    "modal_analyzer",
    "production_chord_diagnostics",
    "chord_sustain",
    "reference_aware_harmony",
)


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
    reference_chords: list[dict[str, Any]] | None = None,
    expected_progression: list[str] | None = None,
) -> dict[str, Any]:
    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(audio_bytes)
        temporary_path = handle.name
    try:
        return analyzer.analyze_audio_file(
            temporary_path,
            transcription_type,
            reference_chords=reference_chords,
            expected_progression=expected_progression,
        )
    finally:
        Path(temporary_path).unlink(missing_ok=True)


@app.function(image=image, timeout=1800, memory=4096)
def run_benchmark(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    reference_chords = [
        chord for chord in fixture.get("chords", [])
        if isinstance(chord, dict)
    ]
    expected_progression = [
        str(name) for name in fixture.get("expectedProgression", [])
    ]

    generic_rhythm = run_one(audio_bytes, audio_name, "rhythm")
    contextual_rhythm = run_one(
        audio_bytes,
        audio_name,
        "rhythm",
        reference_chords,
        expected_progression,
    )
    lead = run_one(audio_bytes, audio_name, "lead", reference_chords, expected_progression)
    bass = run_one(audio_bytes, audio_name, "bass", reference_chords, expected_progression)

    generic_analysis = generic_rhythm.get("chordAnalysis") or {}
    contextual_analysis = contextual_rhythm.get("chordAnalysis") or {}
    generic_vocabulary = set(generic_analysis.get("chordVocabulary") or [])
    contextual_vocabulary = set(contextual_analysis.get("chordVocabulary") or [])
    promotions = contextual_analysis.get("referenceAwarePromotions") or {}

    checks = {
        "genericModeUnchanged": generic_analysis.get("referenceAwareMode") is None,
        "contextModeEnabled": contextual_analysis.get("referenceAwareMode") == "verified-context-two-tone",
        "contextPromotesE": promotions.get("E") is True and "E" in contextual_vocabulary,
        "contextPromotesG": promotions.get("G") is True and "G" in contextual_vocabulary,
        "contextDoesNotPromoteD": promotions.get("D") is not True,
        "preservesExistingD": ("D" in generic_vocabulary) == ("D" in contextual_vocabulary),
        "preservesG6": "G6" in contextual_vocabulary,
        "preservesATp2": "A(tp2)" in contextual_vocabulary,
        "genericTabPresent": bool(generic_rhythm.get("generatedTab")),
        "contextTabUnchanged": contextual_rhythm.get("generatedTab") == generic_rhythm.get("generatedTab"),
        "contextEventsUnchanged": contextual_rhythm.get("events") == generic_rhythm.get("events"),
        "leadReceivesNoChordAnalysis": "chordAnalysis" not in lead,
        "bassReceivesNoChordAnalysis": "chordAnalysis" not in bass,
        "noSyntheticNotes": contextual_analysis.get("noSyntheticNotes") is True,
        "diagnosticsDoNotAffectTab": contextual_rhythm.get("chordAnalysisAffectsTab") is False,
    }

    report = {
        "benchmarkVersion": 7,
        "benchmarkType": "deployed-v7-verified-context-audio-path",
        "audioName": audio_name,
        "genericVocabulary": sorted(generic_vocabulary),
        "contextualVocabulary": sorted(contextual_vocabulary),
        "referenceAwarePromotions": promotions,
        "eventCount": len(contextual_rhythm.get("events") or []),
        "checks": checks,
        "passed": all(checks.values()),
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "Verified context may enrich read-only rhythm diagnostics only. "
            "It must not change generated tab, note events, lead, or bass. "
            "A chord already found generically is preserved even when context does not promote it."
        ),
    }
    return json.dumps(report, default=json_default, separators=(",", ":")).encode("utf-8")


@app.local_entrypoint()
def main(
    layered_audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_full_chord_sustain_reference.json",
    report_output: str = "/tmp/gomyway-v7-deployed-context-report.json",
) -> None:
    audio_file = Path(layered_audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Layered audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload = run_benchmark.remote(audio_file.read_bytes(), audio_file.name, fixture)
    report = json.loads(bytes(payload).decode("utf-8"))
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("JIMMY PAIGE V7 DEPLOYED VERIFIED-CONTEXT BENCHMARK")
    print("=" * 72)
    print("Generic vocabulary:", report.get("genericVocabulary"))
    print("Contextual vocabulary:", report.get("contextualVocabulary"))
    print("Promotions:", report.get("referenceAwarePromotions"))
    print("Event count:", report.get("eventCount"))
    print("\nChecks")
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
