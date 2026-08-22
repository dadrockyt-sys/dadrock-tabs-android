from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import modal

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-em-riff-single-attempt-detached-state.json"
)


def _format_node(node: Any) -> str:
    fields = []
    for name in (
        "input_id",
        "function_call_id",
        "task_id",
        "status",
        "function_name",
        "module_name",
    ):
        value = getattr(node, name, None)
        if value is not None:
            fields.append(f"{name}={value}")
    if fields:
        return " | ".join(fields)
    return repr(node)


def main() -> None:
    if not STATE_PATH.exists():
        raise FileNotFoundError(
            "Detached state not found. Run the detached submitter first."
        )

    state = json.loads(STATE_PATH.read_text())
    call_id = state.get("callId")
    if not call_id:
        raise RuntimeError("Detached state does not contain a Modal call ID.")

    started_at = float(state.get("startedAtEpoch") or time.time())
    elapsed = time.time() - started_at
    call = modal.FunctionCall.from_id(call_id)

    print("Jimmy PAIge detached call inspection")
    print("Call ID:", call_id)
    print("Saved status:", state.get("status"))
    print("Elapsed:", round(elapsed, 1), "seconds")

    print("\n===== CALL GRAPH / STATE =====")
    try:
        graph = call.get_call_graph()
        if not graph:
            print("No call-graph nodes returned.")
        else:
            for index, node in enumerate(graph, start=1):
                print(f"{index}. {_format_node(node)}")
    except Exception as exc:
        print("Call graph unavailable:", type(exc).__name__, str(exc))

    print("\n===== RECENT CALL LOGS =====")
    logs_manager = getattr(call, "logs", None)
    if logs_manager is None:
        print("This installed Modal SDK does not expose FunctionCall.logs.")
        print(
            "Fallback command:\n"
            f"modal app logs dadrock-v8-em-riff-extraction-training "
            f"--function-call {call_id} --timestamps"
        )
    else:
        try:
            entries = list(logs_manager.tail(entries=100))
            if not entries:
                print("No recent log entries returned.")
            else:
                for entry in entries:
                    timestamp = getattr(entry, "timestamp", "")
                    source = getattr(entry, "source", "")
                    message = getattr(entry, "message", str(entry))
                    prefix = " ".join(
                        part for part in (str(timestamp), str(source)) if part
                    )
                    if prefix:
                        print(prefix, end=" ")
                    print(message, end="" if str(message).endswith("\n") else "\n")
        except Exception as exc:
            print("Function-call log retrieval failed:", type(exc).__name__, str(exc))
            print(
                "Fallback command:\n"
                f"modal app logs dadrock-v8-em-riff-extraction-training "
                f"--function-call {call_id} --timestamps"
            )

    print("\n===== RESULT POLL =====")
    try:
        result = call.get(timeout=0)
    except TimeoutError:
        print("Result status: still running or queued")
    except Exception as exc:
        print("Result status: failed")
        print("Exception:", type(exc).__name__, str(exc))
    else:
        size = len(result) if isinstance(result, (bytes, bytearray)) else None
        print("Result status: complete")
        if size is not None:
            print("Returned bytes:", size)
        print(
            "Collect with: python analyzer/collect_jimmy_paige_single_attempt_detached.py"
        )


if __name__ == "__main__":
    main()
