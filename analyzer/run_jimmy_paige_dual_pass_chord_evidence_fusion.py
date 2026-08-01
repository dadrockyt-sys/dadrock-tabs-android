from __future__ import annotations

import json
import os
import time
from typing import Any

import modal

from run_jimmy_paige_chord_recovery_extraction_sweep import (
    APP_NAME,
    FUNCTION_NAME,
    ATTEMPTS,
    PROTECTED_LOW,
    PROTECTED_MIDI52,
    PROTECTED_MIDI62,
    PROTECTED_OVERALL,
    _cancel,
    _score_chords,
)
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

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-dual-pass-chord-evidence-fusion.json"
)
CHECKPOINT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-dual-pass-chord-evidence-fusion-checkpoint.json"
)
LOG_PATH = REPO_ROOT / "jimmy-paige-dual-pass-chord-evidence-fusion-heartbeat.log"


def _log(message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} | {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _write(payload: dict[str, Any]) -> None:
    CHECKPOINT_PATH.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def _extract(
    audio_bytes: bytes,
    parameters: dict[str, Any],
    heartbeat: int,
    retries: int,
    worker_start_timeout: int,
    total_timeout: int,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    retry_rows: list[dict[str, Any]] = []

    for retry in range(1, retries + 1):
        function = modal.Function.from_name(APP_NAME, FUNCTION_NAME)
        call = function.spawn(audio_bytes, parameters)
        submitted = time.time()
        _log(
            f"Extraction submitted | name={parameters['name']} | "
            f"retry={retry}/{retries} | callId={call.object_id}"
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
                retry_rows.append(
                    {
                        "retry": retry,
                        "status": "worker-start-timeout",
                        "elapsedSeconds": round(elapsed, 3),
                    }
                )
                _cancel(call)
                break

            if elapsed >= total_timeout:
                retry_rows.append(
                    {
                        "retry": retry,
                        "status": "total-timeout",
                        "elapsedSeconds": round(elapsed, 3),
                    }
                )
                _cancel(call)
                break

            try:
                result = json.loads(call.get(timeout=0).decode("utf-8"))
                retry_rows.append(
                    {
                        "retry": retry,
                        "status": "complete",
                        "elapsedSeconds": round(elapsed, 3),
                    }
                )
                return result, retry_rows
            except TimeoutError:
                phase = "prediction" if task_id else "worker-start"
                _log(
                    f"[{phase} heartbeat] name={parameters['name']} | "
                    f"retry={retry}/{retries} | elapsed={elapsed:.1f}s | "
                    f"taskId={task_id or '-'}"
                )
                time.sleep(heartbeat)
            except Exception as error:
                retry_rows.append(
                    {
                        "retry": retry,
                        "status": "failed",
                        "error": repr(error),
                    }
                )
                break

    return None, retry_rows


def _pitch_guard(
    events: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    bounds: dict[int, tuple[float, float]],
) -> tuple[dict[str, Any], int, int, bool]:
    professional = score_professional(events, targets, bounds)
    matched = {
        str(key): int(value)
        for key, value in professional.get("matchedByPitch", {}).items()
    }
    midi52 = matched.get("52", 0)
    midi62 = matched.get("62", 0)
    guard = bool(
        professional["overallRecallPercentage"] >= PROTECTED_OVERALL
        and professional["lowRegisterRecallPercentage"] >= PROTECTED_LOW
        and midi52 >= PROTECTED_MIDI52
        and midi62 >= PROTECTED_MIDI62
        and professional["protectedPitchGuardPassed"]
    )
    return professional, midi52, midi62, guard


def _fusion_score(
    primary: dict[str, Any],
    secondary: dict[str, Any],
) -> dict[str, Any]:
    primary_predicted = set(primary["acceptedMeasures"])
    secondary_predicted = set(secondary["acceptedMeasures"])
    fused = primary_predicted | secondary_predicted

    expected = {2, 4, 6, 8, 10, 12, 14, 16}
    negatives = {1, 3, 5, 7, 9, 11, 13, 15}

    tp_measures = sorted(fused & expected)
    fp_measures = sorted(fused & negatives)
    fn_measures = sorted(expected - fused)
    tn_measures = sorted(negatives - fused)

    tp = len(tp_measures)
    fp = len(fp_measures)
    fn = len(fn_measures)
    tn = len(tn_measures)
    precision = 100.0 * tp / (tp + fp) if tp + fp else 0.0
    recall = 100.0 * tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "truePositive": tp,
        "falsePositive": fp,
        "falseNegative": fn,
        "trueNegative": tn,
        "precisionPercentage": round(precision, 2),
        "recallPercentage": round(recall, 2),
        "f1Percentage": round(f1, 2),
        "acceptedMeasures": sorted(fused),
        "truePositiveMeasures": tp_measures,
        "falsePositiveMeasures": fp_measures,
        "missedProfessionalMeasures": fn_measures,
        "trueNegativeMeasures": tn_measures,
        "recoveredBySecondaryPass": sorted(
            (secondary_predicted - primary_predicted) & expected
        ),
        "newFalsePositivesFromSecondaryPass": sorted(
            (secondary_predicted - primary_predicted) & negatives
        ),
    }


def main() -> None:
    heartbeat = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    retries = max(1, int(os.getenv("JIMMY_MAX_RETRIES", "3")))
    worker_start_timeout = max(
        60,
        int(os.getenv("JIMMY_WORKER_START_TIMEOUT_SECONDS", "180")),
    )
    total_timeout = max(
        worker_start_timeout,
        int(os.getenv("JIMMY_TOTAL_TIMEOUT_SECONDS", "1200")),
    )

    LOG_PATH.write_text("", encoding="utf-8")
    reference = _load_json(REFERENCE_PATH)
    calibration = _load_json(CALIBRATION_PATH)
    targets = _targets(reference)
    bounds = _measure_bounds(calibration)
    audio_bytes = _build_audio_only_wav()

    report: dict[str, Any] = {
        "benchmarkVersion": 1,
        "benchmarkType": "protected-dual-pass-chord-evidence-fusion",
        "primaryPass": ATTEMPTS[0]["name"],
        "secondaryPasses": [item["name"] for item in ATTEMPTS[1:]],
        "primaryEventsRemainCanonical": True,
        "secondaryEventsUsedOnlyAsChordEvidence": True,
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
        "attempts": [],
        "bestFusion": None,
    }
    _write(report)

    primary_result, primary_retries = _extract(
        audio_bytes,
        ATTEMPTS[0],
        heartbeat,
        retries,
        worker_start_timeout,
        total_timeout,
    )
    if primary_result is None:
        raise RuntimeError("Unable to obtain protected primary extraction")

    primary_events = primary_result.get("events", [])
    primary_professional, primary_midi52, primary_midi62, primary_guard = (
        _pitch_guard(primary_events, targets, bounds)
    )
    primary_chords = _score_chords(primary_events, bounds)

    report["primaryResult"] = {
        "parameters": ATTEMPTS[0],
        "retries": primary_retries,
        "eventCount": len(primary_events),
        "professionalScore": primary_professional,
        "midi52Matches": primary_midi52,
        "midi62Matches": primary_midi62,
        "protectedPitchCheckpointPassed": primary_guard,
        "chordScore": primary_chords,
    }
    _write(report)

    if not primary_guard:
        raise RuntimeError("Protected primary extraction failed the pitch checkpoint")

    for secondary_parameters in ATTEMPTS[1:]:
        secondary_result, secondary_retries = _extract(
            audio_bytes,
            secondary_parameters,
            heartbeat,
            retries,
            worker_start_timeout,
            total_timeout,
        )
        if secondary_result is None:
            report["attempts"].append(
                {
                    "name": secondary_parameters["name"],
                    "status": "failed",
                    "retries": secondary_retries,
                }
            )
            _write(report)
            continue

        secondary_events = secondary_result.get("events", [])
        secondary_professional, midi52, midi62, pitch_guard = _pitch_guard(
            secondary_events,
            targets,
            bounds,
        )
        secondary_chords = _score_chords(secondary_events, bounds)
        fusion = _fusion_score(primary_chords, secondary_chords)

        row = {
            "name": secondary_parameters["name"],
            "status": "complete",
            "parameters": secondary_parameters,
            "retries": secondary_retries,
            "eventCount": len(secondary_events),
            "professionalScore": secondary_professional,
            "midi52Matches": midi52,
            "midi62Matches": midi62,
            "secondaryPitchCheckpointPassed": pitch_guard,
            "secondaryChordScore": secondary_chords,
            "fusedChordScore": fusion,
        }
        report["attempts"].append(row)

        best = report.get("bestFusion")
        if (
            best is None
            or fusion["f1Percentage"] > best["fusedChordScore"]["f1Percentage"]
            or (
                fusion["f1Percentage"]
                == best["fusedChordScore"]["f1Percentage"]
                and fusion["recallPercentage"]
                > best["fusedChordScore"]["recallPercentage"]
            )
        ):
            report["bestFusion"] = row

        _write(report)
        _log(
            f"Fusion complete | secondary={secondary_parameters['name']} | "
            f"secondaryProfessional={secondary_professional['overallRecallPercentage']}% | "
            f"secondaryPitchGuard={pitch_guard} | "
            f"fusedTP={fusion['truePositive']}/8 | fusedFP={fusion['falsePositive']}/8 | "
            f"fusedRecall={fusion['recallPercentage']}% | fusedF1={fusion['f1Percentage']}% | "
            f"recovered={fusion['recoveredBySecondaryPass']} | "
            f"newFP={fusion['newFalsePositivesFromSecondaryPass']}"
        )

    report["trainingComplete"] = True
    report["readyForNextValidationStage"] = report.get("bestFusion") is not None
    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    _write(report)

    best = report.get("bestFusion")
    if best:
        fusion = best["fusedChordScore"]
        _log(
            f"Dual-pass fusion complete | best={best['name']} | "
            f"TP={fusion['truePositive']}/8 | FP={fusion['falsePositive']}/8 | "
            f"recall={fusion['recallPercentage']}% | F1={fusion['f1Percentage']}% | "
            f"recovered={fusion['recoveredBySecondaryPass']}"
        )
    else:
        _log("Dual-pass fusion complete | no secondary extraction completed")
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
