from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import modal

try:
    from modal_analyzer import (
        MAX_AUDIO_SIZE_BYTES,
        analyze_audio_file as _analyze_audio_file_v6,
        inspect_audio_file,
        normalize_audio_file,
        validate_audio_metadata,
    )
    from production_chord_diagnostics import (
        attach_rhythm_chord_diagnostics,
    )
    from production_lead_technique_diagnostics import (
        attach_lead_technique_diagnostics,
    )
except ImportError:
    from analyzer.modal_analyzer import (
        MAX_AUDIO_SIZE_BYTES,
        analyze_audio_file as _analyze_audio_file_v6,
        inspect_audio_file,
        normalize_audio_file,
        validate_audio_metadata,
    )
    from analyzer.production_chord_diagnostics import (
        attach_rhythm_chord_diagnostics,
    )
    from analyzer.production_lead_technique_diagnostics import (
        attach_lead_technique_diagnostics,
    )


app = modal.App("dadrock-tab-analyzer")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "basic-pitch",
        "fastapi[standard]",
        "requests",
    )
    .add_local_python_source(
        "modal_analyzer",
        "production_chord_diagnostics",
        "chord_sustain",
        "reference_aware_harmony",
        "production_lead_technique_diagnostics",
        "lead_technique_diagnostics_v7",
    )
)


def normalize_verified_context(
    payload: dict[str, Any],
) -> tuple[list[dict[str, Any]] | None, list[str] | None]:
    """Accept optional verified harmony context without trusting malformed data."""

    raw_chords = payload.get("referenceChords")
    raw_progression = payload.get("expectedProgression")

    if not isinstance(raw_chords, list) or not isinstance(raw_progression, list):
        return None, None

    reference_chords: list[dict[str, Any]] = []
    for raw_chord in raw_chords:
        if not isinstance(raw_chord, dict):
            continue

        name = str(raw_chord.get("name") or "").strip()
        raw_pitch_classes = raw_chord.get("pitchClasses")
        if not name or not isinstance(raw_pitch_classes, list):
            continue

        pitch_classes: list[int] = []
        for value in raw_pitch_classes:
            try:
                pitch_class = int(value) % 12
            except (TypeError, ValueError):
                continue
            if pitch_class not in pitch_classes:
                pitch_classes.append(pitch_class)

        if len(pitch_classes) < 2:
            continue

        reference_chords.append(
            {
                "name": name[:64],
                "pitchClasses": pitch_classes,
            }
        )

    expected_progression = [
        str(value).strip()[:64]
        for value in raw_progression
        if str(value).strip()
    ]

    if not reference_chords or not expected_progression:
        return None, None

    allowed_names = {
        str(chord.get("name") or "")
        for chord in reference_chords
    }
    filtered_progression = [
        name
        for name in expected_progression
        if name in allowed_names
    ]

    if not filtered_progression:
        return None, None

    return reference_chords, filtered_progression


def normalize_lead_technique_context(
    payload: dict[str, Any],
) -> tuple[bool, bool]:
    """Accept explicit lead-technique flags only when they are real booleans."""

    enabled = payload.get("enableReferenceGuidedLeadTechniques") is True
    bend_evidence = payload.get("bendEvidencePresent") is True
    return enabled, bend_evidence


def analyze_audio_file(
    audio_path: str,
    transcription_type: str,
    reference_chords: list[dict[str, Any]] | None = None,
    expected_progression: list[str] | None = None,
    *,
    enable_reference_guided_lead_techniques: bool = False,
    bend_evidence_present: bool = False,
) -> dict[str, Any]:
    """Run V6 analysis, then attach opt-in read-only V7 diagnostics."""

    result = _analyze_audio_file_v6(
        audio_path,
        transcription_type,
    )

    result = attach_rhythm_chord_diagnostics(
        result,
        transcription_type,
        reference_chords=reference_chords,
        expected_progression=expected_progression,
    )

    return attach_lead_technique_diagnostics(
        result,
        transcription_type,
        enable_reference_guided_techniques=(
            enable_reference_guided_lead_techniques
        ),
        bend_evidence_present=bend_evidence_present,
    )


@app.function(
    image=image,
    timeout=600,
    memory=4096,
    secrets=[
        modal.Secret.from_name(
            "dadrock-analyzer-secret"
        )
    ],
)
@modal.fastapi_endpoint(method="POST")
def analyze(payload: dict) -> dict:
    import requests
    from fastapi import HTTPException

    expected_token = os.environ.get("ANALYZER_API_TOKEN")
    supplied_token = str(payload.get("token") or "")

    if (
        not expected_token
        or supplied_token != expected_token
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized analyzer request.",
        )

    audio_url = str(
        payload.get("audioUrl") or ""
    ).strip()
    transcription_type = str(
        payload.get("transcriptionType") or ""
    ).strip().lower()

    if transcription_type not in {
        "lead",
        "rhythm",
        "bass",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "transcriptionType must be "
                "lead, rhythm, or bass."
            ),
        )

    if not audio_url.startswith(("https://", "http://")):
        raise HTTPException(
            status_code=400,
            detail="A valid audioUrl is required.",
        )

    reference_chords, expected_progression = (
        normalize_verified_context(payload)
    )
    (
        enable_reference_guided_lead_techniques,
        bend_evidence_present,
    ) = normalize_lead_technique_context(payload)

    suffix = Path(audio_url).suffix.lower()

    if suffix not in {
        ".mp3",
        ".wav",
        ".m4a",
        ".aac",
        ".flac",
        ".ogg",
    }:
        suffix = ".audio"

    blob_token = str(
        payload.get("blobToken") or ""
    ).strip()
    request_headers: dict[str, str] = {}

    if blob_token:
        request_headers["Authorization"] = (
            f"Bearer {blob_token}"
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / f"uploaded{suffix}"

        try:
            response = requests.get(
                audio_url,
                headers=request_headers,
                timeout=120,
            )
        except requests.RequestException as error:
            raise HTTPException(
                status_code=502,
                detail=(
                    "The analyzer could not "
                    "download the audio file."
                ),
            ) from error

        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail=(
                    "The analyzer could not "
                    "download the audio file."
                ),
            )

        if len(response.content) > MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=(
                    "The uploaded audio cannot "
                    "be larger than 50 MB."
                ),
            )

        audio_path.write_bytes(response.content)

        try:
            audio_metadata = inspect_audio_file(
                str(audio_path)
            )
            validate_audio_metadata(audio_metadata)

            normalized_path = (
                Path(temp_dir) / "normalized.wav"
            )
            normalize_audio_file(
                str(audio_path),
                str(normalized_path),
            )
            normalized_metadata = inspect_audio_file(
                str(normalized_path)
            )
            result = analyze_audio_file(
                str(normalized_path),
                transcription_type,
                reference_chords=reference_chords,
                expected_progression=expected_progression,
                enable_reference_guided_lead_techniques=(
                    enable_reference_guided_lead_techniques
                ),
                bend_evidence_present=bend_evidence_present,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

        result["audioMetadata"] = audio_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }

    return result
