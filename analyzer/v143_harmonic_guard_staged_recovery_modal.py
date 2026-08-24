from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_repaired_timing_precision_candidate_product_modal import candidate_image


APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_NORMALIZED_SHA256 = "ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f"
EXPECTED_DIRECT_SHA256 = "0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c"
EXPECTED_CASCADE_SHA256 = "546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41"
PROTECTED_PIPELINE_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"

app = modal.App("dadrock-v143-harmonic-guard-staged-recovery")
recovery_image = candidate_image.add_local_python_source(
    "v143_repaired_timing_precision_candidate_product_modal",
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_suffix(value: str) -> str:
    suffix = str(value or ".audio").strip().lower()
    return suffix if suffix in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"} else ".audio"


def _normalize_outer(source: Path, destination: Path) -> None:
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", str(source),
            "-map", "0:a:0", "-vn", "-ar", "44100", "-ac", "2",
            "-c:a", "pcm_s16le", str(destination),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not destination.exists() or destination.stat().st_size <= 0:
        raise RuntimeError((result.stderr or result.stdout or "normalization failed")[-4000:])


def _common_separator_env() -> dict[str, str]:
    from v143_seeded_separator import CUBLAS_WORKSPACE_CONFIG, SEPARATOR_SEED

    return {
        "PYTHONHASHSEED": SEPARATOR_SEED,
        "V143_SEPARATOR_SEED": SEPARATOR_SEED,
        "CUBLAS_WORKSPACE_CONFIG": CUBLAS_WORKSPACE_CONFIG,
        "NVIDIA_TF32_OVERRIDE": "0",
    }


@app.function(image=recovery_image, cpu=1.0, memory=8192, timeout=1500)
def direct_demucs_cpu(source_audio: bytes, suffix: str = ".audio") -> dict[str, Any]:
    """Fresh direct Demucs stage with the exact frozen deterministic CPU controls."""
    from v143_production_separator import normalize_input_audio, separate_demucs_guitar
    from v143_seeded_separator import (
        DEMUCS_SINGLE_THREAD_ENV,
        _temporary_environment,
        seeded_audio_separator_cli,
    )

    if _sha256_bytes(source_audio) != APPROVED_AUDIO_SHA256:
        raise RuntimeError("direct stage did not receive approved fixture")

    with tempfile.TemporaryDirectory(prefix="v143-hg-direct-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"source{_safe_suffix(suffix)}"
        outer = root / "normalized.wav"
        source.write_bytes(source_audio)
        _normalize_outer(source, outer)
        if _sha256_file(outer) != EXPECTED_NORMALIZED_SHA256:
            raise RuntimeError("outer normalized WAV drifted from exact two-pass proof")

        inner = normalize_input_audio(outer, root / "inner")
        with _temporary_environment(_common_separator_env()):
            with _temporary_environment(DEMUCS_SINGLE_THREAD_ENV):
                separated = separate_demucs_guitar(
                    seeded_audio_separator_cli(),
                    inner,
                    root / "direct",
                )
        direct = Path(str(separated["path"]))
        direct_bytes = direct.read_bytes()
        direct_sha = _sha256_bytes(direct_bytes)
        if direct_sha != EXPECTED_DIRECT_SHA256:
            raise RuntimeError(f"direct deterministic stem drifted: {direct_sha}")

        return {
            "schemaVersion": 1,
            "outerNormalizedSha256": _sha256_file(outer),
            "innerNormalizedSha256": _sha256_file(inner),
            "innerNormalizedWav": inner.read_bytes(),
            "directGuitarSha256": direct_sha,
            "directGuitarWav": direct_bytes,
            "executionDevice": "cpu",
            "demucsThreads": 1,
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "productionModified": False,
        }


@app.function(image=recovery_image, gpu="L4", memory=8192, timeout=600)
def roformer_gpu(inner_normalized_wav: bytes) -> dict[str, Any]:
    """The only GPU stage: frozen BS-RoFormer Instrumental."""
    from v143_production_separator import separate_roformer_instrumental
    from v143_seeded_separator import _temporary_environment, seeded_audio_separator_cli

    if not inner_normalized_wav:
        raise RuntimeError("roformer stage received empty normalized WAV")

    with tempfile.TemporaryDirectory(prefix="v143-hg-roformer-") as temp_dir:
        root = Path(temp_dir)
        source = root / "input-normalized.wav"
        source.write_bytes(inner_normalized_wav)
        with _temporary_environment(_common_separator_env()):
            with _temporary_environment({"CUDA_VISIBLE_DEVICES": None}):
                separated = separate_roformer_instrumental(
                    seeded_audio_separator_cli(),
                    source,
                    root / "roformer",
                )
        instrumental = Path(str(separated["path"]))
        data = instrumental.read_bytes()
        return {
            "schemaVersion": 1,
            "inputSha256": _sha256_bytes(inner_normalized_wav),
            "instrumentalSha256": _sha256_bytes(data),
            "instrumentalWav": data,
            "executionDevice": "gpu-auto-proven-deterministic",
            "gpuType": "L4",
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "productionModified": False,
        }


@app.function(image=recovery_image, cpu=1.0, memory=8192, timeout=1500)
def cascade_demucs_cpu(roformer_instrumental_wav: bytes) -> dict[str, Any]:
    """Fresh cascade Demucs stage with the same deterministic CPU controls."""
    from v143_production_separator import separate_demucs_guitar
    from v143_seeded_separator import (
        DEMUCS_SINGLE_THREAD_ENV,
        _temporary_environment,
        seeded_audio_separator_cli,
    )

    if not roformer_instrumental_wav:
        raise RuntimeError("cascade stage received empty RoFormer instrumental")

    with tempfile.TemporaryDirectory(prefix="v143-hg-cascade-") as temp_dir:
        root = Path(temp_dir)
        source = root / "bsroformer-instrumental.wav"
        source.write_bytes(roformer_instrumental_wav)
        with _temporary_environment(_common_separator_env()):
            with _temporary_environment(DEMUCS_SINGLE_THREAD_ENV):
                separated = separate_demucs_guitar(
                    seeded_audio_separator_cli(),
                    source,
                    root / "cascade",
                )
        cascade = Path(str(separated["path"]))
        data = cascade.read_bytes()
        digest = _sha256_bytes(data)
        if digest != EXPECTED_CASCADE_SHA256:
            raise RuntimeError(f"cascade deterministic stem drifted: {digest}")
        return {
            "schemaVersion": 1,
            "roformerInstrumentalSha256": _sha256_bytes(roformer_instrumental_wav),
            "cascadeGuitarSha256": digest,
            "cascadeGuitarWav": data,
            "executionDevice": "cpu",
            "demucsThreads": 1,
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "productionModified": False,
        }


@app.function(image=recovery_image, cpu=2.0, memory=12288, timeout=2400)
def assemble_candidate_cpu(
    source_audio: bytes,
    direct_guitar_wav: bytes,
    cascade_guitar_wav: bytes,
    suffix: str = ".audio",
) -> dict[str, Any]:
    """Run the unchanged post-separator candidate graph on CPU from exact-bound stems."""
    if _sha256_bytes(source_audio) != APPROVED_AUDIO_SHA256:
        raise RuntimeError("assembly stage did not receive approved fixture")
    if _sha256_bytes(direct_guitar_wav) != EXPECTED_DIRECT_SHA256:
        raise RuntimeError("assembly direct stem is not the exact proven stem")
    if _sha256_bytes(cascade_guitar_wav) != EXPECTED_CASCADE_SHA256:
        raise RuntimeError("assembly cascade stem is not the exact proven stem")

    import soundfile as sf

    from v143_contextual_prune_precision_candidate_events import build_precision_candidate_assembly
    from v143_contextual_prune_precision_shadow import apply_reference_free_precision_shadow
    from v143_contextual_prune_reference_free_carrier import build_contextual_prune_reference_free_carrier
    from v143_contextual_prune_runtime import run_contextual_prune
    from v143_contextual_prune_shadow_correction import apply_reference_free_shadow_correction
    from v143_precision_promoted_harmonic_guard import apply_reference_free_promoted_harmonic_guard
    from v143_precision_sustain_promotion import promote_candidate_sustain
    from v143_reference_free_beat_grid_repair import repair_reference_free_beat_grid_from_samples
    from v143_reference_free_timing import estimate_reference_free_timing
    from v143_rhythm_bend_consensus import enrich_rhythm_assembly_with_consensus_bends
    from v143_rhythm_bend_evidence import build_pitch_energy_view
    from v143_rhythm_event_assembly import RhythmEventAssemblyResult
    from v143_rhythm_legato_evidence import enrich_rhythm_assembly_with_legato
    from v143_rhythm_output_adapter import render_rhythm_tab
    from v143_rhythm_semantic_primary_note_guard import guard_semantic_events
    from v143_rhythm_sustain_consensus_shadow import annotate_sustain_shadow

    with tempfile.TemporaryDirectory(prefix="v143-hg-assemble-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        _normalize_outer(source, normalized)
        normalized_sha = _sha256_file(normalized)
        if normalized_sha != EXPECTED_NORMALIZED_SHA256:
            raise RuntimeError(f"assembly normalized WAV drifted: {normalized_sha}")

        original_timing = estimate_reference_free_timing(normalized)
        samples, sample_rate = sf.read(str(normalized), always_2d=False)
        repair = repair_reference_free_beat_grid_from_samples(samples, int(sample_rate), original_timing)
        if repair.repaired_interval_outlier_count != 0:
            raise RuntimeError("recovery candidate timing still contains interval outliers")
        if repair.timing.first_beat_in_measure != original_timing.first_beat_in_measure:
            raise RuntimeError("recovery candidate changed first-beat phase")
        if repair.timing.downbeat_index_mod4 != original_timing.downbeat_index_mod4:
            raise RuntimeError("recovery candidate changed downbeat phase")

        stem_dir = root / "stems"
        stem_dir.mkdir(parents=True, exist_ok=True)
        direct = stem_dir / "direct-demucs6s-guitar.wav"
        cascade = stem_dir / "bsroformer-demucs6s-guitar.wav"
        direct.write_bytes(direct_guitar_wav)
        cascade.write_bytes(cascade_guitar_wav)

        def repaired_timing_estimator(_path: Any):
            return repair.timing

        carrier = build_contextual_prune_reference_free_carrier(
            normalized,
            (direct, cascade),
            measure_start=1,
            measure_end=None,
            timing_estimator=repaired_timing_estimator,
        )
        targets = set(range(carrier.measure_start, carrier.measure_end + 1))
        base = run_contextual_prune(carrier.rows_by_measure, carrier.grid, targets, context_measures=targets)
        correction = apply_reference_free_shadow_correction(carrier.rows, carrier.grid, base.candidate_events, targets)
        precision = apply_reference_free_precision_shadow(carrier.rows, carrier.grid, correction, targets)
        precision, guard_diagnostics = apply_reference_free_promoted_harmonic_guard(
            carrier.rows,
            carrier.grid,
            precision,
        )
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
        events = promote_candidate_sustain(
            [dict(event) for event in sustained_events],
            float(carrier.timing.tempo_bpm),
        )

        attack_locations = {(int(event["measure"]), int(event["step"])) for event in events}
        if attack_locations != set(precision.retained_events):
            raise RuntimeError("recovery semantics/sustain changed attack identity")
        if {measure for measure, _step in attack_locations} != targets:
            raise RuntimeError("recovery candidate lost audio-derived measure coverage")
        for event in events:
            key = (int(event["measure"]), int(event["step"]))
            if int(event["midi"]) not in set(precision.pitch_sets[key]):
                raise RuntimeError(f"recovery candidate emitted unsupported pitch at {key}")

        technique_types = sorted({
            str(item.get("type"))
            for event in events
            for item in event.get("rhythmTechniques", []) or []
            if isinstance(item, dict) and str(item.get("type") or "")
        })
        source_sha = _sha256_bytes(source_audio)
        return {
            "schemaVersion": 4,
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
            "audioDerivedMeasureCount": len(targets),
            "assembly": {
                "version": 6,
                "mode": "v143-repaired-timing-contextual-prune-precision-promoted-harmonic-guard-candidate",
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
            "promotedHarmonicGuardDiagnostics": guard_diagnostics.to_dict(),
            "semanticGuard": semantic_diagnostics.to_dict(),
            "sustainDiagnostics": sustain_diagnostics,
            "timing": {
                "tempoBpm": float(carrier.timing.tempo_bpm),
                "firstBeatInMeasure": int(carrier.timing.first_beat_in_measure),
                "downbeatIndexMod4": int(carrier.timing.downbeat_index_mod4),
                "beatConfidence": float(carrier.timing.beat_confidence),
                "barConfidence": float(carrier.timing.bar_confidence),
                "originalBeatCount": len(original_timing.beat_times),
                "repairedBeatCount": len(repair.repaired_beat_times),
                "repairedIntervalOutlierCount": int(repair.repaired_interval_outlier_count),
                "lookaheadBridgeBeatCount": int(repair.lookahead_bridge_beat_count),
                "measureRangeDerivedFromAudio": True,
                "measureStart": int(carrier.measure_start),
                "measureEnd": int(carrier.measure_end),
            },
            "liveV143": {
                "version": 7,
                "rhythmOnly": True,
                "referenceFree": True,
                "professionalReferenceUsed": False,
                "referenceRuntimeInputUsed": False,
                "runtimeLabelsRequired": False,
                "candidateMode": "isolated-repaired-timing-contextual-prune-precision-promoted-harmonic-guard",
            },
            "candidate": {
                "schemaVersion": 4,
                "mode": "v143-repaired-timing-contextual-prune-precision-promoted-harmonic-guard-approved-audio",
                "approvedFixture": source_sha == APPROVED_AUDIO_SHA256,
                "sourceSha256": source_sha,
                "sourceBytes": len(source_audio),
                "measureRangeDerivedFromAudio": True,
                "tempoChangedByRepair": False,
                "barPhaseChangedByRepair": False,
                "repairedIntervalOutliersZero": repair.repaired_interval_outlier_count == 0,
                "protectedLivePipelineModified": False,
                "liveEndpointDeployedOrModified": False,
                "productionModified": False,
                "professionalReferenceUsed": False,
                "runtimeLabelsRequired": False,
                "addsUnobservedAttack": False,
                "addsUnobservedPitch": False,
                "relocatesAttack": False,
            },
            "stagedRecovery": {
                "schemaVersion": 1,
                "outerNormalizedSha256": normalized_sha,
                "directGuitarStemSha256": _sha256_bytes(direct_guitar_wav),
                "cascadeGuitarStemSha256": _sha256_bytes(cascade_guitar_wav),
                "directDemucsResource": "cpu",
                "roformerResource": "L4",
                "cascadeDemucsResource": "cpu",
                "assemblyResource": "cpu",
                "fullPipelineL4ReservationAvoided": True,
                "referenceFree": True,
                "professionalReferenceUsed": False,
                "productionModified": False,
            },
        }


@app.local_entrypoint(name="approved_audio")
def approved_audio(
    audio_path: str = "public/gomywayfullaitest.m4a",
    output_path: str = "debug/v143-contextual-prune/repaired-timing-precision-harmonic-guard-candidate-product.json",
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Approved fixture missing: {source}")
    data = source.read_bytes()
    digest = _sha256_bytes(data)
    if digest != APPROVED_AUDIO_SHA256:
        raise RuntimeError(f"Approved fixture SHA changed: {digest}")

    direct = direct_demucs_cpu.remote(data, source.suffix)
    if direct.get("directGuitarSha256") != EXPECTED_DIRECT_SHA256:
        raise RuntimeError("direct stage hash gate failed")

    roformer = roformer_gpu.remote(direct["innerNormalizedWav"])
    cascade = cascade_demucs_cpu.remote(roformer["instrumentalWav"])
    if cascade.get("cascadeGuitarSha256") != EXPECTED_CASCADE_SHA256:
        raise RuntimeError("cascade stage hash gate failed")

    result = assemble_candidate_cpu.remote(
        data,
        direct["directGuitarWav"],
        cascade["cascadeGuitarWav"],
        source.suffix,
    )
    staged = result.get("stagedRecovery") or {}
    staged["innerNormalizedSha256"] = direct.get("innerNormalizedSha256")
    staged["roformerInstrumentalSha256"] = roformer.get("instrumentalSha256")
    staged["sourceSha256"] = digest
    result["stagedRecovery"] = staged

    candidate = result.get("candidate") or {}
    guard = result.get("promotedHarmonicGuardDiagnostics") or {}
    if candidate.get("approvedFixture") is not True:
        raise RuntimeError("staged recovery did not receive approved fixture")
    if candidate.get("measureRangeDerivedFromAudio") is not True:
        raise RuntimeError("staged recovery used a non-audio measure range")
    if candidate.get("repairedIntervalOutliersZero") is not True:
        raise RuntimeError("staged recovery timing contains outliers")
    if int(guard.get("suppressedStrongestHarmonicCount") or 0) <= 0:
        raise RuntimeError("staged recovery guard suppressed no harmonic duplicates")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result["timing"], sort_keys=True))
    print(json.dumps(result["promotedHarmonicGuardDiagnostics"], sort_keys=True))
    print(json.dumps(result["stagedRecovery"], sort_keys=True))
    print(f"WROTE={output}")


if __name__ == "__main__":
    pass
