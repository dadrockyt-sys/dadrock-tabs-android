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
EXPECTED_CASCADE_SHA256 = "546e5170870cc6c73e1f0a8eeb8314f7b6262079593e0b484207bb38f323cc41"
EXPECTED_DEMUCS_WEIGHT_SHA256 = "34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd"
EXPECTED_DEMUCS_CONFIG_SHA256 = "207405151270af8fd81c2373c25d27950916682ac91dca7884a11ce13dad6f58"
EXPECTED_SHIFT_TRACE = ["0,22050,6026"]
COLLECTION_DEADLINE_SECONDS = 1200.0
OUT = Path("debug/v143-contextual-prune/exact-cascade-cache-real-audio/summary.json")


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
        "dadrock-v143-exact-cascade-cache-real-audio",
        "probe",
        environment_name="main",
    )

    print("exact-cascade-cache.local.spawn.start roformerGpu=L4 cascadeDemucs=cpu", flush=True)
    call = fn.spawn(source_bytes, SOURCE.suffix)
    print(f"exact-cascade-cache.local.spawn.done functionCallId={call.object_id}", flush=True)
    print(
        f"exact-cascade-cache.local.wait.start deadlineSeconds={COLLECTION_DEADLINE_SECONDS}",
        flush=True,
    )
    started = time.monotonic()

    try:
        result = call.get(timeout=COLLECTION_DEADLINE_SECONDS)
    except Exception as exc:
        wall = time.monotonic() - started
        cancel_error_type = None
        print(
            f"exact-cascade-cache.local.wait.failed terminalType={type(exc).__name__} wallSeconds={wall:.3f}",
            flush=True,
        )
        try:
            call.cancel(terminate_containers=True)
            print("exact-cascade-cache.local.cancel.attempted terminateContainers=true", flush=True)
        except Exception as cancel_exc:
            cancel_error_type = type(cancel_exc).__name__
            print(
                f"exact-cascade-cache.local.cancel.error terminalType={cancel_error_type}",
                flush=True,
            )

        write_summary(
            {
                "schemaVersion": 1,
                "gate": "v143-exact-cascade-stage-cache-real-audio",
                "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
                "completed": False,
                "terminalType": type(exc).__name__,
                "functionCallId": call.object_id,
                "wallSeconds": round(wall, 3),
                "collectionDeadlineSeconds": COLLECTION_DEADLINE_SECONDS,
                "sourceSha256": source_sha,
                "referenceFree": True,
                "referenceFacingAccuracyScored": False,
                "referenceScoreCalls": 0,
                "qualityVerdictMade": False,
                "gpuPerformanceComparisonPerformed": False,
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
        raise RuntimeError("cascade exact-cache probe returned non-dict result")

    model = result.get("modelIdentity") or {}
    parity_passed = bool(
        result.get("sourceSha256") == EXPECTED_SOURCE_SHA256
        and result.get("normalizedWavSha256") == EXPECTED_NORMALIZED_SHA256
        and result.get("historicalCurrentRegimeCascadeAnchorSha256") == EXPECTED_CASCADE_SHA256
        and result.get("cascadeGuitarSha256") == EXPECTED_CASCADE_SHA256
        and result.get("warmHitCascadeGuitarSha256") == EXPECTED_CASCADE_SHA256
        and result.get("cascadeDemucsShiftTrace") == EXPECTED_SHIFT_TRACE
        and model.get("demucsWeightSha256") == EXPECTED_DEMUCS_WEIGHT_SHA256
        and model.get("demucsConfigSha256") == EXPECTED_DEMUCS_CONFIG_SHA256
    )
    cache_semantics_passed = bool(
        result.get("initialMissPassed") is True
        and result.get("missPopulatePassed") is True
        and result.get("warmHitPassed") is True
        and result.get("fingerprintMismatchMissPassed") is True
        and result.get("fingerprintMismatchChangesKeyPassed") is True
        and result.get("corruptionLookupRejectedPassed") is True
        and result.get("corruptionFallbackReachedPassed") is True
        and int(result.get("computeCalls", 0)) == 1
        and int(result.get("roformerComputeCalls", 0)) == 1
        and int(result.get("cascadeDemucsComputeCalls", 0)) == 1
        and int(result.get("directDemucsComputeCalls", -1)) == 0
        and int(result.get("corruptionFallbackCalls", 0)) == 1
        and result.get("cleanupPassed") is True
        and result.get("allPassed") is True
    )
    safety_passed = bool(
        result.get("referenceFree") is True
        and result.get("referenceFacingAccuracyScored") is False
        and int(result.get("referenceScoreCalls", -1)) == 0
        and result.get("qualityVerdictMade") is False
        and result.get("gpuPerformanceComparisonPerformed") is False
        and result.get("rawAudioRetained") is False
        and result.get("stemBytesRetained") is False
        and result.get("productionWorkerChanged") is False
        and result.get("productionBridgeChanged") is False
        and result.get("vercelChanged") is False
        and result.get("mainMergePerformed") is False
    )

    summary = {
        "schemaVersion": 1,
        "gate": "v143-exact-cascade-stage-cache-real-audio",
        "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
        "completed": True,
        "terminalType": "Completed",
        "functionCallId": call.object_id,
        "wallSeconds": round(wall, 3),
        "collectionDeadlineSeconds": COLLECTION_DEADLINE_SECONDS,
        "sourceSha256": result.get("sourceSha256"),
        "normalizedWavSha256": result.get("normalizedWavSha256"),
        "historicalCurrentRegimeCascadeAnchorSha256": result.get(
            "historicalCurrentRegimeCascadeAnchorSha256"
        ),
        "cacheKey": result.get("cacheKey"),
        "fingerprint": result.get("fingerprint"),
        "modelIdentity": model,
        "roformerParentRuntime": result.get("roformerParentRuntime"),
        "roformerInstrumentalSha256": result.get("roformerInstrumentalSha256"),
        "roformerInstrumentalPcmInt16Sha256": result.get(
            "roformerInstrumentalPcmInt16Sha256"
        ),
        "roformerInstrumentalBytes": result.get("roformerInstrumentalBytes"),
        "roformerSampleRate": result.get("roformerSampleRate"),
        "roformerPcmFrames": result.get("roformerPcmFrames"),
        "roformerPcmChannels": result.get("roformerPcmChannels"),
        "cascadeGuitarSha256": result.get("cascadeGuitarSha256"),
        "cascadePcmInt16Sha256": result.get("cascadePcmInt16Sha256"),
        "cascadeBytes": result.get("cascadeBytes"),
        "cascadeSampleRate": result.get("cascadeSampleRate"),
        "cascadePcmFrames": result.get("cascadePcmFrames"),
        "cascadePcmChannels": result.get("cascadePcmChannels"),
        "warmHitCascadeGuitarSha256": result.get("warmHitCascadeGuitarSha256"),
        "warmHitCascadePcmInt16Sha256": result.get("warmHitCascadePcmInt16Sha256"),
        "cascadeDemucsShiftTrace": result.get("cascadeDemucsShiftTrace"),
        "roformerElapsedSeconds": result.get("roformerElapsedSeconds"),
        "cascadeDemucsElapsedSeconds": result.get("cascadeDemucsElapsedSeconds"),
        "missWallSeconds": result.get("missWallSeconds"),
        "hitWallSeconds": result.get("hitWallSeconds"),
        "hitSpeedup": result.get("hitSpeedup"),
        "computeCalls": result.get("computeCalls"),
        "roformerComputeCalls": result.get("roformerComputeCalls"),
        "cascadeDemucsComputeCalls": result.get("cascadeDemucsComputeCalls"),
        "directDemucsComputeCalls": result.get("directDemucsComputeCalls"),
        "corruptionFallbackCalls": result.get("corruptionFallbackCalls"),
        "initialMissPassed": result.get("initialMissPassed"),
        "missPopulatePassed": result.get("missPopulatePassed"),
        "warmHitPassed": result.get("warmHitPassed"),
        "fingerprintMismatchMissPassed": result.get("fingerprintMismatchMissPassed"),
        "fingerprintMismatchChangesKeyPassed": result.get(
            "fingerprintMismatchChangesKeyPassed"
        ),
        "corruptionLookupRejectedPassed": result.get("corruptionLookupRejectedPassed"),
        "corruptionFallbackReachedPassed": result.get("corruptionFallbackReachedPassed"),
        "cleanupPassed": result.get("cleanupPassed"),
        "exactCascadeParityPassed": parity_passed,
        "cacheSemanticsPassed": cache_semantics_passed,
        "safetyBoundaryPassed": safety_passed,
        "allPassed": bool(parity_passed and cache_semantics_passed and safety_passed),
        "referenceFree": True,
        "referenceFacingAccuracyScored": False,
        "referenceScoreCalls": 0,
        "qualityVerdictMade": False,
        "gpuPerformanceComparisonPerformed": False,
        "rawAudioRetained": False,
        "stemBytesRetained": False,
        "productionWorkerChanged": False,
        "productionBridgeChanged": False,
        "vercelChanged": False,
        "mainMergePerformed": False,
    }
    write_summary(summary)

    if not summary["allPassed"]:
        raise SystemExit("cascade exact-cache gate failed")

    print(
        "exact-cascade-cache.local.wait.done "
        f"allPassed=true wallSeconds={wall:.3f} "
        f"missWallSeconds={result.get('missWallSeconds')} "
        f"hitWallSeconds={result.get('hitWallSeconds')} "
        f"directDemucsComputeCalls={result.get('directDemucsComputeCalls')}",
        flush=True,
    )


if __name__ == "__main__":
    main()
