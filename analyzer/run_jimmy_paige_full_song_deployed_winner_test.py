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

APP_NAME = "dadrock-jimmy-paige-training-worker"
FUNCTION_NAME = "upper_string_recovery"
SOURCE_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-test.json"
CHECKPOINT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-test-checkpoint.json"
LOG_PATH = REPO_ROOT / "jimmy-paige-full-song-winner-test-heartbeat.log"


def _log(message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} | {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _build_audio_only_wav() -> bytes:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Missing full-song source: {SOURCE_PATH}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        wav_path = Path(handle.name)

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(SOURCE_PATH),
                "-map",
                "0:a:0",
                "-vn",
                "-ac",
                "1",
                "-ar",
                "22050",
                "-c:a",
                "pcm_s16le",
                str(wav_path),
            ],
            check=True,
        )
        return wav_path.read_bytes()
    finally:
        wav_path.unlink(missing_ok=True)


def _write_checkpoint(report: dict[str, Any]) -> None:
    CHECKPOINT_PATH.write_text(json.dumps(report, indent=2) + "\n")


def main() -> None:
    heartbeat = max(10, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "30")))
    worker_start_timeout = max(
        60,
        int(os.getenv("JIMMY_WORKER_START_TIMEOUT", "180")),
    )
    retries = max(1, int(os.getenv("JIMMY_MAX_RETRIES", "3")))

    LOG_PATH.write_text("")
    audio_bytes = _build_audio_only_wav()
    started = time.time()

    report: dict[str, Any] = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-full-song-deployed-winner-test",
        "source": str(SOURCE_PATH.relative_to(REPO_ROOT)),
        "functionName": FUNCTION_NAME,
        "parameters": {
            "onset_threshold": 0.35,
            "frame_threshold": 0.20,
            "minimum_note_length": 75.0,
            "minimum_frequency": 100.0,
            "maximum_frequency": 1400.0,
        },
        "status": "running",
        "payloadMiB": round(len(audio_bytes) / 1024 / 1024, 3),
        "professionalReferenceScope": "protected Em-riff slots derived from the professional rhythm tab",
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    _write_checkpoint(report)

    _log(
        "Starting full-song deployed winner test | "
        f"payload={report['payloadMiB']:.2f} MiB | function={FUNCTION_NAME}"
    )

    for retry in range(1, retries + 1):
        function = modal.Function.from_name(APP_NAME, FUNCTION_NAME)
        call = function.spawn(audio_bytes)
        submitted = time.time()
        report.update(
            {
                "status": "submitted",
                "retry": retry,
                "callId": call.object_id,
            }
        )
        _write_checkpoint(report)
        _log(
            f"Full-song call submitted | retry={retry}/{retries} | "
            f"callId={call.object_id}"
        )

        while True:
            try:
                result_bytes = call.get(timeout=0)
                result = json.loads(result_bytes.decode("utf-8"))
                events = result.get("events", [])
                score = _score(events)

                report.update(
                    {
                        "status": "complete",
                        "trainingComplete": True,
                        "remoteElapsedSeconds": result.get("remoteElapsedSeconds"),
                        "totalElapsedSeconds": round(time.time() - started, 3),
                        "attemptElapsedSeconds": round(time.time() - submitted, 3),
                        "extractedEventCount": len(events),
                        "correctCandidateSlots": score["correctCandidateSlots"],
                        "candidatePresencePercentage": score[
                            "candidatePresencePercentage"
                        ],
                        "slotReports": score["slotReports"],
                    }
                )
                OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
                _write_checkpoint(report)
                _log(
                    "Full-song winner test complete | "
                    f"events={len(events)} | "
                    f"professional-reference score={report['correctCandidateSlots']}/9 | "
                    f"remote={report['remoteElapsedSeconds']}s | "
                    f"total={report['totalElapsedSeconds']}s"
                )
                _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
                return
            except TimeoutError:
                elapsed = time.time() - submitted
                task_id = ""
                for item in call.get_call_graph():
                    task_id = str(getattr(item, "task_id", "") or "")
                    if task_id:
                        break

                phase = "prediction" if task_id else "worker-start"
                _log(
                    f"[{phase} heartbeat] elapsed={elapsed:.1f}s | "
                    f"retry={retry}/{retries} | taskId={task_id or '-'} | "
                    f"callId={call.object_id}"
                )

                if not task_id and elapsed >= worker_start_timeout:
                    call.cancel()
                    _log(
                        "Full-song call cancelled after worker-start timeout | "
                        f"retry={retry}/{retries}"
                    )
                    break

                time.sleep(heartbeat)
            except Exception as error:
                report.update(
                    {
                        "status": "failed",
                        "error": repr(error),
                        "totalElapsedSeconds": round(time.time() - started, 3),
                    }
                )
                _write_checkpoint(report)
                raise

    report.update(
        {
            "status": "stopped-no-worker",
            "totalElapsedSeconds": round(time.time() - started, 3),
        }
    )
    _write_checkpoint(report)
    _log(f"Full-song test stopped after {retries} worker-start retries.")


if __name__ == "__main__":
    main()
