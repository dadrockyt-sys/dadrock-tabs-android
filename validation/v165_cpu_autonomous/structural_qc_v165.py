#!/usr/bin/env python3
"""V165 structural QC: frozen V164 QC with wrapper-aware adapter identity checks."""
from __future__ import annotations

import hashlib
import sys
import types
from pathlib import Path
from typing import Any

FROZEN_V164_STRUCTURAL_QC_BLOB = "c1a81c7a97e646398f5e50cbc63dae341cdc500b"
FROZEN_V164_TRANSCRIBER_BLOB = "df1302216df404bc3368ff820f005d6b63ae100d"
FROZEN_V164_EVENT_LOGIC_BLOB = "62303877a1971f75cacda002c5ad921680161674"
V165_REQUIRED_OCCURRENCE_COUNT = 3


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _build_impl() -> types.ModuleType:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "validation/v164_cpu_autonomous/structural_qc_v164.py"
    if not path.is_file() or _git_blob_sha(path) != FROZEN_V164_STRUCTURAL_QC_BLOB:
        raise RuntimeError("V165 frozen V164 structural-QC identity mismatch")
    source = path.read_text().replace("v164", "v165").replace("V164", "V165")
    module = types.ModuleType("_dadrock_v165_structural_qc")
    module.__file__ = str(Path(__file__).resolve())
    module.__dict__["__builtins__"] = __builtins__
    parent = str(Path(__file__).resolve().parent)
    inserted = parent not in sys.path
    if inserted:
        sys.path.insert(0, parent)
    try:
        exec(compile(source, str(Path(__file__).resolve()), "exec"), module.__dict__)
    finally:
        if inserted:
            sys.path.remove(parent)
    return module


_IMPL = _build_impl()
_BASE_ADDITIONAL_CHECKS = _IMPL.additional_checks


def _wrapper_aware_additional_checks(
    args,
    candidate: dict[str, Any],
    generation: dict[str, Any],
    timebase: dict[str, Any],
    timebase_qc: dict[str, Any],
    contract: dict[str, Any],
    pre_run: dict[str, Any],
) -> dict[str, bool]:
    checks = dict(_BASE_ADDITIONAL_CHECKS(args, candidate, generation, timebase, timebase_qc, contract, pre_run))
    transcriber_source = args.transcriber.read_text()
    event_source = args.event_logic.read_text()
    repair = contract.get("adapterRepairContract") or {}
    requirements = contract.get("structuralQcRequirements") or {}

    checks["transcriberLocalAdaptationPath"] = (
        FROZEN_V164_TRANSCRIBER_BLOB in transcriber_source
        and 'V165_REQUIRED_OCCURRENCE_COUNT = 3' in transcriber_source
        and '_adapt_v164_adapter_source' in transcriber_source
        and "event_logic_v162.py" in transcriber_source
        and "event_logic_v165.py" in transcriber_source
        and "source.count(old) != 1" in transcriber_source
        and "source.replace(old, new)" in transcriber_source
    )
    checks["eventLogicLocalityPath"] = (
        FROZEN_V164_EVENT_LOGIC_BLOB in event_source
        and "_build_frozen_v164_behavior" in event_source
        and 'source = source.replace("V164", "V165")' in event_source
    )
    checks["adapterRepairIdentityPinned"] = (
        requirements.get("adapterRepairIdentityPinned") is True
        and repair.get("V164AdapterSourceGitBlob") == FROZEN_V164_TRANSCRIBER_BLOB
        and repair.get("V165RequiredOccurrenceCount") == V165_REQUIRED_OCCURRENCE_COUNT
        and repair.get("allThreeOccurrencesMustBeReplaced") is True
        and repair.get("zeroOldNeedleOccurrencesRequiredAfterTransform") is True
        and repair.get("threeNewNeedleOccurrencesRequiredAfterTransform") is True
        and repair.get("noFallbackToUnboundedReplace") is True
        and repair.get("countCheckedReplacementRequired") is True
    )
    return checks


_IMPL.additional_checks = _wrapper_aware_additional_checks

QC_SCHEMA = _IMPL.QC_SCHEMA
CANDIDATE_SCHEMA = _IMPL.CANDIDATE_SCHEMA
GENERATION_SCHEMA = _IMPL.GENERATION_SCHEMA
TIMEBASE_SCHEMA = _IMPL.TIMEBASE_SCHEMA
TIMEBASE_QC_SCHEMA = _IMPL.TIMEBASE_QC_SCHEMA
PRE_RUN_SCHEMA = _IMPL.PRE_RUN_SCHEMA
ENV_SCHEMA = _IMPL.ENV_SCHEMA


def build_adapted_module() -> types.ModuleType:
    return _IMPL.build_adapted_module()


def main() -> int:
    return int(_IMPL.main())


if __name__ == "__main__":
    raise SystemExit(main())
