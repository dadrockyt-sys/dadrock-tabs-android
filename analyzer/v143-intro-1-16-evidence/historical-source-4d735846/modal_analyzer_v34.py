import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v33 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v33")

# Reach the Phase 1 module without changing its scoring callback chain.
v31 = previous.previous
v30 = v31.previous
v29 = v30.previous


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def group_start(group: list[dict[str, Any]]) -> float:
    return min(float(note["start"]) for note in group)


def group_end(group: list[dict[str, Any]]) -> float:
    return max(float(note.get("end") or note["start"]) for note in group)


def estimate_beat_interval(
    groups: list[list[dict[str, Any]]],
) -> float | None:
    """Estimate a stable beat-sized interval from onset spacing.

    This is intentionally conservative. It ignores tiny flam/arpeggio gaps and
    large phrase breaks, then folds likely subdivisions up toward a beat.
    """
    if len(groups) < 3:
        return None

    starts = [group_start(group) for group in groups]
    gaps = [
        later - earlier
        for earlier, later in zip(starts, starts[1:])
        if 0.09 <= later - earlier <= 1.25
    ]
    if not gaps:
        return None

    median_gap = float(statistics.median(gaps))
    beat = median_gap
    while beat < 0.32:
        beat *= 2.0
    while beat > 0.95:
        beat /= 2.0
    return max(0.28, min(0.95, beat))


def rhythm_aware_harmonic_windows(
    phrase: list[list[dict[str, Any]]],
) -> list[list[list[dict[str, Any]]]]:
    """Split harmony near musical pulse boundaries instead of fixed seconds."""
    if not phrase:
        return []

    beat = estimate_beat_interval(phrase)
    if beat is None:
        return v29._ORIGINAL_SPLIT_HARMONIC_WINDOWS(phrase)

    windows: list[list[list[dict[str, Any]]]] = []
    current: list[list[dict[str, Any]]] = []
    window_start = group_start(phrase[0])
    target_length = beat * 2.0
    maximum_length = beat * 4.0

    for group in phrase:
        start = group_start(group)
        elapsed = start - window_start
        gap = start - group_start(current[-1]) if current else 0.0

        near_two_beats = elapsed >= target_length * 0.82
        near_four_beats = elapsed >= maximum_length * 0.82
        phrase_break = gap >= beat * 1.55
        overcrowded = len(current) >= 8

        should_break = bool(current) and (
            phrase_break
            or near_four_beats
            or overcrowded
            or (near_two_beats and len(current) >= 3)
        )

        if should_break:
            windows.append(current)
            current = []
            window_start = start

        current.append(group)

    if current:
        windows.append(current)
    return windows


# Preserve the original fallback before installing the rhythm-aware splitter.
if not hasattr(v29, "_ORIGINAL_SPLIT_HARMONIC_WINDOWS"):
    v29._ORIGINAL_SPLIT_HARMONIC_WINDOWS = v29.split_harmonic_windows
v29.split_harmonic_windows = rhythm_aware_harmonic_windows


def build_rhythm_diagnostics(events: list[dict[str, Any]]) -> dict[str, Any]:
    if not events:
        return {
            "estimatedBeatSeconds": None,
            "estimatedTempoBpm": None,
            "onsetCount": 0,
        }

    grouped: dict[float, list[dict[str, Any]]] = {}
    for event in events:
        start = round(float(event.get("start") or 0.0), 3)
        grouped.setdefault(start, []).append(event)

    onset_groups = [grouped[key] for key in sorted(grouped)]
    beat = estimate_beat_interval(onset_groups)
    tempo = round(60.0 / beat, 1) if beat else None
    return {
        "estimatedBeatSeconds": round(beat, 3) if beat else None,
        "estimatedTempoBpm": tempo,
        "onsetCount": len(onset_groups),
        "windowStrategy": "pulse-aware-two-to-four-beat-harmony",
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    events = list(result.get("events") or [])
    rhythm = build_rhythm_diagnostics(events)

    musical_understanding = dict(result.get("musicalUnderstanding") or {})
    musical_understanding["rhythm"] = rhythm
    result["musicalUnderstanding"] = musical_understanding
    if rhythm.get("estimatedTempoBpm"):
        result["tempo"] = rhythm["estimatedTempoBpm"]

    result["engineVersion"] = "3.4-phase-1-rhythm-aware-harmony"
    result["guitarBrainLesson"] = (
        "align-harmonic-decisions-to-musical-pulse-before-fret-assignment"
    )
    return result


@app.function(
    image=image,
    timeout=600,
    memory=4096,
    secrets=[modal.Secret.from_name("dadrock-analyzer-secret")],
)
@modal.fastapi_endpoint(method="POST")
def analyze(payload: dict) -> dict:
    import requests
    from fastapi import HTTPException

    expected_token = os.environ.get("ANALYZER_API_TOKEN")
    supplied_token = str(payload.get("token") or "")
    if not expected_token or supplied_token != expected_token:
        raise HTTPException(status_code=401, detail="Unauthorized analyzer request.")

    audio_url = str(payload.get("audioUrl") or "").strip()
    transcription_type = str(payload.get("transcriptionType") or "").strip().lower()
    if transcription_type not in {"lead", "rhythm", "bass"}:
        raise HTTPException(
            status_code=400,
            detail="transcriptionType must be lead, rhythm, or bass.",
        )
    if not audio_url.startswith(("https://", "http://")):
        raise HTTPException(status_code=400, detail="A valid audioUrl is required.")

    suffix = Path(audio_url).suffix.lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        suffix = ".audio"

    headers: dict[str, str] = {}
    blob_token = str(payload.get("blobToken") or "").strip()
    if blob_token:
        headers["Authorization"] = f"Bearer {blob_token}"

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / f"uploaded{suffix}"
        try:
            response = requests.get(audio_url, headers=headers, timeout=120)
        except requests.RequestException as error:
            raise HTTPException(
                status_code=502,
                detail="The analyzer could not download the audio file.",
            ) from error

        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail="The analyzer could not download the audio file.",
            )
        if len(response.content) > engine.MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="The uploaded audio cannot be larger than 50 MB.",
            )

        audio_path.write_bytes(response.content)
        try:
            original_metadata = engine.inspect_audio_file(str(audio_path))
            engine.validate_audio_metadata(original_metadata)
            normalized_path = Path(temp_dir) / "normalized.wav"
            engine.normalize_audio_file(str(audio_path), str(normalized_path))
            normalized_metadata = engine.inspect_audio_file(str(normalized_path))
            result = analyze_audio_file(str(normalized_path), transcription_type)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        result["audioMetadata"] = original_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }

    return to_json_safe(result)
