from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

from run_jimmy_paige_em_riff_extraction_training_loop import REPO_ROOT

SOURCE_PATH = (
    REPO_ROOT / "public" / "gomyway-jimmy-paige-em-riff-b-step-10-diagnosis.json"
)
OUTPUT_PATH = (
    REPO_ROOT / "public" / "gomyway-jimmy-paige-em-riff-b-step-10-timing-diagnosis.json"
)
TARGET_MIDI = 45


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required diagnosis: {path}")
    return json.loads(path.read_text())


def main() -> None:
    source = _load(SOURCE_PATH)
    occurrences: list[dict[str, Any]] = []

    for occurrence_index, window in enumerate(source.get("windows", []), start=1):
        target = float(window.get("target") or 0.0)
        candidates = [
            event
            for event in window.get("events", [])
            if int(event.get("midiPitch", -1)) == TARGET_MIDI
        ]
        candidates.sort(
            key=lambda event: (
                abs(float(event.get("deltaSeconds") or 0.0)),
                -float(event.get("confidence") or 0.0),
            )
        )

        if candidates:
            best = candidates[0]
            occurrences.append(
                {
                    "occurrence": occurrence_index,
                    "target": round(target, 6),
                    "midiPitch": TARGET_MIDI,
                    "start": best.get("start"),
                    "deltaSeconds": round(float(best.get("deltaSeconds") or 0.0), 6),
                    "confidence": best.get("confidence"),
                    "candidateCount": len(candidates),
                }
            )
        else:
            occurrences.append(
                {
                    "occurrence": occurrence_index,
                    "target": round(target, 6),
                    "midiPitch": TARGET_MIDI,
                    "candidateCount": 0,
                }
            )

    deltas = [
        float(item["deltaSeconds"])
        for item in occurrences
        if item.get("deltaSeconds") is not None
    ]

    median_delta = statistics.median(deltas) if deltas else None
    deviations = (
        [abs(delta - median_delta) for delta in deltas]
        if median_delta is not None
        else []
    )
    median_absolute_deviation = (
        statistics.median(deviations) if deviations else None
    )

    consistent = bool(
        len(deltas) >= 3
        and median_absolute_deviation is not None
        and median_absolute_deviation <= 0.12
    )

    recommendation = (
        "apply-slot-specific-timing-correction"
        if consistent
        else "retain-8-of-9-and-investigate-occurrence-variation"
    )

    report = {
        "benchmarkVersion": 8,
        "diagnosisType": "jimmy-paige-em-riff-b-step-10-timing-correction",
        "source": str(SOURCE_PATH.relative_to(REPO_ROOT)),
        "expectedMidiPitch": TARGET_MIDI,
        "occurrencesInspected": len(occurrences),
        "occurrencesWithMidi45": len(deltas),
        "medianDeltaSeconds": (
            round(median_delta, 6) if median_delta is not None else None
        ),
        "medianAbsoluteDeviationSeconds": (
            round(median_absolute_deviation, 6)
            if median_absolute_deviation is not None
            else None
        ),
        "timingPatternConsistent": consistent,
        "recommendedNextAction": recommendation,
        "occurrences": occurrences,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Jimmy PAIge final-slot timing diagnosis")
    print(f"Occurrences inspected: {len(occurrences)}")
    print(f"Occurrences containing MIDI 45: {len(deltas)}")
    print(f"Median delta: {report['medianDeltaSeconds']} seconds")
    print(
        "Median absolute deviation: "
        f"{report['medianAbsoluteDeviationSeconds']} seconds"
    )
    print(f"Consistent timing pattern: {consistent}")
    print(f"Recommended next action: {recommendation}")
    for item in occurrences:
        if item.get("deltaSeconds") is None:
            print(f"- occurrence {item['occurrence']}: MIDI 45 not found")
        else:
            print(
                f"- occurrence {item['occurrence']}: "
                f"delta={item['deltaSeconds']}s | "
                f"confidence={item.get('confidence')}"
            )
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
