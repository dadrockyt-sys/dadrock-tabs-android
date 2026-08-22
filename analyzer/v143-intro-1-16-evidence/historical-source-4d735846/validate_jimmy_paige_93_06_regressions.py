from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import modal

from run_jimmy_paige_em_riff_extraction_training_loop import _score as score_nine_slots
from run_jimmy_paige_full_song_deployed_winner_test import _build_audio_only_wav
from run_jimmy_paige_low_register_recovery_training_loop import (
    CALIBRATION_PATH,
    REFERENCE_PATH,
    REPO_ROOT,
    _load_json,
    _measure_bounds,
    _score as score_professional,
    _targets,
)

APP_NAME = "dadrock-jimmy-paige-professional-worker"
FUNCTION_NAME = "extract_parameterized"

OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-regression-validation.json"
CHECKPOINT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-protected-checkpoint.json"
EVENT_CACHE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json"
LOG_PATH = REPO_ROOT / "jimmy-paige-93-06-regression-validation-heartbeat.log"

WINNING_PARAMETERS: dict[str, Any] = {
    "name": "professional-93-06-winner",
    "minimum_frequency": 82.0,
    "maximum_frequency": 1400.0,
    "onset_threshold": 0.28,
    "frame_threshold": 0.12,
    "minimum_note_length": 35.0,
    "multiple_pitch_bends": True,
}

PROTECTED_MINIMUMS = {
    "professionalOverallRecallPercentage": 93.06,
    "professionalLowRegisterRecallPercentage": 84.38,
    "midi52Matches": 32,
    "midi62Matches": 16,
    "nineSlotCorrectMinimum": 8,
}


def _log(message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} | {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _cancel(call: Any) -> None:
    try:
        call.cancel(terminate_containers=False)
        _log(f"Cancelled Modal call | callId={call.object_id}")
    except Exception as error:
        _log(f"Cancellation unavailable | callId={call.object_id} | error={error!r}")


def main() -> None:
    heartbeat = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    worker_start_timeout = max(60, int(os.getenv("JIMMY_WORKER_START_TIMEOUT_SECONDS", "180")))
    total_timeout = max(worker_start_timeout, int(os.getenv("JIMMY_TOTAL_TIMEOUT_SECONDS", "1200")))
    retries = max(1, int(os.getenv("JIMMY_MAX_RETRIES", "3")))

    LOG_PATH.write_text("", encoding="utf-8")
    reference = _load_json(REFERENCE_PATH)
    calibration = _load_json(CALIBRATION_PATH)
    targets = _targets(reference)
    bounds = _measure_bounds(calibration)
    audio_bytes = _build_audio_only_wav()

    report: dict[str, Any] = {
        "benchmarkVersion": 1,
        "benchmarkType": "jimmy-paige-93-06-combined-regression-validation",
        "status": "running",
        "modalApp": APP_NAME,
        "modalFunction": FUNCTION_NAME,
        "parameters": WINNING_PARAMETERS,
        "protectedMinimums": PROTECTED_MINIMUMS,
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "syntheticNotesAllowed": False,
        "readOnlySourceEvents": True,
    }
    _write(CHECKPOINT_PATH, report)
    started = time.time()

    completed_result: dict[str, Any] | None = None
    retry_reports: list[dict[str, Any]] = []

    for retry in range(1, retries + 1):
        function = modal.Function.from_name(APP_NAME, FUNCTION_NAME)
        call = function.spawn(audio_bytes, WINNING_PARAMETERS)
        submitted = time.time()
        _log(f"93.06 regression call submitted | retry={retry}/{retries} | callId={call.object_id}")

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
                retry_reports.append({"retry": retry, "status": "worker-start-timeout", "elapsedSeconds": round(elapsed, 3), "callId": call.object_id})
                _cancel(call)
                break

            if elapsed >= total_timeout:
                retry_reports.append({"retry": retry, "status": "total-timeout", "elapsedSeconds": round(elapsed, 3), "callId": call.object_id})
                _cancel(call)
                break

            try:
                result_bytes = call.get(timeout=0)
                completed_result = json.loads(result_bytes.decode("utf-8"))
                retry_reports.append({"retry": retry, "status": "complete", "elapsedSeconds": round(elapsed, 3), "callId": call.object_id})
                break
            except TimeoutError:
                phase = "prediction" if task_id else "worker-start"
                _log(f"[{phase} heartbeat] retry={retry}/{retries} | elapsed={elapsed:.1f}s | taskId={task_id or '-'} | callId={call.object_id}")
                time.sleep(heartbeat)
            except Exception as error:
                retry_reports.append({"retry": retry, "status": "failed", "elapsedSeconds": round(elapsed, 3), "callId": call.object_id, "error": repr(error)})
                _log(f"Regression call failed | retry={retry}/{retries} | error={error!r}")
                break

        if completed_result is not None:
            break

    if completed_result is None:
        report.update({
            "status": "failed-after-retries",
            "retries": retry_reports,
            "totalElapsedSeconds": round(time.time() - started, 3),
            "readyForProductionPromotion": False,
        })
        _write(CHECKPOINT_PATH, report)
        _write(OUTPUT_PATH, report)
        _log("93.06 regression validation failed to obtain worker result")
        return

    events = completed_result.get("events", [])
    EVENT_CACHE_PATH.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")

    professional = score_professional(events, targets, bounds)
    nine_slot = score_nine_slots(events)

    matched = {str(key): int(value) for key, value in professional.get("matchedByPitch", {}).items()}
    midi_52 = matched.get("52", 0)
    midi_62 = matched.get("62", 0)
    nine_correct = int(nine_slot.get("correctCandidateSlots", 0))

    professional_pass = bool(
        professional["overallRecallPercentage"] >= PROTECTED_MINIMUMS["professionalOverallRecallPercentage"]
        and professional["lowRegisterRecallPercentage"] >= PROTECTED_MINIMUMS["professionalLowRegisterRecallPercentage"]
        and midi_52 >= PROTECTED_MINIMUMS["midi52Matches"]
        and midi_62 >= PROTECTED_MINIMUMS["midi62Matches"]
        and professional["protectedPitchGuardPassed"]
    )
    nine_slot_pass = nine_correct >= PROTECTED_MINIMUMS["nineSlotCorrectMinimum"]
    combined_pass = professional_pass and nine_slot_pass

    report.update({
        "status": "complete",
        "retries": retry_reports,
        "remoteElapsedSeconds": completed_result.get("remoteElapsedSeconds"),
        "totalElapsedSeconds": round(time.time() - started, 3),
        "extractedEventCount": len(events),
        "professionalScore": professional,
        "midi52Matches": midi_52,
        "midi62Matches": midi_62,
        "professionalCheckpointPassed": professional_pass,
        "nineSlotScore": nine_slot,
        "nineSlotCorrect": nine_correct,
        "nineSlotRegressionPassed": nine_slot_pass,
        "combinedRegressionPassed": combined_pass,
        "readyForProductionPromotion": combined_pass,
        "productionPromotionAllowed": combined_pass,
        "eventCache": str(EVENT_CACHE_PATH.relative_to(REPO_ROOT)),
    })
    _write(CHECKPOINT_PATH, report)
    _write(OUTPUT_PATH, report)

    _log(
        "93.06 regression validation complete | "
        f"professional={professional['overallRecallPercentage']}% | "
        f"low={professional['lowRegisterRecallPercentage']}% | "
        f"MIDI52={midi_52}/32 | MIDI62={midi_62}/16 | "
        f"nineSlots={nine_correct}/9 | combinedPass={combined_pass}"
    )
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
