#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any

from v143_precision_sustain_promotion import promote_candidate_sustain


ROOT = Path(__file__).resolve().parents[1]
ASSEMBLY_PATH = ROOT / "analyzer" / "v143_contextual_prune_precision_candidate_events.py"
PRODUCT_PATH = ROOT / "analyzer" / "v143_repaired_timing_precision_candidate_product_modal.py"
PROMOTION_PATH = ROOT / "analyzer" / "v143_precision_sustain_promotion.py"
DEFAULT_OUTPUT = ROOT / "debug" / "v143-contextual-prune" / "precision-sustain-onset-handoff.json"
EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"

IDENTITY_FIELDS = ("measure", "step", "midi", "stringIndex", "fret", "timeSeconds")


def _function(tree: ast.AST, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise RuntimeError(f"function not found: {name}")


def _assigned_name(function: ast.FunctionDef, name: str) -> ast.AST:
    for node in ast.walk(function):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == name:
            return node.value
    raise RuntimeError(f"assignment not found in {function.name}: {name}")


def _dict_literal(value: ast.AST) -> dict[str, ast.AST]:
    if not isinstance(value, ast.Dict):
        raise RuntimeError("expected literal dict")
    result: dict[str, ast.AST] = {}
    for key, item in zip(value.keys, value.values):
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            result[key.value] = item
    return result


def _source_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _static_contract() -> dict[str, Any]:
    assembly_source = ASSEMBLY_PATH.read_text(encoding="utf-8")
    product_source = PRODUCT_PATH.read_text(encoding="utf-8")
    assembly_tree = ast.parse(assembly_source, filename=str(ASSEMBLY_PATH))
    product_tree = ast.parse(product_source, filename=str(PRODUCT_PATH))

    assembly = _function(assembly_tree, "build_precision_candidate_assembly")
    wrapper = _function(product_tree, "_promote_candidate_sustain")

    grid_expr = ast.unparse(_assigned_name(assembly, "grid_time"))
    physical_expr = ast.unparse(_assigned_name(assembly, "physical_onset"))
    source_row = _dict_literal(_assigned_name(assembly, "source_row"))
    source_time_expr = ast.unparse(source_row.get("timeSeconds")) if "timeSeconds" in source_row else None
    source_onset_expr = ast.unparse(source_row.get("onsetTime")) if "onsetTime" in source_row else None

    assembly_separates = (
        "grid[key]" in grid_expr
        and "row.get('onsetTime')" in physical_expr
        and source_time_expr == "grid_time"
        and source_onset_expr == "physical_onset"
    )

    returns = [node for node in ast.walk(wrapper) if isinstance(node, ast.Return)]
    wrapper_expr = ast.unparse(returns[0].value) if len(returns) == 1 and returns[0].value is not None else None
    wrapper_delegates = wrapper_expr == "promote_candidate_sustain(events, tempo_bpm)"
    module_bundled = '"v143_precision_sustain_promotion"' in product_source

    return {
        "assemblyGridExpression": grid_expr,
        "assemblyPhysicalOnsetExpression": physical_expr,
        "assemblySourceTimeExpression": source_time_expr,
        "assemblySourceOnsetExpression": source_onset_expr,
        "assemblySeparatesPhysicalFromGrid": assembly_separates,
        "productPromotionWrapperExpression": wrapper_expr,
        "productDelegatesToPurePromotion": wrapper_delegates,
        "promotionModuleBundledInCandidateImage": module_bundled,
    }


def _synthetic_contract() -> dict[str, Any]:
    before = [
        {
            "measure": 7,
            "step": 3,
            "midi": 57,
            "dominantMidi": 57,
            "stringIndex": 2,
            "fret": 2,
            "timeSeconds": 10.0,
            "onsetTime": 10.083,
            "rhythmSustainShadow": {
                "durationSeconds": 0.42,
                "durationSteps": 3,
            },
        },
        {
            "measure": 7,
            "step": 8,
            "midi": 64,
            "dominantMidi": 64,
            "stringIndex": 0,
            "fret": 0,
            "timeSeconds": 10.5,
            "onsetTime": 10.472,
            "rhythmSustainShadow": {
                "durationSeconds": 0.21,
                "durationSteps": 2,
            },
        },
    ]
    after = promote_candidate_sustain(before, 120.0)

    same_count = len(after) == len(before)
    identity_unchanged = same_count and all(
        all(item_before[field] == item_after[field] for field in IDENTITY_FIELDS)
        for item_before, item_after in zip(before, after)
    )
    physical_onset_preserved = same_count and all(
        math.isclose(float(item_after["onsetTime"]), float(item_before["onsetTime"]), abs_tol=1e-12)
        for item_before, item_after in zip(before, after)
    )
    grid_start_preserved = same_count and all(
        math.isclose(float(item_after["start"]), float(item_before["timeSeconds"]), abs_tol=1e-12)
        for item_before, item_after in zip(before, after)
    )
    duration_contract_consistent = same_count and all(
        math.isclose(
            float(item_after["end"]) - float(item_after["start"]),
            float(item_after["duration"]),
            abs_tol=1e-12,
        )
        and math.isclose(
            float(item_after["duration"]),
            float(item_after["rhythmSustain"]["durationSeconds"]),
            abs_tol=1e-12,
        )
        and math.isclose(float(item_after["offsetTime"]), float(item_after["end"]), abs_tol=1e-12)
        for item_after in after
    )
    delta_truthful = same_count and all(
        math.isclose(
            float(item_after["physicalOnsetDeltaFromGridSeconds"]),
            float(item_before["onsetTime"]) - float(item_before["timeSeconds"]),
            abs_tol=1e-12,
        )
        for item_before, item_after in zip(before, after)
    )
    sustain_truthful = same_count and all(
        item_after["rhythmSustain"].get("attackTimingChanged") is False
        and item_after["rhythmSustain"].get("physicalOnsetPreserved") is True
        and item_after["rhythmSustain"].get("analysisTimingBasis") == "quantized-timeSeconds"
        and item_after["rhythmSustain"].get("offsetTimingBasis") == "quantized-timeSeconds-plus-durationSeconds"
        for item_after in after
    )

    no_invented_attack_or_pitch = identity_unchanged and physical_onset_preserved
    correction_proven = all(
        (
            same_count,
            identity_unchanged,
            physical_onset_preserved,
            grid_start_preserved,
            duration_contract_consistent,
            delta_truthful,
            sustain_truthful,
            no_invented_attack_or_pitch,
        )
    )

    return {
        "syntheticEventCountBefore": len(before),
        "syntheticEventCountAfter": len(after),
        "eventCountUnchanged": same_count,
        "attackPitchPositionIdentityUnchanged": identity_unchanged,
        "physicalOnsetPreserved": physical_onset_preserved,
        "quantizedGridStartPreserved": grid_start_preserved,
        "durationContractConsistent": duration_contract_consistent,
        "physicalOnsetDeltaTruthful": delta_truthful,
        "sustainTimingMetadataTruthful": sustain_truthful,
        "noInventedAttackOrPitch": no_invented_attack_or_pitch,
        "examplePositiveResidualSeconds": float(after[0]["physicalOnsetDeltaFromGridSeconds"]),
        "exampleNegativeResidualSeconds": float(after[1]["physicalOnsetDeltaFromGridSeconds"]),
        "correctionProven": correction_proven,
    }


def main() -> None:
    static = _static_contract()
    synthetic = _synthetic_contract()

    protected_blob = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        cwd=ROOT,
        text=True,
    ).strip()
    protected_unchanged = protected_blob == EXPECTED_PROTECTED_BLOB

    passed = all(
        (
            static["assemblySeparatesPhysicalFromGrid"],
            static["productDelegatesToPurePromotion"],
            static["promotionModuleBundledInCandidateImage"],
            synthetic["correctionProven"],
            protected_unchanged,
        )
    )

    report: dict[str, Any] = {
        "schemaVersion": 2,
        "gate": "v143-precision-sustain-onset-handoff-static-proof",
        "assemblySourceSha256": _source_digest(ASSEMBLY_PATH),
        "productSourceSha256": _source_digest(PRODUCT_PATH),
        "promotionSourceSha256": _source_digest(PROMOTION_PATH),
        **static,
        **synthetic,
        "passed": passed,
        "defectPresent": False,
        "protectedPipelineBlob": protected_blob,
        "expectedProtectedPipelineBlob": EXPECTED_PROTECTED_BLOB,
        "protectedPipelineUnchanged": protected_unchanged,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "modalGpuUsed": False,
    }

    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if not passed:
        raise SystemExit("corrected onset handoff contract failed")

    print("V143 precision sustain physical-onset handoff correction proven")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
