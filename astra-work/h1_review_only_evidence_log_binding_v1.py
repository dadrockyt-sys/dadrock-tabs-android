"""Offline byte-integrity verifier for externally gathered H1 scalar evidence.

This utility NEVER launches a workflow, downloads data, executes models, or
claims that log bytes prove an upper bound or independent approval. Synthetic
fixture passes are not H1 feasibility results. Uses only the Python stdlib.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import stat

SCHEMA = "astra-h1-human-feasibility-measurement-worksheet-v1"
MANIFEST_SCHEMA = "astra-h1-review-only-evidence-log-bindings-v1"
STAGES = (
    "environmentAndDependencies", "sourceAcquisition", "archivesAndPreparation",
    "originalFold1Training", "originalFold2Training",
    "treatmentFold1Training", "treatmentFold2Training",
    "originalFold1Evaluation", "originalFold2Evaluation",
    "treatmentFold1Evaluation", "treatmentFold2Evaluation",
    "uploadCleanupReserve",
)
RESOURCE_KEYS = (
    "availableDiskBytesAtJobStart", "peakAdditionalDiskBytes", "diskReserveBytes",
    "availableRamBytes", "peakResidentRamBytes", "ramReserveBytes",
)
ANCHORS = {
    "framesGitBlob": "701d4626de0e04200534ed17827db00c896a3d6b",
    "stageCapacityGitBlob": "e8375ec0cd132eadda93456a023df77a88153eda",
    "priorV9TimingsGitBlob": "309bbe19d6e52083237bd8f10d0998623bea6e80",
    "dormantWorkflowGitBlob": "90e8168fc1ca40738ba07291ca1001a36718f4e3",
}
SHA_RE = re.compile(r"[a-f0-9]{64}\Z")
MAX_LOG_BYTES = 64 * 1024 * 1024


def _regular_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.resolve() != path.absolute():
        raise ValueError("UNTRUSTED_JSON_PATH")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON_OBJECT_REQUIRED")
    return data


def _log_digest(root: Path, relative: str) -> str:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("INVALID_LOG_BINDING_PATH")
    parts = relative.split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise ValueError("INVALID_LOG_BINDING_PATH")
    target = root
    for part in parts:
        target = target / part
        if target.is_symlink():
            raise ValueError("LOG_SYMLINK_REJECTED")
    if not target.is_file() or target.resolve() != target:
        raise ValueError("EVIDENCE_LOG_ABSENT_OR_UNTRUSTED")
    mode = target.stat()
    if not stat.S_ISREG(mode.st_mode) or mode.st_size == 0 or mode.st_size > MAX_LOG_BYTES:
        raise ValueError("LOG_NOT_BOUNDED_REGULAR_FILE")
    digest = hashlib.sha256()
    size = 0
    with target.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(block)
            if size > MAX_LOG_BYTES:
                raise ValueError("LOG_SIZE_CHANGED_DURING_READ")
            digest.update(block)
    if size != mode.st_size:
        raise ValueError("LOG_SIZE_CHANGED_DURING_READ")
    return digest.hexdigest()


def _valid_receipt(row: object, *, runner: bool) -> bool:
    if not isinstance(row, dict):
        return False
    if runner:
        return (
            set(row) == {"runId", "evidenceSha256", "runnerImage"}
            and type(row["runId"]) is int and row["runId"] > 0
            and row["runnerImage"] == "ubuntu-22.04"
            and isinstance(row["evidenceSha256"], str)
            and SHA_RE.fullmatch(row["evidenceSha256"]) is not None
        )
    return (
        set(row) == {"upperBoundSeconds", "evidenceRunId", "evidenceSha256"}
        and type(row["evidenceRunId"]) is int and row["evidenceRunId"] > 0
        and type(row["upperBoundSeconds"]) in (int, float)
        and math.isfinite(row["upperBoundSeconds"]) and row["upperBoundSeconds"] > 0
        and isinstance(row["evidenceSha256"], str)
        and SHA_RE.fullmatch(row["evidenceSha256"]) is not None
    )


def _binding_path(binding: object) -> str:
    if not isinstance(binding, dict) or set(binding) != {"relativePath"}:
        raise ValueError("MISSING_OR_INVALID_LOG_BINDING")
    return binding["relativePath"]


def audit(worksheet: dict, bindings: dict, log_root: Path) -> dict:
    """Match locally provided log bytes to receipts, never authenticate their claims."""
    if log_root.is_symlink() or not log_root.is_dir() or log_root.resolve() != log_root.absolute():
        raise ValueError("EVIDENCE_LOG_ROOT_NOT_TRUSTED")
    if (not isinstance(worksheet, dict) or worksheet.get("schema") != SCHEMA
            or worksheet.get("sourceAnchors") != ANCHORS
            or set(worksheet) != {"schema", "sourceAnchors", "stageUpperBounds",
                                   "runnerResources", "runnerEvidence", "documentation"}):
        raise ValueError("WORKSHEET_IDENTITY_MISMATCH")
    stages, resources = worksheet["stageUpperBounds"], worksheet["runnerResources"]
    if (not isinstance(stages, dict) or set(stages) != set(STAGES)
            or not isinstance(resources, dict) or set(resources) != set(RESOURCE_KEYS)):
        raise ValueError("WORKSHEET_FIELD_SET_MISMATCH")
    if (not isinstance(bindings, dict) or bindings.get("schema") != MANIFEST_SCHEMA
            or set(bindings) != {"schema", "runner", "stages"}
            or not isinstance(bindings["stages"], dict)
            or set(bindings["stages"]) != set(STAGES)):
        raise ValueError("BINDING_SCHEMA_OR_STAGE_SET_MISMATCH")
    doc = worksheet["documentation"]
    review_keys = ("independentSourceAndPackageReview", "sharedAtomicOneUseControlReview",
                   "writtenSupportCase16795041")
    if (not isinstance(doc, dict) or set(doc) != set(review_keys) | {"notes"}
            or any(doc[k] != "PENDING" for k in review_keys)
            or not isinstance(doc["notes"], str) or not doc["notes"]):
        raise ValueError("PAPER_REVIEW_CANNOT_SELF_APPROVE")
    missing = []
    matched = []
    reused = {}
    for key in STAGES:
        row, binding = stages[key], bindings["stages"][key]
        if row is None:
            if binding is not None:
                raise ValueError("BINDING_WITHOUT_STAGE_EVIDENCE:" + key)
            missing.append("stage:" + key)
            continue
        if not _valid_receipt(row, runner=False):
            raise ValueError("INVALID_STAGE_PROVENANCE:" + key)
        location = _binding_path(binding)
        if _log_digest(log_root, location) != row["evidenceSha256"]:
            raise ValueError("STAGE_LOG_SHA256_MISMATCH:" + key)
        matched.append("stage:" + key)
        reused.setdefault(location, []).append(key)
    runner = worksheet["runnerEvidence"]
    if runner is None:
        if bindings["runner"] is not None:
            raise ValueError("BINDING_WITHOUT_RUNNER_RECEIPT")
        missing.append("runnerEvidence")
    else:
        if not _valid_receipt(runner, runner=True):
            raise ValueError("INVALID_RUNNER_PROVENANCE")
        if _log_digest(log_root, _binding_path(bindings["runner"])) != runner["evidenceSha256"]:
            raise ValueError("RUNNER_LOG_SHA256_MISMATCH")
        matched.append("runnerEvidence")
    for key, value in resources.items():
        if value is None:
            missing.append("resource:" + key)
        elif type(value) is not int or value < 0:
            raise ValueError("INVALID_RESOURCE_VALUE:" + key)
    return {
        "schema": "astra-h1-review-only-evidence-log-integrity-result-v1",
        "matchedLogBindings": len(matched),
        "matchedBindingFields": sorted(matched),
        "missingEvidenceFields": sorted(missing),
        "reusedStageLogPaths": {k: v for k, v in reused.items() if len(v) > 1},
        "logBytesMatchClaimedHashes": True,
        "loggedNumericalClaimsIndependentlyValidated": False,
        "independentH1RunnerComparabilityProven": False,
        "completeTwelveStageUpperBoundsProven": False,
        "sourceAuthenticityIndependentlyAttested": False,
        "reviewStatus": ("BLOCKED_MISSING_EVIDENCE" if missing
                         else "LOG_BYTES_MATCH_REQUIRES_INDEPENDENT_VALIDATION"),
        "launchPermission": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worksheet", required=True, type=Path)
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--log-root", required=True, type=Path)
    args = parser.parse_args()
    result = audit(_regular_json(args.worksheet), _regular_json(args.bindings), args.log_root)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
