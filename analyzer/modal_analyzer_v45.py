import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v44 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v44")

v25 = previous.v25
LOW_BASS_MIDI_MAX = previous.LOW_BASS_MIDI_MAX


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def assignment_region(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> dict[str, Any]:
    upper = [
        (note, int(string_index), int(fret))
        for note, string_index, fret in assignment
        if int(note["midi"]) > LOW_BASS_MIDI_MAX
    ]
    positive = [fret for _, _, fret in upper if fret > 0]
    opens = sum(1 for _, _, fret in upper if fret == 0)
    center = float(statistics.median(positive)) if positive else None

    if center is None:
        region = "open"
    elif center <= 3.0:
        region = "low"
    elif center <= 9.0:
        region = "mid"
    else:
        region = "high"

    return {
        "region": region,
        "upperCenter": round(center, 2) if center is not None else None,
        "upperOpenCount": opens,
        "upperFrets": positive,
        "positions": [
            {
                "midi": int(note["midi"]),
                "stringIndex": string_index,
                "fret": fret,
            }
            for note, string_index, fret in assignment
        ],
    }


_original_build_phrase_paths = v25.build_phrase_paths
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
    for rank, (score, path) in enumerate(paths[:4], start=1):
        group_summaries = [assignment_region(assignment) for assignment in path]
        regions = [item["region"] for item in group_summaries]
        candidates.append(
            {
                "rank": rank,
                "score": round(float(score), 3),
                "scoreDeltaFromWinner": round(float(score - paths[0][0]), 3),
                "regions": regions,
                "groups": group_summaries,
            }
        )

    _PATH_DIAGNOSTICS.append(
        {
            "phraseIndex": len(_PATH_DIAGNOSTICS),
            "phraseStart": phrase_start,
            "anchor": int(anchor),
            "groupCount": len(groups),
            "topCandidates": candidates,
            "bestByRegion": {
                region: next(
                    (
                        {
                            "rank": candidate["rank"],
                            "score": candidate["score"],
                            "scoreDeltaFromWinner": candidate["scoreDeltaFromWinner"],
                        }
                        for candidate in candidates
                        if region in candidate["regions"]
                    ),
                    None,
                )
                for region in ("open", "low", "mid", "high")
            },
        }
    )
    return paths


v25.build_phrase_paths = diagnostic_build_phrase_paths


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _PATH_DIAGNOSTICS.clear()
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["topPathDiagnostics"] = {
        "benchmarkBaseline": 53.0,
        "phraseCount": len(_PATH_DIAGNOSTICS),
        "phrases": list(_PATH_DIAGNOSTICS),
        "policy": (
            "inspect-the-winning-path-and-the-nearest-open-low-mid-and-high-"
            "alternatives-before-changing-any-more-weights"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "4.5-phase-1-top-path-diagnostics"
    result["guitarBrainLesson"] = (
        "show-why-the-winning-fingering-beats-each-regional-alternative"
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
