from __future__ import annotations

import json
import time
from pathlib import Path

from run_jimmy_paige_em_riff_extraction_training_loop import (
    AUDIO_PATH,
    ATTEMPTS,
    REPO_ROOT,
    app,
    extract_attempt_remote,
)

STATE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-em-riff-single-attempt-detached-state.json"
)


def main() -> None:
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing training audio: {AUDIO_PATH}")

    parameters = ATTEMPTS[0]
    started_at = time.time()

    print("Submitting detached Jimmy PAIge full-song timing run...", flush=True)

    with app.run(detach=True):
        call = extract_attempt_remote.spawn(
            AUDIO_PATH.read_bytes(),
            AUDIO_PATH.suffix,
            1,
            parameters,
        )

    state = {
        "benchmarkVersion": 8,
        "status": "submitted",
        "callId": call.object_id,
        "startedAtEpoch": started_at,
        "startedAt": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "attempt": 1,
        "name": parameters["name"],
        "parameters": {
            key: value for key, value in parameters.items() if key != "name"
        },
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")

    print("Detached run submitted successfully.")
    print("Call ID:", call.object_id)
    print("State:", STATE_PATH.relative_to(REPO_ROOT))
    print("The Modal job can continue after Codespaces disconnects.")
    print(
        "Check later with: python analyzer/collect_jimmy_paige_single_attempt_detached.py"
    )


if __name__ == "__main__":
    main()
