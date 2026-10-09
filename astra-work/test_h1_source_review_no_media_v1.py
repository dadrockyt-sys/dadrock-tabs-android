"""Synthetic, local-only tests for the review-only static import checker."""
import tempfile
from pathlib import Path
import unittest
from h1_source_review_no_media_v1 import (
    LOCK_SCHEMA, LOCK_STATUS, WORKFLOW, GENERATED_INIT, audit, git_blob,
    inspect_imports, verify_upstream,
)

MODULE = "astra_backend/synthetic_pkg/entry.py"
HELPER = "astra_backend/synthetic_pkg/helper.py"
INIT = "astra_backend/synthetic_pkg/__init__.py"


class SourceReviewFixtureTests(unittest.TestCase):
    def make_tree(self, root, entry="from synthetic_pkg import helper\n", helper=True, init=None):
        content = {MODULE: entry, WORKFLOW: "required={'" + MODULE + "','" + WORKFLOW + "'}\n"}
        if helper:
            content[HELPER] = "VALUE=1\n"
        if init is not None:
            content[INIT] = init
        for path, src in content.items():
            out = root / path
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(src)
        return {
            "schema": LOCK_SCHEMA, "status": LOCK_STATUS,
            "requiredLiveWorkflowSources": {path: git_blob(content[path].encode()) for path in (MODULE, WORKFLOW)},
            "additionalOfflineTestAndBudgetSources": {},
        }

    def test_unpinned_static_helper_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = self.make_tree(root)
            with self.assertRaisesRegex(RuntimeError, "UNPINNED_EXECUTABLE_LOCAL_SOURCE"):
                audit(root, lock)

    def test_executable_package_initializer_must_be_pinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = self.make_tree(root, init="print('synthetic init')\n")
            self.assertIn(INIT, inspect_imports(root, MODULE)[0])
            with self.assertRaisesRegex(RuntimeError, "UNPINNED_EXECUTABLE_LOCAL_SOURCE"):
                audit(root, lock)

    def test_complete_fixture_remains_non_authorizing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = self.make_tree(root)
            lock["requiredLiveWorkflowSources"][HELPER] = git_blob((root/HELPER).read_bytes())
            workflow = root/WORKFLOW
            workflow.write_text("required={'" + MODULE + "','" + WORKFLOW + "','" + HELPER + "'}\n")
            lock["requiredLiveWorkflowSources"][WORKFLOW] = git_blob(workflow.read_bytes())
            report = audit(root, lock)
            self.assertEqual(report["staticStatus"], "MATCH_PENDING_INDEPENDENT_REVIEW")
            self.assertFalse(report["completeDynamicImportClosure"])
            self.assertFalse(report["launchPermission"])
            self.assertEqual(report["externalPinAudit"]["identityStatus"], "NOT_RUN")

    def test_dynamic_import_call_is_reported_not_executed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_tree(root, entry="import importlib\nimportlib.import_module('synthetic_pkg.helper')\n")
            files, indicators, external = inspect_imports(root, MODULE)
            self.assertEqual(files, set())
            self.assertIn({"line": 2, "call": "importlib.import_module"}, indicators)

    def test_changed_source_hash_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = self.make_tree(root)
            (root/MODULE).write_text("pass\n")
            with self.assertRaisesRegex(RuntimeError, "DRAFT_LOCK_BLOB_MISMATCH"):
                audit(root, lock)

    def test_fake_upstream_bytes_pass_and_init_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "amt_tools/models/common.py"
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_bytes(b"fixture upstream, not real\n")
            for path, raw in GENERATED_INIT.items():
                out = root / "amt_tools" / path
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(raw)
            fake = {"models/common.py": git_blob(src.read_bytes())}
            self.assertEqual(verify_upstream(root, fake)["identityStatus"], "match")
            (root/"amt_tools/tools/__init__.py").write_bytes(b"bad init\n")
            with self.assertRaisesRegex(RuntimeError, "UPSTREAM_GENERATED_INIT_MISMATCH"):
                verify_upstream(root, fake)


if __name__ == "__main__":
    unittest.main()
