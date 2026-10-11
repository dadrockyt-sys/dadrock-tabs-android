"""Isolated synthetic evidence tests, no network, workflows, models or media."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from h1_review_only_evidence_log_binding_v1 import (
    ANCHORS, MANIFEST_SCHEMA, RESOURCE_KEYS, SCHEMA, STAGES, audit,
)


def blank():
    return {
        "schema": SCHEMA,
        "sourceAnchors": dict(ANCHORS),
        "stageUpperBounds": {k: None for k in STAGES},
        "runnerResources": {k: None for k in RESOURCE_KEYS},
        "runnerEvidence": None,
        "documentation": {
            "notes": "SYNTHETIC FIXTURE NOT AN ACTUAL MEASUREMENT",
            "independentSourceAndPackageReview": "PENDING",
            "sharedAtomicOneUseControlReview": "PENDING",
            "writtenSupportCase16795041": "PENDING",
        },
    }


def bindings():
    return {"schema": MANIFEST_SCHEMA, "runner": None,
            "stages": {k: None for k in STAGES}}


class EvidenceLogBindingTest(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        self.worksheet = blank()
        self.bindings = bindings()

    def full_mock(self):
        for i, stage in enumerate(STAGES, 1):
            name = "stage%d.log" % i
            data = ("SYNTHETIC FIXTURE STAGE %d\n" % i).encode()
            (self.root / name).write_bytes(data)
            self.worksheet["stageUpperBounds"][stage] = {
                "upperBoundSeconds": 100, "evidenceRunId": i,
                "evidenceSha256": hashlib.sha256(data).hexdigest(),
            }
            self.bindings["stages"][stage] = {"relativePath": name}
        data = b"SYNTHETIC RUNNER FIXTURE NOT EVIDENCE\n"
        (self.root / "runner.log").write_bytes(data)
        self.worksheet["runnerEvidence"] = {
            "runId": 42, "runnerImage": "ubuntu-22.04",
            "evidenceSha256": hashlib.sha256(data).hexdigest(),
        }
        self.bindings["runner"] = {"relativePath": "runner.log"}
        for key in RESOURCE_KEYS:
            self.worksheet["runnerResources"][key] = 100

    def test_blank_remains_19_missing(self):
        result = audit(self.worksheet, self.bindings, self.root)
        self.assertEqual(len(result["missingEvidenceFields"]), 19)
        self.assertFalse(result["logBytesMatchClaimedHashes"])
        self.assertFalse(result["launchPermission"])

    def test_committed_blank_binding_template_is_fail_closed(self):
        template = Path(__file__).with_name(
            "H1_EVIDENCE_LOG_BINDINGS_BLANK_2026-10-11.json")
        manifest = json.loads(template.read_text(encoding="utf-8"))
        result = audit(self.worksheet, manifest, self.root)
        self.assertEqual(len(result["missingEvidenceFields"]), 19)
        self.assertFalse(result["logBytesMatchClaimedHashes"])
        self.assertFalse(result["launchPermission"])

    def test_complete_mock_only_proves_byte_integrity(self):
        self.full_mock()
        result = audit(self.worksheet, self.bindings, self.root)
        self.assertEqual(result["matchedLogBindings"], 13)
        self.assertEqual(result["missingEvidenceFields"], [])
        self.assertEqual(result["reviewStatus"], "LOG_BYTES_MATCH_REQUIRES_INDEPENDENT_VALIDATION")
        self.assertFalse(result["loggedNumericalClaimsIndependentlyValidated"])
        self.assertFalse(result["launchPermission"])

    def test_altered_stage_log_detected(self):
        self.full_mock()
        (self.root / "stage3.log").write_text("modified")
        with self.assertRaisesRegex(ValueError, "STAGE_LOG_SHA256_MISMATCH"):
            audit(self.worksheet, self.bindings, self.root)

    def test_altered_runner_log_detected(self):
        self.full_mock()
        (self.root / "runner.log").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "RUNNER_LOG_SHA256_MISMATCH"):
            audit(self.worksheet, self.bindings, self.root)

    def test_missing_stage_log_rejected(self):
        self.full_mock()
        (self.root / "stage1.log").unlink()
        with self.assertRaisesRegex(ValueError, "EVIDENCE_LOG_ABSENT"):
            audit(self.worksheet, self.bindings, self.root)

    def test_missing_log_binding_rejected(self):
        self.full_mock()
        self.bindings["stages"][STAGES[0]] = None
        with self.assertRaisesRegex(ValueError, "MISSING_OR_INVALID_LOG_BINDING"):
            audit(self.worksheet, self.bindings, self.root)

    def test_cannot_bind_missing_receipt(self):
        self.bindings["runner"] = {"relativePath": "unrelated.txt"}
        with self.assertRaisesRegex(ValueError, "BINDING_WITHOUT_RUNNER_RECEIPT"):
            audit(self.worksheet, self.bindings, self.root)

    def test_path_traversal_rejected(self):
        self.full_mock()
        self.bindings["stages"][STAGES[0]] = {"relativePath": "../stage1.log"}
        with self.assertRaisesRegex(ValueError, "INVALID_LOG_BINDING_PATH"):
            audit(self.worksheet, self.bindings, self.root)

    def test_symlinked_log_rejected(self):
        self.full_mock()
        (self.root / "alias.log").symlink_to(self.root / "stage1.log")
        self.bindings["stages"][STAGES[0]] = {"relativePath": "alias.log"}
        with self.assertRaisesRegex(ValueError, "LOG_SYMLINK_REJECTED"):
            audit(self.worksheet, self.bindings, self.root)

    def test_source_anchor_change_rejected(self):
        self.worksheet["sourceAnchors"]["dormantWorkflowGitBlob"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "WORKSHEET_IDENTITY_MISMATCH"):
            audit(self.worksheet, self.bindings, self.root)

    def test_forged_approval_flag_rejected(self):
        self.worksheet["documentation"]["writtenSupportCase16795041"] = "APPROVED"
        with self.assertRaisesRegex(ValueError, "PAPER_REVIEW_CANNOT_SELF_APPROVE"):
            audit(self.worksheet, self.bindings, self.root)

    def test_boolean_resource_does_not_count_as_integer(self):
        self.worksheet["runnerResources"][RESOURCE_KEYS[0]] = True
        with self.assertRaisesRegex(ValueError, "INVALID_RESOURCE_VALUE"):
            audit(self.worksheet, self.bindings, self.root)

    def test_impossible_stage_provenance_rejected(self):
        self.full_mock()
        self.worksheet["stageUpperBounds"][STAGES[0]]["evidenceRunId"] = 0
        with self.assertRaisesRegex(ValueError, "INVALID_STAGE_PROVENANCE"):
            audit(self.worksheet, self.bindings, self.root)

    def test_missing_manifest_stage_rejected(self):
        self.bindings["stages"].pop(STAGES[0])
        with self.assertRaisesRegex(ValueError, "BINDING_SCHEMA_OR_STAGE_SET_MISMATCH"):
            audit(self.worksheet, self.bindings, self.root)

    def test_empty_file_rejected(self):
        self.full_mock()
        (self.root / "stage1.log").write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "LOG_NOT_BOUNDED_REGULAR_FILE"):
            audit(self.worksheet, self.bindings, self.root)

    def test_oversize_receipt_rejected_without_reading(self):
        self.full_mock()
        with (self.root / "stage1.log").open("wb") as f:
            f.truncate(64 * 1024 * 1024 + 1)
        with self.assertRaisesRegex(ValueError, "LOG_NOT_BOUNDED_REGULAR_FILE"):
            audit(self.worksheet, self.bindings, self.root)

    def test_reused_stage_log_is_reported(self):
        self.full_mock()
        row0 = copy.deepcopy(self.worksheet["stageUpperBounds"][STAGES[0]])
        self.worksheet["stageUpperBounds"][STAGES[1]] = row0
        self.bindings["stages"][STAGES[1]] = {"relativePath": "stage1.log"}
        result = audit(self.worksheet, self.bindings, self.root)
        self.assertIn("stage1.log", result["reusedStageLogPaths"])
        self.assertFalse(result["launchPermission"])


if __name__ == "__main__":
    unittest.main()
