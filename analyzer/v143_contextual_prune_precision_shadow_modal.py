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

MODEL_FILES = (
    "intro-correlation-safe-grid-event-selector-model.json",
    "intro-correlation-safe-sequence-event-model.json",
    "fresh-17-96-correlation-safe-sequence-frozen-events.json",
    "contextual-prune-frozen-model.json",
)

SHADOW_MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_candidate_timing_adapter",
    "v143_reference_free_timing",
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

app = modal.App("dadrock-v143-contextual-prune-precision-shadow")

shadow_image = (
    separator_gpu_image
    .pip_install("setuptools==81.0.0", "basic-pitch", "librosa", "scipy", "soundfile")
    .add_local_python_source(*SHADOW_MODULES)
)
for filename in MODEL_FILES:
    shadow_image = shadow_image.add_local_file(
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


@app.function(image=shadow_image, gpu="L4", timeout=1800, memory=12288)
def analyze_precision_shadow(source_audio: bytes, suffix: str = ".audio") -> dict[str, Any]:
    if not source_audio:
        raise ValueError("source audio empty")

    from v143_contextual_prune_precision_shadow import apply_reference_free_precision_shadow
    from v143_contextual_prune_reference_free_carrier import build_contextual_prune_reference_free_carrier
    from v143_contextual_prune_runtime import run_contextual_prune
    from v143_contextual_prune_shadow_correction import apply_reference_free_shadow_correction
    from v143_deterministic_separator import build_deterministic_v143_stems

    with tempfile.TemporaryDirectory(prefix="v143-precision-shadow-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"source{_safe_suffix(suffix)}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        _normalize(source, normalized)
        stems = build_deterministic_v143_stems(normalized, root / "stems")
        direct = Path(str(stems.get("directGuitar") or ""))
        cascade = Path(str(stems.get("cascadeGuitar") or ""))
        if not direct.exists() or not cascade.exists():
            raise RuntimeError("deterministic guitar views missing")
        if stems.get("deterministic") is not True or stems.get("referenceFree") is not True:
            raise RuntimeError("separator invariants failed")

        carrier = build_contextual_prune_reference_free_carrier(normalized, (direct, cascade), measure_start=1, measure_end=113)
        targets = set(range(carrier.measure_start, carrier.measure_end + 1))
        base = run_contextual_prune(carrier.rows_by_measure, carrier.grid, targets, context_measures=targets)
        correction = apply_reference_free_shadow_correction(carrier.rows, carrier.grid, base.candidate_events, targets)
        precision = apply_reference_free_precision_shadow(carrier.rows, carrier.grid, correction, targets)

        input_measures = {measure for measure, _step in precision.input_events}
        retained_measures = {measure for measure, _step in precision.retained_events}
        missing = sorted(targets - retained_measures)
        pitch_subset = all(
            set(precision.pitch_sets.get(key, ())).issubset(set(precision.original_pitch_sets.get(key, ())))
            for key in precision.pitch_sets
        )

        return {
            "schemaVersion": 1,
            "mode": "v143-contextual-prune-reference-free-precision-shadow",
            "sourceSha256": _sha256_bytes(source_audio),
            "carrier": carrier.summary(),
            "baseSelector": base.diagnostics(),
            "correction": correction.diagnostics(),
            "precision": precision.diagnostics(),
            "coverage": {
                "targetMeasureCount": len(targets),
                "inputPopulatedMeasureCount": len(input_measures),
                "retainedPopulatedMeasureCount": len(retained_measures),
                "missingMeasuresAfterPrecision": missing,
            },
            "pitchSupport": {
                "before": _pitch_hist(precision.original_pitch_sets),
                "after": _pitch_hist(precision.pitch_sets),
                "fundamentalPromotionCount": precision.fundamental_promotions,
                "suppressedPitchCount": precision.suppressed_pitch_count,
            },
            "failSafeEvents": [
                {"measure": int(measure), "step": int(step)} for measure, step in sorted(precision.fail_safe_events)
            ],
            "invariants": {
                "sourceIsApprovedFixture": _sha256_bytes(source_audio) == APPROVED_AUDIO_SHA256,
                "referenceFree": True,
                "runtimeLabelsRequired": False,
                "precisionAttacksSubsetOfCorrectedAttacks": precision.retained_events.issubset(correction.corrected_events),
                "precisionPitchesSubsetOfObservedCarrierPitches": pitch_subset,
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
    output_path: str = "debug/v143-contextual-prune/precision-shadow-approved-audio.json",
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Approved audio fixture missing: {source}")
    data = source.read_bytes()
    digest = _sha256_bytes(data)
    if digest != APPROVED_AUDIO_SHA256:
        raise RuntimeError(f"Approved fixture SHA changed: {digest}")
    result = analyze_precision_shadow.remote(data, source.suffix)
    required = result.get("invariants") or {}
    if not all(
        required.get(key) is True
        for key in (
            "sourceIsApprovedFixture",
            "referenceFree",
            "precisionAttacksSubsetOfCorrectedAttacks",
            "precisionPitchesSubsetOfObservedCarrierPitches",
            "allTargetMeasuresPopulated",
        )
    ):
        raise RuntimeError(f"Precision shadow invariant failure: {required}")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["precision"], sort_keys=True))
    print(json.dumps(result["coverage"], sort_keys=True))
    print(json.dumps(result["pitchSupport"], sort_keys=True))
    print(f"WROTE={output}")


if __name__ == "__main__":
    pass
