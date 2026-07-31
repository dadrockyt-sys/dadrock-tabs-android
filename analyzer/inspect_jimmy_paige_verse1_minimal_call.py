from __future__ import annotations

import json
from pathlib import Path

import modal

STATE_PATH = Path(
    "public/gomyway-jimmy-paige-verse1-minimal-detached-state.json"
)


def main() -> None:
    if not STATE_PATH.exists():
        raise FileNotFoundError(
            f"Missing detached state file: {STATE_PATH}"
        )

    state = json.loads(STATE_PATH.read_text())
    call_id = state["callId"]
    call = modal.FunctionCall.from_id(call_id)

    print("Jimmy PAIge minimal Verse 1 call inspection")
    print("Call ID:", call_id)
    print("Saved status:", state.get("status"))

    print("\n===== CALL GRAPH =====")
    graph = call.get_call_graph()
    if not graph:
        print("No call-graph entries returned.")
    else:
        for item in graph:
            print(
                "function_call_id=",
                getattr(item, "function_call_id", None),
                "| task_id=",
                getattr(item, "task_id", None),
                "| status=",
                getattr(item, "status", None),
                "| function_name=",
                getattr(item, "function_name", None),
            )

    print("\n===== RECENT LOGS =====")
    try:
        found = False
        for line in call.logs.tail(timeout=3):
            print(line, end="" if line.endswith("\n") else "\n")
            found = True
        if not found:
            print("No recent logs returned.")
    except Exception as error:
        print("Log inspection unavailable:", repr(error))

    print("\n===== RESULT POLL =====")
    try:
        result = call.get(timeout=0)
        print("Result is complete. Bytes returned:", len(result))
    except TimeoutError:
        print("Result is still running or queued.")
    except Exception as error:
        print("Remote call failed:", repr(error))


if __name__ == "__main__":
    main()
