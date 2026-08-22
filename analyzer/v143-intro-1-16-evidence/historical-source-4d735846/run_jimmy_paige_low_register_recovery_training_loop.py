from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any

import modal

from run_jimmy_paige_em_riff_extraction_training_loop import REPO_ROOT

SOURCE_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
CALIBRATION_PATH = REPO_ROOT / "public" / "gomyway-professional-measures-1-16-timing-calibration.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-low-register-recovery-training.json"
CHECKPOINT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-low-register-recovery-checkpoint.json"
LOG_PATH = REPO_ROOT / "jimmy-paige-low-register-recovery-heartbeat.log"

LOW_REGISTER_PITCHES = {40, 45, 50, 58}
PROTECTED_PITCHES = {52, 62}
TARGET_MEASURES = set(range(1, 17))

ATTEMPTS: list[dict[str, Any]] = [
    {
        "name": "baseline",
        "onset_threshold": 0.50,
        "frame_threshold": 0.30,
        "minimum_note_length": 127.7,
        "minimum_frequency": None,
        "maximum_frequency": None,
        "multiple_pitch_bends": False,
    },
    {
        "name": "low-floor-70",
        "onset_threshold": 0.50,
        "frame_threshold": 0.30,
        "minimum_note_length": 127.7,
        "minimum_frequency": 70.0,
        "maximum_frequency": None,
        "multiple_pitch_bends": False,
    },
    {
        "name": "lower-onset",
        "onset_threshold": 0.38,
        "frame_threshold": 0.30,
        "minimum_note_length": 127.7,
        "minimum_frequency": 70.0,
        "maximum_frequency": None,
        "multiple_pitch_bends": False,
    },
    {
        "name": "lower-frame",
        "onset_threshold": 0.45,
        "frame_threshold": 0.20,
        "minimum_note_length": 127.7,
        "minimum_frequency": 70.0,
        "maximum_frequency": None,
        "multiple_pitch_bends": False,
    },
    {
        "name": "balanced-sensitive",
        "onset_threshold": 0.38,
        "frame_threshold": 0.20,
        "minimum_note_length": 100.0,
        "minimum_frequency": 70.0,
        "maximum_frequency": None,
        "multiple_pitch_bends": False,
    },
    {
        "name": "short-note-recovery",
        "onset_threshold": 0.35,
        "frame_threshold": 0.18,
        "minimum_note_length": 70.0,
        "minimum_frequency": 65.0,
        "maximum_frequency": None,
        "multiple_pitch_bends": False,
    },
    {
        "name": "bend-aware-sensitive",
        "onset_threshold": 0.38,
        "frame_threshold": 0.20,
        "minimum_note_length": 100.0,
        "minimum_frequency": 65.0,
        "maximum_frequency": None,
        "multiple_pitch_bends": True,
    },
    {
        "name": "very-sensitive-guarded",
        "onset_threshold": 0.30,
        "frame_threshold": 0.15,
        "minimum_note_length": 60.0,
        "minimum_frequency": 60.0,
        "maximum_frequency": None,
        "multiple_pitch_bends": True,
    },
]

app = modal.App("dadrock-jimmy-paige-low-register-recovery")
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("basic-pitch")
)


def _log(message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} | {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_note_event(event: Any) -> dict[str, Any] | None:
    if isinstance(event, dict):
        start = event.get("start_time", event.get("start", 0.0))
        end = event.get("end_time", event.get("end", start))
        pitch = event.get("pitch_midi", event.get("midi_pitch", event.get("midiPitch", event.get("pitch"))))
        confidence = event.get("amplitude", event.get("confidence", 0.0))
    elif isinstance(event, (list, tuple)) and len(event) >= 3:
        start, end, pitch = event[0], event[1], event[2]
        confidence = event[3] if len(event) >= 4 else 0.0
    else:
        return None
    try:
        return {
            "start": float(start),
            "end": float(end),
            "midiPitch": int(round(float(pitch))),
            "confidence": float(confidence or 0.0),
        }
    except (TypeError, ValueError):
        return None


@app.function(image=image, timeout=1200, memory=4096)
def extract_attempt(audio_bytes: bytes, parameters: dict[str, Any]) -> bytes:
    from basic_pitch.inference import predict

    started = time.time()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        audio_path = Path(handle.name)
        handle.write(audio_bytes)
    try:
        _, _, note_events = predict(
            audio_path,
            onset_threshold=float(parameters["onset_threshold"]),
            frame_threshold=float(parameters["frame_threshold"]),
            minimum_note_length=float(parameters["minimum_note_length"]),
            minimum_frequency=parameters.get("minimum_frequency"),
            maximum_frequency=parameters.get("maximum_frequency"),
            multiple_pitch_bends=bool(parameters.get("multiple_pitch_bends", False)),
            melodia_trick=True,
        )
        events = [item for raw in note_events if (item := _normalize_note_event(raw)) is not None]
        return json.dumps({
            "events": events,
            "parameters": parameters,
            "remoteElapsedSeconds": round(time.time() - started, 3),
        }).encode("utf-8")
    finally:
        audio_path.unlink(missing_ok=True)


def _build_intro_wav() -> bytes:
    if not SOURCE_PATH.is_file():
        raise FileNotFoundError(f"Missing full-song audio: {SOURCE_PATH}")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        wav_path = Path(handle.name)
    try:
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(SOURCE_PATH), "-map", "0:a:0", "-vn",
            "-t", "38", "-ac", "1", "-ar", "22050", "-c:a", "pcm_s16le",
            str(wav_path),
        ], check=True)
        return wav_path.read_bytes()
    finally:
        wav_path.unlink(missing_ok=True)


def _targets(reference: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for measure in reference.get("measures", []):
        number = int(measure.get("measureNumber", 0))
        if number not in TARGET_MEASURES:
            continue
        for event in measure.get("events", []):
            pitch = int(event["midiPitch"])
            accepted = {pitch}
            sounding = event.get("soundingMidiPitch")
            if sounding is not None:
                accepted.add(int(sounding))
            result.append({
                "measureNumber": number,
                "midiPitch": pitch,
                "acceptedPitches": sorted(accepted),
            })
    return result


def _measure_bounds(calibration: dict[str, Any]) -> dict[int, tuple[float, float]]:
    best = calibration.get("best") or {}
    tempo = float(best.get("tempo") or 135.88)
    offset = float(best.get("offsetSeconds") or best.get("firstMeasureOffsetSeconds") or 5.045)
    duration = 4.0 * 60.0 / tempo
    return {
        number: (offset + (number - 1) * duration, offset + number * duration)
        for number in TARGET_MEASURES
    }


def _score(events: list[dict[str, Any]], targets: list[dict[str, Any]], bounds: dict[int, tuple[float, float]]) -> dict[str, Any]:
    events_by_measure: dict[int, list[dict[str, Any]]] = {}
    for number, (start, end) in bounds.items():
        events_by_measure[number] = [event for event in events if start <= float(event["start"]) < end]

    matched_by_pitch: Counter[int] = Counter()
    expected_by_pitch: Counter[int] = Counter()
    matched_total = 0
    for target in targets:
        pitch = int(target["midiPitch"])
        expected_by_pitch[pitch] += 1
        candidates = events_by_measure.get(int(target["measureNumber"]), [])
        if any(int(event["midiPitch"]) in target["acceptedPitches"] for event in candidates):
            matched_by_pitch[pitch] += 1
            matched_total += 1

    def recall(pitches: set[int]) -> float:
        expected = sum(expected_by_pitch[p] for p in pitches)
        matched = sum(matched_by_pitch[p] for p in pitches)
        return round(100.0 * matched / expected, 2) if expected else 0.0

    low_recall = recall(LOW_REGISTER_PITCHES)
    protected_recall = recall(PROTECTED_PITCHES)
    overall_recall = round(100.0 * matched_total / len(targets), 2) if targets else 0.0
    guard_passed = all(matched_by_pitch[p] == expected_by_pitch[p] for p in PROTECTED_PITCHES)
    weighted_score = round(low_recall * 0.70 + overall_recall * 0.20 + protected_recall * 0.10, 3)

    return {
        "matchedTargets": matched_total,
        "professionalTargets": len(targets),
        "overallRecallPercentage": overall_recall,
        "lowRegisterRecallPercentage": low_recall,
        "protectedRecallPercentage": protected_recall,
        "protectedPitchGuardPassed": guard_passed,
        "weightedScore": weighted_score,
        "expectedByPitch": dict(sorted(expected_by_pitch.items())),
        "matchedByPitch": dict(sorted(matched_by_pitch.items())),
    }


def _write_checkpoint(report: dict[str, Any]) -> None:
    CHECKPOINT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    heartbeat_seconds = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    max_attempts = max(1, min(len(ATTEMPTS), int(os.getenv("JIMMY_MAX_ATTEMPTS", str(len(ATTEMPTS))))))

    reference = _load_json(REFERENCE_PATH)
    calibration = _load_json(CALIBRATION_PATH)
    targets = _targets(reference)
    bounds = _measure_bounds(calibration)
    audio_bytes = _build_intro_wav()
    LOG_PATH.write_text("", encoding="utf-8")

    report: dict[str, Any] = {
        "benchmarkVersion": 1,
        "benchmarkType": "jimmy-paige-low-register-recovery-training",
        "source": str(SOURCE_PATH.relative_to(REPO_ROOT)),
        "professionalReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "targetMeasures": [1, 16],
        "targetPitches": sorted(LOW_REGISTER_PITCHES),
        "protectedPitches": sorted(PROTECTED_PITCHES),
        "attemptsRequested": max_attempts,
        "attemptsCompleted": 0,
        "attempts": [],
        "bestAttempt": None,
        "trainingComplete": False,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "readOnlySourceEvents": True,
        "noSyntheticNotes": True,
    }
    _write_checkpoint(report)
    started = time.time()
    _log(f"Starting low-register recovery training | attempts={max_attempts} | payload={len(audio_bytes)/1024/1024:.2f} MiB")

    with app.run():
        for index, parameters in enumerate(ATTEMPTS[:max_attempts], start=1):
            attempt_started = time.time()
            call = extract_attempt.spawn(audio_bytes, dict(parameters))
            _log(f"Attempt {index}/{max_attempts} submitted | name={parameters['name']} | callId={call.object_id}")
            while True:
                try:
                    result_bytes = call.get(timeout=0)
                    break
                except TimeoutError:
                    _log(
                        f"[low-register heartbeat] attempt={index}/{max_attempts} | name={parameters['name']} | "
                        f"elapsed={time.time()-attempt_started:.1f}s | callId={call.object_id}"
                    )
                    time.sleep(heartbeat_seconds)

            result = json.loads(result_bytes.decode("utf-8"))
            score = _score(result.get("events", []), targets, bounds)
            attempt_report = {
                "attemptNumber": index,
                "name": parameters["name"],
                "parameters": parameters,
                "callId": call.object_id,
                "remoteElapsedSeconds": result.get("remoteElapsedSeconds"),
                "totalElapsedSeconds": round(time.time() - attempt_started, 3),
                "extractedEventCount": len(result.get("events", [])),
                **score,
            }
            report["attempts"].append(attempt_report)
            report["attemptsCompleted"] = index

            best = report.get("bestAttempt")
            eligible = attempt_report["protectedPitchGuardPassed"]
            if eligible and (best is None or attempt_report["weightedScore"] > best["weightedScore"]):
                report["bestAttempt"] = attempt_report

            _write_checkpoint(report)
            _log(
                f"Attempt {index}/{max_attempts} complete | events={attempt_report['extractedEventCount']} | "
                f"low={attempt_report['lowRegisterRecallPercentage']}% | overall={attempt_report['overallRecallPercentage']}% | "
                f"protected={attempt_report['protectedRecallPercentage']}% | guard={attempt_report['protectedPitchGuardPassed']} | "
                f"weighted={attempt_report['weightedScore']}"
            )

    report["trainingComplete"] = True
    report["totalElapsedSeconds"] = round(time.time() - started, 3)
    best = report.get("bestAttempt")
    report["readyForNextValidationStage"] = bool(best and best["lowRegisterRecallPercentage"] >= 50.0)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _write_checkpoint(report)

    if best:
        _log(
            f"Training complete | best={best['name']} | low={best['lowRegisterRecallPercentage']}% | "
            f"overall={best['overallRecallPercentage']}% | protected={best['protectedRecallPercentage']}% | "
            f"weighted={best['weightedScore']}"
        )
    else:
        _log("Training complete | no attempt passed the MIDI 52/62 protection guard")
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
