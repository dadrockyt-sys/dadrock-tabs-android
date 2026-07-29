import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v47 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v47")

v25 = previous.v25
_original_builder = previous.reranked_build_phrase_paths
_original_renderer = v25.render_path
_PENDING_ANCHOR_CALLS: list[dict[str, Any]] = []
_CROSS_ANCHOR_WINDOWS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def path_profile(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> dict[str, Any]:
    return previous.previous.path_region_profile(path)


def traced_build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    paths = _original_builder(
        groups,
        transcription_type,
        anchor,
        previous_assignment,
    )
    phrase_start = None
    if groups and groups[0]:
        phrase_start = round(float(groups[0][0].get("start") or 0.0), 4)

    _PENDING_ANCHOR_CALLS.append(
        {
            "anchor": int(anchor),
            "phraseStart": phrase_start,
            "paths": paths,
        }
    )
    return paths


def traced_render_path(
    winning_path: list[list[tuple[dict[str, Any], int, int]]],
) -> list[list[dict[str, Any]]]:
    selected_call = None
    selected_rank = None
    selected_score = None

    candidates: list[dict[str, Any]] = []
    for call in _PENDING_ANCHOR_CALLS:
        for rank, (score, path) in enumerate(call["paths"], start=1):
            profile = path_profile(path)
            candidate = {
                "anchor": call["anchor"],
                "rankWithinAnchor": rank,
                "scoreBeforeAnchorShift": round(float(score), 3),
                "pathUpperCenter": profile.get("pathUpperCenter"),
                "dominantRegion": profile.get("dominantRegion"),
                "regionCounts": profile.get("regionCounts"),
            }
            candidates.append(candidate)
            if path == winning_path and selected_call is None:
                selected_call = call
                selected_rank = rank
                selected_score = float(score)

    selected_profile = path_profile(winning_path)
    selected_center = selected_profile.get("pathUpperCenter")
    selected_center_value = float(selected_center) if selected_center is not None else 0.0

    true_mid = [
        candidate
        for candidate in candidates
        if candidate["pathUpperCenter"] is not None
        and 4.0 <= float(candidate["pathUpperCenter"]) <= 9.0
    ]
    closest_mid = min(
        true_mid,
        key=lambda item: item["scoreBeforeAnchorShift"],
        default=None,
    )

    window_start = selected_call.get("phraseStart") if selected_call else None
    _CROSS_ANCHOR_WINDOWS.append(
        {
            "windowIndex": len(_CROSS_ANCHOR_WINDOWS),
            "windowStart": window_start,
            "selectedAnchor": selected_call.get("anchor") if selected_call else None,
            "selectedRankWithinAnchor": selected_rank,
            "selectedScoreBeforeAnchorShift": (
                round(selected_score, 3) if selected_score is not None else None
            ),
            "selectedUpperCenter": round(selected_center_value, 2),
            "selectedDominantRegion": selected_profile.get("dominantRegion"),
            "closestMidAcrossAnchors": closest_mid,
            "candidateCount": len(candidates),
            "anchorsEvaluated": sorted({item["anchor"] for item in candidates}),
            "highWinner": selected_center_value > 9.0,
            "topAcrossAnchorsBeforeShift": sorted(
                candidates,
                key=lambda item: item["scoreBeforeAnchorShift"],
            )[:12],
        }
    )
    _PENDING_ANCHOR_CALLS.clear()
    return _original_renderer(winning_path)


v25.build_phrase_paths = traced_build_phrase_paths
v25.render_path = traced_render_path


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _PENDING_ANCHOR_CALLS.clear()
    _CROSS_ANCHOR_WINDOWS.clear()
    result = previous.analyze_audio_file(audio_path, transcription_type)

    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["crossAnchorWinnerDiagnostics"] = {
        "benchmarkBaseline": 63.0,
        "windowCount": len(_CROSS_ANCHOR_WINDOWS),
        "highWinnerCount": sum(
            1 for item in _CROSS_ANCHOR_WINDOWS if item.get("highWinner")
        ),
        "windows": list(_CROSS_ANCHOR_WINDOWS),
        "policy": (
            "trace-every-reranked-path-for-every-anchor-then-identify-the-path-"
            "actually-selected-after-anchor-shift-and-cross-anchor-sorting"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "5.3-phase-1-cross-anchor-winner-diagnostics"
    result["guitarBrainLesson"] = (
        "measure-whether-a-mid-neck-path-wins-inside-an-anchor-but-loses-during-final-cross-anchor-selection"
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
        raise HTTPException(status_code=400, detail="transcriptionType must be lead, rhythm, or bass.")
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
            raise HTTPException(status_code=502, detail="The analyzer could not download the audio file.") from error
        if not response.ok:
            raise HTTPException(status_code=502, detail="The analyzer could not download the audio file.")
        if len(response.content) > engine.MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="The uploaded audio cannot be larger than 50 MB.")

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
