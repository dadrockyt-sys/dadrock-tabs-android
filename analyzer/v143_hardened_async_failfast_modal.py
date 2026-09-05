from __future__ import annotations

import os
import time
from typing import Any

# These names are intentionally isolated and must be set before importing the
# bridge so its Queue/app handles resolve away from production.
os.environ.setdefault("V143_HTTP_APP_NAME", "dadrock-v143-async-failfast-smoke")
os.environ.setdefault(
    "V143_ASYNC_RESULT_QUEUE_NAME",
    "dadrock-v143-async-failfast-smoke-results",
)

import modal
import v143_modal_http_endpoint as bridge


DRIVER_APP_NAME = "dadrock-v143-async-failfast-driver"
app = modal.App(DRIVER_APP_NAME)
image = bridge.http_image.add_local_python_source("v143_modal_http_endpoint")


@app.function(
    image=image,
    timeout=120,
    memory=1024,
    secrets=[modal.Secret.from_name("dadrock-analyzer-secret")],
)
def prove_failfast_status_transition() -> dict[str, Any]:
    expected_token = str(os.environ.get("ANALYZER_API_TOKEN") or "")
    if not expected_token:
        raise RuntimeError("Analyzer token is unavailable.")

    job_id = bridge.create_job_id()
    job_token = bridge.build_job_token(job_id, expected_token)

    # This payload is deliberately rejected by the real worker before download,
    # normalization, separator/model execution, or any audio access.
    payload = {
        "token": expected_token,
        "blobToken": "not-used",
        "audioUrl": "not-a-url",
        "pathname": "diagnostic/no-audio",
        "song": "diagnostic",
        "artist": "diagnostic",
        "transcriptionType": "rhythm",
    }

    call = bridge.run_rhythm_async_job.spawn(job_id, payload)
    bridge._queue_orchestrator_control(job_id, call.object_id)

    saw_processing = False
    terminal: dict[str, Any] | None = None
    deadline = time.monotonic() + 60.0
    while time.monotonic() < deadline:
        state = bridge._status_rhythm_job(
            {
                "token": expected_token,
                "jobToken": job_token,
                "transcriptionType": "rhythm",
            },
            expected_token=expected_token,
        )
        status = str(state.get("status") or "")
        if status == "processing":
            saw_processing = True
            time.sleep(0.5)
            continue
        terminal = state
        break

    if terminal is None:
        raise RuntimeError("Hardened status poll never reached a terminal state.")
    if terminal.get("status") != "failed":
        raise RuntimeError(f"Expected bounded failed state, got {terminal!r}")

    ack = bridge._ack_rhythm_job(
        {
            "token": expected_token,
            "jobToken": job_token,
            "transcriptionType": "rhythm",
        },
        expected_token=expected_token,
    )
    if ack.get("status") != "acknowledged":
        raise RuntimeError("ACK did not succeed.")

    result_remaining = list(
        bridge.async_result_queue.iterate(
            partition=job_id,
            item_poll_timeout=0.0,
        )
    )
    control_remaining = list(
        bridge.async_result_queue.iterate(
            partition=bridge._control_partition(job_id),
            item_poll_timeout=0.0,
        )
    )
    if result_remaining or control_remaining:
        raise RuntimeError("ACK did not clear both transient partitions.")

    return {
        "schemaVersion": 1,
        "gate": "v143-hardened-async-failfast",
        "sawProcessing": saw_processing,
        "terminalStatus": "failed",
        "boundedFailure": True,
        "controlTracked": True,
        "functionCallIdPresent": str(call.object_id).startswith("fc-"),
        "resultPartitionCleared": True,
        "controlPartitionCleared": True,
        "resultTtlSeconds": bridge.ASYNC_RESULT_TTL_SECONDS,
        "audioRead": False,
        "modelExecuted": False,
        "separatorModelExecuted": False,
        "referenceFacingInputs": 0,
        "referenceScoreCalls": 0,
        "qualityVerdictMade": False,
    }
