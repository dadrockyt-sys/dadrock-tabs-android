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
EXPECTED_SHIFT_TRACE = ["0,22050,6026", "0,22050,6026"]
EXPECTED_KEYS = [
    "cascadeGuitar",
    "diagnosticOnly",
    "directGuitar",
    "models",
    "referenceFree",
    "roformerInstrumental",
    "settings",
]
COLLECTION_DEADLINE_SECONDS = 1500.0
OUT = Path("debug/v143-contextual-prune/seeded-scheduler-runtime/summary.json")


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
        "dadrock-v143-seeded-scheduler-runtime-gate",
        "probe",
        environment_name="main",
    )

    print("seeded-scheduler-runtime.local.spawn.start implementationSpecific=true", flush=True)
    call = fn.spawn(source_bytes, SOURCE.suffix)
    print(f"seeded-scheduler-runtime.local.spawn.done functionCallId={call.object_id}", flush=True)
    started = time.monotonic()

    try:
        result = call.get(timeout=COLLECTION_DEADLINE_SECONDS)
    except Exception as exc:
        wall = time.monotonic() - started
        try:
            call.cancel(terminate_containers=True)
        except Exception:
            pass
        summary = {
            "schemaVersion": 1,
            "gate": "v143-seeded-scheduler-runtime",
            "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
            "completed": False,
            "terminalType": type(exc).__name__,
            "functionCallId": call.object_id,
            "collectorWallSeconds": round(wall, 3),
            "sourceSha256": source_sha,
            "referenceFree": True,
            "referenceFacingInputs": 0,
            "referenceFacingAccuracyScored": False,
            "referenceScoreCalls": 0,
            "qualityVerdictMade": False,
            "rawAudioRetained": False,
            "stemBytesRetained": False,
            "productionWorkerChanged": False,
            "productionBridgeChanged": False,
            "vercelChanged": False,
            "mainMergePerformed": False,
            "allPassed": False,
        }
        write_summary(summary)
        raise SystemExit(1)

    wall = time.monotonic() - started
    if not isinstance(result, dict):
        raise RuntimeError("seeded scheduler runtime probe returned non-dict result")

    model = result.get("modelIdentity") or {}
    parity_passed = bool(
        result.get("sourceSha256") == EXPECTED_SOURCE_SHA256
        and result.get("normalizedWavSha256") == EXPECTED_NORMALIZED_SHA256
        and result.get("directGuitarSha256") == EXPECTED_DIRECT_SHA256
        and result.get("directPcmInt16Sha256") == EXPECTED_DIRECT_PCM_SHA256
        and result.get("roformerInstrumentalSha256") == EXPECTED_ROFORMER_SHA256
        and result.get("roformerInstrumentalPcmInt16Sha256") == EXPECTED_ROFORMER_PCM_SHA256
        and result.get("cascadeGuitarSha256") == EXPECTED_CASCADE_SHA256
        and result.get("cascadePcmInt16Sha256") == EXPECTED_CASCADE_PCM_SHA256
        and result.get("demucsShiftTrace") == EXPECTED_SHIFT_TRACE
        and model.get("roformerWeightSha256") == EXPECTED_ROFORMER_WEIGHT_SHA256
        and model.get("demucsWeightSha256") == EXPECTED_DEMUCS_WEIGHT_SHA256
        and model.get("demucsConfigSha256") == EXPECTED_DEMUCS_CONFIG_SHA256
        and result.get("exactParityPassed") is True
    )

    contract_passed = bool(
        result.get("publicReturnKeys") == EXPECTED_KEYS
        and result.get("publicContractPassed") is True
        and result.get("runtimeInvariantPassed") is True
        and result.get("schedulerStartMethod") == "spawn"
    )

    safety_passed = bool(
        result.get("cleanupPassed") is True
        and result.get("rawAudioRetained") is False
        and result.get("stemBytesRetained") is False
        and result.get("crossRequestPersistence") is False
        and result.get("referenceFree") is True
        and int(result.get("referenceFacingInputs", -1)) == 0
        and result.get("referenceFacingAccuracyScored") is False
        and int(result.get("referenceScoreCalls", -1)) == 0
        and result.get("qualityVerdictMade") is False
        and result.get("productionWorkerChanged") is False
        and result.get("productionBridgeChanged") is False
        and result.get("vercelChanged") is False
        and result.get("mainMergePerformed") is False
        and result.get("allPassed") is True
    )

    summary = dict(result)
    summary.update(
        {
            "schemaVersion": 1,
            "gate": "v143-seeded-scheduler-runtime",
            "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
            "functionCallId": call.object_id,
            "collectorWallSeconds": round(wall, 3),
            "collectionDeadlineSeconds": COLLECTION_DEADLINE_SECONDS,
            "exactParityPassed": parity_passed,
            "publicContractPassed": contract_passed,
            "safetyBoundaryPassed": safety_passed,
            "allPassed": bool(parity_passed and contract_passed and safety_passed),
        }
    )
    write_summary(summary)

    if not summary["allPassed"]:
        raise SystemExit("seeded scheduler approved-fixture runtime gate failed")

    print(
        "seeded-scheduler-runtime.local.wait.done "
        f"allPassed=true wallSeconds={wall:.3f} runtimeSeconds={result.get('runtimeSeconds')}",
        flush=True,
    )


if __name__ == "__main__":
    main()
