#!/usr/bin/env python3
"""Independent reference-blind structural QC for the single V158 CPU candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

EXPECTED_PREREG_BLOB = "728cf28646db225f3c266a4bb73a6112b1f60330"
EXPECTED_CONTRACT_BLOB = "68f01df155cd27077cea3de5a0cd048ddcb7bd76"
EXPECTED_RESOLUTION_BLOB = "b4b6a5c1f8a88d359a981eb1238907805f2fc2a9"
EXPECTED_BASE_HELPER_BLOB = "5617ff1a6ea301ecaeb898b123b05d2a8c915388"
EXPECTED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_NORMALIZED_WAV_SHA256 = "3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e"

CANDIDATE_SCHEMA = "dadrock.tabs.v158.cpu-sequential-onset-first-generated.v1"
RECEIPT_SCHEMA = "dadrock.tabs.v158.cpu-generation-receipt.v1"
ENV_SCHEMA = "dadrock.tabs.v158.cpu-environment-receipt.v1"
QC_SCHEMA = "dadrock.tabs.v158.reference-blind-structural-qc.v1"
PRE_RUN_SCHEMA = "dadrock.tabs.v158.pre-run-identity-receipt.v1"
RESOLUTION_SCHEMA = "dadrock.tabs.v158.sparse-pursuit-contract-resolution.v1"

RANGES = {"combinedGuitar": (40, 88), "bass": (28, 67)}
ALLOWED_SOURCES = {
    "combinedGuitar": {"basic_pitch", "harmonic_track"},
    "bass": {"onset_harmonic_pyin"},
}
FORBIDDEN_GUITAR_SOURCES = {"cqt", "cqt_only", "single_frame_cqt"}
EXPECTED_EVENT_FIELDS = [
    "measure",
    "step",
    "midi",
    "startSeconds",
    "rawGridStep",
    "absoluteGridStep",
    "source",
]
EXPECTED_DEPS = {
    "numpy": "1.26.4",
    "scipy": "1.13.1",
    "librosa": "0.11.0",
    "soundfile": "0.12.1",
    "imageio-ffmpeg": "0.6.0",
    "demucs": "4.1.0",
    "basic-pitch": "0.4.0",
    "torch": "2.8.0+cpu",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def fail(message: str) -> None:
    raise RuntimeError(f"V158 structural QC failure: {message}")


def require_file(path: Path) -> None:
    if not path.is_file():
        fail(f"missing input {path}")


def validate_safety(label: str, payload: dict[str, Any]) -> None:
    required_false = (
        "referenceRead",
        "priorGeneratedCandidateRead",
        "priorScoreOrDiagnosticRead",
        "referenceGuidedFiltering",
        "thresholdSweep",
        "variantSelection",
        "humanCorrection",
        "cudaGpuUsed",
        "modalUsed",
        "mainOrProductionModified",
    )
    for key in required_false:
        if payload.get(key) is not False:
            fail(f"{label} safety {key}")
    if payload.get("professionalReferencePathsOpened") != 0:
        fail(f"{label} professionalReferencePathsOpened")
    if payload.get("referenceFacingScoreCalls") != 0:
        fail(f"{label} referenceFacingScoreCalls")


def validate_environment(environment: dict[str, Any]) -> None:
    if environment.get("schema") != ENV_SCHEMA or environment.get("validation") != "PASS":
        fail("environment receipt schema/state")
    if environment.get("device") != "cpu" or environment.get("cudaAvailable") is not False or environment.get("torchCudaVersion") is not None:
        fail("environment is not confirmed CPU-only")
    if environment.get("sourceAudioSha256") != EXPECTED_AUDIO_SHA256:
        fail("source audio identity")
    if environment.get("normalizedWavSha256") != EXPECTED_NORMALIZED_WAV_SHA256:
        fail("normalized WAV identity")
    if environment.get("workflowRunNumber") != 1 or environment.get("generationWorkflowRunCount") != 1:
        fail("single generation workflow run invariant")
    if environment.get("demucsModel") != "htdemucs_6s" or environment.get("demucsShifts") != 1 or environment.get("demucsJobs") != 1:
        fail("Demucs contract drift")

    versions = environment.get("versions") or {}
    for package, expected in EXPECTED_DEPS.items():
        if str(versions.get(package)) != expected:
            fail(f"dependency drift {package}: {versions.get(package)!r} != {expected!r}")
    if not str(versions.get("python", "")).startswith("3.10"):
        fail(f"python drift: {versions.get('python')!r}")

    determinism = environment.get("determinism") or {}
    expected_determinism = {
        "seed": 0,
        "pythonRandomSeed": 0,
        "numpyRandomSeed": 0,
        "torchManualSeed": 0,
        "torchDeterministicAlgorithms": True,
        "torchDeterministicWarnOnly": False,
        "torchNumThreads": 1,
        "torchNumInteropThreads": 1,
        "ompNumThreads": 1,
        "mklNumThreads": 1,
        "openblasNumThreads": 1,
        "numexprNumThreads": 1,
        "separationRepeatCount": 1,
    }
    for key, expected in expected_determinism.items():
        if determinism.get(key) != expected:
            fail(f"determinism drift {key}: {determinism.get(key)!r}")
    if determinism.get("demucsInvocation") != "in-process demucs.separate.main":
        fail("Demucs invocation drift")

    model_blobs = environment.get("demucsModelBlobFiles")
    if not isinstance(model_blobs, list) or not model_blobs:
        fail("missing resolved Demucs model blob receipt")
    resolved_seen: set[str] = set()
    for item in model_blobs:
        if not isinstance(item, dict):
            fail("invalid Demucs model blob record")
        logical = item.get("logicalPath")
        resolved = item.get("resolvedPath")
        digest = item.get("sha256")
        size = item.get("bytes")
        if not isinstance(logical, str) or not logical or not isinstance(resolved, str) or not resolved:
            fail("invalid Demucs model blob paths")
        if not valid_sha256(digest):
            fail("invalid Demucs model blob sha256")
        if not isinstance(size, int) or size < 1048576:
            fail("invalid Demucs model blob size")
        if resolved in resolved_seen:
            fail("duplicate resolved Demucs model blob")
        resolved_seen.add(resolved)


def validate_streams(candidate: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    streams = candidate.get("streams") or {}
    if set(streams) != {"combinedGuitar", "bass"}:
        fail("unexpected stream set")
    required_fields = (contract.get("structuralQcContract") or {}).get("eventRequiredFields") or []
    if required_fields != EXPECTED_EVENT_FIELDS:
        fail("event-required-fields contract drift")
    metadata = candidate.get("streamMetadata") or {}
    stats: dict[str, Any] = {}

    for stream, (midi_low, midi_high) in RANGES.items():
        rows = streams.get(stream)
        if not isinstance(rows, list) or not rows:
            fail(f"empty {stream} stream")
        seen: set[tuple[int, int]] = set()
        previous_sort: tuple[int, int, str] | None = None
        sources: dict[str, int] = {}
        retained_bass_onsets = (metadata.get("bass") or {}).get("retainedOnsetCount")

        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                fail(f"{stream}[{index}] is not an object")
            for field in required_fields:
                if field not in row:
                    fail(f"{stream}[{index}] missing {field}")
            if not isinstance(row.get("measure"), int) or row["measure"] < 1:
                fail(f"{stream}[{index}] invalid measure")
            if not isinstance(row.get("step"), int) or not 0 <= row["step"] <= 15:
                fail(f"{stream}[{index}] invalid step")
            if not isinstance(row.get("absoluteGridStep"), int) or row["absoluteGridStep"] < 0:
                fail(f"{stream}[{index}] invalid absoluteGridStep")
            if row["measure"] != row["absoluteGridStep"] // 16 + 1 or row["step"] != row["absoluteGridStep"] % 16:
                fail(f"{stream}[{index}] measure/step mismatch")
            if not finite_number(row.get("startSeconds")) or float(row["startSeconds"]) < 0:
                fail(f"{stream}[{index}] invalid startSeconds")
            if not finite_number(row.get("rawGridStep")):
                fail(f"{stream}[{index}] invalid rawGridStep")
            if not isinstance(row.get("midi"), int) or not midi_low <= row["midi"] <= midi_high:
                fail(f"{stream}[{index}] MIDI range")

            source = row.get("source")
            if source not in ALLOWED_SOURCES[stream]:
                fail(f"{stream}[{index}] source {source!r}")
            if stream == "combinedGuitar":
                if source in FORBIDDEN_GUITAR_SOURCES:
                    fail(f"forbidden Guitar source {source!r}")
                if source == "harmonic_track":
                    if row.get("persistentTrackFrames") != 3:
                        fail(f"combinedGuitar[{index}] persistence provenance")
                    if not finite_number(row.get("sparsePursuitGain")) or float(row["sparsePursuitGain"]) <= 0:
                        fail(f"combinedGuitar[{index}] sparse-pursuit provenance")
            else:
                proposal = row.get("onsetProposalIndex")
                onset_frame = row.get("onsetFrame")
                if not isinstance(proposal, int) or proposal < 0 or not isinstance(onset_frame, int) or onset_frame < 0:
                    fail(f"bass[{index}] missing onset provenance")
                if not isinstance(retained_bass_onsets, int) or proposal >= retained_bass_onsets:
                    fail(f"bass[{index}] onset provenance out of range")

            dedupe_key = (row["absoluteGridStep"], row["midi"])
            if dedupe_key in seen:
                fail(f"{stream} duplicate dedupe key {dedupe_key}")
            seen.add(dedupe_key)
            sort_key = (row["absoluteGridStep"], row["midi"], str(source))
            if previous_sort is not None and sort_key < previous_sort:
                fail(f"{stream} output sort order")
            previous_sort = sort_key
            sources[str(source)] = sources.get(str(source), 0) + 1

        stats[stream] = {
            "count": len(rows),
            "sources": sources,
            "midiMin": min(int(row["midi"]) for row in rows),
            "midiMax": max(int(row["midi"]) for row in rows),
        }
    return stats


def validate_timebase(candidate: dict[str, Any]) -> dict[str, Any]:
    timebase = candidate.get("timebase") or {}
    beat_times = timebase.get("beatTimesSeconds")
    beat_steps = timebase.get("beatGridSteps")
    states = timebase.get("viterbiBarStates")
    if not isinstance(beat_times, list) or len(beat_times) < 8:
        fail("invalid beat times")
    if not isinstance(beat_steps, list) or len(beat_steps) != len(beat_times):
        fail("beat grid length")
    if not isinstance(states, list) or len(states) != len(beat_times):
        fail("Viterbi path length != beat count")
    if any(not finite_number(value) for value in beat_times + beat_steps):
        fail("nonfinite beat grid")
    if any(float(later) <= float(earlier) for earlier, later in zip(beat_times, beat_times[1:])):
        fail("beat times not strictly increasing")
    if any(not isinstance(state, int) or state not in {0, 1, 2, 3} for state in states):
        fail("invalid Viterbi state")
    for first_step, second_step, first_state, second_state in zip(beat_steps, beat_steps[1:], states, states[1:]):
        state_delta = (second_state - first_state) % 4
        if state_delta not in {0, 1, 2}:
            fail("invalid Viterbi transition")
        if abs((float(second_step) - float(first_step)) - 4.0 * state_delta) > 1e-9:
            fail("beat grid/state transition mismatch")
    embedded_qc = timebase.get("qc") or {}
    if embedded_qc.get("beatCount") != len(beat_times) or embedded_qc.get("statePathLength") != len(states):
        fail("timebase QC count mismatch")
    if embedded_qc.get("strictlyIncreasingBeatTimes") is not True:
        fail("timebase increasing flag")
    return {
        "beatCount": len(beat_times),
        "statePathLength": len(states),
        "stateCounts": {str(state): states.count(state) for state in range(4)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--environment-receipt", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--implementation-contract", type=Path, required=True)
    parser.add_argument("--sparse-pursuit-resolution", type=Path, required=True)
    parser.add_argument("--pre-run-receipt", type=Path, required=True)
    parser.add_argument("--transcriber", type=Path, required=True)
    parser.add_argument("--base-helper", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists():
        fail("QC output is write-once")
    for path in (
        args.candidate,
        args.receipt,
        args.environment_receipt,
        args.preregistration,
        args.implementation_contract,
        args.sparse_pursuit_resolution,
        args.pre_run_receipt,
        args.transcriber,
        args.base_helper,
    ):
        require_file(path)

    candidate = json.loads(args.candidate.read_text())
    receipt = json.loads(args.receipt.read_text())
    environment = json.loads(args.environment_receipt.read_text())
    preregistration = json.loads(args.preregistration.read_text())
    contract = json.loads(args.implementation_contract.read_text())
    resolution = json.loads(args.sparse_pursuit_resolution.read_text())
    pre_run = json.loads(args.pre_run_receipt.read_text())

    if candidate.get("schema") != CANDIDATE_SCHEMA:
        fail("candidate schema")
    if receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("validation") != "PENDING_INDEPENDENT_STRUCTURAL_QC":
        fail("generation receipt schema/state")
    if preregistration.get("version") != "V158" or preregistration.get("status") != "PREREGISTERED_BEFORE_GENERATION":
        fail("preregistration status")
    if contract.get("version") != "V158" or contract.get("status") != "SEALED_BEFORE_GENERATION_CODE":
        fail("implementation contract status")
    if resolution.get("schema") != RESOLUTION_SCHEMA or resolution.get("status") != "SEALED_BEFORE_CANONICAL_EXECUTION_CODE":
        fail("sparse-pursuit resolution status")
    if pre_run.get("schema") != PRE_RUN_SCHEMA or pre_run.get("version") != "V158" or pre_run.get("validation") != "PASS" or pre_run.get("status") != "SEALED_BEFORE_GENERATION":
        fail("pre-run receipt schema/state")

    if git_blob_sha(args.preregistration) != EXPECTED_PREREG_BLOB:
        fail("preregistration Git blob drift")
    if git_blob_sha(args.implementation_contract) != EXPECTED_CONTRACT_BLOB:
        fail("implementation contract Git blob drift")
    if git_blob_sha(args.sparse_pursuit_resolution) != EXPECTED_RESOLUTION_BLOB:
        fail("sparse-pursuit resolution Git blob drift")
    if git_blob_sha(args.base_helper) != EXPECTED_BASE_HELPER_BLOB:
        fail("base-helper Git blob drift")

    schemas = contract.get("canonicalSchemas") or {}
    expected_schemas = {
        "candidate": CANDIDATE_SCHEMA,
        "generationReceipt": RECEIPT_SCHEMA,
        "environmentReceipt": ENV_SCHEMA,
        "structuralQc": QC_SCHEMA,
        "preRunReceipt": PRE_RUN_SCHEMA,
    }
    if any(schemas.get(key) != value for key, value in expected_schemas.items()):
        fail("canonical schema contract drift")

    transcriber_blob = git_blob_sha(args.transcriber)
    qc_blob = git_blob_sha(Path(__file__))
    pins = pre_run.get("pinnedGitBlobs") or {}
    expected_pins = {
        "preregistration": EXPECTED_PREREG_BLOB,
        "implementationContract": EXPECTED_CONTRACT_BLOB,
        "sparsePursuitResolution": EXPECTED_RESOLUTION_BLOB,
        "transcriber": transcriber_blob,
        "baseHelper": EXPECTED_BASE_HELPER_BLOB,
        "structuralQc": qc_blob,
    }
    for key, expected in expected_pins.items():
        if pins.get(key) != expected:
            fail(f"pre-run pin drift {key}")

    if pre_run.get("candidateExistsAtSeal") is not False:
        fail("candidate existed at pre-run seal")
    if pre_run.get("generationReceiptAbsentAtSeal") is not True or pre_run.get("environmentReceiptAbsentAtSeal") is not True or pre_run.get("generationWorkflowAbsentAtSeal") is not True:
        fail("pre-run absence boundary")
    if pre_run.get("referenceReadAtSeal") is not False or pre_run.get("professionalReferencePathsOpenedAtSeal") != 0 or pre_run.get("referenceFacingScoreCallsAtSeal") != 0:
        fail("pre-run reference boundary")
    trigger = pre_run.get("triggerSafety") or {}
    if trigger.get("generationWorkflowCreationIsSingleTrigger") is not True or trigger.get("secondArmEditForbidden") is not True:
        fail("pre-run trigger safety")
    if trigger.get("expectedGenerationWorkflowRunCount") != 1 or trigger.get("workflowMustSelfSealAfterSuccessfulFreeze") is not True:
        fail("pre-run workflow-count/freeze contract")
    if trigger.get("duplicateRunAction") != "ABORT_V158_WITHOUT_SCORING":
        fail("pre-run duplicate-run policy")

    if receipt.get("candidateSha256") != sha256(args.candidate):
        fail("candidate SHA receipt mismatch")
    if receipt.get("preregistrationSha256") != sha256(args.preregistration):
        fail("preregistration SHA receipt mismatch")
    if receipt.get("implementationContractSha256") != sha256(args.implementation_contract):
        fail("implementation-contract SHA receipt mismatch")
    if receipt.get("sparsePursuitResolutionSha256") != sha256(args.sparse_pursuit_resolution):
        fail("sparse-pursuit-resolution SHA receipt mismatch")
    if receipt.get("preRunReceiptSha256") != sha256(args.pre_run_receipt):
        fail("pre-run receipt SHA linkage")
    if receipt.get("environmentReceiptSha256") != sha256(args.environment_receipt):
        fail("environment receipt SHA linkage")
    if receipt.get("environment") != environment:
        fail("embedded environment does not equal environment receipt")

    sealed_inputs = candidate.get("sealedInputs") or {}
    expected_candidate_pins = {
        "preregistrationGitBlob": EXPECTED_PREREG_BLOB,
        "implementationContractGitBlob": EXPECTED_CONTRACT_BLOB,
        "sparsePursuitResolutionGitBlob": EXPECTED_RESOLUTION_BLOB,
        "canonicalEntryPointGitBlob": transcriber_blob,
        "baseHelperGitBlob": EXPECTED_BASE_HELPER_BLOB,
        "structuralQcGitBlob": qc_blob,
        "preRunReceiptSha256": sha256(args.pre_run_receipt),
    }
    for key, expected in expected_candidate_pins.items():
        if sealed_inputs.get(key) != expected:
            fail(f"candidate sealed-input drift {key}")

    implementation = receipt.get("implementation") or {}
    expected_implementation = {
        "canonicalEntryPointGitBlob": transcriber_blob,
        "baseHelperGitBlob": EXPECTED_BASE_HELPER_BLOB,
        "structuralQcGitBlob": qc_blob,
        "sparsePursuitResolutionGitBlob": EXPECTED_RESOLUTION_BLOB,
    }
    for key, expected in expected_implementation.items():
        if implementation.get(key) != expected:
            fail(f"generation receipt implementation drift {key}")

    validate_safety("candidate", candidate.get("safety") or {})
    validate_safety("receipt", receipt.get("safety") or {})
    validate_environment(environment)
    input_identities = receipt.get("inputIdentities") or {}
    if input_identities.get("mixSha256") != EXPECTED_NORMALIZED_WAV_SHA256:
        fail("generation mix identity")
    for key in ("guitarStemSha256", "bassStemSha256", "drumsStemSha256"):
        if not valid_sha256(input_identities.get(key)):
            fail(f"invalid stem identity {key}")

    stream_stats = validate_streams(candidate, contract)
    counts = receipt.get("counts") or {}
    for stream in ("combinedGuitar", "bass"):
        if counts.get(stream) != stream_stats[stream]["count"]:
            fail(f"receipt count mismatch {stream}")
    guitar_metadata = (candidate.get("streamMetadata") or {}).get("combinedGuitar") or {}
    if guitar_metadata.get("sparsePursuitResolutionGitBlob") != EXPECTED_RESOLUTION_BLOB:
        fail("Guitar sparse-pursuit resolution provenance")
    timebase_stats = validate_timebase(candidate)

    report = {
        "schema": QC_SCHEMA,
        "version": "V158",
        "validation": "PASS",
        "candidatePath": str(args.candidate),
        "candidateSha256": sha256(args.candidate),
        "generationReceiptPath": str(args.receipt),
        "generationReceiptSha256": sha256(args.receipt),
        "environmentReceiptPath": str(args.environment_receipt),
        "environmentReceiptSha256": sha256(args.environment_receipt),
        "preRunReceiptPath": str(args.pre_run_receipt),
        "preRunReceiptSha256": sha256(args.pre_run_receipt),
        "pinnedGitBlobs": {
            "preregistration": EXPECTED_PREREG_BLOB,
            "implementationContract": EXPECTED_CONTRACT_BLOB,
            "sparsePursuitResolution": EXPECTED_RESOLUTION_BLOB,
            "transcriber": transcriber_blob,
            "baseHelper": EXPECTED_BASE_HELPER_BLOB,
            "structuralQc": qc_blob,
        },
        "streamStats": stream_stats,
        "timebaseStats": timebase_stats,
        "environmentIdentity": {
            "device": environment.get("device"),
            "versions": environment.get("versions"),
            "demucsModel": environment.get("demucsModel"),
            "demucsModelBlobFiles": environment.get("demucsModelBlobFiles"),
            "workflowRunNumber": environment.get("workflowRunNumber"),
            "generationWorkflowRunCount": environment.get("generationWorkflowRunCount"),
        },
        "safety": {
            "referenceRead": False,
            "professionalReferencePathsOpened": 0,
            "referenceFacingScoreCalls": 0,
            "professionalQualityMetricUsed": False,
            "humanCorrection": False,
            "thresholdSweep": False,
            "variantSelection": False,
            "gpuUsed": False,
            "mainOrProductionModified": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
