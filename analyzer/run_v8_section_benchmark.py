from __future__ import annotations

import json
from pathlib import Path

from modal_analyzer_v8_section_benchmark import run_benchmark


ROOT = Path(__file__).resolve().parent.parent
AUDIO_PATH = ROOT / "public" / "gomywayfullaitest.m4a"
FIXTURE_PATH = (
    ROOT
    / "analyzer"
    / "fixtures"
    / "gomyway_full_chord_sustain_reference.json"
)
OUTPUT_PATH = ROOT / "public" / "gomyway-full-song-v8-sections.json"


def main() -> None:
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing audio fixture: {AUDIO_PATH}")
    if not FIXTURE_PATH.exists():
        raise FileNotFoundError(f"Missing reference fixture: {FIXTURE_PATH}")

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    result_bytes = run_benchmark.remote(
        AUDIO_PATH.read_bytes(),
        AUDIO_PATH.name,
        fixture,
    )

    report = json.loads(result_bytes.decode("utf-8"))
    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote: {OUTPUT_PATH}")
    print(f"Passed: {report.get('passed')}")
    print("Detected sections:")
    for section in report.get("sections", []):
        print(
            f"  {section.get('label')}: "
            f"measures {section.get('startMeasure')}-"
            f"{section.get('endMeasure')} "
            f"(confidence {section.get('confidence')})"
        )


if __name__ == "__main__":
    main()
