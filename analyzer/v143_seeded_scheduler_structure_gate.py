from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SEPARATOR_PATH = REPO_ROOT / "analyzer" / "v143_seeded_separator.py"

EXPECTED_BLOBS = {
    "analyzer/v143_modal_http_endpoint.py": "9a550f0afd5ced3894d8f1ccd18543fa5cd68ad6",
    "analyzer/v143_modal_live_endpoint.py": "111bf14a8f91045d3478901f8e36b88a2e7f181a",
    "analyzer/v143_vercel_audio_request_adapter.py": "6d1787f34a3b7ca781ced8e5695993a3777406a8",
    "analyzer/v143_rhythm_deterministic_stem_provider.py": "3c6dcf9b8e7360ba1dd886810f3c14c05ac0579b",
    "analyzer/v143_rhythm_stem_provider.py": "cd180bfb35e8110f031504035af5f11e502c3dc6",
    "analyzer/v143_deterministic_separator.py": "28b3e6fe0eb761178b142cf7dcbda533f0bf918d",
    "analyzer/v143_seeded_separator.py": "fc9b4c45c208d80be7abab64a8959f2a3babcee8",
    "analyzer/v143_seeded_audio_separator_cli.py": "645f324c207d67b32c6d279657805ff8f25c3aa0",
    "analyzer/v143_production_separator.py": "05ae1978fa02f8c84ccc1e44547fc4e4cea9798b",
}

EXPECTED_OUTPUT_FILENAMES = {
    "direct-demucs6s-guitar.wav",
    "bsroformer-instrumental.wav",
    "bsroformer-demucs6s-guitar.wav",
}

EXPECTED_RETURN_KEYS = {
    "directGuitar",
    "roformerInstrumental",
    "cascadeGuitar",
    "models",
    "settings",
    "referenceFree",
    "diagnosticOnly",
}

FORBIDDEN_ACTIVE_TOKENS = (
    "goat",
    "guitarset",
    "splitmysong",
    "score",
    "scorer",
    "quality_target",
    "reference_corpus",
    "reference_audio",
)


class GateFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateFailure(message)


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def find_function(tree: ast.AST, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise GateFailure(f"missing function: {name}")


def calls_in(node: ast.AST) -> list[ast.Call]:
    return [item for item in ast.walk(node) if isinstance(item, ast.Call)]


def matching_calls(node: ast.AST, name: str) -> list[ast.Call]:
    return [call for call in calls_in(node) if dotted_name(call.func) == name]


def one_call(node: ast.AST, name: str) -> ast.Call:
    matches = matching_calls(node, name)
    require(len(matches) == 1, f"expected exactly one call to {name}, found {len(matches)}")
    return matches[0]


def call_lines(node: ast.AST, name: str) -> list[int]:
    return sorted(call.lineno for call in matching_calls(node, name))


def source_expr(node: ast.AST) -> str:
    return ast.unparse(node)


def enclosing_withs(node: ast.AST, line: int) -> list[ast.With]:
    result: list[ast.With] = []
    for candidate in ast.walk(node):
        if not isinstance(candidate, ast.With):
            continue
        if candidate.lineno <= line <= getattr(candidate, "end_lineno", candidate.lineno):
            result.append(candidate)
    return result


def with_has_context_call(with_node: ast.With, function_name: str, arg_source: str) -> bool:
    for item in with_node.items:
        context = item.context_expr
        if not isinstance(context, ast.Call):
            continue
        if dotted_name(context.func) != function_name or len(context.args) != 1:
            continue
        if source_expr(context.args[0]) == arg_source:
            return True
    return False


def process_assignment(function: ast.FunctionDef, variable_name: str) -> ast.Call:
    for node in ast.walk(function):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id != variable_name:
            continue
        if isinstance(node.value, ast.Call) and dotted_name(node.value.func) == "ctx.Process":
            return node.value
    raise GateFailure(f"missing {variable_name} = ctx.Process(...)")


def keyword_value(call: ast.Call, keyword: str) -> ast.AST:
    for item in call.keywords:
        if item.arg == keyword:
            return item.value
    raise GateFailure(f"missing Process keyword: {keyword}")


def dict_literal_keys(return_node: ast.Return) -> set[str]:
    require(isinstance(return_node.value, ast.Dict), "final seeded separator return must remain a dict literal")
    keys: set[str] = set()
    assert isinstance(return_node.value, ast.Dict)
    for key in return_node.value.keys:
        require(isinstance(key, ast.Constant) and isinstance(key.value, str), "return key must be a string literal")
        assert isinstance(key, ast.Constant)
        keys.add(str(key.value))
    return keys


def active_import_and_call_names(tree: ast.AST) -> Iterable[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                yield node.module
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.Call):
            name = dotted_name(node.func)
            if name:
                yield name


def validate_blob_pins() -> dict[str, str]:
    actual: dict[str, str] = {}
    for relative, expected in EXPECTED_BLOBS.items():
        path = REPO_ROOT / relative
        require(path.is_file(), f"pinned source missing: {relative}")
        digest = git_blob_sha(path.read_bytes())
        actual[relative] = digest
        require(digest == expected, f"source blob changed for {relative}: {digest} != {expected}")
    return actual


def validate_scheduler_structure() -> dict[str, Any]:
    source = SEPARATOR_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(SEPARATOR_PATH))
    build = find_function(tree, "build_seeded_v143_stems")
    run_child = find_function(tree, "_run_demucs_child")
    terminate_join = find_function(tree, "_terminate_and_join")
    join_child = find_function(tree, "_join_demucs_child")

    spawn_call = one_call(build, "multiprocessing.get_context")
    require(
        len(spawn_call.args) == 1
        and isinstance(spawn_call.args[0], ast.Constant)
        and spawn_call.args[0].value == "spawn",
        "scheduler start method must remain literal spawn",
    )

    direct_process_call = process_assignment(build, "direct_process")
    cascade_process_call = process_assignment(build, "cascade_process")
    for label, process_call in (("direct", direct_process_call), ("cascade", cascade_process_call)):
        target = keyword_value(process_call, "target")
        require(isinstance(target, ast.Name) and target.id == "_run_demucs_child", f"{label} Process target changed")

    direct_args = source_expr(keyword_value(direct_process_call, "args"))
    cascade_args = source_expr(keyword_value(cascade_process_call, "args"))
    require("str(normalized_input)" in direct_args and "str(work / 'direct')" in direct_args, "direct Process inputs changed")
    require("str(Path(roformer['path']))" in cascade_args and "str(work / 'cascade')" in cascade_args, "cascade Process inputs changed")

    direct_start = one_call(build, "direct_process.start")
    roformer_call = one_call(build, "separate_roformer_instrumental")
    cascade_start = one_call(build, "cascade_process.start")
    direct_join_calls = [
        call for call in matching_calls(build, "_join_demucs_child")
        if call.args and isinstance(call.args[0], ast.Name) and call.args[0].id == "direct_process"
    ]
    cascade_join_calls = [
        call for call in matching_calls(build, "_join_demucs_child")
        if call.args and isinstance(call.args[0], ast.Name) and call.args[0].id == "cascade_process"
    ]
    require(len(direct_join_calls) == 1, "expected exactly one direct child join")
    require(len(cascade_join_calls) == 1, "expected exactly one cascade child join")
    direct_join = direct_join_calls[0]
    cascade_join = cascade_join_calls[0]

    copy_lines = call_lines(build, "shutil.copy2")
    require(len(copy_lines) == 3, f"expected exactly three output copies, found {len(copy_lines)}")
    returns = [node for node in ast.walk(build) if isinstance(node, ast.Return)]
    require(len(returns) == 1, f"expected one build return, found {len(returns)}")
    final_return = returns[0]

    ordered_lines = [
        direct_start.lineno,
        roformer_call.lineno,
        cascade_start.lineno,
        direct_join.lineno,
        cascade_join.lineno,
        min(copy_lines),
        final_return.lineno,
    ]
    require(ordered_lines == sorted(ordered_lines) and len(set(ordered_lines)) == len(ordered_lines), f"scheduler order changed: {ordered_lines}")

    for label, start_call in (("direct", direct_start), ("cascade", cascade_start)):
        withs = enclosing_withs(build, start_call.lineno)
        require(
            any(with_has_context_call(item, "_temporary_environment", "DEMUCS_SINGLE_THREAD_ENV") for item in withs),
            f"{label} child start escaped deterministic Demucs environment",
        )

    roformer_withs = enclosing_withs(build, roformer_call.lineno)
    require(
        any(
            isinstance(item.context_expr, ast.Call)
            and dotted_name(item.context_expr.func) == "_temporary_environment"
            and len(item.context_expr.args) == 1
            and isinstance(item.context_expr.args[0], ast.Dict)
            and source_expr(item.context_expr.args[0]) == "{'CUDA_VISIBLE_DEVICES': None}"
            for with_node in roformer_withs
            for item in with_node.items
        ),
        "RoFormer call escaped parent GPU-visibility environment",
    )

    try_nodes = [node for node in ast.walk(build) if isinstance(node, ast.Try)]
    cleanup_try: ast.Try | None = None
    for try_node in try_nodes:
        for handler in try_node.handlers:
            if isinstance(handler.type, ast.Name) and handler.type.id == "BaseException":
                cleanup_try = try_node
                break
        if cleanup_try is not None:
            break
    require(cleanup_try is not None, "missing BaseException scheduler cleanup handler")
    assert cleanup_try is not None

    base_handler = next(
        handler
        for handler in cleanup_try.handlers
        if isinstance(handler.type, ast.Name) and handler.type.id == "BaseException"
    )
    handler_calls = {dotted_name(call.func) + ":" + source_expr(call.args[0]) for call in calls_in(base_handler) if call.args}
    require("_terminate_and_join:direct_process" in handler_calls, "direct child is not terminated/joined on failure")
    require("_terminate_and_join:cascade_process" in handler_calls, "cascade child is not terminated/joined on failure")
    require(any(isinstance(node, ast.Raise) and node.exc is None for node in ast.walk(base_handler)), "scheduler failure is not re-raised")

    final_close_targets = {
        source_expr(call.args[0])
        for call in calls_in(ast.Module(body=cleanup_try.finalbody, type_ignores=[]))
        if dotted_name(call.func) == "_close_connection" and call.args
    }
    require(
        final_close_targets == {"direct_send", "direct_receive", "cascade_send", "cascade_receive"},
        f"pipe cleanup changed: {sorted(final_close_targets)}",
    )

    terminate_calls = {dotted_name(call.func) for call in calls_in(terminate_join)}
    for expected in ("process.is_alive", "process.terminate", "process.join"):
        require(expected in terminate_calls, f"_terminate_and_join lost {expected}")

    join_calls = {dotted_name(call.func) for call in calls_in(join_child)}
    for expected in ("process.join", "process.is_alive", "result_connection.poll", "result_connection.recv"):
        require(expected in join_calls, f"_join_demucs_child lost {expected}")
    require(any(isinstance(node, ast.Attribute) and node.attr == "exitcode" for node in ast.walk(join_child)), "_join_demucs_child lost exitcode check")
    require(len(matching_calls(join_child, "RuntimeError")) >= 4, "_join_demucs_child fail-closed checks weakened")

    child_demucs = one_call(run_child, "separate_demucs_guitar")
    require(len(child_demucs.args) == 3, "child Demucs helper call shape changed")
    require(source_expr(child_demucs.args[0]) == "seeded_audio_separator_cli()", "child Demucs CLI contract changed")

    string_literals = {
        str(node.value)
        for node in ast.walk(build)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    require(EXPECTED_OUTPUT_FILENAMES.issubset(string_literals), "frozen output filename changed")

    return_keys = dict_literal_keys(final_return)
    require(return_keys == EXPECTED_RETURN_KEYS, f"public seeded separator return keys changed: {sorted(return_keys)}")

    active_names = [name.lower() for name in active_import_and_call_names(tree)]
    forbidden_hits = sorted(
        name for name in active_names if any(token in name for token in FORBIDDEN_ACTIVE_TOKENS)
    )
    require(not forbidden_hits, f"reference/scoring/dataset-facing active symbol found: {forbidden_hits}")

    return {
        "spawnMethod": "spawn",
        "orderedLines": {
            "directStart": direct_start.lineno,
            "roformer": roformer_call.lineno,
            "cascadeStart": cascade_start.lineno,
            "directJoin": direct_join.lineno,
            "cascadeJoin": cascade_join.lineno,
            "firstOutputCopy": min(copy_lines),
            "return": final_return.lineno,
        },
        "outputFilenames": sorted(EXPECTED_OUTPUT_FILENAMES),
        "returnKeys": sorted(return_keys),
        "failureCleanup": {
            "terminatesAndJoinsBothChildren": True,
            "closesAllPipeEndpoints": True,
            "reraises": True,
        },
        "referenceFacingInputs": 0,
        "scoreCalls": 0,
        "qualityVerdictMade": False,
    }


def main() -> None:
    report: dict[str, Any] = {
        "gate": "v143-seeded-scheduler-structure",
        "allPassed": False,
        "referenceFacingInputs": 0,
        "scoreCalls": 0,
        "qualityVerdictMade": False,
    }
    try:
        report["sourceBlobs"] = validate_blob_pins()
        report["scheduler"] = validate_scheduler_structure()
        report["allPassed"] = True
    except BaseException as exc:
        report["errorType"] = type(exc).__name__
        report["error"] = str(exc)
        print(json.dumps(report, indent=2, sort_keys=True))
        raise

    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
