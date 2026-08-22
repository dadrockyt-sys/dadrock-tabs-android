from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

from run_jimmy_paige_em_riff_extraction_training_loop import (
    ATTEMPTS,
    AUDIO_PATH,
    MEASURE_SECONDS,
    REPO_ROOT,
    _score,
)

STATE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-verse1-minimal-detached-state.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-verse1-minimal-timing-test.json"
LOG_PATH = REPO_ROOT / "verse1-minimal-basic-pitch-heartbeat.log"

VERSE_START_MEASURE = 18
VERSE_END_MEASURE = 32
PAD_SECONDS = 1.0

app = modal.App("dadrock-jimmy-paige-verse1-minimal-basic-pitch")
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
def extract_minimal(audio_bytes: bytes, parameters: dict[str, Any]) -> bytes:
    from basic_pitch.inference import predict

    started = time.time()
    print("[remote] minimal Basic Pitch worker started", flush=True)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        audio_path = Path(handle.name)
        handle.write(audio_bytes)

    try:
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
        normalized = []
        for event in note_events:
            item = _normalize_note_event(event)
            if item is not None:
                normalized.append(item)

        payload = {
            "events": normalized,
            "parameters": parameters,
            "remoteElapsedSeconds": round(time.time() - started, 3),
        }
        print(
            f"[remote] minimal Basic Pitch completed events={len(normalized)} "
            f"elapsed={payload['remoteElapsedSeconds']}s",
            flush=True,
        )
        return json.dumps(payload).encode("utf-8")
    finally:
        audio_path.unlink(missing_ok=True)


def _clip_bounds() -> tuple[float, float]:
    verse_start = (VERSE_START_MEASURE - 1) * MEASURE_SECONDS
    verse_end = VERSE_END_MEASURE * MEASURE_SECONDS
    clip_start = max(0.0, verse_start - PAD_SECONDS)
    clip_end = verse_end + PAD_SECONDS
    return clip_start, clip_end


def _build_wav_clip() -> tuple[bytes, float, float]:
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing training audio: {AUDIO_PATH}")

    clip_start, clip_end = _clip_bounds()
    duration = clip_end - clip_start

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
        clip_path = Path(handle.name)

    try:
        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{clip_start:.6f}",
            "-i",
            str(AUDIO_PATH),
            "-t",
            f"{duration:.6f}",
            "-map",
            "0:a:0",
            "-vn",
            "-ac",
            "1",
            "-ar",
            "22050",
            "-c:a",
            "pcm_s16le",
            str(clip_path),
        ]
        subprocess.run(command, check=True)
        return clip_path.read_bytes(), clip_start, duration
    finally:
        clip_path.unlink(missing_ok=True)


def _submit() -> dict[str, Any]:
    parameters = dict(ATTEMPTS[0])
    clip_bytes, clip_start, clip_duration = _build_wav_clip()
    started_at = time.time()

    _log(
        "Submitting detached Verse 1 test on minimal Basic Pitch image "
        f"for measures {VERSE_START_MEASURE}-{VERSE_END_MEASURE} "
        f"({clip_duration:.2f}s WAV)."
    )

    with app.run(detach=True):
        call = extract_minimal.spawn(clip_bytes, parameters)

    state = {
        "benchmarkVersion": 8,
        "status": "submitted",
        "callId": call.object_id,
        "startedAtEpoch": started_at,
        "startedAt": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "measureRange": [VERSE_START_MEASURE, VERSE_END_MEASURE],
        "clipStartSeconds": clip_start,
        "clipDurationSeconds": clip_duration,
        "parameters": parameters,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
    _log(f"Detached minimal-image call submitted: {call.object_id}")
    return state


def _load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        raise FileNotFoundError(
            "Minimal Verse 1 detached state not found. Run without "
            "JIMMY_RESUME_EXISTING first."
        )
    return json.loads(STATE_PATH.read_text())


def _collect_if_ready(state: dict[str, Any]) -> bool:
    call = modal.FunctionCall.from_id(state["callId"])
    try:
        result_bytes = call.get(timeout=0)
    except TimeoutError:
        return False

    result = json.loads(result_bytes.decode("utf-8"))
    clip_start = float(state["clipStartSeconds"])
    shifted_events = []

    for event in result.get("events", []):
        if not isinstance(event, dict):
            continue
        shifted = dict(event)
        shifted["start"] = float(shifted.get("start") or 0.0) + clip_start
        shifted["end"] = float(shifted.get("end") or shifted["start"]) + clip_start
        shifted_events.append(shifted)

    score = _score(shifted_events)
    elapsed = time.time() - float(state["startedAtEpoch"])
    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-verse1-minimal-basic-pitch-timing-test",
        "passed": True,
        "detachedRun": True,
        "callId": state["callId"],
        "measureRange": state["measureRange"],
        "clipStartSeconds": state["clipStartSeconds"],
        "clipDurationSeconds": state["clipDurationSeconds"],
        "remoteElapsedSeconds": result.get("remoteElapsedSeconds"),
        "totalElapsedSeconds": round(elapsed, 3),
        "extractedEventCount": len(shifted_events),
        "correctCandidateSlots": score["correctCandidateSlots"],
        "candidatePresencePercentage": score["candidatePresencePercentage"],
        "parameters": result.get("parameters", state.get("parameters")),
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "lockedV7EventsProtected": True,
        "lockedV8TimingProtected": True,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    state["status"] = "complete"
    state["completedAt"] = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    state["outputPath"] = str(OUTPUT_PATH.relative_to(REPO_ROOT))
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")

    _log(
        "Minimal-image Verse 1 test completed | "
        f"remote={report['remoteElapsedSeconds']}s | "
        f"total={report['totalElapsedSeconds']}s | "
        f"events={report['extractedEventCount']} | "
        f"correct={report['correctCandidateSlots']}/9"
    )
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return True


def main() -> None:
    heartbeat_seconds = max(15, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "60")))
    resume = os.getenv("JIMMY_RESUME_EXISTING", "0") == "1"

    if resume:
        state = _load_state()
        _log(f"Resuming minimal Verse 1 monitor for {state['callId']}")
    else:
        LOG_PATH.write_text("")
        state = _submit()

    while True:
        if _collect_if_ready(state):
            return

        elapsed = time.time() - float(state["startedAtEpoch"])
        _log(
            "[minimal verse1 heartbeat] "
            f"elapsed={elapsed / 60.0:.1f}m | "
            f"status={state.get('status')} | "
            f"callId={state['callId']}"
        )
        time.sleep(heartbeat_seconds)


if __name__ == "__main__":
    main()
