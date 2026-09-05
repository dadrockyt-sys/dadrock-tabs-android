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
EXPECTED_DIRECT_SHA256 = "0ac47da671df6f8387c1ad1343171de0cf7a0db6985dadf3f30e4a9c7cf0189c"
EXPECTED_DIRECT_PCM_SHA256 = "2c22f04014c0f5c9c0c036125c3d702c8b87a9f67358e0dd0d3836c39c936bed"
EXPECTED_ROFORMER_SHA256 = "ce7ae8c6c57e00e1e191b8c15a8c4f39627cbcdf3b7a75ac7ca4c246f6f64b14"
EXPECTED_ROFORMER_PCM_SHA256 = "16e0a16a54ab1b007d15647d293900ecfbfabceccfa886f004a86162d4a454dd"
EXPECTED_CASCADE_SHA256 = "546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41"
EXPECTED_CASCADE_PCM_SHA256 = "75c0feefb416d8438641ceebe903253f935bd19c550e97e9ef0a90426e7727ba"
EXPECTED_ROFORMER_WEIGHT_SHA256 = "5b84f37e8d444c8cb30c79d77f613a41c05868ff9c9ac6c7049c00aefae115aa"
EXPECTED_DEMUCS_WEIGHT_SHA256 = "34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd"
EXPECTED_DEMUCS_CONFIG_SHA256 = "207405151270af8fd81c2373c25d27950916682ac91dca7884a11ce13dad6f58"
EXPECTED_SHIFT_TRACE = ["0,22050,6026"]
COLLECTION_DEADLINE_SECONDS = 1500.0
OUT = Path("debug/v143-contextual-prune/view-level-concurrency/summary.json")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_summary(summary: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, allow_nan=False), flush=True)


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    source_sha = sha256_bytes(source_bytes)
    if source_sha != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"approved fixture SHA changed: {source_sha}")

    fn = modal.Function.from_name(
        "dadrock-v143-view-level-concurrency-probe",
        "probe",
        environment_name="main",
    )

    print("view-concurrency.local.spawn.start directDemucs=cpu roformer=L4 cascadeDemucs=cpu", flush=True)
    call = fn.spawn(source_bytes, SOURCE.suffix)
    print(f"view-concurrency.local.spawn.done functionCallId={call.object_id}", flush=True)
    started = time.monotonic()

    try:
        result = call.get(timeout=COLLECTION_DEADLINE_SECONDS)
    except Exception as exc:
        wall = time.monotonic() - started
        try:
            call.cancel(terminate_containers=True)
        except Exception:
            pass
        write_summary(
            {
                "schemaVersion": 1,
                "gate": "v143-view-level-concurrency",
                "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
                "completed": False,
                "terminalType": type(exc).__name__,
                "functionCallId": call.object_id,
                "wallSeconds": round(wall, 3),
                "sourceSha256": source_sha,
                "referenceFree": True,
                "referenceFacingAccuracyScored": False,
                "referenceScoreCalls": 0,
                "qualityVerdictMade": False,
                "rawAudioRetained": False,
                "stemBytesRetained": False,
                "productionWorkerChanged": False,
                "productionBridgeChanged": False,
                "vercelChanged": False,
                "mainMergePerformed": False,
            }
        )
        raise SystemExit(1)

    wall = time.monotonic() - started
    if not isinstance(result, dict):
        raise RuntimeError("view-level concurrency probe returned non-dict result")

    model = result.get("modelIdentity") or {}
    runtime = result.get("runtime") or {}
    schedule = result.get("schedule") or {}

    parity_passed = bool(
        result.get("sourceSha256") == EXPECTED_SOURCE_SHA256
        and result.get("normalizedWavSha256") == EXPECTED_NORMALIZED_SHA256
        and result.get("directGuitarSha256") == EXPECTED_DIRECT_SHA256
        and result.get("directPcmInt16Sha256") == EXPECTED_DIRECT_PCM_SHA256
        and result.get("roformerInstrumentalSha256") == EXPECTED_ROFORMER_SHA256
        and result.get("roformerInstrumentalPcmInt16Sha256") == EXPECTED_ROFORMER_PCM_SHA256
        and result.get("cascadeGuitarSha256") == EXPECTED_CASCADE_SHA256
        and result.get("cascadePcmInt16Sha256") == EXPECTED_CASCADE_PCM_SHA256
        and result.get("directShiftTrace") == EXPECTED_SHIFT_TRACE
        and result.get("cascadeShiftTrace") == EXPECTED_SHIFT_TRACE
        and model.get("roformerWeightSha256") == EXPECTED_ROFORMER_WEIGHT_SHA256
        and model.get("demucsWeightSha256") == EXPECTED_DEMUCS_WEIGHT_SHA256
        and model.get("demucsConfigSha256") == EXPECTED_DEMUCS_CONFIG_SHA256
        and result.get("exactDirectParityPassed") is True
        and result.get("exactCascadeParityPassed") is True
        and result.get("exactRoformerParityPassed") is True
    )

    scheduling_passed = bool(
        runtime.get("demucsExecutionDevice") == "cpu"
        and int(runtime.get("demucsCpuThreadsPerChild", 0)) == 1
        and runtime.get("childProcessStartMethod") == "spawn"
        and schedule.get("directStartsBeforeRoformer") is True
        and schedule.get("cascadeStartsAfterRoformer") is True
        and schedule.get("intraDemucsParallelism") is False
        and schedule.get("unchangedExactDemucsInvocation") is True
        and schedule.get("crossRequestPersistence") is False
    )

    safety_passed = bool(
        result.get("cleanupPassed") is True
        and result.get("rawAudioRetained") is False
        and result.get("stemBytesRetained") is False
        and result.get("referenceFree") is True
        and result.get("referenceFacingAccuracyScored") is False
        and int(result.get("referenceScoreCalls", -1)) == 0
        and result.get("qualityVerdictMade") is False
        and result.get("gpuDemucsRequested") is False
        and result.get("gpuPerformanceComparisonPerformed") is False
        and result.get("productionWorkerChanged") is False
        and result.get("productionBridgeChanged") is False
        and result.get("vercelChanged") is False
        and result.get("mainMergePerformed") is False
        and result.get("allPassed") is True
    )

    summary = {
        "schemaVersion": 1,
        "gate": "v143-view-level-concurrency",
        "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
        "completed": True,
        "terminalType": "Completed",
        "functionCallId": call.object_id,
        "collectorWallSeconds": round(wall, 3),
        "collectionDeadlineSeconds": COLLECTION_DEADLINE_SECONDS,
        "sourceSha256": result.get("sourceSha256"),
        "normalizedWavSha256": result.get("normalizedWavSha256"),
        "modelIdentity": model,
        "runtime": runtime,
        "schedule": schedule,
        "roformerInstrumentalSha256": result.get("roformerInstrumentalSha256"),
        "roformerInstrumentalPcmInt16Sha256": result.get("roformerInstrumentalPcmInt16Sha256"),
        "directGuitarSha256": result.get("directGuitarSha256"),
        "directPcmInt16Sha256": result.get("directPcmInt16Sha256"),
        "cascadeGuitarSha256": result.get("cascadeGuitarSha256"),
        "cascadePcmInt16Sha256": result.get("cascadePcmInt16Sha256"),
        "directShiftTrace": result.get("directShiftTrace"),
        "cascadeShiftTrace": result.get("cascadeShiftTrace"),
        "roformerElapsedSeconds": result.get("roformerElapsedSeconds"),
        "directDemucsElapsedSeconds": result.get("directDemucsElapsedSeconds"),
        "cascadeDemucsElapsedSeconds": result.get("cascadeDemucsElapsedSeconds"),
        "roformerWallSeconds": result.get("roformerWallSeconds"),
        "directProcessWallSeconds": result.get("directProcessWallSeconds"),
        "cascadeProcessWallSeconds": result.get("cascadeProcessWallSeconds"),
        "concurrentSeparationWallSeconds": result.get("concurrentSeparationWallSeconds"),
        "sumOfConcurrentStageElapsedSeconds": result.get("sumOfConcurrentStageElapsedSeconds"),
        "historicalSequentialStageSumSeconds": result.get("historicalSequentialStageSumSeconds"),
        "crossRunContextualSpeedup": result.get("crossRunContextualSpeedup"),
        "crossRunContextualSpeedupOnly": result.get("crossRunContextualSpeedupOnly"),
        "exactParityPassed": parity_passed,
        "schedulingBoundaryPassed": scheduling_passed,
        "safetyBoundaryPassed": safety_passed,
        "allPassed": bool(parity_passed and scheduling_passed and safety_passed),
        "referenceFree": True,
        "referenceFacingAccuracyScored": False,
        "referenceScoreCalls": 0,
        "qualityVerdictMade": False,
        "rawAudioRetained": False,
        "stemBytesRetained": False,
        "productionWorkerChanged": False,
        "productionBridgeChanged": False,
        "vercelChanged": False,
        "mainMergePerformed": False,
    }
    write_summary(summary)
    if not summary["allPassed"]:
        raise SystemExit("view-level concurrency gate failed")

    print(
        "view-concurrency.local.wait.done "
        f"allPassed=true wallSeconds={wall:.3f} "
        f"concurrentSeparationWallSeconds={result.get('concurrentSeparationWallSeconds')} "
        f"crossRunContextualSpeedup={result.get('crossRunContextualSpeedup')}",
        flush=True,
    )


if __name__ == "__main__":
    main()
