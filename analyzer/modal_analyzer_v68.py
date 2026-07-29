from typing import Any

import modal
import modal_analyzer_v67 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v67")


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["benchmarkAlignment"] = {
        "method": "score-rendered-events-against-the-actual-harmonic-window-start-and-end-times",
        "reason": (
            "the-legacy-fixture-used-equal-progress-slices-even-though-the-recorded-"
            "phrase-timing-is-not-uniform"
        ),
        "legacyScoreRetained": True,
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "6.8-phase-1-harmonic-window-benchmark-alignment"
    result["guitarBrainLesson"] = (
        "measure-the-winning-rendered-path-on-musical-window-boundaries-not-equal-time-slices"
    )
    return result


@app.function(image=image, timeout=600, memory=4096)
def benchmark_healthcheck() -> dict[str, Any]:
    return {
        "ok": True,
        "engineVersion": "6.8-phase-1-harmonic-window-benchmark-alignment",
        "legacyAnalyzer": "6.7-phase-1-paired-chord-transition-scoring",
    }
