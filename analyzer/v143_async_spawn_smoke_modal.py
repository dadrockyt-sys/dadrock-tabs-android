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
    os.environ.get("V143_ASYNC_SPAWN_SMOKE_APP_NAME")
    or "dadrock-v143-async-spawn-smoke"
).strip()
QUEUE_NAME = str(
    os.environ.get("V143_ASYNC_SPAWN_SMOKE_QUEUE_NAME")
    or "dadrock-v143-async-spawn-smoke-results"
).strip()

if not APP_NAME or not QUEUE_NAME:
    raise RuntimeError("V143 async spawn smoke resource names must not be empty.")

app = modal.App(APP_NAME)

# Match the production bridge image composition without importing or invoking the
# L4 worker. This diagnostic exists only to prove the Modal spawned-oneshot layer.
http_image = (
    legacy.image.env(
        {
            "V143_ASYNC_SPAWN_SMOKE_APP_NAME": APP_NAME,
            "V143_ASYNC_SPAWN_SMOKE_QUEUE_NAME": QUEUE_NAME,
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
    timeout=60,
    memory=512,
)
def synthetic_spawn_child(job_id: str) -> dict[str, Any]:
    """Spawned oneshot child: Queue write only; no audio, GPU, model, or worker."""
    synthetic_result = {
        "generatedTab": "SYNTHETIC-ONESHOT-SPAWN-SMOKE",
        "liveV143": {
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "referenceRuntimeInputUsed": False,
            "runtimeLabelsRequired": False,
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
        "modelExecuted": False,
    }


@app.function(
    image=http_image,
    timeout=120,
    memory=512,
)
def synthetic_spawn_smoke() -> dict[str, Any]:
    """Start exactly one spawned child and prove its transient Queue handoff."""
    started = time.monotonic()
    job_id = create_job_id()
    result_queue.clear(partition=job_id)

    # This is the exact Modal primitive under suspicion in the production bridge.
    call = synthetic_spawn_child.spawn(job_id)

    deadline = time.monotonic() + 75.0
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
        time.sleep(0.5)

    if not items:
        raise RuntimeError("Spawned oneshot child did not publish its synthetic result.")

    envelope = decode_result_items(items)
    result = envelope.get("result") if isinstance(envelope, dict) else None
    completed = (
        envelope.get("status") == "completed"
        and isinstance(result, dict)
        and result.get("generatedTab") == "SYNTHETIC-ONESHOT-SPAWN-SMOKE"
    )
    if not completed:
        raise RuntimeError("Spawned oneshot child published an invalid result.")

    result_queue.clear(partition=job_id)
    remaining = list(
        result_queue.iterate(
            partition=job_id,
            item_poll_timeout=0.0,
        )
    )

    return {
        "schemaVersion": 1,
        "gate": "v143-async-spawn-smoke",
        "appName": APP_NAME,
        "queueName": QUEUE_NAME,
        "spawnCallIdPresent": bool(getattr(call, "object_id", None)),
        "spawnedResultCompleted": completed,
        "queueCleared": not remaining,
        "resultTtlSeconds": ASYNC_RESULT_TTL_SECONDS,
        "elapsedSeconds": round(time.monotonic() - started, 3),
        "audioRead": False,
        "workerInvoked": False,
        "modelExecuted": False,
        "referenceFacingInputs": 0,
        "referenceScoreCalls": 0,
        "qualityVerdictMade": False,
    }
