from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYZER_DIR = ROOT / "analyzer"
if str(ANALYZER_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYZER_DIR))

from intro_fingering_normalization_v8 import normalize_intro_fingering
from modal_analyzer_v8_notation_benchmark import app, run_benchmark

AUDIO_PATH = ROOT / "public" / "gomywayfullaitest.m4a"
FIXTURE_PATH = ROOT / "analyzer" / "fixtures" / "gomyway_full_chord_sustain_reference.json"
OUTPUT_PATH = ROOT / "public" / "gomyway-full-song-v8-notation.json"


def main() -> None:
    audio_bytes = AUDIO_PATH.read_bytes()
    fixture = json.loads(FIXTURE_PATH.read_text())

    with app.run():
        result_bytes = run_benchmark.remote(
            audio_bytes,
            AUDIO_PATH.name,
            fixture,
        )

    report = json.loads(result_bytes.decode("utf-8"))
    motif_events = (
        report.get("motifStabilizedEvents")
        or report.get("renderEvents")
        or report.get("rhythmEvents")
        or []
    )
    normalized_events, fingering_diagnostics = normalize_intro_fingering(motif_events)
    report["fingeringNormalizedEvents"] = normalized_events
    report["fingeringDiagnostics"] = fingering_diagnostics

    checks = dict(report.get("checks") or {})
    checks["fingeringEventsPresent"] = bool(normalized_events)
    checks["fingeringCountUnchanged"] = len(normalized_events) == len(motif_events)
    checks["normalizedPitchPreserved"] = fingering_diagnostics.get("pitchPreserved") is True
    report["checks"] = checks
    report["passed"] = all(checks.values())

    OUTPUT_PATH.write_text(json.dumps(report, indent=2))

    print(f"Wrote: {OUTPUT_PATH}")
    print(f"Passed: {report.get('passed')}")
    print(f"Protected V7 unchanged: {report.get('protectedBaselinesChanged') is False}")
    print(f"Rhythm events: {len(report.get('rhythmEvents', []))}")
    print(f"Measures: {report.get('totalMeasures')}")
    print(
        "Intro fingerings normalized:",
        fingering_diagnostics.get("changedIntroFingerings"),
    )
    print(
        "Normalized pitch preserved:",
        fingering_diagnostics.get("pitchPreserved"),
    )


if __name__ == "__main__":
    main()
