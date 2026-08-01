from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from run_jimmy_paige_em_riff_extraction_training_loop import REPO_ROOT

TIMING_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-em-riff-b-step-10-timing-diagnosis.json"
)
MISS_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-em-riff-b-step-10-diagnosis.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-em-riff-b-step-10-occurrence-variation.json"
)

TARGET_MIDI = 45


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required diagnosis: {path}")
    return json.loads(path.read_text())


def main() -> None:
    timing = _load(TIMING_PATH)
    miss = _load(MISS_PATH)

    windows = miss.get("windows", [])
    occurrence_reports: list[dict[str, Any]] = []
    global_pitch_counts: Counter[int] = Counter()

    for index, window in enumerate(windows, start=1):
        events = window.get("events", [])
        pitch_counts: Counter[int] = Counter()
        closest = None

        for event in events:
            try:
                pitch = int(event.get("midiPitch"))
                delta = float(event.get("deltaSeconds"))
            except (TypeError, ValueError):
                continue

            pitch_counts[pitch] += 1
            global_pitch_counts[pitch] += 1

            if closest is None or abs(delta) < abs(float(closest["deltaSeconds"])):
                closest = {
                    "midiPitch": pitch,
                    "deltaSeconds": round(delta, 6),
                    "confidence": event.get("confidence"),
                }

        expected = [
            event
            for event in events
            if int(event.get("midiPitch", -1)) == TARGET_MIDI
        ]
        expected.sort(key=lambda event: abs(float(event.get("deltaSeconds", 0.0))))

        occurrence_reports.append(
            {
                "occurrence": index,
                "target": window.get("target"),
                "expectedMidi45Present": bool(expected),
                "closestExpectedMidi45": expected[0] if expected else None,
                "closestAnyPitch": closest,
                "dominantNearbyPitches": [
                    {"midiPitch": pitch, "support": count}
                    for pitch, count in pitch_counts.most_common(8)
                ],
            }
        )

    expected_occurrences = sum(
        1 for report in occurrence_reports if report["expectedMidi45Present"]
    )
    missing_occurrences = len(occurrence_reports) - expected_occurrences

    if expected_occurrences >= 4:
        classification = "mostly-present-occurrence-specific-timing"
        next_action = "add-occurrence-aware-timing-window"
    elif expected_occurrences >= 2:
        classification = "mixed-phrase-variation-or-reference-overgeneralization"
        next_action = "compare-professional-tab-occurrence-by-occurrence"
    else:
        classification = "rare-candidate-requires-targeted-extraction"
        next_action = "run-narrow-parameter-sweep-on-missing-occurrences"

    report = {
        "benchmarkVersion": 8,
        "diagnosisType": "jimmy-paige-em-riff-b-step-10-occurrence-variation",
        "targetMidiPitch": TARGET_MIDI,
        "occurrencesInspected": len(occurrence_reports),
        "occurrencesWithExpectedPitch": expected_occurrences,
        "occurrencesWithoutExpectedPitch": missing_occurrences,
        "classification": classification,
        "recommendedNextAction": next_action,
        "timingSummary": {
            "medianDeltaSeconds": timing.get("medianDeltaSeconds"),
            "medianAbsoluteDeviationSeconds": timing.get(
                "medianAbsoluteDeviationSeconds"
            ),
            "consistentTimingPattern": timing.get("consistentTimingPattern"),
        },
        "globalNearbyPitchHistogram": [
            {"midiPitch": pitch, "support": count}
            for pitch, count in global_pitch_counts.most_common(12)
        ],
        "occurrences": occurrence_reports,
        "protectedCheckpointMaintained": True,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Jimmy PAIge final-slot occurrence variation analysis")
    print(
        f"MIDI 45 present in {expected_occurrences}/{len(occurrence_reports)} occurrences"
    )
    print(f"Classification: {classification}")
    print(f"Recommended next action: {next_action}")
    for item in occurrence_reports:
        status = "FOUND" if item["expectedMidi45Present"] else "MISSING"
        print(
            f"- occurrence {item['occurrence']}: {status} | "
            f"closest={item['closestAnyPitch']} | "
            f"dominant={item['dominantNearbyPitches'][:4]}"
        )
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
