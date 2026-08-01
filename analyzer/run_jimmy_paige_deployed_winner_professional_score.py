from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import modal

from run_jimmy_paige_full_song_deployed_winner_test import (
    APP_NAME,
    FUNCTION_NAME,
    _build_audio_only_wav,
)
from run_jimmy_paige_low_register_recovery_training_loop import (
    CALIBRATION_PATH,
    REFERENCE_PATH,
    REPO_ROOT,
    _load_json,
    _measure_bounds,
    _score,
    _targets,
)

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-deployed-winner-professional-score.json"
)
CHECKPOINT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-deployed-winner-professional-score-checkpoint.json"
)
EVENT_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-deployed-winner-professional-events.json"
)
LOG_PATH = REPO_ROOT / "jimmy-paige-deployed-winner-professional-score-heartbeat.log"

PROVEN_PARAMETERS = {
    "onset_threshold": 0.35,
    "frame_threshold": 0.20,
    "minimum_note_length": 75.0,
    "minimum_frequency": 100.0,
    "maximum_frequency": 1400.0,
}


def _log(message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} | {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _write_checkpoint(report: dict[str, Any]) -> None:
    CHECKPOINT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )


def _cancel(call: Any) -> None:
    try:
        call.cancel(terminate_containers=False)
        _log(f"Cancelled deployed Modal call | callId={call.object_id}")
    except Exception as error:
        _log(
            "Could not cancel deployed Modal call; Modal timeout will clean it up | "
            f"callId={call.object_id} | error={error!r}"
        )


def main() -> None:
    heartbeat = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    worker_start_timeout = max(
        60,
        int(os.getenv("JIMMY_WORKER_START_TIMEOUT_SECONDS", "180")),
    )
    total_timeout = max(
        worker_start_timeout,
        int(os.getenv("JIMMY_TOTAL_TIMEOUT_SECONDS", "1200")),
    )
    retries = max(1, int(os.getenv("JIMMY_MAX_RETRIES", "3")))

    LOG_PATH.write_text("", encoding="utf-8")
    reference = _load_json(REFERENCE_PATH)
    calibration = _load_json(CALIBRATION_PATH)
    targets = _targets(reference)
    bounds = _measure_bounds(calibration)
    audio_bytes = _build_audio_only_wav()

    report: dict[str, Any] = {
        "benchmarkVersion": 1,
        "benchmarkType": "deployed-winner-professional-measures-1-16-score",
        "modalApp": APP_NAME,
        "modalFunction": FUNCTION_NAME,
        "recordedProvenParameters": PROVEN_PARAMETERS,
        "professionalReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "targetMeasures": [1, 16],
        "status": "starting",
        "retriesRequested": retries,
        "retryReports": [],
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "professionalPdfRemainsScoringAuthority": True,
    }
    _write_checkpoint(report)
    started = time.time()

    _log(
        "Starting deployed winner professional score | "
        f"app={APP_NAME} | function={FUNCTION_NAME} | "
        f"payload={len(audio_bytes) / 1024 / 1024:.2f} MiB"
    )

    for retry in range(1, retries + 1):
        function = modal.Function.from_name(APP_NAME, FUNCTION_NAME)
        call = function.spawn(audio_bytes)
        submitted = time.time()
        retry_report: dict[str, Any] = {
            "retry": retry,
            "callId": call.object_id,
            "status": "submitted",
        }
        report["status"] = "submitted"
        report["activeRetry"] = retry
        report["activeCallId"] = call.object_id
        _write_checkpoint(report)
        _log(
            f"Deployed winner call submitted | retry={retry}/{retries} | "
            f"callId={call.object_id}"
        )

        while True:
            elapsed = time.time() - submitted
            task_id = ""
            try:
                for item in call.get_call_graph():
                    task_id = str(getattr(item, "task_id", "") or "")
                    if task_id:
                        break
            except Exception:
                task_id = ""

            if not task_id and elapsed >= worker_start_timeout:
                retry_report.update(
                    {
                        "status": "worker-start-timeout",
                        "elapsedSeconds": round(elapsed, 3),
                    }
                )
                _log(
                    f"Worker-start timeout | retry={retry}/{retries} | "
                    f"elapsed={elapsed:.1f}s | callId={call.object_id}"
                )
                _cancel(call)
                break

            if elapsed >= total_timeout:
                retry_report.update(
                    {
                        "status": "total-timeout",
                        "elapsedSeconds": round(elapsed, 3),
                    }
                )
                _log(
                    f"Total call timeout | retry={retry}/{retries} | "
                    f"elapsed={elapsed:.1f}s | taskId={task_id or '-'} | "
                    f"callId={call.object_id}"
                )
                _cancel(call)
                break

            try:
                result_bytes = call.get(timeout=0)
                result = json.loads(result_bytes.decode("utf-8"))
                events = result.get("events", [])
                score = _score(events, targets, bounds)

                EVENT_CACHE_PATH.write_text(
                    json.dumps(
                        {
                            "sourceCallId": call.object_id,
                            "modalApp": APP_NAME,
                            "modalFunction": FUNCTION_NAME,
                            "events": events,
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )

                retry_report.update(
                    {
                        "status": "complete",
                        "elapsedSeconds": round(elapsed, 3),
                        "taskId": task_id,
                        "extractedEventCount": len(events),
                    }
                )
                report["retryReports"].append(retry_report)
                report.update(
                    {
                        "status": "complete",
                        "trainingComplete": True,
                        "successfulRetry": retry,
                        "callId": call.object_id,
                        "remoteElapsedSeconds": result.get(
                            "remoteElapsedSeconds"
                        ),
                        "totalElapsedSeconds": round(
                            time.time() - started,
                            3,
                        ),
                        "extractedEventCount": len(events),
                        **score,
                        "eventCache": str(
                            EVENT_CACHE_PATH.relative_to(REPO_ROOT)
                        ),
                        "readyForFrequencyFloorSweep": bool(
                            score["protectedPitchGuardPassed"]
                        ),
                    }
                )
                OUTPUT_PATH.write_text(
                    json.dumps(report, indent=2) + "\n",
                    encoding="utf-8",
                )
                _write_checkpoint(report)
                _log(
                    "Deployed winner professional score complete | "
                    f"events={len(events)} | "
                    f"low={score['lowRegisterRecallPercentage']}% | "
                    f"overall={score['overallRecallPercentage']}% | "
                    f"protected={score['protectedRecallPercentage']}% | "
                    f"guard={score['protectedPitchGuardPassed']} | "
                    f"weighted={score['weightedScore']}"
                )
                _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
                return
            except TimeoutError:
                phase = "prediction" if task_id else "worker-start"
                _log(
                    f"[{phase} heartbeat] retry={retry}/{retries} | "
                    f"elapsed={elapsed:.1f}s | taskId={task_id or '-'} | "
                    f"callId={call.object_id}"
                )
                time.sleep(heartbeat)
            except Exception as error:
                retry_report.update(
                    {
                        "status": "failed",
                        "elapsedSeconds": round(elapsed, 3),
                        "error": repr(error),
                    }
                )
                _log(
                    f"Deployed winner call failed | retry={retry}/{retries} | "
                    f"error={error!r}"
                )
                break

        report["retryReports"].append(retry_report)
        _write_checkpoint(report)

    report.update(
        {
            "status": "stopped-no-result",
            "trainingComplete": False,
            "totalElapsedSeconds": round(time.time() - started, 3),
            "readyForFrequencyFloorSweep": False,
        }
    )
    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_checkpoint(report)
    _log("No deployed winner result returned after all retries.")
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
