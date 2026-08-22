from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from v143_modal_rhythm_router import RhythmStemProvider, route_normalized_audio


DownloadBlob = Callable[[str, str, Path], None]
NormalizeAudio = Callable[[Path, Path], None]
LegacyAnalyzer = Callable[[str, str], dict[str, Any]]
RhythmRouter = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class VercelAudioRequest:
    audio_url: str
    pathname: str
    transcription_type: str
    song: str = ""
    artist: str = ""
    blob_token: str = ""

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "VercelAudioRequest":
        audio_url = str(payload.get("audioUrl") or "").strip()
        pathname = str(payload.get("pathname") or "").strip()
        transcription_type = str(payload.get("transcriptionType") or "").strip().lower()
        song = str(payload.get("song") or "").strip()
        artist = str(payload.get("artist") or "").strip()
        blob_token = str(payload.get("blobToken") or "").strip()

        if not audio_url.startswith(("https://", "http://")):
            raise ValueError("A valid audioUrl is required")
        if not pathname:
            raise ValueError("A Vercel Blob pathname is required")
        if transcription_type not in {"lead", "rhythm", "bass"}:
            raise ValueError("transcriptionType must be lead, rhythm, or bass")

        return cls(
            audio_url=audio_url,
            pathname=pathname,
            transcription_type=transcription_type,
            song=song,
            artist=artist,
            blob_token=blob_token,
        )


def process_vercel_audio_request(
    payload: dict[str, Any],
    *,
    download_blob: DownloadBlob,
    normalize_audio: NormalizeAudio,
    legacy_analyzer: LegacyAnalyzer,
    rhythm_stem_provider: RhythmStemProvider,
    rhythm_router: RhythmRouter = route_normalized_audio,
) -> dict[str, Any]:
    """Bridge the existing Vercel Blob request contract into the V143 router.

    This adapter intentionally owns no separation policy and no musical inference.
    Vercel continues to supply the private Blob URL/pathname. The caller supplies
    the already-authoritative production download, normalization, legacy analyzer,
    and Rhythm stem-provider functions. Only the normalized local audio path is
    handed to the V143 rhythm routing boundary.
    """

    request = VercelAudioRequest.from_payload(payload)

    with tempfile.TemporaryDirectory(prefix="dadrock-v143-") as temp_dir:
        temp_root = Path(temp_dir)
        source_path = temp_root / "uploaded.audio"
        normalized_path = temp_root / "normalized.wav"

        download_blob(request.audio_url, request.blob_token, source_path)
        if not source_path.exists() or source_path.stat().st_size <= 0:
            raise RuntimeError("Vercel Blob download produced no audio file")

        normalize_audio(source_path, normalized_path)
        if not normalized_path.exists() or normalized_path.stat().st_size <= 0:
            raise RuntimeError("Audio normalization produced no WAV file")

        result = rhythm_router(
            normalized_path,
            request.transcription_type,
            legacy_analyzer=legacy_analyzer,
            rhythm_stem_provider=rhythm_stem_provider,
        )

    if not isinstance(result, dict):
        raise TypeError("Analyzer route must return a dict")
    if not str(result.get("generatedTab") or "").strip():
        raise RuntimeError("Analyzer route returned no generatedTab")

    output = dict(result)
    output["vercelAudioHandoff"] = {
        "version": 1,
        "privateBlobContractPreserved": True,
        "pathnamePreserved": bool(request.pathname),
        "requestedPart": request.transcription_type,
        "normalizedBeforeRouting": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
    }
    return output


__all__ = [
    "VercelAudioRequest",
    "process_vercel_audio_request",
]
