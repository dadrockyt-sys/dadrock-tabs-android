#!/usr/bin/env python3
"""Reference-blind manifest-to-plan binding for a future purpose-built V6 holdout.

This layer closes population-construction loopholes that cannot be solved by
validating the capture manifest alone:

1. acquisition-failure reasons must come from a closed objective acquisition-QA
   vocabulary and their exact criteria must be frozen in the plan;
2. the final captured slot population must exactly match a roster frozen before
   capture, with no omitted or newly-added slots; and
3. every planned slot must end with exactly one admitted transport-valid take.

The plan itself is intentionally content-only: it does NOT contain the Git commit
that later freezes it. Putting that commit inside the plan would create a circular
self-reference because the plan hash helps define the commit. A separate Git
provenance layer must prove that the exact plan bytes/hash existed at the
manifest-declared preregistration commit before this binding may authorize even a
reference-blind structural audit.

This tool opens only JSON declarations supplied by the caller. It does not open
candidate audio/MIDI media, invoke Basic Pitch/V6, inspect correctness, contact
networks, or authorize model execution.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
GUARD_PATH = HERE / "purpose_built_capture_manifest_semantic_guard_v1.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_manifest_semantic_guard_v1", GUARD_PATH
)
assert spec and spec.loader
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)
base = guard.base

PLAN_CONTRACT = "songsterr-fresh-purpose-built-capture-plan-v1"

# Derived from the frozen purpose-built design's Capture-QA boundary. These are
# acquisition/transport failures, not musical-quality or model-performance
# judgments. A future plan may choose a subset, but may not invent new classes.
OBJECTIVE_ACQUISITION_FAILURE_CODES = {
    "ABSENT_REFERENCE_CHANNEL",
    "CLIPPING_LIMIT_EXCEEDED",
    "DEVICE_DISCONNECT",
    "MALFORMED_MIDI_STREAM",
    "MISSING_OR_CORRUPT_FILE",
    "TRANSPORT_FAILURE",
    "WRONG_SAMPLE_RATE_OR_FORMAT",
}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalized_reason_list(value: Any, errors: list[str], prefix: str) -> list[str]:
    if not isinstance(value, list) or not value:
        errors.append(f"{prefix}_NONEMPTY_LIST_REQUIRED")
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not _nonempty_string(item):
            errors.append(f"{prefix}_ENTRY_INVALID")
            continue
        reason = item.strip()
        if reason in seen:
            errors.append(f"{prefix}_DUPLICATE:{reason}")
            continue
        seen.add(reason)
        normalized.append(reason)
    return sorted(normalized)


def _validate_plan(
    plan: Any,
) -> tuple[list[str], dict[str, dict[str, str]], list[str], bool]:
    errors: list[str] = []
    slots: dict[str, dict[str, str]] = {}

    if not isinstance(plan, dict):
        return ["CAPTURE_PLAN_TOP_LEVEL_OBJECT_REQUIRED"], slots, [], False
    if plan.get("contract") != PLAN_CONTRACT:
        errors.append(f"CAPTURE_PLAN_CONTRACT_MISMATCH:{plan.get('contract')!r}")
    if not _nonempty_string(plan.get("planId")):
        errors.append("CAPTURE_PLAN_ID_REQUIRED")

    reasons = _normalized_reason_list(
        plan.get("allowedAcquisitionFailureReasons"),
        errors,
        "CAPTURE_PLAN_FAILURE_REASONS",
    )
    for reason in reasons:
        if reason not in OBJECTIVE_ACQUISITION_FAILURE_CODES:
            errors.append(f"CAPTURE_PLAN_FAILURE_REASON_NOT_OBJECTIVE:{reason}")

    criteria = plan.get("acquisitionFailureCriteria")
    criteria_bound = True
    if not isinstance(criteria, dict):
        errors.append("CAPTURE_PLAN_FAILURE_CRITERIA_OBJECT_REQUIRED")
        criteria_bound = False
    else:
        reason_set = set(reasons)
        for key in sorted(set(criteria) - reason_set):
            errors.append(f"CAPTURE_PLAN_FAILURE_CRITERION_UNDECLARED_REASON:{key}")
            criteria_bound = False
        for reason in reasons:
            criterion = criteria.get(reason)
            if not _nonempty_string(criterion):
                errors.append(f"CAPTURE_PLAN_FAILURE_CRITERION_REQUIRED:{reason}")
                criteria_bound = False

    planned_slots = plan.get("plannedSlots")
    if not isinstance(planned_slots, list) or not planned_slots:
        errors.append("CAPTURE_PLAN_PLANNED_SLOTS_NONEMPTY_LIST_REQUIRED")
        return sorted(set(errors)), slots, reasons, criteria_bound

    for index, row in enumerate(planned_slots):
        prefix = f"CAPTURE_PLAN_SLOT[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}_OBJECT_REQUIRED")
            continue
        slot_id = row.get("slotId")
        player_id = row.get("playerId")
        exercise_id = row.get("exerciseId")
        category = row.get("category")

        if not _nonempty_string(slot_id):
            errors.append(f"{prefix}_SLOT_ID_REQUIRED")
            continue
        slot_key = slot_id.strip()
        if slot_key in slots:
            errors.append(f"CAPTURE_PLAN_DUPLICATE_SLOT_ID:{slot_key}")
            continue
        if not _nonempty_string(player_id):
            errors.append(f"{prefix}_PLAYER_ID_REQUIRED")
        if not _nonempty_string(exercise_id):
            errors.append(f"{prefix}_EXERCISE_ID_REQUIRED")
        if category not in base.ALLOWED_CATEGORIES:
            errors.append(f"{prefix}_CATEGORY_INVALID:{category!r}")

        if (
            _nonempty_string(player_id)
            and _nonempty_string(exercise_id)
            and category in base.ALLOWED_CATEGORIES
        ):
            slots[slot_key] = {
                "playerId": player_id.strip(),
                "exerciseId": exercise_id.strip(),
                "category": category,
            }

    return sorted(set(errors)), slots, reasons, criteria_bound


def validate_binding(manifest: Any, plan: Any) -> dict[str, Any]:
    manifest_result = guard.validate_manifest(manifest)
    errors = list(manifest_result.get("errors", []))
    plan_errors, planned_slots, plan_reasons, criteria_bound = _validate_plan(plan)
    errors.extend(plan_errors)

    plan_sha = None
    if isinstance(plan, dict):
        plan_sha = base.sha256_bytes(base.canonical_json(plan).encode("utf-8"))

    manifest_slots: dict[str, dict[str, str]] = {}
    admitted_counts: dict[str, int] = defaultdict(int)
    manifest_reasons: list[str] = []
    preregistration_fields_present = False

    if isinstance(manifest, dict):
        corpus = manifest.get("corpus")
        if isinstance(corpus, dict):
            plan_path = corpus.get("capturePlanPath")
            declared_plan_sha = corpus.get("capturePlanSha256")
            prereg_path = corpus.get("capturePreregistrationPath")
            prereg_commit = corpus.get("capturePreregistrationCommit")

            if not _nonempty_string(plan_path):
                errors.append("MANIFEST_CAPTURE_PLAN_PATH_REQUIRED")
            if not base._is_sha256(declared_plan_sha):
                errors.append("MANIFEST_CAPTURE_PLAN_SHA256_INVALID")
            elif plan_sha is not None and declared_plan_sha != plan_sha:
                errors.append(
                    f"CAPTURE_PLAN_SHA256_MISMATCH:{declared_plan_sha}!={plan_sha}"
                )
            if not _nonempty_string(prereg_path):
                errors.append("MANIFEST_CAPTURE_PREREGISTRATION_PATH_REQUIRED")
            if not base._is_commit(prereg_commit):
                errors.append("MANIFEST_CAPTURE_PREREGISTRATION_COMMIT_INVALID")
            preregistration_fields_present = bool(
                _nonempty_string(plan_path)
                and base._is_sha256(declared_plan_sha)
                and _nonempty_string(prereg_path)
                and base._is_commit(prereg_commit)
            )

        manifest_reasons = _normalized_reason_list(
            manifest.get("allowedAcquisitionFailureReasons"),
            errors,
            "MANIFEST_FAILURE_REASONS",
        )
        if manifest_reasons != plan_reasons:
            errors.append(
                "CAPTURE_PLAN_FAILURE_REASONS_MISMATCH:"
                f"{manifest_reasons!r}!={plan_reasons!r}"
            )

        attempts = manifest.get("attempts")
        if isinstance(attempts, list):
            for row in attempts:
                if not isinstance(row, dict):
                    continue
                slot_id = row.get("slotId")
                if not _nonempty_string(slot_id):
                    continue
                slot_key = slot_id.strip()
                identity = {
                    "playerId": row.get("playerId"),
                    "exerciseId": row.get("exerciseId"),
                    "category": row.get("category"),
                }
                if slot_key not in manifest_slots:
                    manifest_slots[slot_key] = identity
                elif manifest_slots[slot_key] != identity:
                    # The semantic guard also catches this. Keep a local error so
                    # the binding remains fail-closed even if layers change.
                    errors.append(f"CAPTURE_PLAN_SLOT_IDENTITY_INCONSISTENT:{slot_key}")
                if row.get("admitted") is True:
                    admitted_counts[slot_key] += 1

    planned_ids = set(planned_slots)
    captured_ids = set(manifest_slots)
    for slot_id in sorted(planned_ids - captured_ids):
        errors.append(f"CAPTURE_PLAN_SLOT_MISSING_FROM_MANIFEST:{slot_id}")
    for slot_id in sorted(captured_ids - planned_ids):
        errors.append(f"MANIFEST_SLOT_NOT_IN_CAPTURE_PLAN:{slot_id}")
    for slot_id in sorted(planned_ids & captured_ids):
        expected = planned_slots[slot_id]
        actual = manifest_slots[slot_id]
        for field in ("playerId", "exerciseId", "category"):
            if actual.get(field) != expected.get(field):
                errors.append(
                    f"CAPTURE_PLAN_SLOT_IDENTITY_MISMATCH:{slot_id}:{field}:"
                    f"{actual.get(field)!r}!={expected.get(field)!r}"
                )

    for slot_id in sorted(planned_ids):
        admitted_count = admitted_counts.get(slot_id, 0)
        if admitted_count != 1:
            errors.append(
                f"CAPTURE_PLAN_SLOT_MUST_HAVE_EXACTLY_ONE_ADMITTED_PASS:"
                f"{slot_id}:{admitted_count}"
            )

    merged_errors = sorted(set(errors))
    binding_valid = not merged_errors
    roster_exact = planned_ids == captured_ids and bool(planned_ids)
    all_slots_admitted = bool(planned_ids) and all(
        admitted_counts.get(slot_id, 0) == 1 for slot_id in planned_ids
    )

    # Deliberately remain fail-closed here. A separate Git-history proof must
    # establish that the exact plan hash/path existed at the declared
    # preregistration commit before even a reference-blind raw-byte audit.
    return {
        "contract": PLAN_CONTRACT,
        "bindingValid": binding_valid,
        "errors": merged_errors,
        "capturePlanSha256": plan_sha,
        "plannedSlotCount": len(planned_slots),
        "capturedSlotCount": len(manifest_slots),
        "failureReasonVocabularyBound": manifest_reasons == plan_reasons and bool(plan_reasons),
        "failureCriteriaBound": criteria_bound and bool(plan_reasons),
        "slotRosterExactlyBound": roster_exact,
        "allPlannedSlotsAdmitted": all_slots_admitted,
        "manifestPreregistrationFieldsPresent": preregistration_fields_present,
        "manifestSemanticGuardPassed": manifest_result.get("semanticGuardPassed") is True,
        "gitPreregistrationBindingEstablished": False,
        "mayAdvanceToReferenceBlindStructuralAudit": False,
        "authoritativeStructuralSuitabilityEstablished": False,
        "basicPitchAuthorized": False,
        "v6Authorized": False,
        "correctnessAuthorized": False,
        "policyBoundary": dict(base.REQUIRED_POLICY_BOUNDARY),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to final capture manifest JSON")
    parser.add_argument("--capture-plan", required=True, help="Path to frozen capture-plan JSON")
    parser.add_argument("--output", help="Optional deterministic binding-result JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    plan = json.loads(Path(args.capture_plan).read_text(encoding="utf-8"))
    result = validate_binding(manifest, plan)
    rendered = base.canonical_json(result) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["bindingValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
