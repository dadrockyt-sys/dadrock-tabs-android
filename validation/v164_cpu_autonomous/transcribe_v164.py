#!/usr/bin/env python3
"""V164 CPU transcriber adapter over the exact frozen V162 transcriber.

Only onset/subdivision normalization paths are changed. The adapter verifies the
frozen V162 source identities, performs count-checked source substitutions for
V164 local q95 onset admission provenance, then patches locality-sensitive pure
helpers and the runtime boundary. No song/reference/scorer I/O occurs at import.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import types
from pathlib import Path
from typing import Any

import numpy as np

import event_logic_v164 as v164

CANDIDATE_SCHEMA = "dadrock.tabs.v164.local-evidence-generated.v1"
RECEIPT_SCHEMA = "dadrock.tabs.v164.cpu-generation-receipt.v1"
TIMEBASE_SCHEMA = "dadrock.tabs.v164.local-evidence-timebase.v1"
TIMEBASE_QC_SCHEMA = "dadrock.tabs.v164.local-evidence-timebase-qc.v1"
PRE_RUN_SCHEMA = "dadrock.tabs.v164.pre-run-identity-receipt.v1"
ENV_SCHEMA = "dadrock.tabs.v164.cpu-environment-receipt.v1"

V162_TRANSCRIBER_BLOB = "fa163cafe2131aa73cdbb50df10d4e4912cff53b"
V162_EVENT_LOGIC_BLOB = "9f9b33fd8c210ad581025b454cf69b6999aa544b"
V162_CONTRACT_BLOB = "409da313ed03a6c232d6578d48b0da6aa35b000b"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def replace_exact(source: str, old: str, new: str, expected_count: int, label: str) -> str:
    count = source.count(old)
    if count != expected_count:
        raise RuntimeError(f"V164 frozen-source transform drift for {label}: expected {expected_count}, found {count}")
    return source.replace(old, new)


def _local_admission_support(env: np.ndarray, center_frame: int) -> tuple[float, dict[str, Any]]:
    x = np.asarray(env, dtype=float)
    center = int(np.clip(int(center_frame), 0, len(x) - 1))
    support, provenance = v164.local_support_unit(float(x[center]), x, center)
    return float(support), {
        "centerFrame": center,
        "loFrame": int(provenance["loFrame"]),
        "hiFrame": int(provenance["hiFrame"]),
        "positiveCount": int(provenance["positiveCount"]),
        "supportScale": provenance["supportScale"],
    }


def validate_runtime_boundary(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    prereg = load_json(args.preregistration)
    contract = load_json(args.implementation_contract)
    timebase = load_json(args.timebase)
    qc = load_json(args.timebase_qc)
    pre_run = load_json(args.pre_run_receipt)
    environment = load_json(args.environment_receipt)
    if prereg.get("version") != "V164" or prereg.get("status") != "PREREGISTERED_BEFORE_NUMERIC_CONTRACT_OR_IMPLEMENTATION_CODE":
        raise RuntimeError("V164 preregistration state invalid")
    if contract.get("version") != "V164" or contract.get("status") != "SEALED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("V164 implementation-contract state invalid")
    schemas = contract.get("canonicalSchemas") or {}
    if timebase.get("schema") != TIMEBASE_SCHEMA or timebase.get("version") != "V164" or schemas.get("timebase") != TIMEBASE_SCHEMA:
        raise RuntimeError("V164 timebase schema/version invalid")
    if schemas.get("candidate") != CANDIDATE_SCHEMA or schemas.get("generationReceipt") != RECEIPT_SCHEMA:
        raise RuntimeError("V164 candidate/generation schema contract drift")
    if qc.get("schema") != TIMEBASE_QC_SCHEMA or schemas.get("timebaseQc") != TIMEBASE_QC_SCHEMA or qc.get("validation") != "PASS":
        raise RuntimeError("V164 timebase QC is not frozen PASS")
    if qc.get("timebaseSha256") != sha256_file(args.timebase):
        raise RuntimeError("V164 timebase differs from PASS QC receipt")
    if qc.get("implementationContractSha256") != sha256_file(args.implementation_contract) or qc.get("preregistrationSha256") != sha256_file(args.preregistration):
        raise RuntimeError("V164 timebase-QC provenance drift")
    if pre_run.get("schema") != PRE_RUN_SCHEMA or schemas.get("preRunReceipt") != PRE_RUN_SCHEMA or pre_run.get("validation") != "PASS":
        raise RuntimeError("V164 pre-run identity receipt invalid")
    if environment.get("schema") != ENV_SCHEMA or schemas.get("environmentReceipt") != ENV_SCHEMA or environment.get("validation") != "PASS" or environment.get("device") != "cpu":
        raise RuntimeError("V164 environment receipt invalid")
    if environment.get("cudaAvailable") is not False or environment.get("torchCudaVersion") is not None:
        raise RuntimeError("V164 environment is not CPU-only")

    frozen = contract.get("frozenV162SourcePins") or {}
    if frozen.get("numericContract") != V162_CONTRACT_BLOB or frozen.get("eventLogic") != V162_EVENT_LOGIC_BLOB or frozen.get("transcriber") != V162_TRANSCRIBER_BLOB:
        raise RuntimeError("V164 frozen V162 transcriber pins drift")
    pins = pre_run.get("pinnedGitBlobs") or {}
    expected = {
        "preregistration": git_blob_sha(args.preregistration),
        "implementationContract": git_blob_sha(args.implementation_contract),
        "eventLogic": git_blob_sha(Path(__file__).with_name("event_logic_v164.py")),
        "transcriber": git_blob_sha(Path(__file__)),
        "timebaseBuilder": git_blob_sha(Path(__file__).with_name("build_timebase_v164.py")),
        "timebaseQc": git_blob_sha(Path(__file__).with_name("timebase_qc_v164.py")),
    }
    for key, value in expected.items():
        if pins.get(key) != value:
            raise RuntimeError(f"V164 pre-run pin drift: {key}")
    for key in ("timebaseMustNotExistAtSeal", "timebaseQcReceiptMustNotExistAtSeal", "candidateMustNotExistAtSeal", "generationReceiptMustNotExistAtSeal"):
        if pre_run.get(key) is not True:
            raise RuntimeError(f"V164 pre-run absence boundary invalid: {key}")
    if (
        pre_run.get("referenceReadAtSeal") is not False
        or pre_run.get("professionalReferencePathsOpenedAtSeal") != 0
        or pre_run.get("V163CandidateReadAtSeal") is not False
        or pre_run.get("V163ScoreReadAtSeal") is not False
    ):
        raise RuntimeError("V164 pre-run reference/V163 boundary invalid")

    timebase_safety = timebase.get("safety") or {}
    if not (
        timebase_safety.get("referenceRead") is False
        and timebase_safety.get("professionalReferencePathsOpened") == 0
        and timebase_safety.get("priorGeneratedCandidateRead") is False
        and timebase_safety.get("priorScoreRead") is False
        and timebase_safety.get("V163CandidateRead") is False
        and timebase_safety.get("V163ScoreRead") is False
        and timebase_safety.get("gpu") is False
    ):
        raise RuntimeError("V164 timebase safety boundary invalid")
    qc_safety = qc.get("safety") or {}
    if not (
        qc_safety.get("referenceRead") is False
        and qc_safety.get("professionalReferencePathsOpened") == 0
        and qc_safety.get("pitchInferenceInvoked") is False
        and qc_safety.get("V163CandidateRead") is False
        and qc_safety.get("V163ScoreRead") is False
        and qc_safety.get("gpuUsed") is False
    ):
        raise RuntimeError("V164 timebase-QC safety boundary invalid")

    for name, path in {"guitar": args.guitar, "bass": args.bass, "drums": args.drums}.items():
        record = (timebase.get("stemIdentities") or {}).get(name) or {}
        if record.get("sha256") != sha256_file(path) or record.get("bytes") != path.stat().st_size:
            raise RuntimeError(f"V164 {name} stem differs from frozen timebase")
    mix_record = (timebase.get("audioIdentity") or {}).get("normalizedMix") or {}
    if mix_record.get("sha256") != sha256_file(args.mix) or mix_record.get("bytes") != args.mix.stat().st_size:
        raise RuntimeError("V164 normalized mix differs from frozen timebase")
    subdivisions = np.asarray(timebase.get("subdivisionTimesSeconds", []), dtype=float)
    steps = np.asarray(timebase.get("subdivisionAbsoluteSteps", []), dtype=int)
    if (
        len(subdivisions) < 5
        or (len(subdivisions) - 1) % 4 != 0
        or len(subdivisions) != len(steps)
        or not np.all(np.isfinite(subdivisions))
        or not np.all(np.diff(subdivisions) > 0.0)
        or not np.array_equal(steps, np.arange(len(steps), dtype=int))
    ):
        raise RuntimeError("V164 frozen subdivision lattice invalid")
    return prereg, contract, timebase, environment


def build_adapted_module() -> types.ModuleType:
    repo = Path(__file__).resolve().parents[2]
    v162_path = repo / "validation/v162_cpu_autonomous/transcribe_v162.py"
    v162_event = repo / "validation/v162_cpu_autonomous/event_logic_v162.py"
    v162_contract = repo / "debug/v162-cpu-autonomous/implementation-contract.json"
    if git_blob_sha(v162_path) != V162_TRANSCRIBER_BLOB:
        raise RuntimeError("V164 frozen V162 transcriber dependency drift")
    if git_blob_sha(v162_event) != V162_EVENT_LOGIC_BLOB:
        raise RuntimeError("V164 frozen V162 event-logic dependency drift")
    if git_blob_sha(v162_contract) != V162_CONTRACT_BLOB:
        raise RuntimeError("V164 frozen V162 numeric-contract dependency drift")

    source = v162_path.read_text()
    old_support = "        onset_support = support_unit(float(env[min(refined_frame, len(env) - 1)]), env)\n"
    new_support = "        onset_support, onset_provenance = _v164_local_support_at_frame(env, refined_frame)\n"
    source = replace_exact(source, old_support, new_support, 2, "local onset admission support")
    old_metadata = '            "onsetSupport": onset_support,\n'
    new_metadata = '            "onsetSupport": onset_support,\n            "onsetNormalization": onset_provenance,\n'
    source = replace_exact(source, old_metadata, new_metadata, 2, "local onset admission provenance")
    source = replace_exact(source, 'event_logic_v162.py', 'event_logic_v164.py', 2, "event-logic provenance path")
    source = replace_exact(source, '"V161CandidateRead"', '"V163CandidateRead"', 2, "predecessor safety key")
    old_safety = '        "V163CandidateRead": False,\n'
    new_safety = '        "V163CandidateRead": False,\n        "V163ScoreRead": False,\n'
    source = replace_exact(source, old_safety, new_safety, 1, "V163 score safety key")
    old_candidate = '    candidate = {\n        "schema": CANDIDATE_SCHEMA,\n'
    new_candidate = '    candidate = {\n        "schema": CANDIDATE_SCHEMA,\n        "version": "V164",\n'
    source = replace_exact(source, old_candidate, new_candidate, 1, "candidate version")
    source = replace_exact(
        source,
        '"single-preregistered-reference-blind-v162-cpu-state-segmented-subdivision-candidate"',
        '"single-preregistered-reference-blind-v164-cpu-local-evidence-candidate"',
        1,
        "candidate classification",
    )
    source = replace_exact(
        source,
        '        "version": "V162",\n        "validation": "PENDING_INDEPENDENT_STRUCTURAL_QC",\n',
        '        "version": "V164",\n        "validation": "PENDING_INDEPENDENT_STRUCTURAL_QC",\n',
        1,
        "generation receipt version",
    )
    source = source.replace("V162", "V164")

    module = types.ModuleType("_dadrock_v164_adapted_transcriber")
    module.__file__ = str(Path(__file__).resolve())
    module.__dict__["__builtins__"] = __builtins__
    parent = str(v162_path.parent)
    inserted = parent not in sys.path
    if inserted:
        sys.path.insert(0, parent)
    try:
        exec(compile(source, str(v162_path), "exec"), module.__dict__)
    finally:
        if inserted:
            sys.path.remove(parent)

    module.CANDIDATE_SCHEMA = CANDIDATE_SCHEMA
    module.RECEIPT_SCHEMA = RECEIPT_SCHEMA
    module.TIMEBASE_SCHEMA = TIMEBASE_SCHEMA
    module.TIMEBASE_QC_SCHEMA = TIMEBASE_QC_SCHEMA
    module.PRE_RUN_SCHEMA = PRE_RUN_SCHEMA
    module.ENV_SCHEMA = ENV_SCHEMA
    module._v164_local_support_at_frame = _local_admission_support
    module.segment_guitar_rows = v164.segment_guitar_rows
    module.active_state_reattack_candidates = v164.active_state_reattack_candidates
    module.bass_state_proposals = v164.bass_state_proposals
    module.local_peak = v164.local_peak
    module.refine_onset_frame = v164.refine_onset_frame
    module.choose_sequence_register = v164.choose_sequence_register
    module.median_smooth_midi = v164.median_smooth_midi
    module.stable_bass_states = v164.stable_bass_states
    module.select_event_step = v164.select_event_step
    module.cap_guitar_polyphony = v164.cap_guitar_polyphony
    module.cap_bass_grid = v164.cap_bass_grid
    module.validate_runtime_boundary = validate_runtime_boundary
    return module


def main() -> int:
    module = build_adapted_module()
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
