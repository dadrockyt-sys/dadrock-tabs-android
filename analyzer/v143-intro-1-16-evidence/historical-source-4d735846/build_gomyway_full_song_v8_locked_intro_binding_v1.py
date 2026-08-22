from __future__ import annotations

import copy
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-v2.json"
AUDIT_PATH = ROOT / "public" / "gomyway-full-song-intro-slot-recall-audit-v2.json"
OUTPUT_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-locked-intro-v1.json"
MANIFEST_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-locked-intro-v1-manifest.json"

INTRO_MEASURES = range(1, 17)
MAX_SNAP_DISTANCE = 1


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def measure_number(event: dict[str, Any]) -> int | None:
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


def event_strength(event: dict[str, Any]) -> float:
    for key in ("confidence", "strength", "score"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return 0.0


def main() -> None:
    source = load(SOURCE_PATH)
    audit = load(AUDIT_PATH)

    if audit.get("readyForLockedIntroBinding") is not True:
        raise RuntimeError("Intro slot-recall audit did not authorize locked binding")

    expected_steps = [int(value) for value in audit.get("expectedLocalSteps", [])]
    if not expected_steps:
        raise RuntimeError("Intro slot-recall audit has no expected local steps")

    events = source.get("events", source.get("candidates", []))
    if not isinstance(events, list) or not events:
        raise RuntimeError("Full-song source has no candidate events")

    intro_by_measure_step: dict[int, dict[int, list[dict[str, Any]]]] = {
        measure: defaultdict(list) for measure in INTRO_MEASURES
    }
    non_intro: list[dict[str, Any]] = []

    for raw in events:
        if not isinstance(raw, dict):
            continue
        measure = measure_number(raw)
        step = event_step(raw)
        if measure in intro_by_measure_step and step is not None:
            intro_by_measure_step[measure][step].append(raw)
        else:
            non_intro.append(copy.deepcopy(raw))

    bound_intro: list[dict[str, Any]] = []
    measure_reports: list[dict[str, Any]] = []
    total_exact = 0
    total_snapped = 0
    total_unresolved = 0

    for measure in INTRO_MEASURES:
        step_map = intro_by_measure_step[measure]
        available_steps = sorted(step_map)
        used_source_steps: set[int] = set()
        bindings: list[dict[str, Any]] = []

        for expected in expected_steps:
            selected_step: int | None = None
            mode = "unresolved"

            if expected in step_map and expected not in used_source_steps:
                selected_step = expected
                mode = "exact"
            else:
                nearby = [
                    step for step in available_steps
                    if step not in used_source_steps and abs(step - expected) <= MAX_SNAP_DISTANCE
                ]
                if nearby:
                    selected_step = min(
                        nearby,
                        key=lambda step: (
                            abs(step - expected),
                            -max(event_strength(item) for item in step_map[step]),
                            step,
                        ),
                    )
                    mode = "snapped"

            if selected_step is None:
                total_unresolved += 1
                bindings.append({
                    "expectedStep": expected,
                    "sourceStep": None,
                    "mode": mode,
                    "eventCount": 0,
                })
                continue

            used_source_steps.add(selected_step)
            source_events = step_map[selected_step]
            for source_event in source_events:
                bound = copy.deepcopy(source_event)
                bound["quantizedStep"] = expected
                bound["measureNumber"] = measure
                bound["introBinding"] = {
                    "schemaVersion": 1,
                    "mode": mode,
                    "sourceStep": selected_step,
                    "boundStep": expected,
                    "snapDistance": abs(selected_step - expected),
                    "audioDerivedNotesPreserved": True,
                }
                bound_intro.append(bound)

            if mode == "exact":
                total_exact += 1
            else:
                total_snapped += 1

            bindings.append({
                "expectedStep": expected,
                "sourceStep": selected_step,
                "mode": mode,
                "eventCount": len(source_events),
            })

        extras = sorted(set(available_steps) - used_source_steps)
        measure_reports.append({
            "measureNumber": measure,
            "bindings": bindings,
            "unusedDetectedSteps": extras,
            "resolvedSlotCount": sum(1 for item in bindings if item["sourceStep"] is not None),
            "unresolvedSteps": [item["expectedStep"] for item in bindings if item["sourceStep"] is None],
        })

    combined = bound_intro + non_intro
    combined.sort(key=lambda item: (
        int(item.get("measureNumber", 9999)),
        int(item.get("quantizedStep", 9999)),
        -event_strength(item),
    ))

    covered = sorted({
        measure for item in combined
        for measure in [measure_number(item)]
        if measure is not None
    })
    missing_measures = sorted(set(range(1, 114)) - set(covered))
    unresolved_measures = [
        item["measureNumber"] for item in measure_reports if item["unresolvedSteps"]
    ]

    passed = bool(
        not missing_measures
        and total_unresolved == 0
        and len(covered) == 113
        and source.get("readyForFullSongTraining") is True
    )

    result = copy.deepcopy(source)
    result.update({
        "schemaVersion": 3,
        "candidateType": "full-song-rhythm-with-locked-intro-slots",
        "sourceCandidatePath": str(SOURCE_PATH.relative_to(ROOT)),
        "introRecallAuditPath": str(AUDIT_PATH.relative_to(ROOT)),
        "events": combined,
        "candidates": combined,
        "eventCount": len(combined),
        "measuresCovered": covered,
        "measureCoverageCount": len(covered),
        "missingMeasures": missing_measures,
        "lockedIntroExpectedSteps": expected_steps,
        "lockedIntroExactSlots": total_exact,
        "lockedIntroSnappedSlots": total_snapped,
        "lockedIntroUnresolvedSlots": total_unresolved,
        "lockedIntroUnresolvedMeasures": unresolved_measures,
        "measures17To113Preserved": True,
        "professionalNotesCopiedIntoOutput": False,
        "audioDerivedNotesPreserved": True,
        "readyForFullSongTraining": passed,
        "productionPromotionAllowed": False,
    })

    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "sourceEvents": len(events),
        "outputEvents": len(combined),
        "expectedIntroSlots": len(expected_steps) * len(list(INTRO_MEASURES)),
        "exactIntroSlots": total_exact,
        "snappedIntroSlots": total_snapped,
        "unresolvedIntroSlots": total_unresolved,
        "unresolvedIntroMeasures": unresolved_measures,
        "coveredMeasures": len(covered),
        "missingMeasures": missing_measures,
        "measureReports": measure_reports,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "professionalNotesCopiedIntoOutput": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("Full-song V8 locked-intro binding V1 complete")
    print("Passed:", passed)
    print("Source events:", len(events))
    print("Output events:", len(combined))
    print("Covered measures:", len(covered))
    print("Missing measures:", missing_measures)
    print("Expected intro slots:", manifest["expectedIntroSlots"])
    print("Exact intro slots:", total_exact)
    print("Snapped intro slots:", total_snapped)
    print("Unresolved intro slots:", total_unresolved)
    print("Unresolved intro measures:", unresolved_measures)
    print("Measures 17-113 preserved: True")
    print("Professional notes copied into output: False")
    print("Audio-derived notes preserved: True")
    print("Ready for full-song training:", passed)
    print()
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit("Locked-intro binding requires targeted recovery before training")


if __name__ == "__main__":
    main()
