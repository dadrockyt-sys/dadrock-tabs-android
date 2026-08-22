from __future__ import annotations

import json
import os
import time
from typing import Any

import modal

from run_jimmy_paige_full_song_deployed_winner_test import _build_audio_only_wav
from run_jimmy_paige_low_register_recovery_training_loop import (
    CALIBRATION_PATH,
    REFERENCE_PATH,
    REPO_ROOT,
    _load_json,
    _measure_bounds,
    _score,
    _targets,
)

APP_NAME = "dadrock-jimmy-paige-professional-worker"
FUNCTION_NAME = "extract_parameterized"

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-82hz-sensitivity-sweep.json"
)
CHECKPOINT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-82hz-sensitivity-sweep-checkpoint.json"
)
LOG_PATH = REPO_ROOT / "jimmy-paige-82hz-sensitivity-sweep-heartbeat.log"

ATTEMPTS: list[dict[str, Any]] = [
    {
        "name": "82hz-proven-baseline",
        "onset_threshold": 0.35,
        "frame_threshold": 0.20,
        "minimum_note_length": 75.0,
    },
    {
        "name": "82hz-onset-032",
        "onset_threshold": 0.32,
        "frame_threshold": 0.20,
        "minimum_note_length": 75.0,
    },
    {
        "name": "82hz-onset-030",
        "onset_threshold": 0.30,
        "frame_threshold": 0.20,
        "minimum_note_length": 75.0,
    },
    {
        "name": "82hz-frame-018",
        "onset_threshold": 0.35,
        "frame_threshold": 0.18,
        "minimum_note_length": 75.0,
    },
    {
        "name": "82hz-frame-015",
        "onset_threshold": 0.35,
        "frame_threshold": 0.15,
        "minimum_note_length": 75.0,
    },
    {
        "name": "82hz-length-60",
        "onset_threshold": 0.35,
        "frame_threshold": 0.20,
        "minimum_note_length": 60.0,
    },
    {
        "name": "82hz-length-45",
        "onset_threshold": 0.35,
        "frame_threshold": 0.20,
        "minimum_note_length": 45.0,
    },
    {
        "name": "82hz-balanced-sensitive",
        "onset_threshold": 0.32,
        "frame_threshold": 0.18,
        "minimum_note_length": 60.0,
    },
    {
        "name": "82hz-most-sensitive",
        "onset_threshold": 0.30,
        "frame_threshold": 0.15,
        "minimum_note_length": 45.0,
    },
]


def _log(message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} | {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _write(report: dict[str, Any]) -> None:
    CHECKPOINT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )


def _cancel(call: Any) -> None:
    try:
        call.cancel(terminate_containers=False)
        _log(f"Cancelled Modal call | callId={call.object_id}")
    except Exception as error:
        _log(
            f"Modal cancellation unavailable | callId={call.object_id} | "
            f"error={error!r}"
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
    max_attempts = max(
        1,
        min(
            len(ATTEMPTS),
            int(os.getenv("JIMMY_MAX_ATTEMPTS", str(len(ATTEMPTS)))),
        ),
    )

    LOG_PATH.write_text("", encoding="utf-8")
    reference = _load_json(REFERENCE_PATH)
    calibration = _load_json(CALIBRATION_PATH)
    targets = _targets(reference)
    bounds = _measure_bounds(calibration)
    audio_bytes = _build_audio_only_wav()

    report: dict[str, Any] = {
        "benchmarkVersion": 1,
        "benchmarkType": "82hz-professional-sensitivity-sweep",
        "modalApp": APP_NAME,
        "modalFunction": FUNCTION_NAME,
        "professionalReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "fixedParameters": {
            "minimum_frequency": 82.0,
            "maximum_frequency": 1400.0,
            "multiple_pitch_bends": False,
        },
        "baselineOverallRecallPercentage": 64.58,
        "baselineLowRegisterRecallPercentage": 39.06,
        "attemptsRequested": max_attempts,
        "attemptsCompleted": 0,
        "attemptsFailed": 0,
        "attempts": [],
        "bestAttempt": None,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "protectedPitches": [52, 62],
    }
    _write(report)
    started = time.time()

    for index, candidate in enumerate(ATTEMPTS[:max_attempts], start=1):
        parameters = {
            **candidate,
            "minimum_frequency": 82.0,
            "maximum_frequency": 1400.0,
            "multiple_pitch_bends": False,
        }
        completed_result: dict[str, Any] | None = None
        retry_reports: list[dict[str, Any]] = []

        for retry in range(1, retries + 1):
            function = modal.Function.from_name(APP_NAME, FUNCTION_NAME)
            call = function.spawn(audio_bytes, parameters)
            submitted = time.time()
            _log(
                f"Attempt {index}/{max_attempts} submitted | "
                f"name={parameters['name']} | retry={retry}/{retries} | "
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
                    retry_reports.append(
                        {
                            "retry": retry,
                            "status": "worker-start-timeout",
                            "elapsedSeconds": round(elapsed, 3),
                            "callId": call.object_id,
                        }
                    )
                    _log(
                        f"Worker-start timeout | attempt={index}/{max_attempts} | "
                        f"retry={retry}/{retries}"
                    )
                    _cancel(call)
                    break

                if elapsed >= total_timeout:
                    retry_reports.append(
                        {
                            "retry": retry,
                            "status": "total-timeout",
                            "elapsedSeconds": round(elapsed, 3),
                            "callId": call.object_id,
                        }
                    )
                    _log(
                        f"Total timeout | attempt={index}/{max_attempts} | "
                        f"retry={retry}/{retries}"
                    )
                    _cancel(call)
                    break

                try:
                    result_bytes = call.get(timeout=0)
                    completed_result = json.loads(result_bytes.decode("utf-8"))
                    retry_reports.append(
                        {
                            "retry": retry,
                            "status": "complete",
                            "elapsedSeconds": round(elapsed, 3),
                            "callId": call.object_id,
                        }
                    )
                    break
                except TimeoutError:
                    phase = "prediction" if task_id else "worker-start"
                    _log(
                        f"[{phase} heartbeat] attempt={index}/{max_attempts} | "
                        f"name={parameters['name']} | retry={retry}/{retries} | "
                        f"elapsed={elapsed:.1f}s | taskId={task_id or '-'} | "
                        f"callId={call.object_id}"
                    )
                    time.sleep(heartbeat)
                except Exception as error:
                    retry_reports.append(
                        {
                            "retry": retry,
                            "status": "failed",
                            "elapsedSeconds": round(elapsed, 3),
                            "callId": call.object_id,
                            "error": repr(error),
                        }
                    )
                    _log(
                        f"Attempt failed | attempt={index}/{max_attempts} | "
                        f"retry={retry}/{retries} | error={error!r}"
                    )
                    break

            if completed_result is not None:
                break

        if completed_result is None:
            report["attempts"].append(
                {
                    "attemptNumber": index,
                    "name": parameters["name"],
                    "parameters": parameters,
                    "status": "failed-after-retries",
                    "retries": retry_reports,
                }
            )
            report["attemptsFailed"] += 1
            _write(report)
            continue

        events = completed_result.get("events", [])
        score = _score(events, targets, bounds)
        matched = {
            str(key): int(value)
            for key, value in score.get("matchedByPitch", {}).items()
        }
        midi_52 = matched.get("52", 0)
        midi_62 = matched.get("62", 0)

        attempt_report = {
            "attemptNumber": index,
            "name": parameters["name"],
            "parameters": parameters,
            "status": "complete",
            "retries": retry_reports,
            "extractedEventCount": len(events),
            "remoteElapsedSeconds": completed_result.get(
                "remoteElapsedSeconds"
            ),
            "midi52Matches": midi_52,
            "midi62Matches": midi_62,
            "beats82HzBaseline": bool(
                score["overallRecallPercentage"] > 64.58
                and score["lowRegisterRecallPercentage"] >= 39.06
            ),
            **score,
        }
        report["attempts"].append(attempt_report)
        report["attemptsCompleted"] += 1

        best = report.get("bestAttempt")
        if score["protectedPitchGuardPassed"] and (
            best is None
            or score["weightedScore"] > best["weightedScore"]
        ):
            report["bestAttempt"] = attempt_report

        _write(report)
        _log(
            f"Attempt {index}/{max_attempts} complete | "
            f"name={parameters['name']} | "
            f"low={score['lowRegisterRecallPercentage']}% | "
            f"overall={score['overallRecallPercentage']}% | "
            f"MIDI52={midi_52}/32 | MIDI62={midi_62}/16 | "
            f"protected={score['protectedRecallPercentage']}% | "
            f"guard={score['protectedPitchGuardPassed']} | "
            f"weighted={score['weightedScore']}"
        )

    report["trainingComplete"] = True
    report["totalElapsedSeconds"] = round(time.time() - started, 3)
    report["readyForNextValidationStage"] = bool(
        report.get("bestAttempt")
        and report["bestAttempt"]["overallRecallPercentage"] > 64.58
        and report["bestAttempt"]["lowRegisterRecallPercentage"] >= 39.06
    )
    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    _write(report)

    best = report.get("bestAttempt")
    if best:
        _log(
            f"Sweep complete | best={best['name']} | "
            f"low={best['lowRegisterRecallPercentage']}% | "
            f"overall={best['overallRecallPercentage']}% | "
            f"MIDI52={best['midi52Matches']}/32 | "
            f"MIDI62={best['midi62Matches']}/16"
        )
    else:
        _log(
            "Sweep complete | no sensitivity configuration restored the "
            "MIDI 52/62 guard"
        )
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
