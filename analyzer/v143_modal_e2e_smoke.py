from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from v143_modal_live_endpoint import app, rhythm_image


# The E2E entrypoint is its own Modal source module. When Modal hydrates the
# remote function it imports this file again, so the sibling live-endpoint
# module must also be explicitly present in the function image. The production
# rhythm image already contains the rest of the frozen V143 source manifest.
e2e_image = rhythm_image.add_local_python_source("v143_modal_live_endpoint")


@app.function(
    image=e2e_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def rhythm_file_smoke(
    source_audio: bytes,
    suffix: str = ".m4a",
) -> dict[str, Any]:
    """Run one real local audio file through the complete frozen V143 Rhythm path.

    This deliberately bypasses only the Vercel Blob download boundary. Everything
    after download is production code: validation, normalization, frozen separator,
    candidate generation, reference-free timing, V143 scoring/selection, note
    mapping, sustain/techniques, event assembly, and production tab output.
    """
    import modal_analyzer as legacy
    from v143_modal_rhythm_router import route_normalized_audio
    from v143_rhythm_stem_provider import build_rhythm_stem_bundle

    safe_suffix = str(suffix or ".audio").lower()
    if safe_suffix not in {
        ".mp3",
        ".wav",
        ".m4a",
        ".aac",
        ".flac",
        ".ogg",
    }:
        safe_suffix = ".audio"

    with tempfile.TemporaryDirectory(prefix="v143-modal-e2e-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"

        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("Smoke-test source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))
        normalized_metadata = legacy.inspect_audio_file(str(normalized))

        def legacy_must_not_run(_audio_path: str, _part: str) -> dict[str, Any]:
            raise RuntimeError("Legacy analyzer was called during Rhythm V143 smoke")

        result = route_normalized_audio(
            normalized,
            "rhythm",
            legacy_analyzer=legacy_must_not_run,
            rhythm_stem_provider=build_rhythm_stem_bundle,
        )

        generated_tab = str(result.get("generatedTab") or "")
        routing = dict(result.get("rhythmRouting") or {})
        events = list(result.get("events") or [])
        techniques = list(result.get("techniques") or [])

        return {
            "success": bool(generated_tab.strip()),
            "generatedTabCharacters": len(generated_tab),
            "generatedTabPreview": generated_tab[:800],
            "noteCount": int(result.get("noteCount") or len(events)),
            "eventCount": len(events),
            "techniques": techniques,
            "tempo": result.get("tempo"),
            "timeSignature": result.get("timeSignature"),
            "tuning": result.get("tuning"),
            "candidateStemCount": routing.get("candidateStemCount"),
            "pairedCarrierStemContractPreserved": routing.get(
                "pairedCarrierStemContractPreserved"
            ),
            "referenceFree": routing.get("professionalReferenceUsed") is False,
            "runtimeLabelsRequired": routing.get("runtimeLabelsRequired"),
            "sourceMetadata": source_metadata,
            "normalizedMetadata": normalized_metadata,
        }


@app.local_entrypoint()
def main(
    mode: str = "deps",
    audio_path: str = "public/gomywayfullaitest.m4a",
) -> None:
    """Print smoke results because direct `modal run ...::function` hides returns."""
    if mode == "deps":
        from v143_modal_live_endpoint import rhythm_dependency_smoke

        result = rhythm_dependency_smoke.remote()
        print()
        print("=== V143 MODAL DEPENDENCY SMOKE ===")
        print(json.dumps(result, indent=2, default=str))
        return

    if mode == "rhythm-file":
        source = Path(audio_path)
        if not source.exists() or source.stat().st_size <= 0:
            raise RuntimeError(f"Audio file missing or empty: {source}")

        payload = source.read_bytes()
        payload_mib = len(payload) / (1024 * 1024)
        if payload_mib >= 95:
            raise RuntimeError(
                "Local smoke audio is too close to Modal's 100 MB payload limit"
            )

        print(
            "Starting complete V143 Rhythm Guitar Modal smoke:",
            source,
            f"({payload_mib:.2f} MiB)",
        )

        result = rhythm_file_smoke.remote(payload, source.suffix)
        print()
        print("=== V143 MODAL RHYTHM E2E SMOKE COMPLETE ===")
        print(json.dumps(result, indent=2, default=str))

        if result.get("success") is not True:
            raise RuntimeError("V143 Rhythm E2E smoke returned no generated tab")
        return

    raise RuntimeError("mode must be deps or rhythm-file")
