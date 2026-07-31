from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

from run_jimmy_paige_em_riff_extraction_training_loop import REPO_ROOT, _score

SOURCE_PATH = REPO_ROOT / "public" / "DadRock TABS - gomyway2test.m4a"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-v7-snippet-fixed-function-training.json"
CHECKPOINT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-v7-snippet-fixed-function-training-checkpoint.json"
LOG_PATH = REPO_ROOT / "jimmy-paige-v7-snippet-fixed-function-training.log"

app = modal.App("dadrock-jimmy-paige-v7-fixed-function-training")
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


def _normalize_note_event(event: Any) -> dict[str, Any] | None:
    if isinstance(event, dict):
        start = event.get("start_time", event.get("start", 0.0))
        end = event.get("end_time", event.get("end", start))
        pitch = event.get(
            "pitch_midi",
            event.get("midi_pitch", event.get("midiPitch", event.get("pitch"))),
        )
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
            "midiPitch": int(pitch),
            "confidence": float(confidence or 0.0),
        }
    except (TypeError, ValueError):
        return None


def _predict_fixed(audio_bytes: bytes, parameters: dict[str, Any]) -> bytes:
    from basic_pitch.inference import predict

    started = time.time()
    print(f"[remote] fixed function started name={parameters['name']}", flush=True)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        audio_path = Path(handle.name)
        handle.write(audio_bytes)

    try:
        kwargs = {key: value for key, value in parameters.items() if key != "name"}
        _, _, note_events = predict(
            audio_path,
            multiple_pitch_bends=False,
            melodia_trick=True,
            **kwargs,
        )
        events: list[dict[str, Any]] = []
        for event in note_events:
            normalized = _normalize_note_event(event)
            if normalized is not None:
                events.append(normalized)

        payload = {
            "name": parameters["name"],
            "parameters": kwargs,
            "events": events,
            "remoteElapsedSeconds": round(time.time() - started, 3),
        }
        print(
            f"[remote] fixed function complete name={parameters['name']} "
            f"events={len(events)} elapsed={payload['remoteElapsedSeconds']}s",
            flush=True,
        )
        return json.dumps(payload).encode("utf-8")
    finally:
        audio_path.unlink(missing_ok=True)


@app.function(image=image, timeout=900, memory=4096)
def extract_default(audio_bytes: bytes) -> bytes:
    return _predict_fixed(audio_bytes, {
        "name": "default", "onset_threshold": 0.50,
        "frame_threshold": 0.30, "minimum_note_length": 127.7,
    })


@app.function(image=image, timeout=900, memory=4096)
def extract_lower_onset(audio_bytes: bytes) -> bytes:
    return _predict_fixed(audio_bytes, {
        "name": "lower-onset", "onset_threshold": 0.40,
        "frame_threshold": 0.30, "minimum_note_length": 127.7,
    })


@app.function(image=image, timeout=900, memory=4096)
def extract_lower_frame(audio_bytes: bytes) -> bytes:
    return _predict_fixed(audio_bytes, {
        "name": "lower-frame", "onset_threshold": 0.50,
        "frame_threshold": 0.22, "minimum_note_length": 127.7,
    })


@app.function(image=image, timeout=900, memory=4096)
def extract_sensitive_balanced(audio_bytes: bytes) -> bytes:
    return _predict_fixed(audio_bytes, {
        "name": "sensitive-balanced", "onset_threshold": 0.40,
        "frame_threshold": 0.22, "minimum_note_length": 100.0,
    })


@app.function(image=image, timeout=900, memory=4096)
def extract_short_note_recovery(audio_bytes: bytes) -> bytes:
    return _predict_fixed(audio_bytes, {
        "name": "short-note-recovery", "onset_threshold": 0.45,
        "frame_threshold": 0.25, "minimum_note_length": 75.0,
    })


@app.function(image=image, timeout=900, memory=4096)
def extract_upper_string_recovery(audio_bytes: bytes) -> bytes:
    return _predict_fixed(audio_bytes, {
        "name": "upper-string-recovery", "onset_threshold": 0.35,
        "frame_threshold": 0.20, "minimum_note_length": 75.0,
        "minimum_frequency": 100.0, "maximum_frequency": 1400.0,
    })


FIXED_ATTEMPTS = (
    ("default", extract_default),
    ("lower-onset", extract_lower_onset),
    ("lower-frame", extract_lower_frame),
    ("sensitive-balanced", extract_sensitive_balanced),
    ("short-note-recovery", extract_short_note_recovery),
    ("upper-string-recovery", extract_upper_string_recovery),
)


def _build_audio_only_wav() -> bytes:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Missing proven V7 snippet: {SOURCE_PATH}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        wav_path = Path(handle.name)

    try:
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(SOURCE_PATH), "-map", "0:a:0", "-vn",
                "-ac", "1", "-ar", "22050", "-c:a", "pcm_s16le",
                str(wav_path),
            ],
            check=True,
        )
        return wav_path.read_bytes()
    finally:
        wav_path.unlink(missing_ok=True)


def _worker_started(call: modal.FunctionCall) -> bool:
    try:
        for item in call.get_call_graph():
            if getattr(item, "task_id", None):
                return True
    except Exception:
        return False
    return False


def _write_checkpoint(report: dict[str, Any]) -> None:
    CHECKPOINT_PATH.write_text(json.dumps(report, indent=2) + "\n")


def main() -> None:
    heartbeat = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    start_timeout = max(30, int(os.getenv("JIMMY_WORKER_START_TIMEOUT", "90")))
    retries = max(1, int(os.getenv("JIMMY_MAX_RETRIES", "3")))
    max_attempts = max(1, min(len(FIXED_ATTEMPTS), int(os.getenv("JIMMY_MAX_ATTEMPTS", "6"))))

    audio_bytes = _build_audio_only_wav()
    LOG_PATH.write_text("")
    overall_started = time.time()

    report: dict[str, Any] = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-v7-snippet-fixed-function-training",
        "source": str(SOURCE_PATH.relative_to(REPO_ROOT)),
        "audioPayloadBytes": len(audio_bytes),
        "attemptsRequested": max_attempts,
        "attemptsCompleted": 0,
        "bestCorrectCandidateSlots": 0,
        "bestCandidatePresencePercentage": 0.0,
        "bestAttempt": None,
        "attempts": [],
        "status": "running",
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "lockedV7EventsProtected": True,
        "lockedV8TimingProtected": True,
    }
    _write_checkpoint(report)

    _log(
        "Starting fixed-function training with audio-only payload | "
        f"payload={len(audio_bytes) / 1024 / 1024:.2f} MiB | attempts={max_attempts}"
    )

    with app.run():
        for attempt_number, (name, function) in enumerate(FIXED_ATTEMPTS[:max_attempts], start=1):
            completed = False
            for retry in range(1, retries + 1):
                submitted_at = time.time()
                call = function.spawn(audio_bytes)
                _log(
                    f"Attempt {attempt_number}/{max_attempts} submitted | name={name} | "
                    f"retry={retry}/{retries} | callId={call.object_id}"
                )

                worker_seen = False
                while True:
                    try:
                        result_bytes = call.get(timeout=0)
                        completed = True
                        break
                    except TimeoutError:
                        elapsed = time.time() - submitted_at
                        worker_seen = worker_seen or _worker_started(call)
                        phase = "prediction" if worker_seen else "worker-start"
                        _log(
                            f"[{phase} heartbeat] attempt={attempt_number}/{max_attempts} | "
                            f"name={name} | retry={retry}/{retries} | elapsed={elapsed:.1f}s | "
                            f"callId={call.object_id}"
                        )
                        if not worker_seen and elapsed >= start_timeout:
                            call.cancel()
                            _log(
                                f"Attempt {attempt_number}/{max_attempts} cancelled after "
                                f"worker-start timeout | retry={retry}/{retries}"
                            )
                            break
                        time.sleep(heartbeat)

                if completed:
                    result = json.loads(result_bytes.decode("utf-8"))
                    events = result.get("events", [])
                    score = _score(events)
                    attempt_report = {
                        "attemptNumber": attempt_number,
                        "name": name,
                        "retryUsed": retry,
                        "callId": call.object_id,
                        "remoteElapsedSeconds": result.get("remoteElapsedSeconds"),
                        "totalElapsedSeconds": round(time.time() - submitted_at, 3),
                        "extractedEventCount": len(events),
                        "correctCandidateSlots": score["correctCandidateSlots"],
                        "candidatePresencePercentage": score["candidatePresencePercentage"],
                        "slotReports": score["slotReports"],
                    }
                    report["attempts"].append(attempt_report)
                    report["attemptsCompleted"] = len(report["attempts"])

                    if (
                        attempt_report["correctCandidateSlots"] > report["bestCorrectCandidateSlots"]
                        or (
                            attempt_report["correctCandidateSlots"] == report["bestCorrectCandidateSlots"]
                            and attempt_report["candidatePresencePercentage"]
                            > report["bestCandidatePresencePercentage"]
                        )
                    ):
                        report["bestCorrectCandidateSlots"] = attempt_report["correctCandidateSlots"]
                        report["bestCandidatePresencePercentage"] = attempt_report["candidatePresencePercentage"]
                        report["bestAttempt"] = attempt_report

                    _write_checkpoint(report)
                    _log(
                        f"Attempt {attempt_number}/{max_attempts} complete | name={name} | "
                        f"events={len(events)} | correct={score['correctCandidateSlots']}/9 | "
                        f"presence={score['candidatePresencePercentage']}%"
                    )
                    break

            if not completed:
                report["status"] = "stopped-no-worker"
                report["failedAttempt"] = attempt_number
                report["failedAttemptName"] = name
                report["totalElapsedSeconds"] = round(time.time() - overall_started, 3)
                _write_checkpoint(report)
                _log(
                    f"Training stopped: attempt {attempt_number}/{max_attempts} "
                    f"could not obtain a worker after {retries} retries."
                )
                return

    report["status"] = "complete"
    report["trainingComplete"] = True
    report["totalElapsedSeconds"] = round(time.time() - overall_started, 3)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    _write_checkpoint(report)
    _log(
        f"Fixed-function training complete | best={report['bestCorrectCandidateSlots']}/9 | "
        f"presence={report['bestCandidatePresencePercentage']}% | "
        f"elapsed={report['totalElapsedSeconds']}s"
    )
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
