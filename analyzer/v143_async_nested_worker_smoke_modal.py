from __future__ import annotations

import os
import time
from typing import Any

import modal
import modal_analyzer as legacy
from v143_async_job_protocol import (
    ASYNC_RESULT_TTL_SECONDS,
    build_completed_envelope,
    create_job_id,
    decode_result_items,
    encode_result_envelope,
)


APP_NAME = str(
    os.environ.get("V143_ASYNC_NESTED_SMOKE_APP_NAME")
    or "dadrock-v143-async-nested-worker-smoke"
).strip()
QUEUE_NAME = str(
    os.environ.get("V143_ASYNC_NESTED_SMOKE_QUEUE_NAME")
    or "dadrock-v143-async-nested-worker-smoke-results"
).strip()
WORKER_APP_NAME = "dadrock-v143-ai-tab-live"
WORKER_SMOKE_FUNCTION = "rhythm_dependency_smoke"

if not APP_NAME or not QUEUE_NAME:
    raise RuntimeError("V143 nested worker smoke resource names must not be empty.")

app = modal.App(APP_NAME)

http_image = (
    legacy.image.env(
        {
            "V143_ASYNC_NESTED_SMOKE_APP_NAME": APP_NAME,
            "V143_ASYNC_NESTED_SMOKE_QUEUE_NAME": QUEUE_NAME,
        }
    )
    .add_local_python_source("modal_analyzer")
    .add_local_python_source("v143_async_job_protocol")
)

result_queue = modal.Queue.from_name(
    QUEUE_NAME,
    create_if_missing=True,
)


def _queue_envelope(job_id: str, envelope: dict[str, Any]) -> None:
    result_queue.put_many(
        encode_result_envelope(envelope),
        partition=job_id,
        partition_ttl=ASYNC_RESULT_TTL_SECONDS,
        timeout=30,
    )


@app.function(
    image=http_image,
    timeout=300,
    memory=4096,
)
def nested_worker_child(job_id: str) -> dict[str, Any]:
    """Match the production orchestrator shape, but call only the worker smoke."""
    worker = modal.Function.from_name(
        WORKER_APP_NAME,
        WORKER_SMOKE_FUNCTION,
    )
    worker_result = worker.remote()

    if worker_result.get("cudaAvailable") is not True:
        raise RuntimeError("Nested worker dependency smoke reported no CUDA.")
    if worker_result.get("deviceName") != "NVIDIA L4":
        raise RuntimeError("Nested worker dependency smoke reported wrong GPU.")
    if worker_result.get("deterministicSeparatorSeed") != 143:
        raise RuntimeError("Nested worker dependency smoke reported wrong seed.")
    if worker_result.get("referenceFree") is not True:
        raise RuntimeError("Nested worker dependency smoke violated reference-free boundary.")

    synthetic_result = {
        "generatedTab": "SYNTHETIC-NESTED-WORKER-SMOKE",
        "liveV143": {
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "referenceRuntimeInputUsed": False,
            "runtimeLabelsRequired": False,
        },
        "nestedWorkerSmoke": {
            "cudaAvailable": True,
            "deviceName": "NVIDIA L4",
            "deterministicSeparatorSeed": 143,
            "referenceFree": True,
        },
    }
    _queue_envelope(
        job_id,
        build_completed_envelope(synthetic_result),
    )
    return {
        "status": "completed",
        "resultQueued": True,
        "audioRead": False,
        "separatorModelExecuted": False,
    }


@app.function(
    image=http_image,
    timeout=360,
    memory=512,
)
def nested_worker_spawn_smoke() -> dict[str, Any]:
    """Spawn the orchestrator, nest a cross-app worker smoke, and read Queue."""
    started = time.monotonic()
    job_id = create_job_id()
    result_queue.clear(partition=job_id)

    call = nested_worker_child.spawn(job_id)

    deadline = time.monotonic() + 300.0
    items: list[Any] = []
    while time.monotonic() < deadline:
        items = list(
            result_queue.iterate(
                partition=job_id,
                item_poll_timeout=0.0,
            )
        )
        if items:
            break
        time.sleep(1.0)

    if not items:
        raise RuntimeError(
            "Spawned orchestrator did not publish nested worker smoke result."
        )

    envelope = decode_result_items(items)
    result = envelope.get("result") if isinstance(envelope, dict) else None
    completed = (
        envelope.get("status") == "completed"
        and isinstance(result, dict)
        and result.get("generatedTab") == "SYNTHETIC-NESTED-WORKER-SMOKE"
        and result.get("nestedWorkerSmoke", {}).get("deviceName") == "NVIDIA L4"
    )
    if not completed:
        raise RuntimeError("Nested worker smoke published an invalid result.")

    result_queue.clear(partition=job_id)
    remaining = list(
        result_queue.iterate(
            partition=job_id,
            item_poll_timeout=0.0,
        )
    )

    return {
        "schemaVersion": 1,
        "gate": "v143-async-nested-worker-smoke",
        "appName": APP_NAME,
        "queueName": QUEUE_NAME,
        "spawnCallIdPresent": bool(getattr(call, "object_id", None)),
        "nestedWorkerCompleted": completed,
        "queueCleared": not remaining,
        "resultTtlSeconds": ASYNC_RESULT_TTL_SECONDS,
        "elapsedSeconds": round(time.monotonic() - started, 3),
        "workerApp": WORKER_APP_NAME,
        "workerFunction": WORKER_SMOKE_FUNCTION,
        "workerGpu": "NVIDIA L4",
        "audioRead": False,
        "separatorModelExecuted": False,
        "referenceFacingInputs": 0,
        "referenceScoreCalls": 0,
        "qualityVerdictMade": False,
    }
