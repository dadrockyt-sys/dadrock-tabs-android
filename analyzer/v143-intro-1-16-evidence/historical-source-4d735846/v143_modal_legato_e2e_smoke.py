from __future__ import annotations

import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from v143_modal_live_endpoint import app, rhythm_image


legato_smoke_image = rhythm_image.add_local_python_source(
    "v143_modal_live_endpoint",
    "v143_rhythm_bend_consensus",
    "v143_rhythm_legato_evidence",
)


@app.function(
    image=legato_smoke_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def rhythm_legato_file_smoke(
    source_audio: bytes,
    suffix: str = ".m4a",
) -> dict[str, Any]:
    """Run real audio through frozen V143, strict bends, then legato evidence.

    Only the Vercel Blob transport boundary is bypassed. No song fixture,
    professional transcription, expected technique locations, or runtime labels
    are used. Bend consensus remains upstream so bend events cannot be
    reclassified as slides/hammer-ons/pull-offs.
    """
    import modal_analyzer as legacy
    from v143_modal_rhythm_router import route_normalized_audio
    from v143_rhythm_bend_consensus import (
        enrich_router_assembly_with_consensus_bends,
    )
    from v143_rhythm_legato_evidence import enrich_router_assembly_with_legato
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

    with tempfile.TemporaryDirectory(prefix="v143-legato-e2e-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"

        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("Legato smoke source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        def legacy_must_not_run(_audio_path: str, _part: str) -> dict[str, Any]:
            raise RuntimeError("Legacy analyzer was called during V143 Rhythm legato smoke")

        def enrich_all(assembly: Any, bundle: Any) -> Any:
            with_bends = enrich_router_assembly_with_consensus_bends(assembly, bundle)
            return enrich_router_assembly_with_legato(with_bends, bundle)

        result = route_normalized_audio(
            normalized,
            "rhythm",
            legacy_analyzer=legacy_must_not_run,
            rhythm_stem_provider=build_rhythm_stem_bundle,
            assembly_enricher=enrich_all,
        )

        events = [
            event for event in (result.get("events") or [])
            if isinstance(event, dict)
        ]
        legato_events = [
            event for event in events
            if isinstance(event.get("legatoEvidence"), dict)
        ]
        bend_events = [
            event for event in events
            if event.get("bendSemitones") is not None
        ]

        type_counts = Counter(
            str((event.get("legatoEvidence") or {}).get("type") or "")
            for event in legato_events
        )
        view_counts = Counter(
            int((event.get("legatoEvidence") or {}).get("viewAgreement") or 0)
            for event in legato_events
        )

        examples: list[dict[str, Any]] = []
        for index, event in enumerate(events):
            evidence = event.get("legatoEvidence")
            if not isinstance(evidence, dict):
                continue
            target_index = event.get("legatoTargetEventIndex")
            target = (
                events[int(target_index)]
                if isinstance(target_index, int) and 0 <= target_index < len(events)
                else {}
            )
            technique = str(evidence.get("type") or "")
            fret = int(event.get("fret") or 0)
            target_fret = int(event.get("legatoTargetFret") or 0)
            symbol = {
                "hammer-on": "h",
                "pull-off": "p",
                "slide-up": "/",
                "slide-down": "\\\\",
            }.get(technique, "?")
            examples.append(
                {
                    "sourceEventIndex": index,
                    "targetEventIndex": target_index,
                    "measure": event.get("measure"),
                    "step": event.get("step"),
                    "timeSeconds": event.get("timeSeconds"),
                    "stringIndex": event.get("stringIndex"),
                    "fret": fret,
                    "midi": event.get("midi", event.get("dominantMidi")),
                    "targetMeasure": target.get("measure"),
                    "targetStep": target.get("step"),
                    "targetTimeSeconds": target.get("timeSeconds"),
                    "targetFret": target_fret,
                    "targetMidi": event.get("legatoTargetMidi"),
                    "technique": technique,
                    "notation": f"{fret}{symbol}{target_fret}",
                    "viewAgreement": evidence.get("viewAgreement"),
                    "requiredViewAgreement": evidence.get("requiredViewAgreement"),
                    "consensusPassed": evidence.get("consensusPassed"),
                    "score": evidence.get("score"),
                }
            )
            if len(examples) >= 30:
                break

        single_view_remaining = sum(
            1
            for event in legato_events
            if int((event.get("legatoEvidence") or {}).get("viewAgreement") or 0) < 2
        )
        strict_consensus = bool(legato_events) and single_view_remaining == 0 and all(
            int((event.get("legatoEvidence") or {}).get("requiredViewAgreement") or 0) == 2
            and (event.get("legatoEvidence") or {}).get("consensusPassed") is True
            for event in legato_events
        )
        reference_free = all(
            (event.get("legatoEvidence") or {}).get("professionalReferenceUsed") is False
            and (event.get("legatoEvidence") or {}).get("runtimeLabelsRequired") is False
            for event in legato_events
        )
        bend_overlap = sum(
            1
            for event in legato_events
            if event.get("bendSemitones") is not None
        )

        routing = dict(result.get("rhythmRouting") or {})
        return {
            "success": bool(str(result.get("generatedTab") or "").strip()),
            "noteCount": len(events),
            "frozenBendEventCount": len(bend_events),
            "legatoEventCount": len(legato_events),
            "legatoTypeCounts": dict(sorted(type_counts.items())),
            "legatoViewAgreementCounts": dict(sorted(view_counts.items())),
            "singleViewLegatoRemaining": single_view_remaining,
            "strictDualViewConsensus": strict_consensus,
            "bendLegatoOverlapCount": bend_overlap,
            "legatoExamples": examples,
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
        "Starting reference-free V143 real-audio legato smoke:",
        source,
        f"({payload_mib:.2f} MiB)",
    )
    result = rhythm_legato_file_smoke.remote(payload, source.suffix)

    print()
    print("=== V143 STRICT REAL-AUDIO RHYTHM LEGATO SMOKE COMPLETE ===")
    print(json.dumps(result, indent=2, default=str))

    if result.get("success") is not True:
        raise RuntimeError("V143 legato smoke returned no generated tab")
    if result.get("postSelectionEvidenceEnrichment") is not True:
        raise RuntimeError("V143 legato enrichment did not execute")
    if result.get("referenceFree") is not True:
        raise RuntimeError("V143 legato smoke violated reference-free contract")
    if result.get("singleViewLegatoRemaining") != 0:
        raise RuntimeError("Single-view legato events survived strict production consensus")
    if result.get("strictDualViewConsensus") is not True:
        raise RuntimeError("Strict dual-view legato consensus was not preserved")
    if result.get("bendLegatoOverlapCount") != 0:
        raise RuntimeError("A frozen bend event was reclassified as legato")


if __name__ == "__main__":
    main()
