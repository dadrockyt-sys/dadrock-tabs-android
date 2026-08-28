#!/usr/bin/env python3
"""Song-blind static negative guard for the sealed V160 runtime boundary.

Reviewer-facing only. This guard reads source text/AST, never song audio,
professional references, prior candidates, scores, or runtime diagnostics.
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
    "debug/v159-",
    "validation/v159_",
    "dadrock.tabs.v159.",
    "debug/v158-",
    "validation/v158_",
    "debug/v157-",
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


def forbidden_text_failures(path: Path, text: str) -> list[str]:
    normalized = text.replace("\\", "/").lower()
    return [
        f"{path}: forbidden runtime text {forbidden!r}"
        for forbidden in FORBIDDEN_RUNTIME_LITERALS
        if forbidden.lower() in normalized
    ]


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
    for module in imported_modules(tree):
        if any(module == prefix or module.startswith(prefix + ".") for prefix in PITCH_IMPORT_PREFIXES):
            failures.append(f"{path}: pre-pitch file imports {module}")
    for name in pitch_calls(tree):
        failures.append(f"{path}: pre-pitch file calls pitch primitive {name}")
    return failures


def function(tree: ast.AST, name: str) -> ast.FunctionDef | None:
    matches = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    return matches[0] if len(matches) == 1 else None


def call_lines(fn: ast.FunctionDef) -> dict[str, list[int]]:
    found: dict[str, list[int]] = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            name = call_leaf_name(node)
            if name:
                found.setdefault(name, []).append(int(node.lineno))
    return found


def transcriber_boundary_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    if 'qc.get("validation") != "PASS"' not in text:
        failures.append(f"{path}: missing explicit frozen timebase-QC PASS rejection")
    if 'qc.get("timebaseSha256") != sha256_file(args.timebase)' not in text:
        failures.append(f"{path}: missing exact PASS-QC timebase hash-chain rejection")

    main_fn = function(tree, "main")
    if main_fn is None:
        failures.append(f"{path}: expected exactly one main()")
        return failures
    calls = call_lines(main_fn)
    boundary_lines = calls.get("validate_runtime_boundary", [])
    bass_lines = calls.get("bass_events", [])
    guitar_lines = calls.get("guitar_events", [])
    if len(boundary_lines) != 1 or len(bass_lines) != 1 or len(guitar_lines) != 1:
        failures.append(f"{path}: expected one runtime-boundary, bass, and guitar call in main()")
    elif not (boundary_lines[0] < bass_lines[0] and boundary_lines[0] < guitar_lines[0]):
        failures.append(f"{path}: pitch inference occurs before validate_runtime_boundary")

    boundary_fn = function(tree, "validate_runtime_boundary")
    if boundary_fn is None:
        failures.append(f"{path}: expected exactly one validate_runtime_boundary()")
    else:
        boundary_text = ast.get_source_segment(text, boundary_fn) or ""
        required = (
            'qc.get("validation") != "PASS"',
            'environment.get("device") != "cpu"',
            'environment.get("cudaAvailable") is not False',
            'pre_run.get("referenceReadAtSeal") is not False',
            'safety.get("referenceRead") is False',
            'safety.get("priorGeneratedCandidateRead") is False',
        )
        for token in required:
            if token not in boundary_text:
                failures.append(f"{path}: runtime boundary missing {token!r}")
    return failures


def structural_serializer_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    if function(tree, "json_native") is None:
        failures.append(f"{path}: missing exactly one json_native() normalizer")
    required_text = (
        'checks["frozenGrid"] = bool(',
        'native_checks = {key: bool(value) for key, value in checks.items()}',
        '"checks": native_checks',
        'normalized_receipt = json_native(receipt)',
        'allow_nan=False',
        'isinstance(value, np.generic)',
        'isinstance(value, np.ndarray)',
        'value.item()',
        'value.tolist()',
    )
    for token in required_text:
        if token not in text:
            failures.append(f"{path}: JSON-native contract token missing {token!r}")

    passed_index = text.find("passed = all(bool(value) for value in checks.values())")
    native_index = text.find("native_checks = {key: bool(value) for key, value in checks.items()}")
    receipt_index = text.find("receipt = {")
    normalize_index = text.find("normalized_receipt = json_native(receipt)")
    write_index = text.find("args.receipt.write_text")
    if min(passed_index, native_index, receipt_index, normalize_index, write_index) < 0:
        failures.append(f"{path}: unable to prove structural decision/normalization/write ordering")
    elif not (passed_index < native_index < receipt_index < normalize_index < write_index):
        failures.append(f"{path}: structural PASS/FAIL is not frozen before JSON normalization/write")
    return failures


def serializer_test_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    modules = imported_modules(tree)
    for forbidden_module in ("librosa", "basic_pitch", "demucs", "torch"):
        if any(module == forbidden_module or module.startswith(forbidden_module + ".") for module in modules):
            failures.append(f"{path}: song-blind serializer test imports {forbidden_module}")
    required = (
        'json.dumps({"x": np.bool_(True)})',
        "np.int64(7)",
        "np.float64(1.25)",
        "np.asarray([[1, 2], [3, 4]]",
        "json_native(fixture)",
        "contains_numpy(normalized)",
        "allow_nan=False",
        'float("nan")',
        'float("inf")',
        'float("-inf")',
        '"controlReproducedV159Failure": True',
        '"numpyTypesRemainAfterNormalization": False',
        '"nativeCheckValuesAreBool": True',
        '"roundTripExact": True',
        '"nonfiniteRejected": True',
        '"songAudioRead": False',
        '"professionalReferenceRead": False',
    )
    for token in required:
        if token not in text:
            failures.append(f"{path}: serializer static-test token missing {token!r}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timebase-builder", type=Path, required=True)
    parser.add_argument("--timebase-qc", type=Path, required=True)
    parser.add_argument("--transcriber", type=Path, required=True)
    parser.add_argument("--structural-qc", type=Path, required=True)
    parser.add_argument("--json-native-test", type=Path, required=True)
    parser.add_argument("--workflow", type=Path)
    args = parser.parse_args()

    python_runtime_paths = [
        args.timebase_builder,
        args.timebase_qc,
        args.transcriber,
        args.structural_qc,
    ]
    for path in [*python_runtime_paths, args.json_native_test]:
        if not path.is_file():
            raise RuntimeError(f"V160 negative guard missing input: {path}")
    if args.workflow is not None and not args.workflow.is_file():
        raise RuntimeError(f"V160 negative guard missing workflow: {args.workflow}")

    failures: list[str] = []
    parsed: dict[Path, tuple[str, ast.AST]] = {}
    for path in python_runtime_paths:
        text, tree = parse(path)
        parsed[path] = (text, tree)
        failures.extend(runtime_literal_failures(path, tree))

    test_text, test_tree = parse(args.json_native_test)
    parsed[args.json_native_test] = (test_text, test_tree)
    # The synthetic test may mention V159 as a historical control, but it must
    # still contain no professional-reference/scorer paths.
    lowered_test = test_text.replace("\\", "/").lower()
    for forbidden in FORBIDDEN_RUNTIME_LITERALS[:3]:
        if forbidden.lower() in lowered_test:
            failures.append(f"{args.json_native_test}: forbidden reference/scorer text {forbidden!r}")

    if args.workflow is not None:
        workflow_text = args.workflow.read_text()
        failures.extend(forbidden_text_failures(args.workflow, workflow_text))

    for path in (args.timebase_builder, args.timebase_qc):
        _text, tree = parsed[path]
        failures.extend(pre_pitch_failures(path, tree))

    transcriber_text, transcriber_tree = parsed[args.transcriber]
    failures.extend(transcriber_boundary_failures(args.transcriber, transcriber_text, transcriber_tree))

    structural_text, structural_tree = parsed[args.structural_qc]
    failures.extend(structural_serializer_failures(args.structural_qc, structural_text, structural_tree))
    failures.extend(serializer_test_failures(args.json_native_test, test_text, test_tree))

    categories = {
        "noProfessionalReferenceOrScorerRuntimePaths": not any("professional" in x.lower() or "scorer" in x.lower() or "frontend-reference" in x.lower() for x in failures),
        "noPriorVersionRuntimePathsOrSchemas": not any("v159" in x.lower() or "v158" in x.lower() or "v157" in x.lower() or "prior-version" in x.lower() for x in failures),
        "prePitchFilesContainNoPitchImportsOrCalls": not any("pre-pitch" in x for x in failures),
        "transcriberRequiresExactTimebaseQcPassBeforePitch": not any("runtime boundary" in x.lower() or "timebase-qc" in x.lower() or "pitch inference" in x.lower() or "pass-qc" in x.lower() for x in failures),
        "structuralQcUsesJsonNativeReceiptBoundary": not any("JSON-native contract" in x or "structural PASS/FAIL" in x or "json_native" in x for x in failures),
        "serializerStaticTestCoversV159FailureClass": not any("serializer static-test" in x or "song-blind serializer test" in x for x in failures),
    }
    result = {
        "schema": "dadrock.tabs.v160.negative-runtime-guard.v1",
        "validation": "PASS" if not failures else "FAIL",
        "checks": categories,
        "failures": failures,
        "safety": {
            "songAudioRead": False,
            "demucsInvoked": False,
            "pitchInferenceInvoked": False,
            "professionalReferenceRead": False,
            "priorCandidateRead": False,
            "priorScoreRead": False,
            "gpuUsed": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if not failures else 4


if __name__ == "__main__":
    raise SystemExit(main())
