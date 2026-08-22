import os
import statistics
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v45 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v45")

v25 = previous.v25
LOW_BASS_MIDI_MAX = previous.LOW_BASS_MIDI_MAX


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def assignment_region(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> dict[str, Any]:
    return previous.assignment_region(assignment)


def path_region_profile(path: list[list[tuple[dict[str, Any], int, int]]]) -> dict[str, Any]:
    summaries = [assignment_region(assignment) for assignment in path]
    regions = [item["region"] for item in summaries]
    counts = Counter(regions)

    positive_centers = [
        float(item["upperCenter"])
        for item in summaries
        if item.get("upperCenter") is not None
    ]
    path_center = (
        float(statistics.median(positive_centers))
        if positive_centers
        else None
    )

    if path_center is None:
        dominant = "open"
    elif path_center <= 3.0:
        dominant = "low"
    elif path_center <= 9.0:
        dominant = "mid"
    else:
        dominant = "high"

    return {
        "dominantRegion": dominant,
        "pathUpperCenter": round(path_center, 2) if path_center is not None else None,
        "regionCounts": {
            region: int(counts.get(region, 0))
            for region in ("open", "low", "mid", "high")
        },
        "regions": regions,
        "groups": summaries,
    }


_original_build_phrase_paths = previous._original_build_phrase_paths
_PATH_DIAGNOSTICS: list[dict[str, Any]] = []


def diagnostic_build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    paths = _original_build_phrase_paths(
        groups,
        transcription_type,
        anchor,
        previous_assignment,
    )

    phrase_start = None
    if groups and groups[0]:
        phrase_start = round(float(groups[0][0].get("start") or 0.0), 3)

    candidates: list[dict[str, Any]] = []
    winner_score = float(paths[0][0]) if paths else 0.0

    for rank, (score, path) in enumerate(paths[:8], start=1):
        profile = path_region_profile(path)
        candidates.append(
            {
                "rank": rank,
                "score": round(float(score), 3),
                "scoreDeltaFromWinner": round(float(score) - winner_score, 3),
                **profile,
            }
        )

    best_by_dominant_region = {
        region: next(
            (
                {
                    "rank": candidate["rank"],
                    "score": candidate["score"],
                    "scoreDeltaFromWinner": candidate["scoreDeltaFromWinner"],
                    "pathUpperCenter": candidate["pathUpperCenter"],
                    "regionCounts": candidate["regionCounts"],
                }
                for candidate in candidates
                if candidate["dominantRegion"] == region
            ),
            None,
        )
        for region in ("open", "low", "mid", "high")
    }

    _PATH_DIAGNOSTICS.append(
        {
            "phraseIndex": len(_PATH_DIAGNOSTICS),
            "phraseStart": phrase_start,
            "anchor": int(anchor),
            "groupCount": len(groups),
            "winnerDominantRegion": (
                candidates[0]["dominantRegion"] if candidates else None
            ),
            "winnerUpperCenter": (
                candidates[0]["pathUpperCenter"] if candidates else None
            ),
            "topCandidates": candidates,
            "bestByDominantRegion": best_by_dominant_region,
        }
    )
    return paths


# Replace v45's ambiguous "contains region" diagnostic with whole-path labels.
v25.build_phrase_paths = diagnostic_build_phrase_paths


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _PATH_DIAGNOSTICS.clear()
    result = previous.previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["dominantPathDiagnostics"] = {
        "benchmarkBaseline": 53.0,
        "phraseCount": len(_PATH_DIAGNOSTICS),
        "phrases": list(_PATH_DIAGNOSTICS),
        "policy": (
            "classify-each-complete-candidate-path-by-its-median-upper-hand-region-"
            "so-one-mixed-path-cannot-pretend-to-be-open-low-mid-and-high-at-once"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "4.6-phase-1-dominant-path-diagnostics"
    result["guitarBrainLesson"] = (
        "compare-distinct-whole-path-regions-instead-of-counting-one-mixed-path-as-every-alternative"
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
