from __future__ import annotations

import ast
import unittest
from pathlib import Path


BRIDGE_PATH = Path(__file__).with_name("v143_modal_http_endpoint.py")
STATUS_FUNCTION = "_status_rhythm_job"
PENDING_ERROR = "The analyzer job stopped before it could complete."


def _dotted_name(node: ast.AST | None) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _dict_constants(return_node: ast.Return) -> dict[str, object]:
    value = return_node.value
    if not isinstance(value, ast.Dict):
        return {}

    result: dict[str, object] = {}
    for key, item in zip(value.keys, value.values):
        if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
            continue
        if isinstance(item, ast.Constant):
            result[key.value] = item.value
    return result


def _status_poll_try() -> ast.Try:
    source = BRIDGE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(BRIDGE_PATH))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == STATUS_FUNCTION
    )

    for node in ast.walk(function):
        if not isinstance(node, ast.Try):
            continue
        for call in ast.walk(node):
            if not isinstance(call, ast.Call):
                continue
            if not isinstance(call.func, ast.Attribute) or call.func.attr != "get":
                continue
            if any(
                keyword.arg == "timeout"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value == 0
                for keyword in call.keywords
            ):
                return node

    raise AssertionError("Could not find FunctionCall.get(timeout=0) polling try block.")


def _handler_return_constants(handler: ast.ExceptHandler) -> dict[str, object]:
    for node in handler.body:
        if isinstance(node, ast.Return):
            return _dict_constants(node)
    return {}


class V143ModalPollTimeoutContractTest(unittest.TestCase):
    def test_pending_poll_catches_builtin_and_modal_timeout(self) -> None:
        poll_try = _status_poll_try()
        self.assertGreaterEqual(len(poll_try.handlers), 2)

        pending_handler = poll_try.handlers[0]
        self.assertIsInstance(pending_handler.type, ast.Tuple)
        caught = {
            _dotted_name(item)
            for item in pending_handler.type.elts
        }
        self.assertEqual(
            caught,
            {"TimeoutError", "modal.exception.TimeoutError"},
        )

        returned = _handler_return_constants(pending_handler)
        self.assertEqual(returned.get("status"), "processing")
        self.assertIs(returned.get("orchestratorRunning"), True)

    def test_non_timeout_exception_remains_terminal_failed(self) -> None:
        poll_try = _status_poll_try()
        self.assertGreaterEqual(len(poll_try.handlers), 2)

        failure_handler = poll_try.handlers[1]
        self.assertEqual(_dotted_name(failure_handler.type), "Exception")
        returned = _handler_return_constants(failure_handler)
        self.assertEqual(returned.get("status"), "failed")
        self.assertEqual(returned.get("error"), PENDING_ERROR)

    def test_python_exception_matching_matches_bridge_contract(self) -> None:
        class ModalTimeoutError(Exception):
            pass

        def classify(error: Exception) -> str:
            try:
                raise error
            except (TimeoutError, ModalTimeoutError):
                return "processing"
            except Exception:
                return "failed"

        self.assertEqual(classify(TimeoutError()), "processing")
        self.assertEqual(classify(ModalTimeoutError()), "processing")
        self.assertEqual(classify(RuntimeError()), "failed")


if __name__ == "__main__":
    unittest.main()
