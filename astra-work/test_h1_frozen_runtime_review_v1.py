"""Synthetic-only fixture tests; no model, optimizer, repo checkout, or media."""
import tempfile
from pathlib import Path
import unittest
from h1_frozen_runtime_review_v1 import (
    PARITY, LOCK, WORKFLOW, extract_pins, read_text, review_bytes, review_checkout,
)

WORKFLOW_TEXT = "steps:\n  - with:\n      python-version: '3.10.15'\n"
LOCK_TEXT = "numpy==1.21.6\ntorch==1.11.0+cpu\n"
NO_CHECKS = 'import torch\nimport numpy as np\nimport platform\ndef main():\n  print(torch.__version__)\n  print("PASS_SYNTHETIC_ONLY")\n'
WITH_CHECKS = ("import torch, numpy as np, platform\n"
               "def main():\n"
               "  assert platform.python_version() == '3.10.15'\n"
               "  assert torch.__version__ == '1.11.0+cpu'\n"
               "  assert np.__version__ == '1.21.6'\n"
               "  print('PASS_SYNTHETIC_ONLY')\n")


class FrozenSourceAuditTests(unittest.TestCase):
    def test_missing_comparisons_are_flagged_and_non_authorizing(self):
        r = review_bytes(WORKFLOW_TEXT, LOCK_TEXT, NO_CHECKS)
        self.assertEqual(r['missingExplicitVersionComparisons'], ['numpy', 'python', 'torch'])
        self.assertFalse(r['safeToClaimFrozenParityPass'])
        self.assertFalse(r['launchPermission'])
        self.assertFalse(r['runtimeEnforcementProven'])

    def test_literal_comparisons_still_not_runtime_approval(self):
        r = review_bytes(WORKFLOW_TEXT, LOCK_TEXT, WITH_CHECKS)
        self.assertEqual(r['missingExplicitVersionComparisons'], [])
        self.assertFalse(r['runtimeEnforcementProven'])
        self.assertFalse(r['safeToClaimFrozenParityPass'])

    def test_strings_and_comments_do_not_count_as_guard(self):
        text = '"torch.__version__ == \'1.11.0+cpu\'"\n# numpy.__version__ == "1.21.6"\n'
        r = review_bytes(WORKFLOW_TEXT, LOCK_TEXT, text)
        self.assertEqual(r['missingExplicitVersionComparisons'], ['numpy', 'python', 'torch'])

    def test_drifted_or_missing_pin_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, 'FROZEN_DEPENDENCY_PIN_DRIFT'):
            extract_pins(WORKFLOW_TEXT, LOCK_TEXT.replace('1.11.0+cpu', '2.10.0+cpu'))
        with self.assertRaisesRegex(RuntimeError, 'DEPENDENCY_PIN_MISSING_OR_AMBIGUOUS'):
            extract_pins(WORKFLOW_TEXT, LOCK_TEXT + 'torch==1.11.0+cpu\n')
        with self.assertRaisesRegex(RuntimeError, 'PYTHON_PIN_MISSING_OR_AMBIGUOUS'):
            extract_pins('steps: []\n', LOCK_TEXT)

    def test_malformed_probe_fails_parse(self):
        with self.assertRaises(SyntaxError):
            review_bytes(WORKFLOW_TEXT, LOCK_TEXT, 'def main(:\n  pass\n')

    def test_checkout_paths_are_read_only_and_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative, text in ((WORKFLOW, WORKFLOW_TEXT), (LOCK, LOCK_TEXT), (PARITY, NO_CHECKS)):
                file = root / relative
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(text)
            self.assertEqual(len(review_checkout(root)['missingExplicitVersionComparisons']), 3)
            (root/LOCK).unlink()
            (root/LOCK).symlink_to(root/PARITY)
            with self.assertRaisesRegex(RuntimeError, 'MISSING_OR_LINKED_SOURCE'):
                read_text(root, LOCK)


if __name__ == '__main__':
    unittest.main(verbosity=2)
