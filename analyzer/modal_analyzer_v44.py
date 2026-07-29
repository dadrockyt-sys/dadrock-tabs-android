import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v43 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v43")

v25 = previous.v25
LOW_BASS_MIDI_MAX = previous.LOW_BASS_MIDI_MAX


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def upper_notes(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> list[tuple[dict[str, Any], int, int]]:
    return [
        item for item in assignment
        if int(item[0]["midi"]) > LOW_BASS_MIDI_MAX
    ]


def upper_open_count(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> int:
    return sum(1 for _, _, fret in upper_notes(assignment) if int(fret) == 0)


def upper_center(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> float | None:
    frets = [int(fret) for _, _, fret in upper_notes(assignment) if int(fret) > 0]
    return float(statistics.median(frets)) if frets else None


def upper_span(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> int:
    frets = [int(fret) for _, _, fret in upper_notes(assignment) if int(fret) > 0]
    return max(frets) - min(frets) if len(frets) >= 2 else 0


base_assignment_cost = previous.equivalent_region_assignment_cost


def anchor_aware_assignment_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    """Keep a phrase in its established region until harmony supports a move.

    V43 proved that simply rewarding mid-neck candidates was insufficient. This
    lesson adds regional hysteresis directly to each assignment. A mid-neck
    phrase resists both open-string collapse and unnecessary climbing, while a
    genuinely low anchor is allowed to release into an open-position cadence.
    """
    cost = base_assignment_cost(assignment, transcription_type, anchor)

    if previous.is_low_bass_assignment(assignment):
        return cost

    notes = upper_notes(assignment)
    if not notes:
        return cost

    center = upper_center(assignment)
    opens = upper_open_count(assignment)
    span = upper_span(assignment)
    all_have_mid = previous.all_upper_notes_have_mid_options(
        assignment,
        transcription_type,
    )

    # Established mid-neck phrase: resist open-string collapse and parking above
    # the normal 5-8 box. These costs act before beam pruning.
    if int(anchor) >= 4:
        if opens and all_have_mid:
            cost += opens * 22.0
        if center is not None:
            if center < 4.0 and all_have_mid:
                cost += 18.0 + (4.0 - center) * 5.0
            elif 5.0 <= center <= 8.0:
                cost -= 10.0
            elif center > 8.0 and all_have_mid:
                cost += 10.0 + (center - 8.0) * 7.0

    # Low-anchor cadence: allow the hand to release, and stop the persistent
    # upper-memory system from dragging a genuine open-position ending upward.
    elif int(anchor) <= 3:
        if center is None or center <= 5.0:
            cost -= 8.0
        elif center > 5.0:
            cost += 10.0 + (center - 5.0) * 6.0
        if opens:
            cost -= min(6.0, opens * 2.0)

    # Compactness remains a universal guitar constraint.
    if span <= 4:
        cost -= 2.5
    else:
        cost += (span - 4) * 6.0

    return cost


v25.guitarist_assignment_cost = anchor_aware_assignment_cost


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["regionalHysteresis"] = {
        "benchmarkBaseline": 53.0,
        "midAnchorThreshold": 4,
        "midTargetFrets": [5, 8],
        "lowCadenceMaximumFret": 5,
        "policy": (
            "hold-the-established-mid-neck-region-until-a-low-harmonic-anchor-"
            "supports-an-open-position-release"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "4.4-phase-1-anchor-aware-regional-hysteresis"
    result["guitarBrainLesson"] = (
        "resist-open-and-high-region-errors-while-the-phrase-anchor-is-mid-neck-and-release-only-on-a-low-cadence"
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
