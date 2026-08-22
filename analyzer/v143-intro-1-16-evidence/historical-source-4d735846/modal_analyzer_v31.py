import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v30 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v30")


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def safe_harmony_voicing_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    """V29 harmony scorer copied locally so V30 cannot call itself recursively."""
    cost = previous.previous.previous.held_shape_assignment_cost(
        assignment,
        transcription_type,
        anchor,
    )

    chord = previous.previous.ACTIVE_HARMONY.get("chord")
    confidence = float(previous.previous.ACTIVE_HARMONY.get("confidence") or 0.0)
    texture = str(previous.previous.ACTIVE_HARMONY.get("texture") or "unknown")

    if not chord or confidence < 0.45 or transcription_type == "bass":
        return cost

    voicing = previous.previous.OPEN_VOICINGS.get(str(chord))
    if voicing is None and "/" in str(chord):
        voicing = previous.previous.OPEN_VOICINGS.get(str(chord).split("/", 1)[0])

    if voicing:
        matched = 0
        mismatched = 0
        for _, string_index, fret in assignment:
            string_index = int(string_index)
            fret = int(fret)
            if string_index in voicing:
                if int(voicing[string_index]) == fret:
                    matched += 1
                else:
                    mismatched += 1

        cost -= matched * (2.8 + confidence * 2.0)
        cost += mismatched * (0.8 + confidence * 1.2)

        if texture in {"arpeggio", "chordal"} and anchor <= 2:
            cost -= matched * 0.8

    return cost


# Repair the callback chain created by V30:
# bass_voice_cost -> V29 harmony scorer -> V28 held-shape scorer.
previous.previous.harmony_voicing_cost = safe_harmony_voicing_cost
previous.previous.v25.guitarist_assignment_cost = previous.bass_voice_cost


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    result["engineVersion"] = "3.1-phase-1-recursion-safe"
    result["guitarBrainLesson"] = "harmony-sequence-with-nonrecursive-scoring"
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
