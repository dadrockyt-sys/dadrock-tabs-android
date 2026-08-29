#!/usr/bin/env python3
"""Static negative runtime guard for the V165 implementation-only adapter repair."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

PREREG_BLOB = "1ca5c7b91263c99c0150db085d12f4c0853940b7"
CONTRACT_BLOB = "727782651e14699a0205ea97abc6e82b387299dc"
EVENT_LOGIC_BLOB = "b296b3c322c13f8963f253f9b0666db66766a178"
EVENT_TEST_BLOB = "92bacaa37b4ccc7913309d677eeb88732132376d"
TIMEBASE_BUILDER_BLOB = "62d67becb768e1e5e3e8de1cd3b121eb863b2a18"
TIMEBASE_QC_BLOB = "3c11a490d24d06647894ee8c3700d9ff7decd993"
TRANSCRIBER_BLOB = "45d595853302b077fbf4f3094e9a4922fba02435"
STRUCTURAL_QC_BLOB = "36b4738cc7c00fa32aa684b3d395a67d5294a61d"
ADAPTER_TEST_BLOB = "b7f92b0c9ade4c76472499999b63414564a68530"
JSON_TEST_BLOB = "dbff545295c97fe075462efce034f59394b6f1e3"

FROZEN_V164_EVENT_LOGIC_BLOB = "62303877a1971f75cacda002c5ad921680161674"
FROZEN_V164_TIMEBASE_BUILDER_BLOB = "170a7a15d68e271d93775c2aaba058fe3ebaa8bb"
FROZEN_V164_TIMEBASE_QC_BLOB = "e59498e76d881f22ea405c81781ca2004ea8f53e"
FROZEN_V164_TRANSCRIBER_BLOB = "df1302216df404bc3368ff820f005d6b63ae100d"
FROZEN_V164_STRUCTURAL_QC_BLOB = "c1a81c7a97e646398f5e50cbc63dae341cdc500b"

FORBIDDEN_RUNTIME_LITERALS = (
    "debug/v164-cpu-autonomous/generated.json",
    "debug/v164-cpu-autonomous/generation-receipt.json",
    "debug/v164-cpu-autonomous/timebase.json",
    "debug/v164-cpu-autonomous/timebase-qc.json",
    "debug/v164-cpu-autonomous/structural-qc.json",
    "debug/v164-cpu-autonomous/terminal-freeze.json",
    ".github/workflows/v164-generate.yml",
    "professional-reference",
    "professional_reference",
    "reference-score",
    "reference_score",
)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def require_blob(path: Path, expected: str, label: str, failures: list[str]) -> None:
    if not path.is_file():
        failures.append(f"missing {label}: {path}")
    elif git_blob_sha(path) != expected:
        failures.append(f"blob drift {label}: {git_blob_sha(path)} != {expected}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--implementation-contract", type=Path, required=True)
    parser.add_argument("--event-logic", type=Path, required=True)
    parser.add_argument("--event-test", type=Path, required=True)
    parser.add_argument("--timebase-builder", type=Path, required=True)
    parser.add_argument("--timebase-qc", type=Path, required=True)
    parser.add_argument("--transcriber", type=Path, required=True)
    parser.add_argument("--structural-qc", type=Path, required=True)
    parser.add_argument("--adapter-test", type=Path, required=True)
    parser.add_argument("--json-native-test", type=Path, required=True)
    parser.add_argument("--workflow", type=Path)
    args = parser.parse_args()

    failures: list[str] = []
    pins = [
        (args.preregistration, PREREG_BLOB, "preregistration"),
        (args.implementation_contract, CONTRACT_BLOB, "implementation contract"),
        (args.event_logic, EVENT_LOGIC_BLOB, "event logic"),
        (args.event_test, EVENT_TEST_BLOB, "event test"),
        (args.timebase_builder, TIMEBASE_BUILDER_BLOB, "timebase builder"),
        (args.timebase_qc, TIMEBASE_QC_BLOB, "timebase QC"),
        (args.transcriber, TRANSCRIBER_BLOB, "transcriber"),
        (args.structural_qc, STRUCTURAL_QC_BLOB, "structural QC"),
        (args.adapter_test, ADAPTER_TEST_BLOB, "adapter test"),
        (args.json_native_test, JSON_TEST_BLOB, "JSON test"),
    ]
    for path, expected, label in pins:
        require_blob(path, expected, label, failures)

    prereg = json.loads(args.preregistration.read_text())
    contract = json.loads(args.implementation_contract.read_text())
    if prereg.get("version") != "V165" or prereg.get("validation") != "PASS":
        failures.append("V165 preregistration state invalid")
    if contract.get("version") != "V165" or contract.get("validation") != "PASS":
        failures.append("V165 contract state invalid")
    repair = contract.get("adapterRepairContract") or {}
    if not (
        repair.get("V164AdapterSourceGitBlob") == FROZEN_V164_TRANSCRIBER_BLOB
        and repair.get("V164ExpectedOccurrenceCount") == 2
        and repair.get("pinnedFrozenSourceActualOccurrenceCount") == 3
        and repair.get("V165RequiredOccurrenceCount") == 3
        and repair.get("allThreeOccurrencesMustBeReplaced") is True
        and repair.get("noFallbackToUnboundedReplace") is True
        and repair.get("countCheckedReplacementRequired") is True
    ):
        failures.append("V165 adapter repair contract drift")

    sources = {
        "eventLogic": args.event_logic.read_text(),
        "eventTest": args.event_test.read_text(),
        "timebaseBuilder": args.timebase_builder.read_text(),
        "timebaseQc": args.timebase_qc.read_text(),
        "transcriber": args.transcriber.read_text(),
        "structuralQc": args.structural_qc.read_text(),
        "adapterTest": args.adapter_test.read_text(),
        "jsonTest": args.json_native_test.read_text(),
    }
    allowed_v164_source_adapters = {"eventLogic", "eventTest", "timebaseBuilder", "timebaseQc", "transcriber", "structuralQc", "jsonTest"}
    for label, source in sources.items():
        for literal in FORBIDDEN_RUNTIME_LITERALS:
            if literal in source:
                failures.append(f"forbidden runtime/reference literal in {label}: {literal}")
        if "validation/v164_cpu_autonomous/" in source and label not in allowed_v164_source_adapters:
            failures.append(f"unexpected V164 source adapter path in {label}")

    event = sources["eventLogic"]
    if not (
        FROZEN_V164_EVENT_LOGIC_BLOB in event
        and "_build_frozen_v164_behavior" in event
        and 'source = source.replace("V164", "V165")' in event
    ):
        failures.append("V165 event-logic frozen-adapter structure invalid")

    trans = sources["transcriber"]
    if not (
        FROZEN_V164_TRANSCRIBER_BLOB in trans
        and "V165_REQUIRED_OCCURRENCE_COUNT = 3" in trans
        and "_adapt_v164_adapter_source" in trans
        and "source.count(old) != 1" in trans
        and "source.replace(old, new)" in trans
        and "'event_logic_v162.py', 'event_logic_v165.py', " in trans
        and '"3, \\"event-logic provenance path\\")"' not in trans
    ):
        # Last condition above intentionally rejects no special content; detailed count is exercised dynamically by adapter test.
        failures.append("V165 transcriber repair structure invalid")

    if FROZEN_V164_TIMEBASE_BUILDER_BLOB not in sources["timebaseBuilder"]:
        failures.append("V165 timebase builder does not pin V164 source")
    if FROZEN_V164_TIMEBASE_QC_BLOB not in sources["timebaseQc"]:
        failures.append("V165 timebase QC does not pin V164 source")
    if FROZEN_V164_STRUCTURAL_QC_BLOB not in sources["structuralQc"]:
        failures.append("V165 structural QC does not pin V164 source")

    adapter_test = sources["adapterTest"]
    if not (
        "frozen_source.count(\"event_logic_v162.py\") == 3" in adapter_test
        and "transcriber.build_adapted_module()" in adapter_test
        and "callable(adapted.main)" in adapter_test
        and "adapted.main()" not in adapter_test
        and '"songAudioRead": False' in adapter_test
        and '"pitchInferenceInvoked": False' in adapter_test
        and '"V164RuntimeArtifactRead": False' in adapter_test
    ):
        failures.append("V165 adapter-construction fixture boundary invalid")

    runtime_paths = [
        Path("debug/v165-cpu-autonomous/timebase.json"),
        Path("debug/v165-cpu-autonomous/timebase-qc.json"),
        Path("debug/v165-cpu-autonomous/generated.json"),
        Path("debug/v165-cpu-autonomous/generation-receipt.json"),
        Path("debug/v165-cpu-autonomous/structural-qc.json"),
        Path("debug/v165-cpu-autonomous/terminal-freeze.json"),
        Path(".github/workflows/v165-generate.yml"),
    ]
    if any(path.exists() for path in runtime_paths):
        failures.append("V165 runtime artifact/generation workflow exists before static seal")

    workflow_ok = True
    if args.workflow is not None:
        if not args.workflow.is_file():
            workflow_ok = False
            failures.append("V165 static workflow missing")
        else:
            workflow = args.workflow.read_text()
            required = (
                "V165 CPU Static Preflight",
                "v143-contextual-prune-lobo",
                "python validation/v165_cpu_autonomous/test_event_logic_v165.py",
                "python validation/v165_cpu_autonomous/test_transcriber_adapter_v165.py",
                "python validation/v165_cpu_autonomous/test_json_native_v165.py",
                "python debug/v165-cpu-autonomous/negative-runtime-guard.py",
            )
            if not all(item in workflow for item in required):
                workflow_ok = False
                failures.append("V165 static workflow missing required CPU/static command")
            forbidden_commands = (
                "python validation/v165_cpu_autonomous/build_timebase_v165.py",
                "python validation/v165_cpu_autonomous/timebase_qc_v165.py",
                "python validation/v165_cpu_autonomous/transcribe_v165.py",
                "python validation/v165_cpu_autonomous/structural_qc_v165.py",
                "demucs.separate",
                "basic_pitch",
                "modal",
                "cuda",
            )
            for item in forbidden_commands:
                if item in workflow.lower():
                    workflow_ok = False
                    failures.append(f"V165 static workflow contains forbidden runtime command: {item}")

    result = {
        "schema": "dadrock.tabs.v165.negative-runtime-guard.v1",
        "validation": "PASS" if not failures else "FAIL",
        "failures": failures,
        "checks": {
            "preCodeSealsExact": all(git_blob_sha(path) == expected for path, expected, _ in pins[:2]),
            "implementationPinsExact": all(path.is_file() and git_blob_sha(path) == expected for path, expected, _ in pins[2:]),
            "adapterRepairContractExact": not any("adapter repair contract" in f for f in failures),
            "frozenV164AdaptersPinned": not any("does not pin V164" in f for f in failures),
            "songBlindAdapterConstructionFixturePresent": not any("adapter-construction fixture" in f for f in failures),
            "runtimeArtifactsAbsent": not any("runtime artifact" in f for f in failures),
            "noReferenceOrV164RuntimePaths": not any("forbidden runtime/reference literal" in f for f in failures),
            "staticWorkflowCpuOnly": workflow_ok,
        },
        "safety": {
            "songAudioRead": False,
            "normalizationExecuted": False,
            "demucsInvoked": False,
            "pitchInferenceInvoked": False,
            "professionalReferenceRead": False,
            "frozenScorerRead": False,
            "V163CandidateRead": False,
            "V163ScoreRead": False,
            "V164RuntimeArtifactRead": False,
            "gpuUsed": False,
        },
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
