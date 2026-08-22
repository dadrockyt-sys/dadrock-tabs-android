import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v35 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v35")

# V35 exposes the Phase 1 beam-search module and current harmonic evidence.
v25 = previous.v25
v31 = previous.v31
HARMONIC_EVIDENCE = previous.HARMONIC_EVIDENCE


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def fretted_center(
    assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> float | None:
    if not assignment:
        return None
    frets = [int(fret) for _, _, fret in assignment if int(fret) > 0]
    return float(statistics.median(frets)) if frets else 0.0


def assignment_pitch_classes(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> set[int]:
    return {int(note["midi"]) % 12 for note, _, _ in assignment}


def candidate_harmony_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    """Score the complete candidate shape against the active harmony."""
    cost = previous.evidence_gated_assignment_cost(
        assignment,
        transcription_type,
        anchor,
    )
    if not assignment or transcription_type == "bass":
        return cost

    root = HARMONIC_EVIDENCE.get("root")
    quality = HARMONIC_EVIDENCE.get("quality")
    bass_pc = HARMONIC_EVIDENCE.get("bassPitchClass")
    confidence = float(HARMONIC_EVIDENCE.get("confidence") or 0.0)

    chord_intervals = previous.v29.CHORD_INTERVALS.get(str(quality), ())
    chord_pcs = (
        {(int(root) + int(interval)) % 12 for interval in chord_intervals}
        if root is not None
        else set()
    )
    candidate_pcs = assignment_pitch_classes(assignment)

    if chord_pcs and confidence >= 0.45:
        matched = len(candidate_pcs & chord_pcs)
        outside = len(candidate_pcs - chord_pcs)
        candidate_coverage = matched / max(1, len(candidate_pcs))

        cost -= matched * (0.55 + confidence * 0.45)
        cost += outside * (2.1 + confidence * 2.2)

        if len(assignment) >= 2 and candidate_coverage < 0.67:
            cost += (0.67 - candidate_coverage) * 8.0

    # Reject a low-string bass choice that conflicts with the inferred inversion.
    if bass_pc is not None and confidence >= 0.48:
        lowest = min(assignment, key=lambda item: int(item[0]["midi"]))
        lowest_pc = int(lowest[0]["midi"]) % 12
        lowest_string = int(lowest[1])
        if lowest_string >= 3:
            if lowest_pc == int(bass_pc):
                cost -= 2.5 + confidence
            else:
                cost += 5.5 + confidence * 4.0

    return cost


def phrase_path_transition_cost(
    prior: list[tuple[dict[str, Any], int, int]] | None,
    current: list[tuple[dict[str, Any], int, int]],
    anchor: int,
) -> float:
    """Prevent an unjustified mid-neck phrase from collapsing to open position."""
    cost = v31.previous.held_shape_transition_cost(prior, current, anchor)
    if not prior or not current:
        return cost

    prior_center = fretted_center(prior)
    current_center = fretted_center(current)
    confidence = float(HARMONIC_EVIDENCE.get("confidence") or 0.0)
    open_approved = bool(HARMONIC_EVIDENCE.get("openVoicingApproved"))

    prior_open = sum(1 for _, _, fret in prior if int(fret) == 0)
    current_open = sum(1 for _, _, fret in current if int(fret) == 0)

    if prior_center is not None and current_center is not None:
        shift = abs(current_center - prior_center)
        if shift > 4:
            cost += (shift - 4) * 3.5

        # This directly targets the V34/V35 behaviour: a phrase around frets
        # 5-8 should not suddenly fall to open position without strong evidence.
        collapsing_to_open = (
            prior_center >= 4.5
            and current_center <= 2.0
            and current_open > 0
        )
        if collapsing_to_open:
            if open_approved and confidence >= 0.68:
                cost += 1.5
            else:
                cost += 12.0 + max(0.0, prior_center - 4.5) * 1.8

    # Reward preserving the same fretted area and shared string/fret anchors.
    prior_map = {int(string_index): int(fret) for _, string_index, fret in prior}
    current_map = {int(string_index): int(fret) for _, string_index, fret in current}
    shared_exact = sum(
        1
        for string_index in set(prior_map) & set(current_map)
        if prior_map[string_index] == current_map[string_index]
    )
    cost -= shared_exact * 1.6

    if prior_open == 0 and current_open >= 2 and not open_approved:
        cost += current_open * 3.0

    return cost


# Install candidate-level harmony scoring and path-level continuity at the
# actual V25 beam-search callbacks.
v25.guitarist_assignment_cost = candidate_harmony_cost
v25.phrase_movement_cost = phrase_path_transition_cost


def summarize_path_training(result: dict[str, Any]) -> dict[str, Any]:
    windows = (
        result.get("musicalUnderstanding", {})
        .get("harmonicWindows", [])
    )
    anchors = [
        int(window["chosenAnchor"])
        for window in windows
        if window.get("chosenAnchor") is not None
    ]
    large_anchor_changes = sum(
        1 for first, second in zip(anchors, anchors[1:])
        if abs(second - first) >= 5
    )
    return {
        "chosenAnchors": anchors,
        "largeAnchorChanges": large_anchor_changes,
        "policy": (
            "compare-complete-voicing-paths-preserve-mid-neck-continuity-"
            "and-reject-wrong-bass-inversions"
        ),
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["phrasePathTraining"] = summarize_path_training(result)
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "3.6-phase-1-complete-voicing-paths"
    result["guitarBrainLesson"] = (
        "compare-whole-voicing-paths-preserve-position-and-respect-inversions"
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
