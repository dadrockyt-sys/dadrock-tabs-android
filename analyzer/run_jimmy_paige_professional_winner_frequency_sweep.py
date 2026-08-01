from __future__ import annotations

import json
import os
import time
from typing import Any

from run_jimmy_paige_low_register_recovery_training_loop import (
    CALIBRATION_PATH,
    CHECKPOINT_PATH,
    LOG_PATH,
    OUTPUT_PATH,
    REFERENCE_PATH,
    REPO_ROOT,
    _build_intro_wav,
    _load_json,
    _log,
    _measure_bounds,
    _score,
    _targets,
    _write_checkpoint,
    app,
    extract_attempt,
)

# Start from the exact parameters recorded by the successful deployed
# full-song winner test, then change only the minimum frequency.
ATTEMPTS: list[dict[str, Any]] = [
    {
        "name": "proven-full-song-winner-100hz",
        "onset_threshold": 0.35,
        "frame_threshold": 0.20,
        "minimum_note_length": 75.0,
        "minimum_frequency": 100.0,
        "maximum_frequency": 1400.0,
        "multiple_pitch_bends": False,
    },
    {
        "name": "winner-frequency-floor-90hz",
        "onset_threshold": 0.35,
        "frame_threshold": 0.20,
        "minimum_note_length": 75.0,
        "minimum_frequency": 90.0,
        "maximum_frequency": 1400.0,
        "multiple_pitch_bends": False,
    },
    {
        "name": "winner-frequency-floor-82hz",
        "onset_threshold": 0.35,
        "frame_threshold": 0.20,
        "minimum_note_length": 75.0,
        "minimum_frequency": 82.0,
        "maximum_frequency": 1400.0,
        "multiple_pitch_bends": False,
    },
    {
        "name": "winner-frequency-floor-80hz",
        "onset_threshold": 0.35,
        "frame_threshold": 0.20,
        "minimum_note_length": 75.0,
        "minimum_frequency": 80.0,
        "maximum_frequency": 1400.0,
        "multiple_pitch_bends": False,
    },
    {
        "name": "winner-frequency-floor-75hz",
        "onset_threshold": 0.35,
        "frame_threshold": 0.20,
        "minimum_note_length": 75.0,
        "minimum_frequency": 75.0,
        "maximum_frequency": 1400.0,
        "multiple_pitch_bends": False,
    },
    {
        "name": "winner-frequency-floor-70hz",
        "onset_threshold": 0.35,
        "frame_threshold": 0.20,
        "minimum_note_length": 75.0,
        "minimum_frequency": 70.0,
        "maximum_frequency": 1400.0,
        "multiple_pitch_bends": False,
    },
]


def _cancel_call(call: Any) -> None:
    try:
        call.cancel(terminate_containers=False)
        _log(f"Cancelled timed-out Modal call | callId={call.object_id}")
    except Exception as error:
        _log(
            "Modal cancellation unavailable; remote timeout will clean it up | "
            f"callId={call.object_id} | error={error!r}"
        )


def main() -> None:
    heartbeat_seconds = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    max_attempts = max(
        1,
        min(len(ATTEMPTS), int(os.getenv("JIMMY_MAX_ATTEMPTS", str(len(ATTEMPTS))))),
    )
    max_retries = max(1, int(os.getenv("JIMMY_MAX_RETRIES", "3")))
    attempt_timeout = max(60, int(os.getenv("JIMMY_ATTEMPT_TIMEOUT_SECONDS", "300")))

    reference = _load_json(REFERENCE_PATH)
    calibration = _load_json(CALIBRATION_PATH)
    targets = _targets(reference)
    bounds = _measure_bounds(calibration)
    audio_bytes = _build_intro_wav()
    LOG_PATH.write_text("", encoding="utf-8")

    report: dict[str, Any] = {
        "benchmarkVersion": 3,
        "benchmarkType": "jimmy-paige-professional-winner-frequency-sweep",
        "professionalReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "comparisonScope": "professional rhythm tab measures 1-16",
        "protectedBaseline": "successful full-song upper_string_recovery parameters",
        "controlledVariable": "minimum_frequency",
        "attemptsRequested": max_attempts,
        "attemptsCompleted": 0,
        "attemptsFailed": 0,
        "attempts": [],
        "bestAttempt": None,
        "trainingComplete": False,
        "maxRetriesPerConfiguration": max_retries,
        "attemptTimeoutSeconds": attempt_timeout,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "readOnlySourceEvents": True,
        "noSyntheticNotes": True,
    }
    _write_checkpoint(report)
    started = time.time()

    _log(
        "Starting professional-scored winner frequency sweep | "
        f"attempts={max_attempts} | retries={max_retries} | timeout={attempt_timeout}s"
    )

    with app.run():
        for index, parameters in enumerate(ATTEMPTS[:max_attempts], start=1):
            completed_result: dict[str, Any] | None = None
            retry_reports: list[dict[str, Any]] = []

            for retry in range(1, max_retries + 1):
                retry_started = time.time()
                call = extract_attempt.spawn(audio_bytes, dict(parameters))
                _log(
                    f"Attempt {index}/{max_attempts} submitted | name={parameters['name']} | "
                    f"frequencyFloor={parameters['minimum_frequency']}Hz | "
                    f"retry={retry}/{max_retries} | callId={call.object_id}"
                )

                timed_out = False
                failure: str | None = None
                while True:
                    elapsed = time.time() - retry_started
                    if elapsed >= attempt_timeout:
                        timed_out = True
                        _log(
                            f"Attempt {index}/{max_attempts} timed out | name={parameters['name']} | "
                            f"retry={retry}/{max_retries} | elapsed={elapsed:.1f}s"
                        )
                        _cancel_call(call)
                        break

                    try:
                        result_bytes = call.get(timeout=0)
                        completed_result = json.loads(result_bytes.decode("utf-8"))
                        break
                    except TimeoutError:
                        _log(
                            f"[winner-frequency heartbeat] attempt={index}/{max_attempts} | "
                            f"name={parameters['name']} | retry={retry}/{max_retries} | "
                            f"elapsed={elapsed:.1f}s | callId={call.object_id}"
                        )
                        time.sleep(heartbeat_seconds)
                    except Exception as error:
                        failure = repr(error)
                        _log(
                            f"Attempt failed | attempt={index}/{max_attempts} | "
                            f"retry={retry}/{max_retries} | error={failure}"
                        )
                        break

                retry_reports.append(
                    {
                        "retry": retry,
                        "callId": call.object_id,
                        "elapsedSeconds": round(time.time() - retry_started, 3),
                        "timedOut": timed_out,
                        "completed": completed_result is not None,
                        "error": failure,
                    }
                )
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
                _write_checkpoint(report)
                continue

            events = completed_result.get("events", [])
            score = _score(events, targets, bounds)
            attempt_report = {
                "attemptNumber": index,
                "name": parameters["name"],
                "parameters": parameters,
                "status": "complete",
                "retries": retry_reports,
                "remoteElapsedSeconds": completed_result.get("remoteElapsedSeconds"),
                "extractedEventCount": len(events),
                **score,
            }
            report["attempts"].append(attempt_report)
            report["attemptsCompleted"] += 1

            best = report.get("bestAttempt")
            if attempt_report["protectedPitchGuardPassed"] and (
                best is None or attempt_report["weightedScore"] > best["weightedScore"]
            ):
                report["bestAttempt"] = attempt_report

            _write_checkpoint(report)
            _log(
                f"Attempt {index}/{max_attempts} complete | floor={parameters['minimum_frequency']}Hz | "
                f"low={attempt_report['lowRegisterRecallPercentage']}% | "
                f"overall={attempt_report['overallRecallPercentage']}% | "
                f"protected={attempt_report['protectedRecallPercentage']}% | "
                f"guard={attempt_report['protectedPitchGuardPassed']} | "
                f"weighted={attempt_report['weightedScore']}"
            )

    report["trainingComplete"] = True
    report["totalElapsedSeconds"] = round(time.time() - started, 3)
    best = report.get("bestAttempt")
    report["readyForNextValidationStage"] = bool(
        best and best["lowRegisterRecallPercentage"] >= 50.0
    )
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _write_checkpoint(report)

    if best:
        _log(
            f"Frequency sweep complete | best={best['name']} | "
            f"floor={best['parameters']['minimum_frequency']}Hz | "
            f"low={best['lowRegisterRecallPercentage']}% | "
            f"overall={best['overallRecallPercentage']}% | "
            f"protected={best['protectedRecallPercentage']}%"
        )
    else:
        _log("Frequency sweep complete | no configuration passed the MIDI 52/62 guard")
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
