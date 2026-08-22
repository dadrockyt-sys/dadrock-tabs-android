from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-v2.json"
ANCHOR_PATH = ROOT / "public" / "gomyway-full-song-v8-professional-rhythm-anchor.json"
OUTPUT_PATH = ROOT / "public" / "gomyway-full-song-intro-slot-recall-audit-v2.json"

INTRO_MEASURES = range(1, 17)
DEFAULT_LOCAL_STEPS = [2, 4, 6, 9, 11, 14]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def event_measure(event: dict[str, Any]) -> int | None:
    value = event.get("measureNumber", event.get("measure"))
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def event_step(event: dict[str, Any]) -> int | None:
    value = event.get("quantizedStep", event.get("step"))
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def reference_local_steps(anchor: dict[str, Any]) -> list[int]:
    raw = anchor.get("referencePairSteps")
    if not isinstance(raw, list):
        return DEFAULT_LOCAL_STEPS
    steps: list[int] = []
    for value in raw:
        try:
            step = int(value) % 16
        except (TypeError, ValueError):
            continue
        if step not in steps:
            steps.append(step)
    return sorted(steps) or DEFAULT_LOCAL_STEPS


def main() -> None:
    candidates = load(CANDIDATES_PATH)
    anchor = load(ANCHOR_PATH)

    events = candidates.get("events", candidates.get("candidates", []))
    if not isinstance(events, list):
        raise RuntimeError("Candidate file has no event list")

    expected_steps = reference_local_steps(anchor)
    by_measure: dict[int, set[int]] = {measure: set() for measure in INTRO_MEASURES}

    for event in events:
        if not isinstance(event, dict):
            continue
        measure = event_measure(event)
        step = event_step(event)
        if measure in by_measure and step is not None:
            by_measure[measure].add(step)

    reports: list[dict[str, Any]] = []
    total_expected = len(expected_steps) * len(list(INTRO_MEASURES))
    total_exact = 0
    total_near = 0

    for measure in INTRO_MEASURES:
        detected = sorted(by_measure[measure])
        exact = sorted(set(expected_steps) & set(detected))
        missing = sorted(set(expected_steps) - set(detected))
        extras = sorted(set(detected) - set(expected_steps))
        nearest: dict[str, Any] = {}
        near_matches = 0

        for expected in missing:
            if detected:
                closest = min(detected, key=lambda value: (abs(value - expected), value))
                distance = abs(closest - expected)
                nearest[str(expected)] = {"detectedStep": closest, "distance": distance}
                if distance <= 1:
                    near_matches += 1
            else:
                nearest[str(expected)] = None

        exact_recall = len(exact) / len(expected_steps)
        tolerant_recall = (len(exact) + near_matches) / len(expected_steps)
        total_exact += len(exact)
        total_near += len(exact) + near_matches

        reports.append({
            "measureNumber": measure,
            "expectedSteps": expected_steps,
            "detectedSteps": detected,
            "exactMatches": exact,
            "missingSteps": missing,
            "extraSteps": extras,
            "nearestForMissing": nearest,
            "exactRecall": exact_recall,
            "tolerantRecallWithinOneStep": tolerant_recall,
        })

    exact_average = total_exact / total_expected if total_expected else 0.0
    tolerant_average = total_near / total_expected if total_expected else 0.0
    perfect_measures = [row["measureNumber"] for row in reports if row["exactRecall"] == 1.0]
    weak_measures = [row["measureNumber"] for row in reports if row["exactRecall"] < 0.75]

    ready_for_training = bool(
        candidates.get("readyForFullSongTraining") is True
        or candidates.get("readyForScoredTraining") is True
    )
    ready_for_locked_intro_binding = exact_average >= 0.70 and tolerant_average >= 0.90

    report = {
        "schemaVersion": 2,
        "auditType": "full-song-intro-slot-recall",
        "candidatePath": str(CANDIDATES_PATH.relative_to(ROOT)),
        "anchorPath": str(ANCHOR_PATH.relative_to(ROOT)),
        "expectedLocalSteps": expected_steps,
        "measureReports": reports,
        "exactAverageRecall": exact_average,
        "tolerantAverageRecallWithinOneStep": tolerant_average,
        "perfectMeasures": perfect_measures,
        "weakMeasures": weak_measures,
        "readyForFullSongTrainingInput": ready_for_training,
        "readyForLockedIntroBinding": ready_for_locked_intro_binding,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Full-song intro slot-recall audit V2 complete")
    print("Expected local steps:", expected_steps)
    print("Exact average recall:", round(exact_average, 6))
    print("Tolerant average recall within one step:", round(tolerant_average, 6))
    print("Perfect measures:", perfect_measures)
    print("Weak measures:", weak_measures)
    print("Ready for full-song training input:", ready_for_training)
    print("Ready for locked intro binding:", ready_for_locked_intro_binding)
    print()
    for row in reports:
        print(
            f"measure={row['measureNumber']} "
            f"detected={row['detectedSteps']} "
            f"missing={row['missingSteps']} "
            f"extras={row['extraSteps']} "
            f"exactRecall={row['exactRecall']:.3f} "
            f"tolerantRecall={row['tolerantRecallWithinOneStep']:.3f}"
        )
    print()
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
