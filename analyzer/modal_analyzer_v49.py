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
LOW_BASS_MIDI_MAX = previous.LOW_BASS_MIDI_MAX
_original_v47_builder = previous.reranked_build_phrase_paths
_HIGH_FAILURE_DIAGNOSTICS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def path_profile(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> dict[str, Any]:
    return previous.previous.path_region_profile(path)


def upper_midi_notes(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> list[int]:
    return sorted(
        {
            int(note["midi"])
            for assignment in path
            for note, _, _ in assignment
            if int(note["midi"]) > LOW_BASS_MIDI_MAX
        }
    )


def mid_positions_for_midi(
    midi: int,
    transcription_type: str,
) -> list[dict[str, int]]:
    return [
        {"stringIndex": int(string_index), "fret": int(fret)}
        for string_index, fret in engine.playable_positions(
            int(midi),
            transcription_type,
        )
        if 4 <= int(fret) <= 9
    ]


def path_mid_eligibility(
    path: list[list[tuple[dict[str, Any], int, int]]],
    transcription_type: str,
) -> dict[str, Any]:
    notes = upper_midi_notes(path)
    blocked: list[dict[str, Any]] = []
    available: dict[str, list[dict[str, int]]] = {}

    for midi in notes:
        positions = mid_positions_for_midi(midi, transcription_type)
        if positions:
            available[str(midi)] = positions
        else:
            blocked.append({"midi": midi, "reason": "no-fret-4-to-9-position"})

    return {
        "allUpperNotesHaveMidOptions": not blocked and bool(notes),
        "blockedMidiNotes": blocked,
        "midPositionsByMidi": available,
    }


def diagnostic_build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    paths = _original_v47_builder(
        groups,
        transcription_type,
        anchor,
        previous_assignment,
    )

    if not paths:
        return paths

    winner_score, winner_path = paths[0]
    winner_profile = path_profile(winner_path)
    winner_center = winner_profile.get("pathUpperCenter")
    winner_center_value = float(winner_center) if winner_center is not None else 0.0

    mid_candidates: list[dict[str, Any]] = []
    for rank, (score, path) in enumerate(paths, start=1):
        profile = path_profile(path)
        center = profile.get("pathUpperCenter")
        center_value = float(center) if center is not None else 0.0
        if 4.0 <= center_value <= 9.0:
            mid_candidates.append(
                {
                    "rank": rank,
                    "score": round(float(score), 3),
                    "scoreGapFromWinner": round(float(score - winner_score), 3),
                    "pathUpperCenter": round(center_value, 2),
                    "regionCounts": profile.get("regionCounts"),
                    "eligibility": path_mid_eligibility(path, transcription_type),
                }
            )

    if winner_center_value > 9.0:
        phrase_start = None
        if groups and groups[0]:
            phrase_start = round(float(groups[0][0].get("start") or 0.0), 3)

        _HIGH_FAILURE_DIAGNOSTICS.append(
            {
                "phraseIndex": len(_HIGH_FAILURE_DIAGNOSTICS),
                "phraseStart": phrase_start,
                "anchor": int(anchor),
                "winner": {
                    "score": round(float(winner_score), 3),
                    "pathUpperCenter": round(winner_center_value, 2),
                    "dominantRegion": winner_profile.get("dominantRegion"),
                    "regionCounts": winner_profile.get("regionCounts"),
                    "eligibility": path_mid_eligibility(
                        winner_path,
                        transcription_type,
                    ),
                },
                "closestMidCandidate": (
                    min(mid_candidates, key=lambda item: item["score"])
                    if mid_candidates
                    else None
                ),
                "midCandidateCount": len(mid_candidates),
            }
        )

    return paths


v25.build_phrase_paths = diagnostic_build_phrase_paths


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _HIGH_FAILURE_DIAGNOSTICS.clear()
    result = previous.previous.previous.previous.previous.analyze_audio_file(
        audio_path,
        transcription_type,
    )
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["highPositionFailureDiagnostics"] = {
        "benchmarkBaseline": 63.0,
        "highPathThreshold": 9.0,
        "phraseCount": len(_HIGH_FAILURE_DIAGNOSTICS),
        "phrases": list(_HIGH_FAILURE_DIAGNOSTICS),
        "policy": (
            "inspect-only-high-winning-phrases-and-report-the-closest-true-mid-"
            "candidate-score-gap-plus-any-midi-notes-that-block-mid-eligibility"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "4.9-phase-1-high-position-failure-diagnostics"
    result["guitarBrainLesson"] = (
        "measure-the-exact-mid-path-gap-and-midi-eligibility-before-changing-the-green-v47-reranker"
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
