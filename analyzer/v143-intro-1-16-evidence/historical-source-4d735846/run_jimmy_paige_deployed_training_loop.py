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

APP_NAME = "dadrock-jimmy-paige-training-worker"
SOURCE_PATH = REPO_ROOT / "public" / "DadRock TABS - gomyway2test.m4a"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-deployed-training.json"
CHECKPOINT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-deployed-training-checkpoint.json"
LOG_PATH = REPO_ROOT / "jimmy-paige-deployed-training-heartbeat.log"

FUNCTION_NAMES = (
    "default",
    "lower_onset",
    "lower_frame",
    "sensitive_balanced",
    "short_note_recovery",
    "upper_string_recovery",
)


def _log(message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} | {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _build_audio_only_wav() -> bytes:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Missing V7 snippet: {SOURCE_PATH}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        wav_path = Path(handle.name)

    try:
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(SOURCE_PATH), "-map", "0:a:0", "-vn",
            "-ac", "1", "-ar", "22050", "-c:a", "pcm_s16le",
            str(wav_path),
        ], check=True)
        return wav_path.read_bytes()
    finally:
        wav_path.unlink(missing_ok=True)


def _write(report: dict[str, Any]) -> None:
    CHECKPOINT_PATH.write_text(json.dumps(report, indent=2) + "\n")


def main() -> None:
    heartbeat = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    timeout = max(30, int(os.getenv("JIMMY_WORKER_START_TIMEOUT", "120")))
    retries = max(1, int(os.getenv("JIMMY_MAX_RETRIES", "3")))
    max_attempts = max(1, min(len(FUNCTION_NAMES), int(os.getenv("JIMMY_MAX_ATTEMPTS", "6"))))

    LOG_PATH.write_text("")
    audio_bytes = _build_audio_only_wav()
    started = time.time()
    report: dict[str, Any] = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-deployed-worker-training",
        "source": str(SOURCE_PATH.relative_to(REPO_ROOT)),
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
    }
    _write(report)

    _log(f"Starting deployed-worker training | payload={len(audio_bytes)/1024/1024:.2f} MiB | attempts={max_attempts}")

    for index, function_name in enumerate(FUNCTION_NAMES[:max_attempts], start=1):
        completed = False
        for retry in range(1, retries + 1):
            function = modal.Function.from_name(APP_NAME, function_name)
            call = function.spawn(audio_bytes)
            submitted = time.time()
            _log(f"Attempt {index}/{max_attempts} submitted | function={function_name} | retry={retry}/{retries} | callId={call.object_id}")

            while True:
                try:
                    result_bytes = call.get(timeout=0)
                    completed = True
                    break
                except TimeoutError:
                    elapsed = time.time() - submitted
                    graph = call.get_call_graph()
                    task_id = ""
                    for item in graph:
                        task_id = str(getattr(item, "task_id", "") or "")
                        if task_id:
                            break
                    phase = "prediction" if task_id else "worker-start"
                    _log(f"[{phase} heartbeat] attempt={index}/{max_attempts} | retry={retry}/{retries} | elapsed={elapsed:.1f}s | taskId={task_id or '-'} | callId={call.object_id}")
                    if not task_id and elapsed >= timeout:
                        call.cancel()
                        _log(f"Attempt {index}/{max_attempts} cancelled after worker-start timeout | retry={retry}/{retries}")
                        break
                    time.sleep(heartbeat)

            if completed:
                result = json.loads(result_bytes.decode("utf-8"))
                events = result.get("events", [])
                score = _score(events)
                attempt = {
                    "attemptNumber": index,
                    "name": ATTEMPTS[index - 1]["name"],
                    "functionName": function_name,
                    "callId": call.object_id,
                    "remoteElapsedSeconds": result.get("remoteElapsedSeconds"),
                    "totalElapsedSeconds": round(time.time() - submitted, 3),
                    "extractedEventCount": len(events),
                    "correctCandidateSlots": score["correctCandidateSlots"],
                    "candidatePresencePercentage": score["candidatePresencePercentage"],
                }
                report["attempts"].append(attempt)
                report["attemptsCompleted"] = index
                if (
                    attempt["correctCandidateSlots"] > report["bestCorrectCandidateSlots"]
                    or (
                        attempt["correctCandidateSlots"] == report["bestCorrectCandidateSlots"]
                        and attempt["candidatePresencePercentage"] > report["bestCandidatePresencePercentage"]
                    )
                ):
                    report["bestCorrectCandidateSlots"] = attempt["correctCandidateSlots"]
                    report["bestCandidatePresencePercentage"] = attempt["candidatePresencePercentage"]
                    report["bestAttempt"] = attempt
                _write(report)
                _log(f"Attempt {index}/{max_attempts} complete | events={len(events)} | correct={attempt['correctCandidateSlots']}/9")
                break

        if not completed:
            report["status"] = "stopped-no-worker"
            report["failedAttempt"] = index
            _write(report)
            _log(f"Training stopped: attempt {index}/{max_attempts} could not obtain a deployed worker after {retries} retries.")
            return

    report["status"] = "complete"
    report["trainingComplete"] = True
    report["totalElapsedSeconds"] = round(time.time() - started, 3)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    _write(report)
    _log(f"Deployed training complete | best={report['bestCorrectCandidateSlots']}/9 | elapsed={report['totalElapsedSeconds']}s")
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
