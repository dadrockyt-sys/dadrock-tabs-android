import json
import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v38 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v38")


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def compact_inventory(result: dict[str, Any]) -> dict[str, Any]:
    inventory = (
        result.get("musicalUnderstanding", {})
        .get("candidateInventory", {})
    )
    groups = list(inventory.get("groups") or [])

    compact_groups: list[dict[str, Any]] = []
    for group in groups:
        buckets = dict(group.get("candidateBucketCounts") or {})
        compact_groups.append(
            {
                "g": group.get("groupIndex"),
                "a": group.get("anchor"),
                "n": group.get("noteCount"),
                "cand": group.get("generatedCandidateCount"),
                "open": buckets.get("open", 0),
                "low": buckets.get("low", 0),
                "mid": buckets.get("mid", 0),
                "high": buckets.get("high", 0),
                "midOK": bool(group.get("midCandidateAvailable")),
                "notesNoMid": [
                    note.get("midi")
                    for note in group.get("notes", [])
                    if not note.get("hasMidNeckPosition")
                ],
            }
        )

    return {
        "engineVersion": result.get("engineVersion"),
        "groupCount": inventory.get("groupCount"),
        "groupsWithoutMidCandidates": inventory.get("groupsWithoutMidCandidates"),
        "notesWithoutMidNeckPositions": inventory.get("notesWithoutMidNeckPositions"),
        "groups": compact_groups,
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    result["engineVersion"] = "3.9-phase-1-compact-inventory-logs"
    result["guitarBrainLesson"] = (
        "print-compact-candidate-inventory-so-missing-mid-neck-options-are-visible"
    )

    summary = compact_inventory(result)
    print("JIMMY_PAIGE_INVENTORY_START", flush=True)
    print(json.dumps(summary, separators=(",", ":"), sort_keys=True), flush=True)
    print("JIMMY_PAIGE_INVENTORY_END", flush=True)
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
