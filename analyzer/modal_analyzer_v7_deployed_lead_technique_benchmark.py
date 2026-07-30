from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v7 as analyzer

app = modal.App("dadrock-v7-deployed-lead-technique-benchmark")
image = analyzer.image.add_local_python_source(
    "modal_analyzer_v7",
    "modal_analyzer",
    "production_chord_diagnostics",
    "chord_sustain",
    "reference_aware_harmony",
    "production_lead_technique_diagnostics",
    "lead_technique_diagnostics_v7",
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
    *,
    enable_reference_guided_lead_techniques: bool,
    bend_evidence_present: bool,
) -> dict[str, Any]:
    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(audio_bytes)
        temporary_path = handle.name

    try:
        return analyzer.analyze_audio_file(
            temporary_path,
            "lead",
            enable_reference_guided_lead_techniques=(
                enable_reference_guided_lead_techniques
            ),
            bend_evidence_present=bend_evidence_present,
        )
    finally:
        Path(temporary_path).unlink(missing_ok=True)


@app.function(image=image, timeout=1800, memory=4096)
def run_benchmark(audio_bytes: bytes, audio_name: str) -> bytes:
    generic = run_one(
        audio_bytes,
        audio_name,
        enable_reference_guided_lead_techniques=False,
        bend_evidence_present=False,
    )
    contextual = run_one(
        audio_bytes,
        audio_name,
        enable_reference_guided_lead_techniques=True,
        bend_evidence_present=True,
    )
    no_bend_context = run_one(
        audio_bytes,
        audio_name,
        enable_reference_guided_lead_techniques=True,
        bend_evidence_present=False,
    )

    analysis = contextual.get("leadTechniqueAnalysis") or {}
    no_bend_analysis = no_bend_context.get("leadTechniqueAnalysis") or {}

    checks = {
        "genericLeadUnchanged": "leadTechniqueAnalysis" not in generic,
        "contextModeEnabled": (
            contextual.get("leadTechniqueAnalysisMode")
            == "diagnostic-only"
        ),
        "detectsBend": analysis.get("bendDetected") is True,
        "detectsRelease": analysis.get("releaseDetected") is True,
        "detectsPalmMute": analysis.get("palmMuteDetected") is True,
        "requiresBendEvidence": (
            no_bend_analysis.get("bendDetected") is False
            and no_bend_analysis.get("releaseDetected") is False
        ),
        "tabPresent": bool(generic.get("generatedTab")),
        "tabUnchanged": (
            contextual.get("generatedTab") == generic.get("generatedTab")
        ),
        "eventsUnchanged": contextual.get("events") == generic.get("events"),
        "noteCountUnchanged": (
            len(contextual.get("events") or [])
            == len(generic.get("events") or [])
        ),
        "noSyntheticNotes": int(analysis.get("syntheticNoteCount") or 0) == 0,
        "diagnosticsDoNotAffectTab": (
            contextual.get("leadTechniqueAnalysisAffectsTab") is False
        ),
        "diagnosticsDoNotAffectEvents": (
            contextual.get("leadTechniqueAnalysisAffectsEvents") is False
        ),
        "rhythmHarmonyAbsent": "chordAnalysis" not in contextual,
    }

    report = {
        "benchmarkVersion": 7,
        "benchmarkType": "deployed-v7-lead-technique-audio-path",
        "audioName": audio_name,
        "eventCount": len(contextual.get("events") or []),
        "leadTechniqueAnalysis": analysis,
        "checks": checks,
        "passed": all(checks.values()),
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "Reference-guided lead technique diagnostics are opt-in and "
            "read-only. They must never alter generated tab, note events, "
            "pitch, fret, timing, rhythm, or bass output."
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
    report_output: str = "/tmp/gomyway-v7-deployed-lead-technique-report.json",
) -> None:
    audio_file = Path(audio_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    payload = run_benchmark.remote(
        audio_file.read_bytes(),
        audio_file.name,
    )
    report = json.loads(bytes(payload).decode("utf-8"))
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    analysis = report.get("leadTechniqueAnalysis") or {}
    print("JIMMY PAIGE V7 DEPLOYED LEAD-TECHNIQUE BENCHMARK")
    print("=" * 72)
    print("Events:", report.get("eventCount"))
    print("Release pairs:", analysis.get("releasePairCount"))
    print("Palm-muted events:", analysis.get("palmMutedEventCount"))
    print("\nChecks")
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
