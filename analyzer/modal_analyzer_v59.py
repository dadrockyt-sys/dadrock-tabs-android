import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v58 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v58")

v25 = previous.v25
_original_build_phrase_paths = previous._original_build_phrase_paths
_CONTEXT_DECISIONS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def contextual_groups(
    groups: list[list[dict[str, Any]]],
    index: int,
) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for nearby in (index - 1, index, index + 1):
        if 0 <= nearby < len(groups):
            notes.extend(groups[nearby])
    return notes


def context_aware_build_phrase_paths(
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

    group_chords = [
        previous.infer_group_chord(contextual_groups(groups, index))
        for index in range(len(groups))
    ]

    rescored: list[tuple[float, Any, float, list[dict[str, Any]]]] = []
    for raw_score, path in candidates:
        total_adjustment = 0.0
        diagnostics: list[dict[str, Any]] = []

        for group_index, assignment in enumerate(path):
            chord = group_chords[group_index] if group_index < len(group_chords) else None
            adjustment, diagnostic = previous.local_assignment_adjustment(
                assignment,
                chord,
            )

            # Context is only trusted when the surrounding note groups support a
            # reasonably confident chord identity. Sparse one-note groups were
            # causing V58 to mistake Am and C/G fragments for open-position shapes.
            confidence = float((chord or {}).get("confidence") or 0.0)
            if confidence < 0.66:
                adjustment *= 0.25
                diagnostic = {
                    **diagnostic,
                    "contextDamped": True,
                    "originalAdjustment": round(
                        float(diagnostic.get("adjustment") or 0.0),
                        3,
                    ),
                    "adjustment": round(adjustment, 3),
                }
            else:
                diagnostic = {**diagnostic, "contextDamped": False}

            total_adjustment += adjustment
            diagnostics.append({"groupIndex": group_index, **diagnostic})

        rescored.append(
            (
                float(raw_score) + total_adjustment,
                path,
                float(raw_score),
                diagnostics,
            )
        )

    rescored.sort(key=lambda item: item[0])
    phrase_start = (
        round(float(groups[0][0].get("start") or 0.0), 4)
        if groups and groups[0]
        else None
    )
    _CONTEXT_DECISIONS.append(
        {
            "phraseIndex": len(_CONTEXT_DECISIONS),
            "phraseStart": phrase_start,
            "anchor": int(anchor),
            "groupChords": group_chords,
            "candidateCount": len(rescored),
            "winnerRawScore": round(rescored[0][2], 3) if rescored else None,
            "winnerScore": round(rescored[0][0], 3) if rescored else None,
            "winnerGroups": rescored[0][3] if rescored else [],
        }
    )

    return [(score, path) for score, path, _, _ in rescored]


v25.build_phrase_paths = context_aware_build_phrase_paths


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _CONTEXT_DECISIONS.clear()
    result = previous.previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["contextAwareLocalChordZones"] = {
        "honestFixtureBaseline": 19.06,
        "decisionCount": len(_CONTEXT_DECISIONS),
        "decisions": list(_CONTEXT_DECISIONS),
        "policy": (
            "infer-each-local-chord-from-the-current-note-group-plus-its-neighbours-"
            "and-dampen-low-confidence-zones-so-sparse-arpeggio-notes-do-not-force-"
            "the-entire-hand-into-the-wrong-open-or-low-position"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "5.9-phase-1-context-aware-local-chord-zones"
    result["guitarBrainLesson"] = (
        "use-neighbouring-note-context-before-applying-local-chord-voicing-zones"
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
