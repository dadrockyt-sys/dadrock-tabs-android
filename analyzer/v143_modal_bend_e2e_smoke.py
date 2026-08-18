from __future__ import annotations

import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from v143_modal_live_endpoint import app, rhythm_image


bend_smoke_image = rhythm_image.add_local_python_source("v143_modal_live_endpoint")


@app.function(
    image=bend_smoke_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def rhythm_bend_file_smoke(
    source_audio: bytes,
    suffix: str = ".m4a",
) -> dict[str, Any]:
    """Run real audio through production V143 plus reference-free bend evidence.

    Only the Vercel Blob transport boundary is bypassed. No song fixture,
    professional transcription, expected bend location, or runtime label is used.
    """
    import modal_analyzer as legacy
    from v143_modal_rhythm_router import route_normalized_audio
    from v143_rhythm_bend_evidence import enrich_router_assembly_with_bends
    from v143_rhythm_output_adapter import render_event_token
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

    with tempfile.TemporaryDirectory(prefix="v143-bend-e2e-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"

        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("Bend smoke source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        def legacy_must_not_run(_audio_path: str, _part: str) -> dict[str, Any]:
            raise RuntimeError("Legacy analyzer was called during V143 Rhythm bend smoke")

        result = route_normalized_audio(
            normalized,
            "rhythm",
            legacy_analyzer=legacy_must_not_run,
            rhythm_stem_provider=build_rhythm_stem_bundle,
            assembly_enricher=enrich_router_assembly_with_bends,
        )

        events = [
            event for event in (result.get("events") or [])
            if isinstance(event, dict)
        ]
        bend_events = [
            event for event in events
            if event.get("bendSemitones") is not None
        ]
        release_events = [
            event for event in bend_events
            if event.get("bendRelease") is True
        ]

        amount_counts = Counter(
            int(event.get("bendSemitones") or 0)
            for event in bend_events
        )

        examples: list[dict[str, Any]] = []
        for event in bend_events[:20]:
            evidence = dict(event.get("bendEvidence") or {})
            examples.append(
                {
                    "measure": event.get("measure"),
                    "step": event.get("step"),
                    "timeSeconds": event.get("timeSeconds"),
                    "stringIndex": event.get("stringIndex"),
                    "fret": event.get("fret"),
                    "midi": event.get("midi", event.get("dominantMidi")),
                    "bendSemitones": event.get("bendSemitones"),
                    "bendTargetFret": event.get("bendTargetFret"),
                    "bendRelease": event.get("bendRelease"),
                    "notation": render_event_token(event),
                    "viewAgreement": evidence.get("viewAgreement"),
                    "score": evidence.get("score"),
                }
            )

        routing = dict(result.get("rhythmRouting") or {})
        reference_free = all(
            (event.get("bendEvidence") or {}).get("professionalReferenceUsed") is False
            and (event.get("bendEvidence") or {}).get("runtimeLabelsRequired") is False
            for event in bend_events
        )

        return {
            "success": bool(str(result.get("generatedTab") or "").strip()),
            "noteCount": len(events),
            "bendEventCount": len(bend_events),
            "bendReleaseCount": len(release_events),
            "bendAmountCounts": dict(sorted(amount_counts.items())),
            "bendExamples": examples,
            "techniques": list(result.get("techniques") or []),
            "tempo": result.get("tempo"),
            "timeSignature": result.get("timeSignature"),
            "candidateStemCount": routing.get("candidateStemCount"),
            "pairedCarrierStemContractPreserved": routing.get(
                "pairedCarrierStemContractPreserved"
            ),
            "postSelectionEvidenceEnrichment": routing.get(
                "postSelectionEvidenceEnrichment"
            ),
            "referenceFree": reference_free,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
            "sourceDurationSeconds": source_metadata.get("duration"),
        }


@app.local_entrypoint()
def main(
    audio_path: str = "public/gomywayfullaitest.m4a",
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Audio file missing or empty: {source}")

    payload = source.read_bytes()
    payload_mib = len(payload) / (1024 * 1024)
    if payload_mib >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print(
        "Starting reference-free V143 real-audio bend smoke:",
        source,
        f"({payload_mib:.2f} MiB)",
    )
    result = rhythm_bend_file_smoke.remote(payload, source.suffix)

    print()
    print("=== V143 REAL-AUDIO RHYTHM BEND SMOKE COMPLETE ===")
    print(json.dumps(result, indent=2, default=str))

    if result.get("success") is not True:
        raise RuntimeError("V143 bend smoke returned no generated tab")
    if result.get("postSelectionEvidenceEnrichment") is not True:
        raise RuntimeError("V143 bend enrichment did not execute")
    if result.get("referenceFree") is not True:
        raise RuntimeError("V143 bend smoke violated reference-free contract")


if __name__ == "__main__":
    main()
