from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v7 as analyzer

app = modal.App("dadrock-v7-combined-full-stack-benchmark")
image = analyzer.image.add_local_python_source(
    "modal_analyzer_v7",
    "modal_analyzer",
    "production_chord_diagnostics",
    "chord_sustain",
    "reference_aware_harmony",
    "production_lead_technique_diagnostics",
    "lead_technique_diagnostics_v7",
    "production_bass_technique_diagnostics",
    "bass_technique_diagnostics_v7",
)


def json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def same_production_output(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        left.get("generatedTab") == right.get("generatedTab")
        and left.get("events") == right.get("events")
        and len(left.get("events") or []) == len(right.get("events") or [])
    )


def run_all(
    audio_path: str,
    reference_chords: list[dict[str, Any]],
    expected_progression: list[str],
) -> dict[str, dict[str, Any]]:
    rhythm_generic = analyzer.analyze_audio_file(audio_path, "rhythm")
    rhythm_contextual = analyzer.analyze_audio_file(
        audio_path,
        "rhythm",
        reference_chords=reference_chords,
        expected_progression=expected_progression,
    )
    lead_generic = analyzer.analyze_audio_file(audio_path, "lead")
    lead_contextual = analyzer.analyze_audio_file(
        audio_path,
        "lead",
        enable_reference_guided_lead_techniques=True,
        bend_evidence_present=True,
    )
    bass_generic = analyzer.analyze_audio_file(audio_path, "bass")
    bass_contextual = analyzer.analyze_audio_file(
        audio_path,
        "bass",
        enable_reference_guided_bass_techniques=True,
    )
    return {
        "rhythmGeneric": rhythm_generic,
        "rhythmContextual": rhythm_contextual,
        "leadGeneric": lead_generic,
        "leadContextual": lead_contextual,
        "bassGeneric": bass_generic,
        "bassContextual": bass_contextual,
    }


@app.function(image=image, timeout=2400, memory=4096)
def run_benchmark(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    reference_chords = [
        chord for chord in fixture.get("chords", []) if isinstance(chord, dict)
    ]
    expected_progression = [
        str(name) for name in fixture.get("expectedProgression", [])
    ]

    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(audio_bytes)
        temporary_path = handle.name

    try:
        results = run_all(
            temporary_path,
            reference_chords,
            expected_progression,
        )
    finally:
        Path(temporary_path).unlink(missing_ok=True)

    rhythm_generic = results["rhythmGeneric"]
    rhythm_contextual = results["rhythmContextual"]
    lead_generic = results["leadGeneric"]
    lead_contextual = results["leadContextual"]
    bass_generic = results["bassGeneric"]
    bass_contextual = results["bassContextual"]

    chord_analysis = rhythm_contextual.get("chordAnalysis") or {}
    chord_vocabulary = set(chord_analysis.get("chordVocabulary") or [])
    promotions = chord_analysis.get("referenceAwarePromotions") or {}
    lead_analysis = lead_contextual.get("leadTechniqueAnalysis") or {}
    bass_analysis = bass_contextual.get("bassTechniqueAnalysis") or {}

    checks = {
        "rhythmGenericHasNoReferenceMode": (
            (rhythm_generic.get("chordAnalysis") or {}).get("referenceAwareMode")
            is None
        ),
        "rhythmContextEnabled": (
            chord_analysis.get("referenceAwareMode") == "verified-context-two-tone"
        ),
        "rhythmPromotesE": promotions.get("E") is True and "E" in chord_vocabulary,
        "rhythmPromotesG": promotions.get("G") is True and "G" in chord_vocabulary,
        "rhythmPreservesG6": "G6" in chord_vocabulary,
        "rhythmPreservesATp2": "A(tp2)" in chord_vocabulary,
        "rhythmProductionUnchanged": same_production_output(
            rhythm_generic, rhythm_contextual
        ),
        "leadGenericUnchanged": "leadTechniqueAnalysis" not in lead_generic,
        "leadContextEnabled": (
            lead_contextual.get("leadTechniqueAnalysisMode") == "diagnostic-only"
        ),
        "leadDetectsBend": lead_analysis.get("bendDetected") is True,
        "leadDetectsRelease": lead_analysis.get("releaseDetected") is True,
        "leadDetectsPalmMute": lead_analysis.get("palmMuteDetected") is True,
        "leadProductionUnchanged": same_production_output(
            lead_generic, lead_contextual
        ),
        "bassGenericUnchanged": "bassTechniqueAnalysis" not in bass_generic,
        "bassContextEnabled": (
            bass_contextual.get("bassTechniqueAnalysisMode") == "diagnostic-only"
        ),
        "bassDetectsFiveSevenContour": (
            bass_analysis.get("contour5And7Detected") is True
        ),
        "bassDetectsSlide": bass_analysis.get("slideDetected") is True,
        "bassDetectsMute": bass_analysis.get("mutedAttackDetected") is True,
        "bassDetectsRest": bass_analysis.get("restDetected") is True,
        "bassProductionUnchanged": same_production_output(
            bass_generic, bass_contextual
        ),
        "rhythmReceivesNoLeadAnalysis": (
            "leadTechniqueAnalysis" not in rhythm_contextual
        ),
        "rhythmReceivesNoBassAnalysis": (
            "bassTechniqueAnalysis" not in rhythm_contextual
        ),
        "leadReceivesNoChordAnalysis": "chordAnalysis" not in lead_contextual,
        "leadReceivesNoBassAnalysis": (
            "bassTechniqueAnalysis" not in lead_contextual
        ),
        "bassReceivesNoChordAnalysis": "chordAnalysis" not in bass_contextual,
        "bassReceivesNoLeadAnalysis": (
            "leadTechniqueAnalysis" not in bass_contextual
        ),
        "rhythmNoSyntheticNotes": chord_analysis.get("noSyntheticNotes") is True,
        "leadNoSyntheticNotes": int(lead_analysis.get("syntheticNoteCount") or 0) == 0,
        "bassNoSyntheticNotes": int(bass_analysis.get("syntheticNoteCount") or 0) == 0,
        "allTabsPresent": all(
            bool(result.get("generatedTab"))
            for result in (rhythm_generic, lead_generic, bass_generic)
        ),
    }

    report = {
        "benchmarkVersion": 7,
        "benchmarkType": "combined-v7-rhythm-lead-bass-full-stack-audio-path",
        "audioName": audio_name,
        "eventCounts": {
            "rhythm": len(rhythm_contextual.get("events") or []),
            "lead": len(lead_contextual.get("events") or []),
            "bass": len(bass_contextual.get("events") or []),
        },
        "rhythm": {
            "vocabulary": sorted(chord_vocabulary),
            "promotions": promotions,
        },
        "lead": lead_analysis,
        "bass": bass_analysis,
        "checks": checks,
        "passed": all(checks.values()),
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "V7 rhythm harmony, lead techniques, and bass techniques are opt-in, "
            "read-only, and instrument-isolated. No diagnostic may change generated "
            "tab, events, note count, pitch, fret, or timing."
        ),
    }
    return json.dumps(
        report,
        default=json_default,
        separators=(",", ":"),
    ).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_full_chord_sustain_reference.json",
    report_output: str = "/tmp/gomyway-v7-combined-full-stack-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
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

    print("JIMMY PAIGE V7 COMBINED FULL-STACK BENCHMARK")
    print("=" * 72)
    print("Event counts:", report.get("eventCounts"))
    print("Rhythm vocabulary:", (report.get("rhythm") or {}).get("vocabulary"))
    print("Rhythm promotions:", (report.get("rhythm") or {}).get("promotions"))
    print("Lead release pairs:", (report.get("lead") or {}).get("releasePairCount"))
    print("Lead palm-muted events:", (report.get("lead") or {}).get("palmMutedEventCount"))
    print("Bass 5/7 contour:", (report.get("bass") or {}).get("contour5And7Detected"))
    print("Bass slide target:", (report.get("bass") or {}).get("slideTargetFret"))
    print("\nChecks")
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
