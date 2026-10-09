"""No-network tests for H1 draft source snapshot integrity."""
import tempfile
from pathlib import Path
import unittest
from guitartechs_training_v10.h1_source_lock_audit_v1 import git_blob_id, required_workflow_paths, verify_lock, SCHEMA

WORKFLOW = '.github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml'
CORE = 'astra_backend/guitartechs_training_v10/h1_pilot_core_v1.py'
EXTRA = 'astra_backend/guitartechs_training_v10/test_stub.py'


class DraftSourceLockChecks(unittest.TestCase):
    def fixture(self, root):
        workflow = b'jobs:\n  verify:\n    run: |\n      required={"'+CORE.encode()+b'", "'+WORKFLOW.encode()+b'"}\n'
        payload = {WORKFLOW: workflow, CORE: b'print("stub")\n', EXTRA: b'# synthetic\n'}
        for name, content in payload.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        lock = {"schema": SCHEMA,
                "status": "DRAFT_REQUIRES_INDEPENDENT_REVIEW_NOT_LAUNCH_AUTHORIZATION",
                "requiredLiveWorkflowSources": {name: git_blob_id(payload[name]) for name in (WORKFLOW, CORE)},
                "additionalOfflineTestAndBudgetSources": {EXTRA: git_blob_id(payload[EXTRA])}}
        return lock

    def test_matching_snapshot_does_not_grant_launch(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name)
            receipt=verify_lock(root,self.fixture(root))
            self.assertEqual((receipt['requiredCount'],receipt['additionalCount']), (2,1))
            self.assertEqual(receipt['reviewStatus'],'PENDING')
            self.assertFalse(receipt['launchPermission'])

    def test_mutation_and_missing_path_fail_closed(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name)
            lock=self.fixture(root)
            (root/CORE).write_text('different')
            with self.assertRaisesRegex(RuntimeError,'BLOB_MISMATCH'):
                verify_lock(root,lock)
            (root/CORE).unlink()
            with self.assertRaisesRegex(RuntimeError,'MISSING_OR_LINK'):
                verify_lock(root,lock)

    def test_workflow_required_set_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name)
            lock=self.fixture(root)
            workflow=(root/WORKFLOW)
            changed=workflow.read_text().replace(CORE,'new/extraneous.py')
            workflow.write_text(changed)
            lock['requiredLiveWorkflowSources'][WORKFLOW] = git_blob_id(changed.encode())
            with self.assertRaisesRegex(RuntimeError,'EXHAUSTIVE_SET_MISMATCH'):
                verify_lock(root,lock)

    def test_traversal_and_ambiguous_sets_fail(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name)
            lock=self.fixture(root)
            lock['additionalOfflineTestAndBudgetSources']['../escape.py']='0'*40
            with self.assertRaisesRegex(RuntimeError,'PATH_TRAVERSAL'):
                verify_lock(root,lock)
        with self.assertRaisesRegex(RuntimeError,'MISSING_OR_AMBIGUOUS'):
            required_workflow_paths('run: echo safe')
        with self.assertRaisesRegex(RuntimeError,'NOT_LITERAL'):
            required_workflow_paths('required={unknown_variable}')


if __name__ == '__main__': unittest.main()
