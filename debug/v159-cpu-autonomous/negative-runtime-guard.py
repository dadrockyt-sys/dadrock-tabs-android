#!/usr/bin/env python3
"""Static negative guard for the sealed V159 runtime boundary.

Reviewer-facing check only.  It proves that the pre-pitch files do not import or
invoke pitch recognition, that V159 runtime files contain no prior-version or
professional-reference/scorer path hooks, and that the transcriber validates a
frozen PASS timebase-QC receipt before its first pitch-inference call.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Iterable

FORBIDDEN_RUNTIME_LITERALS = (
    "research/v154-professional-references",
    "frontend-reference-payload.json",
    "score_frontend_reference.py",
    "debug/v158-",
    "debug/v157-",
    "validation/v158_",
    "validation/v157_",
    "post-score-architecture-diagnosis",
)
PITCH_IMPORT_PREFIXES = ("basic_pitch",)
PITCH_CALL_NAMES = {"pyin", "yin", "predict"}


def parse(path: Path) -> tuple[str, ast.AST]:
    text = path.read_text()
    return text, ast.parse(text, filename=str(path))


def imported_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def call_leaf_name(node: ast.Call) -> str | None:
    fn = node.func
    if isinstance(fn, ast.Name):
        return fn.id
    if isinstance(fn, ast.Attribute):
        return fn.attr
    return None


def pitch_calls(tree: ast.AST) -> list[str]:
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = call_leaf_name(node)
            if name in PITCH_CALL_NAMES:
                found.append(name)
    return found


def string_literals(tree: ast.AST) -> Iterable[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.value


def runtime_literal_failures(path: Path, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    for literal in string_literals(tree):
        normalized = literal.replace("\\", "/").lower()
        for forbidden in FORBIDDEN_RUNTIME_LITERALS:
            if forbidden.lower() in normalized:
                failures.append(f"{path}: forbidden runtime literal {forbidden!r}")
    return failures


def pre_pitch_failures(path: Path, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    modules = imported_modules(tree)
    for module in modules:
        if any(module == prefix or module.startswith(prefix + ".") for prefix in PITCH_IMPORT_PREFIXES):
            failures.append(f"{path}: pre-pitch file imports {module}")
    for name in pitch_calls(tree):
        failures.append(f"{path}: pre-pitch file calls pitch primitive {name}")
    return failures


def transcriber_boundary_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    if "qc.get(\"validation\") != \"PASS\"" not in text:
        failures.append(f"{path}: missing explicit frozen timebase-QC PASS rejection")
    boundary = text.find("validate_runtime_boundary(args)")
    bass = text.find("bass_events(args.bass)")
    guitar = text.find("guitar_events(args.guitar)")
    if boundary < 0 or bass < 0 or guitar < 0 or not (boundary < bass and boundary < guitar):
        failures.append(f"{path}: pitch inference is not textually after validate_runtime_boundary")

    main_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "main"]
    if len(main_nodes) != 1:
        failures.append(f"{path}: expected exactly one main()")
    else:
        ordered_calls: list[str] = []
        for node in ast.walk(main_nodes[0]):
            if isinstance(node, ast.Call):
                name = call_leaf_name(node)
                if name:
                    ordered_calls.append(name)
        if "validate_runtime_boundary" not in ordered_calls or "bass_events" not in ordered_calls or "guitar_events" not in ordered_calls:
            failures.append(f"{path}: required runtime-boundary/pitch calls missing")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timebase-builder", type=Path, required=True)
    parser.add_argument("--timebase-qc", type=Path, required=True)
    parser.add_argument("--transcriber", type=Path, required=True)
    parser.add_argument("--structural-qc", type=Path, required=True)
    parser.add_argument("--workflow", type=Path)
    args = parser.parse_args()

    runtime_paths = [args.timebase_builder, args.timebase_qc, args.transcriber, args.structural_qc]
    if args.workflow is not None:
        runtime_paths.append(args.workflow)
    for path in runtime_paths:
        if not path.is_file():
            raise RuntimeError(f"negative guard missing input: {path}")

    failures: list[str] = []
    parsed: dict[Path, tuple[str, ast.AST]] = {}
    for path in runtime_paths:
        if path.suffix in {".py", ".pyw"}:
            text, tree = parse(path)
            parsed[path] = (text, tree)
            failures.extend(runtime_literal_failures(path, tree))
        else:
            text = path.read_text()
            normalized = text.replace("\\", "/").lower()
            for forbidden in FORBIDDEN_RUNTIME_LITERALS:
                if forbidden.lower() in normalized:
                    failures.append(f"{path}: forbidden runtime text {forbidden!r}")

    for path in (args.timebase_builder, args.timebase_qc):
        _text, tree = parsed[path]
        failures.extend(pre_pitch_failures(path, tree))

    transcriber_text, transcriber_tree = parsed[args.transcriber]
    failures.extend(transcriber_boundary_failures(args.transcriber, transcriber_text, transcriber_tree))

    result = {
        "schema": "dadrock.tabs.v159.negative-runtime-guard.v1",
        "validation": "PASS" if not failures else "FAIL",
        "checks": {
            "noProfessionalReferenceOrScorerRuntimePaths": not any("forbidden runtime" in x for x in failures),
            "noPriorVersionRuntimePaths": not any("forbidden runtime" in x for x in failures),
            "prePitchFilesContainNoPitchImportsOrCalls": not any("pre-pitch" in x for x in failures),
            "transcriberRequiresTimebaseQcPassBeforePitch": not any("timebase-QC" in x or "pitch inference" in x or "runtime-boundary" in x for x in failures),
        },
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 4


if __name__ == "__main__":
    raise SystemExit(main())
