from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import run_jimmy_paige_verse1_detached_with_heartbeat as verse1


def _build_wav_clip() -> tuple[bytes, float, float]:
    """Build an audio-only PCM WAV clip so ffmpeg ignores embedded H.264 artwork/video."""
    if not verse1.AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing training audio: {verse1.AUDIO_PATH}")

    clip_start, clip_end = verse1._clip_bounds()
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
            str(verse1.AUDIO_PATH),
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


def _submit_wav() -> dict:
    parameters = verse1.ATTEMPTS[0]
    clip_bytes, clip_start, clip_duration = _build_wav_clip()
    started_at = verse1.time.time()

    verse1._log(
        "Submitting detached Verse 1 Basic Pitch WAV test "
        f"for measures {verse1.VERSE_START_MEASURE}-{verse1.VERSE_END_MEASURE} "
        f"({clip_duration:.2f}s clip)."
    )

    with verse1.app.run(detach=True):
        call = verse1.extract_attempt_remote.spawn(
            clip_bytes,
            ".wav",
            1,
            parameters,
        )

    state = {
        "benchmarkVersion": 8,
        "status": "submitted",
        "callId": call.object_id,
        "startedAtEpoch": started_at,
        "startedAt": verse1.time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "clipStartSeconds": clip_start,
        "clipDurationSeconds": clip_duration,
        "clipFormat": "wav-pcm-s16le-mono-22050",
        "measureRange": [verse1.VERSE_START_MEASURE, verse1.VERSE_END_MEASURE],
        "name": parameters["name"],
        "parameters": {
            key: value for key, value in parameters.items() if key != "name"
        },
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    verse1.STATE_PATH.write_text(verse1.json.dumps(state, indent=2) + "\n")
    verse1._log(f"Detached call submitted: {call.object_id}")
    return state


if __name__ == "__main__":
    verse1._build_clip = _build_wav_clip
    verse1._submit = _submit_wav
    verse1.main()
