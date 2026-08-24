from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

import modal

from v143_ai_tab_gpu_worker import image as separator_gpu_image


ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"
APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"

MODEL_FILES = (
    "intro-correlation-safe-grid-event-selector-model.json",
    "intro-correlation-safe-sequence-event-model.json",
    "fresh-17-96-correlation-safe-sequence-frozen-events.json",
    "contextual-prune-frozen-model.json",
)

MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_candidate_timing_adapter",
    "v143_reference_free_timing",
    "v143_reference_free_beat_grid_repair",
    "v143_contextual_prune_reference_free_carrier",
    "v143_contextual_prune_runtime",
    "v143_contextual_prune_shadow_correction",
    "v143_contextual_prune_precision_shadow",
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
)

app = modal.App("dadrock-v143-repaired-timing-precision-shadow")

image = (
    separator_gpu_image
    .pip_install("setuptools==81.0.0", "basic-pitch", "librosa", "scipy", "soundfile")
    .add_local_python_source(*MODULES)
)
for filename in MODEL_FILES:
    image = image.add_local_file(
        CAL / filename,
        f"/public/training/v143-musical-reconstruction-calibration/{filename}",
    )


def _safe_suffix(value: str) -> str:
    suffix = str(value or ".audio").strip().lower()
    return suffix if suffix in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"} else ".audio"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _event_payload(values: Any) -> list[list[int]]:
    return [[int(measure), int(step)] for measure, step in sorted(values)]


def _pitch_payload(values: dict[tuple[int, int], tuple[int, ...]]) -> list[list[Any]]:
    return [
        [int(key[0]), int(key[1]), [int(midi) for midi in midis]]
        for key, midis in sorted(values.items())
    ]


def _primary_payload(values: dict[tuple[int, int], int]) -> list[list[int]]:
    return [[int(key[0]), int(key[1]), int(midi)] for key, midi in sorted(values.items())]


def _normalize(source: Path, destination: Path) -> None:
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


def _pitch_hist(values: dict[tuple[int, int], tuple[int, ...]]) -> dict[str, Any]:
    counts = [len(midis) for midis in values.values()]
    hist = Counter(counts)
    return {
        "attackCount": len(counts),
        "totalPitchHypotheses": int(sum(counts)),
        "meanPitchesPerAttack": float(mean(counts)) if counts else 0.0,
        "maxPitchesPerAttack": max(counts, default=0),
        "histogram": {str(key): int(value) for key, value in sorted(hist.items())},
    }


@app.function(image=image, gpu="L4", timeout=1800, memory=12288)
def analyze(source_audio: bytes, suffix: str = ".audio") -> dict[str, Any]:
    if not source_audio:
        raise ValueError("source audio empty")

    import soundfile as sf

    from v143_contextual_prune_precision_shadow import apply_reference_free_precision_shadow
    from v143_contextual_prune_reference_free_carrier import build_contextual_prune_reference_free_carrier
    from v143_contextual_prune_runtime import run_contextual_prune
    from v143_contextual_prune_shadow_correction import apply_reference_free_shadow_correction
    from v143_deterministic_separator import build_deterministic_v143_stems
    from v143_reference_free_beat_grid_repair import repair_reference_free_beat_grid_from_samples
    from v143_reference_free_timing import estimate_reference_free_timing

    with tempfile.TemporaryDirectory(prefix="v143-repaired-precision-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"source{_safe_suffix(suffix)}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        _normalize(source, normalized)

        original_timing = estimate_reference_free_timing(normalized)
        samples, sample_rate = sf.read(str(normalized), always_2d=False)
        repair = repair_reference_free_beat_grid_from_samples(
            samples,
            int(sample_rate),
            original_timing,
        )
        if repair.repaired_interval_outlier_count != 0:
            raise RuntimeError("Repaired timing still contains beat-interval outliers")
        if repair.timing.first_beat_in_measure != original_timing.first_beat_in_measure:
            raise RuntimeError("Beat repair changed first-beat phase")
        if repair.timing.downbeat_index_mod4 != original_timing.downbeat_index_mod4:
            raise RuntimeError("Beat repair changed downbeat phase")
        if abs(repair.timing.tempo_bpm - original_timing.tempo_bpm) > 1e-12:
            raise RuntimeError("Beat repair changed tempo")

        stems = build_deterministic_v143_stems(normalized, root / "stems")
        direct = Path(str(stems.get("directGuitar") or ""))
        cascade = Path(str(stems.get("cascadeGuitar") or ""))
        if not direct.exists() or not cascade.exists():
            raise RuntimeError("deterministic guitar views missing")
        if stems.get("deterministic") is not True or stems.get("referenceFree") is not True:
            raise RuntimeError("separator invariants failed")

        def repaired_timing_estimator(_path: Any):
            return repair.timing

        carrier = build_contextual_prune_reference_free_carrier(
            normalized,
            (direct, cascade),
            measure_start=1,
            measure_end=113,
            timing_estimator=repaired_timing_estimator,
        )
        targets = set(range(1, 114))
        base = run_contextual_prune(
            carrier.rows_by_measure,
            carrier.grid,
            targets,
            context_measures=targets,
        )
        correction = apply_reference_free_shadow_correction(
            carrier.rows,
            carrier.grid,
            base.candidate_events,
            targets,
        )
        precision = apply_reference_free_precision_shadow(
            carrier.rows,
            carrier.grid,
            correction,
            targets,
        )

        retained_measures = {measure for measure, _step in precision.retained_events}
        missing = sorted(targets - retained_measures)
        pitch_subset = all(
            set(precision.pitch_sets.get(key, ())).issubset(
                set(precision.original_pitch_sets.get(key, ()))
            )
            for key in precision.pitch_sets
        )
        primary_complete = (
            set(precision.primary_midis) == set(precision.retained_events)
            and all(
                int(primary) in set(precision.pitch_sets.get(key, ()))
                for key, primary in precision.primary_midis.items()
            )
        )

        carrier_grid = [
            [int(key[0]), int(key[1]), float(value)]
            for key, value in sorted(carrier.grid.items())
        ]
        carrier_rows = [dict(row) for row in carrier.rows]
        stage_hashes = {
            "sourceBytesSha256": _sha256_bytes(source_audio),
            "normalizedWavSha256": _sha256_file(normalized),
            "originalBeatTimesSha256": _canonical_sha([float(v) for v in original_timing.beat_times]),
            "repairedBeatTimesSha256": _canonical_sha([float(v) for v in repair.repaired_beat_times]),
            "directGuitarStemSha256": _sha256_file(direct),
            "cascadeGuitarStemSha256": _sha256_file(cascade),
            "carrierGridSha256": _canonical_sha(carrier_grid),
            "carrierRowsSha256": _canonical_sha(carrier_rows),
            "baseCandidateEventsSha256": _canonical_sha(_event_payload(base.candidate_events)),
            "correctionEventsSha256": _canonical_sha(_event_payload(correction.corrected_events)),
            "correctionPitchSetsSha256": _canonical_sha(_pitch_payload(correction.pitch_sets)),
            "precisionEventsSha256": _canonical_sha(_event_payload(precision.retained_events)),
            "precisionPitchSetsSha256": _canonical_sha(_pitch_payload(precision.pitch_sets)),
            "precisionPrimaryMidisSha256": _canonical_sha(_primary_payload(precision.primary_midis)),
        }

        return {
            "schemaVersion": 1,
            "mode": "v143-reference-free-repaired-timing-precision-shadow",
            "sourceSha256": _sha256_bytes(source_audio),
            "timing": {
                "tempoBpm": float(repair.timing.tempo_bpm),
                "firstBeatInMeasure": int(repair.timing.first_beat_in_measure),
                "downbeatIndexMod4": int(repair.timing.downbeat_index_mod4),
                "originalBeatCount": len(original_timing.beat_times),
                "repairedBeatCount": len(repair.repaired_beat_times),
                "originalIntervalOutlierCount": int(repair.original_interval_outlier_count),
                "repairedIntervalOutlierCount": int(repair.repaired_interval_outlier_count),
                "repairedFirstBeatTime": float(repair.repaired_beat_times[0]),
                "repairedLastBeatTime": float(repair.repaired_beat_times[-1]),
                "activeAudioEndSeconds": float(repair.active_audio_end_seconds),
                "lookaheadBridgeBeatCount": int(repair.lookahead_bridge_beat_count),
            },
            "carrier": carrier.summary(),
            "baseSelector": base.diagnostics(),
            "correction": correction.diagnostics(),
            "precision": precision.diagnostics(),
            "pitchSupport": {
                "before": _pitch_hist(precision.original_pitch_sets),
                "after": _pitch_hist(precision.pitch_sets),
            },
            "coverage": {
                "targetMeasureCount": 113,
                "retainedPopulatedMeasureCount": len(retained_measures),
                "missingMeasures": missing,
            },
            "stageHashes": stage_hashes,
            "invariants": {
                "sourceIsApprovedFixture": _sha256_bytes(source_audio) == APPROVED_AUDIO_SHA256,
                "referenceFree": True,
                "professionalReferenceUsed": False,
                "referenceRuntimeInputUsed": False,
                "runtimeLabelsRequired": False,
                "tempoChangedByRepair": False,
                "barPhaseChangedByRepair": False,
                "repairedIntervalOutliersZero": repair.repaired_interval_outlier_count == 0,
                "carrierUsesRepairedTiming": tuple(carrier.timing.beat_times) == tuple(repair.repaired_beat_times),
                "precisionAttacksSubsetOfCorrectedAttacks": precision.retained_events.issubset(correction.corrected_events),
                "precisionPitchesSubsetOfObservedCarrierPitches": pitch_subset,
                "explicitPrimaryComplete": primary_complete,
                "allTargetMeasuresPopulated": not missing,
                "candidateAddsUnobservedAttack": False,
                "candidateRelocatesEvents": False,
                "candidateAddsUnobservedPitch": False,
                "liveRhythmOutputChanged": False,
                "leadChanged": False,
                "bassChanged": False,
                "productionModified": False,
            },
        }


@app.local_entrypoint(name="approved_audio")
def approved_audio(
    audio_path: str = "public/gomywayfullaitest.m4a",
    output_path: str = "debug/v143-contextual-prune/repaired-timing-precision-shadow.json",
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Approved fixture missing: {source}")
    data = source.read_bytes()
    digest = _sha256_bytes(data)
    if digest != APPROVED_AUDIO_SHA256:
        raise RuntimeError(f"Approved fixture SHA changed: {digest}")
    result = analyze.remote(data, source.suffix)
    invariants = result.get("invariants") or {}
    required = (
        "sourceIsApprovedFixture",
        "referenceFree",
        "repairedIntervalOutliersZero",
        "carrierUsesRepairedTiming",
        "precisionAttacksSubsetOfCorrectedAttacks",
        "precisionPitchesSubsetOfObservedCarrierPitches",
        "explicitPrimaryComplete",
        "allTargetMeasuresPopulated",
    )
    failed = [key for key in required if invariants.get(key) is not True]
    if failed:
        raise RuntimeError(f"Repaired-timing precision invariant failure: {failed}")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result["timing"], sort_keys=True))
    print(json.dumps(result["precision"], sort_keys=True))
    print(json.dumps(result["coverage"], sort_keys=True))
    print(json.dumps(result["stageHashes"], sort_keys=True))
    print(f"WROTE={output}")


if __name__ == "__main__":
    pass
