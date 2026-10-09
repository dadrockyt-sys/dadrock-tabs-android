"""No-media fixture tests for static import closure, including missing pins."""
import tempfile
from pathlib import Path
import unittest
from guitartechs_training_v10.h1_source_lock_audit_v1 import git_blob_id, SCHEMA
from guitartechs_training_v10.h1_static_import_closure_v1 import (
    audit_import_closure, internal_imports, SPECIAL_MODULE_PATHS,
)

WORKFLOW = ".github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml"
DRIVER = "astra_backend/guitartechs_training_v10/driver.py"
V7 = "astra_backend/guitartechs_training_v7/model.py"
V4 = "astra_backend/guitartechs_training_v4/objective_decoder.py"
RUNTIME = SPECIAL_MODULE_PATHS["preprocessing"]
HELPER = "astra_backend/guitartechs_training_v10/helper.py"


class StaticImportClosureTests(unittest.TestCase):
    def setup_tree(self, root, omit=()):
        files = {
            DRIVER: ("from guitartechs_training_v7.model import Tiny\n"
                     "from guitartechs_training_v4 import objective_decoder as v4\n"
                     "from preprocessing import SAMPLE_RATE_HZ\n"
                     "from .helper import CHECK\nimport torch\n"),
            V7: "class Tiny: pass\n",
            V4: "VALUE=3\n",
            RUNTIME: "SAMPLE_RATE_HZ=22050\n",
            HELPER: "CHECK=True\n",
        }
        required = set(files) - set(omit)
        required.add(WORKFLOW)
        files[WORKFLOW] = "required=" + repr(required) + "\n"
        for path, content in files.items():
            dest=root/path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
        return {
            "schema": SCHEMA,
            "status": "DRAFT_REQUIRES_INDEPENDENT_REVIEW_NOT_LAUNCH_AUTHORIZATION",
            "requiredLiveWorkflowSources": {name: git_blob_id(files[name].encode()) for name in required},
            "additionalOfflineTestAndBudgetSources": {},
        }

    def test_complete_static_closure_stays_review_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            lock=self.setup_tree(root)
            result=audit_import_closure(root,lock)
            self.assertEqual(result["staticImportClosure"],"match")
            self.assertFalse(result["dynamicAndExternalDependenciesReviewed"])
            self.assertFalse(result["launchPermission"])
            self.assertEqual(result["staticInternalDependencies"],4)

    def test_unpinned_import_fails_even_when_workflow_lock_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            lock=self.setup_tree(root,omit=(V4,))
            with self.assertRaisesRegex(RuntimeError,"H1_UNPINNED_STATIC_INTERNAL_IMPORTS"):
                audit_import_closure(root,lock)

    def test_relative_and_special_preprocessing_imports_found(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self.setup_tree(root)
            result=internal_imports(root,DRIVER)
            self.assertEqual(result,{V7,V4,RUNTIME,HELPER})

    def test_tampered_source_blocked_at_blob_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            lock=self.setup_tree(root)
            (root/V7).write_text("class Tiny: pass # modified\n")
            with self.assertRaisesRegex(RuntimeError,"H1_SOURCE_LOCK_BLOB_MISMATCH"):
                audit_import_closure(root,lock)


if __name__=="__main__":
    unittest.main()
