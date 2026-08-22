from __future__ import annotations

import json
import os
import time
from pathlib import Path

import modal

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-minimal-basic-pitch-image-smoke-test.json"
)

app = modal.App("dadrock-jimmy-paige-minimal-basic-pitch-smoke")

# Deliberately isolated from modal_analyzer_v7.image.
# This proves whether a clean Basic Pitch-only image can start and import.
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("basic-pitch")
)


@app.function(image=image, timeout=900, memory=4096)
def minimal_basic_pitch_import_smoke() -> dict:
    started = time.time()
    from basic_pitch.inference import predict  # noqa: F401

    return {
        "remoteImportElapsedSeconds": round(time.time() - started, 3),
        "imported": True,
    }


def main() -> None:
    heartbeat_seconds = max(
        10,
        int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")),
    )
    max_wait_seconds = max(
        60,
        int(os.getenv("JIMMY_SMOKE_MAX_WAIT_SECONDS", "900")),
    )

    submitted_at = time.time()
    print("Jimmy PAIge minimal Basic Pitch image smoke test", flush=True)
    print("Submitting clean Basic Pitch-only image test...", flush=True)

    with app.run(detach=True):
        call = minimal_basic_pitch_import_smoke.spawn()

    print(f"Call ID: {call.object_id}", flush=True)

    while True:
        elapsed = time.time() - submitted_at

        try:
            result = call.get(timeout=0)
        except TimeoutError:
            if elapsed >= max_wait_seconds:
                call.cancel()
                report = {
                    "benchmarkVersion": 8,
                    "benchmarkType": (
                        "jimmy-paige-minimal-basic-pitch-image-smoke-test"
                    ),
                    "passed": False,
                    "timedOut": True,
                    "callId": call.object_id,
                    "elapsedSeconds": round(elapsed, 3),
                    "diagnosis": (
                        "minimal-basic-pitch-image-or-import-timeout"
                    ),
                    "productionPromotionAllowed": False,
                    "rendererChanged": False,
                    "protectedBaselinesChanged": False,
                }
                OUTPUT_PATH.write_text(
                    json.dumps(report, indent=2) + "\n"
                )
                print(
                    "Minimal Basic Pitch image smoke test timed out.",
                    flush=True,
                )
                print(
                    "This means Basic Pitch installation/image startup itself "
                    "is the bottleneck.",
                    flush=True,
                )
                print(
                    f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}",
                    flush=True,
                )
                raise SystemExit(1)

            print(
                "[minimal-basic-pitch heartbeat] "
                f"elapsed={elapsed:.1f}s | "
                f"callId={call.object_id} | "
                "waiting-for-clean-image-worker-or-import",
                flush=True,
            )
            time.sleep(heartbeat_seconds)
            continue

        total_elapsed = time.time() - submitted_at
        report = {
            "benchmarkVersion": 8,
            "benchmarkType": (
                "jimmy-paige-minimal-basic-pitch-image-smoke-test"
            ),
            "passed": bool(result.get("imported")),
            "timedOut": False,
            "callId": call.object_id,
            "queueImageAndImportElapsedSeconds": round(total_elapsed, 3),
            "remoteImportElapsedSeconds": result.get(
                "remoteImportElapsedSeconds"
            ),
            "diagnosis": "minimal-basic-pitch-image-healthy",
            "productionPromotionAllowed": False,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
        }
        OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

        print(
            "Minimal Basic Pitch image smoke test pass: "
            f"{report['passed']}",
            flush=True,
        )
        print(
            "Queue + clean image + import: "
            f"{report['queueImageAndImportElapsedSeconds']} seconds",
            flush=True,
        )
        print(
            "Remote Basic Pitch import runtime: "
            f"{report['remoteImportElapsedSeconds']} seconds",
            flush=True,
        )
        print(
            f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}",
            flush=True,
        )
        return


if __name__ == "__main__":
    main()
