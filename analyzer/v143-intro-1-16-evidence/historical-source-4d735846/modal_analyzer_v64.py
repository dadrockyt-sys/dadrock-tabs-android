import statistics
from typing import Any

import modal
import modal_analyzer_v47 as v47
import modal_analyzer_v63 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = (
    previous.image
    .add_local_python_source("modal_analyzer_v63")
    .add_local_python_source("modal_analyzer_v47")
)


def local_path_metrics(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> dict[str, float | int]:
    """Provide the path metrics expected by V63 without legacy dependencies."""
    centers: list[float] = []
    assignment_keys: list[tuple[tuple[int, int, int], ...]] = []

    for assignment in path:
        frets = [int(item[2]) for item in assignment]
        if frets:
            centers.append(float(statistics.median(frets)))

        assignment_keys.append(
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
        )

    shifts = [
        abs(second - first)
        for first, second in zip(centers, centers[1:])
    ]
    repeated_pairs = sum(
        1
        for first, second in zip(assignment_keys, assignment_keys[1:])
        if first == second
    )

    return {
        "positionShiftTotal": round(sum(shifts), 4),
        "largeShiftCount": sum(1 for shift in shifts if shift >= 5.0),
        "repeatConsistency": repeated_pairs,
    }


# V63's runtime lookup reaches modal_analyzer_v47.path_metrics. Older versions of
# that module do not expose it, which caused the benchmark AttributeError.
v47.path_metrics = local_path_metrics


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    result["engineVersion"] = "6.4-phase-1-oracle-beam-path-metrics-fix"
    result["guitarBrainLesson"] = (
        "preserve-target-zone-beam-paths-with-self-contained-path-metrics"
    )
    return result


@app.function(
    image=image,
    timeout=600,
    memory=4096,
)
def benchmark_healthcheck() -> dict[str, Any]:
    return {
        "ok": True,
        "engineVersion": "6.4-phase-1-oracle-beam-path-metrics-fix",
        "pathMetricsInstalled": hasattr(v47, "path_metrics"),
    }
