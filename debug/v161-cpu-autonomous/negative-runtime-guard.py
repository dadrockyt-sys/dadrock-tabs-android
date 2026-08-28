#!/usr/bin/env python3
"""Song-blind static negative guard for the sealed V161 runtime boundary.

This reviewer/static tool reads source text and AST only. It never reads song
audio, professional-reference payloads, frozen scorer content, prior candidates,
or score artifacts.
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
    "debug/v160-cpu-autonomous/generated.json",
    "debug/v160-cpu-autonomous/reference-score.json",
    "debug/v160-cpu-autonomous/score-terminal-freeze.json",
    ".github/workflows/v160-score.yml",
    ".github/workflows/v160-generate.yml",
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
    return [f"{path}: forbidden runtime text {token!r}" for token in FORBIDDEN_RUNTIME_LITERALS if token.lower() in normalized]


def runtime_literal_failures(path: Path, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    for literal in string_literals(tree):
        normalized = literal.replace("\\", "/").lower()
        for token in FORBIDDEN_RUNTIME_LITERALS:
            if token.lower() in normalized:
                failures.append(f"{path}: forbidden runtime literal {token!r}")
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
    matches = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name]
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
    required_global = (
        'qc.get("validation") != "PASS"',
        'qc.get("timebaseSha256") != sha256_file(args.timebase)',
        'environment.get("device") != "cpu"',
        'environment.get("cudaAvailable") is not False',
        'pre_run.get("referenceReadAtSeal") is not False',
        'pre_run.get("V160CandidateReadAtSeal") is not False',
    )
    for token in required_global:
        if token not in text:
            failures.append(f"{path}: runtime boundary token missing {token!r}")

    main_fn = function(tree, "main")
    if main_fn is None:
        failures.append(f"{path}: expected exactly one main()")
        return failures
    calls = call_lines(main_fn)
    boundary = calls.get("validate_runtime_boundary", [])
    bass = calls.get("bass_events", [])
    guitar = calls.get("guitar_events", [])
    if len(boundary) != 1 or len(bass) != 1 or len(guitar) != 1:
        failures.append(f"{path}: expected one runtime-boundary, Bass, and Guitar call in main()")
    elif not (boundary[0] < bass[0] and boundary[0] < guitar[0]):
        failures.append(f"{path}: pitch inference occurs before validate_runtime_boundary")

    boundary_fn = function(tree, "validate_runtime_boundary")
    if boundary_fn is None:
        failures.append(f"{path}: expected exactly one validate_runtime_boundary()")
    else:
        segment = ast.get_source_segment(text, boundary_fn) or ""
        for token in required_global:
            if token not in segment:
                failures.append(f"{path}: validate_runtime_boundary missing {token!r}")
    return failures


def guitar_architecture_failures(path: Path, text: str) -> list[str]:
    failures: list[str] = []
    required = (
        'onset_threshold=0.50',
        'frame_threshold=0.30',
        'minimum_note_length=90.0',
        'merge_same_pitch_rows(raw)',
        'refine_onset_frame(env, original_frame, GUITAR_ONSET_RADIUS_FRAMES)',
        'guitar_admission_score(',
        'admission + EPS < 0.50',
        'activity_support + EPS < 0.05',
        '"source": "basic_pitch_consolidated"',
        '"standaloneHarmonicTrackRecoveryEnabled": False',
        '"standaloneHarmonicTrackAddedCount": 0',
    )
    for token in required:
        if token not in text:
            failures.append(f"{path}: Guitar sealed architecture token missing {token!r}")
    forbidden_emission = ('"source": "harmonic_track"', "top_template_midi_per_frame(")
    for token in forbidden_emission:
        if token in text:
            failures.append(f"{path}: forbidden standalone Guitar harmonic recovery token {token!r}")
    return failures


def bass_architecture_failures(path: Path, text: str) -> list[str]:
    failures: list[str] = []
    required = (
        'median_smooth_midi(pyin_midi)',
        'bass_transition_frames(smoothed, voiced_prob)',
        'merge_bass_proposals(retained_onsets, transitions, env)',
        'refine_onset_frame(env, original_frame, BASS_ONSET_RADIUS_FRAMES)',
        '(0.120 / 2.0)',
        'bass_admission_score(',
        'activity_support + EPS < 0.04',
        'vp + EPS >= 0.60',
        'admission + EPS < 0.42',
        'suppress_same_pitch_refractory(admitted)',
        '"onset_harmonic_pyin_refined"',
        '"transition_harmonic_pyin_refined"',
    )
    for token in required:
        if token not in text:
            failures.append(f"{path}: Bass sealed architecture token missing {token!r}")
    return failures


def event_logic_contract_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    required_constants = (
        "GUITAR_MERGE_GAP_SECONDS = 0.080",
        "GUITAR_ONSET_RADIUS_FRAMES = 6",
        "BASS_ONSET_RADIUS_FRAMES = 8",
        "ONSET_MOVE_POSITIVE_QUANTILE = 0.60",
        "ONSET_MOVE_MIN_RATIO = 1.10",
        "BASS_TRANSITION_SEMITONES = 1.50",
        "BASS_TRANSITION_MIN_VOICED = 0.55",
        "BASS_TRANSITION_MIN_IOI_SECONDS = 0.060",
        "BASS_PROPOSAL_MERGE_SECONDS = 0.045",
        "BASS_RAW_REFRACTORY_SECONDS = 0.060",
        "GUITAR_POLYPHONY_CAP = 6",
        "BASS_GRID_CAP = 1",
    )
    for token in required_constants:
        if token not in text:
            failures.append(f"{path}: sealed event-logic constant missing {token!r}")
    required_functions = (
        "refine_onset_frame", "merge_same_pitch_rows", "median_smooth_midi",
        "bass_transition_frames", "merge_bass_proposals", "suppress_same_pitch_refractory",
        "cap_guitar_polyphony", "cap_bass_grid", "guitar_admission_score", "bass_admission_score",
    )
    for name in required_functions:
        if function(tree, name) is None:
            failures.append(f"{path}: required event-logic function missing/duplicated {name}")
    return failures


def structural_serializer_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    if function(tree, "json_native") is None:
        failures.append(f"{path}: missing exactly one json_native()")
    required = (
        'checks["frozenGrid"] = bool(',
        'native_checks = {key: bool(value) for key, value in checks.items()}',
        'passed = all(native_checks.values()) and not errors',
        '"checks": native_checks',
        'normalized = json_native(receipt)',
        'allow_nan=False',
        'isinstance(value, np.generic)',
        'isinstance(value, np.ndarray)',
        'value.item()',
        'value.tolist()',
        'checks["guitarNoStandaloneHarmonicRecovery"]',
        'checks["guitarPolyphonyCapSix"]',
        'checks["bassGridMonophonyCapOne"]',
        'checks["eventAdmissionScoresFiniteAndWithinZeroOne"]',
        'checks["eventRefinementFieldsPresent"]',
    )
    for token in required:
        if token not in text:
            failures.append(f"{path}: structural/static contract token missing {token!r}")
    passed_i = text.find("passed = all(native_checks.values()) and not errors")
    receipt_i = text.find("receipt = {")
    normalize_i = text.find("normalized = json_native(receipt)")
    write_i = text.find("args.receipt.write_text")
    if min(passed_i, receipt_i, normalize_i, write_i) < 0 or not (passed_i < receipt_i < normalize_i < write_i):
        failures.append(f"{path}: structural decision/receipt normalization/write ordering unproven")
    return failures


def static_test_failures(event_test: Path, event_text: str, event_tree: ast.AST, json_test: Path, json_text: str, json_tree: ast.AST) -> list[str]:
    failures: list[str] = []
    for path, tree in ((event_test, event_tree), (json_test, json_tree)):
        modules = imported_modules(tree)
        for forbidden_module in ("librosa", "basic_pitch", "demucs", "torch"):
            if any(module == forbidden_module or module.startswith(forbidden_module + ".") for module in modules):
                failures.append(f"{path}: song-blind static test imports {forbidden_module}")
    event_required = (
        "test_same_pitch_merge()", "test_onset_refinement()", "test_bass_transition_boundary()",
        "test_bass_proposal_merge()", "test_refractory()", "test_polyphony_caps()", "test_admission_scores()",
        '"V161 song-blind event logic fixtures: PASS"',
    )
    for token in event_required:
        if token not in event_text:
            failures.append(f"{event_test}: event fixture token missing {token!r}")
    json_required = (
        'json.dumps({"x": np.bool_(True)})', "np.int64(7)", "np.float64(1.25)",
        "np.asarray([[1, 2], [3, 4]]", "json_native(fixture)", "contains_numpy(normalized)",
        "allow_nan=False", 'float("nan")', 'float("inf")', 'float("-inf")',
        '"numpyTypesRemainAfterNormalization": False', '"nativeCheckValuesAreBool": True',
        '"roundTripExact": True', '"nonfiniteRejected": True', '"songAudioRead": False',
        '"professionalReferenceRead": False', '"V160CandidateRead": False',
    )
    for token in json_required:
        if token not in json_text:
            failures.append(f"{json_test}: JSON fixture token missing {token!r}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-logic", type=Path, required=True)
    parser.add_argument("--timebase-builder", type=Path, required=True)
    parser.add_argument("--timebase-qc", type=Path, required=True)
    parser.add_argument("--transcriber", type=Path, required=True)
    parser.add_argument("--structural-qc", type=Path, required=True)
    parser.add_argument("--event-logic-test", type=Path, required=True)
    parser.add_argument("--json-native-test", type=Path, required=True)
    parser.add_argument("--workflow", type=Path)
    args = parser.parse_args()

    python_runtime = [args.event_logic, args.timebase_builder, args.timebase_qc, args.transcriber, args.structural_qc]
    all_python = [*python_runtime, args.event_logic_test, args.json_native_test]
    for path in all_python:
        if not path.is_file():
            raise RuntimeError(f"V161 negative guard missing input: {path}")
    if args.workflow is not None and not args.workflow.is_file():
        raise RuntimeError(f"V161 negative guard missing workflow: {args.workflow}")

    failures: list[str] = []
    parsed: dict[Path, tuple[str, ast.AST]] = {}
    for path in all_python:
        text, tree = parse(path)
        parsed[path] = (text, tree)
        if path in python_runtime:
            failures.extend(runtime_literal_failures(path, tree))

    if args.workflow is not None:
        failures.extend(forbidden_text_failures(args.workflow, args.workflow.read_text()))

    for path in (args.timebase_builder, args.timebase_qc):
        _text, tree = parsed[path]
        failures.extend(pre_pitch_failures(path, tree))

    event_text, event_tree = parsed[args.event_logic]
    failures.extend(event_logic_contract_failures(args.event_logic, event_text, event_tree))

    trans_text, trans_tree = parsed[args.transcriber]
    failures.extend(transcriber_boundary_failures(args.transcriber, trans_text, trans_tree))
    failures.extend(guitar_architecture_failures(args.transcriber, trans_text))
    failures.extend(bass_architecture_failures(args.transcriber, trans_text))

    struct_text, struct_tree = parsed[args.structural_qc]
    failures.extend(structural_serializer_failures(args.structural_qc, struct_text, struct_tree))

    event_test_text, event_test_tree = parsed[args.event_logic_test]
    json_test_text, json_test_tree = parsed[args.json_native_test]
    failures.extend(static_test_failures(args.event_logic_test, event_test_text, event_test_tree, args.json_native_test, json_test_text, json_test_tree))

    result = {
        "schema": "dadrock.tabs.v161.negative-runtime-guard.v1",
        "validation": "PASS" if not failures else "FAIL",
        "checks": {
            "noProfessionalReferenceScorerOrV160CandidateRuntimePaths": not any("forbidden runtime" in x for x in failures),
            "prePitchFilesContainNoPitchImportsOrCalls": not any("pre-pitch" in x for x in failures),
            "transcriberRequiresExactTimebaseQcPassBeforePitch": not any("runtime boundary" in x.lower() or "pitch inference" in x.lower() for x in failures),
            "eventLogicMatchesSealedNumerics": not any("event-logic" in x.lower() for x in failures),
            "guitarStandaloneHarmonicRecoveryDisabled": not any("guitar" in x.lower() and "harmonic" in x.lower() for x in failures),
            "bassTransitionArchitecturePresent": not any("bass sealed architecture" in x.lower() for x in failures),
            "structuralQcUsesJsonNativeAndV161Rules": not any("structural" in x.lower() for x in failures),
            "staticFixturesAreSongBlind": not any("song-blind static test" in x.lower() for x in failures),
        },
        "failures": failures,
        "safety": {
            "songAudioRead": False,
            "demucsInvoked": False,
            "pitchInferenceInvoked": False,
            "professionalReferenceRead": False,
            "frozenScorerRead": False,
            "V160CandidateRead": False,
            "priorScoreRead": False,
            "gpuUsed": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if not failures else 4


if __name__ == "__main__":
    raise SystemExit(main())
