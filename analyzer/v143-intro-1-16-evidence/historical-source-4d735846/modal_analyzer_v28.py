import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v27 as previous

engine = previous.engine
v25 = previous.previous.previous
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v27")


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def held_shape_assignment_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    """Score one note group as part of a realistic left-hand shape."""
    if not assignment:
        return 0.0

    strings = [int(string_index) for _, string_index, _ in assignment]
    frets = [int(fret) for _, _, fret in assignment]
    fretted = [fret for fret in frets if fret > 0]

    if len(set(strings)) != len(strings):
        return 1000.0

    cost = 0.0
    if fretted:
        center = float(statistics.median(fretted))
        span = max(fretted) - min(fretted)
        cost += abs(center - float(anchor)) * 1.55
        cost += span * 1.6
        if span > 4:
            cost += (span - 4) * 9.0
        if max(fretted) > 15:
            cost += (max(fretted) - 15) * 3.0

    if len(strings) > 1:
        string_span = max(strings) - min(strings)
        skipped = string_span + 1 - len(set(strings))
        cost += string_span * 0.35
        cost += skipped * 3.2

    open_count = sum(1 for fret in frets if fret == 0)
    if transcription_type != "bass":
        if anchor <= 2:
            cost -= min(open_count, 3) * 0.45
        elif open_count:
            cost += open_count * 2.6

    if transcription_type == "lead":
        highest = max(assignment, key=lambda item: int(item[0]["midi"]))
        cost += -1.7 if int(highest[1]) <= 2 else 1.8

    return cost


def held_shape_transition_cost(
    prior: list[tuple[dict[str, Any], int, int]] | None,
    current: list[tuple[dict[str, Any], int, int]],
    anchor: int,
) -> float:
    """Reward keeping a fretted hand shape while an arpeggio moves through it."""
    if not current:
        return 0.0

    cost = 0.0
    current_fretted = [int(fret) for _, _, fret in current if int(fret) > 0]
    if current_fretted:
        current_center = float(statistics.median(current_fretted))
        cost += abs(current_center - float(anchor)) * 1.1

    if not prior:
        return cost

    prior_map = {int(string_index): int(fret) for _, string_index, fret in prior}
    current_map = {int(string_index): int(fret) for _, string_index, fret in current}

    shared_strings = set(prior_map) & set(current_map)
    for string_index in shared_strings:
        if prior_map[string_index] == current_map[string_index]:
            cost -= 3.4
        else:
            cost += abs(prior_map[string_index] - current_map[string_index]) * 1.1

    prior_fretted = [fret for fret in prior_map.values() if fret > 0]
    if prior_fretted and current_fretted:
        prior_center = float(statistics.median(prior_fretted))
        current_center = float(statistics.median(current_fretted))
        shift = abs(current_center - prior_center)
        cost += shift * 2.1
        if shift > 3:
            cost += (shift - 3) * 6.0

    prior_strings = [int(item[1]) for item in prior]
    current_strings = [int(item[1]) for item in current]
    string_shift = abs(
        float(statistics.mean(current_strings))
        - float(statistics.mean(prior_strings))
    )
    cost += string_shift * 0.8
    if string_shift > 2:
        cost += (string_shift - 2) * 3.0

    if len(prior) == 1 and len(current) == 1:
        prior_note, prior_string, prior_fret = prior[0]
        current_note, current_string, current_fret = current[0]
        if int(prior_note["midi"]) == int(current_note["midi"]):
            if int(prior_string) == int(current_string) and int(prior_fret) == int(current_fret):
                cost -= 4.0
            else:
                cost += 3.0
        if int(prior_string) == int(current_string):
            distance = abs(int(current_fret) - int(prior_fret))
            cost += max(0, distance - 4) * 2.0

    current_start = min(float(note["start"]) for note, _, _ in current)
    ringing_strings = {
        int(string_index)
        for note, string_index, _ in prior
        if float(note.get("end") or note["start"]) > current_start + 0.04
    }
    reused_ringing = sum(
        1 for _, string_index, _ in current if int(string_index) in ringing_strings
    )
    cost += reused_ringing * 4.2

    return cost


# Replace both callbacks used inside v25's phrase beam search.
v25.guitarist_assignment_cost = held_shape_assignment_cost
v25.phrase_movement_cost = held_shape_transition_cost


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    result["engineVersion"] = "2.8-held-shape-continuity"
    result["guitarBrainLesson"] = "preserve-left-hand-shapes-across-arpeggios"
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
