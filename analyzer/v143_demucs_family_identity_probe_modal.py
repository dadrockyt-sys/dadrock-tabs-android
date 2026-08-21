from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import subprocess
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_historical_band_diagnostic_modal import diagnostic_image
from v143_section3_hashseed_ab_probe_modal import (
    KNOWN_CASCADE,
    KNOWN_DIRECT,
    _build_three_stage_stems,
    _family,
)
from v143_contextual_prune_historical_band_diagnostic_modal import (
    _research_normalize_audio,
    _safe_suffix,
)
from v143_contextual_prune_section3_repeatability_modal import _pcm_sha256


app = modal.App("dadrock-v143-demucs-family-identity-probe")
probe_image = diagnostic_image.add_local_python_source(
    "v143_section3_hashseed_ab_probe_modal",
    "v143_contextual_prune_historical_band_diagnostic_modal",
    "v143_contextual_prune_section3_repeatability_modal",
)

BATCH_SIZE = 4
MAX_BATCHES = 3


def _package_version(name: str) -> str | None:
    try:
        return importlib_metadata.version(name)
    except importlib_metadata.PackageNotFoundError:
        return None


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _model_inventory() -> list[dict[str, Any]]:
    roots = [
        Path("/tmp/audio-separator-models"),
        Path.home() / ".cache" / "torch" / "hub" / "checkpoints",
        Path.home() / ".cache" / "audio-separator",
        Path.home() / ".local" / "share" / "audio-separator",
    ]
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            key = str(path.resolve())
            if key in seen:
                continue
            seen.add(key)
            try:
                size = int(path.stat().st_size)
                rows.append(
                    {
                        "path": key,
                        "size": size,
                        "sha256": _sha256_file(path),
                    }
                )
            except OSError as exc:
                rows.append({"path": key, "error": f"{type(exc).__name__}: {exc}"})
    return rows


def _canonical_sha(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _runtime_identity() -> dict[str, Any]:
    import torch

    smi: dict[str, Any]
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
        smi = {
            "returnCode": int(completed.returncode),
            "rows": [line.strip() for line in completed.stdout.splitlines() if line.strip()],
            "stderrTail": (completed.stderr or "")[-1000:],
        }
    except Exception as exc:
        smi = {"error": f"{type(exc).__name__}: {exc}"}

    env_info: dict[str, Any]
    try:
        completed = subprocess.run(
            ["audio-separator", "--env_info"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        env_info = {
            "returnCode": int(completed.returncode),
            "stdoutTail": (completed.stdout or "")[-8000:],
            "stderrTail": (completed.stderr or "")[-4000:],
        }
    except Exception as exc:
        env_info = {"error": f"{type(exc).__name__}: {exc}"}

    gpu: dict[str, Any] = {
        "available": bool(torch.cuda.is_available()),
        "deviceCount": int(torch.cuda.device_count()),
    }
    if torch.cuda.is_available():
        properties = torch.cuda.get_device_properties(0)
        gpu.update(
            {
                "name": str(properties.name),
                "computeCapability": [int(properties.major), int(properties.minor)],
                "totalMemory": int(properties.total_memory),
                "properties": str(properties),
            }
        )

    return {
        "modalTaskId": os.environ.get("MODAL_TASK_ID"),
        "packages": {
            "torch": str(torch.__version__),
            "audioSeparator": _package_version("audio-separator"),
            "demucs": _package_version("demucs"),
            "basicPitch": _package_version("basic-pitch"),
        },
        "cuda": {
            "torchCudaVersion": None if torch.version.cuda is None else str(torch.version.cuda),
            "cudnnVersion": int(torch.backends.cudnn.version()) if torch.backends.cudnn.version() is not None else None,
            "deterministicAlgorithmsEnabled": bool(torch.are_deterministic_algorithms_enabled()),
            "cudnnDeterministic": bool(torch.backends.cudnn.deterministic),
            "cudnnBenchmark": bool(torch.backends.cudnn.benchmark),
            "cudaMatmulAllowTf32": bool(torch.backends.cuda.matmul.allow_tf32),
            "cudnnAllowTf32": bool(torch.backends.cudnn.allow_tf32),
        },
        "gpu": gpu,
        "nvidiaSmi": smi,
        "audioSeparatorEnvInfo": env_info,
        "relevantEnvironment": {
            "TORCH_HOME": os.environ.get("TORCH_HOME"),
            "XDG_CACHE_HOME": os.environ.get("XDG_CACHE_HOME"),
            "CUBLAS_WORKSPACE_CONFIG": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
        },
    }


@app.function(image=probe_image, gpu="L4", timeout=1800, memory=12288)
def identity_worker(source_audio: bytes, suffix: str, worker_index: int) -> dict[str, Any]:
    import tempfile

    if not source_audio:
        raise ValueError("Probe audio is empty")

    with tempfile.TemporaryDirectory(prefix=f"v143-demucs-identity-{worker_index}-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, normalized)

        stems = _build_three_stage_stems(normalized, root / "separator", "fixed-143")
        direct = _pcm_sha256(stems["direct"])
        roformer = _pcm_sha256(stems["roformer"])
        cascade = _pcm_sha256(stems["cascade"])
        inventory = _model_inventory()
        runtime = _runtime_identity()

        direct_family = _family(direct["sha256"], KNOWN_DIRECT)
        cascade_family = _family(cascade["sha256"], KNOWN_CASCADE)
        software_payload = {
            "packages": runtime["packages"],
            "cuda": runtime["cuda"],
            "audioSeparatorEnvInfo": runtime["audioSeparatorEnvInfo"],
            "modelInventory": inventory,
        }

        return {
            "worker": int(worker_index),
            "directFamily": direct_family,
            "cascadeFamily": cascade_family,
            "familyLockstep": direct_family == cascade_family,
            "directPcm": direct,
            "roformerPcm": roformer,
            "cascadePcm": cascade,
            "runtimeIdentity": runtime,
            "modelInventory": inventory,
            "modelInventorySha256": _canonical_sha(inventory),
            "softwarePayloadSha256": _canonical_sha(software_payload),
        }


def _counts(values: list[str]) -> dict[str, int]:
    return {value: values.count(value) for value in sorted(set(values))}


@app.local_entrypoint(name="diagnose")
def diagnose(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    payload = source.read_bytes()

    workers: list[dict[str, Any]] = []
    batches_run = 0
    for batch in range(MAX_BATCHES):
        start = batch * BATCH_SIZE + 1

        def invoke(offset: int) -> dict[str, Any]:
            return identity_worker.remote(payload, source.suffix, start + offset)

        with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as pool:
            workers.extend(pool.map(invoke, range(BATCH_SIZE)))
        batches_run += 1
        families = {row["directFamily"] for row in workers}
        if "A" in families and "B" in families:
            break

    workers.sort(key=lambda row: int(row["worker"]))
    direct_families = [str(row["directFamily"]) for row in workers]
    cascade_families = [str(row["cascadeFamily"]) for row in workers]
    inventory_hashes = {str(row["modelInventorySha256"]) for row in workers}
    software_hashes = {str(row["softwarePayloadSha256"]) for row in workers}
    roformer_hashes = {str(row["roformerPcm"]["sha256"]) for row in workers}

    result = {
        "schemaVersion": 1,
        "gate": "v143-demucs-family-identity-probe",
        "executionStrategy": "adaptive-fixed-143-demucs-family-capture-with-post-separation-runtime-and-model-identity",
        "batchSize": BATCH_SIZE,
        "maxBatches": MAX_BATCHES,
        "batchesRun": batches_run,
        "workerCount": len(workers),
        "sourceSha256": hashlib.sha256(payload).hexdigest(),
        "workers": workers,
        "summary": {
            "directFamilyCounts": _counts(direct_families),
            "cascadeFamilyCounts": _counts(cascade_families),
            "allDirectCascadeFamiliesLockstep": all(row["familyLockstep"] is True for row in workers),
            "bothKnownFamiliesObserved": "A" in direct_families and "B" in direct_families,
            "roformerPcmExactAcrossWorkers": len(roformer_hashes) == 1,
            "modelInventoryExactAcrossWorkers": len(inventory_hashes) == 1,
            "softwarePayloadExactAcrossWorkers": len(software_hashes) == 1,
            "modelInventoryHashes": sorted(inventory_hashes),
            "softwarePayloadHashes": sorted(software_hashes),
            "roformerPcmHashes": sorted(roformer_hashes),
        },
        "invariants": {
            "pythonHashSeedAtChildStartup": 143,
            "separatorSeed": 143,
            "demucsShifts": 1,
            "demucsOverlap": 0.10,
            "demucsSegmentSize": 6,
            "roformerBatchSize": 1,
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
