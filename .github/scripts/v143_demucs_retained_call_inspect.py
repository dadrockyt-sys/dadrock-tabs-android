from __future__ import annotations

import json
import os
from pathlib import Path

import modal


CALL_IDS = [
    "fc-01M1PNPXNEST24KNCBC2XN054Z",
    "fc-01M1PNPXRQ51CWRASTG0E8FT3A",
    "fc-01M1PNPXVP2A7YAJZ6WDCTVMA8",
    "fc-01M1PNPXYXRPD6C0EWPWS7DNT4",
]

OUT = Path("debug/v143-contextual-prune/demucs-retained-call-inspection/summary.json")


def safe_result(call_id: str) -> dict:
    call = modal.FunctionCall.from_id(call_id)
    try:
        result = call.get(timeout=5.0)
    except Exception as exc:
        return {
            "functionCallId": call_id,
            "terminalType": type(exc).__name__,
            "completedAggregateAvailable": False,
        }

    if not isinstance(result, dict):
        return {
            "functionCallId": call_id,
            "terminalType": "UnexpectedResultType",
            "completedAggregateAvailable": False,
        }

    # Retain only aggregate diagnostic fields. Never persist audio/stem payloads.
    return {
        "functionCallId": call_id,
        "terminalType": "Completed",
        "completedAggregateAvailable": True,
        "gate": result.get("gate"),
        "policy": result.get("policy"),
        "clipSeconds": result.get("clipSeconds"),
        "elapsedSeconds": result.get("elapsedSeconds"),
        "wallSeconds": result.get("wallSeconds"),
        "sha256": result.get("sha256"),
        "bytes": result.get("bytes"),
        "referenceFacingAccuracyScored": result.get("referenceFacingAccuracyScored"),
        "referenceScoreCalls": result.get("referenceScoreCalls"),
        "rawAudioRetained": result.get("rawAudioRetained"),
        "stemBytesRetained": result.get("stemBytesRetained"),
    }


def main() -> None:
    rows = [safe_result(call_id) for call_id in CALL_IDS]
    summary = {
        "schemaVersion": 1,
        "gate": "v143-demucs-retained-call-inspection",
        "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
        "readOnlyInspection": True,
        "newAudioExecution": False,
        "newFunctionCallsSpawned": 0,
        "referenceFree": True,
        "referenceFacingAccuracyScored": False,
        "referenceScoreCalls": 0,
        "rawAudioRetained": False,
        "stemBytesRetained": False,
        "productionWorkerChanged": False,
        "productionBridgeChanged": False,
        "vercelChanged": False,
        "calls": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
