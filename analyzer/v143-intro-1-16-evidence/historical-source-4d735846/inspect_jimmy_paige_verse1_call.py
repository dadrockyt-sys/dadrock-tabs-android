from __future__ import annotations

import json
import time
from pathlib import Path

import modal

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-verse1-detached-state.json"
)


def main() -> None:
    if not STATE_PATH.exists():
        raise FileNotFoundError(
            "Verse 1 detached state not found. Start the Verse 1 detached test first."
        )

    state = json.loads(STATE_PATH.read_text())
    call_id = state.get("callId")
    if not call_id:
        raise RuntimeError("Verse 1 detached state does not contain a Modal call ID.")

    elapsed = time.time() - float(state.get("startedAtEpoch") or time.time())
    call = modal.FunctionCall.from_id(call_id)

    print("Jimmy PAIge Verse 1 detached call inspection")
    print("Call ID:", call_id)
    print("Saved status:", state.get("status"))
    print("Elapsed:", round(elapsed, 1), "seconds")
    print("Measure range:", state.get("measureRange"))
    print("Clip duration:", state.get("clipDurationSeconds"), "seconds")

    print("\n===== CALL GRAPH / STATE =====")
    try:
        graph = call.get_call_graph()
        if not graph:
            print("No call graph entries returned.")
        else:
            for index, item in enumerate(graph, start=1):
                values = []
                for key in (
                    "input_id",
                    "function_call_id",
                    "task_id",
                    "status",
                    "function_name",
                    "module_name",
                ):
                    value = getattr(item, key, None)
                    values.append(f"{key}={value}")
                print(f"{index}. " + " | ".join(values))
    except Exception as exc:
        print("Call graph unavailable:", type(exc).__name__, str(exc))

    print("\n===== RECENT CALL LOGS =====")
    try:
        logs = []
        tail = getattr(getattr(call, "logs", None), "tail", None)
        if callable(tail):
            for entry in tail():
                logs.append(str(entry))
                if len(logs) >= 100:
                    break
        if logs:
            for entry in logs[-100:]:
                print(entry.rstrip())
        else:
            print("No recent log entries returned.")
    except Exception as exc:
        print("Per-call logs unavailable:", type(exc).__name__, str(exc))
        print(
            "Fallback: modal app logs dadrock-v8-em-riff-extraction-training "
            f"--function-call {call_id} --timestamps"
        )

    print("\n===== RESULT POLL =====")
    try:
        result = call.get(timeout=0)
    except TimeoutError:
        print("Result status: still running or queued")
    except Exception as exc:
        print("Result status: failed or cancelled")
        print(type(exc).__name__ + ":", str(exc))
    else:
        size = len(result) if isinstance(result, (bytes, bytearray)) else None
        print("Result status: complete")
        print("Result bytes:", size)


if __name__ == "__main__":
    main()
