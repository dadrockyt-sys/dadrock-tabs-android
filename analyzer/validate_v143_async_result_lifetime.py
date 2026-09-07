from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "analyzer" / "v143_async_job_protocol.py"
ENDPOINT_PATH = ROOT / "analyzer" / "v143_modal_http_endpoint.py"

EXPECTED_WORKER_TIMEOUT_SECONDS = 20 * 60
MINIMUM_POST_WORKER_MARGIN_SECONDS = 10 * 60
EXPECTED_ASYNC_RESULT_TTL_SECONDS = (
    EXPECTED_WORKER_TIMEOUT_SECONDS + MINIMUM_POST_WORKER_MARGIN_SECONDS
)


def _literal_int(node: ast.AST) -> int:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        return _literal_int(node.left) * _literal_int(node.right)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _literal_int(node.left) + _literal_int(node.right)
    raise AssertionError(f"Expected a static integer expression, got {ast.dump(node)}")


def _assignment_int(module: ast.Module, name: str) -> int:
    for node in module.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == name:
            return _literal_int(node.value)
    raise AssertionError(f"Missing static assignment for {name}")


def _function(module: ast.Module, name: str) -> ast.FunctionDef:
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"Missing function {name}")


def _modal_timeout(function: ast.FunctionDef) -> int:
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        called = decorator.func
        if not (
            isinstance(called, ast.Attribute)
            and called.attr == "function"
            and isinstance(called.value, ast.Name)
            and called.value.id == "app"
        ):
            continue
        for keyword in decorator.keywords:
            if keyword.arg == "timeout":
                return _literal_int(keyword.value)
    raise AssertionError(f"Missing @app.function timeout on {function.name}")


def _assert_partition_ttl_uses_shared_constant(function: ast.FunctionDef) -> None:
    ttl_keywords = [
        keyword
        for call in ast.walk(function)
        if isinstance(call, ast.Call)
        for keyword in call.keywords
        if keyword.arg == "partition_ttl"
    ]
    assert len(ttl_keywords) == 1, (
        f"{function.name} must set exactly one partition_ttl; found {len(ttl_keywords)}"
    )
    value = ttl_keywords[0].value
    assert isinstance(value, ast.Name) and value.id == "ASYNC_RESULT_TTL_SECONDS", (
        f"{function.name} must use ASYNC_RESULT_TTL_SECONDS for partition ownership"
    )


def _assert_expires_response_uses_shared_constant(function: ast.FunctionDef) -> None:
    matches = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if (
                isinstance(key, ast.Constant)
                and key.value == "expiresInSeconds"
            ):
                matches.append(value)
    assert matches, f"{function.name} must expose expiresInSeconds"
    assert all(
        isinstance(value, ast.Name) and value.id == "ASYNC_RESULT_TTL_SECONDS"
        for value in matches
    ), f"{function.name} must report the shared async TTL"


def main() -> None:
    protocol_source = PROTOCOL_PATH.read_text(encoding="utf-8")
    endpoint_source = ENDPOINT_PATH.read_text(encoding="utf-8")
    protocol_module = ast.parse(protocol_source, filename=str(PROTOCOL_PATH))
    endpoint_module = ast.parse(endpoint_source, filename=str(ENDPOINT_PATH))

    ttl_seconds = _assignment_int(protocol_module, "ASYNC_RESULT_TTL_SECONDS")
    assert ttl_seconds == EXPECTED_ASYNC_RESULT_TTL_SECONDS, (
        f"Async TTL must be {EXPECTED_ASYNC_RESULT_TTL_SECONDS}s; got {ttl_seconds}s"
    )
    assert ttl_seconds > EXPECTED_WORKER_TIMEOUT_SECONDS, (
        "Async ownership TTL must exceed the worker execution budget"
    )
    margin_seconds = ttl_seconds - EXPECTED_WORKER_TIMEOUT_SECONDS
    assert margin_seconds >= MINIMUM_POST_WORKER_MARGIN_SECONDS, (
        f"Async ownership margin must be at least "
        f"{MINIMUM_POST_WORKER_MARGIN_SECONDS}s; got {margin_seconds}s"
    )

    orchestrator = _function(endpoint_module, "run_rhythm_async_job")
    assert _modal_timeout(orchestrator) == EXPECTED_WORKER_TIMEOUT_SECONDS, (
        "run_rhythm_async_job execution budget changed unexpectedly"
    )

    _assert_partition_ttl_uses_shared_constant(
        _function(endpoint_module, "_queue_orchestrator_control")
    )
    _assert_partition_ttl_uses_shared_constant(
        _function(endpoint_module, "_queue_job_envelope")
    )
    _assert_expires_response_uses_shared_constant(
        _function(endpoint_module, "_start_rhythm_job")
    )
    _assert_expires_response_uses_shared_constant(
        _function(endpoint_module, "_status_rhythm_job")
    )

    print(
        "PASS v143 async result lifetime: "
        f"ttl={ttl_seconds}s worker={EXPECTED_WORKER_TIMEOUT_SECONDS}s "
        f"margin={margin_seconds}s control=result=shared-ttl"
    )


if __name__ == "__main__":
    main()
