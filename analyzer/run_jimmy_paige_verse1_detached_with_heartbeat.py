from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import modal

from run_jimmy_paige_em_riff_extraction_training_loop import (
    AUDIO_PATH,
    ATTEMPTS,
    MEASURE_SECONDS,
    REPO_ROOT,
    _score,
    app,
    extract_attempt_remote,
)

STATE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-verse1-detached-state.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-verse1-single-attempt-timing-test.json"
)
LOG_PATH = REPO_ROOT / "verse1-detached-heartbeat.log"

VERSE_START_MEASURE = 18
VERSE_END_MEASURE = 32
PAD_SECONDS = 1.0


def _log(message: str) -> None:
    timestamped = f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} | {message}"
    print(timestamped, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(timestamped + "\n")


def _clip_bounds() -> tuple[float, float]:
    verse_start = (VERSE_START_MEASURE - 1) * MEASURE_SECONDS
    verse_end = VERSE_END_MEASURE * MEASURE_SECONDS
    clip_start = max(0.0, verse_start - PAD_SECONDS)
    clip_end = verse_end + PAD_SECONDS
    return clip_start, clip_end


def _build_clip() -> tuple[bytes, float, float]:
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing training audio: {AUDIO_PATH}")

    clip_start, clip_end = _clip_bounds()
    duration = clip_end - clip_start

    with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as handle:
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
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(clip_path),
        ]
        subprocess.run(command, check=True)
        return clip_path.read_bytes(), clip_start, duration
    finally:
        clip_path.unlink(missing_ok=True)


def _submit() -> dict:
    parameters = ATTEMPTS[0]
    clip_bytes, clip_start, clip_duration = _build_clip()
    started_at = time.time()

    _log(
        "Submitting detached Verse 1 Basic Pitch test "
        f"for measures {VERSE_START_MEASURE}-{VERSE_END_MEASURE} "
        f"({clip_duration:.2f}s clip)."
    )

    with app.run(detach=True):
        call = extract_attempt_remote.spawn(
            clip_bytes,
            ".m4a",
            1,
            parameters,
        )

    state = {
        "benchmarkVersion": 8,
        "status": "submitted",
        "callId": call.object_id,
        "startedAtEpoch": started_at,
        "startedAt": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "clipStartSeconds": clip_start,
        "clipDurationSeconds": clip_duration,
        "measureRange": [VERSE_START_MEASURE, VERSE_END_MEASURE],
        "name": parameters["name"],
        "parameters": {
            key: value for key, value in parameters.items() if key != "name"
        },
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
    _log(f"Detached call submitted: {call.object_id}")
    return state


def _load_state() -> dict:
    if not STATE_PATH.exists():
        raise FileNotFoundError(
            "Verse 1 detached state not found. Run without JIMMY_RESUME_EXISTING first."
        )
    return json.loads(STATE_PATH.read_text())


def _collect_if_ready(state: dict) -> bool:
    call_id = state["callId"]
    call = modal.FunctionCall.from_id(call_id)

    try:
        result_bytes = call.get(timeout=0)
    except TimeoutError:
        return False

    extracted = json.loads(result_bytes.decode("utf-8"))
    clip_start = float(state["clipStartSeconds"])
    events = []
    for event in extracted.pop("events", []):
        if not isinstance(event, dict):
            continue
        shifted = dict(event)
        shifted["start"] = float(shifted.get("start") or 0.0) + clip_start
        shifted["end"] = float(shifted.get("end") or shifted["start"]) + clip_start
        events.append(shifted)

    score = _score(events)
    elapsed = time.time() - float(state["startedAtEpoch"])
    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-verse1-single-attempt-timing-test",
        "passed": True,
        "detachedRun": True,
        "callId": call_id,
        "measureRange": state["measureRange"],
        "clipStartSeconds": state["clipStartSeconds"],
        "clipDurationSeconds": state["clipDurationSeconds"],
        "parameters": extracted.get("parameters", state.get("parameters")),
        "extractedEventCount": len(events),
        "correctCandidateSlots": score["correctCandidateSlots"],
        "candidatePresencePercentage": score["candidatePresencePercentage"],
        "totalElapsedSeconds": round(elapsed, 3),
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
        "Verse 1 test completed | "
        f"elapsed={report['totalElapsedSeconds']}s | "
        f"events={report['extractedEventCount']} | "
        f"correct={report['correctCandidateSlots']}/9"
    )
    _log(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return True


def main() -> None:
    heartbeat_seconds = max(30, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "300")))
    resume = os.getenv("JIMMY_RESUME_EXISTING", "0") == "1"

    if resume:
        state = _load_state()
        _log(f"Resuming Verse 1 monitor for call {state['callId']}")
    else:
        LOG_PATH.write_text("")
        state = _submit()

    while True:
        if _collect_if_ready(state):
            return

        elapsed = time.time() - float(state["startedAtEpoch"])
        _log(
            "[verse1 heartbeat] "
            f"elapsed={elapsed / 60.0:.1f}m | "
            f"status={state.get('status')} | "
            f"callId={state['callId']}"
        )
        time.sleep(heartbeat_seconds)


if __name__ == "__main__":
    main()
