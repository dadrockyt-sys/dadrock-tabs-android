#!/usr/bin/env python3
"""V166 structural QC: frozen V165 QC engine with paired-window identity checks.

The sealed V165 structural-QC wrapper is mechanically versioned forward. Its
V165 adapter-repair-specific additional checks are replaced by V166 checks for
the exact paired-window transcriber boundary. A structural-QC schema key is
added only to the in-memory contract view consumed by the inherited QC engine;
the sealed contract file and all numeric behavior remain unchanged.
"""
from __future__ import annotations

import copy
import hashlib
import sys
import types
from pathlib import Path
from typing import Any

FROZEN_V165_STRUCTURAL_QC_BLOB = "36b4738cc7c00fa32aa684b3d395a67d5294a61d"
FROZEN_V165_TRANSCRIBER_BLOB = "45d595853302b077fbf4f3094e9a4922fba02435"
FROZEN_V165_EVENT_LOGIC_BLOB = "b296b3c322c13f8963f253f9b0666db66766a178"
FROZEN_CONTRACT_BLOB = "9ab505ee8c7de732b6e9a8928854ae99d3ebb0c7"
EXPECTED_OFFSETS = [-1, 0, 1, 2, 3, 4]


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _build_versioned_v165_wrapper() -> types.ModuleType:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "validation/v165_cpu_autonomous/structural_qc_v165.py"
    if not path.is_file() or _git_blob_sha(path) != FROZEN_V165_STRUCTURAL_QC_BLOB:
        raise RuntimeError("V166 frozen V165 structural-QC dependency identity mismatch")
    source = path.read_text().replace("v165", "v166").replace("V165", "V166")
    module = types.ModuleType("_dadrock_v166_versioned_v165_structural_qc")
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


def _paired_window_additional_checks(
    args,
    candidate: dict[str, Any],
    generation: dict[str, Any],
    timebase: dict[str, Any],
    timebase_qc: dict[str, Any],
    contract: dict[str, Any],
    pre_run: dict[str, Any],
) -> dict[str, bool]:
    del timebase, timebase_qc
    transcriber_source = args.transcriber.read_text()
    event_source = args.event_logic.read_text()
    paired = contract.get("pairedTemplate") or {}
    pins = contract.get("frozenSourcePins") or {}
    prereg_path = args.preregistration
    contract_path = args.implementation_contract
    return {
        "candidateVersion": candidate.get("version") == "V166",
        "generationVersion": generation.get("version") == "V166",
        "preregistrationIdentityPinned": _git_blob_sha(prereg_path) == "ca45241b4ab4689c8ceb3a7107e158367814cc1d",
        "implementationContractIdentityPinned": _git_blob_sha(contract_path) == FROZEN_CONTRACT_BLOB,
        "pairedTemplateContractExact": (
            paired.get("combinedOffsets") == EXPECTED_OFFSETS
            and paired.get("frameCount") == 6
            and paired.get("primaryOffsets") == [-1, 0, 1]
            and paired.get("adjacentOffsets") == [2, 3, 4]
            and paired.get("frozenTemplateScoringFunction") == "template_scores"
            and float(paired.get("relativeAbsoluteTestTolerance", -1.0)) == 1e-12
        ),
        "frozenV165SourcePinsExact": (
            pins.get("v165EventLogic") == FROZEN_V165_EVENT_LOGIC_BLOB
            and pins.get("v165Transcriber") == FROZEN_V165_TRANSCRIBER_BLOB
            and pins.get("v165StructuralQc") == FROZEN_V165_STRUCTURAL_QC_BLOB
        ),
        "transcriberPairedWindowPath": (
            FROZEN_V165_TRANSCRIBER_BLOB in transcriber_source
            and "V166_TEMPLATE_FRAME_OFFSETS = (-1, 0, 1, 2, 3, 4)" in transcriber_source
            and "V166_TEMPLATE_FRAME_COUNT = 6" in transcriber_source
            and "def paired_window_frames(" in transcriber_source
            and "def paired_window_template_with(" in transcriber_source
            and "frozen_template_scores = module.template_scores" in transcriber_source
            and "module.three_frame_template = _paired_window_template" in transcriber_source
        ),
        "eventLogicFrozenV165Path": (
            FROZEN_V165_EVENT_LOGIC_BLOB in event_source
            and "_build_frozen_v165_behavior" in event_source
            and '.replace("v165", "v166").replace("V165", "V166")' in event_source
        ),
        "preRunV165RuntimeBlind": (
            pre_run.get("referenceReadAtSeal") is False
            and pre_run.get("professionalReferencePathsOpenedAtSeal") == 0
            and pre_run.get("V165CandidateReadAtSeal") is False
            and pre_run.get("V165ScoreReadAtSeal") is False
            and pre_run.get("songAudioExecutionsAtSeal") == 0
            and pre_run.get("pitchInferenceExecutionsAtSeal") == 0
            and pre_run.get("gpuExecutionsAtSeal") == 0
        ),
    }


_BASE = _build_versioned_v165_wrapper()
# Replace V165's adapter-count-specific additional checks before a final QC module is built.
_BASE._IMPL.additional_checks = _paired_window_additional_checks

QC_SCHEMA = _BASE.QC_SCHEMA
CANDIDATE_SCHEMA = _BASE.CANDIDATE_SCHEMA
GENERATION_SCHEMA = _BASE.GENERATION_SCHEMA
TIMEBASE_SCHEMA = _BASE.TIMEBASE_SCHEMA
TIMEBASE_QC_SCHEMA = _BASE.TIMEBASE_QC_SCHEMA
PRE_RUN_SCHEMA = _BASE.PRE_RUN_SCHEMA
ENV_SCHEMA = _BASE.ENV_SCHEMA


def build_adapted_module() -> types.ModuleType:
    module = _BASE.build_adapted_module()
    original_load_json = module.load_json

    def _load_json_with_qc_schema(path: Path) -> dict[str, Any]:
        data = original_load_json(path)
        if path.name == "implementation-contract.json" and data.get("version") == "V166":
            data = copy.deepcopy(data)
            schemas = dict(data.get("canonicalSchemas") or {})
            schemas["structuralQc"] = QC_SCHEMA
            data["canonicalSchemas"] = schemas
        return data

    module.load_json = _load_json_with_qc_schema
    return module


def main() -> int:
    return int(build_adapted_module().main())


if __name__ == "__main__":
    raise SystemExit(main())
