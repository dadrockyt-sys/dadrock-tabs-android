from __future__ import annotations

import json
import os
import time
from pathlib import Path

import modal
import modal_analyzer_v7 as protected_analyzer

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-basic-pitch-image-smoke-test.json"
)

app = modal.App("dadrock-v8-basic-pitch-image-smoke-test")


@app.function(
    image=protected_analyzer.image,
    timeout=600,
    memory=4096,
)
def basic_pitch_image_smoke_remote() -> dict:
    import inspect
    import platform
    import time as remote_time

    started = remote_time.time()

    from basic_pitch.inference import predict

    return {
        "workerStarted": True,
        "basicPitchImported": True,
        "pythonVersion": platform.python_version(),
        "predictSignature": str(inspect.signature(predict)),
        "remoteRuntimeSeconds": round(remote_time.time() - started, 3),
    }


def main() -> None:
    heartbeat_seconds = max(
        5,
        int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")),
    )
    max_wait_seconds = max(
        heartbeat_seconds,
        int(os.getenv("JIMMY_SMOKE_MAX_WAIT_SECONDS", "900")),
    )

    submitted_at = time.time()
    print("Jimmy PAIge Basic Pitch image smoke test", flush=True)
    print("Submitting same protected analyzer image...", flush=True)

    with app.run(detach=True):
        call = basic_pitch_image_smoke_remote.spawn()

    print("Call ID:", call.object_id, flush=True)

    while True:
        elapsed = time.time() - submitted_at

        try:
            remote_result = call.get(timeout=0)
        except TimeoutError:
            if elapsed >= max_wait_seconds:
                call.cancel()
                report = {
                    "benchmarkVersion": 8,
                    "benchmarkType": "jimmy-paige-basic-pitch-image-smoke-test",
                    "passed": False,
                    "timedOut": True,
                    "callId": call.object_id,
                    "elapsedSeconds": round(elapsed, 3),
                    "productionPromotionAllowed": False,
                    "rendererChanged": False,
                    "protectedBaselinesChanged": False,
                }
                OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
                print("Basic Pitch image smoke test timed out.")
                print("This isolates the delay to the protected image/import path.")
                print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
                raise SystemExit(1)

            print(
                "[basic-pitch image heartbeat] "
                f"elapsed={elapsed:.1f}s | "
                f"callId={call.object_id} | "
                "waiting-for-image-worker-or-import",
                flush=True,
            )
            time.sleep(heartbeat_seconds)
            continue

        total_elapsed = time.time() - submitted_at
        queue_and_start_delay = max(
            0.0,
            total_elapsed - float(remote_result["remoteRuntimeSeconds"]),
        )
        report = {
            "benchmarkVersion": 8,
            "benchmarkType": "jimmy-paige-basic-pitch-image-smoke-test",
            "passed": bool(
                remote_result.get("workerStarted")
                and remote_result.get("basicPitchImported")
            ),
            "callId": call.object_id,
            "queueAndImageStartSeconds": round(queue_and_start_delay, 3),
            "remoteImportRuntimeSeconds": remote_result["remoteRuntimeSeconds"],
            "totalElapsedSeconds": round(total_elapsed, 3),
            "pythonVersion": remote_result["pythonVersion"],
            "predictSignature": remote_result["predictSignature"],
            "productionPromotionAllowed": False,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
            "lockedV7EventsProtected": True,
            "lockedV8TimingProtected": True,
        }
        OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

        print("Basic Pitch image smoke test pass:", report["passed"])
        print(
            "Queue + protected-image startup:",
            report["queueAndImageStartSeconds"],
            "seconds",
        )
        print(
            "Basic Pitch import runtime:",
            report["remoteImportRuntimeSeconds"],
            "seconds",
        )
        print("Total elapsed:", report["totalElapsedSeconds"], "seconds")
        print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
        return


if __name__ == "__main__":
    main()
