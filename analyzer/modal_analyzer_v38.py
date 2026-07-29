import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v37 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v37")

v25 = previous.v25
original_protected_group_assignments = previous.protected_group_assignments

POSITION_INVENTORY: list[dict[str, Any]] = []
GROUP_COUNTER = 0


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def position_region(fret: int) -> str:
    fret = int(fret)
    if fret <= 3:
        return "openLow"
    if fret <= 9:
        return "mid"
    if fret <= 16:
        return "upperMid"
    return "high"


def summarize_positions(
    note: dict[str, Any],
    transcription_type: str,
) -> dict[str, Any]:
    positions = [
        (int(string_index), int(fret))
        for string_index, fret in engine.playable_positions(
            int(note["midi"]),
            transcription_type,
        )
    ]
    counts = {"openLow": 0, "mid": 0, "upperMid": 0, "high": 0}
    for _, fret in positions:
        counts[position_region(fret)] += 1

    return {
        "midi": int(note["midi"]),
        "start": round(float(note.get("start") or 0.0), 3),
        "positionCount": len(positions),
        "regionCounts": counts,
        "positions": [
            {"stringIndex": string_index, "fret": fret}
            for string_index, fret in positions
        ],
        "hasMidNeckPosition": any(4 <= fret <= 9 for _, fret in positions),
    }


def inventory_group_assignments(
    group: list[dict[str, Any]],
    transcription_type: str,
    anchor: int,
) -> list[list[tuple[dict[str, Any], int, int]]]:
    global GROUP_COUNTER

    candidates = original_protected_group_assignments(
        group,
        transcription_type,
        anchor,
    )

    bucket_counts = {"open": 0, "low": 0, "mid": 0, "high": 0}
    for candidate in candidates:
        bucket_counts[previous.candidate_bucket(candidate)] += 1

    POSITION_INVENTORY.append(
        {
            "groupIndex": GROUP_COUNTER,
            "anchor": int(anchor),
            "noteCount": len(group),
            "notes": [
                summarize_positions(note, transcription_type)
                for note in sorted(group, key=lambda item: int(item["midi"]))
            ],
            "generatedCandidateCount": len(candidates),
            "candidateBucketCounts": bucket_counts,
            "midCandidateAvailable": bucket_counts["mid"] > 0,
            "highCandidateAvailable": bucket_counts["high"] > 0,
        }
    )
    GROUP_COUNTER += 1
    return candidates


# Capture the raw inventory at the exact point candidates enter the beam.
v25.all_group_assignments = inventory_group_assignments
# Keep slightly more alternatives alive while the diagnostic version is tested.
v25.PATH_BEAM_WIDTH = max(int(getattr(v25, "PATH_BEAM_WIDTH", 72)), 88)


def summarize_inventory() -> dict[str, Any]:
    groups = list(POSITION_INVENTORY)
    missing_mid = [
        int(item["groupIndex"])
        for item in groups
        if not bool(item.get("midCandidateAvailable"))
    ]
    notes_without_mid = [
        {
            "groupIndex": int(item["groupIndex"]),
            "midi": int(note["midi"]),
            "start": note["start"],
        }
        for item in groups
        for note in item.get("notes", [])
        if not bool(note.get("hasMidNeckPosition"))
    ]

    return {
        "groupCount": len(groups),
        "groupsWithoutMidCandidates": missing_mid,
        "notesWithoutMidNeckPositions": notes_without_mid,
        "beamWidth": int(v25.PATH_BEAM_WIDTH),
        "groups": groups,
        "policy": (
            "record-every-playable-position-and-candidate-region-before-beam-pruning"
        ),
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    global GROUP_COUNTER
    POSITION_INVENTORY.clear()
    GROUP_COUNTER = 0

    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["candidateInventory"] = summarize_inventory()
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "3.8-phase-1-candidate-inventory"
    result["guitarBrainLesson"] = (
        "inspect-every-raw-fretboard-choice-before-changing-scoring-again"
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
