from __future__ import annotations

import ast
import base64
import hashlib
import json
import random
from pathlib import Path
from typing import Any

from v143_async_job_protocol import (
    ASYNC_RESULT_CHUNK_BYTES,
    ASYNC_RESULT_TTL_SECONDS,
    build_completed_envelope,
    build_job_token,
    decode_result_items,
    encode_result_envelope,
    parse_job_token,
)


ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "analyzer" / "v143_modal_http_endpoint.py"
PROTOCOL = ROOT / "analyzer" / "v143_async_job_protocol.py"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_value_error(fn: Any, message: str) -> None:
    try:
        fn()
    except ValueError:
        return
    raise AssertionError(message)


def function_source(tree: ast.AST, source: str, name: str) -> str:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            segment = ast.get_source_segment(source, node)
            if segment:
                return segment
    raise AssertionError(f"missing function source: {name}")


def main() -> None:
    require(ASYNC_RESULT_TTL_SECONDS == 900, "async TTL must remain 15 minutes")
    require(
        ASYNC_RESULT_CHUNK_BYTES < 1_000_000,
        "queue chunks must remain safely below Modal's 1 MiB item limit",
    )

    secret = "unit-test-secret-with-enough-entropy"
    job_id = "job_ABCDEFGHIJKLMNOPQRSTUVWX"
    token = build_job_token(job_id, secret)
    require(parse_job_token(token, secret) == job_id, "signed token roundtrip failed")
    expect_value_error(
        lambda: parse_job_token(token + "x", secret),
        "tampered token did not fail closed",
    )
    expect_value_error(
        lambda: parse_job_token(token, "different-secret-with-enough-entropy"),
        "wrong signing secret did not fail closed",
    )

    rng = random.Random(143)
    text = base64.b64encode(rng.randbytes(1_600_000)).decode("ascii")
    result = {
        "generatedTab": "e|--0--|\nB|--1--|",
        "events": [{"id": 1, "detail": text}],
        "liveV143": {
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "referenceRuntimeInputUsed": False,
            "runtimeLabelsRequired": False,
        },
    }
    envelope = build_completed_envelope(result)
    items = encode_result_envelope(envelope)
    require(
        isinstance(items[0], dict) and items[0].get("chunkCount", 0) >= 2,
        "test payload did not exercise multi-chunk transport",
    )
    require(
        all(
            not isinstance(item, bytes) or len(item) <= ASYNC_RESULT_CHUNK_BYTES
            for item in items
        ),
        "encoded chunk exceeded configured queue boundary",
    )
    decoded = decode_result_items(items)
    require(decoded == envelope, "async envelope roundtrip changed structured result")

    expect_value_error(
        lambda: build_completed_envelope(
            {"generatedTab": "ok", "rawAudio": b"not-allowed"}
        ),
        "binary payload crossed structured-result boundary",
    )

    bridge_source = BRIDGE.read_text(encoding="utf-8")
    protocol_source = PROTOCOL.read_text(encoding="utf-8")
    bridge_tree = ast.parse(bridge_source)
    ast.parse(protocol_source)

    required_bridge_fragments = [
        'os.environ.get("V143_HTTP_APP_NAME")',
        'or "dadrock-v143-http-bridge"',
        'os.environ.get("V143_ASYNC_RESULT_QUEUE_NAME")',
        'or "dadrock-v143-async-results"',
        'ASYNC_CONTROL_KIND = "orchestrator-control"',
        "create_if_missing=True",
        "def async_protocol_smoke()",
        "build_completed_envelope(synthetic_result)",
        "queueRoundtrip",
        "queueCleared",
        "def _control_partition(job_id: str)",
        'return f"control-{job_id}"',
        "partition_ttl=ASYNC_RESULT_TTL_SECONDS",
        "def _queue_orchestrator_control(job_id: str, function_call_id: str)",
        '"functionCallId": call_id',
        "call = run_rhythm_async_job.spawn(job_id, dict(payload))",
        "_queue_orchestrator_control(job_id, call.object_id)",
        "call.cancel()",
        '"orchestratorTracked": True',
        "modal.FunctionCall.from_id(",
        "call.get(timeout=0)",
        "except modal.exception.TimeoutError:",
        '"orchestratorRunning": True',
        "_worker_handle().remote(dict(routed_payload))",
        "item_poll_timeout=0.0",
        "async_result_queue.clear(partition=job_id)",
        "async_result_queue.clear(partition=_control_partition(job_id))",
        '"controlCleared": True',
        'print("V143_ASYNC_STAGE orchestrator.start", flush=True)',
        'print("V143_ASYNC_STAGE worker_call.start", flush=True)',
        'print("V143_ASYNC_STAGE worker_call.done status=completed", flush=True)',
        'print("V143_ASYNC_STAGE worker_call.done status=failed", flush=True)',
        'print(f"V143_ASYNC_STAGE result_queue.done status={status}", flush=True)',
        'operation == "start"',
        'operation == "status"',
        'operation == "ack"',
        'operation != "analyze"',
        "route_http_payload(",
        "legacy_handler=_legacy_request",
        "rhythm_handler=rhythm_handler",
    ]
    for fragment in required_bridge_fragments:
        require(fragment in bridge_source, f"missing bridge invariant: {fragment}")

    # The control partition must remain metadata-only. It may contain only the
    # FunctionCall identity/schema/kind required to query Modal job state.
    control_source = function_source(
        bridge_tree,
        bridge_source,
        "_queue_orchestrator_control",
    )
    for forbidden in [
        "routed_payload",
        "payload",
        "audioUrl",
        "blobToken",
        "pathname",
        "generatedTab",
        "events",
        "result",
        "song",
        "artist",
    ]:
        require(
            forbidden not in control_source,
            f"sensitive/non-control field entered orchestrator control: {forbidden}",
        )

    # Stage logging must stay aggregate-only. Never emit request/job identities,
    # private URLs/tokens, generated content, or labels from the orchestrator.
    orchestrator_source = function_source(
        bridge_tree,
        bridge_source,
        "run_rhythm_async_job",
    )
    for forbidden in [
        "print(job_id",
        "print(routed_payload",
        "audioUrl",
        "blobToken",
        "pathname",
        "generatedTab",
        "professionalReference",
        "runtimeLabels",
    ]:
        require(
            forbidden not in orchestrator_source,
            f"sensitive orchestrator logging/source fragment: {forbidden}",
        )

    # Field names that explicitly report zero/false reference use are allowed and
    # required evidence. Forbid only executable/import-style scoring/reference
    # hooks plus restricted-lane names, not harmless safety metadata strings.
    forbidden_bridge_fragments = [
        "modal.Dict",
        "ASYNC_RESULT_TTL_SECONDS = 24",
        "score_reference(",
        "reference_score(",
        "load_reference(",
        "professional_reference(",
        "GOAT",
        "guitarset",
    ]
    for fragment in forbidden_bridge_fragments:
        require(fragment not in bridge_source, f"forbidden bridge fragment: {fragment}")

    summary = {
        "schemaVersion": 4,
        "gate": "v143-async-job-protocol",
        "allPassed": True,
        "protocolBlob": git_blob_sha(PROTOCOL),
        "bridgeBlob": git_blob_sha(BRIDGE),
        "resultTtlSeconds": ASYNC_RESULT_TTL_SECONDS,
        "controlTtlSeconds": ASYNC_RESULT_TTL_SECONDS,
        "chunkBytes": ASYNC_RESULT_CHUNK_BYTES,
        "chunkCount": items[0]["chunkCount"],
        "tokenRoundtrip": True,
        "tamperRejected": True,
        "wrongSecretRejected": True,
        "binaryPayloadRejected": True,
        "multiChunkRoundtrip": True,
        "isolatedResourceNamesSupported": True,
        "syntheticModalSmokeDefined": True,
        "orchestratorFunctionCallTracked": True,
        "functionCallNonblockingPoll": True,
        "functionCallFailureFailClosed": True,
        "controlMetadataOnly": True,
        "controlClearedOnAck": True,
        "aggregateStageLoggingOnly": True,
        "defaultSynchronousDispatchPreserved": True,
        "leadBassFallbackPreserved": True,
        "asyncRhythmOnly": True,
        "rawAudioQueued": False,
        "stemBytesQueued": False,
        "modelExecuted": False,
        "audioRead": False,
        "referenceFacingInputs": 0,
        "referenceScoreCalls": 0,
        "qualityVerdictMade": False,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
