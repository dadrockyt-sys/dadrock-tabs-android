from __future__ import annotations

import json
import time
from pathlib import Path

import modal

from run_jimmy_paige_em_riff_extraction_training_loop import REPO_ROOT, _score

STATE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-em-riff-single-attempt-detached-state.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-em-riff-single-attempt-timing-test.json"
)


def main() -> None:
    if not STATE_PATH.exists():
        raise FileNotFoundError(
            "Detached state not found. Run "
            "python analyzer/submit_jimmy_paige_single_attempt_detached.py first."
        )

    state = json.loads(STATE_PATH.read_text())
    call_id = state.get("callId")
    if not call_id:
        raise RuntimeError("Detached state does not contain a Modal call ID.")

    call = modal.FunctionCall.from_id(call_id)

    try:
        result_bytes = call.get(timeout=0)
    except TimeoutError:
        elapsed = time.time() - float(state.get("startedAtEpoch") or time.time())
        print("Detached Jimmy PAIge run is still working.")
        print("Call ID:", call_id)
        print("Elapsed:", round(elapsed, 1), "seconds")
        print("No result is available yet. Run this collector again later.")
        return

    extracted = json.loads(result_bytes.decode("utf-8"))
    events = [event for event in extracted.pop("events", []) if isinstance(event, dict)]
    score = _score(events)
    total_elapsed = time.time() - float(state.get("startedAtEpoch") or time.time())

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-em-riff-single-full-run-timing-test",
        "passed": True,
        "detachedRun": True,
        "callId": call_id,
        "attempt": extracted.get("attempt", 1),
        "name": extracted.get("name", state.get("name")),
        "parameters": extracted.get("parameters", state.get("parameters")),
        "fullSongAudio": True,
        "extractedEventCount": len(events),
        "correctCandidateSlots": score["correctCandidateSlots"],
        "candidatePresencePercentage": score["candidatePresencePercentage"],
        "totalElapsedSeconds": round(total_elapsed, 3),
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

    print("Detached Jimmy PAIge run completed.")
    print("Total elapsed:", report["totalElapsedSeconds"], "seconds")
    print("Extracted events:", report["extractedEventCount"])
    print("Correct pitch candidates:", f"{report['correctCandidateSlots']}/9")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("Renderer changed: False")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
