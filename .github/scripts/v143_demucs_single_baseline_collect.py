from __future__ import annotations

import json
import os
from pathlib import Path

import modal


AUDIO_URL = os.environ["AUDIO_URL"]
AUDIO_BLOB_SHA = os.environ["AUDIO_BLOB_SHA"]
CLIP_SECONDS = 6.0
COLLECTION_DEADLINE_SECONDS = 300.0
OUT = Path("debug/v143-contextual-prune/demucs-single-frozen-baseline/summary.json")


def write_summary(summary: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


def validate_result(result: object) -> dict:
    if not isinstance(result, dict):
        raise RuntimeError("single baseline returned a non-dict aggregate")
    required = {
        "gate": "v143-demucs-single-frozen-baseline",
        "policy": "frozen",
        "clipSeconds": CLIP_SECONDS,
        "referenceFacingAccuracyScored": False,
        "referenceScoreCalls": 0,
        "rawAudioRetained": False,
        "stemBytesRetained": False,
    }
    for key, expected in required.items():
        if result.get(key) != expected:
            raise RuntimeError(f"single baseline returned unexpected {key}")
    return result


def main() -> None:
    fn = modal.Function.from_name(
        "dadrock-v143-demucs-single-baseline-probe",
        "run_single_frozen_baseline",
        environment_name="main",
    )

    print("baseline.local.spawn.start", flush=True)
    call = fn.spawn(AUDIO_URL, CLIP_SECONDS)
    print(f"baseline.local.spawn.done functionCallId={call.object_id}", flush=True)
    print(
        f"baseline.local.wait.start deadlineSeconds={COLLECTION_DEADLINE_SECONDS}",
        flush=True,
    )

    try:
        result = validate_result(call.get(timeout=COLLECTION_DEADLINE_SECONDS))
    except Exception as exc:
        cancel_error_type = None
        print(f"baseline.local.wait.failed terminalType={type(exc).__name__}", flush=True)
        try:
            call.cancel(terminate_containers=True)
            print("baseline.local.cancel.attempted terminateContainers=true", flush=True)
        except Exception as cancel_exc:
            cancel_error_type = type(cancel_exc).__name__
            print(
                f"baseline.local.cancel.error terminalType={cancel_error_type}",
                flush=True,
            )

        summary = {
            "schemaVersion": 1,
            "gate": "v143-demucs-single-frozen-baseline",
            "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
            "audioBlobSha": AUDIO_BLOB_SHA,
            "clipSeconds": CLIP_SECONDS,
            "collectionDeadlineSeconds": COLLECTION_DEADLINE_SECONDS,
            "completed": False,
            "terminalType": type(exc).__name__,
            "functionCallId": call.object_id,
            "remoteCallCancelAttempted": True,
            "remoteCallCancelErrorType": cancel_error_type,
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
        raise SystemExit(1)

    print("baseline.local.wait.done completed=true", flush=True)
    summary = {
        "schemaVersion": 1,
        "gate": "v143-demucs-single-frozen-baseline",
        "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
        "audioBlobSha": AUDIO_BLOB_SHA,
        "clipSeconds": CLIP_SECONDS,
        "collectionDeadlineSeconds": COLLECTION_DEADLINE_SECONDS,
        "completed": True,
        "terminalType": "Completed",
        "functionCallId": call.object_id,
        "model": result["model"],
        "singleStem": result["singleStem"],
        "demucsShifts": result["demucsShifts"],
        "demucsOverlap": result["demucsOverlap"],
        "demucsSegmentSize": result["demucsSegmentSize"],
        "separatorSeed": result["separatorSeed"],
        "device": result["device"],
        "policy": result["policy"],
        "elapsedSeconds": float(result["elapsedSeconds"]),
        "wallSeconds": float(result["wallSeconds"]),
        "sha256": str(result["sha256"]),
        "bytes": int(result["bytes"]),
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


if __name__ == "__main__":
    main()
