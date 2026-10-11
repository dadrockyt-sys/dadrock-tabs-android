"""Synthetic-only, stdlib-only contract tests. No external connectivity."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from h1_review_only_environment_contract_v1 import (
    ANCHORS, EVIDENCE, FORBIDDEN_ACTIONS, TARGET, validate_contract, review,
)

CONTRACT = Path(__file__).with_name('H1_REVIEW_ONLY_ENVIRONMENT_CONTRACT_2026-10-11.json')


class ReviewOnlyEnvironmentContractTest(unittest.TestCase):
    def setUp(self):
        self.c = json.loads(CONTRACT.read_text(encoding='utf-8'))

    def test_baseline_contract_valid(self):
        validate_contract(self.c)
        self.assertEqual(self.c['state'], 'DESIGN_ONLY_NO_RUNNER_PROVISIONED')

    def test_all_forbidden_actions_asserted(self):
        self.assertEqual(set(self.c['prohibitions']), set(FORBIDDEN_ACTIONS))
        self.assertTrue(all(self.c['prohibitions'].values()))

    def test_launch_permission_cannot_be_switched_on(self):
        c = deepcopy(self.c)
        c['launchPermission'] = True
        with self.assertRaisesRegex(ValueError, 'NONAUTHORIZING'):
            validate_contract(c)

    def test_relaxing_safety_prohibition_fails(self):
        c = deepcopy(self.c)
        c['prohibitions']['createOrEditBlockedLaunchJson'] = False
        with self.assertRaisesRegex(ValueError, 'SAFETY_BOUNDARY'):
            validate_contract(c)

    def test_extra_prohibition_key_fails(self):
        c = deepcopy(self.c)
        c['prohibitions']['externalBypass'] = True
        with self.assertRaises(ValueError):
            validate_contract(c)

    def test_modified_frozen_python_version_fails(self):
        c = deepcopy(self.c)
        c['target']['python'] = '3.13.5'
        with self.assertRaisesRegex(ValueError, 'DRIFT'):
            validate_contract(c)

    def test_changed_workflow_blob_fails(self):
        c = deepcopy(self.c)
        c['sourceAnchors']['dormantWorkflowGitBlob'] = '0'*40
        with self.assertRaisesRegex(ValueError, 'DRIFT'):
            validate_contract(c)

    def test_required_review_milestone_cannot_be_dropped(self):
        c = deepcopy(self.c)
        c['requiredIndependentEvidence'] = list(EVIDENCE[:-1])
        with self.assertRaisesRegex(ValueError, 'EVIDENCE'):
            validate_contract(c)

    def test_mismatched_python_and_os_remains_no_go(self):
        r = review(self.c, {**TARGET, 'python': '3.13.5', 'operatingSystemId': 'debian'})
        self.assertFalse(r['allLiteralPinsMatch'])
        self.assertFalse(r['launchPermission'])

    def test_all_literal_pins_fake_match_remains_no_go(self):
        r = review(self.c, dict(TARGET))
        self.assertTrue(r['allLiteralPinsMatch'])
        self.assertEqual(r['readiness'], 'NO_GO_INSUFFICIENT_EVIDENCE')
        self.assertFalse(r['importedRuntimeAndCudaVerified'])
        self.assertFalse(r['launchPermission'])

    def test_partial_evidence_cannot_pass(self):
        r = review(self.c, {'python':'3.10.15'})
        self.assertFalse(r['allLiteralPinsMatch'])
        self.assertFalse(r['independentlyAuthorizedMeasurementSetting'])

    def test_target_and_anchor_exact_shapes(self):
        self.assertEqual(self.c['target'], TARGET)
        self.assertEqual(self.c['sourceAnchors'], ANCHORS)

    def test_nonevidence_input_rejected(self):
        with self.assertRaises(ValueError):
            review(self.c, None)


if __name__ == '__main__':
    unittest.main()
