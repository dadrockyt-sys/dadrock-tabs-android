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
COLLECTION_DEADLINE_SECONDS = 900.0
OUT = Path("debug/v143-contextual-prune/demucs-explicit-cpu-anchor/summary.json")


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
        "dadrock-v143-demucs-cpu-host-probe",
        "probe",
        environment_name="main",
    )

    print("explicit-cpu.local.spawn.start cpu=1.0 gpu=false", flush=True)
    call = fn.spawn(source_bytes, SOURCE.suffix)
    print(f"explicit-cpu.local.spawn.done functionCallId={call.object_id}", flush=True)
    print(
        f"explicit-cpu.local.wait.start deadlineSeconds={COLLECTION_DEADLINE_SECONDS}",
        flush=True,
    )
    started = time.monotonic()

    try:
        result = call.get(timeout=COLLECTION_DEADLINE_SECONDS)
    except Exception as exc:
        wall = time.monotonic() - started
        cancel_error_type = None
        print(
            f"explicit-cpu.local.wait.failed terminalType={type(exc).__name__} wallSeconds={wall:.3f}",
            flush=True,
        )
        try:
            call.cancel(terminate_containers=True)
            print("explicit-cpu.local.cancel.attempted terminateContainers=true", flush=True)
        except Exception as cancel_exc:
            cancel_error_type = type(cancel_exc).__name__
            print(
                f"explicit-cpu.local.cancel.error terminalType={cancel_error_type}",
                flush=True,
            )

        write_summary(
            {
                "schemaVersion": 1,
                "gate": "v143-demucs-explicit-cpu-anchor",
                "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
                "completed": False,
                "terminalType": type(exc).__name__,
                "functionCallId": call.object_id,
                "wallSeconds": round(wall, 3),
                "collectionDeadlineSeconds": COLLECTION_DEADLINE_SECONDS,
                "explicitModalCpu": 1.0,
                "modalGpuRequested": False,
                "remoteCallCancelAttempted": True,
                "remoteCallCancelErrorType": cancel_error_type,
                "sourceSha256": source_sha,
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
        raise RuntimeError("explicit CPU probe returned non-dict result")

    inv = result.get("invariants") or {}
    child = result.get("childRuntime") or {}
    env = child.get("environment") or {}

    structural_invariants = bool(
        inv.get("approvedFixture") is True
        and inv.get("referenceFree") is True
        and inv.get("modalGpuRequested") is False
        and inv.get("productionModified") is False
        and inv.get("protectedPipelineModified") is False
        and inv.get("childRuntimeTracePresent") is True
        and child.get("mkldnnEnabled") is False
        and int(child.get("torchNumThreads", 0)) == 1
        and int(child.get("torchNumInteropThreads", 0)) == 1
        and str(child.get("torchCpuCapability") or "").upper() == "DEFAULT"
        and env.get("V143_DEMUCS_DISABLE_MKLDNN") == "1"
        and env.get("OMP_NUM_THREADS") == "1"
        and env.get("MKL_NUM_THREADS") == "1"
        and env.get("MKL_CBWR") == "COMPATIBLE"
    )

    parity_passed = bool(
        result.get("sourceSha256") == EXPECTED_SOURCE_SHA256
        and result.get("normalizedWavSha256") == EXPECTED_NORMALIZED_SHA256
        and result.get("directGuitarSha256") == EXPECTED_GUITAR_SHA256
        and result.get("directPcmInt16Sha256") == EXPECTED_PCM_SHA256
        and result.get("demucsShiftTrace") == EXPECTED_SHIFT_TRACE
    )

    summary = {
        "schemaVersion": 1,
        "gate": "v143-demucs-explicit-cpu-anchor",
        "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
        "completed": True,
        "terminalType": "Completed",
        "functionCallId": call.object_id,
        "wallSeconds": round(wall, 3),
        "collectionDeadlineSeconds": COLLECTION_DEADLINE_SECONDS,
        "explicitModalCpu": 1.0,
        "modalGpuRequested": False,
        "sourceSha256": result.get("sourceSha256"),
        "normalizedWavSha256": result.get("normalizedWavSha256"),
        "directGuitarSha256": result.get("directGuitarSha256"),
        "directPcmInt16Sha256": result.get("directPcmInt16Sha256"),
        "directBytes": result.get("directBytes"),
        "sampleRate": result.get("sampleRate"),
        "pcmFrames": result.get("pcmFrames"),
        "pcmChannels": result.get("pcmChannels"),
        "demucsShiftTrace": result.get("demucsShiftTrace"),
        "torchVersion": child.get("torchVersion"),
        "torchCpuCapability": child.get("torchCpuCapability"),
        "torchNumThreads": child.get("torchNumThreads"),
        "torchNumInteropThreads": child.get("torchNumInteropThreads"),
        "mkldnnEnabled": child.get("mkldnnEnabled"),
        "structuralInvariantsPassed": structural_invariants,
        "historicalAnchorGuitarSha256": EXPECTED_GUITAR_SHA256,
        "historicalAnchorPcmSha256": EXPECTED_PCM_SHA256,
        "exactParityPassed": parity_passed,
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

    if not structural_invariants:
        raise SystemExit("explicit CPU structural invariants failed")
    if not parity_passed:
        raise SystemExit("explicit CPU exact historical parity failed")

    print(
        f"explicit-cpu.local.wait.done exactParityPassed=true wallSeconds={wall:.3f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
