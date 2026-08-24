#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ASSEMBLY_PATH = ROOT / "analyzer" / "v143_contextual_prune_precision_candidate_events.py"
PRODUCT_PATH = ROOT / "analyzer" / "v143_repaired_timing_precision_candidate_product_modal.py"
DEFAULT_OUTPUT = ROOT / "debug" / "v143-contextual-prune" / "precision-sustain-onset-handoff.json"
EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"


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


def _event_field_assignments(function: ast.FunctionDef) -> dict[str, ast.AST]:
    found: dict[str, ast.AST] = {}
    for node in ast.walk(function):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Subscript):
            continue
        if not isinstance(target.value, ast.Name) or target.value.id != "event":
            continue
        key = target.slice
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            found[key.value] = node.value
    return found


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


def main() -> None:
    assembly_source = ASSEMBLY_PATH.read_text(encoding="utf-8")
    product_source = PRODUCT_PATH.read_text(encoding="utf-8")
    assembly_tree = ast.parse(assembly_source, filename=str(ASSEMBLY_PATH))
    product_tree = ast.parse(product_source, filename=str(PRODUCT_PATH))

    assembly = _function(assembly_tree, "build_precision_candidate_assembly")
    promote = _function(product_tree, "_promote_candidate_sustain")

    grid_expr = ast.unparse(_assigned_name(assembly, "grid_time"))
    physical_expr = ast.unparse(_assigned_name(assembly, "physical_onset"))
    source_row = _dict_literal(_assigned_name(assembly, "source_row"))
    source_time_expr = ast.unparse(source_row.get("timeSeconds")) if "timeSeconds" in source_row else None
    source_onset_expr = ast.unparse(source_row.get("onsetTime")) if "onsetTime" in source_row else None

    event_fields = _event_field_assignments(promote)
    start_expr = ast.unparse(_assigned_name(promote, "start"))
    promoted_onset_expr = ast.unparse(event_fields.get("onsetTime")) if "onsetTime" in event_fields else None
    promoted_offset_expr = ast.unparse(event_fields.get("offsetTime")) if "offsetTime" in event_fields else None
    sustain = _dict_literal(event_fields["rhythmSustain"]) if "rhythmSustain" in event_fields else {}
    attack_changed = sustain.get("attackTimingChanged")
    attack_changed_value = attack_changed.value if isinstance(attack_changed, ast.Constant) else None

    assembly_preserves_grid = source_time_expr == "grid_time"
    assembly_preserves_physical_onset = source_onset_expr == "physical_onset"
    assembly_separates_physical_from_grid = (
        "grid[key]" in grid_expr
        and "row.get('onsetTime')" in physical_expr
        and assembly_preserves_grid
        and assembly_preserves_physical_onset
    )
    promotion_anchors_start_to_grid = start_expr == "float(event['timeSeconds'])"
    promotion_overwrites_physical_onset = promoted_onset_expr == "start"
    promotion_offsets_from_grid_start = promoted_offset_expr == "start + duration_seconds"
    promotion_claims_attack_unchanged = attack_changed_value is False

    synthetic_grid = 10.0
    synthetic_physical = 10.083
    synthetic_after = synthetic_grid if promotion_overwrites_physical_onset else synthetic_physical
    synthetic_overwrite_delta = synthetic_after - synthetic_physical

    protected_blob = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        cwd=ROOT,
        text=True,
    ).strip()
    protected_unchanged = protected_blob == EXPECTED_PROTECTED_BLOB

    defect_proven = all(
        (
            assembly_separates_physical_from_grid,
            promotion_anchors_start_to_grid,
            promotion_overwrites_physical_onset,
            promotion_offsets_from_grid_start,
            promotion_claims_attack_unchanged,
            abs(synthetic_overwrite_delta) > 1e-9,
        )
    )

    report: dict[str, Any] = {
        "schemaVersion": 1,
        "gate": "v143-precision-sustain-onset-handoff-static-proof",
        "assemblySourceSha256": _source_digest(ASSEMBLY_PATH),
        "productSourceSha256": _source_digest(PRODUCT_PATH),
        "assemblyGridExpression": grid_expr,
        "assemblyPhysicalOnsetExpression": physical_expr,
        "assemblySourceTimeExpression": source_time_expr,
        "assemblySourceOnsetExpression": source_onset_expr,
        "assemblySeparatesPhysicalFromGrid": assembly_separates_physical_from_grid,
        "promotionStartExpression": start_expr,
        "promotionOnsetExpression": promoted_onset_expr,
        "promotionOffsetExpression": promoted_offset_expr,
        "promotionAnchorsStartToGrid": promotion_anchors_start_to_grid,
        "promotionOverwritesPhysicalOnset": promotion_overwrites_physical_onset,
        "promotionOffsetsFromGridStart": promotion_offsets_from_grid_start,
        "promotionClaimsAttackTimingChangedFalse": promotion_claims_attack_unchanged,
        "synthetic": {
            "gridTimeSeconds": synthetic_grid,
            "physicalOnsetSecondsBeforePromotion": synthetic_physical,
            "onsetSecondsAfterCurrentPromotion": synthetic_after,
            "physicalOnsetDeltaSeconds": synthetic_overwrite_delta,
        },
        "defectProven": defect_proven,
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

    if not defect_proven:
        raise SystemExit("static onset handoff defect was not proven")
    if not protected_unchanged:
        raise SystemExit(f"protected pipeline changed: {protected_blob}")

    print("V143 precision sustain onset handoff defect proven statically")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
