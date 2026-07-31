from __future__ import annotations

import json
import time
from pathlib import Path

from run_jimmy_paige_em_riff_extraction_training_loop import (
    AUDIO_PATH,
    ATTEMPTS,
    REPO_ROOT,
    _score,
    app,
    extract_attempt_remote,
)

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-em-riff-single-attempt-timing-test.json"
)


def main() -> None:
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing training audio: {AUDIO_PATH}")

    parameters = ATTEMPTS[0]
    started_at = time.time()

    print("Jimmy PAIge single-attempt timing test", flush=True)
    print("Attempt: default", flush=True)
    print("Full training audio:", AUDIO_PATH.relative_to(REPO_ROOT), flush=True)
    print("Started:", time.strftime("%Y-%m-%d %H:%M:%S %Z"), flush=True)

    with app.run():
        print("[trainer] Modal session ready; starting full Basic Pitch run", flush=True)
        attempt_started = time.time()
        result_bytes = extract_attempt_remote.remote(
            AUDIO_PATH.read_bytes(),
            AUDIO_PATH.suffix,
            1,
            parameters,
        )
        remote_elapsed = time.time() - attempt_started

    extracted = json.loads(result_bytes.decode("utf-8"))
    events = [event for event in extracted.pop("events", []) if isinstance(event, dict)]
    score = _score(events)
    total_elapsed = time.time() - started_at

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-em-riff-single-full-run-timing-test",
        "passed": True,
        "attempt": 1,
        "name": parameters["name"],
        "parameters": {
            key: value for key, value in parameters.items() if key != "name"
        },
        "fullSongAudio": True,
        "extractedEventCount": len(events),
        "correctCandidateSlots": score["correctCandidateSlots"],
        "candidatePresencePercentage": score["candidatePresencePercentage"],
        "remoteAttemptElapsedSeconds": round(remote_elapsed, 3),
        "totalElapsedSeconds": round(total_elapsed, 3),
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "lockedV7EventsProtected": True,
        "lockedV8TimingProtected": True,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print(
        "[trainer] completed full attempt | "
        f"correct={report['correctCandidateSlots']}/9 | "
        f"events={report['extractedEventCount']} | "
        f"remoteElapsed={report['remoteAttemptElapsedSeconds']}s | "
        f"totalElapsed={report['totalElapsedSeconds']}s",
        flush=True,
    )
    print("Production promotion allowed: False", flush=True)
    print("Renderer changed: False", flush=True)
    print("Protected baselines changed: False", flush=True)
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT), flush=True)


if __name__ == "__main__":
    main()
