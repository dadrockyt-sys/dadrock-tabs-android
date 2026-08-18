from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from v143_modal_live_endpoint import app, rhythm_image


seeded_repeatability_image = rhythm_image.add_local_python_source(
    "v143_modal_live_endpoint",
    "v143_rhythm_bend_consensus",
    "v143_rhythm_legato_evidence",
    "v143_seeded_audio_separator_cli",
    "v143_seeded_separator",
)


def _sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _note_fingerprint(events: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    return [
        (
            event.get("measure"),
            event.get("step"),
            event.get("timeSeconds"),
            event.get("stringIndex"),
            event.get("fret"),
            event.get("midi", event.get("dominantMidi")),
        )
        for event in events
    ]


def _structural_note_fingerprint(events: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    return [
        (
            event.get("measure"),
            event.get("step"),
            event.get("stringIndex"),
            event.get("fret"),
            event.get("midi", event.get("dominantMidi")),
        )
        for event in events
    ]


def _bend_fingerprint(events: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    return [
        (
            index,
            event.get("measure"),
            event.get("step"),
            event.get("stringIndex"),
            event.get("fret"),
            event.get("midi", event.get("dominantMidi")),
            event.get("bendSemitones"),
            event.get("bendRelease"),
            (event.get("bendEvidence") or {}).get("viewAgreement"),
        )
        for index, event in enumerate(events)
        if event.get("bendSemitones") is not None
    ]


def _legato_fingerprint(events: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    return [
        (
            index,
            event.get("legatoTargetEventIndex"),
            event.get("measure"),
            event.get("step"),
            event.get("stringIndex"),
            event.get("fret"),
            event.get("legatoTargetFret"),
            (event.get("legatoEvidence") or {}).get("type"),
            (event.get("legatoEvidence") or {}).get("viewAgreement"),
        )
        for index, event in enumerate(events)
        if isinstance(event.get("legatoEvidence"), dict)
    ]


@app.function(
    image=seeded_repeatability_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def rhythm_seeded_repeatability_diagnostic(
    source_audio: bytes,
    suffix: str = ".m4a",
) -> dict[str, Any]:
    """Run two fresh separations with the frozen graph plus deterministic RNG seed.

    No production separator code is modified by this diagnostic. Demucs remains
    shifts=1; only the random generator state is fixed before each audio-separator
    subprocess starts.
    """
    import modal_analyzer as legacy
    from v143_modal_rhythm_router import route_normalized_audio
    from v143_rhythm_bend_consensus import enrich_router_assembly_with_consensus_bends
    from v143_rhythm_legato_evidence import enrich_router_assembly_with_legato
    from v143_rhythm_stem_provider import build_rhythm_stem_bundle
    from v143_seeded_separator import build_seeded_v143_stems

    safe_suffix = str(suffix or ".audio").lower()
    if safe_suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        safe_suffix = ".audio"

    def run_once(pass_number: int) -> dict[str, Any]:
        with tempfile.TemporaryDirectory(prefix=f"v143-seeded-repeat-{pass_number}-") as temp_dir:
            root = Path(temp_dir)
            source = root / f"uploaded{safe_suffix}"
            normalized = root / "normalized.wav"
            source.write_bytes(source_audio)
            legacy.validate_audio_metadata(legacy.inspect_audio_file(str(source)))
            legacy.normalize_audio_file(str(source), str(normalized))

            stem_hashes: dict[str, str] = {}

            def stem_provider(audio_path: str | Path):
                bundle = build_rhythm_stem_bundle(
                    audio_path,
                    separator_builder=build_seeded_v143_stems,
                )
                stem_hashes["carrierA"] = _sha256(bundle.carrier_stem_a_path)
                stem_hashes["carrierB"] = _sha256(bundle.carrier_stem_b_path)
                return bundle

            def legacy_must_not_run(_audio_path: str, _part: str) -> dict[str, Any]:
                raise RuntimeError("Legacy analyzer was called during seeded V143 repeatability diagnostic")

            def enrich_all(assembly: Any, bundle: Any) -> Any:
                with_bends = enrich_router_assembly_with_consensus_bends(assembly, bundle)
                return enrich_router_assembly_with_legato(with_bends, bundle)

            result = route_normalized_audio(
                normalized,
                "rhythm",
                legacy_analyzer=legacy_must_not_run,
                rhythm_stem_provider=stem_provider,
                assembly_enricher=enrich_all,
            )
            events = [event for event in (result.get("events") or []) if isinstance(event, dict)]
            return {
                "noteCount": len(events),
                "bendCount": sum(1 for event in events if event.get("bendSemitones") is not None),
                "legatoCount": sum(1 for event in events if isinstance(event.get("legatoEvidence"), dict)),
                "stemHashes": stem_hashes,
                "noteFingerprint": _note_fingerprint(events),
                "structuralNoteFingerprint": _structural_note_fingerprint(events),
                "bendFingerprint": _bend_fingerprint(events),
                "legatoFingerprint": _legato_fingerprint(events),
            }

    first = run_once(1)
    second = run_once(2)

    carrier_a_exact = first["stemHashes"].get("carrierA") == second["stemHashes"].get("carrierA")
    carrier_b_exact = first["stemHashes"].get("carrierB") == second["stemHashes"].get("carrierB")
    note_exact = first["noteFingerprint"] == second["noteFingerprint"]
    structural_note_exact = first["structuralNoteFingerprint"] == second["structuralNoteFingerprint"]
    bend_exact = first["bendFingerprint"] == second["bendFingerprint"]
    legato_exact = first["legatoFingerprint"] == second["legatoFingerprint"]
    output_exact = note_exact and bend_exact and legato_exact

    return {
        "success": True,
        "seed": 143,
        "demucsShiftsPreserved": 1,
        "pass1": {
            "noteCount": first["noteCount"],
            "bendCount": first["bendCount"],
            "legatoCount": first["legatoCount"],
            "stemHashes": first["stemHashes"],
        },
        "pass2": {
            "noteCount": second["noteCount"],
            "bendCount": second["bendCount"],
            "legatoCount": second["legatoCount"],
            "stemHashes": second["stemHashes"],
        },
        "carrierAExact": carrier_a_exact,
        "carrierBExact": carrier_b_exact,
        "frozenNoteFingerprintExact": note_exact,
        "structuralNoteFingerprintExact": structural_note_exact,
        "bendFingerprintExact": bend_exact,
        "legatoFingerprintExact": legato_exact,
        "customerOutputExact": output_exact,
        "allExact": carrier_a_exact and carrier_b_exact and output_exact,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionSeparatorModified": False,
    }


@app.local_entrypoint()
def main(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Audio file missing or empty: {source}")

    payload = source.read_bytes()
    print("Starting SEEDED two-pass V143 repeatability diagnostic:", source)
    result = rhythm_seeded_repeatability_diagnostic.remote(payload, source.suffix)
    print()
    print("=== V143 SEEDED REAL-AUDIO REPEATABILITY DIAGNOSTIC COMPLETE ===")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
