from __future__ import annotations

import hashlib
import json
import math
import subprocess
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
CALIBRATION_FILES = MODEL_FILES + (
    # Label-free calibration carrier used only to prove exact audio-carrier replay.
    "fresh-section5-reference-free-cache.json",
)
SECTION5_CACHE_PATH = CAL / "fresh-section5-reference-free-cache.json"

SHADOW_MODULES = (
    "v143_ai_tab_gpu_worker",
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

for filename in CALIBRATION_FILES:
    shadow_image = shadow_image.add_local_file(
        CAL / filename,
        f"/public/training/v143-musical-reconstruction-calibration/{filename}",
    )


def _safe_suffix(value: str) -> str:
    suffix = str(value or ".audio").strip().lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        return ".audio"
    return suffix


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _research_normalize_audio(source: Path, destination: Path) -> Path:
    """Exact FFmpeg normalization used by the historical fresh-section captures."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        str(source),
        "-map",
        "0:a:0",
        "-vn",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-c:a",
        "pcm_s16le",
        str(destination),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Historical V143 research normalization failed:\n"
            + (result.stderr or result.stdout or "unknown ffmpeg error")[-4000:]
        )
    if not destination.exists() or destination.stat().st_size <= 0:
        raise RuntimeError("Historical V143 research normalization produced no audio")
    return destination


def _build_shadow_stems(normalized: Path, output_dir: Path) -> tuple[dict[str, Any], Path, Path]:
    from v143_deterministic_separator import build_deterministic_v143_stems

    stems = build_deterministic_v143_stems(normalized, output_dir)
    direct = Path(str(stems.get("directGuitar") or ""))
    cascade = Path(str(stems.get("cascadeGuitar") or ""))
    for label, path in (("direct", direct), ("cascade", cascade)):
        if not path.exists() or path.stat().st_size <= 0:
            raise RuntimeError(f"Shadow {label} guitar view is missing: {path}")
    if stems.get("deterministic") is not True:
        raise RuntimeError("Shadow separator is not marked deterministic")
    if stems.get("referenceFree") is not True:
        raise RuntimeError("Shadow separator is not marked reference-free")
    return stems, direct, cascade


def _first_mismatch(expected: Any, actual: Any, path: str = "$") -> dict[str, Any] | None:
    """Return one compact mismatch while allowing only sub-nanosecond float noise."""
    if isinstance(expected, bool) or isinstance(actual, bool):
        if expected != actual:
            return {"path": path, "expected": expected, "actual": actual}
        return None

    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        left = float(expected)
        right = float(actual)
        if math.isfinite(left) and math.isfinite(right) and math.isclose(
            left,
            right,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            return None
        if left != right:
            return {"path": path, "expected": expected, "actual": actual}
        return None

    if type(expected) is not type(actual):
        return {
            "path": path,
            "expectedType": type(expected).__name__,
            "actualType": type(actual).__name__,
            "expected": expected,
            "actual": actual,
        }

    if isinstance(expected, dict):
        expected_keys = list(expected.keys())
        actual_keys = list(actual.keys())
        if set(expected_keys) != set(actual_keys):
            return {
                "path": path,
                "missingKeys": sorted(set(expected_keys) - set(actual_keys)),
                "extraKeys": sorted(set(actual_keys) - set(expected_keys)),
            }
        for key in expected_keys:
            mismatch = _first_mismatch(expected[key], actual[key], f"{path}.{key}")
            if mismatch is not None:
                return mismatch
        return None

    if isinstance(expected, list):
        if len(expected) != len(actual):
            return {
                "path": path,
                "expectedLength": len(expected),
                "actualLength": len(actual),
            }
        for index, (left, right) in enumerate(zip(expected, actual)):
            mismatch = _first_mismatch(left, right, f"{path}[{index}]")
            if mismatch is not None:
                return mismatch
        return None

    if expected != actual:
        return {"path": path, "expected": expected, "actual": actual}
    return None


def _carrier_replay_payload(carrier: Any) -> dict[str, Any]:
    return {
        "timing": {
            "tempoBpm": float(carrier.timing.tempo_bpm),
            "firstBeatInMeasure": int(carrier.timing.first_beat_in_measure),
            "downbeatIndexMod4": int(carrier.timing.downbeat_index_mod4),
            "beatConfidence": float(carrier.timing.beat_confidence),
            "barConfidence": float(carrier.timing.bar_confidence),
        },
        "grid": [dict(row) for row in carrier.grid_rows],
        "rawEventCount": int(carrier.raw_event_count),
        "candidateClusterCount": int(carrier.candidate_cluster_count),
        "onsetGroupCount": len(carrier.rows),
        "rows": [dict(row) for row in carrier.rows],
        "sweepEventCounts": dict(carrier.sweep_event_counts),
        "stemEventCounts": dict(carrier.stem_event_counts),
        "candidateStemCount": len(carrier.stem_event_counts),
        "targetSampleRate": 22050,
        "hopLength": 128,
        "binsPerOctave": 36,
        "spectrumMidiMin": 28,
        "spectrumMidiMax": 112,
        "guitarMidiMin": 40,
        "guitarMidiMax": 88,
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
    }


def _expected_section5_replay_payload(cache: dict[str, Any]) -> dict[str, Any]:
    required_true = {
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
    }
    for key, expected in required_true.items():
        if cache.get(key) is not expected:
            raise RuntimeError(f"Section-5 cache lost label-blind invariant: {key}")

    section = dict(cache.get("section") or {})
    if int(section.get("startMeasure", -1)) != 81 or int(section.get("endMeasure", -1)) != 96:
        raise RuntimeError(f"Unexpected Section-5 cache range: {section}")

    keys = (
        "timing",
        "grid",
        "rawEventCount",
        "candidateClusterCount",
        "onsetGroupCount",
        "rows",
        "sweepEventCounts",
        "stemEventCounts",
        "candidateStemCount",
        "targetSampleRate",
        "hopLength",
        "binsPerOctave",
        "spectrumMidiMin",
        "spectrumMidiMax",
        "guitarMidiMin",
        "guitarMidiMax",
        "referenceFree",
        "professionalReferenceUsedByAnalyzer",
    )
    missing = [key for key in keys if key not in cache]
    if missing:
        raise RuntimeError(f"Section-5 cache missing replay fields: {missing}")
    return {key: cache[key] for key in keys}


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

    with tempfile.TemporaryDirectory(prefix="v143-contextual-shadow-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, normalized)

        stems, direct, cascade = _build_shadow_stems(normalized, root / "stems")
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
            "schemaVersion": 2,
            "mode": "v143-contextual-prune-isolated-shadow",
            "sourceSha256": hashlib.sha256(source_audio).hexdigest(),
            "researchNormalizedSha256": _sha256_path(normalized),
            "contextualModelSha256": _sha256_path(CONTEXTUAL_MODEL_PATH),
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
            "normalization": {
                "mode": "historical-fresh-section-ffmpeg-44100-stereo-pcm-s16le",
                "sampleRate": 44100,
                "channels": 2,
                "codec": "pcm_s16le",
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
    timeout=1800,
    memory=12288,
)
def replay_section5_reference_free_carrier(
    source_audio: bytes,
    suffix: str = ".audio",
) -> dict[str, Any]:
    """Regenerate measures 81-96 and compare to the frozen label-free carrier."""
    if not source_audio:
        raise ValueError("source_audio is empty")
    if len(source_audio) > 50 * 1024 * 1024:
        raise ValueError("Section-5 replay audio cannot be larger than 50 MB")

    from v143_contextual_prune_reference_free_carrier import (
        build_contextual_prune_reference_free_carrier,
    )

    cache = json.loads(SECTION5_CACHE_PATH.read_text(encoding="utf-8"))
    if not isinstance(cache, dict):
        raise RuntimeError("Fresh Section-5 reference-free cache is not a JSON object")
    expected = _expected_section5_replay_payload(cache)

    with tempfile.TemporaryDirectory(prefix="v143-section5-shadow-replay-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, normalized)

        stems, direct, cascade = _build_shadow_stems(normalized, root / "stems")
        carrier = build_contextual_prune_reference_free_carrier(
            normalized,
            (direct, cascade),
            measure_start=81,
            measure_end=96,
        )
        generated = _carrier_replay_payload(carrier)
        mismatch = _first_mismatch(expected, generated)

        return {
            "schemaVersion": 1,
            "gate": "v143-contextual-prune-section5-reference-free-audio-carrier-replay",
            "measures": "81-96",
            "sourceSha256": hashlib.sha256(source_audio).hexdigest(),
            "researchNormalizedSha256": _sha256_path(normalized),
            "expectedCarrierSha256": _canonical_sha256(expected),
            "generatedCarrierSha256": _canonical_sha256(generated),
            "exactReplayPassed": mismatch is None and expected == generated,
            "toleranceReplayPassed": mismatch is None,
            "firstMismatch": mismatch,
            "expected": {
                "gridCount": len(expected["grid"]),
                "rawEventCount": int(expected["rawEventCount"]),
                "candidateClusterCount": int(expected["candidateClusterCount"]),
                "onsetGroupCount": int(expected["onsetGroupCount"]),
                "rowCount": len(expected["rows"]),
                "sweepEventCounts": dict(expected["sweepEventCounts"]),
                "stemEventCounts": dict(expected["stemEventCounts"]),
            },
            "generated": {
                "gridCount": len(generated["grid"]),
                "rawEventCount": int(generated["rawEventCount"]),
                "candidateClusterCount": int(generated["candidateClusterCount"]),
                "onsetGroupCount": int(generated["onsetGroupCount"]),
                "rowCount": len(generated["rows"]),
                "sweepEventCounts": dict(generated["sweepEventCounts"]),
                "stemEventCounts": dict(generated["stemEventCounts"]),
            },
            "normalization": {
                "mode": "historical-fresh-section-ffmpeg-44100-stereo-pcm-s16le",
                "sampleRate": 44100,
                "channels": 2,
                "codec": "pcm_s16le",
            },
            "separator": {
                "deterministic": stems.get("deterministic") is True,
                "referenceFree": stems.get("referenceFree") is True,
                "settings": dict(stems.get("settings") or {}),
                "models": dict(stems.get("models") or {}),
            },
            "invariants": {
                "calibrationCacheReferenceFree": cache.get("referenceFree") is True,
                "professionalReferenceUsedByCalibrationCache": cache.get(
                    "professionalReferenceUsedByAnalyzer"
                ) is not False,
                "professionalReferenceOpened": False,
                "runtimeLabelsRequired": False,
                "liveEndpointDeployedOrModified": False,
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

    cache = json.loads(SECTION5_CACHE_PATH.read_text(encoding="utf-8"))
    if cache.get("referenceFree") is not True:
        raise RuntimeError("Section-5 calibration carrier is no longer reference-free")
    if cache.get("professionalReferenceUsedByAnalyzer") is not False:
        raise RuntimeError("Section-5 calibration carrier unexpectedly used reference labels")

    return {
        "ok": True,
        "cudaAvailable": bool(torch.cuda.is_available()),
        "deviceName": str(torch.cuda.get_device_name(0)) if torch.cuda.is_available() else None,
        "basicPitchImported": bool(_predict),
        "historicalSweepCount": len(HISTORICAL_WIDE_RECALL_SWEEPS),
        "wideGridToleranceSeconds": WIDE_GRID_TOLERANCE_SECONDS,
        "contextualFeatureCount": len(FEATURE_NAMES),
        "contextualModelSha256": _sha256_path(CONTEXTUAL_MODEL_PATH),
        "section5CacheSha256": _sha256_path(SECTION5_CACHE_PATH),
        "section5CacheReferenceFree": True,
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


@app.local_entrypoint(name="section5_replay")
def section5_replay(
    audio_path: str = "public/gomywayfullaitest.m4a",
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    result = replay_section5_reference_free_carrier.remote(
        source.read_bytes(),
        source.suffix,
    )
    print(json.dumps(result, indent=2))
    if result.get("toleranceReplayPassed") is not True:
        raise RuntimeError(
            "Section-5 reference-free carrier replay failed: "
            + json.dumps(result.get("firstMismatch"), sort_keys=True)
        )


@app.local_entrypoint(name="smoke")
def smoke() -> None:
    print(json.dumps(shadow_dependency_smoke.remote(), indent=2))


if __name__ == "__main__":
    # Modal owns execution through the local entrypoints above.
    pass
