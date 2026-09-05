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
COLLECTION_DEADLINE_SECONDS = 1200.0
OUT = Path("debug/v143-contextual-prune/exact-stage-cache-real-audio/summary.json")


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
        "dadrock-v143-exact-cache-real-audio",
        "probe",
        environment_name="main",
    )

    print("exact-cache-real.local.spawn.start cpu=1.0 gpu=false", flush=True)
    call = fn.spawn(source_bytes, SOURCE.suffix)
    print(
        f"exact-cache-real.local.spawn.done functionCallId={call.object_id}",
        flush=True,
    )
    print(
        f"exact-cache-real.local.wait.start deadlineSeconds={COLLECTION_DEADLINE_SECONDS}",
        flush=True,
    )
    started = time.monotonic()

    try:
        result = call.get(timeout=COLLECTION_DEADLINE_SECONDS)
    except Exception as exc:
        wall = time.monotonic() - started
        cancel_error_type = None
        print(
            "exact-cache-real.local.wait.failed "
            f"terminalType={type(exc).__name__} wallSeconds={wall:.3f}",
            flush=True,
        )
        try:
            call.cancel(terminate_containers=True)
            print(
                "exact-cache-real.local.cancel.attempted terminateContainers=true",
                flush=True,
            )
        except Exception as cancel_exc:
            cancel_error_type = type(cancel_exc).__name__
            print(
                "exact-cache-real.local.cancel.error "
                f"terminalType={cancel_error_type}",
                flush=True,
            )

        write_summary(
            {
                "schemaVersion": 1,
                "gate": "v143-exact-stage-cache-real-audio",
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
        raise RuntimeError("real-audio exact-cache probe returned non-dict result")

    parity_passed = bool(
        result.get("sourceSha256") == EXPECTED_SOURCE_SHA256
        and result.get("normalizedWavSha256") == EXPECTED_NORMALIZED_SHA256
        and result.get("directGuitarSha256") == EXPECTED_GUITAR_SHA256
        and result.get("directPcmInt16Sha256") == EXPECTED_PCM_SHA256
        and result.get("warmHitGuitarSha256") == EXPECTED_GUITAR_SHA256
        and result.get("warmHitPcmInt16Sha256") == EXPECTED_PCM_SHA256
        and result.get("demucsShiftTrace") == EXPECTED_SHIFT_TRACE
    )
    cache_semantics_passed = bool(
        result.get("initialMissPassed") is True
        and result.get("missPopulatePassed") is True
        and result.get("warmHitPassed") is True
        and result.get("fingerprintMismatchMissPassed") is True
        and result.get("fingerprintMismatchChangesKeyPassed") is True
        and result.get("corruptionLookupRejectedPassed") is True
        and result.get("corruptionFallbackReachedPassed") is True
        and int(result.get("separatorComputeCalls", 0)) == 1
        and int(result.get("corruptionFallbackCalls", 0)) == 1
        and result.get("cleanupPassed") is True
        and result.get("allPassed") is True
    )
    safety_passed = bool(
        result.get("referenceFree") is True
        and result.get("referenceFacingAccuracyScored") is False
        and int(result.get("referenceScoreCalls", -1)) == 0
        and result.get("qualityVerdictMade") is False
        and result.get("rawAudioRetained") is False
        and result.get("stemBytesRetained") is False
        and result.get("productionWorkerChanged") is False
        and result.get("productionBridgeChanged") is False
        and result.get("vercelChanged") is False
        and result.get("mainMergePerformed") is False
    )

    summary = {
        "schemaVersion": 1,
        "gate": "v143-exact-stage-cache-real-audio",
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
        "warmHitGuitarSha256": result.get("warmHitGuitarSha256"),
        "warmHitPcmInt16Sha256": result.get("warmHitPcmInt16Sha256"),
        "demucsShiftTrace": result.get("demucsShiftTrace"),
        "directBytes": result.get("directBytes"),
        "sampleRate": result.get("sampleRate"),
        "pcmFrames": result.get("pcmFrames"),
        "pcmChannels": result.get("pcmChannels"),
        "cacheKey": result.get("cacheKey"),
        "fingerprint": result.get("fingerprint"),
        "modelIdentity": result.get("modelIdentity"),
        "separatorComputeCalls": result.get("separatorComputeCalls"),
        "corruptionFallbackCalls": result.get("corruptionFallbackCalls"),
        "missWallSeconds": result.get("missWallSeconds"),
        "hitWallSeconds": result.get("hitWallSeconds"),
        "hitSpeedup": result.get("hitSpeedup"),
        "separatorElapsedSeconds": result.get("separatorElapsedSeconds"),
        "initialMissPassed": result.get("initialMissPassed"),
        "missPopulatePassed": result.get("missPopulatePassed"),
        "warmHitPassed": result.get("warmHitPassed"),
        "fingerprintMismatchMissPassed": result.get("fingerprintMismatchMissPassed"),
        "fingerprintMismatchChangesKeyPassed": result.get(
            "fingerprintMismatchChangesKeyPassed"
        ),
        "corruptionLookupRejectedPassed": result.get(
            "corruptionLookupRejectedPassed"
        ),
        "corruptionFallbackReachedPassed": result.get(
            "corruptionFallbackReachedPassed"
        ),
        "cleanupPassed": result.get("cleanupPassed"),
        "exactAnchorParityPassed": parity_passed,
        "cacheSemanticsPassed": cache_semantics_passed,
        "safetyBoundaryPassed": safety_passed,
        "allPassed": bool(parity_passed and cache_semantics_passed and safety_passed),
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
        raise SystemExit("real-audio exact-cache gate failed")

    print(
        "exact-cache-real.local.wait.done "
        f"allPassed=true wallSeconds={wall:.3f} "
        f"missWallSeconds={result.get('missWallSeconds')} "
        f"hitWallSeconds={result.get('hitWallSeconds')} "
        f"separatorComputeCalls={result.get('separatorComputeCalls')}",
        flush=True,
    )


if __name__ == "__main__":
    main()
