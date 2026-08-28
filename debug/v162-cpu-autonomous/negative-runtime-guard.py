#!/usr/bin/env python3
"""Song-blind AST/source guard for the sealed V162 generation boundary."""
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
    "debug/v161-cpu-autonomous/generated.json",
    "debug/v161-cpu-autonomous/reference-score.json",
    "debug/v161-cpu-autonomous/score-terminal-freeze.json",
    ".github/workflows/v161-score.yml",
    ".github/workflows/v161-generate.yml",
    "validation/v161_cpu_autonomous",
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


def string_literals(tree: ast.AST) -> Iterable[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.value


def forbidden_runtime_literals(path: Path, tree: ast.AST) -> list[str]:
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
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = call_leaf_name(node)
            if name in PITCH_CALL_NAMES:
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


def transcriber_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    required_tokens = (
        'qc.get("validation") != "PASS"',
        'qc.get("timebaseSha256") != sha256_file(args.timebase)',
        'environment.get("device") != "cpu"',
        'environment.get("cudaAvailable") is not False',
        'pre_run.get("referenceReadAtSeal") is not False',
        'pre_run.get("V161CandidateReadAtSeal") is not False',
        'safety.get("referenceRead") is False',
        'safety.get("V161CandidateRead") is False',
        'standaloneHarmonicPitchDiscoveryEnabled": False',
        'segment_guitar_rows(raw, env)',
        'active_state_reattack_candidates(',
        'choose_sequence_register(',
        'stable_bass_states(smoothed, voiced_prob)',
        'bass_state_proposals(states, retained_onsets, env)',
        'select_event_step(event_time, lattice, instrument_env, shared_env)',
        'onset_threshold=0.50',
        'frame_threshold=0.30',
        'minimum_note_length=90.0',
    )
    for token in required_tokens:
        if token not in text:
            failures.append(f"{path}: sealed V162 token missing {token!r}")
    main_fn = function(tree, "main")
    if main_fn is None:
        failures.append(f"{path}: expected exactly one main()")
        return failures
    calls = call_lines(main_fn)
    boundary = calls.get("validate_runtime_boundary", [])
    bass = calls.get("bass_events", [])
    guitar = calls.get("guitar_events", [])
    if len(boundary) != 1 or len(bass) != 1 or len(guitar) != 1:
        failures.append(f"{path}: expected one boundary, bass, and guitar call")
    elif not (boundary[0] < bass[0] and boundary[0] < guitar[0]):
        failures.append(f"{path}: pitch inference occurs before runtime boundary")
    return failures


def event_logic_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    forbidden_modules = ("librosa", "basic_pitch", "demucs", "torch")
    for module in imported_modules(tree):
        if any(module == x or module.startswith(x + ".") for x in forbidden_modules):
            failures.append(f"{path}: pure helper imports {module}")
    required = (
        "SUBDIV_SEARCH_RADIUS_FRAMES = 3",
        "SUBDIV_POSITIVE_QUANTILE = 0.55",
        "SUBDIV_MOVE_MIN_RATIO = 1.05",
        "EVENT_NON_NEAREST_MARGIN = 0.05",
        "GUITAR_MAX_UNSUPPORTED_GAP_SECONDS = 0.120",
        "GUITAR_REATTACK_MIN_SUPPORT = 0.30",
        "GUITAR_RECOVERY_MIN_SCORE = 0.58",
        "GUITAR_RECOVERY_CAP = 3",
        "REGISTER_CONTEXT_WINDOW_SECONDS = 0.75",
        "REGISTER_MIN_RANK_GAIN = 0.15",
        "REGISTER_MIN_CONTEXT_DISTANCE_GAIN = 3.0",
        "BASS_MEDIAN_WINDOW = 7",
        "BASS_STATE_MIN_FRAMES = 4",
        "BASS_BRIDGE_GAP_FRAMES = 2",
        "BASS_REATTACK_MIN_IOI_SECONDS = 0.080",
        "def segment_guitar_rows(",
        "def active_state_reattack_candidates(",
        "def choose_sequence_register(",
        "def refine_beat_subdivisions(",
        "def extrapolated_final_beat(",
        "def build_subdivision_lattice(",
        "def select_event_step(",
        "def stable_bass_states(",
        "def bass_state_proposals(",
        "def cap_guitar_polyphony(",
        "def cap_bass_grid(",
    )
    for token in required:
        if token not in text:
            failures.append(f"{path}: event-logic contract token missing {token!r}")
    return failures


def fixture_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    for module in imported_modules(tree):
        if any(module == x or module.startswith(x + ".") for x in ("librosa", "basic_pitch", "demucs", "torch")):
            failures.append(f"{path}: song-blind fixture imports {module}")
    required = (
        "guitar_segmentation_fixture()",
        "active_state_recovery_fixture()",
        "register_fixture()",
        "subdivision_fixture()",
        "bass_state_fixture()",
        "grid_cap_fixture()",
        '"finalBeatExtrapolation": True',
        '"professionalReferenceRead": False',
        '"V161CandidateRead": False',
        '"songAudioRead": False',
    )
    for token in required:
        if token not in text:
            failures.append(f"{path}: fixture token missing {token!r}")
    return failures


def structural_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    required = (
        "def json_native(",
        "build_subdivision_lattice(grid_times.tolist(), shared)",
        "select_event_step(float(row[\"startSeconds\"]), lattice, instrument_env, shared)",
        'checks["subdivisionLatticeRecomputed"]',
        'checks["guitarNoStandaloneHarmonicRecovery"]',
        'checks["guitarPolyphonyCapSix"]',
        'checks["bassGridMonophonyCapOne"]',
        'native_checks = {key: bool(value) for key, value in checks.items()}',
        "normalized = json_native(receipt)",
        "allow_nan=False",
    )
    for token in required:
        if token not in text:
            failures.append(f"{path}: structural contract token missing {token!r}")
    return failures


def timebase_failures(path: Path, text: str) -> list[str]:
    failures: list[str] = []
    required = (
        "0.65 * unit_drums + 0.35 * unit_mix",
        "build_subdivision_lattice([float(x) for x in grid_times], shared)",
        '"subdivisionTimesSeconds"',
        '"subdivisionAbsoluteSteps"',
        '"V161CandidateRead": False',
    )
    for token in required:
        if token not in text:
            failures.append(f"{path}: subdivision timebase token missing {token!r}")
    return failures


def timebase_qc_failures(path: Path, text: str) -> list[str]:
    failures: list[str] = []
    required = (
        "build_subdivision_lattice(grid_times.tolist(), shared)",
        'checks["subdivisionRecomputedExact"]',
        'checks["beatAnchorsUnmoved"]',
        'checks["finalBeatExtrapolationExact"]',
        '"pitchInferenceInvoked": False',
        '"V161CandidateRead": False',
    )
    for token in required:
        if token not in text:
            failures.append(f"{path}: timebase-QC token missing {token!r}")
    return failures


def json_test_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    for module in imported_modules(tree):
        if any(module == x or module.startswith(x + ".") for x in ("librosa", "basic_pitch", "demucs", "torch")):
            failures.append(f"{path}: JSON fixture imports {module}")
    required = (
        'json.dumps({"x": np.bool_(True)})',
        "json_native(fixture)",
        "contains_numpy(normalized)",
        "allow_nan=False",
        'float("nan")',
        'float("inf")',
        'float("-inf")',
        '"professionalReferenceRead": False',
        '"V161CandidateRead": False',
    )
    for token in required:
        if token not in text:
            failures.append(f"{path}: JSON fixture token missing {token!r}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-logic", type=Path, required=True)
    parser.add_argument("--event-test", type=Path, required=True)
    parser.add_argument("--timebase-builder", type=Path, required=True)
    parser.add_argument("--timebase-qc", type=Path, required=True)
    parser.add_argument("--transcriber", type=Path, required=True)
    parser.add_argument("--structural-qc", type=Path, required=True)
    parser.add_argument("--json-native-test", type=Path, required=True)
    parser.add_argument("--workflow", type=Path)
    args = parser.parse_args()

    paths = [args.event_logic, args.event_test, args.timebase_builder, args.timebase_qc, args.transcriber, args.structural_qc, args.json_native_test]
    for path in paths:
        if not path.is_file():
            raise RuntimeError(f"V162 negative guard missing input: {path}")
    if args.workflow is not None and not args.workflow.is_file():
        raise RuntimeError(f"V162 negative guard missing workflow: {args.workflow}")

    failures: list[str] = []
    parsed: dict[Path, tuple[str, ast.AST]] = {}
    for path in paths:
        text, tree = parse(path)
        parsed[path] = (text, tree)
        if path not in (args.event_test, args.json_native_test):
            failures.extend(forbidden_runtime_literals(path, tree))

    for path in (args.timebase_builder, args.timebase_qc):
        failures.extend(pre_pitch_failures(path, parsed[path][1]))

    failures.extend(event_logic_failures(args.event_logic, *parsed[args.event_logic]))
    failures.extend(fixture_failures(args.event_test, *parsed[args.event_test]))
    failures.extend(timebase_failures(args.timebase_builder, parsed[args.timebase_builder][0]))
    failures.extend(timebase_qc_failures(args.timebase_qc, parsed[args.timebase_qc][0]))
    failures.extend(transcriber_failures(args.transcriber, *parsed[args.transcriber]))
    failures.extend(structural_failures(args.structural_qc, *parsed[args.structural_qc]))
    failures.extend(json_test_failures(args.json_native_test, *parsed[args.json_native_test]))

    if args.workflow is not None:
        workflow_text = args.workflow.read_text().replace("\\", "/").lower()
        for forbidden in FORBIDDEN_RUNTIME_LITERALS:
            if forbidden.lower() in workflow_text:
                failures.append(f"{args.workflow}: forbidden workflow text {forbidden!r}")

    result = {
        "schema": "dadrock.tabs.v162.negative-runtime-guard.v1",
        "validation": "PASS" if not failures else "FAIL",
        "checks": {
            "pureEventLogic": not any("event-logic" in x or "pure helper" in x for x in failures),
            "songBlindFixtures": not any("fixture" in x for x in failures),
            "prePitchFilesContainNoPitchImportsOrCalls": not any("pre-pitch" in x for x in failures),
            "subdivisionTimebaseContract": not any("subdivision timebase" in x or "timebase-QC" in x for x in failures),
            "transcriberRequiresQcBeforePitchAndSealedArchitecture": not any("transcriber" in x.lower() or "sealed V162" in x for x in failures),
            "structuralQcRecomputesLatticeAndStepSelection": not any("structural contract" in x for x in failures),
            "jsonNativeBoundary": not any("JSON fixture" in x for x in failures),
            "noReferenceScorerOrV161ArtifactPaths": not any("forbidden runtime" in x or "forbidden workflow" in x for x in failures),
        },
        "failures": failures,
        "safety": {
            "songAudioRead": False,
            "demucsInvoked": False,
            "pitchInferenceInvoked": False,
            "professionalReferenceRead": False,
            "frozenScorerRead": False,
            "V161CandidateRead": False,
            "priorScoreRead": False,
            "gpuUsed": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if not failures else 4


if __name__ == "__main__":
    raise SystemExit(main())
