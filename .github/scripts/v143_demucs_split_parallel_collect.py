from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import modal


SOURCE = Path("public/gomywayfullaitest.m4a")
EXPECTED_SOURCE_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_NORMALIZED_SHA256 = "ab64e7cdd8a792aecfb6eec518577d8d7e9d2f8aa43007e632470d9fe4511e7f"
EXPECTED_GUITAR_SHA256 = "0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c"
EXPECTED_PCM_SHA256 = "2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed"
EXPECTED_SHIFT_TRACE = ["0,22050,6026"]
EXPECTED_SPLIT_WORKERS = 4
CPU_ANCHOR_WALL_SECONDS = 666.404
COLLECTION_DEADLINE_SECONDS = 360.0
MIN_MATERIAL_SPEEDUP = 1.5
OUT = Path("debug/v143-contextual-prune/demucs-split-parallel/summary.json")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_summary(summary: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    source_sha = sha256_bytes(source_bytes)
    if source_sha != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"approved fixture SHA changed: {source_sha}")

    fn = modal.Function.from_name(
        "dadrock-v143-demucs-split-parallel-probe",
        "probe",
        environment_name="main",
    )

    print("split-parallel.local.spawn.start splitWorkers=4 modalCpu=4", flush=True)
    call = fn.spawn(source_bytes, SOURCE.suffix)
    print(f"split-parallel.local.spawn.done functionCallId={call.object_id}", flush=True)
    print(
        f"split-parallel.local.wait.start deadlineSeconds={COLLECTION_DEADLINE_SECONDS}",
        flush=True,
    )
    started = time.monotonic()

    try:
        result = call.get(timeout=COLLECTION_DEADLINE_SECONDS)
    except Exception as exc:
        wall = time.monotonic() - started
        cancel_error_type = None
        print(
            f"split-parallel.local.wait.failed terminalType={type(exc).__name__} wallSeconds={wall:.3f}",
            flush=True,
        )
        try:
            call.cancel(terminate_containers=True)
            print("split-parallel.local.cancel.attempted terminateContainers=true", flush=True)
        except Exception as cancel_exc:
            cancel_error_type = type(cancel_exc).__name__
            print(
                f"split-parallel.local.cancel.error terminalType={cancel_error_type}",
                flush=True,
            )

        write_summary(
            {
                "schemaVersion": 1,
                "gate": "v143-demucs-split-parallel",
                "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
                "completed": False,
                "terminalType": type(exc).__name__,
                "functionCallId": call.object_id,
                "wallSeconds": round(wall, 3),
                "collectionDeadlineSeconds": COLLECTION_DEADLINE_SECONDS,
                "modalCpu": 4.0,
                "demucsTorchThreadsPerOp": 1,
                "demucsSplitWorkers": EXPECTED_SPLIT_WORKERS,
                "remoteCallCancelAttempted": True,
                "remoteCallCancelErrorType": cancel_error_type,
                "exactCpuParityPassed": False,
                "materialSpeedupPassed": False,
                "referenceFree": True,
                "referenceFacingAccuracyScored": False,
                "referenceScoreCalls": 0,
                "rawAudioRetained": False,
                "stemBytesRetained": False,
                "productionWorkerChanged": False,
                "productionBridgeChanged": False,
                "vercelChanged": False,
            }
        )
        raise SystemExit(1)

    wall = time.monotonic() - started
    if not isinstance(result, dict):
        raise RuntimeError("split-parallel probe returned non-dict result")

    child = result.get("childRuntime") or {}
    child_env = child.get("environment") or {}
    parallel = result.get("splitParallelTrace") or {}

    runtime_invariants = bool(
        result.get("gate") == "v143-demucs-split-parallel-probe"
        and result.get("referenceFree") is True
        and result.get("referenceFacingAccuracyScored") is False
        and result.get("referenceScoreCalls") == 0
        and result.get("rawAudioRetained") is False
        and result.get("stemBytesRetained") is False
        and result.get("productionWorkerChanged") is False
        and result.get("productionBridgeChanged") is False
        and result.get("vercelChanged") is False
        and child.get("torchCudaAvailable") is False
        and child.get("mkldnnEnabled") is False
        and int(child.get("torchNumThreads", 0)) == 1
        and int(child.get("torchNumInteropThreads", 0)) == 1
        and child_env.get("OMP_NUM_THREADS") == "1"
        and child_env.get("MKL_NUM_THREADS") == "1"
        and child_env.get("V143_DEMUCS_DISABLE_MKLDNN") == "1"
        and parallel.get("requestedSplitWorkers") == EXPECTED_SPLIT_WORKERS
        and parallel.get("architectureApplyModelInvocationCount") == 1
        and parallel.get("device") == "cpu"
        and parallel.get("torchNumThreads") == 1
        and parallel.get("torchNumInteropThreads") == 1
        and parallel.get("cudaAvailable") is False
        and parallel.get("mkldnnEnabled") is False
        and parallel.get("ompNumThreads") == "1"
        and parallel.get("mklNumThreads") == "1"
        and parallel.get("fixedShiftRng") == "1"
    )

    exact_cpu_parity = bool(
        result.get("sourceSha256") == EXPECTED_SOURCE_SHA256
        and result.get("normalizedWavSha256") == EXPECTED_NORMALIZED_SHA256
        and result.get("directGuitarSha256") == EXPECTED_GUITAR_SHA256
        and result.get("directPcmInt16Sha256") == EXPECTED_PCM_SHA256
        and result.get("demucsShiftTrace") == EXPECTED_SHIFT_TRACE
        and result.get("exactCpuParityPassed") is True
    )

    speedup = CPU_ANCHOR_WALL_SECONDS / wall if wall > 0.0 else 0.0
    material_speedup = speedup >= MIN_MATERIAL_SPEEDUP

    summary = {
        "schemaVersion": 1,
        "gate": "v143-demucs-split-parallel",
        "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
        "completed": True,
        "terminalType": "Completed",
        "functionCallId": call.object_id,
        "wallSeconds": round(wall, 3),
        "collectionDeadlineSeconds": COLLECTION_DEADLINE_SECONDS,
        "modalCpu": 4.0,
        "demucsTorchThreadsPerOp": 1,
        "demucsSplitWorkers": EXPECTED_SPLIT_WORKERS,
        "sourceSha256": result.get("sourceSha256"),
        "normalizedWavSha256": result.get("normalizedWavSha256"),
        "directGuitarSha256": result.get("directGuitarSha256"),
        "directPcmInt16Sha256": result.get("directPcmInt16Sha256"),
        "directBytes": result.get("directBytes"),
        "sampleRate": result.get("sampleRate"),
        "pcmFrames": result.get("pcmFrames"),
        "pcmChannels": result.get("pcmChannels"),
        "demucsShiftTrace": result.get("demucsShiftTrace"),
        "separationElapsedSeconds": result.get("separationElapsedSeconds"),
        "separationWallSeconds": result.get("separationWallSeconds"),
        "totalRemoteSeconds": result.get("totalRemoteSeconds"),
        "cpuAnchorWallSeconds": CPU_ANCHOR_WALL_SECONDS,
        "speedupVsCpuAnchor": round(speedup, 3),
        "minimumMaterialSpeedup": MIN_MATERIAL_SPEEDUP,
        "runtimeInvariantsPassed": runtime_invariants,
        "exactCpuParityPassed": exact_cpu_parity,
        "materialSpeedupPassed": material_speedup,
        "splitParallelTrace": parallel,
        "referenceFree": True,
        "referenceFacingAccuracyScored": False,
        "referenceScoreCalls": 0,
        "rawAudioRetained": False,
        "stemBytesRetained": False,
        "productionWorkerChanged": False,
        "productionBridgeChanged": False,
        "vercelChanged": False,
    }
    write_summary(summary)

    if not runtime_invariants:
        raise SystemExit("split-parallel runtime invariants failed")
    if not exact_cpu_parity:
        raise SystemExit("split-parallel candidate failed exact CPU output identity")
    if not material_speedup:
        raise SystemExit("split-parallel candidate did not achieve material speedup")

    print(
        f"split-parallel.local.wait.done exactCpuParityPassed=true speedup={speedup:.3f}x wallSeconds={wall:.3f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
