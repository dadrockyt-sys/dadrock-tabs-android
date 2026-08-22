from __future__ import annotations

import json
import os
import time
from pathlib import Path

import modal

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-modal-worker-smoke-test.json"

app = modal.App("dadrock-jimmy-paige-worker-smoke-test")
image = modal.Image.debian_slim(python_version="3.11")


@app.function(image=image, timeout=300)
def worker_smoke_test(submitted_at: float) -> dict:
    import os
    import socket
    import time

    started_at = time.time()
    print("[remote smoke] worker started", flush=True)
    print(f"[remote smoke] hostname={socket.gethostname()}", flush=True)
    print(f"[remote smoke] pid={os.getpid()}", flush=True)
    time.sleep(2)
    finished_at = time.time()
    print("[remote smoke] worker finished", flush=True)

    return {
        "workerStarted": True,
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "queueDelaySeconds": round(started_at - submitted_at, 3),
        "remoteRuntimeSeconds": round(finished_at - started_at, 3),
        "remoteFinishedAtEpoch": finished_at,
    }


def main() -> None:
    heartbeat_seconds = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    max_wait_seconds = max(30, int(os.getenv("JIMMY_SMOKE_MAX_WAIT_SECONDS", "600")))

    submitted_at = time.time()
    print("Jimmy PAIge Modal worker smoke test", flush=True)
    print("Submitting tiny worker-start test...", flush=True)

    with app.run(detach=True):
        call = worker_smoke_test.spawn(submitted_at)

    call_id = call.object_id
    print("Call ID:", call_id, flush=True)

    while True:
        elapsed = time.time() - submitted_at

        try:
            result = call.get(timeout=0)
        except TimeoutError:
            if elapsed >= max_wait_seconds:
                report = {
                    "benchmarkVersion": 8,
                    "benchmarkType": "jimmy-paige-modal-worker-smoke-test",
                    "passed": False,
                    "status": "timed-out-waiting-for-worker",
                    "callId": call_id,
                    "elapsedSeconds": round(elapsed, 3),
                    "workerStarted": False,
                    "rendererChanged": False,
                    "protectedBaselinesChanged": False,
                }
                OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
                print("Smoke test timed out waiting for a Modal worker.", flush=True)
                print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT), flush=True)
                raise SystemExit(1)

            print(
                "[worker heartbeat] "
                f"elapsed={elapsed:.1f}s | callId={call_id} | waiting-for-worker-or-result",
                flush=True,
            )
            time.sleep(heartbeat_seconds)
            continue

        total_elapsed = time.time() - submitted_at
        report = {
            "benchmarkVersion": 8,
            "benchmarkType": "jimmy-paige-modal-worker-smoke-test",
            "passed": bool(result.get("workerStarted")),
            "status": "complete",
            "callId": call_id,
            "totalElapsedSeconds": round(total_elapsed, 3),
            **result,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
            "lockedV7EventsProtected": True,
            "lockedV8TimingProtected": True,
        }
        OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

        print("Modal worker smoke test pass:", report["passed"], flush=True)
        print("Queue delay:", report["queueDelaySeconds"], "seconds", flush=True)
        print("Remote runtime:", report["remoteRuntimeSeconds"], "seconds", flush=True)
        print("Total elapsed:", report["totalElapsedSeconds"], "seconds", flush=True)
        print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT), flush=True)
        return


if __name__ == "__main__":
    main()
