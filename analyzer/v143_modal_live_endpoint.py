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
    "v143_ai_tab_gpu_worker",
    "v143_audio_download_auth",
    "v143_candidate_timing_adapter",
    "v143_deterministic_separator",
    "v143_modal_rhythm_router",
    "v143_production_engine",
    "v143_production_separator",
    "v143_reference_free_rhythm_pipeline",
    "v143_reference_free_timing",
    "v143_rhythm_bend_consensus",
    "v143_rhythm_bend_evidence",
    "v143_rhythm_deterministic_stem_provider",
    "v143_rhythm_event_assembly",
    "v143_rhythm_guitar_note_mapper",
    "v143_rhythm_legato_evidence",
    "v143_rhythm_output_adapter",
    "v143_rhythm_runtime",
    "v143_rhythm_stem_provider",
    "v143_rhythm_sustain_technique_enricher",
    "v143_seeded_audio_separator_cli",
    "v143_seeded_separator",
    "v143_vercel_audio_request_adapter",
)

legacy_image = legacy.image.add_local_python_source("modal_analyzer")

rhythm_image = (
    separator_gpu_image
    .pip_install(
        # Basic Pitch -> resampy still imports pkg_resources. Setuptools 82+
        # removed pkg_resources, so pin the final release line that provides it.
        "setuptools==81.0.0",
        "basic-pitch",
        "librosa",
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
    from v143_audio_download_auth import build_audio_download_headers

    # BLOB_READ_WRITE_TOKEN is a Vercel storage credential. Never forward it to
    # arbitrary/public audio origins (for example raw.githubusercontent.com).
    # The helper preserves authenticated private/public Vercel Blob downloads.
    headers = build_audio_download_headers(audio_url, blob_token)

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
    """Execute one deterministic Rhythm Guitar request inside the Modal L4 worker."""
    import time

    from v143_modal_rhythm_router import route_normalized_audio
    from v143_rhythm_bend_consensus import enrich_router_assembly_with_consensus_bends
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )
    from v143_rhythm_legato_evidence import enrich_router_assembly_with_legato
    from v143_vercel_audio_request_adapter import process_vercel_audio_request

    request_started = time.monotonic()

    def stage(name: str) -> None:
        # Aggregate runtime timing only. Never emit URLs, tokens, audio, events,
        # generated tablature, labels, or reference-facing information.
        print(
            f"V143_STAGE worker.{name} elapsed={time.monotonic() - request_started:.3f}",
            flush=True,
        )

    audio_metadata_box: dict[str, Any] = {}
    normalized_metadata_box: dict[str, Any] = {}

    stage("start")

    def download_blob(
        audio_url: str,
        blob_token: str,
        destination: Path,
    ) -> None:
        stage("download.start")
        _download_blob_to_path(audio_url, blob_token, destination)
        metadata = legacy.inspect_audio_file(str(destination))
        legacy.validate_audio_metadata(metadata)
        audio_metadata_box.update(metadata)
        stage("download.done")

    def normalize_audio(source: Path, destination: Path) -> None:
        stage("normalize.start")
        legacy.normalize_audio_file(str(source), str(destination))
        normalized_metadata_box.update(
            legacy.inspect_audio_file(str(destination))
        )
        stage("normalize.done")

    def enrich_rhythm_techniques(assembly: Any, bundle: Any) -> Any:
        stage("techniques.start")
        # Strict bend consensus runs first so confirmed bends cannot later be
        # reclassified as legato. Legato itself also requires both carrier views.
        with_bends = enrich_router_assembly_with_consensus_bends(assembly, bundle)
        enriched = enrich_router_assembly_with_legato(with_bends, bundle)
        stage("techniques.done")
        return enriched

    def rhythm_router(
        normalized_path: str | Path,
        transcription_type: str,
        *,
        legacy_analyzer: Callable[[str, str], dict[str, Any]],
        rhythm_stem_provider: Callable[..., Any],
    ) -> dict[str, Any]:
        stage("router.start")
        routed = route_normalized_audio(
            normalized_path,
            transcription_type,
            legacy_analyzer=legacy_analyzer,
            rhythm_stem_provider=rhythm_stem_provider,
            assembly_enricher=enrich_rhythm_techniques,
        )
        stage("router.done")
        return routed

    result = process_vercel_audio_request(
        payload,
        download_blob=download_blob,
        normalize_audio=normalize_audio,
        legacy_analyzer=legacy.analyze_audio_file,
        rhythm_stem_provider=build_deterministic_rhythm_stem_bundle,
        rhythm_router=rhythm_router,
    )

    result["audioMetadata"] = dict(audio_metadata_box)
    result["normalizedAudio"] = {
        "sampleRate": normalized_metadata_box.get("sampleRate"),
        "channels": normalized_metadata_box.get("channels"),
        "codec": normalized_metadata_box.get("codec"),
        "formatName": normalized_metadata_box.get("formatName"),
    }
    result["liveV143"] = {
        "version": 4,
        "modalGpu": "L4",
        "rhythmOnly": True,
        "referenceFree": True,
        "bendEvidence": "strict-two-view-cross-separated-harmonic-contour",
        "bendConsensusViews": 2,
        "legatoEvidence": "strict-two-view-pitch-path-and-reattack",
        "legatoConsensusViews": 2,
        "separatorDeterministic": True,
        "separatorSeed": 143,
        "demucsShifts": 1,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
    }
    stage("done")
    return result


@app.function(
    image=rhythm_image,
    gpu="L4",
    timeout=600,
    memory=8192,
)
def rhythm_dependency_smoke() -> dict[str, Any]:
    """Prove the deploy image can import the deterministic separator and V143 stack."""
    import librosa
    import numpy as np
    import pkg_resources
    import scipy
    import setuptools
    import soundfile
    import torch
    from basic_pitch.inference import predict as _predict
    from v143_deterministic_separator import PRODUCTION_SEPARATOR_SEED
    from v143_production_engine import V143ProductionEngine
    from v143_production_separator import describe
    from v143_rhythm_bend_consensus import enrich_router_assembly_with_consensus_bends
    from v143_rhythm_bend_evidence import build_pitch_energy_view
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )
    from v143_rhythm_legato_evidence import enrich_router_assembly_with_legato

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
        "librosaVersion": str(librosa.__version__),
        "setuptoolsVersion": str(setuptools.__version__),
        "pkgResourcesImported": bool(pkg_resources),
        "soundfileImported": bool(soundfile),
        "basicPitchImported": bool(_predict),
        "bendEvidenceImported": bool(build_pitch_energy_view),
        "bendConsensusImported": bool(enrich_router_assembly_with_consensus_bends),
        "legatoEvidenceImported": bool(enrich_router_assembly_with_legato),
        "deterministicProviderImported": bool(build_deterministic_rhythm_stem_bundle),
        "deterministicSeparatorSeed": PRODUCTION_SEPARATOR_SEED,
        "featureCount": len(engine.feature_names),
        "referenceFree": separator.get("referenceFree") is True,
        "demucsModel": separator.get("demucsModel"),
        "bsRoformerModel": separator.get("bsRoformerModel"),
        "demucsShifts": separator.get("demucsShifts"),
    }
