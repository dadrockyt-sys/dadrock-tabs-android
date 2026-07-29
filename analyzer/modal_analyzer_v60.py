import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v55 as previous
import modal_analyzer_v58 as voicing

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = (
    previous.image
    .add_local_python_source("modal_analyzer_v55")
    .add_local_python_source("modal_analyzer_v58")
)

v25 = previous.v25
_original_build_phrase_paths = voicing._original_build_phrase_paths
_ORACLE_DECISIONS: list[dict[str, Any]] = []

# Benchmark-only oracle for the trusted 12-measure Stairway excerpt.
# This is deliberately not a production harmony detector. Its purpose is to
# prove whether the candidate generator already contains the human-reference
# fingering when supplied with the correct harmonic-position sequence.
REFERENCE_DURATION_SECONDS = 10.35

POSITION_SEQUENCE = [
    (0.000000, 0.083333, "Am", [5.0, 7.0], False),
    (0.083333, 0.125000, "C/G", [5.0, 8.0], False),
    (0.125000, 0.166667, "D/F#", [2.0, 4.0], False),
    (0.166667, 0.250000, "Fmaj7", [0.0, 3.0], True),
    (0.250000, 0.333333, "G/B-Am", [0.0, 3.0], True),
    (0.333333, 0.416667, "Am", [5.0, 7.0], False),
    (0.416667, 0.458333, "C/G", [5.0, 8.0], False),
    (0.458333, 0.500000, "D/F#", [2.0, 4.0], False),
    (0.500000, 0.583333, "Am", [5.0, 7.0], False),
    (0.583333, 0.625000, "C/G", [5.0, 8.0], False),
    (0.625000, 0.666667, "D/F#", [2.0, 4.0], False),
    (0.666667, 0.750000, "Fmaj7", [0.0, 3.0], True),
    (0.750000, 0.833333, "G/B-Am", [0.0, 3.0], True),
    (0.833333, 0.916667, "Am", [5.0, 7.0], False),
    (0.916667, 0.958333, "C/G", [5.0, 8.0], False),
    (0.958333, 1.000001, "D/F#", [2.0, 4.0], False),
]


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def group_start(group: list[dict[str, Any]]) -> float:
    starts = [float(note.get("start") or 0.0) for note in group]
    return float(statistics.median(starts)) if starts else 0.0


def oracle_chord_for_start(start: float) -> dict[str, Any]:
    progress = max(0.0, min(1.0, start / REFERENCE_DURATION_SECONDS))
    for lower, upper, name, preferred_range, allow_open in POSITION_SEQUENCE:
        if lower <= progress < upper:
            return {
                "name": name,
                "confidence": 1.0,
                "preferredRange": preferred_range,
                "allowOpen": allow_open,
                "progress": round(progress, 4),
            }
    return {
        "name": "D/F#",
        "confidence": 1.0,
        "preferredRange": [2.0, 4.0],
        "allowOpen": False,
        "progress": round(progress, 4),
    }


def oracle_build_phrase_paths(
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
    targets = [oracle_chord_for_start(group_start(group)) for group in groups]
    rescored: list[tuple[float, Any, float, list[dict[str, Any]]]] = []

    for raw_score, path in candidates:
        adjustment = 0.0
        diagnostics: list[dict[str, Any]] = []
        for index, assignment in enumerate(path):
            target = targets[index]
            local_adjustment, diagnostic = voicing.local_assignment_adjustment(
                assignment,
                target,
            )
            # Strong enough to test candidate availability, but still preserves
            # the original guitarist movement and playability score as a tie-breaker.
            local_adjustment *= 1.35
            adjustment += local_adjustment
            diagnostics.append(
                {
                    "groupIndex": index,
                    "groupStart": round(group_start(groups[index]), 4),
                    "oracle": target,
                    **diagnostic,
                    "weightedAdjustment": round(local_adjustment, 3),
                }
            )
        rescored.append(
            (float(raw_score) + adjustment, path, float(raw_score), diagnostics)
        )

    rescored.sort(key=lambda item: item[0])
    _ORACLE_DECISIONS.append(
        {
            "phraseIndex": len(_ORACLE_DECISIONS),
            "phraseStart": round(group_start(groups[0]), 4) if groups else None,
            "anchor": int(anchor),
            "candidateCount": len(rescored),
            "winnerRawScore": round(rescored[0][2], 3) if rescored else None,
            "winnerScore": round(rescored[0][0], 3) if rescored else None,
            "winnerGroups": rescored[0][3] if rescored else [],
        }
    )
    return [(score, path) for score, path, _, _ in rescored]


v25.build_phrase_paths = oracle_build_phrase_paths


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _ORACLE_DECISIONS.clear()
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["fixtureGuidedHarmonyOracle"] = {
        "honestFixtureBaseline": 19.06,
        "decisionCount": len(_ORACLE_DECISIONS),
        "referenceDurationSeconds": REFERENCE_DURATION_SECONDS,
        "decisions": list(_ORACLE_DECISIONS),
        "policy": (
            "benchmark-only-oracle-to-test-whether-correct-human-reference-"
            "fingering-candidates-exist-before-building-a-general-harmonic-sequence-decoder"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "6.0-phase-1-fixture-guided-harmony-oracle"
    result["guitarBrainLesson"] = (
        "validate-the-candidate-pool-with-a-trusted-harmonic-position-sequence"
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
