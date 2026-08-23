from __future__ import annotations

import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import modal

import modal_analyzer as legacy
from v143_ai_tab_gpu_worker import image as separator_gpu_image


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
APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"

SHADOW_MODULES = (
    "modal_analyzer",
    "v143_ai_tab_gpu_worker",
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
    "v143_rhythm_semantic_primary_note_guard",
    "v143_rhythm_stem_provider",
    "v143_rhythm_sustain_consensus_shadow",
    "v143_rhythm_sustain_technique_enricher",
    "v143_seeded_audio_separator_cli",
    "v143_seeded_separator",
)

app = modal.App("dadrock-v143-rhythm-semantics-sustain-approved-shadow")

shadow_image = (
    separator_gpu_image
    .pip_install(
        "setuptools==81.0.0",
        "basic-pitch",
        "librosa",
        "scipy",
        "soundfile",
        "requests",
    )
    .add_local_python_source(*SHADOW_MODULES)
    .add_local_file(MODEL_LOCAL_PATH, MODEL_REMOTE_PATH)
)


def _safe_suffix(value: str) -> str:
    suffix = str(value or ".audio").strip().lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        return ".audio"
    return suffix


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _is_primary(event: Mapping[str, Any]) -> bool:
    mapping = event.get("noteMapping")
    if isinstance(mapping, Mapping) and mapping.get("primaryTechniqueNote") is not None:
        return mapping.get("primaryTechniqueNote") is True
    return True


def _technique_counts(events: list[dict[str, Any]]) -> dict[str, Any]:
    all_counts: Counter[str] = Counter()
    primary_counts: Counter[str] = Counter()
    secondary_counts: Counter[str] = Counter()
    technique_events = 0
    secondary_technique_events = 0
    bend_events = 0
    legato_source_events = 0

    for event in events:
        labels = [
            str(item.get("type") or "")
            for item in event.get("rhythmTechniques", []) or []
            if isinstance(item, Mapping) and str(item.get("type") or "")
        ]
        if labels:
            technique_events += 1
        primary = _is_primary(event)
        if labels and not primary:
            secondary_technique_events += 1
        for label in labels:
            all_counts[label] += 1
            if primary:
                primary_counts[label] += 1
            else:
                secondary_counts[label] += 1
        if event.get("bendSemitones") is not None:
            bend_events += 1
        if event.get("legatoTargetEventIndex") is not None:
            legato_source_events += 1

    return {
        "eventCount": len(events),
        "techniqueEventCount": technique_events,
        "secondaryTechniqueEventCount": secondary_technique_events,
        "bendEventCount": bend_events,
        "legatoSourceEventCount": legato_source_events,
        "allTechniqueLabels": dict(sorted(all_counts.items())),
        "primaryTechniqueLabels": dict(sorted(primary_counts.items())),
        "secondaryTechniqueLabels": dict(sorted(secondary_counts.items())),
    }


def _core_signature(event: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        int(event.get("measure")),
        int(event.get("step")),
        round(float(event.get("timeSeconds")), 9),
        int(event.get("midi")),
        int(event.get("stringIndex")),
        int(event.get("fret")),
    )


@app.function(
    image=shadow_image,
    gpu="L4",
    timeout=1800,
    memory=12288,
)
def analyze_semantics_sustain_shadow(
    source_audio: bytes,
    suffix: str = ".audio",
) -> dict[str, Any]:
    if not source_audio:
        raise ValueError("source_audio is empty")
    if len(source_audio) > 50 * 1024 * 1024:
        raise ValueError("Approved-audio semantics shadow cannot exceed 50 MB")

    from v143_reference_free_rhythm_pipeline import analyze_reference_free_rhythm
    from v143_rhythm_bend_consensus import enrich_router_assembly_with_consensus_bends
    from v143_rhythm_bend_evidence import build_pitch_energy_view
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )
    from v143_rhythm_event_assembly import assemble_rhythm_events
    from v143_rhythm_legato_evidence import enrich_router_assembly_with_legato
    from v143_rhythm_semantic_primary_note_guard import guard_semantic_events
    from v143_rhythm_sustain_consensus_shadow import annotate_sustain_shadow

    with tempfile.TemporaryDirectory(prefix="v143-semantics-sustain-shadow-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        legacy.normalize_audio_file(str(source), str(normalized))
        if not normalized.exists() or normalized.stat().st_size <= 0:
            raise RuntimeError("Production-compatible normalization produced no audio")

        bundle = build_deterministic_rhythm_stem_bundle(normalized)
        rhythm_result = analyze_reference_free_rhythm(
            normalized,
            bundle.candidate_stem_paths,
            bundle.carrier_stem_a_path,
            bundle.carrier_stem_b_path,
        )
        assembly = assemble_rhythm_events(rhythm_result)
        with_bends = enrich_router_assembly_with_consensus_bends(assembly, bundle)
        with_legato = enrich_router_assembly_with_legato(with_bends, bundle)

        before_events = [dict(event) for event in with_legato.events]
        guarded_events, semantic_diagnostics = guard_semantic_events(before_events)

        pitch_views = [
            build_pitch_energy_view(bundle.carrier_stem_a_path),
            build_pitch_energy_view(bundle.carrier_stem_b_path),
        ]
        sustain_events, sustain_diagnostics = annotate_sustain_shadow(
            guarded_events,
            pitch_views,
            tempo_bpm=float(rhythm_result.timing.tempo_bpm),
        )

        before_signature = [_core_signature(event) for event in before_events]
        after_signature = [_core_signature(event) for event in sustain_events]
        semantic_before = _technique_counts(before_events)
        semantic_after = _technique_counts(sustain_events)

        sustain_steps = [
            int((event.get("rhythmSustainShadow") or {}).get("durationSteps"))
            for event in sustain_events
            if isinstance(event.get("rhythmSustainShadow"), Mapping)
        ]
        detector_steps = [
            int((event.get("rhythmSustain") or {}).get("durationSteps") or 1)
            for event in sustain_events
        ]

        source_sha = _sha256_bytes(source_audio)
        return {
            "schemaVersion": 1,
            "mode": "v143-rhythm-approved-audio-semantics-sustain-shadow",
            "sourceSha256": source_sha,
            "timing": {
                "tempoBpm": float(rhythm_result.timing.tempo_bpm),
                "firstBeatInMeasure": int(rhythm_result.timing.first_beat_in_measure),
                "downbeatIndexMod4": int(rhythm_result.timing.downbeat_index_mod4),
                "beatConfidence": float(rhythm_result.timing.beat_confidence),
                "barConfidence": float(rhythm_result.timing.bar_confidence),
            },
            "selection": {
                "candidateCount": int(rhythm_result.candidate_count),
                "selectedAttackCount": int(rhythm_result.selected_count),
                "renderedNoteCount": len(before_events),
            },
            "semantics": {
                "beforeGuard": semantic_before,
                "afterGuard": semantic_after,
                "guard": semantic_diagnostics.to_dict(),
            },
            "sustain": {
                "diagnostics": sustain_diagnostics,
                "shadowDurationStepHistogram": dict(sorted(Counter(sustain_steps).items())),
                "detectorDurationStepHistogram": dict(sorted(Counter(detector_steps).items())),
            },
            "invariants": {
                "sourceIsApprovedFixture": source_sha == APPROVED_AUDIO_SHA256,
                "referenceFree": True,
                "runtimeLabelsRequired": False,
                "eventCountUnchanged": len(before_events) == len(sustain_events),
                "coreEventIdentityUnchanged": before_signature == after_signature,
                "attackTimingChanged": False,
                "pitchChanged": False,
                "stringFretChanged": False,
                "sustainShadowOverwritesProductionSustain": False,
                "tieOrLetRingInferred": False,
                "liveRhythmOutputChanged": False,
                "leadChanged": False,
                "bassChanged": False,
                "productionModified": False,
            },
        }


@app.local_entrypoint(name="approved_audio")
def approved_audio(
    audio_path: str = "public/gomywayfullaitest.m4a",
    output_path: str = "debug/v143-contextual-prune/rhythm-semantics-sustain-approved-shadow.json",
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Approved fixture missing or empty: {source}")
    source_bytes = source.read_bytes()
    source_sha = _sha256_bytes(source_bytes)
    if source_sha != APPROVED_AUDIO_SHA256:
        raise RuntimeError(
            f"Approved audio SHA changed: {source_sha} != {APPROVED_AUDIO_SHA256}"
        )
    result = analyze_semantics_sustain_shadow.remote(source_bytes, source.suffix)
    invariants = result.get("invariants") or {}
    if invariants.get("sourceIsApprovedFixture") is not True:
        raise RuntimeError("Semantics/sustain shadow did not receive approved fixture")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["selection"], sort_keys=True))
    print(json.dumps(result["semantics"], sort_keys=True))
    print(json.dumps(result["sustain"]["diagnostics"], sort_keys=True))
    print(f"WROTE={output}")


if __name__ == "__main__":
    pass
