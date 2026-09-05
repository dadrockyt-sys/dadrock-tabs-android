from __future__ import annotations

import os
import time
from typing import Any

import modal
import v143_modal_http_endpoint as bridge


# This module deliberately attaches only a diagnostic function to the isolated
# bridge app selected through V143_HTTP_APP_NAME / V143_ASYNC_RESULT_QUEUE_NAME.
# The production bridge source itself remains the implementation under test.
app = bridge.app
smoke_image = bridge.http_image.add_local_python_source(
    "v143_modal_http_endpoint"
)


@app.function(
    image=smoke_image,
    timeout=240,
    memory=512,
    secrets=[
        modal.Secret.from_name("dadrock-analyzer-secret")
    ],
)
def async_control_tracking_smoke() -> dict[str, Any]:
    """Prove tracked start/status/terminal/ack with no downloadable audio.

    The syntactically valid loopback HTTPS URL passes async start validation, then
    the unchanged L4 worker fails during requests.get before any bytes can be
    downloaded, normalized, separated, or analyzed. This keeps the proof focused
    on FunctionCall control tracking and terminal-state propagation.
    """
    expected_token = str(
        os.environ.get("ANALYZER_API_TOKEN") or ""
    )
    if not expected_token:
        raise RuntimeError("Analyzer token secret was unavailable.")

    payload = {
        "token": expected_token,
        "blobToken": "diagnostic-no-audio",
        "audioUrl": "https://127.0.0.1:9/no-audio.wav",
        "pathname": "diagnostic-no-audio",
        "song": "diagnostic",
        "artist": "diagnostic",
        "transcriptionType": "rhythm",
    }

    started = time.monotonic()
    start_state = bridge._start_rhythm_job(
        payload,
        expected_token=expected_token,
    )
    job_token = str(start_state.get("jobToken") or "")
    if not job_token or start_state.get("orchestratorTracked") is not True:
        raise RuntimeError("Tracked async start did not return a usable job token.")

    status_payload = {
        "token": expected_token,
        "jobToken": job_token,
        "transcriptionType": "rhythm",
    }

    first_status = bridge._status_rhythm_job(
        status_payload,
        expected_token=expected_token,
    )
    first_status_name = str(first_status.get("status") or "")
    first_orchestrator_running = first_status.get("orchestratorRunning") is True

    terminal: dict[str, Any] | None = None
    deadline = time.monotonic() + 180.0
    while time.monotonic() < deadline:
        current = bridge._status_rhythm_job(
            status_payload,
            expected_token=expected_token,
        )
        if current.get("status") != "processing":
            terminal = current
            break
        time.sleep(1.0)

    if terminal is None:
        raise RuntimeError("Tracked async job did not reach a terminal state.")

    terminal_status = str(terminal.get("status") or "")
    terminal_error_bounded = (
        terminal_status == "failed"
        and isinstance(terminal.get("error"), str)
        and 0 < len(terminal.get("error")) <= 240
    )

    ack_state = bridge._ack_rhythm_job(
        status_payload,
        expected_token=expected_token,
    )

    return {
        "schemaVersion": 1,
        "gate": "v143-async-control-tracking-smoke",
        "appName": bridge.HTTP_APP_NAME,
        "queueName": bridge.ASYNC_RESULT_QUEUE_NAME,
        "startStatus": start_state.get("status"),
        "orchestratorTracked": start_state.get("orchestratorTracked"),
        "firstStatus": first_status_name,
        "firstOrchestratorRunning": first_orchestrator_running,
        "terminalStatus": terminal_status,
        "terminalErrorBounded": terminal_error_bounded,
        "resultCleared": ack_state.get("resultCleared"),
        "controlCleared": ack_state.get("controlCleared"),
        "resultTtlSeconds": start_state.get("expiresInSeconds"),
        "elapsedSeconds": round(time.monotonic() - started, 3),
        "loopbackUrlOnly": True,
        "audioRead": False,
        "audioBytesDownloaded": 0,
        "separatorModelExecuted": False,
        "referenceFacingInputs": 0,
        "referenceScoreCalls": 0,
        "qualityVerdictMade": False,
    }
