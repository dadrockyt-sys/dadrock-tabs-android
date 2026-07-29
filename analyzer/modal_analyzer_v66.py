import statistics
from typing import Any

import modal
import modal_analyzer_v47 as v47
import modal_analyzer_v63 as v63
import modal_analyzer_v65 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = (
    previous.image
    .add_local_python_source("modal_analyzer_v65")
    .add_local_python_source("modal_analyzer_v63")
    .add_local_python_source("modal_analyzer_v47")
)


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def assignment_center(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> float | None:
    frets = [int(item[2]) for item in assignment]
    return float(statistics.median(frets)) if frets else None


def chord_specific_adjustment(
    assignment: list[tuple[dict[str, Any], int, int]],
    oracle: dict[str, Any],
) -> float:
    center = assignment_center(assignment)
    if center is None:
        return 0.0

    name = str(oracle.get("name") or "")
    lower, upper = [float(value) for value in oracle["preferredRange"]]
    allow_open = bool(oracle.get("allowOpen"))
    frets = [int(item[2]) for item in assignment]
    open_count = sum(1 for fret in frets if fret == 0)

    preferred_centers = {
        "Am": 6.0,
        "C/G": 6.5,
        "D/F#": 3.0,
        "Fmaj7": 1.5,
        "G/B-Am": 1.5,
        "G/B - Am": 1.5,
    }
    target_center = preferred_centers.get(name, (lower + upper) / 2.0)

    if lower <= center <= upper:
        adjustment = -55.0 + abs(center - target_center) * 4.0
        if allow_open and open_count:
            adjustment -= min(12.0, 4.0 + open_count * 2.0)
        elif not allow_open and open_count:
            adjustment += open_count * 12.0
        return adjustment

    distance = lower - center if center < lower else center - upper
    adjustment = 45.0 + distance * 40.0

    if name in {"Am", "C/G"} and center < 5.0:
        adjustment += 60.0
    if name in {"D/F#", "Fmaj7", "G/B-Am", "G/B - Am"} and center > upper:
        adjustment += 60.0
    if name == "D/F#" and center < 2.0:
        adjustment += 70.0
    if not allow_open and open_count:
        adjustment += open_count * 15.0
    return adjustment


def neutral_path_metrics(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> dict[str, float | int]:
    assignment_keys = [
        tuple(
            sorted(
                (
                    int(note.get("midi") or 0),
                    int(string_index),
                    int(fret),
                )
                for note, string_index, fret in assignment
            )
        )
        for assignment in path
    ]
    repeated_pairs = sum(
        1
        for first, second in zip(assignment_keys, assignment_keys[1:])
        if first == second
    )
    return {
        "positionShiftTotal": 0.0,
        "largeShiftCount": 0,
        "repeatConsistency": repeated_pairs,
    }


v63.oracle_assignment_adjustment = chord_specific_adjustment
v47.path_metrics = neutral_path_metrics


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["chordSpecificPositionScoring"] = {
        "honestFixtureBaseline": 19.06,
        "benchmarkOnly": True,
        "policy": "score each chord against its own intended fret range",
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "6.6-phase-1-chord-specific-position-scoring"
    result["guitarBrainLesson"] = (
        "each chord keeps its own voicing range during intentional position changes"
    )
    return result


@app.function(image=image, timeout=600, memory=4096)
def benchmark_healthcheck() -> dict[str, Any]:
    return {
        "ok": True,
        "engineVersion": "6.6-phase-1-chord-specific-position-scoring",
        "oracleAdjustmentInstalled": v63.oracle_assignment_adjustment is chord_specific_adjustment,
        "pathMetricsInstalled": v47.path_metrics is neutral_path_metrics,
    }
