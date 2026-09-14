#!/usr/bin/env python3
"""Fail-closed V2.1 identity correction for the purpose-built capture contract.

V2.1 is deliberately narrow. It preserves the V2 validator and all V1/V2
fail-closed boundaries, while correcting one inconsistent anti-duplication rule:

- retries inside one frozen slot MUST retain the same underlyingPerformanceId;
- reuse of one underlyingPerformanceId across distinct slots is forbidden.

The V2 implementation rejected any repeated underlyingPerformanceId across
attempts, which also rejected the intended failed-attempt -> admitted-retry
continuity represented by its own synthetic fixture. V2.1 removes only that
same-slot false positive and adds explicit slot-continuity/cross-slot checks.

This module reads declarations only. It does not open media/reference bytes,
invoke Basic Pitch/V6, inspect correctness, or establish structural suitability.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
V2_PATH = HERE / "purpose_built_capture_manifest_contract_v2.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_manifest_contract_v2", V2_PATH
)
assert spec and spec.loader
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)

CONTRACT = "songsterr-fresh-purpose-built-capture-manifest-v2.1"
V2_DUPLICATE_PREFIX = "DUPLICATE_UNDERLYING_PERFORMANCE_ID_ACROSS_ATTEMPTS:"


def _identity_semantic_errors(manifest: Any) -> tuple[list[str], set[str]]:
    if not isinstance(manifest, dict):
        return [], set()
    attempts = manifest.get("attempts")
    if not isinstance(attempts, list):
        return [], set()

    errors: list[str] = []
    slot_ids: dict[str, set[str]] = defaultdict(set)
    underlying_slots: dict[str, set[str]] = defaultdict(set)
    admitted_underlying_ids: set[str] = set()

    for index, attempt in enumerate(attempts):
        if not isinstance(attempt, dict):
            continue
        slot_id = attempt.get("slotId")
        underlying_id = attempt.get("underlyingPerformanceId")
        if not v2._nonempty(slot_id) or not v2._nonempty(underlying_id):
            continue
        slot_key = slot_id.strip()
        underlying_key = underlying_id.strip()
        slot_ids[slot_key].add(underlying_key)
        underlying_slots[underlying_key].add(slot_key)
        if attempt.get("admitted") is True:
            admitted_underlying_ids.add(underlying_key)

    for slot_id, identities in sorted(slot_ids.items()):
        if len(identities) > 1:
            errors.append(
                "UNDERLYING_PERFORMANCE_ID_CHANGED_WITHIN_SLOT:"
                f"{slot_id}:{','.join(sorted(identities))}"
            )

    for underlying_id, slots in sorted(underlying_slots.items()):
        if len(slots) > 1:
            errors.append(
                "DUPLICATE_UNDERLYING_PERFORMANCE_ID_ACROSS_SLOTS:"
                f"{underlying_id}:{','.join(sorted(slots))}"
            )

    return sorted(errors), admitted_underlying_ids


def validate_manifest(manifest: Any) -> dict[str, Any]:
    # V2 expects its own contract literal. Validate an otherwise identical
    # declaration through V2, then apply the corrected identity semantics.
    projected = manifest
    if isinstance(manifest, dict):
        projected = dict(manifest)
        projected["contract"] = v2.CONTRACT

    result = v2.validate_manifest(projected)
    inherited_errors = [
        error
        for error in result.get("errors", [])
        if not str(error).startswith(V2_DUPLICATE_PREFIX)
    ]
    identity_errors, admitted_underlying_ids = _identity_semantic_errors(manifest)

    errors = sorted(set(inherited_errors) | set(identity_errors))
    if not isinstance(manifest, dict):
        errors = sorted(set(errors) | {"TOP_LEVEL_OBJECT_REQUIRED"})
    elif manifest.get("contract") != CONTRACT:
        errors = sorted(
            set(errors)
            | {f"CONTRACT_MISMATCH:{manifest.get('contract')!r}"}
        )

    contract_valid = not errors
    declared_blockers = result.get("declaredStructuralBlockers", [])
    admitted_count = result.get("admittedPopulationCount", 0)
    may_advance = (
        contract_valid
        and isinstance(admitted_count, int)
        and admitted_count > 0
        and not declared_blockers
    )

    return {
        **result,
        "contract": CONTRACT,
        "contractValid": contract_valid,
        "errors": errors,
        "v2SemanticGuardPassed": contract_valid,
        "identitySemanticsVersion": "same-slot-retry-continuity-cross-slot-unique-v1",
        "admittedUnderlyingPerformanceCount": len(admitted_underlying_ids),
        "mayAdvanceToReferenceBlindStructuralAudit": may_advance,
        "authoritativeStructuralSuitabilityEstablished": False,
        "basicPitchAuthorized": False,
        "v6Authorized": False,
        "correctnessAuthorized": False,
        "policyBoundary": dict(v2.v1.REQUIRED_POLICY_BOUNDARY),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to V2.1 capture manifest JSON")
    parser.add_argument("--output", help="Optional deterministic validation-result JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = validate_manifest(manifest)
    rendered = v2.v1.canonical_json(result) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["contractValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
