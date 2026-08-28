#!/usr/bin/env python3
"""Song-blind AST/source guard for the sealed V164 local-evidence boundary."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Iterable

V162_NEGATIVE_GUARD_BLOB = "8d40bc7f3dce9c9717e41fa1060c553434ad9959"
V162_EVENT_LOGIC_BLOB = "9f9b33fd8c210ad581025b454cf69b6999aa544b"
V162_TRANSCRIBER_BLOB = "fa163cafe2131aa73cdbb50df10d4e4912cff53b"
V162_STRUCTURAL_QC_BLOB = "b7d3fa92fc9f3bed00931d19097e08cd91eab62b"
V162_JSON_FIXTURE_BLOB = "654557363745f580f425252395542e9fb91adaad"
V162_CONTRACT_BLOB = "409da313ed03a6c232d6578d48b0da6aa35b000b"

FORBIDDEN_RUNTIME_LITERALS = (
    "research/v154-professional-references",
    "frontend-reference-payload.json",
    "score_frontend_reference.py",
    "debug/v163-cpu-autonomous/generated.json",
    "debug/v163-cpu-autonomous/reference-score.json",
    "debug/v163-cpu-autonomous/score-terminal-freeze.json",
    ".github/workflows/v163-score.yml",
    ".github/workflows/v163-generate.yml",
    "validation/v163_cpu_autonomous",
)
PITCH_IMPORT_PREFIXES = ("basic_pitch", "demucs")
PITCH_CALL_NAMES = {"pyin", "yin", "predict"}
STATIC_FORBIDDEN_WORKFLOW_TOKENS = ("cuda", "nvidia", "modal run", "modal deploy")


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


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


def require_tokens(path: Path, text: str, tokens: Iterable[str], label: str) -> list[str]:
    return [f"{path}: {label} token missing {token!r}" for token in tokens if token not in text]


def forbidden_runtime_literals(path: Path, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    for literal in string_literals(tree):
        normalized = literal.replace("\\", "/").lower()
        for forbidden in FORBIDDEN_RUNTIME_LITERALS:
            if forbidden.lower() in normalized:
                failures.append(f"{path}: forbidden runtime literal {forbidden!r}")
    return failures


def no_song_or_pitch_imports(path: Path, tree: ast.AST, *, calls: bool = True) -> list[str]:
    failures: list[str] = []
    forbidden_modules = ("librosa", "basic_pitch", "demucs", "torch")
    for module in imported_modules(tree):
        if any(module == prefix or module.startswith(prefix + ".") for prefix in forbidden_modules):
            failures.append(f"{path}: static/pre-pitch file imports {module}")
    if calls:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and call_leaf_name(node) in PITCH_CALL_NAMES:
                failures.append(f"{path}: static/pre-pitch file calls pitch primitive {call_leaf_name(node)}")
    return failures


def frozen_dependency_failures(repo: Path) -> list[str]:
    expected = {
        repo / "debug/v162-cpu-autonomous/negative-runtime-guard.py": V162_NEGATIVE_GUARD_BLOB,
        repo / "validation/v162_cpu_autonomous/event_logic_v162.py": V162_EVENT_LOGIC_BLOB,
        repo / "validation/v162_cpu_autonomous/transcribe_v162.py": V162_TRANSCRIBER_BLOB,
        repo / "validation/v162_cpu_autonomous/structural_qc_v162.py": V162_STRUCTURAL_QC_BLOB,
        repo / "validation/v162_cpu_autonomous/test_json_native_v162.py": V162_JSON_FIXTURE_BLOB,
        repo / "debug/v162-cpu-autonomous/implementation-contract.json": V162_CONTRACT_BLOB,
    }
    failures: list[str] = []
    for path, blob in expected.items():
        if not path.is_file():
            failures.append(f"missing frozen V162 dependency: {path}")
        elif git_blob_sha(path) != blob:
            failures.append(f"frozen V162 dependency blob drift: {path}")
    return failures


def event_logic_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures = no_song_or_pitch_imports(path, tree)
    required = (
        'LOCAL_HALF_WINDOW_FRAMES = 32',
        'SUPPORT_SCALE_QUANTILE = 0.95',
        'SUBDIV_POSITIVE_QUANTILE = 0.55',
        'EVENT_NON_NEAREST_MARGIN = 0.05',
        f'_V162_EVENT_LOGIC_GIT_BLOB = "{V162_EVENT_LOGIC_BLOB}"',
        'def local_positive_population(',
        'def local_positive_quantile(',
        'def local_support_unit(',
        'def beat_frame_bounds(',
        'def beat_positive_quantile(',
        'def beat_support_unit(',
        'def supported_attack(',
        'def refine_onset_frame(',
        'def segment_guitar_rows(',
        'def active_state_reattack_candidates(',
        'def bass_state_proposals(',
        'def build_subdivision_lattice(',
        'def select_event_step(',
        '"normalizationLoFrame"',
        '"normalizationHiFrame"',
        'beat_support_unit(float(inst_env[inst_frame])',
        'beat_support_unit(float(shr_env[shared_frame])',
    )
    failures.extend(require_tokens(path, text, required, "local-evidence event-logic"))
    if "support_unit = _V162.support_unit" in text:
        failures.append(f"{path}: V164 onset support illegally aliases global V162 support_unit")
    return failures


def event_fixture_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures = no_song_or_pitch_imports(path, tree)
    required = (
        'guitar_segmentation_regression_fixture()',
        'active_state_recovery_regression_fixture()',
        'register_regression_fixture()',
        'bass_state_regression_fixture()',
        'grid_cap_regression_fixture()',
        'supported_attack_remote_invariance_fixture()',
        'onset_refinement_remote_invariance_fixture()',
        'bass_proposal_remote_invariance_fixture()',
        'subdivision_remote_and_scale_invariance_fixture()',
        'event_step_remote_and_scale_invariance_fixture()',
        'beat_support_zero_fixture()',
        '"schema": "dadrock.tabs.v164.local-evidence-static-test.v2"',
        '"V163CandidateRead": False',
        '"V163ScoreRead": False',
        '"songAudioRead": False',
        '"gpuUsed": False',
    )
    failures.extend(require_tokens(path, text, required, "song-blind fixture"))
    return failures


def timebase_builder_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures = no_song_or_pitch_imports(path, tree)
    required = (
        'V162_BUILDER_BLOB = "f7e9483aea16af770bcffe01ad8cfaf689d693b9"',
        f'V162_CONTRACT_BLOB = "{V162_CONTRACT_BLOB}"',
        'base.build_subdivision_lattice = build_subdivision_lattice',
        'artifact["version"] = "V164"',
        '"V163CandidateRead": False',
        '"V163ScoreRead": False',
        '"gpu": False',
    )
    failures.extend(require_tokens(path, text, required, "timebase adapter"))
    return failures


def timebase_qc_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures = no_song_or_pitch_imports(path, tree)
    required = (
        'V162_QC_BLOB = "78acc9fd626039801011d039cca12686b72369c0"',
        f'V162_CONTRACT_BLOB = "{V162_CONTRACT_BLOB}"',
        'base.build_subdivision_lattice = build_subdivision_lattice',
        'base.extrapolated_final_beat = extrapolated_final_beat',
        'receipt["version"] = "V164"',
        '"pitchInferenceInvoked": False',
        '"V163CandidateRead": False',
        '"V163ScoreRead": False',
        '"gpuUsed": False',
    )
    failures.extend(require_tokens(path, text, required, "timebase-QC adapter"))
    return failures


def transcriber_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures: list[str] = []
    # The V164 wrapper itself must remain pitch-import free. Pitch exists only in
    # the exact pinned V162 source and can execute only after validate_runtime_boundary.
    failures.extend(no_song_or_pitch_imports(path, tree))
    required = (
        f'V162_TRANSCRIBER_BLOB = "{V162_TRANSCRIBER_BLOB}"',
        f'V162_EVENT_LOGIC_BLOB = "{V162_EVENT_LOGIC_BLOB}"',
        f'V162_CONTRACT_BLOB = "{V162_CONTRACT_BLOB}"',
        'def validate_runtime_boundary(',
        'qc.get("validation") != "PASS"',
        'qc.get("timebaseSha256") != sha256_file(args.timebase)',
        'environment.get("device") != "cpu"',
        'environment.get("cudaAvailable") is not False',
        'pre_run.get("referenceReadAtSeal") is not False',
        'pre_run.get("V163CandidateReadAtSeal") is not False',
        'pre_run.get("V163ScoreReadAtSeal") is not False',
        'qc_safety.get("pitchInferenceInvoked") is False',
        'def _local_admission_support(',
        'v164.local_support_unit(',
        '"onsetNormalization": onset_provenance',
        '"proposalNormalization": {"loFrame": int(proposal["normalizationLoFrame"]), "hiFrame": int(proposal["normalizationHiFrame"])}',
        'replace_exact(source, old_support, new_support, 2, "local onset admission support")',
        'module.segment_guitar_rows = v164.segment_guitar_rows',
        'module.active_state_reattack_candidates = v164.active_state_reattack_candidates',
        'module.bass_state_proposals = v164.bass_state_proposals',
        'module.refine_onset_frame = v164.refine_onset_frame',
        'module.select_event_step = v164.select_event_step',
        'module.validate_runtime_boundary = validate_runtime_boundary',
    )
    failures.extend(require_tokens(path, text, required, "transcriber adapter"))
    return failures


def structural_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures = no_song_or_pitch_imports(path, tree)
    required = (
        f'V162_STRUCTURAL_QC_BLOB = "{V162_STRUCTURAL_QC_BLOB}"',
        f'V162_CONTRACT_BLOB = "{V162_CONTRACT_BLOB}"',
        'def deep_close(',
        'def enhanced_stream_check(',
        'full V164 event-step metadata does not recompute',
        'v164.local_support_unit(float(env[center]), env, center)',
        'local q95 onset support does not recompute',
        'local q95 provenance mismatch',
        'proposalNormalization',
        '"contractStructuralRequirementsSealed"',
        '"transcriberLocalAdaptationPath"',
        '"eventLogicLocalityPath"',
        '"timebaseQcV163BlindBeforePitch"',
        'module.build_subdivision_lattice = v164.build_subdivision_lattice',
        'module.select_event_step = v164.select_event_step',
        'module.safety_pass = v164_safety_pass',
    )
    failures.extend(require_tokens(path, text, required, "structural-QC adapter"))
    return failures


def json_fixture_failures(path: Path, text: str, tree: ast.AST) -> list[str]:
    failures = no_song_or_pitch_imports(path, tree)
    required = (
        f'V162_JSON_FIXTURE_BLOB = "{V162_JSON_FIXTURE_BLOB}"',
        'build_adapted_module().json_native',
        'json.dumps({"x": np.bool_(True)})',
        '"onsetNormalization"',
        '"proposalNormalization"',
        '"normalizedSupport"',
        'contains_numpy(normalized)',
        'allow_nan=False',
        'float("nan")',
        'float("inf")',
        'float("-inf")',
        '"V163CandidateRead": False',
        '"V163ScoreRead": False',
        '"songAudioRead": False',
    )
    failures.extend(require_tokens(path, text, required, "JSON-native fixture"))
    return failures


def workflow_failures(path: Path) -> list[str]:
    text = path.read_text().replace("\\", "/")
    lower = text.lower()
    failures: list[str] = []
    for forbidden in FORBIDDEN_RUNTIME_LITERALS:
        if forbidden.lower() in lower:
            failures.append(f"{path}: forbidden workflow text {forbidden!r}")
    for token in STATIC_FORBIDDEN_WORKFLOW_TOKENS:
        if token in lower:
            failures.append(f"{path}: non-CPU/static workflow token forbidden {token!r}")
    required = (
        'workflow_dispatch:',
        'python validation/v164_cpu_autonomous/test_event_logic_v164.py',
        'python validation/v164_cpu_autonomous/test_json_native_v164.py',
        'python debug/v164-cpu-autonomous/negative-runtime-guard.py',
    )
    failures.extend(require_tokens(path, text, required, "static-preflight workflow"))
    forbidden_execution = (
        'python validation/v164_cpu_autonomous/build_timebase_v164.py --',
        'python validation/v164_cpu_autonomous/timebase_qc_v164.py --',
        'python validation/v164_cpu_autonomous/transcribe_v164.py --',
        'python validation/v164_cpu_autonomous/structural_qc_v164.py --',
    )
    for token in forbidden_execution:
        if token in text:
            failures.append(f"{path}: static preflight illegally executes song/runtime code {token!r}")
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
            raise RuntimeError(f"V164 negative guard missing input: {path}")
    if args.workflow is not None and not args.workflow.is_file():
        raise RuntimeError(f"V164 negative guard missing workflow: {args.workflow}")

    repo = Path(__file__).resolve().parents[2]
    failures = frozen_dependency_failures(repo)
    parsed: dict[Path, tuple[str, ast.AST]] = {}
    for path in paths:
        text, tree = parse(path)
        parsed[path] = (text, tree)
        failures.extend(forbidden_runtime_literals(path, tree))

    failures.extend(event_logic_failures(args.event_logic, *parsed[args.event_logic]))
    failures.extend(event_fixture_failures(args.event_test, *parsed[args.event_test]))
    failures.extend(timebase_builder_failures(args.timebase_builder, *parsed[args.timebase_builder]))
    failures.extend(timebase_qc_failures(args.timebase_qc, *parsed[args.timebase_qc]))
    failures.extend(transcriber_failures(args.transcriber, *parsed[args.transcriber]))
    failures.extend(structural_failures(args.structural_qc, *parsed[args.structural_qc]))
    failures.extend(json_fixture_failures(args.json_native_test, *parsed[args.json_native_test]))
    if args.workflow is not None:
        failures.extend(workflow_failures(args.workflow))

    result = {
        "schema": "dadrock.tabs.v164.negative-runtime-guard.v1",
        "validation": "PASS" if not failures else "FAIL",
        "frozenV162NegativeGuardGitBlob": V162_NEGATIVE_GUARD_BLOB,
        "checks": {
            "frozenV162DependenciesExact": not any("frozen V162" in x or "missing frozen" in x for x in failures),
            "pureLocalEventLogic": not any("event-logic" in x or "static/pre-pitch file imports" in x and str(args.event_logic) in x for x in failures),
            "songBlindInvarianceFixtures": not any("song-blind fixture" in x for x in failures),
            "timebaseBeforePitchBoundary": not any("timebase adapter" in x or "timebase-QC adapter" in x for x in failures),
            "transcriberRequiresQcBeforePitchAndLocalAdaptation": not any("transcriber adapter" in x for x in failures),
            "structuralQcRecomputesLocalEvidence": not any("structural-QC adapter" in x for x in failures),
            "jsonNativeLocalProvenanceBoundary": not any("JSON-native fixture" in x for x in failures),
            "noReferenceScorerOrV163ArtifactPaths": not any("forbidden runtime" in x or "forbidden workflow" in x for x in failures),
            "staticWorkflowCpuOnlyWhenProvided": args.workflow is None or not any(str(args.workflow) in x for x in failures),
        },
        "failures": failures,
        "safety": {
            "songAudioRead": False,
            "demucsInvoked": False,
            "pitchInferenceInvoked": False,
            "professionalReferenceRead": False,
            "frozenScorerRead": False,
            "V163CandidateRead": False,
            "V163ScoreRead": False,
            "priorScoreRead": False,
            "gpuUsed": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if not failures else 4


if __name__ == "__main__":
    raise SystemExit(main())
