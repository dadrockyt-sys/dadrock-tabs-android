from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIO_PATH = REPO_ROOT / "public" / "DadRock TABS - gomyway2test.m4a"
STATE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-v7-snippet-detached-state.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-v7-snippet-minimal-test.json"
LOG_PATH = REPO_ROOT / "v7-snippet-minimal-basic-pitch-heartbeat.log"

app = modal.App("dadrock-jimmy-paige-v7-snippet-minimal-basic-pitch")
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


@app.function(image=image, timeout=900, memory=4096)
def extract_snippet(audio_bytes: bytes) -> bytes:
    from basic_pitch.inference import predict

    started = time.time()
    print("[remote] V7 snippet Basic Pitch worker started", flush=True)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        audio_path = Path(handle.name)
        handle.write(audio_bytes)

    try:
        _, _, note_events = predict(
            audio_path,
            onset_threshold=0.50,
            frame_threshold=0.30,
            minimum_note_length=127.7,
            multiple_pitch_bends=False,
            melodia_trick=True,
        )

        events = []
        for event in note_events:
            normalized = _normalize_note_event(event)
            if normalized is not None:
                events.append(normalized)

        payload = {
            "events": events,
            "remoteElapsedSeconds": round(time.time() - started, 3),
        }
        print(
            f"[remote] V7 snippet completed events={len(events)} "
            f"elapsed={payload['remoteElapsedSeconds']}s",
            flush=True,
        )
        return json.dumps(payload).encode("utf-8")
    finally:
        audio_path.unlink(missing_ok=True)


def _build_audio_only_wav() -> bytes:
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing V7 training snippet: {AUDIO_PATH}")

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
                str(AUDIO_PATH),
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


def _submit() -> dict[str, Any]:
    audio_bytes = _build_audio_only_wav()
    started_at = time.time()

    _log(
        "Submitting proven V7 training snippet on the minimal Basic Pitch image "
        f"({len(audio_bytes) / 1024 / 1024:.2f} MiB WAV payload)."
    )

    with app.run(detach=True):
        call = extract_snippet.spawn(audio_bytes)

    state = {
        "benchmarkVersion": 8,
        "status": "submitted",
        "callId": call.object_id,
        "startedAtEpoch": started_at,
        "sourceAudio": str(AUDIO_PATH.relative_to(REPO_ROOT)),
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
    _log(f"Detached V7-snippet call submitted: {call.object_id}")
    return state


def _load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        raise FileNotFoundError("No V7-snippet detached state file exists yet.")
    return json.loads(STATE_PATH.read_text())


def _collect_if_ready(state: dict[str, Any]) -> bool:
    call = modal.FunctionCall.from_id(state["callId"])
    try:
        result_bytes = call.get(timeout=0)
    except TimeoutError:
        return False

    result = json.loads(result_bytes.decode("utf-8"))
    elapsed = time.time() - float(state["startedAtEpoch"])
    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-v7-snippet-minimal-basic-pitch-test",
        "passed": True,
        "sourceAudio": state["sourceAudio"],
        "callId": state["callId"],
        "remoteElapsedSeconds": result.get("remoteElapsedSeconds"),
        "totalElapsedSeconds": round(elapsed, 3),
        "extractedEventCount": len(result.get("events", [])),
        "events": result.get("events", []),
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "lockedV7EventsProtected": True,
        "lockedV8TimingProtected": True,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    state["status"] = "complete"
    state["outputPath"] = str(OUTPUT_PATH.relative_to(REPO_ROOT))
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")

    _log(
        "V7-snippet minimal-image test completed | "
        f"remote={report['remoteElapsedSeconds']}s | "
        f"total={report['totalElapsedSeconds']}s | "
        f"events={report['extractedEventCount']}"
    )
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return True


def main() -> None:
    heartbeat_seconds = max(10, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "30")))
    resume = os.getenv("JIMMY_RESUME_EXISTING", "0") == "1"

    if resume:
        state = _load_state()
        _log(f"Resuming V7-snippet monitor for {state['callId']}")
    else:
        LOG_PATH.write_text("")
        state = _submit()

    while True:
        if _collect_if_ready(state):
            return

        elapsed = time.time() - float(state["startedAtEpoch"])
        _log(
            "[V7 snippet heartbeat] "
            f"elapsed={elapsed:.1f}s | "
            f"status={state.get('status')} | "
            f"callId={state['callId']}"
        )
        time.sleep(heartbeat_seconds)


if __name__ == "__main__":
    main()
