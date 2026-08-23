from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import modal

from v143_modal_live_endpoint import rhythm_image as live_rhythm_image


app = modal.App("dadrock-v143-ai-tab-product-canary")

APPROVED_FIXTURE = "public/gomywayfullaitest.m4a"
MAX_CANARY_AUDIO_BYTES = 50 * 1024 * 1024

# Reuse the exact live Rhythm image, while explicitly packaging the module from
# which that image is imported. This avoids relying on implicit local-source
# discovery when Modal reloads this canary module inside the worker. It does not
# deploy or modify the live endpoint; it only makes the canary import closure
# explicit and reproducible.
canary_image = live_rhythm_image.add_local_python_source(
    "v143_modal_live_endpoint"
)


@app.function(
    image=canary_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def analyze_approved_audio(source_audio: bytes) -> dict[str, Any]:
    """Run approved audio through the exact V143 Rhythm product chain.

    This is an isolated product canary. It reuses the same Modal image, frozen
    V143 model, deterministic stem provider, request adapter, event assembly,
    bend/legato enrichment, and output builder as the live Rhythm function.
    The only substitution is the download callback: approved fixture bytes are
    written directly into the request adapter's temporary source path, so no
    private Blob URL or Blob token is required or exposed by this canary.
    """
    if not source_audio:
        raise ValueError("Canary source audio is empty")
    if len(source_audio) > MAX_CANARY_AUDIO_BYTES:
        raise ValueError("Canary source audio cannot exceed 50 MB")

    import modal_analyzer as legacy
    from v143_modal_rhythm_router import route_normalized_audio
    from v143_rhythm_bend_consensus import enrich_router_assembly_with_consensus_bends
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )
    from v143_rhythm_legato_evidence import enrich_router_assembly_with_legato
    from v143_vercel_audio_request_adapter import process_vercel_audio_request

    audio_metadata_box: dict[str, Any] = {}
    normalized_metadata_box: dict[str, Any] = {}

    def download_approved_fixture(
        audio_url: str,
        blob_token: str,
        destination: Path,
    ) -> None:
        if audio_url != "https://canary.invalid/approved-fixture.m4a":
            raise RuntimeError("Unexpected canary audio URL")
        if blob_token:
            raise RuntimeError("Product canary must not receive a Blob token")
        destination.write_bytes(source_audio)
        metadata = legacy.inspect_audio_file(str(destination))
        legacy.validate_audio_metadata(metadata)
        audio_metadata_box.update(metadata)

    def normalize_audio(source: Path, destination: Path) -> None:
        legacy.normalize_audio_file(str(source), str(destination))
        normalized_metadata_box.update(
            legacy.inspect_audio_file(str(destination))
        )

    def enrich_rhythm_techniques(assembly: Any, bundle: Any) -> Any:
        # Match v143_modal_live_endpoint.py exactly: strict bend consensus first,
        # then strict two-view legato evidence.
        with_bends = enrich_router_assembly_with_consensus_bends(assembly, bundle)
        return enrich_router_assembly_with_legato(with_bends, bundle)

    def rhythm_router(
        normalized_path: str | Path,
        transcription_type: str,
        *,
        legacy_analyzer: Callable[[str, str], dict[str, Any]],
        rhythm_stem_provider: Callable[..., Any],
    ) -> dict[str, Any]:
        return route_normalized_audio(
            normalized_path,
            transcription_type,
            legacy_analyzer=legacy_analyzer,
            rhythm_stem_provider=rhythm_stem_provider,
            assembly_enricher=enrich_rhythm_techniques,
        )

    payload = {
        "audioUrl": "https://canary.invalid/approved-fixture.m4a",
        "pathname": "canary/approved-fixture.m4a",
        "song": "V143 AI Tab Product Canary",
        "artist": "DadRock Tabs",
        "transcriptionType": "rhythm",
        "blobToken": "",
    }

    result = process_vercel_audio_request(
        payload,
        download_blob=download_approved_fixture,
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
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "bendEvidence": "strict-two-view-cross-separated-harmonic-contour",
        "bendConsensusViews": 2,
        "legatoEvidence": "strict-two-view-pitch-path-and-reattack",
        "legatoConsensusViews": 2,
        "separatorDeterministic": True,
        "separatorSeed": 143,
        "demucsShifts": 1,
        "runtimeLabelsRequired": False,
    }
    result["canary"] = {
        "schemaVersion": 1,
        "mode": "v143-ai-tab-approved-audio-product-canary",
        "approvedFixture": True,
        "approvedFixtureRepositoryPath": APPROVED_FIXTURE,
        "sourceSha256": hashlib.sha256(source_audio).hexdigest(),
        "sourceBytes": len(source_audio),
        "privateBlobNetworkDownloadBypassed": True,
        "privateBlobTokenUsed": False,
        "sameProductRhythmPipeline": True,
        "sameProductRhythmImage": True,
        "liveEndpointDeployedOrModified": False,
        "productionModified": False,
        "productionPromotionAuthorized": False,
    }
    return result


@app.local_entrypoint(name="run")
def run(
    audio_path: str = APPROVED_FIXTURE,
    output_path: str = ".canary/v143-product-output.json",
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Approved canary audio missing or empty: {source}")
    if source.as_posix() != APPROVED_FIXTURE:
        raise RuntimeError(
            "This canary is locked to the approved repository fixture: "
            f"{APPROVED_FIXTURE}"
        )
    if source.stat().st_size > MAX_CANARY_AUDIO_BYTES:
        raise RuntimeError("Approved canary audio exceeds the 50 MB product limit")

    result = analyze_approved_audio.remote(source.read_bytes())

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    canary = dict(result.get("canary") or {})
    live = dict(result.get("liveV143") or {})
    print("=== V143 AI TAB PRODUCT CANARY COMPLETE ===")
    print(f"rawOutput={output}")
    print(f"sourceSha256={canary.get('sourceSha256')}")
    print(f"sourceBytes={canary.get('sourceBytes')}")
    print(f"referenceFree={live.get('referenceFree') is True}")
    print(f"eventCount={len(result.get('events') or [])}")
    print(f"productionModified={canary.get('productionModified') is True}")
