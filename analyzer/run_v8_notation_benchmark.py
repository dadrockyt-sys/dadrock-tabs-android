from __future__ import annotations

import json
from pathlib import Path

from modal_analyzer_v8_notation_benchmark import app, run_benchmark

ROOT = Path(__file__).resolve().parents[1]
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
    OUTPUT_PATH.write_text(json.dumps(report, indent=2))

    print(f"Wrote: {OUTPUT_PATH}")
    print(f"Passed: {report.get('passed')}")
    print(f"Protected V7 unchanged: {report.get('protectedBaselinesChanged') is False}")
    print(f"Rhythm events: {len(report.get('rhythmEvents', []))}")
    print(f"Measures: {report.get('totalMeasures')}")


if __name__ == "__main__":
    main()
