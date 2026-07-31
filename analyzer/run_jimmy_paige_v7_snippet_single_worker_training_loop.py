from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

from run_jimmy_paige_em_riff_extraction_training_loop import ATTEMPTS, REPO_ROOT, _score

SOURCE_PATH = REPO_ROOT / "public" / "DadRock TABS - gomyway2test.m4a"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-v7-snippet-single-worker-training.json"
CHECKPOINT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-v7-snippet-single-worker-training-checkpoint.json"
LOG_PATH = REPO_ROOT / "jimmy-paige-v7-snippet-single-worker-heartbeat.log"

app = modal.App("dadrock-jimmy-paige-v7-snippet-single-worker-training")
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


@app.function(image=image, timeout=1800, memory=4096)
def run_all_attempts(audio_bytes: bytes, attempts: list[dict[str, Any]]) -> bytes:
    from basic_pitch.inference import predict

    remote_started = time.time()
    print(f"[remote] single worker started attempts={len(attempts)}", flush=True)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        audio_path = Path(handle.name)
        handle.write(audio_bytes)

    try:
        results: list[dict[str, Any]] = []
        for index, parameters in enumerate(attempts, start=1):
            attempt_started = time.time()
            print(
                f"[remote] attempt={index}/{len(attempts)} "
                f"name={parameters.get('name')} started",
                flush=True,
            )
            _, _, note_events = predict(
                audio_path,
                onset_threshold=float(parameters.get("onset_threshold", 0.50)),
                frame_threshold=float(parameters.get("frame_threshold", 0.30)),
                minimum_note_length=float(parameters.get("minimum_note_length", 127.7)),
                minimum_frequency=parameters.get("minimum_frequency"),
                maximum_frequency=parameters.get("maximum_frequency"),
                multiple_pitch_bends=False,
                melodia_trick=True,
            )

            normalized: list[dict[str, Any]] = []
            for event in note_events:
                item = _normalize_note_event(event)
                if item is not None:
                    normalized.append(item)

            result = {
                "attemptNumber": index,
                "name": parameters.get("name"),
                "parameters": parameters,
                "events": normalized,
                "remoteElapsedSeconds": round(time.time() - attempt_started, 3),
            }
            results.append(result)
            print(
                f"[remote] attempt={index}/{len(attempts)} completed "
                f"events={len(normalized)} "
                f"elapsed={result['remoteElapsedSeconds']}s",
                flush=True,
            )

        return json.dumps(
            {
                "attempts": results,
                "remoteTotalElapsedSeconds": round(time.time() - remote_started, 3),
            }
        ).encode("utf-8")
    finally:
        audio_path.unlink(missing_ok=True)


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


def main() -> None:
    heartbeat_seconds = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    max_attempts = max(
        1,
        min(len(ATTEMPTS), int(os.getenv("JIMMY_MAX_ATTEMPTS", str(len(ATTEMPTS))))),
    )
    attempts = [dict(item) for item in ATTEMPTS[:max_attempts]]
    audio_bytes = _build_audio_only_wav()
    started = time.time()

    LOG_PATH.write_text("")
    checkpoint = {
        "benchmarkVersion": 8,
        "status": "submitting",
        "source": str(SOURCE_PATH.relative_to(REPO_ROOT)),
        "audioPayloadBytes": len(audio_bytes),
        "attemptsRequested": max_attempts,
        "attemptsCompleted": 0,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "lockedV7EventsProtected": True,
        "lockedV8TimingProtected": True,
    }
    CHECKPOINT_PATH.write_text(json.dumps(checkpoint, indent=2) + "\n")

    _log(
        "Starting single-worker bounded training | "
        f"payload={len(audio_bytes) / 1024 / 1024:.2f} MiB | attempts={max_attempts}"
    )

    with app.run(detach=True):
        call = run_all_attempts.spawn(audio_bytes, attempts)

    checkpoint["status"] = "submitted"
    checkpoint["callId"] = call.object_id
    checkpoint["startedAtEpoch"] = started
    CHECKPOINT_PATH.write_text(json.dumps(checkpoint, indent=2) + "\n")
    _log(f"Single worker submitted | callId={call.object_id}")

    while True:
        try:
            result_bytes = call.get(timeout=0)
            break
        except TimeoutError:
            elapsed = time.time() - started
            _log(
                f"[single-worker heartbeat] elapsed={elapsed:.1f}s | "
                f"attempts=0/{max_attempts} until remote batch returns | "
                f"callId={call.object_id}"
            )
            time.sleep(heartbeat_seconds)

    remote_result = json.loads(result_bytes.decode("utf-8"))
    report: dict[str, Any] = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-v7-snippet-single-worker-training-loop",
        "source": str(SOURCE_PATH.relative_to(REPO_ROOT)),
        "audioPayloadBytes": len(audio_bytes),
        "attemptsRequested": max_attempts,
        "attemptsCompleted": 0,
        "bestCorrectCandidateSlots": 0,
        "bestCandidatePresencePercentage": 0.0,
        "bestAttempt": None,
        "attempts": [],
        "remoteTotalElapsedSeconds": remote_result.get("remoteTotalElapsedSeconds"),
        "trainingComplete": True,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "lockedV7EventsProtected": True,
        "lockedV8TimingProtected": True,
    }

    for item in remote_result.get("attempts", []):
        events = item.get("events", [])
        score = _score(events)
        attempt_report = {
            "attemptNumber": item.get("attemptNumber"),
            "name": item.get("name"),
            "parameters": item.get("parameters"),
            "remoteElapsedSeconds": item.get("remoteElapsedSeconds"),
            "extractedEventCount": len(events),
            "correctCandidateSlots": score["correctCandidateSlots"],
            "candidatePresencePercentage": score["candidatePresencePercentage"],
        }
        report["attempts"].append(attempt_report)
        report["attemptsCompleted"] += 1

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

    report["totalElapsedSeconds"] = round(time.time() - started, 3)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    checkpoint.update(
        {
            "status": "complete",
            "attemptsCompleted": report["attemptsCompleted"],
            "bestCorrectCandidateSlots": report["bestCorrectCandidateSlots"],
            "bestCandidatePresencePercentage": report["bestCandidatePresencePercentage"],
            "outputPath": str(OUTPUT_PATH.relative_to(REPO_ROOT)),
        }
    )
    CHECKPOINT_PATH.write_text(json.dumps(checkpoint, indent=2) + "\n")

    _log(
        "Single-worker bounded training complete | "
        f"best={report['bestCorrectCandidateSlots']}/9 | "
        f"presence={report['bestCandidatePresencePercentage']}% | "
        f"remote={report['remoteTotalElapsedSeconds']}s | "
        f"total={report['totalElapsedSeconds']}s"
    )
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
