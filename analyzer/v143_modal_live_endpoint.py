from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Callable

import modal
import modal_analyzer as legacy

from v143_ai_tab_gpu_worker import image as separator_gpu_image


app = modal.App("dadrock-v143-ai-tab-live")

ROOT = Path(__file__).resolve().parents[1]
MODEL_LOCAL_PATH = (
    ROOT
    / "public"
    / "training"
    / "v143-final-multifamily-development"
    / "v143-production-model-candidate-v1.json"
)
MODEL_REMOTE_PATH = (
    "/public/training/v143-final-multifamily-development/"
    "v143-production-model-candidate-v1.json"
)

V143_MODULES = (
    "modal_analyzer",
    "v143_candidate_timing_adapter",
    "v143_modal_rhythm_router",
    "v143_production_engine",
    "v143_production_separator",
    "v143_reference_free_rhythm_pipeline",
    "v143_reference_free_timing",
    "v143_rhythm_event_assembly",
    "v143_rhythm_guitar_note_mapper",
    "v143_rhythm_output_adapter",
    "v143_rhythm_runtime",
    "v143_rhythm_stem_provider",
    "v143_rhythm_sustain_technique_enricher",
    "v143_vercel_audio_request_adapter",
)

legacy_image = legacy.image.add_local_python_source("modal_analyzer")

rhythm_image = (
    separator_gpu_image
    .pip_install(
        "basic-pitch",
        "scipy",
        "soundfile",
        "requests",
    )
    .add_local_python_source(*V143_MODULES)
    .add_local_file(
        MODEL_LOCAL_PATH,
        MODEL_REMOTE_PATH,
    )
)


LegacyHandler = Callable[[dict[str, Any]], dict[str, Any]]
RhythmHandler = Callable[[dict[str, Any]], dict[str, Any]]


def dispatch_authorized_request(
    payload: dict[str, Any],
    *,
    expected_token: str,
    legacy_handler: LegacyHandler,
    rhythm_handler: RhythmHandler,
) -> dict[str, Any]:
    """Dispatch the Vercel analyzer request without changing Lead/Bass behavior."""
    supplied_token = str(payload.get("token") or "")
    if not expected_token or supplied_token != expected_token:
        raise PermissionError("Unauthorized analyzer request.")

    transcription_type = str(
        payload.get("transcriptionType") or ""
    ).strip().lower()
    if transcription_type not in {"lead", "rhythm", "bass"}:
        raise ValueError("transcriptionType must be lead, rhythm, or bass.")

    audio_url = str(payload.get("audioUrl") or "").strip()
    if not audio_url.startswith(("https://", "http://")):
        raise ValueError("A valid audioUrl is required.")

    if transcription_type == "rhythm":
        return rhythm_handler(dict(payload))

    return legacy_handler(dict(payload))


def _download_blob_to_path(
    audio_url: str,
    blob_token: str,
    destination: Path,
) -> None:
    import requests

    headers: dict[str, str] = {}
    if blob_token:
        headers["Authorization"] = f"Bearer {blob_token}"

    try:
        response = requests.get(
            audio_url,
            headers=headers,
            timeout=120,
        )
    except requests.RequestException as error:
        raise RuntimeError(
            "The analyzer could not download the audio file."
        ) from error

    if not response.ok:
        raise RuntimeError(
            "The analyzer could not download the audio file."
        )

    if len(response.content) > legacy.MAX_AUDIO_SIZE_BYTES:
        raise ValueError(
            "The uploaded audio cannot be larger than 50 MB."
        )

    destination.write_bytes(response.content)


def _legacy_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Run Lead/Bass through the exact existing modal_analyzer functions."""
    audio_url = str(payload.get("audioUrl") or "").strip()
    blob_token = str(payload.get("blobToken") or "").strip()
    transcription_type = str(
        payload.get("transcriptionType") or ""
    ).strip().lower()

    suffix = Path(audio_url).suffix.lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        suffix = ".audio"

    with tempfile.TemporaryDirectory(prefix="dadrock-legacy-") as temp_dir:
        root = Path(temp_dir)
        audio_path = root / f"uploaded{suffix}"
        normalized_path = root / "normalized.wav"

        _download_blob_to_path(audio_url, blob_token, audio_path)
        audio_metadata = legacy.inspect_audio_file(str(audio_path))
        legacy.validate_audio_metadata(audio_metadata)
        legacy.normalize_audio_file(str(audio_path), str(normalized_path))
        normalized_metadata = legacy.inspect_audio_file(str(normalized_path))
        result = legacy.analyze_audio_file(
            str(normalized_path),
            transcription_type,
        )

    result["audioMetadata"] = audio_metadata
    result["normalizedAudio"] = {
        "sampleRate": normalized_metadata["sampleRate"],
        "channels": normalized_metadata["channels"],
        "codec": normalized_metadata["codec"],
        "formatName": normalized_metadata["formatName"],
    }
    return result


@app.function(
    image=rhythm_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def rhythm_v143_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Execute one real Rhythm Guitar request entirely inside the Modal L4 worker."""
    from v143_rhythm_stem_provider import build_rhythm_stem_bundle
    from v143_vercel_audio_request_adapter import process_vercel_audio_request

    audio_metadata_box: dict[str, Any] = {}
    normalized_metadata_box: dict[str, Any] = {}

    def download_blob(
        audio_url: str,
        blob_token: str,
        destination: Path,
    ) -> None:
        _download_blob_to_path(audio_url, blob_token, destination)
        metadata = legacy.inspect_audio_file(str(destination))
        legacy.validate_audio_metadata(metadata)
        audio_metadata_box.update(metadata)

    def normalize_audio(source: Path, destination: Path) -> None:
        legacy.normalize_audio_file(str(source), str(destination))
        normalized_metadata_box.update(
            legacy.inspect_audio_file(str(destination))
        )

    result = process_vercel_audio_request(
        payload,
        download_blob=download_blob,
        normalize_audio=normalize_audio,
        legacy_analyzer=legacy.analyze_audio_file,
        rhythm_stem_provider=build_rhythm_stem_bundle,
    )

    result["audioMetadata"] = dict(audio_metadata_box)
    result["normalizedAudio"] = {
        "sampleRate": normalized_metadata_box.get("sampleRate"),
        "channels": normalized_metadata_box.get("channels"),
        "codec": normalized_metadata_box.get("codec"),
        "formatName": normalized_metadata_box.get("formatName"),
    }
    result["liveV143"] = {
        "version": 1,
        "modalGpu": "L4",
        "rhythmOnly": True,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
    }
    return result


@app.function(
    image=rhythm_image,
    gpu="L4",
    timeout=600,
    memory=8192,
)
def rhythm_dependency_smoke() -> dict[str, Any]:
    """Prove the deploy image can import the separator and frozen V143 stack."""
    import numpy as np
    import scipy
    import soundfile
    import torch
    from basic_pitch.inference import predict as _predict
    from v143_production_engine import V143ProductionEngine
    from v143_production_separator import describe

    engine = V143ProductionEngine()
    separator = describe()

    return {
        "cudaAvailable": bool(torch.cuda.is_available()),
        "deviceName": (
            str(torch.cuda.get_device_name(0))
            if torch.cuda.is_available()
            else None
        ),
        "numpyVersion": str(np.__version__),
        "scipyVersion": str(scipy.__version__),
        "soundfileImported": bool(soundfile),
        "basicPitchImported": bool(_predict),
        "featureCount": len(engine.feature_names),
        "referenceFree": separator.get("referenceFree") is True,
        "demucsModel": separator.get("demucsModel"),
        "bsRoformerModel": separator.get("bsRoformerModel"),
    }


@app.function(
    image=legacy_image,
    timeout=1200,
    memory=4096,
    secrets=[modal.Secret.from_name("dadrock-analyzer-secret")],
)
@modal.fastapi_endpoint(method="POST")
def analyze(payload: dict) -> dict:
    """Vercel-facing endpoint: legacy Lead/Bass, frozen V143 Rhythm Guitar."""
    from fastapi import HTTPException

    expected_token = str(os.environ.get("ANALYZER_API_TOKEN") or "")

    try:
        return dispatch_authorized_request(
            payload,
            expected_token=expected_token,
            legacy_handler=_legacy_request,
            rhythm_handler=lambda body: rhythm_v143_request.remote(body),
        )
    except PermissionError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="The audio could not be analyzed.",
        ) from error


@app.local_entrypoint()
def main(mode: str = "smoke") -> None:
    import json

    if mode != "smoke":
        raise RuntimeError("Only --mode smoke is supported before deployment")

    result = rhythm_dependency_smoke.remote()
    ready = bool(
        result.get("cudaAvailable")
        and result.get("basicPitchImported")
        and result.get("soundfileImported")
        and int(result.get("featureCount") or 0) == 148
        and result.get("referenceFree") is True
    )

    print("=== V143 LIVE MODAL IMAGE SMOKE ===")
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"READY FOR MODAL DEPLOY: {ready}")

    if not ready:
        raise SystemExit(1)
