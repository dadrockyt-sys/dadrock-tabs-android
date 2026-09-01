#!/usr/bin/env python3
"""Validate the frozen V168 GOAT metadata-only integrity/selection receipt.

This validator never opens GOAT audio, reference note/event files, generated
candidates, or scorer inputs. It accepts only a metadata receipt produced after
restricted access and proves that the selected base performances follow the
pre-access deterministic Tier 1 / Tier 2 rule.

The companion contract is frozen by exact SHA256.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Mapping

CONTRACT_SCHEMA = "dadrock.tabs.v168.goat-selection-contract.v1"
RECEIPT_SCHEMA = "dadrock.tabs.v168.goat-selection-receipt.v1"
VERSION = "V168"
ZENODO_RECORD_ID = "15690894"
ZENODO_DOI = "10.5281/zenodo.15690894"
ZENODO_VERSION = "v1"
EXPECTED_CONTRACT_SHA256 = "8c84eefa442d4c547180e1543cace9031ca2d801c1d04956893b3fb24e71096b"
TARGET_WORKS = 3
MIN_WORKS = 2
BASE_SOURCE_ROLE = "base_di"
TIER1 = "official_released_test_split"
TIER2 = "deterministic_hash_fallback"
TIER2_SALT = "dadrock-v168-goat-v1-selection"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_PASS_FLAGS = (
    "sourceIdentityFrozen",
    "referenceIdentityFrozen",
    "sourceReferenceBindingFrozen",
    "referenceParseSucceeded",
    "v154TimebaseCompatible",
    "allScoredReferenceOnsetsWithinSourceEofTolerance",
    "ownerUseConditionsCompatible",
    "decisionMadeWithoutComparativeScores",
)

ALLOWED_FAILURE_REASONS = {
    "SOURCE_IDENTITY_UNFROZEN",
    "REFERENCE_IDENTITY_UNFROZEN",
    "SOURCE_REFERENCE_BINDING_UNRESOLVED",
    "REFERENCE_PARSE_FAILED",
    "V154_TIMEBASE_INCOMPATIBLE",
    "REFERENCE_ONSET_OUTSIDE_SOURCE_EOF",
    "OWNER_USE_CONDITIONS_INCOMPATIBLE",
    "BASE_PERFORMANCE_ID_UNRESOLVED",
    "WORK_ID_UNRESOLVED",
}


class SelectionError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SelectionError(message)


def require_text(value: Any, field: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{field} must be non-empty text")
    return value.strip()


def require_sha256(value: Any, field: str) -> str:
    text = require_text(value, field).lower()
    require(bool(SHA256_RE.fullmatch(text)), f"{field} must be lowercase SHA256")
    return text


def normalize_id(value: str) -> str:
    text = unicodedata.normalize("NFKC", value).strip().casefold()
    return re.sub(r"\s+", "-", text)


def load_contract(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    observed_sha = hashlib.sha256(raw).hexdigest()
    require(
        observed_sha == EXPECTED_CONTRACT_SHA256,
        f"GOAT selection contract SHA256 drift: {observed_sha}",
    )
    payload = json.loads(raw.decode("utf-8"))
    require(isinstance(payload, dict), "contract root must be an object")
    require(payload.get("schema") == CONTRACT_SCHEMA, "contract schema drift")
    require(payload.get("version") == VERSION, "contract version drift")
    dataset = payload.get("dataset") or {}
    require(dataset.get("zenodoRecordId") == ZENODO_RECORD_ID, "contract Zenodo record drift")
    require(dataset.get("doi") == ZENODO_DOI, "contract DOI drift")
    require(dataset.get("version") == ZENODO_VERSION, "contract dataset version drift")
    selection = payload.get("selection") or {}
    require(selection.get("targetHoldoutWorks") == TARGET_WORKS, "contract target work count drift")
    require(selection.get("minimumHoldoutWorks") == MIN_WORKS, "contract minimum work count drift")
    require(selection.get("baseSourceRole") == BASE_SOURCE_ROLE, "contract base source role drift")
    tier2 = selection.get("tier2") or {}
    require(tier2.get("salt") == TIER2_SALT, "contract Tier 2 salt drift")
    integrity = payload.get("integrity") or {}
    require(
        abs(float(integrity.get("sourceEofOnsetToleranceSeconds")) - 0.050) <= 1e-12,
        "contract EOF onset tolerance drift",
    )
    require(integrity.get("noteOffsetBeyondEofAloneIsFailure") is False, "contract note-offset rule drift")
    require(integrity.get("repairAllowed") is False, "contract repair rule drift")
    require(tuple(integrity.get("requiredPassFlags") or []) == REQUIRED_PASS_FLAGS, "contract pass flags drift")
    require(set(integrity.get("allowedFailureReasons") or []) == ALLOWED_FAILURE_REASONS, "contract failure reasons drift")
    return payload


def validate_integrity(value: Any, prefix: str) -> str:
    require(isinstance(value, Mapping), f"{prefix} must be an object")
    status = require_text(value.get("status"), f"{prefix}.status")
    require(status in {"PASS", "FAIL"}, f"{prefix}.status must be PASS or FAIL")
    reasons = value.get("failureReasons")
    require(isinstance(reasons, list), f"{prefix}.failureReasons must be an array")
    require(all(isinstance(x, str) for x in reasons), f"{prefix}.failureReasons must contain strings")
    require(len(reasons) == len(set(reasons)), f"{prefix}.failureReasons must be unique")
    require(set(reasons) <= ALLOWED_FAILURE_REASONS, f"{prefix} contains an unknown failure reason")

    if status == "PASS":
        require(reasons == [], f"{prefix} PASS must have no failureReasons")
        for flag in REQUIRED_PASS_FLAGS:
            require(value.get(flag) is True, f"{prefix}.{flag} must be true for PASS")
    else:
        require(bool(reasons), f"{prefix} FAIL must have at least one failure reason")
        require(
            not all(value.get(flag) is True for flag in REQUIRED_PASS_FLAGS),
            f"{prefix} FAIL cannot have every pass flag true",
        )
    return status


def validate_inventory_row(row: Any, index: int) -> dict[str, Any]:
    prefix = f"inventory[{index}]"
    require(isinstance(row, Mapping), f"{prefix} must be an object")
    base_id = require_text(row.get("basePerformanceId"), f"{prefix}.basePerformanceId")
    work_id = require_text(row.get("workId"), f"{prefix}.workId")
    source_role = require_text(row.get("sourceRole"), f"{prefix}.sourceRole")
    require(source_role == BASE_SOURCE_ROLE, f"{prefix}.sourceRole must be {BASE_SOURCE_ROLE}")
    source_sha = require_sha256(row.get("sourceAudioSha256"), f"{prefix}.sourceAudioSha256")
    reference_sha = require_sha256(row.get("professionalReferenceSha256"), f"{prefix}.professionalReferenceSha256")
    split_label = row.get("officialSplitLabel")
    require(split_label is None or isinstance(split_label, str), f"{prefix}.officialSplitLabel must be string or null")
    status = validate_integrity(row.get("integrity"), f"{prefix}.integrity")
    return {
        "basePerformanceId": base_id,
        "normalizedBasePerformanceId": normalize_id(base_id),
        "workId": work_id,
        "normalizedWorkId": normalize_id(work_id),
        "sourceAudioSha256": source_sha,
        "professionalReferenceSha256": reference_sha,
        "officialSplitLabel": None if split_label is None else normalize_id(split_label),
        "integrityStatus": status,
    }


def representative_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_work: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_work.setdefault(row["normalizedWorkId"], []).append(row)
    reps: list[dict[str, Any]] = []
    for work_id in sorted(by_work):
        reps.append(
            min(
                by_work[work_id],
                key=lambda row: (
                    row["normalizedBasePerformanceId"],
                    row["basePerformanceId"],
                ),
            )
        )
    return reps


def selection_digest(row: Mapping[str, Any]) -> str:
    raw = (
        TIER2_SALT
        + "|"
        + str(row["normalizedWorkId"])
        + "|"
        + str(row["normalizedBasePerformanceId"])
        + "|"
        + str(row["sourceAudioSha256"])
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def expected_selection(
    rows: list[dict[str, Any]],
    *,
    official_test_split_present: bool,
) -> tuple[str, str, list[str], list[dict[str, Any]]]:
    pass_rows = [row for row in rows if row["integrityStatus"] == "PASS"]

    if official_test_split_present:
        tier = TIER1
        eligible = [row for row in pass_rows if row["officialSplitLabel"] == "test"]
        reps = representative_rows(eligible)
        reps.sort(
            key=lambda row: (
                row["normalizedWorkId"],
                row["normalizedBasePerformanceId"],
                row["basePerformanceId"],
            )
        )
    else:
        tier = TIER2
        reps = representative_rows(pass_rows)
        reps.sort(
            key=lambda row: (
                selection_digest(row),
                row["normalizedWorkId"],
                row["normalizedBasePerformanceId"],
                row["basePerformanceId"],
            )
        )

    if len(reps) < MIN_WORKS:
        status = "INCONCLUSIVE_HOLDOUT_INSUFFICIENT"
        chosen = reps
    else:
        status = "SELECTION_FROZEN"
        chosen = reps[:TARGET_WORKS]
    return tier, status, [row["basePerformanceId"] for row in chosen], chosen


def validate_receipt(payload: Mapping[str, Any], contract_path: Path) -> dict[str, Any]:
    load_contract(contract_path)
    require(isinstance(payload, Mapping), "receipt root must be an object")
    require(payload.get("schema") == RECEIPT_SCHEMA, f"schema must equal {RECEIPT_SCHEMA}")
    require(payload.get("version") == VERSION, f"version must equal {VERSION}")

    contract_ref = payload.get("selectionContract") or {}
    require(contract_ref.get("schema") == CONTRACT_SCHEMA, "selectionContract.schema drift")
    require(contract_ref.get("sha256") == EXPECTED_CONTRACT_SHA256, "selectionContract.sha256 drift")

    dataset = payload.get("dataset") or {}
    require(dataset.get("zenodoRecordId") == ZENODO_RECORD_ID, "dataset Zenodo record mismatch")
    require(dataset.get("doi") == ZENODO_DOI, "dataset DOI mismatch")
    require(dataset.get("version") == ZENODO_VERSION, "dataset version mismatch")
    require(dataset.get("accessGrantFrozen") is True, "dataset.accessGrantFrozen must be true")
    require(dataset.get("completeBaseDiInventoryFrozen") is True, "complete base-DI inventory must be frozen")
    require(dataset.get("sourceReferencePairInventoryFrozen") is True, "source/reference pair inventory must be frozen")
    require(dataset.get("inventoryBuiltWithoutComparativeScores") is True, "inventory must be score-blind")

    boundary = payload.get("boundary") or {}
    require(boundary.get("comparativeScoresReadBeforeSelectionFreeze") is False, "comparative scores cannot precede selection freeze")
    require(boundary.get("candidateGenerationArmedBeforeSelectionFreeze") is False, "candidate generation cannot be armed before selection freeze")
    require(boundary.get("referenceFacingScoringArmedBeforeSelectionFreeze") is False, "reference-facing scoring cannot be armed before selection freeze")
    require(boundary.get("v168ReferenceFacingScoreCallsBeforeSelectionFreeze") == 0, "V168 score calls before selection freeze must be 0")
    require(boundary.get("gpuCudaModalUsed") is False, "GPU/CUDA/Modal boundary must remain false")
    require(boundary.get("mainOrProductionModified") is False, "main/Production boundary must remain false")

    official = payload.get("officialReleasedTestSplitPresent")
    require(isinstance(official, bool), "officialReleasedTestSplitPresent must be boolean")

    inventory = payload.get("inventory")
    require(isinstance(inventory, list), "inventory must be an array")
    rows = [validate_inventory_row(row, i) for i, row in enumerate(inventory)]

    base_ids = [row["basePerformanceId"] for row in rows]
    normalized_base_ids = [row["normalizedBasePerformanceId"] for row in rows]
    source_hashes = [row["sourceAudioSha256"] for row in rows]
    reference_hashes = [row["professionalReferenceSha256"] for row in rows]
    require(len(base_ids) == len(set(base_ids)), "basePerformanceId values must be unique")
    require(len(normalized_base_ids) == len(set(normalized_base_ids)), "normalized basePerformanceId values must be unique")
    require(len(source_hashes) == len(set(source_hashes)), "source-audio SHA256 values must be unique")
    require(len(reference_hashes) == len(set(reference_hashes)), "professional-reference SHA256 values must be unique")

    expected_tier, expected_status, expected_ids, chosen_rows = expected_selection(
        rows,
        official_test_split_present=official,
    )
    require(payload.get("tierUsed") == expected_tier, f"tierUsed must equal {expected_tier}")
    require(payload.get("status") == expected_status, f"status must equal {expected_status}")
    selected = payload.get("selectedBasePerformanceIds")
    require(isinstance(selected, list) and all(isinstance(x, str) for x in selected), "selectedBasePerformanceIds must be an array of strings")
    require(selected == expected_ids, f"selectedBasePerformanceIds drift; expected {expected_ids}")

    eligible_rows = [
        row
        for row in rows
        if row["integrityStatus"] == "PASS"
        and (not official or row["officialSplitLabel"] == "test")
    ]
    return {
        "schema": RECEIPT_SCHEMA,
        "status": expected_status,
        "tierUsed": expected_tier,
        "inventoryRows": len(rows),
        "integrityPassRows": sum(row["integrityStatus"] == "PASS" for row in rows),
        "eligibleWorkCount": len(representative_rows(eligible_rows)),
        "selectedBasePerformanceIds": expected_ids,
        "selectedWorkIds": [row["workId"] for row in chosen_rows],
        "targetHoldoutWorks": TARGET_WORKS,
        "minimumHoldoutWorks": MIN_WORKS,
        "referenceFacingScoringArmed": False,
        "v168ReferenceFacingScoreCalls": 0,
    }


def _integrity(status: str = "PASS", reason: str | None = None) -> dict[str, Any]:
    payload = {flag: True for flag in REQUIRED_PASS_FLAGS}
    payload["status"] = status
    payload["failureReasons"] = []
    if status == "FAIL":
        assert reason is not None
        payload["failureReasons"] = [reason]
        if reason == "REFERENCE_ONSET_OUTSIDE_SOURCE_EOF":
            payload["allScoredReferenceOnsetsWithinSourceEofTolerance"] = False
        elif reason == "V154_TIMEBASE_INCOMPATIBLE":
            payload["v154TimebaseCompatible"] = False
        else:
            payload["sourceReferenceBindingFrozen"] = False
    return payload


def _row(
    base_id: str,
    work_id: str,
    source_n: int,
    reference_n: int,
    *,
    split: str | None,
    integrity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "basePerformanceId": base_id,
        "workId": work_id,
        "sourceRole": BASE_SOURCE_ROLE,
        "sourceAudioSha256": f"{source_n:064x}",
        "professionalReferenceSha256": f"{reference_n:064x}",
        "officialSplitLabel": split,
        "integrity": copy.deepcopy(integrity or _integrity()),
    }


def _receipt(rows: list[dict[str, Any]], *, official: bool) -> dict[str, Any]:
    normalized_rows = [validate_inventory_row(row, i) for i, row in enumerate(rows)]
    tier, status, selected, _ = expected_selection(
        normalized_rows,
        official_test_split_present=official,
    )
    return {
        "schema": RECEIPT_SCHEMA,
        "version": VERSION,
        "selectionContract": {
            "schema": CONTRACT_SCHEMA,
            "sha256": EXPECTED_CONTRACT_SHA256,
        },
        "dataset": {
            "zenodoRecordId": ZENODO_RECORD_ID,
            "doi": ZENODO_DOI,
            "version": ZENODO_VERSION,
            "accessGrantFrozen": True,
            "completeBaseDiInventoryFrozen": True,
            "sourceReferencePairInventoryFrozen": True,
            "inventoryBuiltWithoutComparativeScores": True,
        },
        "officialReleasedTestSplitPresent": official,
        "tierUsed": tier,
        "status": status,
        "inventory": rows,
        "selectedBasePerformanceIds": selected,
        "boundary": {
            "comparativeScoresReadBeforeSelectionFreeze": False,
            "candidateGenerationArmedBeforeSelectionFreeze": False,
            "referenceFacingScoringArmedBeforeSelectionFreeze": False,
            "v168ReferenceFacingScoreCallsBeforeSelectionFreeze": 0,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
        },
    }


def self_test(contract_path: Path) -> dict[str, Any]:
    load_contract(contract_path)

    tier1_rows = [
        _row("item_67", "work-b", 1, 101, split="test"),
        _row(
            "item_96",
            "work-a",
            2,
            102,
            split="test",
            integrity=_integrity("FAIL", "REFERENCE_ONSET_OUTSIDE_SOURCE_EOF"),
        ),
        _row("item_110", "work-c", 3, 103, split="train"),
        _row("item_20", "work-a", 4, 104, split="test"),
        _row("item_21", "work-c", 5, 105, split="test"),
        _row("item_22", "work-d", 6, 106, split="test"),
    ]
    tier1 = _receipt(tier1_rows, official=True)
    tier1_summary = validate_receipt(tier1, contract_path)
    require(tier1_summary["tierUsed"] == TIER1, "Tier 1 self-test did not use Tier 1")
    require(tier1_summary["selectedBasePerformanceIds"] == ["item_20", "item_67", "item_21"], "Tier 1 deterministic order drift")

    tier2_rows = [
        _row("base-z", "work-z", 11, 111, split=None),
        _row("base-a2", "work-a", 12, 112, split=None),
        _row("base-a1", "work-a", 13, 113, split=None),
        _row("base-b", "work-b", 14, 114, split=None),
        _row("base-c", "work-c", 15, 115, split=None),
    ]
    tier2 = _receipt(tier2_rows, official=False)
    tier2_summary = validate_receipt(tier2, contract_path)
    require(tier2_summary["tierUsed"] == TIER2, "Tier 2 self-test did not use Tier 2")
    require(len(tier2_summary["selectedBasePerformanceIds"]) == 3, "Tier 2 must select target 3 works")
    if "work-a" in tier2_summary["selectedWorkIds"]:
        require("base-a1" in tier2_summary["selectedBasePerformanceIds"], "Tier 2 representative selection drift for work-a")

    insufficient_rows = [
        _row("only-one", "single-work", 21, 121, split="test"),
        _row(
            "bad-two",
            "second-work",
            22,
            122,
            split="test",
            integrity=_integrity("FAIL", "V154_TIMEBASE_INCOMPATIBLE"),
        ),
    ]
    insufficient = _receipt(insufficient_rows, official=True)
    insufficient_summary = validate_receipt(insufficient, contract_path)
    require(insufficient_summary["status"] == "INCONCLUSIVE_HOLDOUT_INSUFFICIENT", "insufficient self-test must be inconclusive")

    negative_cases: list[str] = []

    wrong_selection = copy.deepcopy(tier1)
    wrong_selection["selectedBasePerformanceIds"] = list(reversed(wrong_selection["selectedBasePerformanceIds"]))
    try:
        validate_receipt(wrong_selection, contract_path)
    except SelectionError:
        negative_cases.append("selection-order-drift")
    else:
        raise SelectionError("self-test expected rejection: selection-order-drift")

    score_leak = copy.deepcopy(tier1)
    score_leak["boundary"]["comparativeScoresReadBeforeSelectionFreeze"] = True
    try:
        validate_receipt(score_leak, contract_path)
    except SelectionError:
        negative_cases.append("comparative-score-leak")
    else:
        raise SelectionError("self-test expected rejection: comparative-score-leak")

    repaired_failure = copy.deepcopy(tier1)
    repaired_failure["inventory"][1]["integrity"]["status"] = "PASS"
    repaired_failure["inventory"][1]["integrity"]["failureReasons"] = []
    try:
        validate_receipt(repaired_failure, contract_path)
    except SelectionError:
        negative_cases.append("failed-eof-item-promoted-to-pass")
    else:
        raise SelectionError("self-test expected rejection: failed-eof-item-promoted-to-pass")

    return {
        "status": "SELF_TEST_PASS",
        "contractSha256": EXPECTED_CONTRACT_SHA256,
        "tier1Selected": tier1_summary["selectedBasePerformanceIds"],
        "tier2Selected": tier2_summary["selectedBasePerformanceIds"],
        "insufficientStatus": insufficient_summary["status"],
        "negativeCasesRejected": negative_cases,
        "audioRead": False,
        "referenceNoteEventRead": False,
        "candidateRead": False,
        "scorerRead": False,
        "referenceFacingScoreCalls": 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--contract",
        type=Path,
        default=Path(__file__).with_name("goat_selection_contract_v168.json"),
    )
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--receipt", type=Path)
    group.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        print(json.dumps(self_test(args.contract), indent=2, sort_keys=True))
        return 0

    payload = json.loads(args.receipt.read_text(encoding="utf-8"))
    print(json.dumps(validate_receipt(payload, args.contract), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SelectionError as exc:
        raise SystemExit(f"V168 GOAT selection receipt invalid: {exc}")
