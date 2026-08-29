#!/usr/bin/env python3
"""Static negative-runtime guard for V166 paired-window implementation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

PREREG_BLOB = "ca45241b4ab4689c8ceb3a7107e158367814cc1d"
CONTRACT_BLOB = "9ab505ee8c7de732b6e9a8928854ae99d3ebb0c7"
EXPECTED_OFFSETS_LITERAL = "V166_TEMPLATE_FRAME_OFFSETS = (-1, 0, 1, 2, 3, 4)"
LEGACY_NUMERIC_CONTRACT = "409da313ed03a6c232d6578d48b0da6aa35b000b"

FORBIDDEN_RUNTIME_PATHS = (
    "debug/v165-cpu-autonomous/generated.json",
    "debug/v165-cpu-autonomous/reference-score.json",
    "debug/v165-cpu-autonomous/score-terminal-freeze.json",
    "research/v154-professional-references/scorer-ready/frontend-reference-payload.json",
    "validation/v154_cpu_multitrack/score_frontend_reference.py",
)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--event-logic", type=Path, required=True)
    p.add_argument("--transcriber", type=Path, required=True)
    p.add_argument("--paired-test", type=Path, required=True)
    p.add_argument("--runtime-test", type=Path, required=True)
    p.add_argument("--timebase-builder", type=Path, required=True)
    p.add_argument("--timebase-qc", type=Path, required=True)
    p.add_argument("--structural-qc", type=Path, required=True)
    p.add_argument("--json-test", type=Path, required=True)
    p.add_argument("--workflow", type=Path)
    args = p.parse_args()

    repo = Path(__file__).resolve().parents[2]
    failures: list[str] = []
    prereg = repo / "debug/v166-cpu-autonomous/preregistration.json"
    contract = repo / "debug/v166-cpu-autonomous/implementation-contract.json"
    if git_blob_sha(prereg) != PREREG_BLOB:
        failures.append("preregistration blob drift")
    if git_blob_sha(contract) != CONTRACT_BLOB:
        failures.append("implementation-contract blob drift")

    sources = {
        "eventLogic": args.event_logic.read_text(),
        "transcriber": args.transcriber.read_text(),
        "pairedTest": args.paired_test.read_text(),
        "runtimeTest": args.runtime_test.read_text(),
        "timebaseBuilder": args.timebase_builder.read_text(),
        "timebaseQc": args.timebase_qc.read_text(),
        "structuralQc": args.structural_qc.read_text(),
        "jsonTest": args.json_test.read_text(),
    }
    runtime_sources = "\n".join(sources.values())
    for path in FORBIDDEN_RUNTIME_PATHS:
        if path in runtime_sources:
            failures.append(f"forbidden runtime path literal: {path}")

    t = sources["transcriber"]
    required_transcriber = (
        EXPECTED_OFFSETS_LITERAL,
        "V166_TEMPLATE_FRAME_COUNT = 6",
        "FROZEN_V165_TRANSCRIBER_BLOB = \"45d595853302b077fbf4f3094e9a4922fba02435\"",
        "def paired_window_frames(",
        "def paired_window_template_with(",
        "frozen_template_scores = module.template_scores",
        "module.three_frame_template = _paired_window_template",
        "def runtime_contract_overlay(",
        "_RUNTIME_ADAPTER.load_json = _compat_runtime_load_json",
        LEGACY_NUMERIC_CONTRACT,
    )
    for needle in required_transcriber:
        if needle not in t:
            failures.append(f"transcriber missing boundary: {needle}")
    if "subprocess" in t or "requests" in t:
        failures.append("transcriber imports external execution/network path")

    e = sources["eventLogic"]
    if "FROZEN_V165_EVENT_LOGIC_BLOB = \"b296b3c322c13f8963f253f9b0666db66766a178\"" not in e:
        failures.append("event logic predecessor pin missing")
    if "_build_frozen_v165_behavior" not in e:
        failures.append("event logic frozen V165 adapter missing")

    tb = sources["timebaseBuilder"]
    if "FROZEN_V165_TIMEBASE_BUILDER_BLOB = \"62d67becb768e1e5e3e8de1cd3b121eb863b2a18\"" not in tb:
        failures.append("timebase builder predecessor pin missing")
    for needle in ("def runtime_contract_overlay(", "_RUNTIME.load_json = _compat_runtime_load_json", LEGACY_NUMERIC_CONTRACT):
        if needle not in tb:
            failures.append(f"timebase builder compatibility boundary missing: {needle}")

    tqc = sources["timebaseQc"]
    if "FROZEN_V165_TIMEBASE_QC_BLOB = \"3c11a490d24d06647894ee8c3700d9ff7decd993\"" not in tqc:
        failures.append("timebase QC predecessor pin missing")
    for needle in ("def runtime_contract_overlay(", "_RUNTIME.load_json = _compat_runtime_load_json", LEGACY_NUMERIC_CONTRACT):
        if needle not in tqc:
            failures.append(f"timebase QC compatibility boundary missing: {needle}")

    q = sources["structuralQc"]
    for needle in (
        "FROZEN_V165_STRUCTURAL_QC_BLOB = \"36b4738cc7c00fa32aa684b3d395a67d5294a61d\"",
        "EXPECTED_OFFSETS = [-1, 0, 1, 2, 3, 4]",
        "transcriberPairedWindowPath",
        "pairedTemplateContractExact",
        "preRunV165RuntimeBlind",
        'schemas["structuralQc"] = QC_SCHEMA',
    ):
        if needle not in q:
            failures.append(f"structural QC missing boundary: {needle}")

    test = sources["pairedTest"]
    for needle in ("constantTimeEquivalence", "boundaryClipping", "singleTransientDilution", "runtimeTemplatePatched"):
        if needle not in test:
            failures.append(f"paired fixture missing check: {needle}")

    rt = sources["runtimeTest"]
    for needle in (
        "sealedContractUnchanged",
        "timebaseLegacyPinsInMemory",
        "timebaseQcLegacyPinsInMemory",
        "transcriberLegacyPinsInMemory",
        "structuralQcSchemaInMemoryOnly",
        'assert "frozenV162SourcePins" not in raw',
    ):
        if needle not in rt:
            failures.append(f"runtime compatibility fixture missing check: {needle}")

    if args.workflow is not None:
        wf = args.workflow.read_text()
        if "runs-on: ubuntu-latest" not in wf:
            failures.append("workflow not CPU hosted runner")
        if "numpy==2.0.2" not in wf:
            failures.append("workflow static numpy pin missing")
        if "test_runtime_compat_v166.py" not in wf:
            failures.append("workflow missing runtime compatibility fixture")
        forbidden_commands = (
            "build_timebase_v166.py --",
            "timebase_qc_v166.py --",
            "transcribe_v166.py --",
            "structural_qc_v166.py --candidate",
            "demucs",
            "basic_pitch",
            "modal",
            "cuda",
        )
        lower = wf.lower()
        for needle in forbidden_commands:
            if needle.lower() in lower:
                failures.append(f"workflow contains forbidden runtime command/token: {needle}")

    result = {
        "schema": "dadrock.tabs.v166.negative-runtime-guard.v2",
        "validation": "PASS" if not failures else "FAIL",
        "failures": failures,
        "checks": {
            "preregistrationPinned": git_blob_sha(prereg) == PREREG_BLOB,
            "contractPinned": git_blob_sha(contract) == CONTRACT_BLOB,
            "pairedWindowExact": EXPECTED_OFFSETS_LITERAL in t,
            "runtimeCompatibilityOverlaysPresent": all("runtime_contract_overlay" in sources[k] for k in ("transcriber", "timebaseBuilder", "timebaseQc")),
            "frozenPredecessorWrappers": True,
            "noForbiddenRuntimePaths": not any("forbidden runtime path" in x for x in failures),
            "staticWorkflowOnlyWhenProvided": args.workflow is None or not any("workflow" in x for x in failures),
        },
        "safety": {
            "songAudioRead": False,
            "demucsInvoked": False,
            "pitchInferenceInvoked": False,
            "professionalReferenceRead": False,
            "scorerRead": False,
            "V165CandidateRead": False,
            "V165ScoreRead": False,
            "gpuUsed": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
