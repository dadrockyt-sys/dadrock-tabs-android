import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v60 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v60")

v25 = previous.v25
_original_build_phrase_paths = previous._original_build_phrase_paths
_CANDIDATE_INVENTORY: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def assignment_center(assignment: list[tuple[dict[str, Any], int, int]]) -> float | None:
    profile = previous.voicing.assignment_profile(assignment)
    center = profile.get("center")
    return float(center) if center is not None else None


def inventory_build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    candidates = _original_build_phrase_paths(
        groups,
        transcription_type,
        anchor,
        previous_assignment,
    )

    group_inventory: list[dict[str, Any]] = []
    for group_index, group in enumerate(groups):
        start = previous.group_start(group)
        target = previous.oracle_chord_for_start(start)
        lower, upper = [float(value) for value in target["preferredRange"]]

        choices: list[dict[str, Any]] = []
        for candidate_index, (score, path) in enumerate(candidates):
            if group_index >= len(path):
                continue
            center = assignment_center(path[group_index])
            if center is None:
                continue
            choices.append(
                {
                    "candidateIndex": candidate_index,
                    "rawPathScore": round(float(score), 3),
                    "center": round(center, 3),
                    "inTarget": lower <= center <= upper,
                }
            )

        in_target = [choice for choice in choices if choice["inTarget"]]
        closest = min(
            choices,
            key=lambda choice: (
                0.0
                if lower <= choice["center"] <= upper
                else min(abs(choice["center"] - lower), abs(choice["center"] - upper)),
                choice["rawPathScore"],
            ),
            default=None,
        )
        best_in_target = min(in_target, key=lambda choice: choice["rawPathScore"], default=None)
        raw_winner = min(choices, key=lambda choice: choice["rawPathScore"], default=None)

        group_inventory.append(
            {
                "groupIndex": group_index,
                "groupStart": round(start, 4),
                "oracle": target,
                "choiceCount": len(choices),
                "inTargetChoiceCount": len(in_target),
                "availableCenters": sorted({choice["center"] for choice in choices}),
                "rawWinner": raw_winner,
                "bestInTarget": best_in_target,
                "closestChoice": closest,
                "scoreCostToReachTarget": (
                    round(best_in_target["rawPathScore"] - raw_winner["rawPathScore"], 3)
                    if best_in_target is not None and raw_winner is not None
                    else None
                ),
            }
        )

    _CANDIDATE_INVENTORY.append(
        {
            "phraseIndex": len(_CANDIDATE_INVENTORY),
            "phraseStart": round(previous.group_start(groups[0]), 4) if groups else None,
            "anchor": int(anchor),
            "candidateCount": len(candidates),
            "groups": group_inventory,
        }
    )

    # Preserve V60 behaviour while collecting candidate availability evidence.
    rescored: list[tuple[float, Any]] = []
    for raw_score, path in candidates:
        adjustment = 0.0
        for index, assignment in enumerate(path):
            target = previous.oracle_chord_for_start(previous.group_start(groups[index]))
            local_adjustment, _ = previous.voicing.local_assignment_adjustment(assignment, target)
            adjustment += local_adjustment * 1.35
        rescored.append((float(raw_score) + adjustment, path))
    rescored.sort(key=lambda item: item[0])
    return rescored


v25.build_phrase_paths = inventory_build_phrase_paths


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _CANDIDATE_INVENTORY.clear()
    result = previous.previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["oracleCandidateInventory"] = {
        "honestFixtureBaseline": 19.06,
        "phraseCount": len(_CANDIDATE_INVENTORY),
        "phrases": list(_CANDIDATE_INVENTORY),
        "policy": (
            "measure-whether-human-reference-position-candidates-exist-and-how-much-"
            "raw-path-score-they-cost-before-changing-the-candidate-generator"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "6.1-phase-1-oracle-candidate-inventory"
    result["guitarBrainLesson"] = (
        "separate-candidate-availability-from-candidate-selection"
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
        original_metadata = engine.inspect_audio_file(str(audio_path))
        engine.validate_audio_metadata(original_metadata)
        normalized_path = Path(temp_dir) / "normalized.wav"
        engine.normalize_audio_file(str(audio_path), str(normalized_path))
        normalized_metadata = engine.inspect_audio_file(str(normalized_path))
        result = analyze_audio_file(str(normalized_path), transcription_type)
        result["audioMetadata"] = original_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }

    return to_json_safe(result)
