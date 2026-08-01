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
    / "gomyway-jimmy-paige-midi62-neighbor-recovery-sweep.json"
)
CHECKPOINT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-midi62-neighbor-recovery-checkpoint.json"
)
LOG_PATH = REPO_ROOT / "jimmy-paige-midi62-neighbor-recovery-heartbeat.log"

PROTECTED_OVERALL = 84.72
PROTECTED_LOW = 70.31
PROTECTED_MIDI_52 = 32
PROTECTED_MIDI_62 = 14

ATTEMPTS: list[dict[str, Any]] = [
    {
        "name": "protected-84-72-baseline",
        "onset_threshold": 0.30,
        "frame_threshold": 0.15,
        "minimum_note_length": 45.0,
        "multiple_pitch_bends": False,
    },
    {
        "name": "bend-aware-baseline",
        "onset_threshold": 0.30,
        "frame_threshold": 0.15,
        "minimum_note_length": 45.0,
        "multiple_pitch_bends": True,
    },
    {
        "name": "bend-aware-onset-028",
        "onset_threshold": 0.28,
        "frame_threshold": 0.15,
        "minimum_note_length": 45.0,
        "multiple_pitch_bends": True,
    },
    {
        "name": "bend-aware-frame-012",
        "onset_threshold": 0.30,
        "frame_threshold": 0.12,
        "minimum_note_length": 45.0,
        "multiple_pitch_bends": True,
    },
    {
        "name": "bend-aware-neighbor-sensitive",
        "onset_threshold": 0.28,
        "frame_threshold": 0.12,
        "minimum_note_length": 35.0,
        "multiple_pitch_bends": True,
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


def _measure_16_neighbor_counts(
    events: list[dict[str, Any]],
    bounds: dict[int, tuple[float, float]],
) -> dict[str, int]:
    start, end = bounds[16]
    counts = {"61": 0, "62": 0, "63": 0}
    for event in events:
        event_start = float(event.get("start", 0.0))
        pitch = int(event.get("midiPitch", -1))
        if start <= event_start < end and pitch in {61, 62, 63}:
            counts[str(pitch)] += 1
    return counts


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
        "benchmarkType": "midi62-neighbor-recovery-sweep",
        "modalApp": APP_NAME,
        "modalFunction": FUNCTION_NAME,
        "professionalReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "fixedParameters": {
            "minimum_frequency": 82.0,
            "maximum_frequency": 1400.0,
        },
        "protectedCheckpoint": {
            "overallRecallPercentage": PROTECTED_OVERALL,
            "lowRegisterRecallPercentage": PROTECTED_LOW,
            "midi52Matches": PROTECTED_MIDI_52,
            "midi62Matches": PROTECTED_MIDI_62,
        },
        "diagnosedMissingMeasures": [16, 16],
        "diagnosedClassification": "neighbor-semitone-detection",
        "attemptsRequested": max_attempts,
        "attemptsCompleted": 0,
        "attemptsFailed": 0,
        "attempts": [],
        "bestAttempt": None,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    _write(report)
    started = time.time()

    for index, candidate in enumerate(ATTEMPTS[:max_attempts], start=1):
        parameters = {
            **candidate,
            "minimum_frequency": 82.0,
            "maximum_frequency": 1400.0,
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
        neighbor_counts = _measure_16_neighbor_counts(events, bounds)

        checkpoint_preserved = bool(
            score["overallRecallPercentage"] >= PROTECTED_OVERALL
            and score["lowRegisterRecallPercentage"] >= PROTECTED_LOW
            and midi_52 == PROTECTED_MIDI_52
            and midi_62 >= PROTECTED_MIDI_62
        )
        full_guard = bool(
            checkpoint_preserved
            and midi_62 == 16
            and score["protectedPitchGuardPassed"]
        )

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
            "measure16NeighborCounts": neighbor_counts,
            "protected84_72CheckpointPreserved": checkpoint_preserved,
            "fullMidi52_62GuardPassed": full_guard,
            **score,
        }
        report["attempts"].append(attempt_report)
        report["attemptsCompleted"] += 1

        best = report.get("bestAttempt")
        if full_guard and (
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
            f"m16-neighbors={neighbor_counts} | "
            f"checkpoint={checkpoint_preserved} | fullGuard={full_guard}"
        )

    report["trainingComplete"] = True
    report["totalElapsedSeconds"] = round(time.time() - started, 3)
    report["readyForNextValidationStage"] = bool(report.get("bestAttempt"))
    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    _write(report)

    best = report.get("bestAttempt")
    if best:
        _log(
            f"MIDI62 recovery complete | best={best['name']} | "
            f"overall={best['overallRecallPercentage']}% | "
            f"low={best['lowRegisterRecallPercentage']}% | "
            f"MIDI52={best['midi52Matches']}/32 | "
            f"MIDI62={best['midi62Matches']}/16"
        )
    else:
        _log(
            "MIDI62 recovery complete | no candidate restored 16/16 while "
            "preserving the protected 84.72% checkpoint"
        )
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
