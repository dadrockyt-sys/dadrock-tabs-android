from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import subprocess
import tempfile
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_historical_band_diagnostic_modal import (
    SECTION3_CACHE,
    _band_result,
    _build_shadow_stems,
    _canonical_sha256,
    _freeze_cache_value,
    _generated_semantics,
    _research_normalize_audio,
    _safe_suffix,
    _sha256,
    diagnostic_image,
)
from v143_contextual_prune_section3_repeatability_modal import (
    _decision_payload,
    _grid_from_cache,
    _max_float_delta,
    _pcm_sha256,
    _rows_by_measure,
)

app = modal.App("dadrock-v143-contextual-prune-section3-cross-container-repeatability")
worker_image = diagnostic_image.add_local_python_source(
    "v143_contextual_prune_historical_band_diagnostic_modal",
    "v143_contextual_prune_section3_repeatability_modal",
)

WORKER_COUNT = 3


def _package_version(name: str) -> str | None:
    try:
        return importlib_metadata.version(name)
    except importlib_metadata.PackageNotFoundError:
        return None


def _post_inference_runtime_fingerprint() -> dict[str, Any]:
    """Capture read-only runtime identity after all scoring-relevant work is done.

    This deliberately runs after separator, Basic Pitch, carrier construction, and
    frozen contextual-prune scoring so the fingerprint cannot perturb the path
    being measured.
    """
    import torch

    gpu: dict[str, Any] = {
        "available": bool(torch.cuda.is_available()),
        "deviceCount": int(torch.cuda.device_count()),
    }
    if torch.cuda.is_available():
        index = int(torch.cuda.current_device())
        properties = torch.cuda.get_device_properties(index)
        gpu.update(
            {
                "currentDevice": index,
                "name": str(properties.name),
                "computeCapability": [int(properties.major), int(properties.minor)],
                "totalMemory": int(properties.total_memory),
            }
        )

    nvidia_smi: dict[str, Any] | None = None
    try:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=uuid,name,driver_version,pci.bus_id",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        nvidia_smi = {
            "returnCode": int(completed.returncode),
            "rows": [line.strip() for line in completed.stdout.splitlines() if line.strip()],
            "stderrTail": (completed.stderr or "")[-1000:],
        }
    except Exception as exc:
        nvidia_smi = {"error": f"{type(exc).__name__}: {exc}"}

    return {
        "packages": {
            "torch": str(torch.__version__),
            "audioSeparator": _package_version("audio-separator"),
            "basicPitch": _package_version("basic-pitch"),
        },
        "cuda": {
            "torchCudaVersion": str(torch.version.cuda) if torch.version.cuda is not None else None,
            "cudnnVersion": int(torch.backends.cudnn.version()) if torch.backends.cudnn.version() is not None else None,
            "deterministicAlgorithmsEnabled": bool(torch.are_deterministic_algorithms_enabled()),
            "cudnnDeterministic": bool(torch.backends.cudnn.deterministic),
            "cudnnBenchmark": bool(torch.backends.cudnn.benchmark),
            "cudaMatmulAllowTf32": bool(torch.backends.cuda.matmul.allow_tf32),
            "cudnnAllowTf32": bool(torch.backends.cudnn.allow_tf32),
        },
        "gpu": gpu,
        "nvidiaSmi": nvidia_smi,
    }


@app.function(image=worker_image, gpu="L4", timeout=1800, memory=12288)
def rebuild_worker(source_audio: bytes, suffix: str, worker_index: int) -> dict[str, Any]:
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import Model, predict as basic_pitch_predict
    from v143_contextual_prune_reference_free_carrier import (
        build_contextual_prune_reference_free_carrier,
    )
    from v143_contextual_prune_runtime import run_contextual_prune
    from v143_reference_free_timing import estimate_reference_free_timing

    if not source_audio:
        raise ValueError("Diagnostic audio is empty")

    section3 = json.loads(SECTION3_CACHE.read_text(encoding="utf-8"))
    targets = set(range(49, 65))
    historical_rows = _rows_by_measure([dict(row) for row in section3.get("rows", []) or []])
    historical_grid = _grid_from_cache(section3)
    historical_runtime = run_contextual_prune(
        historical_rows,
        historical_grid,
        targets,
        context_measures=targets,
    )
    historical_decision = _decision_payload(historical_runtime)

    with tempfile.TemporaryDirectory(prefix=f"v143-cross-worker-{worker_index}-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, normalized)

        stems, direct, cascade = _build_shadow_stems(normalized, root / "stems")
        timing = estimate_reference_free_timing(normalized)
        model = Model(ICASSP_2022_MODEL_PATH)
        prediction_cache: dict[Any, tuple[Any, ...]] = {}

        def memoized_predict(audio_path: str, *args: Any, **kwargs: Any) -> Any:
            key = (
                str(Path(audio_path).resolve()),
                _freeze_cache_value(args),
                _freeze_cache_value(kwargs),
            )
            if key in prediction_cache:
                return (None, None, prediction_cache[key])
            result = basic_pitch_predict(audio_path, model, *args, **kwargs)
            if not isinstance(result, tuple) or len(result) < 3:
                raise RuntimeError(f"Unexpected Basic Pitch return shape for {audio_path}")
            note_events = tuple(result[2] or ())
            prediction_cache[key] = note_events
            return (None, None, note_events)

        def fixed_timing(_path: str | Path) -> Any:
            return timing

        carrier = build_contextual_prune_reference_free_carrier(
            normalized,
            (direct, cascade),
            measure_start=49,
            measure_end=64,
            predictor=memoized_predict,
            timing_estimator=fixed_timing,
        )
        band = _band_result(f"cross-worker-{worker_index}", section3, carrier, 49, 64)
        fresh_runtime = run_contextual_prune(
            carrier.rows_by_measure,
            carrier.grid,
            targets,
            context_measures=targets,
        )
        fresh_decision = _decision_payload(fresh_runtime)

        # Read runtime identity only after all scoring-relevant computation has
        # completed. This metadata is diagnostic evidence, never an input.
        runtime_fingerprint = _post_inference_runtime_fingerprint()

        return {
            "worker": int(worker_index),
            "runtimeIdentity": {
                "hostname": os.environ.get("HOSTNAME"),
                "modalTaskId": os.environ.get("MODAL_TASK_ID"),
                "modalContainerId": os.environ.get("MODAL_CONTAINER_ID"),
                "fingerprint": runtime_fingerprint,
            },
            "normalizedSha256": _sha256(normalized),
            "separator": {
                "deterministicFlag": stems.get("deterministic") is True,
                "referenceFree": stems.get("referenceFree") is True,
                "directFileSha256": _sha256(direct),
                "cascadeFileSha256": _sha256(cascade),
                "directPcm": _pcm_sha256(direct),
                "cascadePcm": _pcm_sha256(cascade),
            },
            "carrier": {
                "semanticSha256": _canonical_sha256(_generated_semantics(carrier)),
                "exactHistoricalReplay": band["exactSemanticReplayPassed"],
                "toleranceHistoricalReplay": band["toleranceSemanticReplayPassed"],
                "firstMismatch": band["firstMismatch"],
                "rawEventCount": int(carrier.raw_event_count),
                "candidateClusterCount": int(carrier.candidate_cluster_count),
                "rowCount": len(carrier.rows),
                "stemEventCounts": dict(carrier.stem_event_counts),
                "sweepEventCounts": dict(carrier.sweep_event_counts),
            },
            "downstream": {
                "decisionSha256": _canonical_sha256(fresh_decision),
                "decisionSetExactToHistorical": fresh_decision == historical_decision,
                "baseScoreDelta": _max_float_delta(historical_runtime.base_scores, fresh_runtime.base_scores),
                "sequenceScoreDelta": _max_float_delta(historical_runtime.sequence_scores, fresh_runtime.sequence_scores),
                "keepProbabilityDelta": _max_float_delta(historical_runtime.keep_probabilities, fresh_runtime.keep_probabilities),
            },
            "predictionCache": {
                "entryCount": len(prediction_cache),
                "singleLoadedBasicPitchModel": True,
                "storesNoteEventsOnly": True,
            },
        }


@app.local_entrypoint(name="diagnose")
def diagnose(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    payload = source.read_bytes()

    def invoke(index: int) -> dict[str, Any]:
        return rebuild_worker.remote(payload, source.suffix, index)

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKER_COUNT) as pool:
        workers = list(pool.map(invoke, range(1, WORKER_COUNT + 1)))

    workers.sort(key=lambda row: int(row["worker"]))
    direct_hashes = [row["separator"]["directPcm"]["sha256"] for row in workers]
    cascade_hashes = [row["separator"]["cascadePcm"]["sha256"] for row in workers]
    carrier_hashes = [row["carrier"]["semanticSha256"] for row in workers]
    decision_hashes = [row["downstream"]["decisionSha256"] for row in workers]

    result = {
        "schemaVersion": 2,
        "gate": "v143-contextual-prune-section3-cross-container-repeatability",
        "executionStrategy": "three-concurrent-independent-l4-workers-each-full-separator-basic-pitch-carrier-runtime-with-post-inference-runtime-fingerprint",
        "workerCount": WORKER_COUNT,
        "sourceSha256": hashlib.sha256(payload).hexdigest(),
        "workers": workers,
        "crossContainerRepeatability": {
            "directStemPcmExactAcrossWorkers": len(set(direct_hashes)) == 1,
            "cascadeStemPcmExactAcrossWorkers": len(set(cascade_hashes)) == 1,
            "carrierSemanticExactAcrossWorkers": len(set(carrier_hashes)) == 1,
            "downstreamDecisionExactAcrossWorkers": len(set(decision_hashes)) == 1,
            "historicalCarrierExactReplayCount": sum(row["carrier"]["exactHistoricalReplay"] is True for row in workers),
            "historicalDecisionExactCount": sum(row["downstream"]["decisionSetExactToHistorical"] is True for row in workers),
        },
        "invariants": {
            "runtimeFingerprintCollectedPostInference": True,
            "runtimeFingerprintUsedAsInput": False,
            "professionalReferenceOpened": False,
            "runtimeLabelsRequired": False,
            "frozenModelModified": False,
            "frozenPredictionsModified": False,
            "thresholdsModified": False,
            "liveEndpointDeployedOrModified": False,
            "productionModified": False,
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    pass
