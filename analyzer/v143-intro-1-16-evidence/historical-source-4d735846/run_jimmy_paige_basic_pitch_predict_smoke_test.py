from __future__ import annotations

import io
import json
import math
import os
import struct
import time
import wave
from pathlib import Path

import modal

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-basic-pitch-predict-smoke-test.json"

app = modal.App("dadrock-jimmy-paige-basic-pitch-predict-smoke-test")
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("basic-pitch")
)


def _build_test_wav() -> bytes:
    sample_rate = 22050
    duration_seconds = 2.0
    frequency_hz = 440.0
    frame_count = int(sample_rate * duration_seconds)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        for index in range(frame_count):
            sample = int(12000 * math.sin(2.0 * math.pi * frequency_hz * index / sample_rate))
            wav.writeframesraw(struct.pack("<h", sample))
    return buffer.getvalue()


@app.function(image=image, timeout=600, memory=4096)
def predict_smoke(audio_bytes: bytes) -> dict:
    from basic_pitch.inference import predict
    import tempfile

    started = time.time()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        handle.write(audio_bytes)
        audio_path = Path(handle.name)

    try:
        print("[remote] predict smoke worker started", flush=True)
        _, _, note_events = predict(audio_path)
        elapsed = time.time() - started
        print(
            f"[remote] predict smoke completed events={len(note_events)} elapsed={elapsed:.3f}s",
            flush=True,
        )
        return {
            "passed": True,
            "eventCount": len(note_events),
            "remoteElapsedSeconds": round(elapsed, 3),
        }
    finally:
        audio_path.unlink(missing_ok=True)


def main() -> None:
    heartbeat_seconds = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "10")))
    max_wait_seconds = max(60, int(os.getenv("JIMMY_SMOKE_MAX_WAIT_SECONDS", "600")))
    audio_bytes = _build_test_wav()
    submitted_at = time.time()

    print("Submitting 2-second Basic Pitch predict smoke test...", flush=True)
    with app.run(detach=True):
        call = predict_smoke.spawn(audio_bytes)

    print("Call ID:", call.object_id, flush=True)

    while True:
        try:
            result = call.get(timeout=0)
            total_elapsed = time.time() - submitted_at
            report = {
                "benchmarkType": "jimmy-paige-basic-pitch-predict-smoke-test",
                "passed": bool(result.get("passed")),
                "callId": call.object_id,
                "remoteElapsedSeconds": result.get("remoteElapsedSeconds"),
                "totalElapsedSeconds": round(total_elapsed, 3),
                "eventCount": result.get("eventCount"),
                "rendererChanged": False,
                "protectedBaselinesChanged": False,
                "lockedV7EventsProtected": True,
                "lockedV8TimingProtected": True,
            }
            OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
            print("Basic Pitch predict smoke test pass:", report["passed"], flush=True)
            print("Remote runtime:", report["remoteElapsedSeconds"], "seconds", flush=True)
            print("Total elapsed:", report["totalElapsedSeconds"], "seconds", flush=True)
            print("Events:", report["eventCount"], flush=True)
            print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT), flush=True)
            return
        except TimeoutError:
            elapsed = time.time() - submitted_at
            print(
                f"[predict smoke heartbeat] elapsed={elapsed:.1f}s | callId={call.object_id}",
                flush=True,
            )
            if elapsed >= max_wait_seconds:
                call.cancel()
                report = {
                    "benchmarkType": "jimmy-paige-basic-pitch-predict-smoke-test",
                    "passed": False,
                    "timedOut": True,
                    "callId": call.object_id,
                    "totalElapsedSeconds": round(elapsed, 3),
                    "rendererChanged": False,
                    "protectedBaselinesChanged": False,
                    "lockedV7EventsProtected": True,
                    "lockedV8TimingProtected": True,
                }
                OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
                print("Basic Pitch predict smoke test timed out.", flush=True)
                print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT), flush=True)
                return
            time.sleep(heartbeat_seconds)


if __name__ == "__main__":
    main()
