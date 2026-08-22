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
    _score as score_professional,
    _targets,
)
from score_jimmy_paige_phase_aware_double_stops import (
    _candidate_events,
    _pairs,
)

APP_NAME = "dadrock-jimmy-paige-professional-worker"
FUNCTION_NAME = "extract_parameterized"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-recovery-extraction-sweep.json"
CHECKPOINT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-recovery-extraction-checkpoint.json"
LOG_PATH = REPO_ROOT / "jimmy-paige-chord-recovery-extraction-heartbeat.log"

PHASE_START = 0.70
PHASE_END = 1.00
PAIR_WINDOW_SECONDS = 0.450
CONTEXT_BEFORE_SECONDS = 0.75
CONTEXT_AFTER_SECONDS = 0.35

PROTECTED_OVERALL = 93.06
PROTECTED_LOW = 84.38
PROTECTED_MIDI52 = 32
PROTECTED_MIDI62 = 16

ATTEMPTS: list[dict[str, Any]] = [
    {
        "name": "protected-93-06-baseline",
        "minimum_frequency": 82.0,
        "maximum_frequency": 1400.0,
        "onset_threshold": 0.28,
        "frame_threshold": 0.12,
        "minimum_note_length": 35.0,
        "multiple_pitch_bends": True,
    },
    {
        "name": "chord-frame-010",
        "minimum_frequency": 82.0,
        "maximum_frequency": 1400.0,
        "onset_threshold": 0.28,
        "frame_threshold": 0.10,
        "minimum_note_length": 35.0,
        "multiple_pitch_bends": True,
    },
    {
        "name": "chord-frame-008",
        "minimum_frequency": 82.0,
        "maximum_frequency": 1400.0,
        "onset_threshold": 0.28,
        "frame_threshold": 0.08,
        "minimum_note_length": 35.0,
        "multiple_pitch_bends": True,
    },
    {
        "name": "chord-sensitive-026-010-25",
        "minimum_frequency": 82.0,
        "maximum_frequency": 1400.0,
        "onset_threshold": 0.26,
        "frame_threshold": 0.10,
        "minimum_note_length": 25.0,
        "multiple_pitch_bends": True,
    },
    {
        "name": "chord-sensitive-024-008-25",
        "minimum_frequency": 82.0,
        "maximum_frequency": 1400.0,
        "onset_threshold": 0.24,
        "frame_threshold": 0.08,
        "minimum_note_length": 25.0,
        "multiple_pitch_bends": True,
    },
]


def _start(event: dict[str, Any]) -> float:
    return float(event.get("start", event.get("start_time", 0.0)))


def _log(message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} | {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _write(payload: dict[str, Any]) -> None:
    CHECKPOINT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _cancel(call: Any) -> None:
    try:
        call.cancel(terminate_containers=False)
    except Exception:
        pass


def _best_phase_pair(
    events: list[dict[str, Any]],
    measure: int,
    bounds: dict[int, tuple[float, float]],
) -> dict[str, Any] | None:
    candidates = _candidate_events(events, measure, bounds)
    qualifying = [
        pair
        for pair in _pairs(candidates, measure, bounds)
        if PHASE_START <= pair["pairCenterPhase"] <= PHASE_END
        and (
            pair["onsetSeparationSeconds"] <= PAIR_WINDOW_SECONDS
            or pair["sustainOverlapSeconds"] > 0.0
        )
    ]
    qualifying.sort(
        key=lambda pair: (
            pair["onsetSeparationSeconds"],
            -pair["sustainOverlapSeconds"],
            abs(pair["pairCenterPhase"] - 0.875),
        )
    )
    return qualifying[0] if qualifying else None


def _context_accepts(events: list[dict[str, Any]], pair: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    center = float(pair["pairCenterSeconds"])
    before = [event for event in events if center - CONTEXT_BEFORE_SECONDS <= _start(event) < center]
    after = [event for event in events if center < _start(event) <= center + CONTEXT_AFTER_SECONDS]
    before_pitches = [int(event.get("midiPitch", -999)) for event in before]

    targets_before = sum(1 for pitch in before_pitches if pitch in {58, 62})
    low_before = sum(1 for pitch in before_pitches if 40 <= pitch <= 57)
    before_density = len(before) / CONTEXT_BEFORE_SECONDS
    after_density = len(after) / CONTEXT_AFTER_SECONDS

    accepted = bool(
        targets_before >= 2
        and after_density >= 0.0
        and before_density <= 100.0
        and low_before < 35
    )
    return accepted, {
        "targetsBefore": targets_before,
        "lowBefore": low_before,
        "beforeDensity": round(before_density, 3),
        "afterDensity": round(after_density, 3),
    }


def _score_chords(
    events: list[dict[str, Any]],
    bounds: dict[int, tuple[float, float]],
) -> dict[str, Any]:
    reports: list[dict[str, Any]] = []
    tp = fp = fn = tn = 0

    for measure in range(1, 17):
        pair = _best_phase_pair(events, measure, bounds)
        context = None
        predicted = False
        if pair is not None:
            predicted, context = _context_accepts(events, pair)

        expected = measure % 2 == 0
        if expected and predicted:
            tp += 1
        elif expected and not predicted:
            fn += 1
        elif not expected and predicted:
            fp += 1
        else:
            tn += 1

        reports.append({
            "measureNumber": measure,
            "expectedDoubleStopEnding": expected,
            "predictedDoubleStopEnding": predicted,
            "bestPhasePair": pair,
            "contextFeatures": context,
        })

    precision = 100.0 * tp / (tp + fp) if tp + fp else 0.0
    recall = 100.0 * tp / (tp + fn) if tp + fn else 0.0
    f1 = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "truePositive": tp,
        "falsePositive": fp,
        "falseNegative": fn,
        "trueNegative": tn,
        "precisionPercentage": round(precision, 2),
        "recallPercentage": round(recall, 2),
        "f1Percentage": round(f1, 2),
        "acceptedMeasures": [row["measureNumber"] for row in reports if row["predictedDoubleStopEnding"]],
        "missedProfessionalMeasures": [row["measureNumber"] for row in reports if row["expectedDoubleStopEnding"] and not row["predictedDoubleStopEnding"]],
        "falsePositiveMeasures": [row["measureNumber"] for row in reports if not row["expectedDoubleStopEnding"] and row["predictedDoubleStopEnding"]],
        "measureReports": reports,
    }


def main() -> None:
    heartbeat = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    retries = max(1, int(os.getenv("JIMMY_MAX_RETRIES", "3")))
    worker_start_timeout = max(60, int(os.getenv("JIMMY_WORKER_START_TIMEOUT_SECONDS", "180")))
    total_timeout = max(worker_start_timeout, int(os.getenv("JIMMY_TOTAL_TIMEOUT_SECONDS", "1200")))
    max_attempts = max(1, min(len(ATTEMPTS), int(os.getenv("JIMMY_MAX_ATTEMPTS", str(len(ATTEMPTS))))))

    LOG_PATH.write_text("", encoding="utf-8")
    reference = _load_json(REFERENCE_PATH)
    calibration = _load_json(CALIBRATION_PATH)
    targets = _targets(reference)
    bounds = _measure_bounds(calibration)
    audio_bytes = _build_audio_only_wav()

    report: dict[str, Any] = {
        "benchmarkVersion": 1,
        "benchmarkType": "protected-end-to-end-rhythm-chord-recovery-sweep",
        "attemptsRequested": max_attempts,
        "attemptsCompleted": 0,
        "attempts": [],
        "bestAttempt": None,
        "protectedPitchMinimums": {
            "overallRecallPercentage": PROTECTED_OVERALL,
            "lowRegisterRecallPercentage": PROTECTED_LOW,
            "midi52Matches": PROTECTED_MIDI52,
            "midi62Matches": PROTECTED_MIDI62,
        },
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
    }
    _write(report)

    for index, parameters in enumerate(ATTEMPTS[:max_attempts], start=1):
        completed: dict[str, Any] | None = None
        retry_rows: list[dict[str, Any]] = []

        for retry in range(1, retries + 1):
            function = modal.Function.from_name(APP_NAME, FUNCTION_NAME)
            call = function.spawn(audio_bytes, parameters)
            submitted = time.time()
            _log(f"Attempt {index}/{max_attempts} submitted | name={parameters['name']} | retry={retry}/{retries} | callId={call.object_id}")

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
                    retry_rows.append({"retry": retry, "status": "worker-start-timeout", "elapsedSeconds": round(elapsed, 3)})
                    _cancel(call)
                    break
                if elapsed >= total_timeout:
                    retry_rows.append({"retry": retry, "status": "total-timeout", "elapsedSeconds": round(elapsed, 3)})
                    _cancel(call)
                    break

                try:
                    completed = json.loads(call.get(timeout=0).decode("utf-8"))
                    retry_rows.append({"retry": retry, "status": "complete", "elapsedSeconds": round(elapsed, 3)})
                    break
                except TimeoutError:
                    phase = "prediction" if task_id else "worker-start"
                    _log(f"[{phase} heartbeat] attempt={index}/{max_attempts} | name={parameters['name']} | retry={retry}/{retries} | elapsed={elapsed:.1f}s | taskId={task_id or '-'}")
                    time.sleep(heartbeat)
                except Exception as error:
                    retry_rows.append({"retry": retry, "status": "failed", "error": repr(error)})
                    break

            if completed is not None:
                break

        if completed is None:
            report["attempts"].append({"attemptNumber": index, "name": parameters["name"], "status": "failed", "retries": retry_rows})
            _write(report)
            continue

        events = completed.get("events", [])
        professional = score_professional(events, targets, bounds)
        matched = {str(key): int(value) for key, value in professional.get("matchedByPitch", {}).items()}
        midi52 = matched.get("52", 0)
        midi62 = matched.get("62", 0)
        pitch_guard = bool(
            professional["overallRecallPercentage"] >= PROTECTED_OVERALL
            and professional["lowRegisterRecallPercentage"] >= PROTECTED_LOW
            and midi52 >= PROTECTED_MIDI52
            and midi62 >= PROTECTED_MIDI62
            and professional["protectedPitchGuardPassed"]
        )
        chord = _score_chords(events, bounds)

        row = {
            "attemptNumber": index,
            "name": parameters["name"],
            "parameters": parameters,
            "status": "complete",
            "retries": retry_rows,
            "extractedEventCount": len(events),
            "professionalScore": professional,
            "midi52Matches": midi52,
            "midi62Matches": midi62,
            "protectedPitchCheckpointPassed": pitch_guard,
            "endToEndChordScore": chord,
        }
        report["attempts"].append(row)
        report["attemptsCompleted"] += 1

        best = report.get("bestAttempt")
        if pitch_guard and (
            best is None
            or chord["f1Percentage"] > best["endToEndChordScore"]["f1Percentage"]
            or (
                chord["f1Percentage"] == best["endToEndChordScore"]["f1Percentage"]
                and chord["recallPercentage"] > best["endToEndChordScore"]["recallPercentage"]
            )
        ):
            report["bestAttempt"] = row

        _write(report)
        _log(
            f"Attempt {index}/{max_attempts} complete | name={parameters['name']} | "
            f"professional={professional['overallRecallPercentage']}% | low={professional['lowRegisterRecallPercentage']}% | "
            f"MIDI52={midi52}/32 | MIDI62={midi62}/16 | pitchGuard={pitch_guard} | "
            f"chordTP={chord['truePositive']}/8 | chordFP={chord['falsePositive']}/8 | "
            f"chordRecall={chord['recallPercentage']}% | chordF1={chord['f1Percentage']}%"
        )

    report["trainingComplete"] = True
    report["readyForNextValidationStage"] = report.get("bestAttempt") is not None
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _write(report)

    best = report.get("bestAttempt")
    if best:
        chord = best["endToEndChordScore"]
        _log(
            f"Chord recovery sweep complete | best={best['name']} | "
            f"professional={best['professionalScore']['overallRecallPercentage']}% | "
            f"TP={chord['truePositive']}/8 | FP={chord['falsePositive']}/8 | "
            f"recall={chord['recallPercentage']}% | F1={chord['f1Percentage']}%"
        )
    else:
        _log("Chord recovery sweep complete | no candidate preserved the protected 93.06% pitch checkpoint")
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
