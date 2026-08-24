from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_ai_tab_gpu_worker import image as separator_gpu_image


ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"
APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"

MODEL_FILES = (
    "intro-correlation-safe-grid-event-selector-model.json",
    "intro-correlation-safe-sequence-event-model.json",
    "fresh-17-96-correlation-safe-sequence-frozen-events.json",
    "contextual-prune-frozen-model.json",
)

CANDIDATE_MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_candidate_timing_adapter",
    "v143_reference_free_timing",
    "v143_reference_free_rhythm_pipeline",
    "v143_contextual_prune_reference_free_carrier",
    "v143_contextual_prune_runtime",
    "v143_contextual_prune_shadow_correction",
    "v143_contextual_prune_precision_shadow",
    "v143_contextual_prune_candidate_events",
    "v143_contextual_prune_precision_candidate_events",
    "v143_correlation_safe_fixed_count_reranker_freeze",
    "v143_intro_sequence_event_model",
    "v143_intro_learned_grid_event_selector",
    "v143_intro_learned_onset_spectral_set_model",
    "v143_intro_raw_attack_temporal_diagnostic",
    "v143_intro_repetition_recovery_event_selector",
    "v143_intro_supervised_temporal_assignment",
    "v143_deterministic_separator",
    "v143_seeded_separator",
    "v143_production_separator",
    "v143_seeded_audio_separator_cli",
    "v143_production_engine",
    "v143_rhythm_runtime",
    "v143_rhythm_event_assembly",
    "v143_rhythm_guitar_note_mapper",
    "v143_rhythm_sustain_technique_enricher",
    "v143_rhythm_bend_consensus",
    "v143_rhythm_bend_evidence",
    "v143_rhythm_legato_evidence",
    "v143_rhythm_semantic_primary_note_guard",
    "v143_rhythm_sustain_consensus_shadow",
    "v143_rhythm_output_adapter",
    "v143_modal_rhythm_router",
    "v143_rhythm_stem_provider",
)

app = modal.App("dadrock-v143-contextual-prune-precision-candidate-product")

candidate_image = (
    separator_gpu_image
    .pip_install("setuptools==81.0.0", "basic-pitch", "librosa", "scipy", "soundfile")
    .add_local_python_source(*CANDIDATE_MODULES)
)
for filename in MODEL_FILES:
    candidate_image = candidate_image.add_local_file(
        CAL / filename,
        f"/public/training/v143-musical-reconstruction-calibration/{filename}",
    )


def _safe_suffix(value: str) -> str:
    suffix = str(value or ".audio").strip().lower()
    return suffix if suffix in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"} else ".audio"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _normalize(source: Path, destination: Path) -> None:
    result = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(source), "-map", "0:a:0", "-vn", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(destination)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not destination.exists() or destination.stat().st_size <= 0:
        raise RuntimeError((result.stderr or result.stdout or "normalization failed")[-4000:])


def _build_stems(normalized: Path, output_dir: Path) -> tuple[Path, Path]:
    from v143_deterministic_separator import build_deterministic_v143_stems
    stems = build_deterministic_v143_stems(normalized, output_dir)
    direct = Path(str(stems.get("directGuitar") or ""))
    cascade = Path(str(stems.get("cascadeGuitar") or ""))
    if not direct.exists() or not cascade.exists():
        raise RuntimeError("precision candidate guitar views missing")
    if stems.get("deterministic") is not True or stems.get("referenceFree") is not True:
        raise RuntimeError("precision candidate separator invariants failed")
    return direct, cascade


def _promote_candidate_sustain(events: list[dict[str, Any]], tempo_bpm: float) -> list[dict[str, Any]]:
    from v143_rhythm_sustain_technique_enricher import step_seconds_from_tempo, sustain_tier
    one_step = step_seconds_from_tempo(float(tempo_bpm))
    output: list[dict[str, Any]] = []
    for index, raw in enumerate(events):
        event = dict(raw)
        shadow = event.get("rhythmSustainShadow") if isinstance(event.get("rhythmSustainShadow"), dict) else {}
        duration_steps = max(1, int(shadow.get("durationSteps") or 1))
        duration_seconds = float(shadow.get("durationSeconds") or one_step)
        event["rhythmSustain"] = {
            "version": 2,
            "durationSeconds": duration_seconds,
            "durationSteps": duration_steps,
            "stepSeconds": float(one_step),
            "tier": sustain_tier(duration_steps),
            "source": "reference-free-two-view-harmonic-persistence-precision-candidate",
            "attackTimingChanged": False,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
        }
        start = float(event["timeSeconds"])
        event["eventIndex"] = int(index)
        event["start"] = start
        event["end"] = start + duration_seconds
        event["duration"] = duration_seconds
        event["onsetTime"] = start
        event["offsetTime"] = start + duration_seconds
        output.append(event)
    return output


@app.function(image=candidate_image, gpu="L4", timeout=1800, memory=12288)
def analyze_precision_candidate(source_audio: bytes, suffix: str = ".audio") -> dict[str, Any]:
    if not source_audio:
        raise ValueError("source audio is empty")
    if len(source_audio) > 50 * 1024 * 1024:
        raise ValueError("precision candidate audio cannot exceed 50 MB")

    from v143_contextual_prune_precision_candidate_events import build_precision_candidate_assembly
    from v143_contextual_prune_precision_shadow import apply_reference_free_precision_shadow
    from v143_contextual_prune_reference_free_carrier import build_contextual_prune_reference_free_carrier
    from v143_contextual_prune_runtime import run_contextual_prune
    from v143_contextual_prune_shadow_correction import apply_reference_free_shadow_correction
    from v143_rhythm_bend_consensus import enrich_rhythm_assembly_with_consensus_bends
    from v143_rhythm_bend_evidence import build_pitch_energy_view
    from v143_rhythm_event_assembly import RhythmEventAssemblyResult
    from v143_rhythm_legato_evidence import enrich_rhythm_assembly_with_legato
    from v143_rhythm_output_adapter import render_rhythm_tab
    from v143_rhythm_semantic_primary_note_guard import guard_semantic_events
    from v143_rhythm_sustain_consensus_shadow import annotate_sustain_shadow

    with tempfile.TemporaryDirectory(prefix="v143-precision-candidate-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        _normalize(source, normalized)
        direct, cascade = _build_stems(normalized, root / "stems")

        carrier = build_contextual_prune_reference_free_carrier(normalized, (direct, cascade), measure_start=1, measure_end=113)
        targets = set(range(1, 114))
        base = run_contextual_prune(carrier.rows_by_measure, carrier.grid, targets, context_measures=targets)
        correction = apply_reference_free_shadow_correction(carrier.rows, carrier.grid, base.candidate_events, targets)
        precision = apply_reference_free_precision_shadow(carrier.rows, carrier.grid, correction, targets)
        candidate = build_precision_candidate_assembly(carrier.rows, carrier.grid, precision, carrier.timing)

        with_bends = enrich_rhythm_assembly_with_consensus_bends(candidate.assembly, carrier_stem_paths=(direct, cascade))
        with_legato = enrich_rhythm_assembly_with_legato(with_bends, carrier_stem_paths=(direct, cascade))
        guarded_events, semantic_diagnostics = guard_semantic_events(with_legato.events)
        guarded = RhythmEventAssemblyResult(source=candidate.source, events=tuple(guarded_events))

        pitch_views = [build_pitch_energy_view(direct), build_pitch_energy_view(cascade)]
        sustained_events, sustain_diagnostics = annotate_sustain_shadow(
            guarded.events,
            pitch_views,
            tempo_bpm=float(carrier.timing.tempo_bpm),
        )
        events = _promote_candidate_sustain([dict(event) for event in sustained_events], float(carrier.timing.tempo_bpm))

        attack_locations = {(int(event["measure"]), int(event["step"])) for event in events}
        if attack_locations != set(precision.retained_events):
            raise RuntimeError("precision semantics/sustain changed attack identity")
        if {measure for measure, _step in attack_locations} != targets:
            raise RuntimeError("precision candidate lost measure coverage")
        for event in events:
            key = (int(event["measure"]), int(event["step"]))
            if int(event["midi"]) not in set(precision.pitch_sets[key]):
                raise RuntimeError(f"precision candidate emitted unsupported pitch at {key}")

        technique_types = sorted({
            str(item.get("type"))
            for event in events
            for item in event.get("rhythmTechniques", []) or []
            if isinstance(item, dict) and str(item.get("type") or "")
        })
        source_sha = _sha256_bytes(source_audio)
        return {
            "schemaVersion": 2,
            "generatedTab": render_rhythm_tab(events),
            "tuning": "E Standard",
            "tempo": float(carrier.timing.tempo_bpm),
            "timeSignature": "4/4",
            "keySignature": None,
            "difficulty": None,
            "techniques": technique_types,
            "confidence": None,
            "events": events,
            "noteCount": len(events),
            "candidateCount": int(len(carrier.rows)),
            "selectedCount": int(len(precision.retained_events)),
            "assembly": {
                "version": 4,
                "mode": "v143-contextual-prune-precision-candidate",
                "polyphonicExpansion": len(events) > len(precision.retained_events),
                "selectedAttackCount": len(precision.retained_events),
                "renderNoteCount": len(events),
                "candidateRelocatesEvents": False,
                "referenceFree": True,
                "professionalReferenceUsed": False,
                "runtimeLabelsRequired": False,
            },
            "candidateDiagnostics": candidate.diagnostics(),
            "correctionDiagnostics": correction.diagnostics(),
            "precisionDiagnostics": precision.diagnostics(),
            "semanticGuard": semantic_diagnostics.to_dict(),
            "sustainDiagnostics": sustain_diagnostics,
            "timing": {
                "tempoBpm": float(carrier.timing.tempo_bpm),
                "firstBeatInMeasure": int(carrier.timing.first_beat_in_measure),
                "downbeatIndexMod4": int(carrier.timing.downbeat_index_mod4),
                "beatConfidence": float(carrier.timing.beat_confidence),
                "barConfidence": float(carrier.timing.bar_confidence),
            },
            "liveV143": {
                "version": 5,
                "rhythmOnly": True,
                "referenceFree": True,
                "professionalReferenceUsed": False,
                "referenceRuntimeInputUsed": False,
                "runtimeLabelsRequired": False,
                "candidateMode": "isolated-contextual-prune-precision",
            },
            "candidate": {
                "schemaVersion": 2,
                "mode": "v143-contextual-prune-precision-approved-audio",
                "approvedFixture": source_sha == APPROVED_AUDIO_SHA256,
                "sourceSha256": source_sha,
                "sourceBytes": len(source_audio),
                "protectedLivePipelineModified": False,
                "liveEndpointDeployedOrModified": False,
                "productionModified": False,
                "professionalReferenceUsed": False,
                "runtimeLabelsRequired": False,
                "addsUnobservedAttack": False,
                "addsUnobservedPitch": False,
                "relocatesAttack": False,
            },
        }


@app.local_entrypoint(name="approved_audio")
def approved_audio(
    audio_path: str = "public/gomywayfullaitest.m4a",
    output_path: str = "debug/v143-contextual-prune/precision-candidate-product.json",
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Approved fixture missing: {source}")
    data = source.read_bytes()
    digest = _sha256_bytes(data)
    if digest != APPROVED_AUDIO_SHA256:
        raise RuntimeError(f"Approved fixture SHA changed: {digest}")
    result = analyze_precision_candidate.remote(data, source.suffix)
    candidate = result.get("candidate") or {}
    if candidate.get("approvedFixture") is not True:
        raise RuntimeError("precision candidate did not receive approved fixture")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result["candidateDiagnostics"], sort_keys=True))
    print(json.dumps(result["precisionDiagnostics"], sort_keys=True))
    print(json.dumps(result["semanticGuard"], sort_keys=True))
    print(json.dumps(result["sustainDiagnostics"], sort_keys=True))
    print(f"WROTE={output}")


if __name__ == "__main__":
    pass
