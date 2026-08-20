from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_ai_tab_gpu_worker import image as separator_gpu_image


ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"

MODEL_FILES = (
    "intro-correlation-safe-grid-event-selector-model.json",
    "intro-correlation-safe-sequence-event-model.json",
    "fresh-17-96-correlation-safe-sequence-frozen-events.json",
    "contextual-prune-frozen-model.json",
)

SHADOW_MODULES = (
    "v143_candidate_timing_adapter",
    "v143_reference_free_timing",
    "v143_contextual_prune_reference_free_carrier",
    "v143_contextual_prune_runtime",
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

app = modal.App("dadrock-v143-contextual-prune-shadow")

shadow_image = (
    separator_gpu_image
    .pip_install(
        # Keep the same compatibility pin as the existing V143 Rhythm image.
        "setuptools==81.0.0",
        "basic-pitch",
        "librosa",
        "scipy",
        "soundfile",
    )
    .add_local_python_source(*SHADOW_MODULES)
)

for filename in MODEL_FILES:
    shadow_image = shadow_image.add_local_file(
        CAL / filename,
        f"/public/training/v143-musical-reconstruction-calibration/{filename}",
    )


def _safe_suffix(value: str) -> str:
    suffix = str(value or ".audio").strip().lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        return ".audio"
    return suffix


def _model_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@app.function(
    image=shadow_image,
    gpu="L4",
    timeout=1800,
    memory=12288,
)
def analyze_contextual_prune_shadow(
    source_audio: bytes,
    suffix: str = ".audio",
    measure_start: int = 1,
    measure_end: int | None = None,
) -> dict[str, Any]:
    """Run the reserve-validated contextual selector without touching live output."""
    if not source_audio:
        raise ValueError("source_audio is empty")
    if len(source_audio) > 50 * 1024 * 1024:
        raise ValueError("Shadow audio cannot be larger than 50 MB")

    from v143_contextual_prune_reference_free_carrier import (
        build_contextual_prune_reference_free_carrier,
    )
    from v143_contextual_prune_runtime import (
        CONTEXTUAL_MODEL_PATH,
        run_contextual_prune,
    )
    from v143_deterministic_separator import build_deterministic_v143_stems
    from v143_production_separator import normalize_input_audio

    with tempfile.TemporaryDirectory(prefix="v143-contextual-shadow-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        source.write_bytes(source_audio)

        # The separator's production-compatible FFmpeg normalization is also used
        # as the reference-free full-mix timing input for the research carrier.
        normalized = normalize_input_audio(source, root / "normalized")
        stems = build_deterministic_v143_stems(normalized, root / "stems")
        direct = Path(str(stems.get("directGuitar") or ""))
        cascade = Path(str(stems.get("cascadeGuitar") or ""))
        for label, path in (("direct", direct), ("cascade", cascade)):
            if not path.exists() or path.stat().st_size <= 0:
                raise RuntimeError(f"Shadow {label} guitar view is missing: {path}")

        carrier = build_contextual_prune_reference_free_carrier(
            normalized,
            (direct, cascade),
            measure_start=int(measure_start),
            measure_end=(None if measure_end is None else int(measure_end)),
        )
        target_measures = set(range(carrier.measure_start, carrier.measure_end + 1))
        result = run_contextual_prune(
            carrier.rows_by_measure,
            carrier.grid,
            target_measures,
            context_measures=target_measures,
        )

        candidate_events = [
            {
                "measure": int(measure),
                "quantizedStep": int(step),
                "contextualKeepProbability": float(
                    result.keep_probabilities.get((measure, step), 0.0)
                ),
                "baseScore": float(result.base_scores.get((measure, step), 0.0)),
                "sequenceScore": float(result.sequence_scores.get((measure, step), 0.0)),
                "sequenceEvidence": bool(
                    result.sequence_evidence.get((measure, step), False)
                ),
            }
            for measure, step in sorted(result.candidate_events)
        ]
        pruned_events = [
            {
                "measure": int(measure),
                "quantizedStep": int(step),
                "contextualKeepProbability": float(
                    result.keep_probabilities.get((measure, step), 0.0)
                ),
            }
            for measure, step in sorted(result.pruned_events)
        ]

        diagnostics = result.diagnostics()
        if diagnostics.get("candidateSubsetOfBase") is not True:
            raise RuntimeError("Shadow contextual output escaped the base event set")
        if diagnostics.get("professionalReferenceRequiredAtRuntime") is not False:
            raise RuntimeError("Shadow contextual runtime unexpectedly requires labels")

        return {
            "schemaVersion": 1,
            "mode": "v143-contextual-prune-isolated-shadow",
            "sourceSha256": hashlib.sha256(source_audio).hexdigest(),
            "contextualModelSha256": _model_sha256(CONTEXTUAL_MODEL_PATH),
            "carrier": carrier.summary(),
            "selector": diagnostics,
            "candidateEvents": candidate_events,
            "prunedEvents": pruned_events,
            "separator": {
                "deterministic": stems.get("deterministic") is True,
                "referenceFree": stems.get("referenceFree") is True,
                "productionCandidate": stems.get("productionCandidate") is True,
                "settings": dict(stems.get("settings") or {}),
                "models": dict(stems.get("models") or {}),
            },
            "invariants": {
                "professionalReferenceUsed": False,
                "runtimeLabelsRequired": False,
                "candidateAddsEvents": False,
                "candidateRelocatesEvents": False,
                "leadChanged": False,
                "bassChanged": False,
                "liveRhythmOutputChanged": False,
                "productionModified": False,
            },
        }


@app.function(
    image=shadow_image,
    gpu="L4",
    timeout=600,
    memory=8192,
)
def shadow_dependency_smoke() -> dict[str, Any]:
    """Import-only smoke: no audio, no reference files, no live route."""
    import torch
    from basic_pitch.inference import predict as _predict
    from v143_contextual_prune_reference_free_carrier import (
        HISTORICAL_WIDE_RECALL_SWEEPS,
        WIDE_GRID_TOLERANCE_SECONDS,
    )
    from v143_contextual_prune_runtime import CONTEXTUAL_MODEL_PATH, FEATURE_NAMES
    from v143_deterministic_separator import PRODUCTION_SEPARATOR_SEED

    return {
        "ok": True,
        "cudaAvailable": bool(torch.cuda.is_available()),
        "deviceName": str(torch.cuda.get_device_name(0)) if torch.cuda.is_available() else None,
        "basicPitchImported": bool(_predict),
        "historicalSweepCount": len(HISTORICAL_WIDE_RECALL_SWEEPS),
        "wideGridToleranceSeconds": WIDE_GRID_TOLERANCE_SECONDS,
        "contextualFeatureCount": len(FEATURE_NAMES),
        "contextualModelSha256": _model_sha256(CONTEXTUAL_MODEL_PATH),
        "deterministicSeparatorSeed": PRODUCTION_SEPARATOR_SEED,
        "professionalReferenceOpened": False,
        "productionModified": False,
    }


@app.local_entrypoint(name="shadow_file")
def shadow_file(
    audio_path: str,
    measure_start: int = 1,
    measure_end: int = 0,
) -> None:
    import json

    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Audio file missing or empty: {source}")
    end = None if int(measure_end) <= 0 else int(measure_end)
    result = analyze_contextual_prune_shadow.remote(
        source.read_bytes(),
        source.suffix,
        int(measure_start),
        end,
    )
    print(json.dumps(result, indent=2))


@app.local_entrypoint(name="smoke")
def smoke() -> None:
    import json

    print(json.dumps(shadow_dependency_smoke.remote(), indent=2))


if __name__ == "__main__":
    # Modal owns execution through the local entrypoints above.
    pass
