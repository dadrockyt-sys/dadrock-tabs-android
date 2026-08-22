from __future__ import annotations

from pathlib import Path
from typing import Any

from v143_modal_rhythm_router import RhythmStemBundle
from v143_vercel_audio_request_adapter import process_vercel_audio_request


def main() -> None:
    calls: list[tuple[str, Any]] = []

    def download_blob(audio_url: str, blob_token: str, destination: Path) -> None:
        calls.append(("download", (audio_url, blob_token, destination.name)))
        destination.write_bytes(b"fake-audio")

    def normalize_audio(source: Path, destination: Path) -> None:
        calls.append(("normalize", (source.name, destination.name)))
        destination.write_bytes(b"fake-normalized-wav")

    def legacy_analyzer(audio_path: str, transcription_type: str) -> dict[str, Any]:
        calls.append(("legacy", (Path(audio_path).name, transcription_type)))
        return {
            "generatedTab": f"legacy-{transcription_type}",
            "events": [{"source": "legacy"}],
        }

    def rhythm_stem_provider(normalized_path: str | Path) -> RhythmStemBundle:
        path = Path(normalized_path)
        calls.append(("stem-provider", path.name))
        candidate = path.with_name("candidate.wav")
        carrier_a = path.with_name("carrier-a.wav")
        carrier_b = path.with_name("carrier-b.wav")
        for item in (candidate, carrier_a, carrier_b):
            item.write_bytes(b"stem")
        return RhythmStemBundle(
            candidate_stem_paths=(candidate,),
            carrier_stem_a_path=carrier_a,
            carrier_stem_b_path=carrier_b,
        )

    def rhythm_router(
        normalized_path: str | Path,
        transcription_type: str,
        *,
        legacy_analyzer,
        rhythm_stem_provider,
    ) -> dict[str, Any]:
        calls.append(("router", (Path(normalized_path).name, transcription_type)))
        if transcription_type != "rhythm":
            return legacy_analyzer(str(normalized_path), transcription_type)
        bundle = rhythm_stem_provider(normalized_path)
        return {
            "generatedTab": "v143-rhythm",
            "rhythmRouting": {
                "requestedPart": "rhythm",
                "candidateStemCount": len(bundle.candidate_stem_paths),
                "pairedCarrierStemContractPreserved": True,
            },
        }

    base_payload = {
        "audioUrl": "https://example.com/private-audio.wav",
        "pathname": "audio/private-audio.wav",
        "blobToken": "secret-token",
        "song": "Test Song",
        "artist": "Test Artist",
    }

    lead = process_vercel_audio_request(
        {**base_payload, "transcriptionType": "lead"},
        download_blob=download_blob,
        normalize_audio=normalize_audio,
        legacy_analyzer=legacy_analyzer,
        rhythm_stem_provider=rhythm_stem_provider,
        rhythm_router=rhythm_router,
    )
    bass = process_vercel_audio_request(
        {**base_payload, "transcriptionType": "bass"},
        download_blob=download_blob,
        normalize_audio=normalize_audio,
        legacy_analyzer=legacy_analyzer,
        rhythm_stem_provider=rhythm_stem_provider,
        rhythm_router=rhythm_router,
    )
    rhythm = process_vercel_audio_request(
        {**base_payload, "transcriptionType": "rhythm"},
        download_blob=download_blob,
        normalize_audio=normalize_audio,
        legacy_analyzer=legacy_analyzer,
        rhythm_stem_provider=rhythm_stem_provider,
        rhythm_router=rhythm_router,
    )
    rhythm_repeat = process_vercel_audio_request(
        {**base_payload, "transcriptionType": "rhythm"},
        download_blob=download_blob,
        normalize_audio=normalize_audio,
        legacy_analyzer=legacy_analyzer,
        rhythm_stem_provider=rhythm_stem_provider,
        rhythm_router=rhythm_router,
    )

    invalid_rejected = False
    try:
        process_vercel_audio_request(
            {**base_payload, "transcriptionType": "drums"},
            download_blob=download_blob,
            normalize_audio=normalize_audio,
            legacy_analyzer=legacy_analyzer,
            rhythm_stem_provider=rhythm_stem_provider,
            rhythm_router=rhythm_router,
        )
    except ValueError:
        invalid_rejected = True

    missing_path_rejected = False
    try:
        process_vercel_audio_request(
            {**base_payload, "pathname": "", "transcriptionType": "rhythm"},
            download_blob=download_blob,
            normalize_audio=normalize_audio,
            legacy_analyzer=legacy_analyzer,
            rhythm_stem_provider=rhythm_stem_provider,
            rhythm_router=rhythm_router,
        )
    except ValueError:
        missing_path_rejected = True

    lead_unchanged = lead.get("generatedTab") == "legacy-lead"
    bass_unchanged = bass.get("generatedTab") == "legacy-bass"
    rhythm_routed = rhythm.get("generatedTab") == "v143-rhythm"
    private_blob_preserved = bool(
        rhythm.get("vercelAudioHandoff", {}).get("privateBlobContractPreserved")
    )
    pathname_preserved = bool(
        rhythm.get("vercelAudioHandoff", {}).get("pathnamePreserved")
    )
    normalized_before_routing = bool(
        rhythm.get("vercelAudioHandoff", {}).get("normalizedBeforeRouting")
    )
    paired_carrier_contract = bool(
        rhythm.get("rhythmRouting", {}).get("pairedCarrierStemContractPreserved")
    )
    professional_reference_used = bool(
        rhythm.get("vercelAudioHandoff", {}).get("professionalReferenceUsed")
    )
    runtime_labels_required = bool(
        rhythm.get("vercelAudioHandoff", {}).get("runtimeLabelsRequired")
    )
    deterministic_repeat = rhythm == rhythm_repeat

    checks = {
        "Lead Vercel handoff delegated unchanged": lead_unchanged,
        "Bass Vercel handoff delegated unchanged": bass_unchanged,
        "Rhythm Vercel handoff enters V143 router": rhythm_routed,
        "Private Vercel Blob contract preserved": private_blob_preserved,
        "Vercel Blob pathname preserved": pathname_preserved,
        "Audio normalized before routing": normalized_before_routing,
        "Paired carrier-stem contract preserved": paired_carrier_contract,
        "Invalid transcription type rejected": invalid_rejected,
        "Missing pathname rejected": missing_path_rejected,
        "Professional reference used": professional_reference_used,
        "Runtime labels required": runtime_labels_required,
        "Deterministic repeat exact": deterministic_repeat,
    }

    ready = (
        lead_unchanged
        and bass_unchanged
        and rhythm_routed
        and private_blob_preserved
        and pathname_preserved
        and normalized_before_routing
        and paired_carrier_contract
        and invalid_rejected
        and missing_path_rejected
        and not professional_reference_used
        and not runtime_labels_required
        and deterministic_repeat
    )

    print("=== V143 VERCEL AUDIO REQUEST ADAPTER VERIFIED ===")
    for label, value in checks.items():
        print(f"{label}: {value}")
    print(f"READY FOR LIVE MODAL ENDPOINT WIRING: {ready}")

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
