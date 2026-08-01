from __future__ import annotations

import json
import os
import time
from pathlib import Path
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
    / "gomyway-jimmy-paige-midi62-miss-diagnosis.json"
)
PROTECTED_CHECKPOINT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-professional-best-84-72-checkpoint.json"
)
EVENT_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-82hz-most-sensitive-events.json"
)
LOG_PATH = REPO_ROOT / "jimmy-paige-midi62-diagnosis-heartbeat.log"

BEST_PARAMETERS: dict[str, Any] = {
    "name": "82hz-most-sensitive-protected",
    "onset_threshold": 0.30,
    "frame_threshold": 0.15,
    "minimum_note_length": 45.0,
    "minimum_frequency": 82.0,
    "maximum_frequency": 1400.0,
    "multiple_pitch_bends": False,
}

PROTECTED_BASELINE = {
    "overallRecallPercentage": 84.72,
    "lowRegisterRecallPercentage": 70.31,
    "midi52Matches": 32,
    "midi52Expected": 32,
    "midi62Matches": 14,
    "midi62Expected": 16,
    "protectedRecallPercentage": 95.83,
    "weightedScore": 75.744,
    "productionPromotionAllowed": False,
}


def _log(message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} | {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _target_midi62_measures(targets: list[dict[str, Any]]) -> list[int]:
    return sorted(
        int(target["measureNumber"])
        for target in targets
        if int(target["midiPitch"]) == 62
    )


def _events_for_window(
    events: list[dict[str, Any]],
    start: float,
    end: float,
) -> list[dict[str, Any]]:
    return [
        event
        for event in events
        if start <= float(event.get("start", 0.0)) < end
    ]


def _diagnose_midi62(
    events: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    bounds: dict[int, tuple[float, float]],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    for measure_number in _target_midi62_measures(targets):
        start, end = bounds[measure_number]
        measure_events = _events_for_window(events, start, end)
        exact = [event for event in measure_events if int(event["midiPitch"]) == 62]

        expanded_start = start - 0.35
        expanded_end = end + 0.35
        expanded_events = _events_for_window(events, expanded_start, expanded_end)
        nearby = [
            event
            for event in expanded_events
            if 59 <= int(event["midiPitch"]) <= 65
        ]

        before_boundary = [
            event
            for event in nearby
            if float(event["start"]) < start
        ]
        after_boundary = [
            event
            for event in nearby
            if float(event["start"]) >= end
        ]

        classification = "exact-match"
        if not exact:
            if any(int(event["midiPitch"]) == 62 for event in before_boundary):
                classification = "midi62-before-measure-boundary"
            elif any(int(event["midiPitch"]) == 62 for event in after_boundary):
                classification = "midi62-after-measure-boundary"
            elif any(int(event["midiPitch"]) in {61, 63} for event in nearby):
                classification = "neighbor-semitone-detection"
            elif nearby:
                classification = "nearby-upper-register-event"
            else:
                classification = "no-upper-register-candidate"

        findings.append(
            {
                "measureNumber": measure_number,
                "measureStart": round(start, 6),
                "measureEnd": round(end, 6),
                "matched": bool(exact),
                "classification": classification,
                "exactMidi62Events": exact,
                "nearbyPitchEventsExpandedWindow": nearby,
                "midi62BeforeBoundary": [
                    event
                    for event in before_boundary
                    if int(event["midiPitch"]) == 62
                ],
                "midi62AfterBoundary": [
                    event
                    for event in after_boundary
                    if int(event["midiPitch"]) == 62
                ],
            }
        )

    return findings


def _load_or_extract_events(
    heartbeat: int,
    worker_start_timeout: int,
    total_timeout: int,
) -> tuple[list[dict[str, Any]], str]:
    if EVENT_CACHE_PATH.is_file():
        cached = _load_json(EVENT_CACHE_PATH)
        events = cached.get("events", [])
        if events:
            _log(f"Using protected event cache | events={len(events)}")
            return events, str(cached.get("sourceCallId") or "cached")

    audio_bytes = _build_audio_only_wav()
    function = modal.Function.from_name(APP_NAME, FUNCTION_NAME)
    call = function.spawn(audio_bytes, BEST_PARAMETERS)
    submitted = time.time()
    _log(
        "Submitted protected 82 Hz most-sensitive extraction | "
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
            try:
                call.cancel(terminate_containers=False)
            except Exception:
                pass
            raise TimeoutError("Protected extraction worker did not start in time.")

        if elapsed >= total_timeout:
            try:
                call.cancel(terminate_containers=False)
            except Exception:
                pass
            raise TimeoutError("Protected extraction exceeded total timeout.")

        try:
            result_bytes = call.get(timeout=0)
            result = json.loads(result_bytes.decode("utf-8"))
            events = result.get("events", [])
            _write_json(
                EVENT_CACHE_PATH,
                {
                    "sourceCallId": call.object_id,
                    "parameters": BEST_PARAMETERS,
                    "events": events,
                },
            )
            return events, call.object_id
        except TimeoutError:
            phase = "prediction" if task_id else "worker-start"
            _log(
                f"[{phase} heartbeat] elapsed={elapsed:.1f}s | "
                f"taskId={task_id or '-'} | callId={call.object_id}"
            )
            time.sleep(heartbeat)


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

    LOG_PATH.write_text("", encoding="utf-8")

    protected_checkpoint = {
        "checkpointVersion": 1,
        "checkpointName": "Jimmy PAIge professional best 84.72 percent",
        "parameters": BEST_PARAMETERS,
        "protectedBaseline": PROTECTED_BASELINE,
        "professionalReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "status": "protected-not-promoted",
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "professionalPdfRemainsScoringAuthority": True,
        "requiredFutureGuards": {
            "overallRecallMinimum": 84.72,
            "lowRegisterRecallMinimum": 70.31,
            "midi52Required": "32/32",
            "midi62Required": "16/16",
        },
    }
    _write_json(PROTECTED_CHECKPOINT_PATH, protected_checkpoint)
    _log(
        "Protected professional checkpoint | overall=84.72% | "
        "low=70.31% | MIDI52=32/32 | MIDI62=14/16"
    )

    reference = _load_json(REFERENCE_PATH)
    calibration = _load_json(CALIBRATION_PATH)
    targets = _targets(reference)
    bounds = _measure_bounds(calibration)

    events, call_id = _load_or_extract_events(
        heartbeat,
        worker_start_timeout,
        total_timeout,
    )
    score = _score(events, targets, bounds)
    findings = _diagnose_midi62(events, targets, bounds)
    misses = [item for item in findings if not item["matched"]]

    classification_counts: dict[str, int] = {}
    for miss in misses:
        classification = str(miss["classification"])
        classification_counts[classification] = (
            classification_counts.get(classification, 0) + 1
        )

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "protected-84-72-midi62-miss-diagnosis",
        "sourceCallId": call_id,
        "parameters": BEST_PARAMETERS,
        "protectedCheckpoint": str(
            PROTECTED_CHECKPOINT_PATH.relative_to(REPO_ROOT)
        ),
        "professionalReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "score": score,
        "midi62Targets": len(findings),
        "midi62Matched": len(findings) - len(misses),
        "midi62Missed": len(misses),
        "missingMeasures": [item["measureNumber"] for item in misses],
        "missClassificationCounts": classification_counts,
        "measureFindings": findings,
        "productionPromotionAllowed": False,
        "nextAction": (
            "Use the two miss classifications to build a narrow recovery test; "
            "do not weaken the protected 84.72 percent checkpoint."
        ),
    }
    _write_json(OUTPUT_PATH, report)

    _log(
        f"MIDI62 diagnosis complete | matched={report['midi62Matched']}/"
        f"{report['midi62Targets']} | missingMeasures={report['missingMeasures']}"
    )
    for miss in misses:
        _log(
            f"MIDI62 MISS | measure={miss['measureNumber']} | "
            f"classification={miss['classification']}"
        )
    _log(f"Protected checkpoint: {PROTECTED_CHECKPOINT_PATH.relative_to(REPO_ROOT)}")
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
