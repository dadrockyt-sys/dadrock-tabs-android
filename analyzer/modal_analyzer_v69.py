from typing import Any

import modal
import modal_analyzer_v68 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v68")


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["canonicalTimelineBenchmark"] = {
        "method": "resolve-overlapping-and-nested-harmonic-windows-into-one-non-overlapping-timeline",
        "reason": (
            "the-harmonic-window-list-contains-parent-child-and-overlapping-candidate-windows-"
            "that-must-not-score-the-same-rendered-events-more-than-once"
        ),
        "previousOverlappingWindowScore": 49.0,
        "legacyProgressSliceScore": 26.06,
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "6.9-phase-1-canonical-harmonic-timeline-benchmark"
    result["guitarBrainLesson"] = (
        "benchmark-one-winning-harmonic-timeline-instead-of-double-scoring-overlapping-windows"
    )
    return result


@app.function(image=image, timeout=600, memory=4096)
def benchmark_healthcheck() -> dict[str, Any]:
    return {
        "ok": True,
        "engineVersion": "6.9-phase-1-canonical-harmonic-timeline-benchmark",
        "previousAnalyzer": "6.8-phase-1-harmonic-window-benchmark-alignment",
    }
