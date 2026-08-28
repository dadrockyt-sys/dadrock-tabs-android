#!/usr/bin/env python3
"""Independent V164 structural QC adapted from the exact frozen V162 QC.

V162 structural checks remain exact. V164 adds independent local-normalization
provenance/support recomputation, full event-step metadata comparison, and
source-path/pin guards for the sealed local-evidence hypothesis.
"""
from __future__ import annotations

import hashlib
import math
import sys
import types
from pathlib import Path
from typing import Any

import numpy as np

import event_logic_v164 as v164

QC_SCHEMA = "dadrock.tabs.v164.reference-blind-structural-qc.v1"
CANDIDATE_SCHEMA = "dadrock.tabs.v164.local-evidence-generated.v1"
GENERATION_SCHEMA = "dadrock.tabs.v164.cpu-generation-receipt.v1"
TIMEBASE_SCHEMA = "dadrock.tabs.v164.local-evidence-timebase.v1"
TIMEBASE_QC_SCHEMA = "dadrock.tabs.v164.local-evidence-timebase-qc.v1"
PRE_RUN_SCHEMA = "dadrock.tabs.v164.pre-run-identity-receipt.v1"
ENV_SCHEMA = "dadrock.tabs.v164.cpu-environment-receipt.v1"
EPS = 1e-12

V162_STRUCTURAL_QC_BLOB = "b7d3fa92fc9f3bed00931d19097e08cd91eab62b"
V162_CONTRACT_BLOB = "409da313ed03a6c232d6578d48b0da6aa35b000b"
V162_TRANSCRIBER_BLOB = "fa163cafe2131aa73cdbb50df10d4e4912cff53b"
V162_EVENT_LOGIC_BLOB = "9f9b33fd8c210ad581025b454cf69b6999aa544b"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def replace_exact(source: str, old: str, new: str, expected_count: int, label: str) -> str:
    count = source.count(old)
    if count != expected_count:
        raise RuntimeError(f"V164 frozen-QC transform drift for {label}: expected {expected_count}, found {count}")
    return source.replace(old, new)


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def deep_close(left: Any, right: Any, tol: float = 1e-12) -> bool:
    if left is None or right is None or isinstance(left, (str, bool)) or isinstance(right, (str, bool)):
        return left == right
    if isinstance(left, (int, float, np.generic)) and isinstance(right, (int, float, np.generic)):
        return finite(left) and finite(right) and abs(float(left) - float(right)) <= tol
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(deep_close(a, b, tol) for a, b in zip(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        return set(left) == set(right) and all(deep_close(left[key], right[key], tol) for key in left)
    return left == right


def v164_safety_pass(safety: Any) -> bool:
    if not isinstance(safety, dict):
        return False
    return (
        safety.get("referenceRead") is False
        and safety.get("professionalReferencePathsOpened") == 0
        and safety.get("referenceFacingScoreCalls") == 0
        and safety.get("priorGeneratedCandidateRead") is False
        and safety.get("priorScoreRead") is False
        and safety.get("V163CandidateRead") is False
        and safety.get("V163ScoreRead") is False
        and safety.get("referenceGuidedFiltering") is False
        and safety.get("thresholdSweep") is False
        and safety.get("variantSelection") is False
        and safety.get("humanCorrection") is False
        and safety.get("cudaGpuUsed") is False
        and safety.get("modalUsed") is False
        and safety.get("mainOrProductionModified") is False
    )


def _check_window(prefix: str, meta: Any, env_len: int, errors: list[str], *, require_center: bool) -> None:
    if not isinstance(meta, dict):
        errors.append(f"{prefix}: missing local normalization provenance")
        return
    keys = {"loFrame", "hiFrame"} | ({"centerFrame"} if require_center else set())
    if not keys.issubset(meta):
        errors.append(f"{prefix}: incomplete local normalization provenance")
        return
    try:
        lo, hi = int(meta["loFrame"]), int(meta["hiFrame"])
        center = int(meta["centerFrame"]) if require_center else None
    except (TypeError, ValueError):
        errors.append(f"{prefix}: non-integer local normalization provenance")
        return
    if not (0 <= lo <= hi < env_len) or hi - lo > 64:
        errors.append(f"{prefix}: local normalization bounds invalid")
    if center is not None:
        if not lo <= center <= hi:
            errors.append(f"{prefix}: local normalization center outside bounds")
        else:
            expected_lo, expected_hi = v164.local_window_bounds(center, env_len)
            if (lo, hi) != (expected_lo, expected_hi):
                errors.append(f"{prefix}: local normalization bounds do not recompute")


def enhanced_stream_check(base_stream_check, name: str, rows: Any, lattice: list[float], instrument_env: np.ndarray, shared: np.ndarray):
    ok, errors = base_stream_check(name, rows, lattice, instrument_env, shared)
    errors = list(errors)
    if not isinstance(rows, list):
        return False, errors
    env = np.asarray(instrument_env, dtype=float)
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        prefix = f"{name}[{index}]"
        source = str(row.get("source", ""))

        recomputed_step, recomputed_meta = v164.select_event_step(float(row.get("startSeconds", 0.0)), lattice, env, shared)
        if recomputed_step != int(row.get("absoluteGridStep", -999)) or not deep_close(row.get("stepSelection"), recomputed_meta):
            errors.append(f"{prefix}: full V164 event-step metadata does not recompute")

        refinement = row.get("onsetRefinement")
        if isinstance(refinement, dict):
            required = {"originalFrame", "normalizationLoFrame", "normalizationHiFrame", "normalizationPositiveCount"}
            if not required.issubset(refinement):
                errors.append(f"{prefix}: onset-refinement local provenance incomplete")
            else:
                original = int(refinement["originalFrame"])
                lo, hi = v164.local_window_bounds(original, len(env))
                if int(refinement["normalizationLoFrame"]) != lo or int(refinement["normalizationHiFrame"]) != hi:
                    errors.append(f"{prefix}: onset-refinement local bounds do not recompute")
                if int(refinement["normalizationPositiveCount"]) != int(np.count_nonzero(env[lo : hi + 1] > 0.0)):
                    errors.append(f"{prefix}: onset-refinement positive population mismatch")

        if source == "basic_pitch_active_state_reattack":
            local = row.get("localNormalization")
            _check_window(prefix + " recovery", local, len(env), errors, require_center=False)
            if not finite(row.get("onsetSupport")) or not 0.0 <= float(row.get("onsetSupport", -1.0)) <= 1.0:
                errors.append(f"{prefix}: recovery onset support outside [0,1]")
        else:
            onset_meta = row.get("onsetNormalization")
            _check_window(prefix + " admission", onset_meta, len(env), errors, require_center=True)
            if isinstance(onset_meta, dict) and "centerFrame" in onset_meta:
                center = int(onset_meta["centerFrame"])
                support, provenance = v164.local_support_unit(float(env[center]), env, center)
                if not finite(row.get("onsetSupport")) or abs(float(row["onsetSupport"]) - support) > 1e-12:
                    errors.append(f"{prefix}: local q95 onset support does not recompute")
                for key in ("loFrame", "hiFrame", "positiveCount"):
                    if int(onset_meta.get(key, -1)) != int(provenance[key]):
                        errors.append(f"{prefix}: local q95 provenance mismatch: {key}")
                stored_scale = onset_meta.get("supportScale")
                expected_scale = provenance.get("supportScale")
                if stored_scale is None or expected_scale is None:
                    if stored_scale is not expected_scale:
                        errors.append(f"{prefix}: local q95 support-scale fallback mismatch")
                elif not finite(stored_scale) or abs(float(stored_scale) - float(expected_scale)) > 1e-12:
                    errors.append(f"{prefix}: local q95 support scale mismatch")

        if name == "bass":
            proposal_meta = row.get("proposalNormalization")
            _check_window(prefix + " proposal", proposal_meta, len(env), errors, require_center=False)

    return not errors and ok, errors


def additional_checks(args, candidate: dict[str, Any], generation: dict[str, Any], timebase: dict[str, Any], timebase_qc: dict[str, Any], contract: dict[str, Any], pre_run: dict[str, Any]) -> dict[str, bool]:
    frozen = contract.get("frozenV162SourcePins") or {}
    requirements = contract.get("structuralQcRequirements") or {}
    expected_requirements = {
        "candidateHashChain",
        "timebaseAndQcHashChain",
        "codePins",
        "singleGenerationProof",
        "referenceBlindSafety",
        "recomputeSubdivisionLatticeFromFrozenTimebase",
        "recomputeEventStepSelection",
        "localNormalizationProvenanceRequired",
        "localWindowBoundsMustBeInRange",
        "remoteDependencyForbiddenByImplementationPath",
        "normalizedSupportFiniteWithinZeroOne",
        "guitarAllowedSourcesAndPolyphonyCapUnchanged",
        "bassAllowedSourcesAndMonophonyCapUnchanged",
        "jsonNativeReceiptNormalization",
    }
    transcriber_source = args.transcriber.read_text()
    event_source = args.event_logic.read_text()
    qc_safety = timebase_qc.get("safety") or {}
    tb_safety = timebase.get("safety") or {}
    return {
        "candidateVersion": candidate.get("version") == "V164",
        "generationVersion": generation.get("version") == "V164",
        "contractStructuralRequirementsSealed": all(requirements.get(key) is True for key in expected_requirements),
        "frozenV162SourcePins": (
            frozen.get("numericContract") == V162_CONTRACT_BLOB
            and frozen.get("eventLogic") == V162_EVENT_LOGIC_BLOB
            and frozen.get("transcriber") == V162_TRANSCRIBER_BLOB
            and frozen.get("structuralQc") == V162_STRUCTURAL_QC_BLOB
        ),
        "transcriberLocalAdaptationPath": (
            V162_TRANSCRIBER_BLOB in transcriber_source
            and "_v164_local_support_at_frame" in transcriber_source
            and "local onset admission support" in transcriber_source
            and "expected_count" in transcriber_source
            and "module.select_event_step = v164.select_event_step" in transcriber_source
        ),
        "eventLogicLocalityPath": (
            "LOCAL_HALF_WINDOW_FRAMES = 32" in event_source
            and "def local_support_unit(" in event_source
            and "def beat_support_unit(" in event_source
            and "def select_event_step(" in event_source
            and "beat_support_unit(" in event_source
            and "support_unit = _V162.support_unit" not in event_source
        ),
        "preRunV163Blind": (
            pre_run.get("referenceReadAtSeal") is False
            and pre_run.get("professionalReferencePathsOpenedAtSeal") == 0
            and pre_run.get("V163CandidateReadAtSeal") is False
            and pre_run.get("V163ScoreReadAtSeal") is False
        ),
        "timebaseV163Blind": (
            tb_safety.get("referenceRead") is False
            and tb_safety.get("professionalReferencePathsOpened") == 0
            and tb_safety.get("V163CandidateRead") is False
            and tb_safety.get("V163ScoreRead") is False
            and tb_safety.get("gpu") is False
        ),
        "timebaseQcV163BlindBeforePitch": (
            qc_safety.get("referenceRead") is False
            and qc_safety.get("professionalReferencePathsOpened") == 0
            and qc_safety.get("pitchInferenceInvoked") is False
            and qc_safety.get("V163CandidateRead") is False
            and qc_safety.get("V163ScoreRead") is False
            and qc_safety.get("gpuUsed") is False
        ),
    }


def build_adapted_module() -> types.ModuleType:
    repo = Path(__file__).resolve().parents[2]
    base_path = repo / "validation/v162_cpu_autonomous/structural_qc_v162.py"
    v162_contract = repo / "debug/v162-cpu-autonomous/implementation-contract.json"
    if git_blob_sha(base_path) != V162_STRUCTURAL_QC_BLOB:
        raise RuntimeError("V164 frozen V162 structural-QC dependency drift")
    if git_blob_sha(v162_contract) != V162_CONTRACT_BLOB:
        raise RuntimeError("V164 frozen V162 numeric-contract dependency drift")

    source = base_path.read_text()
    source = replace_exact(
        source,
        'prereg.get("status") == "PREREGISTERED_BEFORE_IMPLEMENTATION_CODE"',
        'prereg.get("status") == "PREREGISTERED_BEFORE_NUMERIC_CONTRACT_OR_IMPLEMENTATION_CODE"',
        1,
        "V164 preregistration status",
    )
    source = source.replace("V161CandidateRead", "V163CandidateRead")
    old_receipt_safety = '            "V163CandidateRead": False,\n            "gpuUsed": False,\n'
    new_receipt_safety = '            "V163CandidateRead": False,\n            "V163ScoreRead": False,\n            "gpuUsed": False,\n'
    source = replace_exact(source, old_receipt_safety, new_receipt_safety, 1, "V163 score receipt safety")
    old_pass = '    passed = all(bool(value) for value in checks.values()) and not errors\n'
    new_pass = '    checks.update(_v164_additional_checks(args, candidate, generation, timebase, timebase_qc, contract, pre_run))\n    passed = all(bool(value) for value in checks.values()) and not errors\n'
    source = replace_exact(source, old_pass, new_pass, 1, "V164 additional checks")
    source = source.replace("V162", "V164")

    module = types.ModuleType("_dadrock_v164_adapted_structural_qc")
    module.__file__ = str(Path(__file__).resolve())
    module.__dict__["__builtins__"] = __builtins__
    parent = str(base_path.parent)
    inserted = parent not in sys.path
    if inserted:
        sys.path.insert(0, parent)
    try:
        exec(compile(source, str(base_path), "exec"), module.__dict__)
    finally:
        if inserted:
            sys.path.remove(parent)

    base_stream_check = module.stream_check
    module.QC_SCHEMA = QC_SCHEMA
    module.CANDIDATE_SCHEMA = CANDIDATE_SCHEMA
    module.GENERATION_SCHEMA = GENERATION_SCHEMA
    module.TIMEBASE_SCHEMA = TIMEBASE_SCHEMA
    module.TIMEBASE_QC_SCHEMA = TIMEBASE_QC_SCHEMA
    module.PRE_RUN_SCHEMA = PRE_RUN_SCHEMA
    module.ENV_SCHEMA = ENV_SCHEMA
    module.build_subdivision_lattice = v164.build_subdivision_lattice
    module.select_event_step = v164.select_event_step
    module.safety_pass = v164_safety_pass
    module.stream_check = lambda name, rows, lattice, instrument_env, shared: enhanced_stream_check(base_stream_check, name, rows, lattice, instrument_env, shared)
    module._v164_additional_checks = additional_checks
    return module


def main() -> int:
    return int(build_adapted_module().main())


if __name__ == "__main__":
    raise SystemExit(main())
